<template>
  <div class="global">
    <!-- 左侧图片区域 -->
    <div class="image-container">
      <div class="overlay"></div>
      <div class="image-placeholder">
        <img src="https://v2fy.com/asset/bilibili_wallpaper/3203841-d21cffd255ed1961.png" alt="Banner Image1" class="banner-image" />
      </div>
      <div class="welcome-text">
        <h2>基于FastAPI和Vue3的Bilibili视频评论爬取和展示系统</h2>
        <h1>欢迎使用</h1>
        <p>登录您的账户，开始探索</p>
      </div>
    </div>
    
    <div class="login-container">
      <div class="login_frame">
        <div class="logo">
          <img src="/yonghuguanli.png" alt="Login Icon" class="logo-image" />
        </div>
        <div class="title">账户登录</div>
        <p class="subtitle">欢迎回来，请输入您的账户信息</p>
        
        <form class="form">
          <div class="input-group">
            <div class="input-icon">
              <i class="icon-user"></i>
            </div>
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入用户名或邮箱"
              class="input-with-icon"
            />
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
        </form>
        
        <div class="remember-forgot">
          <label class="remember-me">
            <input type="checkbox" v-model="form.remember_me" />
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password">忘记密码?</a>
        </div>
        
        <button class="button_group" @click="login" :disabled="loading">
          <span>登录</span>
          <div class="button-effect"></div>
        </button>

        <div class="register-link">
          还没有账户? <router-link to="/register" class="register_point">立即注册</router-link>
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
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { api_Login } from "../api";

const route = useRoute();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  remember_me: false
});

const loading = ref(false);

// 登录
const login = () => {
  // 表单验证
  if (!form.username) {
    ElMessage.error("请输入用户名或邮箱");
    return;
  }
  if (!form.password) {
    ElMessage.error("请输入密码");
    return;
  }
  
  loading.value = true;
  
  api_Login(form).then((res) => {
    loading.value = false;
    
    // 存储用户信息
    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("name", res.data.name);
    localStorage.setItem("level", res.data.level);
    localStorage.setItem("username", res.data.username);

    ElMessage({
      message: "登录成功",
      type: "success",
    });

    // 如果有重定向地址，则跳转到重定向地址
    const redirectPath = route.query.redirect || "/";
    router.push(redirectPath);
  }).catch(error => {
    loading.value = false;
    if (error.response && error.response.data) {
      ElMessage.error(error.response.data.detail || "登录失败，请稍后重试");
    } else {
      ElMessage.error("登录失败，请检查网络连接");
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
  background: linear-gradient(135deg, rgba(32, 74, 202, 0.8) 0%, rgba(32, 74, 202, 0.4) 100%);
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

/* 右侧登录区域 */
.login-container {
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

.login_frame {
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
  border-color: #4a90e2;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.15);
}

.remember-forgot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 25px;
  font-size: 14px;
}

.remember-me {
  display: flex;
  align-items: center;
  color: #666;
  cursor: pointer;
}

.remember-me input {
  margin-right: 8px;
}

.forgot-password {
  color: #4a90e2;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-password:hover {
  color: #2a70c2;
  text-decoration: underline;
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
  background: linear-gradient(135deg, #4a90e2 0%, #2a70c2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.button_group:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 20px rgba(74, 144, 226, 0.3);
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

.register-link {
  margin-top: 25px;
  color: #666;
  font-size: 14px;
  text-align: center;
}

.register_point {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s;
}

.register_point:hover {
  color: #2a70c2;
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
  .login-container {
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
  .login-container {
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
  .login_frame {
    width: 90%;
    padding: 30px 20px;
  }
  .image-container {
    height: 30%;
  }
  .login-container {
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