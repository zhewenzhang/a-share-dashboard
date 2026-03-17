from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import tushare as ts
import pandas as pd
import os
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

app = FastAPI(title="A 股资金追踪系统 API", version="3.0.6")

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
from app.services.data_cache import data_cache
from app.core.scheduler import data_scheduler

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("🚀 正在启动 A 股资金追踪系统...")
    
    # 启动定时任务调度器
    data_scheduler.start()
    
    # 预加载数据
    try:
        print("📊 正在预加载数据...")
        data_cache.get_indices(force_update=True)
        data_cache.get_sectors(force_update=True)
        data_cache.get_recommendations(force_update=True)
        print("✅ 数据预加载完成")
    except Exception as e:
        print(f"⚠️ 数据预加载失败：{e}")
    
    print("✅ 系统启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("🛑 正在关闭系统...")
    data_scheduler.stop()
    print("✅ 系统已关闭")


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
    cache_status = data_cache.get_cache_status()
    return ApiHealth(
        status="ok",
        version="3.0.6",
        tushare_configured=bool(tushare_token),
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/indices")
async def get_indices(force_update: bool = Query(False, description="强制更新数据")):
    """
    获取主要指数数据
    优先从缓存读取，支持强制更新
    """
    try:
        data = data_cache.get_indices(force_update=force_update)
        return {
            "data": data,
            "success": True,
            "source": "tushare" if tushare_service.is_available() else "mock",
            "cached": not force_update
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "error": str(e)
        }


@app.get("/api/sectors/flow")
async def get_sectors_flow(force_update: bool = Query(False, description="强制更新数据")):
    """
    获取板块资金流向
    优先从缓存读取
    """
    try:
        data = data_cache.get_sectors(force_update=force_update)
        return {
            "data": data,
            "success": True,
            "source": "tushare" if tushare_service.is_available() else "mock",
            "cached": not force_update
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "error": str(e)
        }


@app.get("/api/recommendations")
async def get_recommendations(
    top_n: int = Query(20, description="返回股票数量"),
    force_update: bool = Query(False, description="强制更新数据")
):
    """
    获取资金强度推荐
    优先从缓存读取
    """
    try:
        data = data_cache.get_recommendations(top_n=top_n, force_update=force_update)
        return {
            "data": data,
            "success": True,
            "source": "tushare" if tushare_service.is_available() else "mock",
            "cached": not force_update
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "error": str(e)
        }


@app.get("/api/cache/status")
async def get_cache_status():
    """获取缓存状态"""
    return {
        "data": data_cache.get_cache_status(),
        "success": True
    }


@app.post("/api/cache/clear")
async def clear_cache(data_type: Optional[str] = Query(None, description="数据类型，为空则清除所有")):
    """清除缓存"""
    data_cache.clear_cache(data_type)
    return {
        "success": True,
        "message": f"已清除 {data_type or '所有'} 缓存"
    }


@app.post("/api/cache/update")
async def force_update_cache(
    data_type: str = Query(..., description="数据类型：indices, sectors, stocks")
):
    """强制更新缓存"""
    try:
        if data_type == "indices":
            data = data_cache.get_indices(force_update=True)
        elif data_type == "sectors":
            data = data_cache.get_sectors(force_update=True)
        elif data_type == "stocks":
            data = data_cache.get_recommendations(force_update=True)
        else:
            raise HTTPException(status_code=400, detail=f"未知的数据类型：{data_type}")
        
        return {
            "success": True,
            "data": data,
            "message": f"{data_type} 数据已更新"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from app.services.industry_service import industry_service


# 以下保留原有的其他 API 端点实现...

@app.get("/api/industry/flow")
async def get_industry_flow(force_update: bool = Query(False, description="强制更新数据")):
    """
    获取行业资金流向排行
    展示资金流入/流出最多的行业
    """
    try:
        data = industry_service.get_industry_flow(force_update=force_update)
        return {
            "data": data,
            "success": True,
            "source": "tushare" if tushare_service.is_available() else "mock",
            "cached": not force_update,
            "count": len(data)
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "error": str(e)
        }


@app.get("/api/industry/{industry_code}/stocks")
async def get_industry_stocks(industry_code: str, top_n: int = Query(10, description="返回股票数量")):
    """
    获取行业内的股票资金流向排行
    """
    try:
        # 这里可以实现获取行业成分股的逻辑
        # 简化处理，返回模拟数据
        stocks = [
            {"ts_code": "688981.SH", "name": "中芯国际", "price": 52.38, "change_pct": 4.56, "net_amount": 450000000, "rank": 1},
            {"ts_code": "000938.SZ", "name": "中芯国际", "price": 28.92, "change_pct": 2.34, "net_amount": 280000000, "rank": 2},
            {"ts_code": "600584.SH", "name": "长电科技", "price": 32.15, "change_pct": 3.21, "net_amount": 180000000, "rank": 3}
        ][:top_n]
        
        return {
            "data": stocks,
            "success": True,
            "industry_code": industry_code
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "error": str(e)
        }


# 以下保留原有的其他 API 端点实现...

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
