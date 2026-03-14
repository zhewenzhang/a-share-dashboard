# 🎯 A 股资金追踪与智能投顾系统 - 项目设计文档

## 📋 项目愿景

构建一个专业的 A 股资金流向追踪系统，通过 TuShare 数据实时监控股市资金动向，提供智能板块/个股推荐，支持投资组合管理、风险预警、策略回测和模拟交易功能。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           A 股资金追踪系统                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      前端展示层 (React + ECharts)                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│  │  │ 资金看板 │ │ 持仓管理 │ │ 策略回测 │ │ 模拟交易         │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      API 服务层 (FastAPI)                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│  │  │ 资金分析 │ │ 投资组合 │ │ 回测引擎 │ │ 预警通知         │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      数据处理层                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│  │  │ TuShare  │ │ 数据清洗 │ │ 特征工程 │ │ 策略计算         │   │   │
│  │  │ 数据源   │ │ 存储     │ │ 指标计算 │ │ 信号生成         │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      数据存储层                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │   │
│  │  │ SQLite   │ │ Redis    │ │ 文件存储 │                        │   │
│  │  │ 关系数据 │ │ 缓存     │ │ 日志/报告│                        │   │
│  │  └──────────┘ └──────────┘ └──────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 TuShare 核心数据接口

### 第一阶段：资金流向追踪

| 接口名称 | 接口代码 | 用途 | 积分需求 |
|---------|---------|------|---------|
| **个股资金流向** | `moneyflow` | 追踪单只股票主力资金净流入 | 基础 |
| **板块资金流向** | `moneyflow_ind` | 追踪行业板块资金流向 | 基础 |
| **北向资金** | `north_flow` | 监控沪深股通资金动向 | 进阶 |
| **主力资金流向** | `main_moneyflow` | 追踪超大单/大单资金 | 进阶 |
| **龙虎榜数据** | `top_list` | 追踪游资/机构席位动向 | 进阶 |
| **大宗交易** | `block_trade` | 监控大额协议转让 | 基础 |

### 第二阶段：投资组合管理

| 接口名称 | 接口代码 | 用途 |
|---------|---------|------|
| **实时行情** | `daily` | 获取股票日线数据 |
| **持仓盈亏** | `portfolio_daily` | 计算每日持仓变动 |
| **个股信息** | `stock_basic` | 股票基本信息 |
| **行业分类** | `index_classify` | 股票所属行业 |

### 第三阶段：回测与模拟

| 接口名称 | 接口代码 | 用途 |
|---------|---------|------|
| **历史行情** | `daily` | 获取历史 K 线数据 |
| **复权因子** | `adj_factor` | 计算复权价格 |
| **财务指标** | `fina_indicator` | 基本面数据 |
| **指数行情** | `index_daily` | 大盘对比基准 |

---

## 🎯 三阶段详细设计

### 🔴 第一阶段：资金流向追踪与投资建议（核心）

#### 1.1 资金流向分析引擎

```python
# 核心数据结构
class CapitalFlow:
    """资金流向数据模型"""
    ts_code: str           # 股票代码
    trade_date: str        # 交易日期
    buy_sm_amount: float   # 小单买入金额
    buy_big_amount: float  # 大单买入金额
    sell_sm_amount: float  # 小单卖出金额
    sell_big_amount: float # 大单卖出金额
    net_amount: float      # 净流入金额
    
    @property
    def is_main_inflow(self) -> bool:
        """是否主力净流入"""
        return self.net_amount > 0
    
    @property
    def strength_score(self) -> float:
        """资金强度评分 (0-100)"""
        # 基于净流入占成交额比例计算
        ...
```

#### 1.2 资金追踪策略模块

```
┌────────────────────────────────────────────────────────────┐
│                    资金追踪策略引擎                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. 主力资金连续流入策略                                    │
│     - 连续 N 日主力净流入                                    │
│     - 净流入金额递增                                         │
│     - 配合成交量放大                                         │
│                                                            │
│  2. 北向资金追踪策略                                        │
│     - 沪深股通持股比例变化                                   │
│     - 北向资金连续买入                                       │
│     - 与内资背离信号                                         │
│                                                            │
│  3. 板块轮动策略                                            │
│     - 行业资金流入排名                                       │
│     - 资金流入加速度                                         │
│     - 板块内个股联动                                         │
│                                                            │
│  4. 龙虎榜游资追踪                                          │
│     - 知名游资席位识别                                       │
│     - 机构席位净买入                                         │
│     - 游资接力模式                                           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### 1.3 智能推荐引擎

```python
class StockRecommender:
    """股票推荐引擎"""
    
    def generate_recommendations(self) -> List[StockRecommendation]:
        """生成投资建议"""
        recommendations = []
        
        # 1. 资金面评分 (权重 40%)
        capital_score = self.capital_analysis()
        
        # 2. 技术面评分 (权重 30%)
        technical_score = self.technical_analysis()
        
        # 3. 基本面评分 (权重 30%)
        fundamental_score = self.fundamental_analysis()
        
        # 综合评分
        total_score = (
            capital_score * 0.4 + 
            technical_score * 0.3 + 
            fundamental_score * 0.3
        )
        
        # 生成推荐列表
        return self.rank_stocks(total_score)
```

#### 1.4 第一阶段功能清单

| 功能模块 | 功能描述 | 优先级 |
|---------|---------|--------|
| **资金流向看板** | 实时展示主力/北向/板块资金流向 | P0 |
| **个股资金追踪** | 监控单只股票资金流入流出 | P0 |
| **板块资金排行** | 行业/概念板块资金流入排名 | P0 |
| **智能选股推荐** | 基于资金面生成股票池 | P0 |
| **资金强度评分** | 0-100 分量化资金强度 | P1 |
| **龙虎榜监控** | 游资/机构席位追踪 | P1 |
| **北向资金监控** | 沪深股通持股变化 | P1 |
| **大宗交易监控** | 大额协议转让提醒 | P2 |

---

### 🟡 第二阶段：投资组合管理与预警

#### 2.1 投资组合管理

```python
class Portfolio:
    """投资组合管理"""
    
    positions: Dict[str, Position]  # 持仓
    cash: float                      # 可用资金
    total_value: float               # 总资产
    
    def update_daily(self):
        """每日更新持仓盈亏"""
        for position in self.positions.values():
            position.update_price()
            position.calc_profit()
    
    def risk_metrics(self) -> RiskMetrics:
        """计算风险指标"""
        return RiskMetrics(
            max_drawdown=self.calc_max_drawdown(),
            sharpe_ratio=self.calc_sharpe(),
            concentration=self.calc_concentration(),
            beta=self.calc_beta()
        )
```

#### 2.2 预警系统

```
┌────────────────────────────────────────────────────────────┐
│                      预警系统架构                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  预警类型：                                                 │
│  ┌────────────────┐  ┌────────────────┐                   │
│  │ 价格预警       │  │ 资金预警       │                   │
│  │ - 涨跌幅超阈值 │  │ - 主力大幅流出 │                   │
│  │ - 突破关键位   │  │ - 北向减持     │                   │
│  │ - 止损/止盈    │  │ - 大宗折价     │                   │
│  └────────────────┘  └────────────────┘                   │
│                                                            │
│  ┌────────────────┐  ┌────────────────┐                   │
│  │ 持仓预警       │  │ 市场预警       │                   │
│  │ - 单一持仓过重 │  │ - 大盘大跌     │                   │
│  │ - 行业集中度高 │  │ - 行业利空     │                   │
│  │ - 回撤超阈值   │  │ - 黑天鹅事件   │                   │
│  └────────────────┘  └────────────────┘                   │
│                                                            │
│  通知方式：                                                 │
│  - 站内消息                                                │
│  - 邮件通知                                                │
│  - 微信推送 (可选)                                          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### 2.3 第二阶段功能清单

| 功能模块 | 功能描述 | 优先级 |
|---------|---------|--------|
| **持仓管理** | 记录持仓成本/数量/盈亏 | P0 |
| **每日盈亏** | 自动计算持仓当日变动 | P0 |
| **价格预警** | 涨跌幅/止损止盈提醒 | P0 |
| **资金预警** | 主力流出/北向减持提醒 | P0 |
| **风险指标** | 最大回撤/夏普比率等 | P1 |
| **持仓分析** | 行业分布/集中度分析 | P1 |
| **交易记录** | 买卖记录/盈亏统计 | P1 |
| **消息推送** | 多渠道预警通知 | P2 |

---

### 🟢 第三阶段：回测与模拟交易

#### 3.1 回测引擎

```python
class BacktestEngine:
    """策略回测引擎"""
    
    def __init__(self, strategy, start_date, end_date, initial_capital):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
    
    def run(self) -> BacktestResult:
        """运行回测"""
        # 获取历史数据
        data = self.load_historical_data()
        
        # 逐日回测
        for date in data.trading_dates:
            # 生成交易信号
            signals = self.strategy.generate_signals(date)
            
            # 执行交易
            self.execute_trades(signals, date)
            
            # 更新持仓
            self.update_positions(date)
            
            # 记录净值
            self.record_daily_value(date)
        
        # 计算绩效指标
        return self.calc_performance_metrics()
```

#### 3.2 绩效评估指标

```
┌────────────────────────────────────────────────────────────┐
│                    回测绩效评估体系                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  收益指标：                                                 │
│  - 总收益率 / 年化收益率                                    │
│  - 超额收益 (相对基准)                                       │
│  - 月度收益分布                                             │
│                                                            │
│  风险指标：                                                 │
│  - 最大回撤                                                 │
│  - 波动率 (年化)                                             │
│  - VaR (风险价值)                                            │
│                                                            │
│  风险调整收益：                                             │
│  - 夏普比率                                                 │
│  - 索提诺比率                                               │
│  - 卡玛比率                                                 │
│                                                            │
│  交易统计：                                                 │
│  - 总交易次数                                               │
│  - 胜率 / 盈亏比                                             │
│  - 平均持仓周期                                             │
│  - 换手率                                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### 3.3 模拟交易

```python
class PaperTrading:
    """模拟交易"""
    
    def __init__(self, strategy, initial_capital=1000000):
        self.capital = initial_capital
        self.strategy = strategy
        self.positions = {}
        self.orders = []
    
    def on_market_open(self, date):
        """开盘处理"""
        # 生成交易信号
        signals = self.strategy.generate_signals(date)
        
        # 创建订单
        for signal in signals:
            order = self.create_order(signal)
            self.orders.append(order)
    
    def on_market_close(self, date):
        """收盘处理"""
        # 执行订单 (使用收盘价)
        for order in self.orders:
            order.execute(price=date.close)
        
        # 更新持仓和资金
        self.update_positions()
        
        # 记录每日净值
        self.record_nav(date)
```

#### 3.4 第三阶段功能清单

| 功能模块 | 功能描述 | 优先级 |
|---------|---------|--------|
| **策略回测** | 历史数据验证策略 | P0 |
| **绩效分析** | 收益/风险指标计算 | P0 |
| **模拟交易** | 实时模拟盘运行 | P0 |
| **策略对比** | 多策略绩效对比 | P1 |
| **参数优化** | 网格搜索最优参数 | P1 |
| **归因分析** | 收益来源分解 | P1 |
| **蒙特卡洛模拟** | 策略稳健性检验 | P2 |
| **实盘对接** | 对接券商 API(可选) | P3 |

---

## 🗂️ 项目目录结构

```
a-share-dashboard/
├── frontend/                    # 前端 (React)
│   ├── src/
│   │   ├── components/          # 可复用组件
│   │   │   ├── CapitalFlow/     # 资金流向组件
│   │   │   ├── Portfolio/       # 持仓管理组件
│   │   │   ├── Backtest/        # 回测组件
│   │   │   └── common/          # 通用组件
│   │   ├── pages/               # 页面
│   │   │   ├── Dashboard/       # 资金看板
│   │   │   ├── StockPool/       # 股票池
│   │   │   ├── Portfolio/       # 投资组合
│   │   │   ├── Backtest/        # 回测页面
│   │   │   └── Settings/        # 设置
│   │   ├── services/            # API 服务
│   │   ├── store/               # 状态管理
│   │   └── utils/               # 工具函数
│   └── package.json
│
├── backend/                     # 后端 (FastAPI)
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   │   ├── capital_flow.py  # 资金流向 API
│   │   │   ├── portfolio.py     # 投资组合 API
│   │   │   ├── backtest.py      # 回测 API
│   │   │   └── alert.py         # 预警 API
│   │   ├── core/                # 核心配置
│   │   │   ├── config.py        # 配置文件
│   │   │   └── security.py      # 安全认证
│   │   ├── models/              # 数据模型
│   │   │   ├── stock.py         # 股票模型
│   │   │   ├── capital.py       # 资金模型
│   │   │   └── portfolio.py     # 持仓模型
│   │   ├── services/            # 业务服务
│   │   │   ├── tushare_service.py  # TuShare 服务
│   │   │   ├── capital_analyzer.py # 资金分析
│   │   │   ├── strategy.py      # 策略服务
│   │   │   └── backtest_engine.py # 回测引擎
│   │   └── db/                  # 数据库
│   │       ├── database.py      # 数据库连接
│   │       └── repositories.py  # 数据访问层
│   ├── requirements.txt
│   └── main.py
│
├── data/                        # 数据存储
│   ├── sqlite/                  # SQLite 数据库
│   ├── cache/                   # Redis 缓存
│   └── logs/                    # 日志文件
│
├── strategies/                  # 策略库
│   ├── capital_flow_strategy.py # 资金流向策略
│   ├── north_flow_strategy.py   # 北向资金策略
│   └── sector_rotation.py       # 板块轮动策略
│
├── tests/                       # 测试
│   ├── test_capital_flow.py
│   ├── test_backtest.py
│   └── test_strategy.py
│
├── docs/                        # 文档
│   ├── api.md                   # API 文档
│   ├── strategy_guide.md        # 策略指南
│   └── deployment.md            # 部署指南
│
├── .env.example                 # 环境变量示例
├── docker-compose.yml           # Docker 配置
└── README.md                    # 项目说明
```

---

## 🔧 技术栈选型

### 前端
| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| TypeScript | 类型安全 |
| ECharts 5 | 图表可视化 |
| TailwindCSS | 样式 |
| Zustand | 状态管理 |
| React Query | 数据获取 |

### 后端
| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| SQLAlchemy | ORM |
| SQLite | 主数据库 |
| Redis | 缓存 |
| APScheduler | 定时任务 |
| Pydantic | 数据验证 |

### 数据
| 技术 | 用途 |
|------|------|
| TuShare Pro | 行情数据源 |
| AKShare | 补充数据源 |
| Pandas | 数据处理 |
| NumPy | 数值计算 |

---

## 📅 开发计划

### 第一阶段 (4 周)
| 周次 | 任务 | 交付物 |
|------|------|--------|
| 第 1 周 | 项目初始化、TuShare 接入 | 数据获取服务 |
| 第 2 周 | 资金流向分析引擎 | 核心分析模块 |
| 第 3 周 | 前端资金看板开发 | 可视化界面 |
| 第 4 周 | 智能推荐引擎 | 股票推荐功能 |

### 第二阶段 (3 周)
| 周次 | 任务 | 交付物 |
|------|------|--------|
| 第 5 周 | 投资组合管理模块 | 持仓管理 |
| 第 6 周 | 预警系统开发 | 预警通知 |
| 第 7 周 | 风险指标计算 | 风险分析报告 |

### 第三阶段 (4 周)
| 周次 | 任务 | 交付物 |
|------|------|--------|
| 第 8 周 | 回测引擎开发 | 回测框架 |
| 第 9 周 | 绩效评估体系 | 绩效报告 |
| 第 10 周 | 模拟交易模块 | 模拟盘 |
| 第 11 周 | 策略优化与测试 | 策略库 |

---

## 🔐 TuShare Token 配置

在 `.env` 文件中配置：

```bash
# TuShare API Token (需要在 tushare.pro 注册获取)
TUSHARE_TOKEN=your_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/ashare.db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 后端服务配置
BACKEND_URL=http://localhost:8000
```

---

## 📊 核心算法设计

### 资金强度评分算法

```python
def calc_capital_strength(stock_data: StockData) -> float:
    """
    计算资金强度评分 (0-100)
    
    评分因子:
    1. 主力净流入占比 (40%)
    2. 净流入连续性 (30%)
    3. 资金流入加速度 (20%)
    4. 北向资金持股变化 (10%)
    """
    # 主力净流入占比
    main_flow_ratio = stock_data.main_net_amount / stock_data.total_turnover
    
    # 连续性评分 (连续 N 日净流入)
    continuity_score = count_continuous_inflow_days(stock_data, days=5)
    
    # 加速度 (今日净流入 - 昨日净流入) / 昨日
    acceleration = (
        (stock_data.today_net - stock_data.yesterday_net) / 
        stock_data.yesterday_net if stock_data.yesterday_net else 0
    )
    
    # 北向资金变化
    north_flow_change = stock_data.north_share_change
    
    # 综合评分
    score = (
        normalize(main_flow_ratio) * 40 +
        normalize(continuity_score) * 30 +
        normalize(acceleration) * 20 +
        normalize(north_flow_change) * 10
    )
    
    return min(100, max(0, score))
```

### 板块轮动信号

```python
def detect_sector_rotation(sector_data: List[SectorData]) -> List[Signal]:
    """
    检测板块轮动信号
    
    信号条件:
    1. 板块资金流入排名上升
    2. 流入金额环比增长
    3. 板块内多只股票主力净流入
    4. 板块指数突破均线
    """
    signals = []
    
    for sector in sector_data:
        # 资金流入排名变化
        rank_change = sector.prev_rank - sector.curr_rank
        
        # 流入金额环比
        flow_mom = (sector.curr_inflow - sector.prev_inflow) / sector.prev_inflow
        
        # 板块内净流入股票数
        inflow_stocks_count = count_stocks_with_inflow(sector)
        
        # 技术面突破
        is_breakout = check_price_breakout(sector.index_data)
        
        # 综合判断
        if (rank_change > 3 and 
            flow_mom > 0.3 and 
            inflow_stocks_count > sector.total_stocks * 0.6 and
            is_breakout):
            signals.append(Signal(
                sector=sector.name,
                type='BUY',
                strength=calculate_strength(rank_change, flow_mom)
            ))
    
    return signals
```

---

## 📈 预期成果

### 第一阶段完成后
- ✅ 实时追踪 A 股市场资金流向
- ✅ 识别主力资金动向和板块轮动
- ✅ 生成基于资金面的股票推荐
- ✅ 资金强度量化评分系统

### 第二阶段完成后
- ✅ 完整的投资组合管理
- ✅ 实时风险预警
- ✅ 多维度绩效分析

### 第三阶段完成后
- ✅ 策略历史回测验证
- ✅ 模拟交易实时运行
- ✅ 策略参数优化能力

---

## 🚀 下一步行动

1. **获取 TuShare Token**: 访问 https://tushare.pro 注册并获取 API Token
2. **环境搭建**: 安装 Python 依赖和 Node.js 环境
3. **数据接入**: 测试 TuShare 接口连通性
4. **MVP 开发**: 优先实现资金流向看板

---

**文档版本**: v1.0  
**创建日期**: 2026-03-14  
**作者**: AI Assistant
