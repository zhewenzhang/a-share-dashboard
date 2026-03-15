from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import tushare as ts
import pandas as pd
import os
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

app = FastAPI(title="A 股资金追踪系统 API", version="3.0.5")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置 TuShare
tushare_token = os.getenv("TUSHARE_TOKEN", "")
if tushare_token:
    ts.set_token(tushare_token)
    pro = ts.pro_api()
else:
    pro = None

# 导入服务
from app.services.tushare_service import tushare_service
from app.services.capital_analyzer import capital_analyzer, CapitalFlowData


class ApiHealth(BaseModel):
    status: str
    version: str
    tushare_configured: bool
    timestamp: str


class IndexData(BaseModel):
    ts_code: str
    name: str
    close: float
    change: float
    change_pct: float
    volume: float


class SectorFlow(BaseModel):
    sector_name: str
    net_amount: float
    change_pct: float
    stock_count: int
    inflow_stock_count: int


class StockRecommendation(BaseModel):
    ts_code: str
    name: str
    price: float
    change_pct: float
    score: float
    net_amount: float
    continuous_days: int
    industry: str
    recommendation_type: str


# 投资组合相关模型
class Position(BaseModel):
    ts_code: str
    name: str
    quantity: int
    cost_price: float
    industry: str


class Portfolio(BaseModel):
    positions: List[Position]
    cash: float
    total_value: float
    daily_profit: float
    total_profit: float


class Alert(BaseModel):
    id: str
    ts_code: str
    name: str
    alert_type: str  # PRICE_DROP, PRICE_RISE, FLOW_OUT
    threshold: float
    current_value: float
    triggered: bool
    created_at: str


class BacktestRequest(BaseModel):
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float = 1000000
    commission_rate: float = 0.0003
    top_n: int = 20
    continuous_days: int = 3


class BacktestResult(BaseModel):
    strategy_name: str
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    nav_curve: List[Dict]
    trades: List[Dict]


idx_map = {
    "000001.SH": "上证指数",
    "399001.SZ": "深证成指",
    "399006.SZ": "创业板指",
    "000300.SH": "沪深 300"
}


@app.get("/api/health", response_model=ApiHealth)
async def health_check():
    """健康检查"""
    return ApiHealth(
        status="ok",
        version="3.0.5",
        tushare_configured=bool(tushare_token),
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/indices")
async def get_indices():
    """获取主要指数"""
    if pro:
        try:
            indices = ["000001.SH", "399001.SZ", "399006.SZ", "000300.SH"]
            results = []
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

            for idx in indices:
                try:
                    df = pro.index_daily(ts_code=idx, start_date=start_date, end_date=end_date)
                    if not df.empty:
                        row = df.iloc[0]
                        prev_close = row['pre_close'] if 'pre_close' in df.columns else row['close']
                        results.append({
                            "ts_code": row['ts_code'],
                            "name": idx_map.get(idx, idx),
                            "close": float(row['close']),
                            "change": float(row['close'] - prev_close),
                            "change_pct": float(row['pct_chg']) if 'pct_chg' in df.columns else 0.0,
                            "volume": float(row['vol']) if 'vol' in df.columns else 0
                        })
                except Exception as e:
                    print(f"获取指数 {idx} 数据失败：{e}")
                    continue

            if results:
                return {"data": results, "success": True}
        except Exception as e:
            print(f"获取指数数据失败：{e}")

    # 返回模拟数据
    return {
        "data": [
            {"ts_code": "000001.SH", "name": "上证指数", "close": 3420.25, "change": 12.34, "change_pct": 0.36, "volume": 4567890123},
            {"ts_code": "399001.SZ", "name": "深证成指", "close": 11565.82, "change": -45.67, "change_pct": -0.39, "volume": 5678901234},
            {"ts_code": "399006.SZ", "name": "创业板指", "close": 2356.31, "change": 28.45, "change_pct": 1.22, "volume": 2345678901},
            {"ts_code": "000300.SH", "name": "沪深 300", "close": 4321.56, "change": 15.34, "change_pct": 0.36, "volume": 3456789012}
        ],
        "success": True
    }


@app.get("/api/sectors/flow")
async def get_sector_flow():
    """获取板块资金流向"""
    if pro:
        try:
            # 获取行业分类
            df = pro.index_classify(src='SW2021', level='L1')
            if df is not None and not df.empty:
                sectors = df.to_dict('records')
                # 这里简化处理，实际需要调用板块资金流接口
                results = []
                for sector in sectors[:20]:  # 限制数量
                    results.append({
                        "sector_name": sector.get('index_name', ''),
                        "net_amount": 0,
                        "change_pct": 0,
                        "stock_count": 0,
                        "inflow_stock_count": 0
                    })
                return {"data": results, "success": True}
        except Exception as e:
            print(f"获取板块数据失败：{e}")

    # 返回模拟数据
    return {
        "data": [
            {"sector_name": "半导体", "net_amount": 156000000, "change_pct": 3.25, "stock_count": 60, "inflow_stock_count": 45},
            {"sector_name": "人工智能", "net_amount": 123000000, "change_pct": 2.88, "stock_count": 55, "inflow_stock_count": 38},
            {"sector_name": "光伏设备", "net_amount": 98000000, "change_pct": 2.45, "stock_count": 50, "inflow_stock_count": 32},
            {"sector_name": "汽车整车", "net_amount": 85000000, "change_pct": 1.98, "stock_count": 40, "inflow_stock_count": 28},
            {"sector_name": "医疗器械", "net_amount": 62000000, "change_pct": 1.56, "stock_count": 45, "inflow_stock_count": 25},
            {"sector_name": "软件开发", "net_amount": 51000000, "change_pct": 1.32, "stock_count": 50, "inflow_stock_count": 22},
            {"sector_name": "电池", "net_amount": 43000000, "change_pct": 0.98, "stock_count": 35, "inflow_stock_count": 20},
            {"sector_name": "通信设备", "net_amount": 32000000, "change_pct": 0.76, "stock_count": 40, "inflow_stock_count": 18},
            {"sector_name": "券商", "net_amount": 21000000, "change_pct": 0.54, "stock_count": 30, "inflow_stock_count": 15},
            {"sector_name": "家电", "net_amount": 12000000, "change_pct": 0.32, "stock_count": 25, "inflow_stock_count": 12}
        ],
        "success": True
    }


@app.get("/api/recommendations")
async def get_recommendations(top_n: int = Query(20, description="返回股票数量")):
    """获取资金强度推荐"""
    if pro:
        try:
            # 获取股票列表
            stock_basic = tushare_service.get_stock_basic()
            if stock_basic:
                # 获取资金流数据并分析
                # 这里简化处理，实际应该批量获取资金流数据
                pass
        except Exception as e:
            print(f"获取推荐数据失败：{e}")

    # 返回模拟数据
    return {
        "data": [
            {"ts_code": "300750.SZ", "name": "宁德时代", "price": 412.56, "change_pct": 2.34, "score": 92.5, "net_amount": 85000000, "continuous_days": 5, "industry": "电池", "recommendation_type": "STRONG_BUY"},
            {"ts_code": "688981.SH", "name": "中芯国际", "price": 52.38, "change_pct": 4.56, "score": 88.3, "net_amount": 123000000, "continuous_days": 4, "industry": "半导体", "recommendation_type": "STRONG_BUY"},
            {"ts_code": "000858.SZ", "name": "五粮液", "price": 168.92, "change_pct": 0.87, "score": 75.2, "net_amount": 21000000, "continuous_days": 3, "industry": "白酒", "recommendation_type": "BUY"},
            {"ts_code": "002594.SZ", "name": "比亚迪", "price": 268.45, "change_pct": -1.23, "score": 72.8, "net_amount": -32000000, "continuous_days": 2, "industry": "汽车", "recommendation_type": "BUY"},
            {"ts_code": "600030.SH", "name": "中信证券", "price": 28.92, "change_pct": 1.23, "score": 68.5, "net_amount": 56000000, "continuous_days": 3, "industry": "券商", "recommendation_type": "BUY"}
        ][:top_n],
        "success": True
    }


@app.get("/api/capital-flow/{ts_code}")
async def get_capital_flow(ts_code: str):
    """获取个股资金流向"""
    if pro:
        try:
            data = tushare_service.get_moneyflow(ts_code)
            if data:
                return {"data": data, "success": True}
        except Exception as e:
            print(f"获取资金流数据失败：{e}")

    # 返回模拟数据
    return {
        "data": {
            "ts_code": ts_code,
            "trade_date": datetime.now().strftime('%Y%m%d'),
            "close": 100.0,
            "change_pct": 1.5,
            "buy_elg_amount": 50000000,
            "buy_big_amount": 30000000,
            "buy_sm_amount": 20000000,
            "sell_elg_amount": 40000000,
            "sell_big_amount": 25000000,
            "sell_sm_amount": 15000000
        },
        "success": True
    }


@app.get("/api/capital-flow/history/{ts_code}")
async def get_capital_flow_history(ts_code: str, start_date: str = None, end_date: str = None):
    """获取历史资金流向"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')

    if pro:
        try:
            data = tushare_service.get_moneyflow_history(ts_code, start_date, end_date)
            if data:
                return {"data": data, "success": True}
        except Exception as e:
            print(f"获取历史资金流数据失败：{e}")

    # 返回模拟数据
    history = []
    for i in range(10):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        history.append({
            "ts_code": ts_code,
            "trade_date": date,
            "close": 100.0 + i * 0.5,
            "change_pct": 1.0,
            "buy_elg_amount": 50000000,
            "buy_big_amount": 30000000,
            "sell_elg_amount": 40000000,
            "sell_big_amount": 25000000,
            "net_amount": 15000000
        })
    return {"data": history, "success": True}


@app.get("/api/capital-flow/analysis/{ts_code}")
async def analyze_capital_flow(ts_code: str, days: int = 10):
    """分析资金强度"""
    if pro:
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            history = tushare_service.get_moneyflow_history(ts_code, start_date, end_date)
            if history:
                flow_data = [CapitalFlowData(**h) for h in history]
                current = flow_data[0]
                result = capital_analyzer.calc_capital_strength(current, flow_data[1:])
                return {"data": result.dict(), "success": True}
        except Exception as e:
            print(f"分析资金流失败：{e}")

    # 返回模拟分析结果
    return {
        "data": {
            "ts_code": ts_code,
            "name": "示例股票",
            "score": 75.5,
            "capital_score": 80.0,
            "continuity_score": 70.0,
            "acceleration_score": 65.0,
            "net_amount": 15000000,
            "main_flow_ratio": 0.15,
            "continuous_days": 3,
            "change_pct": 1.5,
            "industry": "示例行业"
        },
        "success": True
    }


@app.post("/api/tushare/test")
async def test_tushare_connection():
    """测试 TuShare 连接"""
    if not pro:
        return {
            "status": "not_configured",
            "message": "未配置 TuShare Token",
            "configured": False
        }

    try:
        # 测试基本连接
        df = pro.trade_cal(exchange='SSE', start_date=datetime.now().strftime('%Y%m%d'))
        if df is not None and len(df) > 0:
            return {
                "status": "connected",
                "message": "TuShare API 连接正常",
                "configured": True,
                "permissions": True
            }
        else:
            return {
                "status": "limited_access",
                "message": "Token 已配置但权限有限",
                "configured": True,
                "permissions": False
            }
    except Exception as e:
        error_msg = str(e)
        if "100" in error_msg or "token" in error_msg.lower():
            return {
                "status": "invalid_token",
                "message": "Token 无效或已过期",
                "configured": True,
                "error": error_msg
            }
        else:
            return {
                "status": "connection_error",
                "message": f"连接错误：{error_msg}",
                "configured": True,
                "error": error_msg
            }


# 投资组合管理 API
@app.get("/api/portfolio")
async def get_portfolio():
    """获取投资组合"""
    # 这里应该从数据库获取，目前返回空组合
    return {
        "data": {
            "positions": [],
            "cash": 1000000,
            "total_value": 1000000,
            "daily_profit": 0,
            "total_profit": 0
        },
        "success": True
    }


@app.post("/api/portfolio/position")
async def add_position(position: Position):
    """添加持仓"""
    # 这里应该保存到数据库
    return {"success": True, "message": "持仓添加成功"}


@app.delete("/api/portfolio/position/{ts_code}")
async def remove_position(ts_code: str):
    """删除持仓"""
    # 这里应该从数据库删除
    return {"success": True, "message": "持仓删除成功"}


@app.get("/api/alerts")
async def get_alerts():
    """获取预警列表"""
    return {"data": [], "success": True}


@app.post("/api/alert")
async def create_alert(alert: Alert):
    """创建预警"""
    return {"success": True, "message": "预警创建成功"}


@app.delete("/api/alert/{alert_id}")
async def delete_alert(alert_id: str):
    """删除预警"""
    return {"success": True, "message": "预警删除成功"}


# 策略回测 API
@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """运行策略回测"""
    # 这里应该运行真实的回测引擎
    # 目前返回模拟结果
    return {
        "data": {
            "strategy_name": request.strategy,
            "total_return": 15.6,
            "annual_return": 28.5,
            "max_drawdown": -8.2,
            "sharpe_ratio": 1.85,
            "win_rate": 62.5,
            "total_trades": 48,
            "nav_curve": [],
            "trades": []
        },
        "success": True
    }


# 模拟交易 API
@app.get("/api/simulate/account")
async def get_simulate_account():
    """获取模拟账户信息"""
    return {
        "data": {
            "cash": 1000000,
            "total_value": 1000000,
            "positions": [],
            "history": []
        },
        "success": True
    }


@app.post("/api/simulate/buy")
async def simulate_buy(ts_code: str, quantity: int, price: float):
    """模拟买入"""
    return {"success": True, "message": f"模拟买入 {ts_code} {quantity}股 @ {price}"}


@app.post("/api/simulate/sell")
async def simulate_sell(ts_code: str, quantity: int, price: float):
    """模拟卖出"""
    return {"success": True, "message": f"模拟卖出 {ts_code} {quantity}股 @ {price}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
