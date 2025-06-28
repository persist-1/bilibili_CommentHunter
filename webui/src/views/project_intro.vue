<template>
  <div class="project-intro-container">
    <div class="page-header">
      <div class="header-content">
          <div class="title-section">
                <h1 class="page-title">项目介绍</h1>
            <p class="page-subtitle">基于FastAPI和Vue3的Bilibili视频评论爬取和展示系统</p>
          </div>
        </div>
    </div>
    
    <!-- 项目背景 -->
    <el-card class="intro-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2 class="section-title">项目背景</h2>
        </div>
      </template>
      <p class="section-content">
        随着数据的快速增长，越来越多的人开始关注数据的价值和应用。而在这个信息爆炸的时代，如何有效地获取和利用数据成为了一个重要的问题。通过爬取Bilibili视频的评论数据，我们可以获得大量的用户反馈和意见，进而分析和挖掘其中的信息。
      </p>
    </el-card>

    <!-- 项目目标 -->
    <el-card class="intro-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2 class="section-title">项目目标</h2>
        </div>
      </template>
      <p class="section-content">
        本项目旨在提供一个方便的平台，用于爬取Bilibili视频的评论数据，并展示给用户。通过该平台，用户可以轻松地获取到指定视频的评论信息，包括评论内容、点赞数、评论时间等。
      </p>
    </el-card>

    <!-- 团队成员 -->
    <el-card class="intro-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2 class="section-title">项目作者</h2>
        </div>
      </template>
      <div class="team-members">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(member, index) in teamMembers" :key="index">
            <div class="member">
              <div class="avatar">
                <el-avatar :size="100" :src="member.avatar" alt="成员头像" />
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.name }}</div>
                <div class="member-class">{{ member.class }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 博客 -->
    <el-card class="intro-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2 class="section-title">项目博客</h2>
        </div>
      </template>
      <div class="blog-section">
        <el-link 
          type="primary" 
          href="https://blog.persist1.cn/archives/project-bilibili_CH" 
          target="_blank"
          :underline="false"
          class="blog-link"
        >
          <el-icon class="el-icon--left"><el-icon-link /></el-icon>
          访问项目博客
        </el-link>
        <p class="blog-description">
          在项目博客中，我们详细记录了开发过程中的技术选型、架构设计、难点突破以及未来展望。
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Link as ElIconLink } from '@element-plus/icons-vue';

// 团队成员数据
const teamMembers = ref([
  {
    name: '贯一',
    class: '"一个敲代码的小人物"',
    avatar: 'http://q1.qlogo.cn/g?b=qq&nk=1822559429&s=100'
  }
]);
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

.project-intro-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-color-primary-dark-2);
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

.intro-card {
  margin-bottom: 25px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.intro-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: var(--el-color-primary);
}

.section-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
  text-align: justify;
  margin: 0;
}

.team-members {
  padding: 10px 0;
}

.member {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  background-color: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-lighter);

}

.member:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
  border-color: var(--el-color-primary-light-5);
}

.avatar {
  margin-bottom: 15px;
}

.member-info {
  text-align: center;
  width: 100%;
}

.member-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--el-color-primary-dark-2);
}

.member-class {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.blog-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}

.blog-link {
  font-size: 18px;
  margin-bottom: 15px;
  padding: 10px 20px;
  border-radius: 8px;
  background-color: var(--el-color-primary-light-9);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.blog-link:hover {
  background-color: var(--el-color-primary-light-8);
  transform: translateY(-2px);
}

.blog-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header-content {
    padding: 20px 24px;
  }

  .project-intro-container {
    padding: 15px 10px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .section-content {
    font-size: 14px;
  }
  
  .blog-link {
    font-size: 16px;
    padding: 8px 16px;
  }
}
</style>