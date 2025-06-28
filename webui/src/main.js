import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)

// 使用Pinia状态管理
app.use(createPinia())

// 使用ElementPlus组件库
app.use(ElementPlus, {
  locale: zhCn,
})

// 使用Vue Router
app.use(router)

app.mount('#app')
