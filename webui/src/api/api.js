import axios from 'axios'

// 创建用户相关的axios实例
const userApi = axios.create({
  baseURL: 'https://bilibili-ch-backend.persist1.cn/api/user',
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 创建爬虫相关的axios实例
const crawlApi = axios.create({
  baseURL: 'https://bilibili-ch-backend.persist1.cn/api',
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 用户API请求拦截器
userApi.interceptors.request.use(
  config => {
    // 如果有token，添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 爬虫API请求拦截器
crawlApi.interceptors.request.use(
  config => {
    // 如果有token，添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 用户API响应拦截器
userApi.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 处理401错误（未授权）
    if (error.response && error.response.status === 401) {
      // 清除本地存储的token
      localStorage.removeItem('token')
      localStorage.removeItem('name')
      localStorage.removeItem('level')
      localStorage.removeItem('username')
      
      // 跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

// 爬虫API响应拦截器
crawlApi.interceptors.response.use(
  response => {
    // 对于blob类型的响应（文件下载），返回完整的response对象
    if (response.config.responseType === 'blob') {
      return response
    }
    // 对于其他类型的响应，只返回data部分
    return response.data
  },
  error => {
    // 处理401错误（未授权）
    if (error.response && error.response.status === 401) {
      // 清除本地存储的token
      localStorage.removeItem('token')
      localStorage.removeItem('name')
      localStorage.removeItem('level')
      localStorage.removeItem('username')
      
      // 跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

// 用户API方法
export const api_Login = (data) => {
  return userApi.post('/login', data)
}

export const api_Register = (data) => {
  return userApi.post('/register', data)
}

export const api_Send_Email_Code = (data) => {
  return userApi.post('/send_email_code', data)
}

export const api_GetUserInfo = () => {
  return userApi.get('/me')
}

// 爬虫API方法
export const crawlComments = (params) => {
  return crawlApi.post('/crawl', params)
}

export const getCrawlRecords = () => {
  return crawlApi.get('/crawl_records')
}

export const getCrawlRecordDetail = (id) => {
  return crawlApi.get(`/crawl_records/${id}`)
}

export const getComments = (crawlId, page = 1, pageSize = 30, filters = {}) => {
  const params = {
    page,
    page_size: pageSize
  }
  
  // 添加筛选参数，只有非空值才会被传递
  if (filters.username) params.username = filters.username
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.gender) params.gender = filters.gender
  if (filters.minReplyCount !== undefined && filters.minReplyCount !== null) params.min_reply_count = filters.minReplyCount
  if (filters.maxReplyCount !== undefined && filters.maxReplyCount !== null) params.max_reply_count = filters.maxReplyCount
  if (filters.minLikeCount !== undefined && filters.minLikeCount !== null) params.min_like_count = filters.minLikeCount
  if (filters.maxLikeCount !== undefined && filters.maxLikeCount !== null) params.max_like_count = filters.maxLikeCount
  if (filters.showSecondLevel !== undefined && filters.showSecondLevel !== null) params.show_second_level = filters.showSecondLevel
  if (filters.userLevel !== undefined && filters.userLevel !== null) params.user_level = filters.userLevel
  if (filters.isVip) params.is_vip = filters.isVip
  if (filters.startTime) params.start_time = filters.startTime
  if (filters.endTime) params.end_time = filters.endTime
  
  return crawlApi.get(`/comments/${crawlId}`, { params })
}

// 删除爬取记录
export const deleteCrawlRecord = (recordId) => {
  return crawlApi.delete(`/crawl_records/${recordId}`)
}

// 下载爬取记录 (CSV)
export const downloadCrawlRecord = (recordId) => {
  return crawlApi.get(`/crawl_records/${recordId}/download`, {
    responseType: 'blob' // 重要：确保响应类型为 blob 以下载文件
  })
}

// 下载评论数据 (CSV)
export const downloadComments = (crawlId, filters = {}) => {
  const params = {}
  
  // 添加筛选参数，只有非空值才会被传递
  if (filters.username) params.username = filters.username
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.gender) params.gender = filters.gender
  if (filters.minReplyCount !== undefined && filters.minReplyCount !== null) params.min_reply_count = filters.minReplyCount
  if (filters.maxReplyCount !== undefined && filters.maxReplyCount !== null) params.max_reply_count = filters.maxReplyCount
  if (filters.minLikeCount !== undefined && filters.minLikeCount !== null) params.min_like_count = filters.minLikeCount
  if (filters.maxLikeCount !== undefined && filters.maxLikeCount !== null) params.max_like_count = filters.maxLikeCount
  if (filters.showSecondLevel !== undefined && filters.showSecondLevel !== null) params.show_second_level = filters.showSecondLevel
  if (filters.userLevel !== undefined && filters.userLevel !== null) params.user_level = filters.userLevel
  if (filters.isVip) params.is_vip = filters.isVip
  if (filters.startTime) params.start_time = filters.startTime
  if (filters.endTime) params.end_time = filters.endTime
  
  return crawlApi.get(`/comments/${crawlId}/download`, {
    params,
    responseType: 'blob' // 重要：确保响应类型为 blob 以下载文件
  })
}

// 默认导出所有API方法
export default {
  api_Login,
  api_Register,
  api_Send_Email_Code,
  api_GetUserInfo,
  crawlComments,
  getCrawlRecords,
  getCrawlRecordDetail,
  getComments,
  deleteCrawlRecord,
  downloadCrawlRecord,
  downloadComments
}