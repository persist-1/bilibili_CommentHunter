import { defineStore } from 'pinia'
import api from '../api'

export const useCrawlerStore = defineStore('crawler', {
  state: () => ({
    // 爬取记录列表
    crawlRecords: [],
    // 当前选中的爬取记录
    currentRecord: null,
    // 当前爬取记录的评论
    comments: [],
    // 评论分页信息
    pagination: {
      total: 0,
      page: 1,
      pageSize: 30,
      totalPages: 0
    },
    // 加载状态
    loading: {
      records: false,
      comments: false,
      crawling: false
    },
    // 错误信息
    error: null
  }),
  
  actions: {
    // 开始爬取评论
    async crawlComments(params) {
      this.loading.crawling = true
      this.error = null
      
      try {
        const response = await api.crawlComments(params)
        // 爬取成功后刷新记录列表
        await this.fetchCrawlRecords()
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '爬取失败'
        throw error
      } finally {
        this.loading.crawling = false
      }
    },
    
    // 获取爬取记录列表
    async fetchCrawlRecords() {
      this.loading.records = true
      this.error = null
      
      try {
        const response = await api.getCrawlRecords()
        this.crawlRecords = response.records || []
      } catch (error) {
        this.error = error.response?.data?.detail || '获取爬取记录失败'
        this.crawlRecords = []
      } finally {
        this.loading.records = false
      }
    },
    
    // 获取爬取记录详情
    async fetchCrawlRecordDetail(id) {
      this.error = null
      
      try {
        const response = await api.getCrawlRecordDetail(id)
        this.currentRecord = response
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '获取爬取记录详情失败'
        throw error
      }
    },
    
    // 获取评论列表
    async fetchComments(crawlId, page = 1, pageSize = 30, username = '', keyword = '') {
      this.loading.comments = true
      this.error = null
      
      try {
        const response = await api.getComments(crawlId, page, pageSize, username, keyword) // 添加搜索参数
        this.comments = response.comments || []
        this.pagination = response.pagination || {
          total: 0,
          page,
          pageSize,
          totalPages: 0
        }
      } catch (error) {
        this.error = error.response?.data?.detail || '获取评论失败'
        this.comments = []
        this.pagination = {
          total: 0,
          page,
          pageSize,
          totalPages: 0
        }
      } finally {
        this.loading.comments = false
      }
    },
    
    // 更改每页显示数量
    async changePageSize(crawlId, pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.page = 1 // 重置到第一页
      await this.fetchComments(crawlId, 1, pageSize)
    },
    
    // 删除爬取记录
    async deleteCrawlRecord(recordId) {
      this.error = null
      try {
        await api.deleteCrawlRecord(recordId) // 假设 api.js 中有 deleteCrawlRecord 方法
        // 从本地列表中移除，或重新获取列表
        this.crawlRecords = this.crawlRecords.filter(record => record.id !== recordId)
        if (this.currentRecord && this.currentRecord.id === recordId) {
          this.clearCurrentData()
        }
      } catch (error) {
        this.error = error.response?.data?.detail || '删除爬取记录失败'
        throw error
      }
    },

    // 下载爬取记录 (CSV)
    async downloadCrawlRecord(recordId) {
      this.error = null
      try {
        const response = await api.downloadCrawlRecord(recordId) // 假设 api.js 中有 downloadCrawlRecord 方法
        // 处理下载，例如创建一个隐藏的a标签并点击
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const contentDisposition = response.headers['content-disposition']
        let fileName = `crawl_record_${recordId}.csv`
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/i)
            if (fileNameMatch.length === 2)
                fileName = fileNameMatch[1]
        }
        link.setAttribute('download', fileName)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.error = error.response?.data?.detail || '下载爬取记录失败'
        throw error
      }
    },

    // 下载评论数据 (CSV)
    async downloadCommentsData(crawlId, username = '', keyword = '') {
      this.error = null
      try {
        const response = await api.downloadComments(crawlId, username, keyword) // 假设 api.js 中有 downloadComments 方法
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const contentDisposition = response.headers['content-disposition']
        let fileName = `comments_crawl_${crawlId}.csv`
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/i)
            if (fileNameMatch.length === 2)
                fileName = fileNameMatch[1]
        }
        link.setAttribute('download', fileName)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.error = error.response?.data?.detail || '下载评论数据失败'
        throw error
      }
    },

    // 清除当前选中的记录和评论
    clearCurrentData() {
      this.currentRecord = null
      this.comments = []
      this.pagination = {
        total: 0,
        page: 1,
        pageSize: 30,
        totalPages: 0
      }
    }
  }
})