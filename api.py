import re
import requests
import json
from urllib.parse import quote
import pandas as pd
import hashlib
import urllib
import time
import csv
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from user_api import router as user_router, get_current_user, init_user_db

# 创建FastAPI应用
app = FastAPI(
    title="Bilibili评论爬虫API",
    description="用于爬取B站视频评论的API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 创建爬取记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crawl_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bv TEXT NOT NULL,
        title TEXT NOT NULL,
        mode INTEGER NOT NULL,
        is_second BOOLEAN NOT NULL,
        comment_count INTEGER NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        status TEXT NOT NULL,
        user_id INTEGER
    )
    ''')
    
    # 创建评论表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crawl_id INTEGER NOT NULL,
        comment_index INTEGER NOT NULL,
        parent_id INTEGER NOT NULL,
        comment_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        user_level INTEGER NOT NULL,
        gender TEXT NOT NULL,
        content TEXT NOT NULL,
        comment_time TIMESTAMP NOT NULL,
        reply_count INTEGER NOT NULL,
        like_count INTEGER NOT NULL,
        signature TEXT,
        ip_location TEXT,
        is_vip TEXT,
        avatar TEXT,
        FOREIGN KEY (crawl_id) REFERENCES crawl_records (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()
init_user_db()

# 获取B站Header
def get_Header():
    try:
        with open('bili_cookie.txt', 'r') as f:
            cookie = f.read()
        header = {
            "Cookie": cookie,
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
        }
    except:
        header = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
        }
    return header

# 通过BV号获取视频OID和标题
def get_information(bv):
    resp = requests.get(f"https://www.bilibili.com/video/{bv}/?p=14&spm_id_from=pageDriver&vd_source=cd6ee6b033cd2da64359bad72619ca8a", headers=get_Header())
    # 提取视频oid
    obj = re.compile(f'"aid":(?P<id>.*?),"bvid":"{bv}"')
    oid = obj.search(resp.text).group('id')

    # 提取视频的标题
    obj = re.compile(r'<title data-vue-meta="true">(?P<title>.*?)</title>')
    try:
        title = obj.search(resp.text).group('title')
    except:
        title = "未识别"

    return oid, title

# MD5加密
def md5(code):
    MD5 = hashlib.md5()
    MD5.update(code.encode('utf-8'))
    w_rid = MD5.hexdigest()
    return w_rid

# 爬取评论并存储到数据库
def crawl_comments(crawl_id, bv, oid, next_pageID, count, is_second, mode, limit_num=300):
    conn = sqlite3.connect('bilibili_CH.db')
    cursor = conn.cursor()
    
    # 更新爬取状态为进行中
    cursor.execute("UPDATE crawl_records SET status = ? WHERE id = ?", ("进行中", crawl_id))
    conn.commit()
    
    try:
        # 参数
        plat = 1
        type = 1  
        sort = mode  # 2是最新评论，3是热门评论
        ps = 20  # 每页显示的评论数量
        page_num = 1  # 当前页码，初始为1
        web_location = 1315875
        
        # 爬取评论
        while True:
            # 获取当下时间戳
            wts = int(time.time())
            
            # 如果不是第一页或有下一页ID
            if next_pageID != "":
                pagination_str = '{"offset":"%s"}' % next_pageID
                code = f"mode={sort}&oid={oid}&pagination_str={urllib.parse.quote(pagination_str)}&plat={plat}&type={type}&web_location={web_location}&wts={wts}" + 'ea1db124af3c7062474693fa704f4ff8'
                w_rid = md5(code)
                url = f"https://api.bilibili.com/x/v2/reply/wbi/main?oid={oid}&type={type}&mode={sort}&pagination_str={urllib.parse.quote(pagination_str, safe=':')}&plat=1&web_location={web_location}&w_rid={w_rid}&wts={wts}"
            # 如果是第一页
            else:
                pagination_str = '{"offset":""}'
                code = f"mode={sort}&oid={oid}&pagination_str={urllib.parse.quote(pagination_str)}&plat={plat}&seek_rpid=&type={type}&web_location={web_location}&wts={wts}" + 'ea1db124af3c7062474693fa704f4ff8'
                w_rid = md5(code)
                url = f"https://api.bilibili.com/x/v2/reply/wbi/main?oid={oid}&type={type}&mode={sort}&pagination_str={urllib.parse.quote(pagination_str, safe=':')}&plat=1&seek_rpid=&web_location={web_location}&w_rid={w_rid}&wts={wts}"
            
            # 发送请求
            comment = requests.get(url=url, headers=get_Header()).content.decode('utf-8')
            comment = json.loads(comment)
            
            # 如果没有评论数据，则退出循环
            if 'data' not in comment or 'replies' not in comment['data'] or not comment['data']['replies']:
                break
            
            # 遍历评论
            for reply in comment['data']['replies']:
                # 评论数量+1
                count += 1
                
                if count > limit_num:
                    break
                
                # 提取评论数据
                parent = reply["parent"]
                rpid = reply["rpid"]
                uid = reply["mid"]
                name = reply["member"]["uname"]
                level = reply["member"]["level_info"]["current_level"]
                sex = reply["member"]["sex"]
                avatar = reply["member"]["avatar"]
                
                # 是否是大会员
                if reply["member"]["vip"]["vipStatus"] == 0:
                    vip = "否"
                else:
                    vip = "是"
                    
                # IP属地
                try:
                    IP = reply["reply_control"]['location'][5:]
                except:
                    IP = "未知"
                    
                # 内容
                context = reply["content"]["message"]
                
                # 评论时间
                reply_time = datetime.fromtimestamp(reply["ctime"])
                
                # 相关回复数
                try:
                    rereply = reply["reply_control"]["sub_reply_entry_text"]
                    rereply = int(re.findall(r'\d+', rereply)[0])
                except:
                    rereply = 0
                    
                # 点赞数
                like = reply['like']
                
                # 个性签名
                try:
                    sign = reply['member']['sign']
                except:
                    sign = ''
                
                # 存储评论到数据库
                cursor.execute("""
                INSERT INTO comments (crawl_id, comment_index, parent_id, comment_id, user_id, username, user_level, gender, content, comment_time, reply_count, like_count, signature, ip_location, is_vip, avatar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (crawl_id, count, parent, rpid, uid, name, level, sex, context, reply_time, rereply, like, sign, IP, vip, avatar))
                
                # 二级评论(如果开启了二级评论爬取，且该评论回复数不为0，则爬取该评论的二级评论)
                if is_second and rereply != 0 and count < limit_num:
                    for page in range(1, rereply//10+2):
                        second_url = f"https://api.bilibili.com/x/v2/reply/reply?oid={oid}&type=1&root={rpid}&ps=10&pn={page}&web_location=333.788"
                        second_comment = requests.get(url=second_url, headers=get_Header()).content.decode('utf-8')
                        second_comment = json.loads(second_comment)
                        
                        if 'data' not in second_comment or 'replies' not in second_comment['data'] or not second_comment['data']['replies']:
                            break
                            
                        for second in second_comment['data']['replies']:
                            # 评论数量+1
                            count += 1
                            
                            if count > limit_num:
                                break
                                
                            # 提取二级评论数据
                            parent = second["parent"]
                            second_rpid = second["rpid"]
                            uid = second["mid"]
                            name = second["member"]["uname"]
                            level = second["member"]["level_info"]["current_level"]
                            sex = second["member"]["sex"]
                            avatar = second["member"]["avatar"]
                            
                            # 是否是大会员
                            if second["member"]["vip"]["vipStatus"] == 0:
                                vip = "否"
                            else:
                                vip = "是"
                                
                            # IP属地
                            try:
                                IP = second["reply_control"]['location'][5:]
                            except:
                                IP = "未知"
                                
                            # 内容
                            context = second["content"]["message"]
                            
                            # 评论时间
                            reply_time = datetime.fromtimestamp(second["ctime"])
                            
                            # 相关回复数
                            try:
                                rereply = second["reply_control"]["sub_reply_entry_text"]
                                rereply = int(re.findall(r'\d+', rereply)[0])
                            except:
                                rereply = 0
                                
                            # 点赞数
                            like = second['like']
                            
                            # 个性签名
                            try:
                                sign = second['member']['sign']
                            except:
                                sign = ''
                            
                            # 存储二级评论到数据库
                            cursor.execute("""
                            INSERT INTO comments (crawl_id, comment_index, parent_id, comment_id, user_id, username, user_level, gender, content, comment_time, reply_count, like_count, signature, ip_location, is_vip, avatar)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (crawl_id, count, parent, second_rpid, uid, name, level, sex, context, reply_time, rereply, like, sign, IP, vip, avatar))
                            
                            conn.commit()
                            
                            if count >= limit_num:
                                break
                        
                        if count >= limit_num:
                            break
                
                conn.commit()
                
                if count >= limit_num:
                    break
            
            # 下一页的pageID
            try:
                next_pageID = comment['data']['cursor']['pagination_reply']['next_offset']
            except:
                next_pageID = 0
            
            # 增加页码
            page_num += 1
            
            # 如果不是最后一页，则停0.5s（避免反爬机制）
            if next_pageID != 0 and count < limit_num:
                time.sleep(0.5)
                
            if count >= limit_num:
                break
            
            # 如果next_pageID为0，说明已经没有下一页了
            if next_pageID == 0:
                break
        
        # 更新爬取记录状态为完成
        cursor.execute("UPDATE crawl_records SET status = ?, end_time = ?, comment_count = ? WHERE id = ?", 
                      ("完成", datetime.now(), count, crawl_id))
        conn.commit()
        
    except Exception as e:
        # 更新爬取记录状态为失败
        cursor.execute("UPDATE crawl_records SET status = ?, end_time = ? WHERE id = ?", 
                      (f"失败: {str(e)}", datetime.now(), crawl_id))
        conn.commit()
    finally:
        conn.close()

# 定义请求模型
class CrawlRequest(BaseModel):
    bv: str = Field(..., description="B站视频的BV号")
    next_pageID: str = Field("", description="评论起始页ID，默认为空字符串表示从第一页开始")
    is_second: bool = Field(True, description="是否爬取二级评论")
    mode: int = Field(3, description="评论模式：2为最新评论，3为热门评论")
    limit_num: int = Field(300, description="爬取评论的数量上限，默认300，最大1000", ge=1, le=1000)

# 定义响应模型
class CrawlResponse(BaseModel):
    crawl_id: int
    bv: str
    title: str
    status: str
    message: str

# 添加用户路由
app.include_router(user_router)

# API路由
@app.post("/api/crawl", response_model=CrawlResponse)
async def crawl_comments_api(request: CrawlRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    # 验证参数
    if request.limit_num > 1000:
        request.limit_num = 1000
    
    try:
        # 获取视频信息
        oid, title = get_information(request.bv)
        
        # 创建爬取记录
        conn = sqlite3.connect('bilibili_CH.db')
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO crawl_records (bv, title, mode, is_second, comment_count, start_time, status, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (request.bv, title, request.mode, request.is_second, 0, datetime.now(), "等待中", current_user["id"]))
        
        conn.commit()
        crawl_id = cursor.lastrowid
        conn.close()
        
        # 在后台任务中执行爬取
        background_tasks.add_task(
            crawl_comments, 
            crawl_id, 
            request.bv, 
            oid, 
            request.next_pageID, 
            0, 
            request.is_second, 
            request.mode, 
            request.limit_num
        )
        
        return CrawlResponse(
            crawl_id=crawl_id,
            bv=request.bv,
            title=title,
            status="已开始爬取",
            message="爬取任务已在后台开始执行"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取爬取记录列表
@app.get("/api/crawl_records")
async def get_crawl_records(current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('bilibili_CH.db')
        conn.row_factory = sqlite3.Row  # 启用字典形式返回结果
        cursor = conn.cursor()
        
        # 根据用户权限级别获取爬取记录
        if current_user["level"] == 2:  # 管理员可以查看所有记录
            cursor.execute("""
            SELECT cr.id, cr.bv, cr.title, cr.mode, cr.is_second, cr.comment_count, cr.start_time, cr.end_time, cr.status, u.username 
            FROM crawl_records cr
            LEFT JOIN users u ON cr.user_id = u.id
            ORDER BY cr.start_time DESC
            """)
        else:  # 普通用户只能查看自己的记录
            cursor.execute("""
            SELECT id, bv, title, mode, is_second, comment_count, start_time, end_time, status 
            FROM crawl_records 
            WHERE user_id = ?
            ORDER BY start_time DESC
            """, (current_user["id"],))
        
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 转换日期时间格式为字符串
        for record in records:
            if record['start_time']:
                record['start_time'] = record['start_time']
            if record['end_time']:
                record['end_time'] = record['end_time']
        
        return {"records": records}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取特定爬取记录的评论
@app.get("/api/comments/{crawl_id}")
async def get_comments(
    crawl_id: int, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(30, ge=10, le=100), 
    username: str = None, 
    keyword: str = None,
    gender: str = None,
    min_reply_count: int = None,
    max_reply_count: int = None,
    min_like_count: int = None,
    max_like_count: int = None,
    show_second_level: bool = None,
    user_level: int = None,
    is_vip: str = None,
    start_time: str = None,
    end_time: str = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        conn = sqlite3.connect('bilibili_CH.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查用户是否有权限访问该爬取记录
        if current_user["level"] != 2:  # 非管理员需要验证所有权
            cursor.execute("SELECT user_id FROM crawl_records WHERE id = ?", (crawl_id,))
            record = cursor.fetchone()
            if not record or record["user_id"] != current_user["id"]:
                conn.close()
                raise HTTPException(status_code=403, detail="您没有权限访问此爬取记录")
        
        # 构建查询条件
        query_conditions = ["crawl_id = ?"] 
        query_params = [crawl_id]
        
        # 添加用户名搜索条件
        if username:
            query_conditions.append("username LIKE ?")
            query_params.append(f"%{username}%")
            
        # 添加关键词搜索条件
        if keyword:
            query_conditions.append("content LIKE ?")
            query_params.append(f"%{keyword}%")
            
        # 添加性别筛选条件
        if gender:
            query_conditions.append("gender = ?")
            query_params.append(gender)
            
        # 添加回复数筛选条件
        if min_reply_count is not None:
            query_conditions.append("reply_count >= ?")
            query_params.append(min_reply_count)
            
        if max_reply_count is not None:
            query_conditions.append("reply_count <= ?")
            query_params.append(max_reply_count)
            
        # 添加点赞数筛选条件
        if min_like_count is not None:
            query_conditions.append("like_count >= ?")
            query_params.append(min_like_count)
            
        if max_like_count is not None:
            query_conditions.append("like_count <= ?")
            query_params.append(max_like_count)
            
        # 添加二级评论筛选条件
        if show_second_level is not None:
            if not show_second_level:
                # 只显示一级评论
                query_conditions.append("parent_id = 0")
                
        # 添加用户等级筛选条件
        if user_level is not None:
            query_conditions.append("user_level = ?")
            query_params.append(user_level)
            
        # 添加VIP筛选条件
        if is_vip:
            query_conditions.append("is_vip = ?")
            query_params.append(is_vip)
            
        # 添加时间范围筛选条件
        if start_time:
            query_conditions.append("comment_time >= ?")
            query_params.append(start_time)
            
        if end_time:
            query_conditions.append("comment_time <= ?")
            query_params.append(end_time)
            

            
        # 构建WHERE子句
        where_clause = " AND ".join(query_conditions)
        
        # 获取总评论数
        count_query = f"SELECT COUNT(*) as count FROM comments WHERE {where_clause}"
        cursor.execute(count_query, query_params)
        total_count = cursor.fetchone()["count"]
        
        # 计算总页数
        total_pages = (total_count + page_size - 1) // page_size
        
        # 获取当前页的评论
        offset = (page - 1) * page_size
        comments_query = f"""
        SELECT * FROM comments 
        WHERE {where_clause} 
        ORDER BY comment_index 
        LIMIT ? OFFSET ?
        """
        cursor.execute(comments_query, query_params + [page_size, offset])
        
        comments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 转换日期时间格式为字符串
        for comment in comments:
            if comment['comment_time']:
                comment['comment_time'] = comment['comment_time']
        
        return {
            "comments": comments,
            "pagination": {
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取爬取记录详情
@app.get("/api/crawl_records/{crawl_id}")
async def get_crawl_record_detail(crawl_id: int, current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('bilibili_CH.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查用户是否有权限访问该爬取记录
        if current_user["level"] != 2:  # 非管理员需要验证所有权
            cursor.execute("SELECT user_id FROM crawl_records WHERE id = ?", (crawl_id,))
            record = cursor.fetchone()
            if not record or record["user_id"] != current_user["id"]:
                conn.close()
                raise HTTPException(status_code=403, detail="您没有权限访问此爬取记录")
        
        # 获取爬取记录详情
        if current_user["level"] == 2:  # 管理员可以看到用户信息
            cursor.execute("""
            SELECT cr.id, cr.bv, cr.title, cr.mode, cr.is_second, cr.comment_count, cr.start_time, cr.end_time, cr.status, u.username 
            FROM crawl_records cr
            LEFT JOIN users u ON cr.user_id = u.id
            WHERE cr.id = ?
            """, (crawl_id,))
        else:
            cursor.execute("""
            SELECT id, bv, title, mode, is_second, comment_count, start_time, end_time, status 
            FROM crawl_records 
            WHERE id = ?
            """, (crawl_id,))
        
        record = cursor.fetchone()
        if not record:
            conn.close()
            raise HTTPException(status_code=404, detail="爬取记录不存在")
            
        record_dict = dict(record)
        
        # 转换日期时间格式为字符串
        if record_dict['start_time']:
            record_dict['start_time'] = record_dict['start_time']
        if record_dict['end_time']:
            record_dict['end_time'] = record_dict['end_time']
        
        conn.close()
        return record_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 删除爬取记录
@app.delete("/api/crawl_records/{crawl_id}")
async def delete_crawl_record(crawl_id: int, current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('bilibili_CH.db')
        cursor = conn.cursor()
        
        # 检查用户是否有权限删除该爬取记录
        if current_user["level"] != 2:  # 非管理员需要验证所有权
            cursor.execute("SELECT user_id FROM crawl_records WHERE id = ?", (crawl_id,))
            record = cursor.fetchone()
            if not record or record[0] != current_user["id"]:
                conn.close()
                raise HTTPException(status_code=403, detail="您没有权限删除此爬取记录")
        
        # 删除相关评论
        cursor.execute("DELETE FROM comments WHERE crawl_id = ?", (crawl_id,))
        
        # 删除爬取记录
        cursor.execute("DELETE FROM crawl_records WHERE id = ?", (crawl_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "爬取记录及相关评论已成功删除"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 下载爬取记录
@app.get("/api/crawl_records/{crawl_id}/download")
async def download_crawl_record(crawl_id: int, current_user: dict = Depends(get_current_user)):
    try:
        from fastapi.responses import StreamingResponse
        import io
        
        conn = sqlite3.connect('bilibili_CH.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查用户是否有权限下载该爬取记录
        if current_user["level"] != 2:  # 非管理员需要验证所有权
            cursor.execute("SELECT user_id FROM crawl_records WHERE id = ?", (crawl_id,))
            record = cursor.fetchone()
            if not record or record["user_id"] != current_user["id"]:
                conn.close()
                raise HTTPException(status_code=403, detail="您没有权限下载此爬取记录")
        
        # 获取爬取记录信息
        cursor.execute("SELECT title FROM crawl_records WHERE id = ?", (crawl_id,))
        record = cursor.fetchone()
        if not record:
            conn.close()
            raise HTTPException(status_code=404, detail="爬取记录不存在")
            
        title = record["title"]
        
        # 获取评论数据
        cursor.execute("""
        SELECT * FROM comments 
        WHERE crawl_id = ? 
        ORDER BY comment_index
        """, (crawl_id,))
        
        comments = cursor.fetchall()
        conn.close()
        
        if not comments:
            raise HTTPException(status_code=404, detail="该爬取记录没有评论数据")
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = ["评论序号", "父评论ID", "评论ID", "用户ID", "用户名", "用户等级", "性别", "评论内容", "评论时间", "回复数", "点赞数", "个性签名", "IP属地", "是否大会员", "头像链接"]
        writer.writerow(headers)
        
        # 写入数据
        for comment in comments:
            writer.writerow([
                comment["comment_index"],
                comment["parent_id"],
                comment["comment_id"],
                comment["user_id"],
                comment["username"],
                comment["user_level"],
                comment["gender"],
                comment["content"],
                comment["comment_time"],
                comment["reply_count"],
                comment["like_count"],
                comment["signature"],
                comment["ip_location"],
                comment["is_vip"],
                comment["avatar"]
            ])
        
        # 返回CSV文件
        output.seek(0)
        filename = f"{title}_评论数据.csv"
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={quote(filename)}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 下载评论数据
@app.get("/api/comments/{crawl_id}/download")
async def download_comments(
    crawl_id: int, 
    username: str = None, 
    keyword: str = None,
    gender: str = None,
    min_reply_count: int = None,
    max_reply_count: int = None,
    min_like_count: int = None,
    max_like_count: int = None,
    show_second_level: bool = None,
    user_level: int = None,
    is_vip: str = None,
    start_time: str = None,
    end_time: str = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        from fastapi.responses import StreamingResponse
        import io
        
        conn = sqlite3.connect('bilibili_CH.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查用户是否有权限下载该爬取记录的评论
        if current_user["level"] != 2:  # 非管理员需要验证所有权
            cursor.execute("SELECT user_id FROM crawl_records WHERE id = ?", (crawl_id,))
            record = cursor.fetchone()
            if not record or record["user_id"] != current_user["id"]:
                conn.close()
                raise HTTPException(status_code=403, detail="您没有权限下载此爬取记录的评论")
        
        # 获取爬取记录信息
        cursor.execute("SELECT title FROM crawl_records WHERE id = ?", (crawl_id,))
        record = cursor.fetchone()
        if not record:
            conn.close()
            raise HTTPException(status_code=404, detail="爬取记录不存在")
            
        title = record["title"]
        
        # 构建查询条件
        query_conditions = ["crawl_id = ?"] 
        query_params = [crawl_id]
        
        # 添加用户名搜索条件
        if username:
            query_conditions.append("username LIKE ?")
            query_params.append(f"%{username}%")
            
        # 添加关键词搜索条件
        if keyword:
            query_conditions.append("content LIKE ?")
            query_params.append(f"%{keyword}%")
            
        # 添加性别筛选条件
        if gender:
            query_conditions.append("gender = ?")
            query_params.append(gender)
            
        # 添加回复数筛选条件
        if min_reply_count is not None:
            query_conditions.append("reply_count >= ?")
            query_params.append(min_reply_count)
            
        if max_reply_count is not None:
            query_conditions.append("reply_count <= ?")
            query_params.append(max_reply_count)
            
        # 添加点赞数筛选条件
        if min_like_count is not None:
            query_conditions.append("like_count >= ?")
            query_params.append(min_like_count)
            
        if max_like_count is not None:
            query_conditions.append("like_count <= ?")
            query_params.append(max_like_count)
            
        # 添加二级评论筛选条件
        if show_second_level is not None:
            if not show_second_level:
                # 只显示一级评论
                query_conditions.append("parent_id = 0")
                
        # 添加用户等级筛选条件
        if user_level is not None:
            query_conditions.append("user_level = ?")
            query_params.append(user_level)
            
        # 添加VIP筛选条件
        if is_vip:
            query_conditions.append("is_vip = ?")
            query_params.append(is_vip)
            
        # 添加时间范围筛选条件
        if start_time:
            query_conditions.append("comment_time >= ?")
            query_params.append(start_time)
            
        if end_time:
            query_conditions.append("comment_time <= ?")
            query_params.append(end_time)
            
        # 构建WHERE子句
        where_clause = " AND ".join(query_conditions)
        
        # 获取评论数据
        comments_query = f"""
        SELECT * FROM comments 
        WHERE {where_clause} 
        ORDER BY comment_index
        """
        cursor.execute(comments_query, query_params)
        
        comments = cursor.fetchall()
        conn.close()
        
        if not comments:
            raise HTTPException(status_code=404, detail="没有找到符合条件的评论数据")
        
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = ["评论序号", "父评论ID", "评论ID", "用户ID", "用户名", "用户等级", "性别", "评论内容", "评论时间", "回复数", "点赞数", "个性签名", "IP属地", "是否大会员", "头像链接"]
        writer.writerow(headers)
        
        # 写入数据
        for comment in comments:
            writer.writerow([
                comment["comment_index"],
                comment["parent_id"],
                comment["comment_id"],
                comment["user_id"],
                comment["username"],
                comment["user_level"],
                comment["gender"],
                comment["content"],
                comment["comment_time"],
                comment["reply_count"],
                comment["like_count"],
                comment["signature"],
                comment["ip_location"],
                comment["is_vip"],
                comment["avatar"]
            ])
        
        # 返回CSV文件
        output.seek(0)
        filename = f"{title}_评论数据"
        if username:
            filename += f"_用户名({username})"
        if keyword:
            filename += f"_关键词({keyword})"
        if gender:
            filename += f"_性别({gender})"
        if user_level is not None:
            filename += f"_等级({user_level})"
        if is_vip:
            filename += f"_VIP({is_vip})"
        if min_reply_count is not None or max_reply_count is not None:
            reply_range = ""
            if min_reply_count is not None:
                reply_range += f"{min_reply_count}-"
            else:
                reply_range += "0-"
            if max_reply_count is not None:
                reply_range += str(max_reply_count)
            else:
                reply_range += "∞"
            filename += f"_回复数({reply_range})"
        if min_like_count is not None or max_like_count is not None:
            like_range = ""
            if min_like_count is not None:
                like_range += f"{min_like_count}-"
            else:
                like_range += "0-"
            if max_like_count is not None:
                like_range += str(max_like_count)
            else:
                like_range += "∞"
            filename += f"_点赞数({like_range})"
        if show_second_level is not None:
            if show_second_level:
                filename += "_包含二级评论"
            else:
                filename += "_仅一级评论"
        filename += ".csv"
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={quote(filename)}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=60001)