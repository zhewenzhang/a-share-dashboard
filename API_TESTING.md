# 🔌 API 连接测试指南

## 问题修复说明

### 之前的问题
- ❌ 前端使用相对路径 `/api/xxx`，在端口 8080 请求不到 8000 端口的 API
- ❌ GitHub Pages 静态页面无法访问本地 API
- ❌ 错误提示不明确，无法定位问题

### 修复内容
- ✅ 添加 `API_CONFIG` 配置，自动检测环境并使用正确的 API 地址
- ✅ 本地开发使用 `http://localhost:8000`
- ✅ 改进错误提示，显示请求 URL 和解决方案
- ✅ 页面加载时自动检查 API 状态

---

## 🏠 本地测试步骤

### 1. 启动后端服务（端口 8000）

```bash
cd /Users/dave/a-share-dashboard/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

确认后端启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 启动前端服务（端口 8080）

```bash
cd /Users/dave/a-share-dashboard
python3 -m http.server 8080
```

### 3. 访问页面并测试 API

打开浏览器访问：
```
http://localhost:8080
```

点击右上角 **"API 测试"** 按钮，然后点击 **"健康检查"**。

---

## ✅ 预期结果

### 成功连接
```json
{
  "status": "ok",
  "version": "3.0.5",
  "tushare_configured": true,
  "timestamp": "2026-03-15T22:00:08.044453"
}
```

顶部状态指示器显示：**"API v3.0.5"** 或 **"API 已连接"**

### 连接失败
```json
{
  "status": "error",
  "error": "Failed to fetch",
  "url": "http://localhost:8000/api/health",
  "message": "无法连接到后端服务",
  "solution": "请确保后端服务已启动: python -m uvicorn app.main:app --reload"
}
```

---

## 🔧 故障排除

### 问题 1: "Failed to fetch" 或 "无法连接"

**检查清单：**
- [ ] 后端服务是否已启动？`ps aux | grep uvicorn`
- [ ] 后端端口是否正确？默认 8000
- [ ] 前端页面 URL 是否是 `localhost:8080`？

**解决方案：**
```bash
# 1. 检查后端进程
ps aux | grep uvicorn

# 2. 如果没有运行，启动后端
cd /Users/dave/a-share-dashboard/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 测试后端是否响应
curl http://localhost:8000/api/health
```

### 问题 2: CORS 跨域错误

**错误信息：**
```
Access to fetch at 'http://localhost:8000/api/health' from origin 'http://localhost:8080' has been blocked by CORS policy
```

**解决方案：**
后端已配置 CORS 允许所有来源，如果仍有问题，检查：
1. 后端是否是最新版本
2. 重启后端服务

### 问题 3: GitHub Pages 无法测试 API

**说明：**
GitHub Pages 是静态页面托管，无法直接访问本地 API。

**解决方案：**
1. 在本地测试 API 功能
2. 部署后端到云服务器后，修改 `API_CONFIG.production` 地址

---

## 🌐 GitHub Pages 限制

GitHub Pages 只能托管静态文件，**无法直接运行后端 API**。

### 临时解决方案

使用浏览器插件绕过 CORS（仅限开发测试）：

**Chrome 扩展：**
- Allow CORS: Access-Control-Allow-Origin
- Moesif Origin & CORS Changer

**注意：** 这只是临时方案，生产环境需要部署后端服务。

### 长期解决方案

1. **部署后端到云服务器**
   - 使用 Vercel、Railway、Heroku 等部署 FastAPI
   - 修改 `API_CONFIG.production` 为实际 API 地址

2. **使用 Vercel Serverless Functions**
   - 将后端 API 转换为 Vercel API Routes
   - 前后端同域部署，避免跨域问题

---

## 📊 API 配置说明

### 前端配置 (`index.html`)

```javascript
const API_CONFIG = {
    // 本地开发环境
    local: 'http://localhost:8000',
    
    // 生产环境（部署后端后修改）
    production: '',
    
    // 自动检测当前环境
    get baseUrl() {
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1') {
            return this.local;
        }
        return '';  // GitHub Pages 使用相对路径
    }
};
```

### 后端 CORS 配置 (`backend/app/main.py`)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 测试命令

### 测试后端 API

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取指数
curl http://localhost:8000/api/indices

# 测试 TuShare 连接
curl -X POST http://localhost:8000/api/tushare/test

# 获取板块资金流
curl http://localhost:8000/api/sectors/flow
```

### 测试前端页面

```bash
# 本地访问
curl http://localhost:8080 | head -20

# 检查 API 配置是否正确加载
curl http://localhost:8080 | grep -A 10 "API_CONFIG"
```

---

## 📝 更新日志

### 2026-03-15
- ✅ 修复 API 连接问题
- ✅ 添加 `API_CONFIG` 自动配置
- ✅ 改进错误提示信息
- ✅ 添加 API 状态自动检测

---

## ❓ 常见问题

**Q: 为什么 GitHub Pages 无法测试 API？**
A: GitHub Pages 是静态托管，不支持后端服务。需要在本地或部署后端服务器。

**Q: 如何部署后端到生产环境？**
A: 可以使用 Vercel、Railway、Heroku 等平台部署 FastAPI，然后修改 `API_CONFIG.production`。

**Q: 可以修改 API 端口吗？**
A: 可以，修改 `API_CONFIG.local` 为需要的端口，如 `http://localhost:3000`。

**Q: 如何同时运行前后端？**
A: 使用两个终端窗口，一个运行后端（端口 8000），一个运行前端（端口 8080）。

---

**最后更新**: 2026-03-15  
**版本**: v3.0.5
