# 📝 更新日志 (CHANGELOG)

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-03-14

### ✨ 新增

#### 核心功能
- **资金流向看板** - 实时展示主要指数行情和板块资金流向
- **智能选股推荐** - 基于资金强度评分 (0-100) 生成股票推荐列表
- **板块资金排行** - 行业/概念板块资金流入排名 TOP10
- **资金强度评分** - 多维度量化资金强度（主力净流入占比、连续性、加速度、北向变化）

#### 后端服务
- 新增 `TuShareService` 数据服务类，支持以下接口：
  - `get_moneyflow()` - 获取个股资金流向
  - `get_moneyflow_history()` - 获取历史资金流向
  - `get_stock_basic()` - 获取股票基本信息
  - `get_daily()` - 获取日线行情
  - `get_north_flow()` - 获取北向资金持股数据
  - `get_top_list()` - 获取龙虎榜数据
- 新增 `CapitalAnalyzer` 资金分析引擎：
  - `calc_capital_strength()` - 计算资金强度评分
  - `analyze_stocks()` - 批量分析股票
  - `generate_recommendations()` - 生成股票推荐
  - `analyze_sectors()` - 分析板块资金流向

#### API 接口
- `GET /api/health` - 健康检查
- `GET /api/capital-flow/{ts_code}` - 获取个股资金流向
- `GET /api/capital-flow/history/{ts_code}` - 获取历史资金流向
- `GET /api/capital-flow/analysis/{ts_code}` - 分析资金强度
- `GET /api/recommendations` - 获取智能推荐
- `GET /api/sectors/flow` - 获取板块资金流向
- `GET /api/indices` - 获取主要指数

#### 前端页面
- 深色金融终端主题 UI 设计
- 动态渐变背景和网格效果
- 指数卡片（支持涨跌状态和悬停光效）
- 板块资金流向 ECharts 图表
- 智能推荐股票表格（带资金强度评分条）
- 响应式设计（支持桌面、平板、手机）

#### 项目结构
- 完整的项目目录结构
- 后端 FastAPI 应用框架
- 前端静态页面
- 配置文件模板（.env.example）
- Python 依赖配置（requirements.txt）
- Node.js 配置（package.json）

### 📖 文档

- 新增 `README.md` - 项目说明和使用指南
- 新增 `PROJECT_DESIGN.md` - 完整的项目设计文档（647 行）
- 新增 `CHANGELOG.md` - 更新日志
- 新增 `VERSION` - 版本号文件

### 🔧 技术

- 使用 FastAPI 构建高性能后端
- 使用 TuShare 作为 A 股数据源
- 使用 Pandas 进行数据处理
- 使用 Pydantic 进行数据验证
- 使用 ECharts 5 进行数据可视化
- 使用 Inter 和 JetBrains Mono 字体提升专业感

### 📦 配置

- 新增 `.env.example` 环境变量模板
- 新增 `.gitignore` Git 忽略规则
- 支持通过环境变量配置 TuShare Token

---

## [0.1.0] - 2026-02-16

### ✨ 新增

- 初始版本 - 基础 A 股市场看板
- 模拟数据展示
- 简单的 HTML+CSS+JavaScript 实现
- ECharts 图表集成

---

## 版本说明

### 语义化版本格式

- **主版本号 (Major)** - 不兼容的 API 变更
- **次版本号 (Minor)** - 向下兼容的功能性新增
- **修订号 (Patch)** - 向下兼容的问题修正

### 变更类型说明

- **新增 (Added)** - 新功能
- **修改 (Changed)** - 现有功能的变更
- **弃用 (Deprecated)** - 即将移除的功能
- **移除 (Removed)** - 已移除的功能
- **修复 (Fixed)** - Bug 修复
- **安全 (Security)** - 安全性修复

---

## 📅 发布计划

### v1.1.0 (计划中)
- [ ] 个股资金追踪详情页
- [ ] 北向资金监控
- [ ] 龙虎榜数据展示

### v1.2.0 (计划中)
- [ ] 投资组合管理模块
- [ ] 持仓盈亏计算
- [ ] 风险指标展示

### v2.0.0 (计划中)
- [ ] 策略回测引擎
- [ ] 绩效评估体系
- [ ] 模拟交易功能

---

## 📞 反馈

如有问题或建议，请通过以下方式反馈：

- **GitHub Issues**: https://github.com/zhewenzhang/a-share-dashboard/issues
- **GitHub Discussions**: https://github.com/zhewenzhang/a-share-dashboard/discussions

---

<div align="center">

**A 股资金追踪系统** | Made with ❤️

</div>
