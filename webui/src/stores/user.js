import { defineStore } from 'pinia'
import { api_Login, api_Register, api_Send_Email_Code, api_GetUserInfo } from '../api/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    user: null,
    // 登录状态
    isLoggedIn: false,
    // 加载状态
    loading: {
      login: false,
      register: false,
      sendCode: false,
      getUserInfo: false
    },
    // 错误信息
    error: null
  }),

  getters: {
    // 用户权限等级
    userLevel: (state) => state.user?.level || 0,
    // 是否为管理员
    isAdmin: (state) => state.user?.level === 2,
    // 用户名
    username: (state) => state.user?.username || '',
    // 用户昵称
    name: (state) => state.user?.name || ''
  },

  actions: {
    // 初始化用户状态（从本地存储恢复）
    initUser() {
      const token = localStorage.getItem('token')
      const name = localStorage.getItem('name')
      const level = localStorage.getItem('level')
      const username = localStorage.getItem('username')
      
      if (token && name && level && username) {
        this.user = {
          name,
          level: parseInt(level),
          username
        }
        this.isLoggedIn = true
      }
    },

    // 用户登录
    async login(credentials) {
      this.loading.login = true
      this.error = null
      
      try {
        const response = await api_Login(credentials)
        const { token, user } = response.data
        
        // 保存到本地存储
        localStorage.setItem('token', token)
        localStorage.setItem('name', user.name)
        localStorage.setItem('level', user.level.toString())
        localStorage.setItem('username', user.username)
        
        // 更新状态
        this.user = user
        this.isLoggedIn = true
        
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '登录失败'
        throw error
      } finally {
        this.loading.login = false
      }
    },

    // 用户注册
    async register(userData) {
      this.loading.register = true
      this.error = null
      
      try {
        const response = await api_Register(userData)
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败'
        throw error
      } finally {
        this.loading.register = false
      }
    },

    // 发送邮箱验证码
    async sendEmailCode(email) {
      this.loading.sendCode = true
      this.error = null
      
      try {
        const response = await api_Send_Email_Code({ email })
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '发送验证码失败'
        throw error
      } finally {
        this.loading.sendCode = false
      }
    },

    // 获取用户信息
    async getUserInfo() {
      this.loading.getUserInfo = true
      this.error = null
      
      try {
        const response = await api_GetUserInfo()
        this.user = response.data
        this.isLoggedIn = true
        
        // 更新本地存储
        localStorage.setItem('name', this.user.name)
        localStorage.setItem('level', this.user.level.toString())
        localStorage.setItem('username', this.user.username)
        
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '获取用户信息失败'
        // 如果获取用户信息失败，可能是token过期，清除登录状态
        this.logout()
        throw error
      } finally {
        this.loading.getUserInfo = false
      }
    },

    // 用户登出
    logout() {
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('name')
      localStorage.removeItem('level')
      localStorage.removeItem('username')
      
      // 重置状态
      this.user = null
      this.isLoggedIn = false
      this.error = null
    },

    // 清除错误信息
    clearError() {
      this.error = null
    }
  }
})