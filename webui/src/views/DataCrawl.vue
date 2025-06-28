<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCrawlerStore } from '../stores/crawler'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete, Download } from '@element-plus/icons-vue'

const crawlerStore = useCrawlerStore()

// 获取用户等级，用于判断是否为管理员
const userLevel = ref(parseInt(localStorage.getItem('level') || '0'))
const isAdmin = computed(() => userLevel.value === 2) // 假设level 2 为管理员

// 表单数据
const formData = ref({
  bv: '',
  next_pageID: '',
  is_second: true,
  mode: 3, // 默认热门评论
  limit_num: 300
})

// 表单验证规则
const rules = {
  bv: [
    { required: true, message: '请输入BV号', trigger: 'blur' },
    { pattern: /^BV[a-zA-Z0-9]+$/, message: 'BV号格式不正确', trigger: 'blur' }
  ],
  limit_num: [
    { required: true, message: '请输入爬取数量上限', trigger: 'blur' },
    { type: 'number', min: 1, max: 1000, message: '爬取数量上限必须在1-1000之间', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref(null)

// 爬取状态
const crawling = ref(false)

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        crawling.value = true
        
        // 确认爬取
        await ElMessageBox.confirm(
          `确定要爬取视频 ${formData.value.bv} 的评论吗？`,
          '确认爬取',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 开始爬取
        const response = await crawlerStore.crawlComments({
          bv: formData.value.bv,
          next_pageID: formData.value.next_pageID,
          is_second: formData.value.is_second,
          mode: formData.value.mode,
          limit_num: formData.value.limit_num
        })
        
        ElMessage.success(`爬取任务已开始，爬取ID: ${response.crawl_id}`)
        
        // 重置表单
        formRef.value.resetFields()
        
        // 刷新爬取记录列表
        await crawlerStore.fetchCrawlRecords()
      } catch (error) {
        if (error === 'cancel') return
        
        console.error('爬取失败:', error)
        ElMessage.error(crawlerStore.error || '爬取失败，请重试')
      } finally {
        crawling.value = false
      }
    } else {
      ElMessage.warning('请正确填写表单')
      return false
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
}

// 获取爬取记录列表
onMounted(async () => {
  await crawlerStore.fetchCrawlRecords()
  // 更新用户等级信息，以防在页面加载后发生变化
  userLevel.value = parseInt(localStorage.getItem('level') || '0')
})

// 删除爬取记录
const handleDeleteRecord = async (recordId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条爬取记录及其相关数据吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    await crawlerStore.deleteCrawlRecord(recordId) // 假设 store 中有 deleteCrawlRecord 方法
    ElMessage.success('爬取记录删除成功')
    await crawlerStore.fetchCrawlRecords() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败，请重试')
      console.error('删除爬取记录失败:', error)
    }
  }
}

// 下载爬取记录
const handleDownloadRecord = async (recordId) => {
  try {
    await ElMessageBox.confirm(
      '确定要下载这条爬取记录的数据吗？',
      '确认下载',
      {
        confirmButtonText: '确定下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    // 假设 store 中有 downloadCrawlRecord 方法，该方法会处理下载逻辑
    // 例如，调用API获取CSV文件，然后触发浏览器下载
    await crawlerStore.downloadCrawlRecord(recordId)
    ElMessage.success('下载任务已开始，请稍候') 
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('下载失败，请重试')
      console.error('下载爬取记录失败:', error)
    }
  }
}
</script>

<template>
  <div class="data-crawl-container">
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            数据爬取
          </h1>
          <p class="page-subtitle">爬取B站视频评论数据</p>
        </div>
      </div>
    </div>
    
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>爬取设置</h2>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="BV号" prop="bv">
          <el-input 
            v-model="formData.bv" 
            placeholder="请输入视频BV号，例如：BV1ex7VzREZ8"
          />
        </el-form-item>
        
        <el-form-item label="评论起始页" prop="next_pageID">
          <el-input 
            v-model="formData.next_pageID" 
            placeholder="留空则从第一页开始爬取"
          />
        </el-form-item>
        
        <el-form-item label="评论爬取模式" prop="mode">
          <el-radio-group v-model="formData.mode">
            <el-radio :label="3">热门评论</el-radio>
            <el-radio :label="2">最新评论</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="二级评论爬取" prop="is_second">
          <el-checkbox v-model="formData.is_second">开启二级评论爬取</el-checkbox>
        </el-form-item>
        
        <el-form-item label="爬取数量上限" prop="limit_num">
          <el-input-number 
            v-model="formData.limit_num" 
            :min="1" 
            :max="1000" 
            :step="50"
          />
          <span class="form-tip">（最大1000条）</span>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitForm" 
            :loading="crawling || crawlerStore.loading.crawling"
          >
            开始爬取
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="records-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>爬取记录</h2>
          <el-button 
            type="primary" 
            size="small" 
            @click="crawlerStore.fetchCrawlRecords()"
            :loading="crawlerStore.loading.records"
            round
          >
            <el-icon class="el-icon--left"><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="crawlerStore.crawlRecords" 
        style="width: 100%"
        v-loading="crawlerStore.loading.records"
        border
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="bv" label="BV号" width="120" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column v-if="isAdmin" prop="username" label="用户名" width="120" /> <!-- 管理员可见 -->
        <el-table-column label="爬取模式" width="100">
          <template #default="{ row }">
            {{ row.mode === 3 ? '热门评论' : '最新评论' }}
          </template>
        </el-table-column>
        <el-table-column label="二级评论" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_second ? 'success' : 'info'">
              {{ row.is_second ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comment_count" label="评论数" width="90" />
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">
            {{ row.start_time ? new Date(row.start_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDeleteRecord(row.id)"
              :icon="Delete"
              circle
              title="删除"
            />
            <el-button 
              type="success" 
              size="small" 
              @click="handleDownloadRecord(row.id)"
              :icon="Download"
              circle
              title="下载"
              style="margin-left: 10px;"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
// 获取状态对应的标签类型
function getStatusType(status) {
  if (status === '完成') return 'success'
  if (status === '进行中' || status === '等待中') return 'warning'
  if (status.includes('失败')) return 'danger'
  return 'info'
}
</script>

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
.data-crawl-container {
  width: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.page-header {
  margin-bottom: 10px;
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  font-weight: 400;
}

.form-card, .records-card {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  margin-bottom: 20px;
  background: white;
}

.form-card:hover, .records-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.card-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.form-tip {
  margin-left: 10px;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 400;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

:deep(.el-card__body) {
  padding: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
}

:deep(.el-input__wrapper),
:deep(.el-input-number__wrapper) {
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  transition: all 0.2s ease;
  border-radius: 8px;
}

:deep(.el-input__wrapper:hover),
:deep(.el-input-number__wrapper:hover) {
  box-shadow: 0 0 0 1px #3b82f6 inset;
}

:deep(.el-input__wrapper:focus-within),
:deep(.el-input-number__wrapper:focus-within) {
  box-shadow: 0 0 0 1px #3b82f6 inset;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

:deep(.el-button:not(.is-disabled):hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

:deep(.el-radio-group .el-radio) {
  margin-right: 20px;
}

:deep(.el-checkbox) {
  font-weight: 400;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

:deep(.el-table__header) {
  background-color: #f8fafc;
}

:deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
}

:deep(.el-table th) {
  background-color: #f1f5f9;
  color: #1e293b;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f1f5f9;
}

:deep(.el-table__body tr:last-child td) {
  border-bottom: none;
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) and (min-width: 769px) {
  .data-crawl-container {
    padding: 20px 16px;
  }
  
  .page-header h1 {
    font-size: 1.625rem;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 20px 24px;
  }

  .data-crawl-container {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 0.8rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  :deep(.el-form-item__label) {
    padding-bottom: 8px;
  }
  
  :deep(.el-table) {
    font-size: 0.875rem;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 8px;
  }
}
</style>