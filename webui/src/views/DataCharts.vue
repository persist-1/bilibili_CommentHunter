<template>
  <div class="data-charts-container">
    <div class="page-header">
        <div class="header-content">
            <div class="title-section">
                <h1 class="page-title">
                    数据图表
                </h1>
            <p class="page-subtitle">可视化展示评论数据分析结果</p>
        </div>
      </div>
    </div>

    <!-- 爬取记录选择 -->
    <el-card class="record-selector-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>选择爬取记录</h2>
          <el-button 
            type="primary" 
            size="small" 
            @click="fetchCrawlRecords"
            :loading="loading.records"
            round
          >
            <el-icon class="el-icon--left"><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
      
      <el-select 
        v-model="selectedRecordId" 
        placeholder="请选择要分析的爬取记录"
        style="width: 100%; max-width: 600px;"
        @change="onRecordChange"
        filterable
      >
        <el-option
          v-for="record in crawlRecords"
          :key="record.id"
          :label="`#${record.id} - ${record.title} (${record.comment_count}条评论)`"
          :value="record.id"
        />
      </el-select>
    </el-card>

    <!-- 图表展示区域 -->
    <div v-if="selectedRecordId && chartData.loaded" class="charts-grid">
      <!-- 性别分布饼状图 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>评论者性别分布</h3>
          <p class="chart-description">直观查看视频受众群体性别构成</p>
        </template>
        <v-chart 
          class="chart" 
          :option="genderChartOption" 
          autoresize
        />
      </el-card>

      <!-- 评论时间分布折线图 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>评论时间分布</h3>
          <p class="chart-description">24小时内评论活跃时间段分析</p>
        </template>
        <v-chart 
          class="chart" 
          :option="timeChartOption" 
          autoresize
        />
      </el-card>

      <!-- 高回复评论词云 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>高回复评论词云</h3>
          <p class="chart-description">争议性或受关注话题分析</p>
        </template>
        <v-chart 
          class="chart" 
          :option="replyWordCloudOption" 
          autoresize
        />
      </el-card>

      <!-- 高点赞评论词云 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>高点赞评论词云</h3>
          <p class="chart-description">受赞同观点和有用信息分析</p>
        </template>
        <v-chart 
          class="chart" 
          :option="likeWordCloudOption" 
          autoresize
        />
      </el-card>

      <!-- VIP用户分布饼状图 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>VIP用户分布</h3>
          <p class="chart-description">会员与非会员用户占比分析</p>
        </template>
        <v-chart 
          class="chart" 
          :option="vipChartOption" 
          autoresize
        />
      </el-card>

      <!-- 用户等级分布柱状图 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <h3>用户等级分布</h3>
          <p class="chart-description">视频受众用户等级构成分析</p>
        </template>
        <v-chart 
          class="chart" 
          :option="levelChartOption" 
          autoresize
        />
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading.charts" class="loading-container">
      <el-loading-spinner size="large" />
      <p>正在分析数据...</p>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!selectedRecordId" 
      description="请选择一个爬取记录开始数据分析"
      :image-size="200"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import {
  CanvasRenderer
} from 'echarts/renderers'
import {
  PieChart,
  LineChart,
  BarChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import 'echarts-wordcloud'
import { getCrawlRecords, getComments } from '../api'

// 注册ECharts组件
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const selectedRecordId = ref(null)
const crawlRecords = ref([])
const loading = reactive({
  records: false,
  charts: false
})

const chartData = reactive({
  loaded: false,
  comments: [],
  genderData: [],
  timeData: [],
  replyWords: [],
  likeWords: [],
  vipData: [],
  levelData: []
})

// 获取爬取记录列表
const fetchCrawlRecords = async () => {
  loading.records = true
  try {
    const response = await getCrawlRecords()
    crawlRecords.value = response.records || []
  } catch (error) {
    ElMessage.error('获取爬取记录失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.records = false
  }
}

// 获取评论数据并分析
const fetchCommentsAndAnalyze = async (crawlId) => {
  loading.charts = true
  chartData.loaded = false
  
  try {
    // 获取所有评论数据（分页获取）
    let allComments = []
    let page = 1
    const pageSize = 100
    
    while (true) {
      const response = await getComments(crawlId, page, pageSize)
      if (!response.comments || response.comments.length === 0) {
        break
      }
      allComments = allComments.concat(response.comments)
      
      // 如果当前页评论数少于pageSize，说明已经是最后一页
      if (response.comments.length < pageSize) {
        break
      }
      page++
    }
    
    chartData.comments = allComments
    analyzeData()
    chartData.loaded = true
    
  } catch (error) {
    ElMessage.error('获取评论数据失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.charts = false
  }
}

// 数据分析函数
const analyzeData = () => {
  const comments = chartData.comments
  
  // 1. 性别分布分析
  const genderCount = { '男': 0, '女': 0, '保密': 0 }
  comments.forEach(comment => {
    if (genderCount.hasOwnProperty(comment.gender)) {
      genderCount[comment.gender]++
    }
  })
  chartData.genderData = Object.entries(genderCount).map(([name, value]) => ({ name, value }))
  
  // 2. 评论时间分布分析（按小时统计）
  const hourCount = new Array(24).fill(0)
  comments.forEach(comment => {
    const hour = new Date(comment.comment_time).getHours()
    hourCount[hour]++
  })
  chartData.timeData = hourCount.map((count, hour) => ({ hour, count }))
  
  // 3. 高回复评论词云分析
  const highReplyComments = comments
    .filter(comment => comment.reply_count > 5)
    .sort((a, b) => b.reply_count - a.reply_count)
    .slice(0, 20)
  chartData.replyWords = extractKeywords(highReplyComments)
  
  // 4. 高点赞评论词云分析
  const highLikeComments = comments
    .filter(comment => comment.like_count > 10)
    .sort((a, b) => b.like_count - a.like_count)
    .slice(0, 20)
  chartData.likeWords = extractKeywords(highLikeComments)
  
  // 5. VIP用户分布分析
  const vipCount = { '是': 0, '否': 0 }
  comments.forEach(comment => {
    if (vipCount.hasOwnProperty(comment.is_vip)) {
      vipCount[comment.is_vip]++
    }
  })
  chartData.vipData = Object.entries(vipCount).map(([name, value]) => ({ name, value }))
  
  // 6. 用户等级分布分析
  const levelCount = {}
  for (let i = 0; i <= 6; i++) {
    levelCount[i] = 0
  }
  comments.forEach(comment => {
    const level = comment.user_level
    if (levelCount.hasOwnProperty(level)) {
      levelCount[level]++
    }
  })
  chartData.levelData = Object.entries(levelCount).map(([level, count]) => ({ level: `Lv${level}`, count }))
}

// 提取关键词函数（简单实现）
const extractKeywords = (comments) => {
  const wordCount = {}
  const stopWords = new Set(['的', '了', '是', '在', '我', '你', '他', '她', '它', '这', '那', '有', '和', '与', '或', '但', '而', '就', '都', '也', '还', '只', '又', '很', '更', '最', '非常', '特别', '真的', '确实', '应该', '可以', '能够', '不是', '没有', '不会', '不能', '不要', '不用', '一个', '一些', '一样', '什么', '怎么', '为什么', '哪里', '哪个', '多少', '几个'])
  
  comments.forEach(comment => {
    // 简单的中文分词（按标点符号和空格分割）
    const words = comment.content
      .replace(/[，。！？；：、""（）【】《》]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length >= 2 && !stopWords.has(word))
    
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1
    })
  })
  
  // 转换为词云格式并按频率排序
  return Object.entries(wordCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 50)
    .map(([name, value]) => ({ name, value }))
}

// 图表配置
const genderChartOption = computed(() => ({
  title: {
    text: '性别分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [{
    name: '性别分布',
    type: 'pie',
    radius: '50%',
    data: chartData.genderData,
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
}))

const timeChartOption = computed(() => ({
  title: {
    text: '24小时评论时间分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: chartData.timeData.map(item => `${item.hour}:00`)
  },
  yAxis: {
    type: 'value',
    name: '评论数量'
  },
  series: [{
    name: '评论数量',
    type: 'line',
    data: chartData.timeData.map(item => item.count),
    smooth: true,
    areaStyle: {}
  }]
}))

const replyWordCloudOption = computed(() => ({
  title: {
    text: '高回复评论词云',
    left: 'center'
  },
  tooltip: {
    show: true
  },
  series: [{
    type: 'wordCloud',
    gridSize: 2,
    sizeRange: [12, 50],
    rotationRange: [-90, 90],
    shape: 'pentagon',
    width: '100%',
    height: '100%',
    drawOutOfBound: true,
    textStyle: {
      fontFamily: 'sans-serif',
      fontWeight: 'bold',
      color: function () {
        return 'rgb(' + [
          Math.round(Math.random() * 160),
          Math.round(Math.random() * 160),
          Math.round(Math.random() * 160)
        ].join(',') + ')'
      }
    },
    emphasis: {
      textStyle: {
        shadowBlur: 10,
        shadowColor: '#333'
      }
    },
    data: chartData.replyWords
  }]
}))

const likeWordCloudOption = computed(() => ({
  title: {
    text: '高点赞评论词云',
    left: 'center'
  },
  tooltip: {
    show: true
  },
  series: [{
    type: 'wordCloud',
    gridSize: 2,
    sizeRange: [12, 50],
    rotationRange: [-90, 90],
    shape: 'pentagon',
    width: '100%',
    height: '100%',
    drawOutOfBound: true,
    textStyle: {
      fontFamily: 'sans-serif',
      fontWeight: 'bold',
      color: function () {
        return 'rgb(' + [
          Math.round(Math.random() * 160),
          Math.round(Math.random() * 160),
          Math.round(Math.random() * 160)
        ].join(',') + ')'
      }
    },
    emphasis: {
      textStyle: {
        shadowBlur: 10,
        shadowColor: '#333'
      }
    },
    data: chartData.likeWords
  }]
}))

const vipChartOption = computed(() => ({
  title: {
    text: 'VIP用户分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [{
    name: 'VIP分布',
    type: 'pie',
    radius: '50%',
    data: chartData.vipData,
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
}))

const levelChartOption = computed(() => ({
  title: {
    text: '用户等级分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: chartData.levelData.map(item => item.level)
  },
  yAxis: {
    type: 'value',
    name: '用户数量'
  },
  series: [{
    name: '用户数量',
    type: 'bar',
    data: chartData.levelData.map(item => item.count),
    itemStyle: {
      color: '#409EFF'
    }
  }]
}))

// 事件处理
const onRecordChange = (recordId) => {
  if (recordId) {
    fetchCommentsAndAnalyze(recordId)
  }
}

// 生命周期
onMounted(() => {
  fetchCrawlRecords()
})
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

.data-charts-container {
  width: 100%;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
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

.record-selector-card {
  margin-bottom: 30px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.record-selector-card:hover {
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

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.chart-card {
  min-height: 400px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  background: white;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  margin: 0 0 5px 0;
  color: #1e293b;
  font-size: 1.125rem;
  font-weight: 600;
}

.chart-description {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 400;
}

.chart {
  height: 300px;
  width: 100%;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748b;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.loading-container p {
  margin-top: 20px;
  font-size: 1rem;
  color: #64748b;
}

/* 响应式设计 */
@media (max-width: 1024px) and (min-width: 769px) {
  .data-charts-container {
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
  .data-charts-container {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 0.8rem;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .chart {
    height: 250px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .chart-card {
    min-height: 350px;
  }
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

:deep(.el-select) {
  border-radius: 8px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  transition: all 0.2s ease;
}

:deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #3b82f6 inset;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

:deep(.el-empty) {
  padding: 48px 20px;
}

:deep(.el-empty__description) {
  color: #64748b;
}
</style>