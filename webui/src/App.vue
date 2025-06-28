<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, DataAnalysis, User, InfoFilled, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 当前激活的菜单项
const activeMenu = ref(route.path)

// 用户信息
const username = ref('')
const userLevel = ref(0)
const isLoggedIn = ref(false)

// 响应式布局 - 是否为移动端模式
const isMobile = ref(false)

// 检测窗口大小变化
const checkMobileMode = () => {
  // 当横向分辨率小于竖向分辨率时，为移动端模式
  isMobile.value = window.innerWidth <= window.innerHeight
}

// 监听路由变化，更新激活的菜单项
router.afterEach((to) => {
  activeMenu.value = to.path
  // 检查登录状态，确保在登录/注册后能正确显示菜单栏
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    username.value = localStorage.getItem('username') || ''
    userLevel.value = parseInt(localStorage.getItem('level') || '0')
  } else {
    isLoggedIn.value = false
  }
})

// 菜单项点击事件
const handleMenuSelect = (index) => {
  router.push(index)
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 清除本地存储的用户信息
    localStorage.removeItem('token')
    localStorage.removeItem('name')
    localStorage.removeItem('level')
    localStorage.removeItem('username')
    
    // 显示退出成功消息
    ElMessage({
      type: 'success',
      message: '退出登录成功'
    })
    
    // 重定向到登录页
    router.push('/login')
  }).catch(() => {})
}

// 组件挂载时检查登录状态和设备类型
onMounted(() => {
  // 检查登录状态
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    username.value = localStorage.getItem('username') || ''
    userLevel.value = parseInt(localStorage.getItem('level') || '0')
    
    // 如果已登录但当前路径是登录或注册页，则重定向到首页
    if (route.path === '/login' || route.path === '/register') {
      router.push('/crawl')
    }
  } else {
    isLoggedIn.value = false
    
    // 如果未登录且当前路径需要登录权限，则重定向到登录页
    if (route.meta.requiresAuth) {
      router.push('/login')
    }
  }
  
  // 初始检测设备类型
  checkMobileMode()
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', checkMobileMode)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', checkMobileMode)
})
</script>

<template>
  <div class="app-container" :class="{ 'is-mobile': isMobile }">
    <el-container class="outer-container">
      <!-- 头部 -->
      <el-header height="60px">
        <div class="header-content">
          <div class="header-left">
            <h1 class="app-title">B站评论爬取系统</h1>
          </div>
          <div class="user-info" v-if="isLoggedIn">
            <span class="username">{{ username }}</span>
            <span class="user-level">权限等级: {{ userLevel }}</span>
            <el-button class="logout-btn" type="text" @click="logout">退出登录</el-button>
          </div>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <!-- PC模式侧边栏菜单 -->
        <el-aside width="220px" v-if="isLoggedIn && !isMobile">
          <div class="sidebar-wrapper">
            <div class="menu-header">
              <el-avatar :size="40" class="menu-avatar">{{ username.charAt(0).toUpperCase() }}</el-avatar>
              <div class="menu-user-info">
                <div class="menu-username">{{ username }}</div>
                <div class="menu-user-level">{{ userLevel === 2 ? '管理员' : '普通用户' }}</div>
              </div>
            </div>
            <el-menu
              style="width: var(--sidebar-width); border-right: none;"
              :default-active="activeMenu"
              @select="handleMenuSelect"
              router
              background-color="#001529"
              text-color="#ffffff"
              active-text-color="#409EFF"
            >
              <el-menu-item index="/crawl">
                <el-icon><Document /></el-icon>
                <span>数据爬取</span>
              </el-menu-item>
              <el-menu-item index="/display">
                <el-icon><DataAnalysis /></el-icon>
                <span>数据展示</span>
              </el-menu-item>
              <el-menu-item index="/charts">
                <el-icon><TrendCharts /></el-icon>
                <span>数据图表</span>
              </el-menu-item>
              <el-menu-item index="/profile">
                <el-icon><User /></el-icon>
                <span>我的信息</span>
              </el-menu-item>
              <el-menu-item index="/project-intro">
                <el-icon><InfoFilled /></el-icon>
                <span>项目介绍</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-aside>
        
        <!-- 主要内容区域 -->
        <el-container>
          <el-main>
            <!-- 登录状态下显示路由内容 -->
            <div v-if="isLoggedIn || route.path === '/login' || route.path === '/register'">
              <router-view></router-view>
            </div>
            <!-- 未登录且不在登录/注册页时显示提示 -->
            <div v-else class="login-required">
              <h2>请先登录</h2>
              <el-button type="primary" @click="router.push('/login')">前往登录</el-button>
            </div>
          </el-main>
        </el-container>
      </el-container>
      
      <!-- 移动端底部菜单 -->
      <div class="mobile-menu" v-if="isLoggedIn && isMobile">
        <el-menu
          class="mobile-menu-bar"
          :default-active="activeMenu"
          @select="handleMenuSelect"
          router
          mode="horizontal"
          background-color="#001529"
          text-color="#ffffff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/crawl" class="mobile-menu-item">
            <el-icon><Document /></el-icon>
            <span>爬取</span>
          </el-menu-item>
          <el-menu-item index="/display" class="mobile-menu-item">
            <el-icon><DataAnalysis /></el-icon>
            <span>展示</span>
          </el-menu-item>
          <el-menu-item index="/charts" class="mobile-menu-item">
            <el-icon><TrendCharts /></el-icon>
            <span>图表</span>
          </el-menu-item>
          <el-menu-item index="/profile" class="mobile-menu-item">
            <el-icon><User /></el-icon>
            <span>我的</span>
          </el-menu-item>
          <el-menu-item index="/project-intro" class="mobile-menu-item">
            <el-icon><InfoFilled /></el-icon>
            <span>介绍</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-container>
  </div>
</template>

<style>
/* 全局CSS变量 */
:root {
  /* 主题色 */
  --primary-color: #409EFF;
  --primary-light: #a0cfff;
  --primary-dark: #337ecc;
  
  /* 背景色 */
  --dark-bg-color: #001529;
  --light-bg-color: #f5f7fa;
  --content-bg-color: #ffffff;
  
  /* 文本色 */
  --text-color: #333333;
  --text-secondary: #666666;
  --text-light: #f0f0f0;
  
  /* 边框和阴影 */
  --border-color: #e6e6e6;
  --shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  
  /* 侧边栏 */
  --sidebar-width: 220px;
  --sidebar-bg-color: #001529;
  --sidebar-text-color: #ffffff;
  --sidebar-active-text-color: #409EFF;
  
  /* 移动端菜单 */
  --mobile-menu-height: 60px;
  --mobile-menu-bg-color: #001529;
  --mobile-menu-text-color: #ffffff;
  --mobile-menu-active-text-color: #409EFF;
  
  /* 过渡动画 */
  --transition-speed: 0.3s;
}

/* 基础布局 */
.app-container {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--light-bg-color);
}

.outer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: row !important; /* 确保PC模式下是水平布局 */
}

/* 头部样式 */
.el-header {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 10;
  box-shadow: var(--shadow);
  height: 60px !important;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  color: white;
}

.username {
  font-size: 14px;
  margin-right: 10px;
  font-weight: 500;
}

.user-level {
  font-size: 12px;
  margin-right: 15px;
  color: var(--text-light);
  background-color: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
}

.logout-btn {
  color: white;
  font-size: 14px;
  transition: all var(--transition-speed);
}

.logout-btn:hover {
  color: #f0f0f0;
  transform: translateY(-1px);
}

/* PC模式侧边栏样式 */
.el-aside {
  width: var(--sidebar-width) !important;
  background-color: var(--sidebar-bg-color);
  transition: all var(--transition-speed);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  overflow: hidden;
  position: relative;
}

.sidebar-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
}

.el-menu-vertical {
  height: calc(100% - 80px);
  border-right: none;
  width: var(--sidebar-width);
}

.menu-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 10px;
}

.menu-avatar {
  background-color: var(--primary-color);
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all var(--transition-speed);
}

.menu-avatar:hover {
  transform: scale(1.05);
}

.menu-user-info {
  margin-left: 10px;
  overflow: hidden;
}

.menu-username {
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-user-level {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 0;
  border-radius: 0 24px 24px 0;
  margin-right: 16px;
  transition: all var(--transition-speed);
}

.el-menu-item.is-active {
  background-color: rgba(64, 158, 255, 0.1);
  font-weight: 500;
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

.el-main {
  padding: 20px;
  background-color: var(--light-bg-color);
  overflow-y: auto;
  flex: 1;
  transition: all var(--transition-speed);
}

/* 移动端模式样式 */
.is-mobile .main-container {
  padding-bottom: var(--mobile-menu-height); /* 为底部菜单留出空间 */
}

.mobile-menu {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0;
  background-color: var(--mobile-menu-bg-color);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.2);
  z-index: 100;
  height: var(--mobile-menu-height);
}

.mobile-menu-bar {
  display: flex;
  justify-content: space-around;
  width: 100%;
  border: none;
  height: var(--mobile-menu-height);
}

.mobile-menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: var(--mobile-menu-height);
  width: 25%; /* 固定每个按钮占25%宽度 */
  flex: 1;
  padding: 0 5px !important; /* 减小内边距 */
  box-sizing: border-box;
}

.mobile-menu-item .el-icon {
  margin-right: 0 !important;
  margin-bottom: 2px;
  font-size: 16px;
}

.mobile-menu-item span {
  font-size: 10px;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  display: block;
  text-align: center;
}

/* 覆盖Element Plus的一些默认样式 */
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  overflow: hidden;
  color: var(--text-color);
}

#app {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  max-width: none;
  text-align: left;
  overflow: hidden;
}

/* 卡片样式优化 */
.el-card {
  border-radius: 8px;
  border: none;
  box-shadow: var(--card-shadow) !important;
  transition: all var(--transition-speed);
  overflow: hidden;
}

.el-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12) !important;
}

.el-card__header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
}

/* 按钮样式优化 */
.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border: none;
  transition: all var(--transition-speed);
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .el-header {
    padding: 0 10px;
  }
  
  .app-title {
    font-size: 18px;
  }
  
  .el-main {
    padding: 15px 10px;
  }
  
  .mobile-menu-item {
    padding: 0 5px !important;
  }
}
/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 登录提示样式 */
.login-required {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
  text-align: center;
  background-color: var(--light-bg-color);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

.login-required h2 {
  margin-bottom: 20px;
  color: var(--primary-color);
}

/* 调试样式 */
.el-main {
  background-color: var(--light-bg-color);
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.el-main > div {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
