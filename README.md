# 📊 A 股资金追踪系统

<div align="center">

**专业的 A 股资金流向追踪与智能投顾平台**

[![Version](https://img.shields.io/github/v/release/zhewenzhang/a-share-dashboard?label=Version&color=6366f1)](https://github.com/zhewenzhang/a-share-dashboard/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-6366f1.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-6366f1.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-6366f1.svg)](https://fastapi.tiangolo.com/)

[📖 项目设计](PROJECT_DESIGN.md) | [🚀 在线演示](https://zhewenzhang.github.io/a-share-dashboard/) | [📝 更新日志](CHANGELOG.md)

</div>

---

## 🌟 项目简介

A 股资金追踪系统是一个专业的股票资金流向分析平台，基于 TuShare 数据实时监控股市资金动向，提供智能板块/个股推荐、投资组合管理、风险预警、策略回测和模拟交易功能。

### ✨ 核心特性

- 🔍 **资金流向追踪** - 实时监控主力/北向/板块资金动向
- 📈 **智能选股推荐** - 基于资金强度评分 (0-100) 生成股票池
- 💼 **投资组合管理** - 持仓跟踪、盈亏计算、风险分析
- ⚠️ **风险预警系统** - 价格/资金/持仓多维度预警
- 🧪 **策略回测引擎** - 历史数据验证策略有效性
- 🎯 **模拟交易** - 实时模拟盘运行，零风险验证策略
- 📊 **TuShare 实时数据** - 支持配置 TuShare Token 获取真实市场数据

---

## 🚀 快速开始

### 在线演示

访问 GitHub Pages 查看演示：

👉 **https://zhewenzhang.github.io/a-share-dashboard/**

> 💡 当前演示使用模拟数据，配置 TuShare Token 后显示真实数据

### 配置 TuShare

1. 访问页面点击右上角 ⚙️ 设置
2. 输入你的 TuShare Token
3. 选择数据源为 "TuShare API"
4. 点击保存即可

### 本地部署

#### 1. 克隆项目

```bash
git clone https://github.com/zhewenzhang/a-share-dashboard.git
cd a-share-dashboard
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 启动后端服务

```bash
# 方式一：直接运行
python app/main.py

# 方式二：使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. 访问应用

- **前端页面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 📁 项目结构

```
a-share-dashboard/
├── backend/                     # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── core/                # 核心配置
│   │   │   └── config.py        # 应用配置
│   │   ├── services/            # 业务服务
│   │   │   ├── tushare_service.py   # TuShare 数据服务
│   │   │   └── capital_analyzer.py  # 资金分析引擎
│   │   └── main.py              # FastAPI 应用入口
│   └── requirements.txt         # Python 依赖
│
├── frontend/                    # 前端页面
│   ├── dist/
│   │   └── index.html           # 资金看板页面
│   └── package.json             # Node.js 配置
│
├── docs/                        # 文档
│   ├── PROJECT_DESIGN.md        # 项目设计文档
│   └── CHANGELOG.md             # 更新日志
│
├── index.html                   # 主页面 (GitHub Pages 部署)
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git 忽略文件
├── VERSION                      # 版本号
└── README.md                    # 项目说明
```

---

## 📊 功能特性

### 第一阶段：资金流向追踪（✅ 已完成）

| 功能 | 描述 | 状态 |
|------|------|------|
| **实时指数看板** | 上证/深证/创业板/沪深 300 实时行情 | ✅ |
| **板块资金流向** | 行业/概念板块资金流入排名 | ✅ |
| **智能选股推荐** | 基于资金强度评分生成推荐列表 | ✅ |
| **资金强度评分** | 0-100 分量化资金强度 | ✅ |
| **个股资金追踪** | 单只股票资金流入流出监控 | ✅ |
| **TuShare 配置** | 网页内配置 API Token | ✅ |
| **侧边栏导航** | 现代化侧边栏布局 | ✅ |

### 第二阶段：投资组合管理（🔄 开发中）

- [ ] 持仓管理模块
- [ ] 每日盈亏计算
- [ ] 价格预警 / 资金流出预警
- [ ] 风险指标（最大回撤、夏普比率）

### 第三阶段：回测与模拟（📋 规划中）

- [ ] 策略历史回测
- [ ] 绩效评估体系
- [ ] 模拟交易运行

---

## 🔧 API 接口

### 健康检查

```bash
GET /api/health
```

### 资金流向

```bash
# 获取个股资金流向
GET /api/capital-flow/{ts_code}

# 获取历史资金流向
GET /api/capital-flow/history/{ts_code}?start_date=20240101&end_date=20240114

# 分析资金强度
GET /api/capital-flow/analysis/{ts_code}?days=10
```

### 智能推荐

```bash
# 获取股票推荐列表
GET /api/recommendations?top_n=20&industry=半导体
```

### 板块资金

```bash
# 获取板块资金流向排行
GET /api/sectors/flow
```

### 指数行情

```bash
# 获取主要指数
GET /api/indices
```

---

## 📈 资金强度评分算法

```python
评分 = (
    主力净流入占比 × 40% +    # 大单/特大单净流入占成交额比例
    连续性评分 × 30% +       # 连续 N 日主力净流入
    加速度评分 × 20% +       # 资金流入加速度
    北向变化评分 × 10%       # 北向资金持股变化
)
```

### 评分等级

| 评分 | 等级 | 建议 |
|------|------|------|
| 80-100 | 🔥 极强 | 强烈买入 |
| 60-79 | 📈 良好 | 买入 |
| 40-59 | ⚠️ 中性 | 观察 |
| 0-39 | 📉 弱势 | 谨慎 |

---

## 🔐 配置说明

### TuShare Token

1. 访问 https://tushare.pro
2. 注册账号
3. 进入个人中心获取 Token
4. 在网页设置中配置 Token

### 数据源切换

- **模拟数据** - 演示模式，无需配置
- **TuShare API** - 真实数据，需要 Token

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **TuShare** - A 股数据源
- **Pandas** - 数据处理
- **Pydantic** - 数据验证

### 前端
- **原生 HTML/CSS/JS** - 轻量级实现
- **ECharts 5** - 图表可视化
- **现代 CSS** - Flexbox/Grid布局

---

## 📋 开发计划

### 第一阶段 (✅ 已完成)
- [x] 项目初始化
- [x] TuShare 数据接入
- [x] 资金分析引擎
- [x] 现代化 UI 设计
- [x] 侧边栏导航
- [x] TuShare 配置功能
- [x] 智能推荐功能

### 第二阶段 (🔄 开发中)
- [ ] 投资组合管理模块
- [ ] 预警系统开发
- [ ] 风险指标计算

### 第三阶段 (📋 规划中)
- [ ] 回测引擎开发
- [ ] 绩效评估体系
- [ ] 模拟交易模块

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解完整更新历史。

### v3.0.4 (2026-03-14)
- 🎨 **全新现代化 UI** - 专业侧边栏导航布局
- 🔧 **TuShare 配置** - 网页内配置 API Token
- 📊 **高级功能** - 数据导出、筛选、排序、搜索
- 📱 **响应式设计** - 完美适配移动端
- ⚡ **性能优化** - 优化加载速度和交互体验
- 🔄 **版本同步** - 所有页面统一 v3.0.4

### v3.0.3 (2026-03-14)
- 🎨 **专业 UI 重构** - 移除 emoji，使用专业 SVG 图标
- 🔌 **API 接口测试** - 内置 API 测试工具，支持快速测试
- 🔐 **权限测试** - TuShare Token 配置状态检查
- 🔗 **连通性测试** - API 延迟和连接状态检测
- ✨ **UI 优化** - 专业深色主题，Inter 字体，精致卡片设计
- 📱 **响应式优化** - 移动端菜单改进
- ⚡ **性能优化** - 减少动画，提升加载速度

### v3.0.2 (2026-03-14)
- ✨ **新增模拟交易页面** - 完整的模拟交易功能
- 📊 **增强数据可视化** - 更多图表和指标
- 🔧 **优化 API 接口** - 提升数据获取性能
- 🎯 **改进推荐算法** - 更精准的选股策略
- 📱 **移动端适配** - 优化触屏操作体验

### v3.0.0 (2026-03-14)
- ✨ **策略回测引擎** - 完整的策略回测系统
  - 6 种预设策略（资金流/北向/板块轮动/动量/反转/聪明钱）
  - 自定义回测参数（日期/资金/手续费）
  - 净值曲线对比（对比赛道基准）
  - 交易记录明细
- ✨ **模拟交易** - 实时模拟盘运行
  - 买入/卖出交易
  - 持仓管理
  - 盈亏计算
  - 资产走势图表
  - 行业分布可视化
- ✨ **绩效评估** - 专业回测指标
  - 总收益率/年化收益
  - 最大回撤
  - 夏普比率
  - 胜率统计
- ✨ **数据导出** - 回测报告 CSV 导出

### v2.1.0 (2026-03-14)
- ✨ **投资组合管理** - 完整的持仓管理系统
- ✨ **盈亏计算** - 实时计算持仓盈亏和收益率
- ✨ **风险指标** - 最大回撤/夏普比率/波动率/胜率
- ✨ **预警系统** - 跌幅/止盈自动预警通知
- ✨ **行业分布** - 饼图可视化持仓行业分布
- ✨ **数据导出** - 投资组合 CSV 导出
- ✨ **本地存储** - 持仓数据自动保存

### v2.0.0 (2026-03-14)
- ✨ 全新现代化 UI 设计
- ✨ 侧边栏导航布局
- ✨ TuShare 网页内配置
- ✨ 本地存储配置
- ✨ Toast 通知系统
- ✨ 详情弹窗优化

### v1.1.0 (2026-03-14)
- ✨ 个股搜索功能
- ✨ 行业筛选功能
- ✨ 股票列表排序
- ✨ 详情弹窗
- ✨ 导出功能

### v1.0.0 (2026-03-14)
- ✨ 初始版本发布
- ✨ 资金流向看板
- ✨ 智能选股推荐
- ✨ 板块资金排行

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- **作者**: zhewenzhang
- **项目**: https://github.com/zhewenzhang/a-share-dashboard

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star 支持！**

Made with ❤️ by AI Assistant

</div>
