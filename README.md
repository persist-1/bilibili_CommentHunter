# Bilibili评论爬取与分析系统

这是一个基于FastAPI和Vue3的Bilibili视频评论爬取、展示和分析系统，支持用户管理、数据可视化等功能。

## 📊 数据来源

本项目使用的数据接口来源于哔哩哔哩开放平台提供的API服务。相关技术文档请参考：
- [Bilibili API 第三方文档](https://qinshixixing.gitbooks.io/bilibiliapi/content/)
- [哔哩哔哩官方文档](http://docs.bilibili.cn/wiki)

## 🚀 功能特点

### 核心功能
- **评论爬取**：根据BV号爬取Bilibili视频评论，支持热门评论和最新评论两种模式
- **二级评论**：支持爬取二级评论（回复）
- **数据存储**：将爬取的评论数据存储到SQLite数据库中
- **数据展示**：以列表形式展示爬取的评论数据，支持分页、搜索和筛选
- **爬取记录**：保存每次爬取的记录，方便后续查看和管理

### 数据分析与可视化
- **性别分布图**：展示评论者性别分布的饼状图
- **时间分布图**：显示24小时内评论时间分布的折线图
- **热门词云**：基于高回复和高点赞评论生成的词云图
- **用户分析**：VIP用户分布和用户等级分布图表
- **交互式图表**：基于ECharts的响应式数据可视化

### 用户管理系统
- **用户注册/登录**：支持邮箱注册和JWT身份验证
- **权限管理**：区分普通用户和管理员权限
- **个人信息**：用户资料管理和密码修改
- **安全认证**：基于JWT的安全认证机制

## 🏗️ 系统架构

- **后端**：FastAPI框架，提供RESTful API和用户认证
- **数据库**：SQLite3，轻量级文件数据库
- **前端**：Vue3 + Element Plus + Vite + ECharts，现代化用户界面
- **状态管理**：Pinia状态管理
- **路由管理**：Vue Router 4

## 📁 目录结构

```
bilibili_CH/
├── api.py                # 主要后端API服务
├── user_api.py           # 用户管理API
├── check_jwt.py          # JWT验证工具
├── install_pyjwt.py      # PyJWT安装脚本
├── requirements.txt      # Python依赖包列表
├── bilibili_CH.db        # SQLite数据库文件
├── bili_cookie.txt       # B站Cookie文件（可选）
├── api.bat               # 后端启动脚本
├── start.bat             # 一键启动脚本
├── README.md             # 项目说明文档
└── webui/                # 前端项目
    ├── src/              # 源代码
    │   ├── api/          # API调用模块
    │   ├── assets/       # 静态资源
    │   ├── components/   # 组件
    │   ├── router/       # 路由配置
    │   ├── stores/       # Pinia状态管理
    │   ├── views/        # 页面视图
    │   │   ├── DataCrawl.vue      # 数据爬取页面
    │   │   ├── DataDisplay.vue    # 数据展示页面
    │   │   ├── DataCharts.vue     # 数据图表页面
    │   │   ├── UserProfile.vue    # 用户信息页面
    │   │   ├── login.vue          # 登录页面
    │   │   └── register.vue       # 注册页面
    │   ├── App.vue       # 根组件
    │   ├── main.js       # 入口文件
    │   └── style.css     # 全局样式
    ├── public/           # 公共资源
    ├── index.html        # HTML模板
    ├── package.json      # 依赖配置
    ├── vite.config.js    # Vite配置
    └── webui.bat         # 前端启动脚本
```

## 🛠️ 环境要求

- **Python**: 3.7+
- **Node.js**: 14+
- **npm**: 6+

## 📦 安装依赖

### 后端依赖

#### 方式一：使用requirements.txt（推荐）
```bash
pip install -r requirements.txt
```

#### 方式二：手动安装
```bash
pip install fastapi uvicorn[standard] requests pandas pydantic[email] PyJWT bcrypt
```

### 前端依赖

```bash
cd webui
npm install
```
## 📦 SMTP配置
### 配置SMTP服务器
1. 在"user_api.py"中配置SMTP服务器地址（通常为 `smtp.{xxx}.com`）、端口号（465/587,并根据端口启动SSL/TLS）、邮箱地址和授权码等信息。

## 🚀 启动系统

### 方式一：使用批处理脚本分别启动（推荐）

1. **启动后端服务**
   ```bash
   # 在项目根目录下运行
   api.bat
   ```

2. **启动前端服务**
   ```bash
   # 在项目根目录下运行
   cd webui
   webui.bat
   ```
### 方式二：使用批处理脚本一键启动（推荐）

1. **一键启动前后端服务**
   ```bash
   # 在项目根目录下运行
   start.bat
   ```
   
   该脚本会自动：
   - 启动后端API服务（端口60001）
   - 启动前端开发服务器（端口60002）
   - 在新窗口中分别显示服务状态

### 方式三：手动启动

1. **启动后端API服务**
   ```bash
   python -m uvicorn api:app --reload --host 0.0.0.0 --port 60001
   ```

2. **启动前端开发服务器**
   ```bash
   cd webui
   npm run dev
   ```

### 访问系统

- **前端界面**：http://localhost:60002
- **后端API文档**：http://localhost:60001/docs

## 📖 使用说明

### 用户注册与登录

1. 首次使用需要注册账号，填写用户名、邮箱和密码
2. 注册成功后使用用户名和密码登录系统
3. 登录后可以访问所有功能模块

### 数据爬取

1. 在「数据爬取」页面填写表单：
   - **BV号**：必填，视频的BV号，例如 `BV1ex7VzREZ8`
   - **评论起始页**：可选，留空则从第一页开始爬取
   - **评论爬取模式**：选择「热门评论」或「最新评论」
   - **二级评论爬取**：是否爬取评论的回复
   - **爬取数量上限**：设置爬取评论的最大数量（1-1000）

2. 点击「开始爬取」按钮，系统会在后台开始爬取评论
3. 爬取记录会显示在下方的表格中，可以查看爬取状态和进度

### 数据展示

1. 在「数据展示」页面左侧选择一条爬取记录
2. 右侧会显示该记录的评论数据，支持分页浏览
3. 支持根据多种数据进行评论检索，并且可以直接下载检索后的数据
4. 可以通过下拉菜单调整每页显示的评论数量（30/60/100条）

### 数据图表

1. 在「数据图表」页面选择要分析的爬取记录
2. 系统会自动生成以下图表：
   - **性别分布饼状图**：展示评论者性别分布
   - **评论时间分布折线图**：显示24小时评论活跃度
   - **高回复评论词云**：热门讨论话题
   - **高点赞评论词云**：受欢迎的观点
   - **VIP用户分布图**：会员用户占比
   - **用户等级分布图**：用户等级统计

### 个人信息管理

1. 在「我的信息」页面可以查看和修改个人资料
2. 支持修改用户名、邮箱和密码
3. 显示账号权限等级信息

## ⚙️ 配置说明

### Cookie设置（可选）

如果需要爬取需要登录才能查看的评论，可以在 `bili_cookie.txt` 文件中填入自己的B站Cookie。

### 数据库

系统使用SQLite数据库，数据库文件为 `bilibili_CH.db`，包含以下主要表：
- `crawl_records`：爬取记录表
- `comments`：评论数据表
- `users`：用户信息表

## 🔧 技术栈

### 后端
- **FastAPI**：现代化的Python Web框架
- **SQLite3**：轻量级数据库
- **PyJWT**：JWT身份验证
- **bcrypt**：密码加密
- **requests**：HTTP请求库
- **pandas**：数据处理

### 前端
- **Vue 3**：渐进式JavaScript框架
- **Element Plus**：Vue 3组件库
- **ECharts**：数据可视化图表库
- **Vue Router 4**：路由管理
- **Pinia**：状态管理
- **Axios**：HTTP客户端
- **Vite**：构建工具

## ⚠️ 注意事项与免责声明

- 请合理设置爬取频率，避免对B站服务器造成过大压力
- 部分视频的评论可能需要登录后才能查看，此时需要配置Cookie
- 首次运行会自动创建数据库表结构
- 建议定期备份数据库文件

**免责声明**：本项目仅供学习和研究使用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。

爬虫违法违规案例参考：[中国爬虫违法违规案例汇总](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**开发环境**：Python 3.11 + Node.js 18 + Vue 3 + FastAPI