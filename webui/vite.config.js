import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    allowedHosts: ['bilibili-ch.persist1.cn'], // 允许 bilibili-ch.persist1.cn 访问
  },
})