import sqlite3
import re
import secrets
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import jwt as pyjwt
import bcrypt
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr

# 创建路由器
router = APIRouter(prefix="/api/user", tags=["用户管理"])

# OAuth2 密码流认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

# JWT 配置
SECRET_KEY = "bilibili_comments_crawler_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天过期

# 邮件配置
EMAIL_HOST = 'smtp.qq.com'  # SMTP服务器地址
EMAIL_PORT = 587  # SMTP服务器端口
EMAIL_USE_SSL = False  # 不使用SSL加密
EMAIL_HOST_USER = ''  # 发送邮件的邮箱
EMAIL_HOST_PASSWORD = ''  # 授权码
EMAIL_FROM = ''  # 发件人
EMAIL_USE_TLS = True  # 使用TLS加密（端口587需要TLS）

# 初始化数据库
def init_user_db():
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP NOT NULL
    )
    ''')
    
    # 创建验证码缓存表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verification_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        code TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL
    )
    ''')
    
    # 修改爬取记录表，添加用户ID字段
    try:
        cursor.execute("ALTER TABLE crawl_records ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        # 如果字段已存在，忽略错误
        pass
    
    # 检查是否已有管理员账户，如果没有则创建一个默认管理员
    cursor.execute("SELECT COUNT(*) FROM users WHERE level = 2")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # 创建默认管理员账户
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, email, password, level, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@example.com", hashed_password, 2, datetime.now())
        )
    
    conn.commit()
    conn.close()

# 清理过期验证码
def clean_expired_codes():
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 删除3分钟前的验证码
    three_minutes_ago = datetime.now() - timedelta(minutes=3)
    cursor.execute("DELETE FROM verification_codes WHERE created_at < ?", (three_minutes_ago,))
    
    conn.commit()
    conn.close()

# 密码加密
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 生成随机验证码
def generate_verification_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

# 发送邮件
def send_email(to_email: str, subject: str, content: str) -> bool:
    try:
        message = MIMEText(content, 'html', 'utf-8')
        # 修复 From 头部格式，符合 RFC5322、RFC2047、RFC822 标准
        message['From'] = f'=?utf-8?B?QmlsaWJpbGnor7forqLniYjnur8=?= <{EMAIL_FROM}>'
        message['To'] = Header(to_email, 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        
        if EMAIL_USE_TLS:
            smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            smtp.starttls()
        elif EMAIL_USE_SSL:
            smtp = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        else:
            smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        smtp.sendmail(EMAIL_FROM, [to_email], message.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except pyjwt.PyJWTError:
        raise credentials_exception
        
    conn = sqlite3.connect('bilibili_CH.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        raise credentials_exception
    
    return dict(user)

# 请求模型
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    code: str = Field(..., min_length=6, max_length=6)

class EmailVerification(BaseModel):
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str
    name: str
    level: int
    username: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    level: int

# API路由
@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    # 清理过期验证码
    clean_expired_codes()
    
    # 验证用户名格式
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', user.username):
        raise HTTPException(status_code=400, detail="用户名只能包含字母、数字和下划线，长度为3-20个字符")
    
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 验证用户名是否已存在
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证邮箱是否已存在
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 验证验证码
    cursor.execute("SELECT code FROM verification_codes WHERE email = ? ORDER BY created_at DESC LIMIT 1", (user.email,))
    code_record = cursor.fetchone()
    
    if not code_record or code_record[0] != user.code:
        conn.close()
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    # 创建用户
    hashed_password = get_password_hash(user.password)
    
    cursor.execute(
        "INSERT INTO users (username, email, password, level, created_at) VALUES (?, ?, ?, ?, ?)",
        (user.username, user.email, hashed_password, 1, datetime.now())
    )
    
    user_id = cursor.lastrowid
    
    # 删除已使用的验证码
    cursor.execute("DELETE FROM verification_codes WHERE email = ?", (user.email,))
    
    conn.commit()
    conn.close()
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.username,
        "level": 1,
        "username": user.username
    }

@router.post("/send_email_code")
async def send_verification_code(email_data: EmailVerification):
    # 清理过期验证码
    clean_expired_codes()
    
    # 检查邮箱格式
    if not re.match(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$', email_data.email.lower()):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    
    # 生成验证码
    code = generate_verification_code()
    
    # 存储验证码
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 删除旧的验证码
    cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email_data.email,))
    
    cursor.execute(
        "INSERT INTO verification_codes (email, code, created_at) VALUES (?, ?, ?)",
        (email_data.email, code, datetime.now())
    )
    
    conn.commit()
    conn.close()
    
    # 发送验证码邮件
    email_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
        <h2 style="color: #409EFF;">Bilibili评论爬虫 - 邮箱验证</h2>
        <p>您好，</p>
        <p>您的验证码是：</p>
        <div style="background-color: #f5f5f5; padding: 10px; font-size: 24px; font-weight: bold; text-align: center; letter-spacing: 5px; margin: 20px 0;">{code}</div>
        <p>该验证码将在 <strong>3分钟</strong> 后失效。</p>
        <p>如果您没有请求此验证码，请忽略此邮件。</p>
        <p style="margin-top: 30px; font-size: 12px; color: #999;">此邮件由系统自动发送，请勿回复。</p>
    </div>
    """
    
    success = send_email(
        to_email=email_data.email,
        subject="Bilibili评论爬虫 - 邮箱验证码",
        content=email_content
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="邮件发送失败，请稍后重试")
    
    return {"message": "验证码已发送到您的邮箱"}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    conn = sqlite3.connect('bilibili_CH.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 查询用户（支持用户名或邮箱登录）
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (form_data.username, form_data.username))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 设置令牌过期时间
    access_token_expires = timedelta(days=30 if form_data.remember_me else 1)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user["username"],
        "level": user["level"],
        "username": user["username"]
    }

@router.get("/me", response_model=UserInfo)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "level": current_user["level"]
    }