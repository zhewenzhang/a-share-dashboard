# 🚀 A 股资金追踪系统 - 部署指南

## 📋 系统要求

- Python 3.9+
- Node.js 16+ (可选，用于前端开发)
- pip (Python 包管理器)

---

## 🔧 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/zhewenzhang/a-share-dashboard.git
cd a-share-dashboard
```

### 2. 配置 TuShare Token（可选）

如果你想要获取真实的市场数据，需要配置 TuShare Token：

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 TuShare Token
# TUSHARE_TOKEN=your_token_here
```

**获取 TuShare Token 步骤：**
1. 访问 https://tushare.pro
2. 注册账号
3. 进入个人中心获取 Token
4. 将 Token 填入 `.env` 文件

> 💡 如果不配置 Token，系统将使用模拟数据运行

### 3. 安装后端依赖

```bash
cd backend
pip3 install -r requirements.txt
```

### 4. 启动后端服务

```bash
# 方式一：直接运行
python3 app/main.py

# 方式二：使用 uvicorn（推荐）
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 http://localhost:8000 启动

### 5. 访问应用

打开浏览器访问以下页面：

- **主页面（数据看板）**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **投资组合**: http://localhost:8000/portfolio.html
- **策略回测**: http://localhost:8000/backtest.html
- **模拟交易**: http://localhost:8000/simulate.html

---

## 📱 配置 TuShare

### 方法一：通过 .env 文件

1. 编辑 `backend/.env` 文件
2. 设置 `TUSHARE_TOKEN=your_token_here`
3. 重启后端服务

### 方法二：通过网页设置

1. 打开应用页面
2. 点击右上角 ⚙️ 设置图标
3. 输入 TuShare Token
4. 选择数据源为 "TuShare API"
5. 点击保存

---

## 🔍 API 接口说明

### 健康检查
```bash
GET /api/health
```

### 获取指数行情
```bash
GET /api/indices
```

### 获取板块资金流向
```bash
GET /api/sectors/flow
```

### 获取股票推荐
```bash
GET /api/recommendations?top_n=20
```

### 获取个股资金流向
```bash
GET /api/capital-flow/{ts_code}
```

### 获取历史资金流向
```bash
GET /api/capital-flow/history/{ts_code}?start_date=20240101&end_date=20240114
```

### 分析资金强度
```bash
GET /api/capital-flow/analysis/{ts_code}?days=10
```

### 测试 TuShare 连接
```bash
POST /api/tushare/test
```

---

## 🛠️ 开发模式

### 后端开发

```bash
cd backend
python3 -m uvicorn app.main:app --reload --log-level debug
```

### 前端开发

前端页面使用纯 HTML/CSS/JavaScript 实现，可以直接通过后端服务访问，也可以使用本地服务器：

```bash
cd frontend
npx http-server dist -p 3000
```

---

## 📊 数据说明

### 模拟数据 vs 真实数据

| 特性 | 模拟数据 | TuShare 真实数据 |
|------|---------|----------------|
| 配置要求 | 无需配置 | 需要 TuShare Token |
| 数据更新 | 固定值 | 实时更新 |
| 历史数据 | 有限 | 完整历史数据 |
| 权限要求 | 无 | 根据 Token 积分决定 |

### TuShare 积分说明

TuShare 采用积分制，不同接口需要不同积分：

- **基础接口** - 无需积分（如股票列表、日线行情）
- **进阶接口** - 需要 120 积分（如资金流向、北向资金）
- **高级接口** - 需要 600+ 积分（如板块资金流、龙虎榜）

访问 https://tushare.pro 了解积分获取方式。

---

## 🐛 常见问题

### 1. 后端服务无法启动

**检查 Python 版本：**
```bash
python3 --version  # 应该是 3.9+
```

**重新安装依赖：**
```bash
cd backend
pip3 install -r requirements.txt --force-reinstall
```

### 2. TuShare 连接失败

**检查 Token 配置：**
```bash
# 查看 .env 文件
cat backend/.env
```

**测试连接：**
```bash
curl -X POST http://localhost:8000/api/tushare/test
```

### 3. 数据为空或报错

- 检查 TuShare Token 是否有效
- 检查积分是否足够
- 查看后端日志了解详细错误信息

---

## 📝 日志查看

后端服务启动后，日志会输出到控制台：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

如需保存日志到文件：

```bash
python3 -m uvicorn app.main:app --log-config logging.conf > app.log 2>&1
```

---

## 🔄 更新升级

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
cd backend
pip3 install -r requirements.txt --upgrade

# 重启服务
```

---

## 📞 技术支持

如有问题，请通过以下方式反馈：

- **GitHub Issues**: https://github.com/zhewenzhang/a-share-dashboard/issues
- **GitHub Discussions**: https://github.com/zhewenzhang/a-share-dashboard/discussions

---

<div align="center">

**A 股资金追踪系统** | Made with ❤️

</div>
