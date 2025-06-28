import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/crawl'
  },
  {
    path: '/crawl',
    name: 'DataCrawl',
    component: () => import('../views/DataCrawl.vue'),
    meta: {
      title: '数据爬取',
      requiresAuth: true
    }
  },
  {
    path: '/display',
    name: 'DataDisplay',
    component: () => import('../views/DataDisplay.vue'),
    meta: {
      title: '数据展示',
      requiresAuth: true
    }
  },
  {
    path: '/charts',
    name: 'DataCharts',
    component: () => import('../views/DataCharts.vue'),
    meta: {
      title: '数据图表',
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue'),
    meta: {
      title: '我的信息',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login.vue'),
    meta: {
      title: '登录'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/register.vue'),
    meta: {
      title: '注册'
    }
  },
  {
    path: '/project-intro',
    name: 'ProjectIntro',
    component: () => import('../views/project_intro.vue'),
    meta: {
      title: '项目介绍'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置页面标题和路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Bilibili评论爬虫`
  }
  
  // 检查是否需要登录权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // 已登录，正常访问
      next()
    }
  } else {
    // 不需要登录权限的页面
    next()
  }
})

export default router