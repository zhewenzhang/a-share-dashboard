# 🏃 运行环境说明

## 快速开始

### 方式一：GitHub Pages（推荐）

直接访问已部署的在线版本：

**https://zhewenzhang.github.io/a-share-dashboard/**

无需安装，打开浏览器即可使用。

---

### 方式二：本地运行（静态模式）

#### 1. 克隆项目

```bash
git clone https://github.com/zhewenzhang/a-share-dashboard.git
cd a-share-dashboard
```

#### 2. 使用 Python 运行

```bash
# Python 3
python3 -m http.server 8000

# 或使用任意端口
python3 -m http.server 3000
```

#### 3. 使用 Node.js 运行

```bash
# 安装 http-server（首次）
npm install -g http-server

# 运行
http-server -p 8000
```

#### 4. 使用 VS Code Live Server

1. 安装 Live Server 扩展
2. 右键 `index.html`
3. 选择 "Open with Live Server"

#### 5. 访问应用

打开浏览器访问：

```
http://localhost:8000
```

---

### 方式三：完整部署（前后端）

#### 后端环境

**要求**: Python 3.9+

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
# 编辑 .env 填入 TuShare Token

# 启动服务
python app/main.py

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端环境

**要求**: Node.js 18+

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

---

## 配置 TuShare

### 获取 Token

1. 访问 https://tushare.pro
2. 注册账号
3. 进入个人中心获取 Token
4. 需要一定积分才能访问高级接口

### 配置方式

#### 网页配置（推荐）

1. 点击右上角 ⚙️ 设置
2. 输入 TuShare Token
3. 选择数据源为 "TuShare API"
4. 点击保存

#### 环境变量配置

创建 `.env` 文件：

```bash
# TuShare API Token
TUSHARE_TOKEN=your_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/ashare.db

# 服务配置
BACKEND_URL=http://localhost:8000
LOG_LEVEL=INFO
```

---

## 功能测试

### API 接口测试

1. 点击侧边栏 "API 测试"
2. 选择要测试的接口
3. 点击 "发送请求"
4. 查看响应结果

### 快速测试

- **健康检查** - 测试服务状态
- **连通性测试** - 测试 API 延迟
- **数据获取** - 测试数据接口
- **权限测试** - 检查 Token 配置

---

## 端口说明

| 服务 | 默认端口 | 说明 |
|------|---------|------|
| HTTP Server | 8000 | 静态页面 |
| Backend API | 8000 | FastAPI 后端 |
| Frontend Dev | 3000 | Vite 开发服务器 |

---

## 浏览器要求

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 常见问题

### Q: 页面显示"模拟数据"？

A: 这是正常的。配置 TuShare Token 后会显示真实数据。

### Q: API 请求失败？

A: 当前为静态页面模式，需要启动后端服务。

### Q: 如何在本地查看完整功能？

A: 
1. 配置 TuShare Token
2. 启动后端服务
3. 访问 http://localhost:8000

### Q: GitHub Pages 无法访问？

A: 
- 检查网络连接
- 清除浏览器缓存
- 尝试无痕模式访问

---

## 项目结构

```
a-share-dashboard/
├── index.html              # 主页面（数据看板）
├── portfolio.html          # 投资组合
├── backtest.html           # 策略回测
├── simulate.html           # 模拟交易
├── frontend/
│   └── dist/               # 部署文件
├── backend/
│   └── app/                # 后端代码
├── .env.example            # 环境变量示例
├── requirements.txt        # Python 依赖
└── package.json            # Node.js 配置
```

---

## 部署说明

### GitHub Pages 部署

项目已配置自动部署：

1. 推送到 main 分支
2. GitHub Actions 自动构建
3. 部署到 GitHub Pages

### 本地部署到服务器

```bash
# 使用 Nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/a-share-dashboard/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 技术支持

- **GitHub Issues**: https://github.com/zhewenzhang/a-share-dashboard/issues
- **项目主页**: https://github.com/zhewenzhang/a-share-dashboard

---

**当前版本**: v3.0.1  
**最后更新**: 2026-03-14
