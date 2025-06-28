<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useUserStore } from '../stores/user'
import { getCrawlRecords, getComments, deleteCrawlRecord, downloadComments } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, Download, Search, Delete, Filter, 
  Male, Female, Star, ChatDotRound, 
  Calendar, User
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const userLevel = ref(userStore.user?.level || 0)

// 基础数据
const selectedRecordId = ref(null)
const pageSize = ref(30)
const currentPage = ref(1)
const crawlRecords = ref([])
const comments = ref([])
const totalComments = ref(0)
const totalPages = ref(0)
const loading = ref(false)
const commentsLoading = ref(false)

// 筛选条件
const filters = reactive({
  username: '',
  keyword: '',
  gender: '',
  minReplyCount: null,
  maxReplyCount: null,
  minLikeCount: null,
  maxLikeCount: null,
  showSecondLevel: true,
  userLevel: null,
  isVip: '',
  dateRange: []
})

// 筛选面板显示状态
const showFilters = ref(false)

// 评论分页大小选项
const pageSizeOptions = [30, 60, 100]

// 计算属性
const isAdmin = computed(() => userLevel.value === 2)

const selectedRecord = computed(() => {
  return crawlRecords.value.find(record => record.id === selectedRecordId.value)
})

// 性别选项
const genderOptions = [
  { label: '全部', value: '' },
  { label: '男', value: '男' },
  { label: '女', value: '女' },
  { label: '保密', value: '保密' }
]

// 用户等级选项
const levelOptions = [
  { label: '全部', value: null },
  { label: 'Lv0', value: 0 },
  { label: 'Lv1', value: 1 },
  { label: 'Lv2', value: 2 },
  { label: 'Lv3', value: 3 },
  { label: 'Lv4', value: 4 },
  { label: 'Lv5', value: 5 },
  { label: 'Lv6', value: 6 }
]

// 会员状态选项
const vipOptions = [
  { label: '全部', value: '' },
  { label: '会员', value: '是' },
  { label: '非会员', value: '否' }
]

// 监听页码变化
watch(currentPage, async (newPage) => {
  if (selectedRecordId.value) {
    await fetchComments()
  }
})

// 监听每页显示数量变化
watch(pageSize, async (newSize) => {
  if (selectedRecordId.value) {
    currentPage.value = 1 // 重置到第一页
    await fetchComments()
  }
})

// 处理记录选择
const handleRecordSelect = (recordId) => {
  selectedRecordId.value = recordId
  currentPage.value = 1
  fetchComments()
}

// 刷新评论
const refreshComments = () => {
  if (selectedRecordId.value) {
    fetchComments()
  }
}

// 获取评论
const fetchComments = async () => {
  if (!selectedRecordId.value) return
  
  try {
    commentsLoading.value = true
    
    // 构建筛选参数
    const filterParams = {
      username: filters.username,
      keyword: filters.keyword,
      gender: filters.gender,
      minReplyCount: filters.minReplyCount,
      maxReplyCount: filters.maxReplyCount,
      minLikeCount: filters.minLikeCount,
      maxLikeCount: filters.maxLikeCount,
      showSecondLevel: filters.showSecondLevel,
      userLevel: filters.userLevel,
      isVip: filters.isVip
    }
    
    // 处理时间范围
    if (filters.dateRange && filters.dateRange.length === 2) {
      filterParams.startTime = filters.dateRange[0]
      filterParams.endTime = filters.dateRange[1]
    }
    
    const response = await getComments(
      selectedRecordId.value,
      currentPage.value,
      pageSize.value,
      filterParams
    )
    
    comments.value = response.comments || []
    totalComments.value = response.pagination?.total || 0
    totalPages.value = response.pagination?.total_pages || 0
  } catch (error) {
    ElMessage.error('获取评论失败：' + error.message)
  } finally {
    commentsLoading.value = false
  }
}

// 刷新爬取记录
const refreshRecords = async () => {
  try {
    loading.value = true
    const response = await getCrawlRecords()
    crawlRecords.value = response.records || []
  } catch (error) {
    ElMessage.error('获取爬取记录失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 切换筛选面板
const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

// 重置筛选条件
const resetFilters = () => {
  Object.assign(filters, {
    username: '',
    keyword: '',
    gender: '',
    minReplyCount: null,
    maxReplyCount: null,
    minLikeCount: null,
    maxLikeCount: null,
    showSecondLevel: true,
    userLevel: null,
    isVip: '',
    dateRange: []
  })
  currentPage.value = 1
  fetchComments()
}

// 应用筛选
const applyFilters = () => {
  currentPage.value = 1
  fetchComments()
}

// 初始化数据
onMounted(async () => {
  await refreshRecords()
})

// 删除爬取记录
const handleDeleteRecordDisplay = async (recordId, event) => {
  event.stopPropagation() // 阻止事件冒泡，防止触发 handleSelectRecord
  try {
    await ElMessageBox.confirm(
      '确定要删除这条爬取记录吗？删除后无法恢复！',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteCrawlRecord(recordId)
    ElMessage.success('删除成功')
    
    // 如果删除的是当前选中的记录，清除选中状态
    if (selectedRecordId.value === recordId) {
      selectedRecordId.value = null
      comments.value = []
      totalComments.value = 0
      totalPages.value = 0
    }
    
    // 刷新记录列表
    await refreshRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除记录失败:', error)
    }
  }
}

// 下载当前查询结果的评论
const handleDownloadComments = async () => {
  if (!selectedRecordId.value) {
    ElMessage.warning('请先选择一个爬取记录')
    return
  }
  
  try {
    // 构建筛选参数
    const filterParams = {
      username: filters.username,
      keyword: filters.keyword,
      gender: filters.gender,
      minReplyCount: filters.minReplyCount,
      maxReplyCount: filters.maxReplyCount,
      minLikeCount: filters.minLikeCount,
      maxLikeCount: filters.maxLikeCount,
      showSecondLevel: filters.showSecondLevel,
      userLevel: filters.userLevel,
      isVip: filters.isVip
    }
    
    // 处理时间范围
    if (filters.dateRange && filters.dateRange.length === 2) {
      filterParams.startTime = filters.dateRange[0]
      filterParams.endTime = filters.dateRange[1]
    }
    
    const response = await downloadComments(selectedRecordId.value, filterParams)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名，如果没有则使用默认名称
    const contentDisposition = response.headers['content-disposition']
    let filename = `comments_${selectedRecordId.value}_${new Date().toISOString().slice(0, 10)}.csv`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败：' + error.message)
  }
}
</script>

<template>
  <div class="data-display-container">
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><ChatDotRound /></el-icon>
            数据展示
          </h1>
          <p class="page-subtitle">查看和管理爬取的评论数据</p>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            :icon="Refresh" 
            @click="refreshRecords"
            :loading="loading"
          >
            刷新记录
          </el-button>
        </div>
      </div>
    </div>
    
    <el-row :gutter="20">
      <!-- 爬取记录列表 -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="records-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2 class="section-title">
                <el-icon><User /></el-icon>
                爬取记录
              </h2>
              <div class="section-info">
                <el-tag type="info" size="small">共 {{ crawlRecords.length }} 条记录</el-tag>
              </div>
            </div>
          </template>
          
          <div class="records-list" v-loading="loading">
            <el-empty v-if="crawlRecords.length === 0" description="暂无爬取记录">
              <el-button type="primary" @click="refreshRecords">刷新记录</el-button>
            </el-empty>
            
            <el-scrollbar height="500px" v-else>
              <div class="records-grid">
                <div 
                  v-for="record in crawlRecords" 
                  :key="record.id"
                  class="record-card"
                  :class="{ 'selected': selectedRecordId === record.id }"
                  @click="handleRecordSelect(record.id)"
                >
                  <div class="record-header">
                    <div class="record-badges">
                      <el-tag size="small" type="primary">ID: {{ record.id }}</el-tag>
                      <el-tag size="small" type="success">{{ record.bv }}</el-tag>
                    </div>
                    <div class="record-actions" v-if="isAdmin">
                      <el-button 
                        type="danger" 
                        :icon="Delete" 
                        size="small"
                        circle
                        @click="handleDeleteRecordDisplay(record.id, $event)"
                      />
                    </div>
                  </div>
                  
                  <div class="record-content">
                    <h4 class="record-title">{{ record.title }}</h4>
                    
                    <div class="record-stats">
                      <div class="stat-item">
                        <el-icon><ChatDotRound /></el-icon>
                        <span>{{ record.comment_count }} 条评论</span>
                      </div>
                      <div class="stat-item">
                        <el-icon><Star /></el-icon>
                        <span>{{ record.mode === 3 ? '热门评论' : '最新评论' }}</span>
                      </div>
                      <div class="stat-item">
                        <el-icon :class="record.is_second ? 'text-success' : 'text-warning'">
                          <ChatDotRound />
                        </el-icon>
                        <span>{{ record.is_second ? '含二级评论' : '仅一级评论' }}</span>
                      </div>
                    </div>
                    
                    <div class="record-footer">
                      <div class="record-time">
                        <el-icon><Calendar /></el-icon>
                        {{ formatDateTime(record.start_time) }}
                      </div>
                      <div v-if="isAdmin" class="record-user">
                        <el-icon><User /></el-icon>
                        用户: {{ record.username || 'N/A' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </div>
        </el-card>
      </el-col>
      
      <!-- 评论列表 -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="comments-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="comments-header-left">
                <h2 class="section-title">
                  <el-icon><ChatDotRound /></el-icon>
                  评论列表
                  <el-tag v-if="selectedRecord" type="success" size="small" class="ml-2">
                    {{ selectedRecord.title }}
                  </el-tag>
                </h2>
              </div>
              
              <div class="comments-header-right">
                <el-button 
                  type="info" 
                  :icon="Filter" 
                  @click="toggleFilters"
                  size="small"
                >
                  {{ showFilters ? '隐藏筛选' : '显示筛选' }}
                </el-button>
                <el-button 
                  type="primary" 
                  :icon="Refresh" 
                  @click="refreshComments"
                  size="small"
                  :disabled="!selectedRecordId"
                >
                  刷新
                </el-button>
                <el-button 
                  type="success" 
                  :icon="Download" 
                  @click="handleDownloadComments"
                  size="small"
                  :disabled="!selectedRecordId"
                >
                  下载
                </el-button>
                <el-select 
                  v-model="pageSize" 
                  placeholder="每页显示"
                  size="small"
                  :disabled="!selectedRecordId"
                  class="page-size-select ml-10"
                >
                  <el-option 
                    v-for="size in pageSizeOptions" 
                    :key="size" 
                    :label="`${size}条/页`" 
                    :value="size" 
                  />
                </el-select>
              </div>
            </div>
          </template>
          
          <!-- 筛选面板 -->
          <el-collapse-transition>
            <div v-show="showFilters" class="filters-panel">
              <el-card class="filter-card">
                <template #header>
                  <div class="filter-header">
                    <span>筛选条件</span>
                    <el-button type="text" size="small" @click="resetFilters">
                      重置
                    </el-button>
                  </div>
                </template>
                
                <el-row :gutter="16">
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="用户名">
                      <el-input 
                        v-model="filters.username" 
                        placeholder="搜索用户名"
                        clearable
                        @change="applyFilters"
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="关键词">
                      <el-input 
                        v-model="filters.keyword" 
                        placeholder="搜索评论内容"
                        clearable
                        @change="applyFilters"
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="性别">
                      <el-select 
                        v-model="filters.gender" 
                        placeholder="选择性别"
                        clearable
                        @change="applyFilters"
                      >
                        <el-option 
                          v-for="option in genderOptions" 
                          :key="option.value" 
                          :label="option.label" 
                          :value="option.value"
                        >
                          <el-icon v-if="option.value === '男'" class="mr-1"><Male /></el-icon>
                          <el-icon v-else-if="option.value === '女'" class="mr-1"><Female /></el-icon>
                          {{ option.label }}
                        </el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="用户等级">
                      <el-select 
                        v-model="filters.userLevel" 
                        placeholder="选择等级"
                        clearable
                        @change="applyFilters"
                      >
                        <el-option 
                          v-for="option in levelOptions" 
                          :key="option.value" 
                          :label="option.label" 
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="16">
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="会员状态">
                      <el-select 
                        v-model="filters.isVip" 
                        placeholder="选择会员状态"
                        clearable
                        @change="applyFilters"
                      >
                        <el-option 
                          v-for="option in vipOptions" 
                          :key="option.value" 
                          :label="option.label" 
                          :value="option.value"
                        >
                          <el-icon v-if="option.value === '是'" class="mr-1"><Star /></el-icon>
                          {{ option.label }}
                        </el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="回复数范围">
                      <div class="range-inputs">
                        <el-input-number 
                          v-model="filters.minReplyCount" 
                          placeholder="最小值"
                          :min="0"
                          size="small"
                          @change="applyFilters"
                        />
                        <span class="range-separator">-</span>
                        <el-input-number 
                          v-model="filters.maxReplyCount" 
                          placeholder="最大值"
                          :min="0"
                          size="small"
                          @change="applyFilters"
                        />
                      </div>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="点赞数范围">
                      <div class="range-inputs">
                        <el-input-number 
                          v-model="filters.minLikeCount" 
                          placeholder="最小值"
                          :min="0"
                          size="small"
                          @change="applyFilters"
                        />
                        <span class="range-separator">-</span>
                        <el-input-number 
                          v-model="filters.maxLikeCount" 
                          placeholder="最大值"
                          :min="0"
                          size="small"
                          @change="applyFilters"
                        />
                      </div>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="评论时间">
                      <el-date-picker
                        v-model="filters.dateRange"
                        type="datetimerange"
                        range-separator="至"
                        start-placeholder="开始时间"
                        end-placeholder="结束时间"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                        @change="applyFilters"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row>
                  <el-col :xs="24" :sm="12">
                    <el-form-item label="显示二级评论">
                      <el-switch 
                        v-model="filters.showSecondLevel"
                        active-text="显示"
                        inactive-text="隐藏"
                        @change="applyFilters"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-card>
            </div>
          </el-collapse-transition>
          
          <div v-if="!selectedRecordId" class="no-record-selected">
            <el-empty description="请先选择一条爬取记录">
              <el-button type="primary" @click="refreshRecords">查看记录</el-button>
            </el-empty>
          </div>
          
          <div v-else>
            <div class="comments-list" v-loading="commentsLoading">
              <div class="comments-info">
                <el-tag type="info" size="small">
                  共 {{ totalComments }} 条评论
                </el-tag>
                <el-tag v-if="filters.username || filters.keyword || filters.gender || filters.userLevel !== null || filters.isVip" 
                       type="warning" size="small" class="ml-2">
                  已应用筛选条件
                </el-tag>
              </div>
              
              <el-empty v-if="comments.length === 0" description="暂无评论数据">
                <el-button type="primary" @click="resetFilters">重置筛选</el-button>
              </el-empty>
              
              <div v-else class="comment-items">
                <div 
                  v-for="comment in comments" 
                  :key="comment.id"
                  class="comment-card"
                  :class="{ 'is-reply': comment.parent_id != 0 && comment.parent_id !== '0' }"
                >
                  <div class="comment-header">
                    <div class="user-info">
                      <el-avatar 
                        :src="comment.user_avatar" 
                        :size="40"
                        class="user-avatar"
                      >
                        <el-icon><User /></el-icon>
                      </el-avatar>
                      <div class="user-details">
                        <div class="user-name-row">
                          <span class="username">{{ comment.username }}</span>
                          <el-tag v-if="comment.is_vip === '是'" type="warning" size="small" class="vip-tag">
                            <el-icon><Star /></el-icon>
                            VIP
                          </el-tag>
                          <el-tag type="info" size="small" class="level-tag">
                            Lv{{ comment.user_level }}
                          </el-tag>
                          <el-tag v-if="comment.gender" 
                                 :type="comment.gender === '男' ? 'primary' : comment.gender === '女' ? 'danger' : 'info'" 
                                 size="small" class="gender-tag">
                            <el-icon v-if="comment.gender === '男'"><Male /></el-icon>
                            <el-icon v-else-if="comment.gender === '女'"><Female /></el-icon>
                            {{ comment.gender }}
                          </el-tag>
                        </div>
                        <div class="user-meta">
                          <span v-if="comment.ip_location" class="ip-location">
                            <el-icon><Calendar /></el-icon>
                            {{ comment.ip_location }}
                          </span>
                          <span class="comment-time">
                            {{ formatDateTime(comment.comment_time) }}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="comment-actions">
                      <el-tag v-if="comment.parent_id != 0 && comment.parent_id !== '0'" type="success" size="small">
                        二级评论
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="comment-content">
                    <p>{{ comment.content }}</p>
                  </div>
                  
                  <div class="comment-footer">
                    <div class="comment-stats">
                      <div class="stat-item">
                        <el-icon class="like-icon"><Star /></el-icon>
                        <span>{{ comment.like_count }}</span>
                      </div>
                      <div class="stat-item">
                        <el-icon class="reply-icon"><ChatDotRound /></el-icon>
                        <span>{{ comment.reply_count }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 分页 -->
              <div class="pagination-container">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="pageSizeOptions"
                  layout="total, sizes, prev, pager, next, jumper"
                  :total="totalComments"
                  :disabled="commentsLoading"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
/* 整体容器 */
.data-display-container {
  padding: 24px;
  background: rgba(248, 250, 252,0);
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  margin-bottom: 24px;
}

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

.title-section {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  margin-right: 16px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 1.875rem;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 0;
  gap: 12px;
}

.title-icon {
  font-size: 1.75rem;
  color: #3b82f6;
}

.page-subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  align-items: center;
}

.subtitle {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* 区域样式 */
.crawl-records-section,
.comments-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-info {
  display: flex;
  gap: 8px;
}

.section-actions {
  display: flex;
  gap: 12px;
}

/* 记录网格 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  padding: 0;
}

/* 记录卡片 */
.record-card {
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.record-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.record-card.selected {
  border-color: #3b82f6;
  background: #f8fafc;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.record-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.record-actions {
  display: flex;
  gap: 8px;
}

.record-content {
  flex: 1;
}

.record-title {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.4;
  display: -webkit-box;
 /* -webkit-line-clamp: 2;*/
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.record-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #666;
}

.stat-item .el-icon {
  font-size: 1rem;
}

.text-success {
  color: #67c23a !important;
}

.text-warning {
  color: #e6a23c !important;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e1e8ed;
  font-size: 0.85rem;
  color: #999;
}

.record-time,
.record-user {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.records-card, .comments-card {
  height: 100%;
  border-radius: 8px;
  transition: all 0.2s ease;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.records-card:hover, .comments-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.record-item {
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 10px;
  border: 1px solid var(--el-border-color-lighter);
}

.record-item:hover {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-5);
  transform: translateY(-2px);
}

.record-item-active {
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.record-item-content {
  width: calc(100% - 40px); /* 为删除按钮留出空间 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-username-display {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 5px;
}

.record-delete-btn {
  margin-left: auto; /* 将按钮推到最右边 */
}

.record-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.record-id {
  font-weight: bold;
  margin-right: 10px;
  color: var(--el-color-primary-dark-2);
}

.record-bv {
  color: var(--el-color-primary);
  font-weight: 500;
}

.record-info {
  font-size: 14px;
}

.record-title-text {
  font-weight: bold;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--el-text-color-primary);
}

.record-meta {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 5px;
}

.record-count {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
}

.record-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.comments-header-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.selected-record-info {
  margin-left: 10px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.comments-header-right {
  display: flex;
  align-items: center;
}

.search-input {
  width: 180px;
}

.page-size-select {
  width: 100px;
}

.comment-item {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 15px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
}

.comment-item:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  border-color: var(--el-border-color);
}

.comment-reply {
  margin-left: 40px;
  background-color: var(--el-color-primary-light-9);
  border-left: 3px solid var(--el-color-primary-light-5);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.comment-user {
  display: flex;
  align-items: center;
}

.user-info {
  margin-left: 12px;
}

.user-name {
  font-weight: 600;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  color: var(--el-text-color-primary);
}

.user-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.comment-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.comment-content {
  margin-bottom: 12px;
  line-height: 1.6;
  word-break: break-word;
  color: var(--el-text-color-primary);
  padding: 5px 0;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px dashed var(--el-border-color-lighter);
}

.comment-stats {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.comment-likes, .comment-replies {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.no-record-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: var(--el-text-color-secondary);
}

:deep(.el-empty__description p) {
  color: var(--el-text-color-secondary);
}

:deep(.el-pagination) {
  justify-content: center;
}

:deep(.el-avatar) {
  border: 2px solid var(--el-color-primary-light-8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-tag) {
  border-radius: 4px;
}

/* 响应式调整 */
/* 中等屏幕适配 */
@media (max-width: 1024px) and (min-width: 769px) {
  .header-content {
    padding: 20px 24px;
  }
  
  .page-title {
    font-size: 1.625rem;
  }
  
  .header-actions {
    gap: 10px;
  }
}

/* 小屏幕适配 */
@media (max-width: 768px) {
  .data-display-container {
    padding: 15px 10px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .comment-reply {
    margin-left: 20px;
  }
  
  .comments-header-left, .comments-header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .comments-header-right {
    align-self: flex-end;
  }
  
  .selected-record-info {
    margin-left: 0;
    margin-top: 5px;
    max-width: 100%;
  }
}

/* 筛选面板 */
.filters-panel {
  margin-bottom: 20px;
}

.filter-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #374151;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #6b7280;
  font-weight: 500;
}

/* 移动端筛选面板适配 */
@media (max-width: 768px) {
  .filters-panel .el-form-item {
    margin-bottom: 16px;
  }
  
  .filters-panel :deep(.el-date-editor.el-input__wrapper),
  .filters-panel :deep(.el-date-editor.el-input),
  .filters-panel :deep(.el-select),
  .filters-panel :deep(.el-input) {
    width: 100%;
  }
  
  .filters-panel :deep(.el-date-editor--datetimerange) {
    width: 100%;
  }
  
  .range-inputs {
    flex-wrap: wrap;
  }
  
  .range-inputs :deep(.el-input-number) {
    width: calc(50% - 10px);
    min-width: 80px;
  }
}

/* 评论信息 */
.comments-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* 评论列表 */
.comments-list {
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.comment-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 评论卡片 */
.comment-card {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.comment-card:last-child {
  border-bottom: none;
}

.comment-card:hover {
  background: #f8fafc;
}

.comment-card.is-reply {
  margin-left: 40px;
  background: #f1f5f9;
  border-left: 3px solid #3b82f6;
  border-radius: 0 6px 6px 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.user-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.username {
  font-weight: 600;
  color: #1e293b;
  font-size: 1rem;
}

.vip-tag {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
  border: none;
  color: white;
}

.level-tag {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
  color: white;
}

.gender-tag {
  border: none;
  color: white;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.8rem;
  color: #64748b;
}

.ip-location,
.comment-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.comment-content {
  margin-bottom: 16px;
  line-height: 1.6;
}

.comment-content p {
  margin: 0;
  color: #374151;
  font-size: 0.9rem;
  word-wrap: break-word;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.comment-stats {
  display: flex;
  gap: 20px;
}

.comment-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 0.85rem;
}

.like-icon {
  color: #ef4444;
}

.reply-icon {
  color: #3b82f6;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

/* 空状态样式 */
.no-record-selected,
.no-comments {
  text-align: center;
  padding: 48px 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  color: #6b7280;
}

.no-record-selected h3,
.no-comments h3 {
  margin: 0 0 12px 0;
  font-size: 1.125rem;
  color: #374151;
}

.no-record-selected p,
.no-comments p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-display-container {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 16px 20px;
    overflow: hidden;
  }
  
  .title-section {
    width: 100%;
    min-width: 0;
    margin-right: 0;
  }
  
  .page-title {
    font-size: 1.5rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 8px;
  }
  
  .records-grid {
    grid-template-columns: 1fr;
  }
  
  .record-card {
    padding: 16px;
  }
  
  .comment-card {
    padding: 16px;
  }
  
  .comment-card.is-reply {
    margin-left: 20px;
  }
  
  .user-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .user-name-row {
    flex-wrap: wrap;
  }
  
  .comment-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

/* 工具类 */
.ml-5 {
  margin-left: 5px;
}

.text-muted {
  color: #909399;
}

.text-primary {
  color: #409eff;
}

.text-success {
  color: #67c23a;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}

.ml-10 {
  margin-left: 10px;
}
</style>