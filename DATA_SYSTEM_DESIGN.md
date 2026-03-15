# 📊 数据缓存与自动更新系统设计

## 🎯 设计目标

解决 TuShare API 的频率限制问题，实现：
1. **降低 API 调用频率** - 避免触发 TuShare 限制
2. **提高响应速度** - 优先从缓存读取数据
3. **自动数据更新** - 定时任务自动抓取最新数据
4. **数据持久化** - SQLite 存储历史数据

---

## 📈 TuShare API 限制分析

### 免费用户限制
| 限制类型 | 说明 |
|---------|------|
| **调用频率** | 每分钟 60 次 |
| **积分系统** | 需要积分才能调用高级接口 |
| **并发限制** | 单账户同时只能有一个连接 |
| **数据延迟** | 部分数据有 15 分钟延迟 |

### 高频抓取的问题
- ❌ 容易触发频率限制
- ❌ 积分消耗过快
- ❌ API 被封禁风险
- ❌ 响应速度慢

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端页面                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   指数卡片    │  │   板块列表    │  │   股票推荐    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP 请求
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 后端                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DataCacheService 缓存服务                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  指数缓存 │  │  板块缓存 │  │  股票缓存 │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐         │
│  │  SQLite  │      │  SQLite  │      │  SQLite  │         │
│  │ 指数数据 │      │ 板块数据 │      │ 股票数据 │         │
│  └──────────┘      └──────────┘      └──────────┘         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           APScheduler 定时任务调度器                 │  │
│  │  • 指数更新: 每 5 分钟                              │  │
│  │  • 板块更新: 每 15 分钟                             │  │
│  │  • 股票更新: 每 30 分钟                             │  │
│  │  • 资金更新: 每 10 分钟                             │  │
│  └────────────────────────┬────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              TuShare Pro API                        │  │
│  │         (受频率限制保护)                             │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 数据模型设计

### 1. 指数数据 (IndexData)
```python
class IndexData(Base):
    id: int                    # 主键
    ts_code: str               # 指数代码
    name: str                  # 指数名称
    trade_date: str            # 交易日期
    close: float               # 收盘价
    open: float                # 开盘价
    high: float                # 最高价
    low: float                 # 最低价
    change: float              # 涨跌额
    change_pct: float          # 涨跌幅
    volume: float              # 成交量
    amount: float              # 成交额
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

### 2. 板块资金流向 (SectorFlow)
```python
class SectorFlow(Base):
    id: int
    sector_code: str           # 板块代码
    sector_name: str           # 板块名称
    trade_date: str            # 交易日期
    net_amount: float          # 净流入金额
    change_pct: float          # 涨跌幅
    stock_count: int           # 股票数量
    inflow_stock_count: int    # 净流入股票数
    avg_strength: float        # 平均资金强度
    rank: int                  # 排名
```

### 3. 股票数据 (StockData)
```python
class StockData(Base):
    id: int
    ts_code: str               # 股票代码
    name: str                  # 股票名称
    industry: str              # 所属行业
    trade_date: str            # 交易日期
    close: float               # 收盘价
    change_pct: float          # 涨跌幅
    score: float               # 资金强度评分
    net_amount: float          # 主力净流入
    continuous_days: int       # 连续流入天数
    recommendation_type: str   # 推荐类型
```

### 4. 缓存状态 (DataCacheStatus)
```python
class DataCacheStatus(Base):
    id: int
    data_type: str             # 数据类型
    last_update: datetime      # 最后更新时间
    next_update: datetime      # 下次更新时间
    update_interval: int       # 更新间隔（分钟）
    record_count: int          # 记录数量
    status: str                # 状态
    error_message: str         # 错误信息
```

---

## ⏰ 定时任务配置

### 更新频率策略

| 数据类型 | 更新频率 | 说明 |
|---------|---------|------|
| **指数数据** | 每 5 分钟 | 变化较快，需要及时更新 |
| **板块数据** | 每 15 分钟 | 相对稳定 |
| **股票数据** | 每 30 分钟 | 计算复杂，降低频率 |
| **资金流向** | 每 10 分钟 | 实时监控需求 |
| **缓存清理** | 每天凌晨 2 点 | 清理 7 天前数据 |

### 代码实现
```python
class DataScheduler:
    UPDATE_INTERVALS = {
        'indices': 5,        # 5 分钟
        'sectors': 15,       # 15 分钟
        'stocks': 30,        # 30 分钟
        'capital_flow': 10   # 10 分钟
    }
    
    def _setup_jobs(self):
        # 指数数据更新
        self.scheduler.add_job(
            func=self._update_indices,
            trigger=IntervalTrigger(minutes=5),
            id='update_indices',
            name='更新指数数据'
        )
        
        # 板块数据更新
        self.scheduler.add_job(
            func=self._update_sectors,
            trigger=IntervalTrigger(minutes=15),
            id='update_sectors',
            name='更新板块数据'
        )
        
        # 股票数据更新
        self.scheduler.add_job(
            func=self._update_stocks,
            trigger=IntervalTrigger(minutes=30),
            id='update_stocks',
            name='更新股票数据'
        )
```

---

## 🔄 数据流流程

### 1. 首次加载流程
```
用户访问首页
    ↓
前端请求 /api/indices
    ↓
后端检查缓存状态
    ↓
缓存不存在 → 从 TuShare 抓取
    ↓
存入 SQLite
    ↓
返回数据给前端
    ↓
渲染页面
```

### 2. 缓存命中流程
```
用户访问首页
    ↓
前端请求 /api/indices
    ↓
后端检查缓存状态
    ↓
缓存有效 → 直接从 SQLite 读取
    ↓
返回数据给前端（< 10ms）
    ↓
渲染页面
```

### 3. 定时更新流程
```
APScheduler 触发
    ↓
调用更新函数
    ↓
从 TuShare 抓取最新数据
    ↓
更新 SQLite 记录
    ↓
更新缓存状态
    ↓
下次请求返回新数据
```

---

## 📊 API 端点设计

### 数据获取端点
```
GET /api/indices?force_update=false
GET /api/sectors/flow?force_update=false
GET /api/recommendations?top_n=20&force_update=false
```

**参数说明：**
- `force_update`: 是否强制从 TuShare 更新（默认 false）
- `top_n`: 返回股票数量

**响应格式：**
```json
{
    "data": [...],
    "success": true,
    "source": "tushare|mock",
    "cached": true|false
}
```

### 缓存管理端点
```
GET    /api/cache/status          # 获取缓存状态
POST   /api/cache/clear           # 清除缓存
POST   /api/cache/update          # 强制更新缓存
```

---

## 🎨 前端数据加载

### 数据状态管理
```javascript
let dataState = {
    indices: [],
    sectors: [],
    recommendations: [],
    loading: {
        indices: false,
        sectors: false,
        recommendations: false
    },
    lastUpdate: null
};
```

### 加载函数
```javascript
async function loadAllData() {
    await Promise.all([
        loadIndices(),
        loadSectors(),
        loadRecommendations()
    ]);
    dataState.lastUpdate = new Date();
    updateLastUpdateTime();
}

async function loadIndices() {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/indices`);
    const result = await response.json();
    if (result.success) {
        dataState.indices = result.data;
        renderIndices(result.data);
    }
}
```

---

## 📈 性能对比

| 指标 | 直接调用 TuShare | 使用缓存系统 |
|------|-----------------|-------------|
| **响应时间** | 500-2000ms | 5-20ms |
| **API 调用次数** | 每次请求都调用 | 每 5-30 分钟调用一次 |
| **并发能力** | 受 TuShare 限制 | 无限制 |
| **数据一致性** | 实时 | 5-30 分钟延迟 |
| **离线可用** | 否 | 是（使用缓存数据）|

---

## 🔒 容错机制

### 1. TuShare 不可用
```python
def get_indices(self, force_update=False):
    if not tushare_service.is_available():
        # 返回缓存数据或模拟数据
        return self._get_indices_from_cache() or self._get_mock_indices()
```

### 2. 网络异常
```python
try:
    data = tushare_service.api.index_daily(...)
except Exception as e:
    # 记录错误，返回缓存数据
    return self._get_indices_from_cache()
```

### 3. 数据更新失败
```python
self._update_cache_status('indices', 'error', str(e))
# 返回上一次成功缓存的数据
```

---

## 🚀 使用说明

### 启动后端服务
```bash
cd /Users/dave/a-share-dashboard/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后会自动：
1. 创建 SQLite 数据库
2. 启动定时任务调度器
3. 预加载数据

### 查看缓存状态
```bash
curl http://localhost:8000/api/cache/status
```

### 强制更新数据
```bash
curl -X POST "http://localhost:8000/api/cache/update?data_type=indices"
```

### 清除缓存
```bash
curl -X POST "http://localhost:8000/api/cache/clear"
```

---

## 📁 文件结构

```
backend/
├── app/
│   ├── db/
│   │   └── models.py          # 数据库模型
│   ├── core/
│   │   └── scheduler.py       # 定时任务
│   ├── services/
│   │   ├── data_cache.py      # 缓存服务
│   │   └── tushare_service.py # TuShare 服务
│   └── main.py                # API 端点
└── data/
    └── ashare.db              # SQLite 数据库
```

---

## 🔮 未来优化

### 1. Redis 缓存层
- 使用 Redis 作为内存缓存
- 进一步提高读取速度
- 支持分布式部署

### 2. WebSocket 实时推送
- 数据更新时主动推送
- 减少轮询请求

### 3. 数据压缩
- 对历史数据进行压缩存储
- 减少磁盘占用

### 4. 智能更新策略
- 根据市场活跃度调整更新频率
- 交易时段高频更新，非交易时段低频更新

---

## 📝 总结

通过引入数据缓存和自动更新系统：
- ✅ **降低 TuShare API 调用频率** 90%+
- ✅ **提高页面加载速度** 10-100 倍
- ✅ **支持离线访问**（使用缓存数据）
- ✅ **自动数据更新**，无需手动刷新
- ✅ **容错机制**，TuShare 不可用时仍可使用

**版本**: v3.0.6  
**更新日期**: 2026-03-15
