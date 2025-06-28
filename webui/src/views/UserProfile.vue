<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api_GetUserInfo } from '../api'
import { Refresh, User, Lock } from '@element-plus/icons-vue'

// 用户信息
const userInfo = ref({
  id: '',
  username: '',
  email: '',
  level: 0
})

// 加载状态
const loading = ref(false)

// 获取用户信息
const fetchUserInfo = async () => {
  loading.value = true
  try {
    const response = await api_GetUserInfo()
    userInfo.value = response.data
    ElMessage({
      message: '用户信息已更新',
      type: 'success',
      duration: 2000
    })
  } catch (error) {
    ElMessage({
      message: '获取用户信息失败：' + (error.response?.data?.detail || error.message),
      type: 'error',
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})

// 用户权限级别文本
const userLevelText = (level) => {
  switch (level) {
    case 1:
      return '普通用户'
    case 2:
      return '管理员'
    default:
      return '未知'
  }
}
</script>

<template>
  <div class="user-profile-container">
    <div class="page-header">
      <div class="header-content">
            <div class="title-section">
                <h1 class="page-title">
                  个人中心
                </h1>
            <p class="page-subtitle">查看和管理您的账户信息</p>
        </div>
      </div>
    </div>
    
    <el-row :gutter="20">
      <!-- 用户基本信息卡片 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <el-card class="user-profile-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>基本信息</h2>
              <el-button 
                type="primary" 
                @click="fetchUserInfo" 
                :loading="loading" 
                size="small"
                circle
              >
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <el-skeleton :loading="loading" animated>
            <template #default>
              <div class="user-info-content">
                <div class="user-avatar-container">
                  <el-avatar 
                    :size="100" 
                    :src="`https://api.dicebear.com/7.x/initials/svg?seed=${userInfo.username}`" 
                    class="user-avatar"
                  />
                  <h3 class="user-name">{{ userInfo.username }}</h3>
                  <div class="user-id">ID: {{ userInfo.id || '未设置' }}</div>
                </div>
                
                <el-divider>
                  <el-icon><User /></el-icon>
                </el-divider>
                
                <div class="user-details">
                  <div class="detail-item">
                    <span class="detail-label">邮箱</span>
                    <span class="detail-value">{{ userInfo.email }}</span>
                  </div>
                  
                  <div class="detail-item">
                    <span class="detail-label">账户类型</span>
                    <el-tag :type="userInfo.level === 2 ? 'danger' : 'success'" size="small">
                      {{ userLevelText(userInfo.level) }}
                    </el-tag>
                  </div>
                  
                  <div class="detail-item">
                    <span class="detail-label">账户状态</span>
                    <el-tag type="success" size="small">正常</el-tag>
                  </div>
                </div>
              </div>
            </template>
          </el-skeleton>
        </el-card>
      </el-col>
      
      <!-- 安全设置卡片 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <el-card class="security-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>安全设置</h2>
              <el-icon><Lock /></el-icon>
            </div>
          </template>
          
          <div class="security-options">
            <div class="security-item">
              <div class="security-info">
                <h4>修改密码</h4>
                <p>定期更换密码可以提高账户安全性</p>
              </div>
              <el-button type="primary" plain size="small">修改</el-button>
            </div>
            
            <el-divider></el-divider>
            
            <div class="security-item">
              <div class="security-info">
                <h4>更换邮箱</h4>
                <p>当前邮箱: {{ userInfo.email }}</p>
              </div>
              <el-button type="primary" plain size="small">更换</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
}

.user-profile-container {
  width: 100%;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-color-primary-dark-2);
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

.user-profile-card,
.security-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  height: 100%;
}

.user-profile-card:hover,
.security-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--el-color-primary);
}

.user-info-content {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.user-avatar {
  border: 4px solid var(--el-color-primary-light-8);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-name {
  margin: 15px 0 5px;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.user-id {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 10px;
}

.user-details {
  width: 100%;
  padding: 0 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.detail-value {
  color: var(--el-text-color-primary);
}

.security-options {
  padding: 10px 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.security-info h4 {
  margin: 0 0 5px;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.security-info p {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header-content {
    padding: 20px 24px;
  }
  
  .user-profile-container {
    padding: 15px 10px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .user-avatar {
    width: 80px;
    height: 80px;
  }
  
  .user-name {
    font-size: 18px;
  }
  
  .security-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .security-item .el-button {
    margin-top: 10px;
  }
}
</style>