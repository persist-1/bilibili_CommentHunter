<template>
  <div class="global">
    <!-- 左侧图片区域 -->
    <div class="image-container">
      <div class="overlay"></div>
      <div class="image-placeholder">
        <img src="https://v2fy.com/asset/bilibili_wallpaper/3203841-b5dde55f280d5633.png" alt="Banner Image" class="banner-image" />
      </div>
      <div class="welcome-text">
        <h4>基于FastAPI和Vue3的Bilibili视频评论爬取和展示系统</h4>
        <h1>创建账户</h1>
        <p>加入我们，开始您的探索之旅</p>
        <!--<h3>本网站用于参与"中国大学生计算机设计大赛"时在线预览小队作品</h3>-->
      </div>
    </div>
    
    <!-- 右侧注册区域 -->
    <div class="register-container">
      <div class="register_frame">
        <div class="logo">
          <img src="/yonghuguanli.png" alt="Register Icon" class="logo-image" />
        </div>
        <div class="title">账户注册</div>
        <p class="subtitle">创建您的账户，开始全新体验</p>
        
        <form class="form">
          <div class="input-group">
            <div class="input-icon">
              <i class="icon-user"></i>
            </div>
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入用户名"
              class="input-with-icon"
            />
          </div>
          <div class="input-group">
            <div class="input-icon">
              <i class="icon-email"></i>
            </div>
            <input
              type="email"
              v-model="form.email"
              placeholder="请输入邮箱"
              class="input-with-icon"
            />
          </div>
          <div class="input-group verification-code-group">
            <div class="input-icon">
              <i class="icon-code"></i>
            </div>
            <input
              type="text"
              v-model="form.code"
              placeholder="请输入验证码"
              class="input-with-icon verification-input"
            />
            <button 
              type="button" 
              class="verification-button" 
              @click="sendVerificationCode"
              :disabled="cooldown > 0 || sendingCode"
            >
              {{ cooldown > 0 ? `${cooldown}秒后重试` : (sendingCode ? '发送中...' : '获取验证码') }}
            </button>
          </div>
          <div class="input-group">
            <div class="input-icon">
              <i class="icon-lock"></i>
            </div>
            <input
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              class="input-with-icon"
            />
          </div>
          <div class="input-group">
            <div class="input-icon">
              <i class="icon-lock"></i>
            </div>
            <input
              type="password"
              v-model="form.pwd"
              placeholder="请确认密码"
              class="input-with-icon"
            />
          </div>
        </form>
        
        <button class="button_group" @click="register" :disabled="loading">
          <span>注册</span>
          <div class="button-effect"></div>
        </button>

        <div class="login-link">
          已有账户? <router-link to="/login" class="login_point">立即登录</router-link>
        </div>
      </div>
      
      <!-- 页脚版权信息 -->
      <div class="footer">
        <div class="copyright"> 2025 WSR. | 请务必不要使用本项目进行违法活动！</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { api_Register, api_Send_Email_Code } from "../api";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  pwd:"",
  email: "",
  code: ""
});

// 验证码冷却时间
const cooldown = ref(0);
let timer = null;

// 加载状态
const loading = ref(false);
const sendingCode = ref(false);

// 发送验证码
const sendVerificationCode = () => {
  // 验证邮箱格式
  const emailRegex = /^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$/;
  if (!form.email || !emailRegex.test(form.email)) {
    ElMessage.error("请输入正确的邮箱地址");
    return;
  }
  
  sendingCode.value = true;
  
  // 发送验证码请求
  api_Send_Email_Code({ email: form.email })
    .then((res) => {
      sendingCode.value = false;
      ElMessage({
        message: "验证码发送成功，请查收邮件",
        type: "success",
      });
      
      // 设置冷却时间
      cooldown.value = 120;
      timer = setInterval(() => {
        cooldown.value--;
        if (cooldown.value <= 0) {
          clearInterval(timer);
        }
      }, 1000);
    })
    .catch((err) => {
      sendingCode.value = false;
      if (err.response && err.response.data) {
        ElMessage.error(err.response.data.detail || "验证码发送失败，请稍后重试");
      } else {
        ElMessage.error("验证码发送失败，请检查网络连接");
      }
    });
};

// 组件卸载时清除定时器
onBeforeUnmount(() => {
  if (timer) {
    clearInterval(timer);
  }
});

//注册
const register = () => {
  // 验证表单
  if (!form.username) {
    ElMessage.error("请输入用户名");
    return;
  }
  if (!form.email) {
    ElMessage.error("请输入邮箱");
    return;
  }
  if (!form.code) {
    ElMessage.error("请输入验证码");
    return;
  }
  if (!form.password) {
    ElMessage.error("请输入密码");
    return;
  }
  if (form.password != form.pwd) {
    ElMessage.error("确认密码与输入密码不一致");
    return;
  }
  
  loading.value = true;

  api_Register(form).then((res) => {
    loading.value = false;
    
    // 存储用户信息
    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("name", res.data.name);
    localStorage.setItem("level", res.data.level);
    localStorage.setItem("username", res.data.username);
    
    ElMessage({
      message: "注册成功，已自动登录",
      type: "success",
    });
      // 跳转到首页
      router.push("/");
  }).catch(err => {
    loading.value = false;
    if (err.response && err.response.data) {
      ElMessage.error(err.response.data.detail || "注册失败，请稍后重试");
    } else {
      ElMessage.error("注册失败，请检查网络连接");
    }
  });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* 图标字体 */
@font-face {
  font-family: 'login-icons';
  src: url('/font/remixicon.woff2') format('woff2');
}

.icon-user:before {
  content: '\1F464';
  font-family: sans-serif;
}

.icon-lock:before {
  content: '\1F512';
  font-family: sans-serif;
}

.icon-email:before {
  content: '\2709';
  font-family: sans-serif;
}

.icon-code:before {
  content: '\1F4AC';
  font-family: sans-serif;
}

/* 全局样式 */
.global {
  width: 100%;
  height: 100vh;
  background-color: #f8faff;
  display: flex;
  position: relative;
  overflow: hidden;
  font-family: 'Poppins', sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
}

/* 左侧图片区域 */
.image-container {
  width: 55%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(76, 29, 149, 0.85) 0%, rgba(124, 58, 237, 0.4) 100%);
  z-index: 1;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: scale 40s infinite alternate;
}

@keyframes scale {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.1);
  }
}

.welcome-text {
  position: relative;
  z-index: 2;
  color: white;
  text-align: center;
  max-width: 80%;
  animation: fadeIn 1s ease-out;
}

.welcome-text h1 {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.welcome-text p {
  font-size: 1.2rem;
  font-weight: 300;
  opacity: 0.9;
}

/* 右侧注册区域 */
.register-container {
  width: 45%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  background-color: #ffffff;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);
}

.register_frame {
  width: 420px;
  background-color: white;
  border-radius: 16px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
  animation: slideIn 0.8s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.logo {
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.logo img {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 4px solid white;
}

.logo-image {
  background-color: #fff;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 14px;
  color: #888;
  margin-bottom: 30px;
  text-align: center;
}

.form {
  width: 100%;
  margin-top: 10px;
}

.input-group {
  position: relative;
  margin-bottom: 24px;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
  font-size: 18px;
  z-index: 1;
}

.input-with-icon {
  width: 100%;
  height: 54px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  font-size: 15px;
  padding: 0 15px 0 45px;
  transition: all 0.3s ease;
  color: #333;
  box-sizing: border-box;
}

.input-with-icon:focus {
  outline: none;
  border-color: #8b5cf6;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.verification-code-group {
  display: flex;
  align-items: center;
}

.verification-input {
  flex: 1;
}

.verification-button {
  margin-left: 10px;
  padding: 0 15px;
  height: 54px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.verification-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 7px 20px rgba(124, 58, 237, 0.3);
}

.verification-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button_group {
  width: 100%;
  height: 54px;
  font-size: 16px;
  border: none;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-top: 10px;
}

.button_group:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 20px rgba(124, 58, 237, 0.3);
}

.button_group:active {
  transform: translateY(0);
}

.button-effect {
  position: absolute;
  background: rgba(255, 255, 255, 0.3);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  transform: scale(0);
  opacity: 0;
  transition: transform 0.6s, opacity 0.6s;
}

.button_group:hover .button-effect {
  transform: scale(3);
  opacity: 0;
  transition: transform 0.6s, opacity 0.6s;
}

.login-link {
  margin-top: 25px;
  color: #666;
  font-size: 14px;
  text-align: center;
}

.login_point {
  color: #8b5cf6;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s;
}

.login_point:hover {
  color: #7c3aed;
  text-decoration: underline;
}

/* 页脚版权信息 */
.footer {
  position: relative;
  width: 100%;
  text-align: center;
  color: #888;
  font-size: 14px;
  margin-top: 30px;
}

.copyright {
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .image-container {
    width: 45%;
  }
  .register-container {
    width: 55%;
  }
}

@media (max-width: 992px) {
  .global {
    flex-direction: column;
  }
  .image-container {
    width: 100%;
    height: 35%;
  }
  .register-container {
    width: 100%;
    height: 65%;
  }
  .welcome-text h1 {
    font-size: 2.5rem;
  }
  .welcome-text p {
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .register_frame {
    width: 90%;
    padding: 30px 20px;
  }
  .image-container {
    height: 30%;
  }
  .register-container {
    height: 70%;
  }
  .welcome-text h1 {
    font-size: 2rem;
  }
  .logo img {
    width: 70px;
    height: 70px;
  }
  .title {
    font-size: 24px;
  }
}
</style>
