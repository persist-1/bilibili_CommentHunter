// 从 api.js 导入所有 API 函数
import * as apiModule from './api'

// 导出所有 API 函数
export const {
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
} = apiModule

// 默认导出
export default apiModule.default