from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.tushare_service import tushare_service
from app.services.capital_analyzer import capital_analyzer, CapitalFlowData

app = FastAPI(
    title="A 股资金追踪系统 API",
    description="基于 TuShare 数据的 A 股资金流向追踪与智能投顾系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== 健康检查 ==============

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "tushare_available": tushare_service.is_available(),
        "timestamp": datetime.now().isoformat()
    }


# ============== 资金流向接口 ==============

@app.get("/api/capital-flow/{ts_code}")
async def get_capital_flow(
    ts_code: str,
    trade_date: Optional[str] = None
):
    """
    获取个股资金流向
    
    - **ts_code**: 股票代码，如 '000001.SZ'
    - **trade_date**: 交易日期，如 '20240114'，默认最近交易日
    """
    if not tushare_service.is_available():
        # 返回模拟数据
        return get_mock_capital_flow(ts_code)
    
    data = tushare_service.get_moneyflow(ts_code, trade_date)
    if data is None:
        raise HTTPException(status_code=404, detail="未找到资金流向数据")
    
    return {"data": data, "success": True}


@app.get("/api/capital-flow/history/{ts_code}")
async def get_capital_flow_history(
    ts_code: str,
    start_date: str = Query(..., description="开始日期，如 20240101"),
    end_date: str = Query(..., description="结束日期，如 20240114")
):
    """获取个股历史资金流向"""
    if not tushare_service.is_available():
        return get_mock_capital_flow_history(ts_code, start_date, end_date)
    
    data = tushare_service.get_moneyflow_history(ts_code, start_date, end_date)
    if data is None:
        raise HTTPException(status_code=404, detail="未找到历史数据")
    
    return {"data": data, "success": True}


@app.get("/api/capital-flow/analysis/{ts_code}")
async def analyze_capital_strength(
    ts_code: str,
    days: int = Query(default=10, description="分析天数")
):
    """
    分析个股资金强度
    
    返回 0-100 的资金强度评分
    """
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    if not tushare_service.is_available():
        mock_data = get_mock_capital_flow_history(ts_code, start_date, end_date)
        if mock_data.get("data"):
            history = [CapitalFlowData(**d) for d in mock_data["data"]]
            current = history[0] if history else None
            if current:
                result = capital_analyzer.calc_capital_strength(
                    current, 
                    history[1:] if len(history) > 1 else []
                )
                result.ts_code = ts_code
                return {"data": result.dict(), "success": True}
    
    # 真实数据
    history_data = tushare_service.get_moneyflow_history(ts_code, start_date, end_date)
    if not history_data:
        raise HTTPException(status_code=404, detail="未找到数据")
    
    flows = [CapitalFlowData(**d) for d in history_data]
    current = flows[0] if flows else None
    if not current:
        raise HTTPException(status_code=404, detail="无当前数据")
    
    result = capital_analyzer.calc_capital_strength(
        current,
        flows[1:] if len(flows) > 1 else []
    )
    result.ts_code = ts_code
    
    return {"data": result.dict(), "success": True}


# ============== 股票列表接口 ==============

@app.get("/api/stocks")
async def get_stock_list():
    """获取股票列表"""
    if not tushare_service.is_available():
        return get_mock_stock_list()
    
    data = tushare_service.get_stock_basic()
    if data is None:
        raise HTTPException(status_code=500, detail="获取股票列表失败")
    
    return {"data": data, "success": True}


# ============== 智能推荐接口 ==============

@app.get("/api/recommendations")
async def get_recommendations(
    top_n: int = Query(default=20, description="推荐数量"),
    industry: Optional[str] = None
):
    """
    获取智能股票推荐
    
    基于资金强度评分生成推荐列表
    """
    if not tushare_service.is_available():
        return get_mock_recommendations(top_n, industry)
    
    # 获取股票列表
    stocks = tushare_service.get_stock_basic()
    if not stocks:
        raise HTTPException(status_code=500, detail="获取股票列表失败")
    
    # 分析资金强度（简化版，实际应该分批处理）
    results = []
    for stock in stocks[:100]:  # 限制数量
        try:
            flow_data = tushare_service.get_moneyflow(stock['ts_code'])
            if flow_data:
                flow = CapitalFlowData(**flow_data)
                result = capital_analyzer.calc_capital_strength(flow)
                result.name = stock.get('name', '')
                result.industry = stock.get('industry', '')
                results.append(result)
        except:
            continue
    
    # 生成推荐
    recommendations = capital_analyzer.generate_recommendations(results, top_n)
    
    return {"data": [r.dict() for r in recommendations], "success": True}


# ============== 板块资金流向 ==============

@app.get("/api/sectors/flow")
async def get_sector_flow():
    """获取板块资金流向排行"""
    if not tushare_service.is_available():
        return get_mock_sector_flow()
    
    return get_mock_sector_flow()  # 简化实现


# ============== 指数行情 ==============

@app.get("/api/indices")
async def get_indices():
    """获取主要指数行情"""
    return get_mock_indices()


# ============== 模拟数据函数 ==============

def get_mock_capital_flow(ts_code: str) -> dict:
    """模拟资金流向数据"""
    import random
    base = random.uniform(1000, 5000)
    return {
        "data": {
            "ts_code": ts_code,
            "trade_date": datetime.now().strftime('%Y%m%d'),
            "close": round(random.uniform(10, 500), 2),
            "change_pct": round(random.uniform(-5, 5), 2),
            "buy_sm_amount": round(base * 0.3, 2),
            "buy_big_amount": round(base * 0.25, 2),
            "buy_elg_amount": round(base * 0.2, 2),
            "sell_sm_amount": round(base * 0.28, 2),
            "sell_big_amount": round(base * 0.22, 2),
            "sell_elg_amount": round(base * 0.18, 2)
        },
        "success": True
    }


def get_mock_capital_flow_history(ts_code: str, start_date: str, end_date: str) -> dict:
    """模拟历史资金流向"""
    import random
    data = []
    # 生成日期范围
    current = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    
    while current <= end:
        if current.weekday() < 5:  # 工作日
            base = random.uniform(1000, 5000)
            data.append({
                "ts_code": ts_code,
                "trade_date": current.strftime('%Y%m%d'),
                "close": round(random.uniform(10, 500), 2),
                "change_pct": round(random.uniform(-5, 5), 2),
                "buy_sm_amount": round(base * 0.3, 2),
                "buy_big_amount": round(base * 0.25, 2),
                "buy_elg_amount": round(base * 0.2, 2),
                "sell_sm_amount": round(base * 0.28, 2),
                "sell_big_amount": round(base * 0.22, 2),
                "sell_elg_amount": round(base * 0.18, 2)
            })
        current += timedelta(days=1)
    
    return {"data": data, "success": True}


def get_mock_stock_list() -> dict:
    """模拟股票列表"""
    return {
        "data": [
            {"ts_code": "000001.SZ", "symbol": "000001", "name": "平安银行", "industry": "银行"},
            {"ts_code": "000002.SZ", "symbol": "000002", "name": "万科 A", "industry": "房地产"},
            {"ts_code": "000858.SZ", "symbol": "000858", "name": "五粮液", "industry": "白酒"},
            {"ts_code": "002594.SZ", "symbol": "002594", "name": "比亚迪", "industry": "汽车"},
            {"ts_code": "300750.SZ", "symbol": "300750", "name": "宁德时代", "industry": "电池"},
            {"ts_code": "600030.SH", "symbol": "600030", "name": "中信证券", "industry": "券商"},
            {"ts_code": "600036.SH", "symbol": "600036", "name": "招商银行", "industry": "银行"},
            {"ts_code": "601012.SH", "symbol": "601012", "name": "隆基绿能", "industry": "光伏"},
            {"ts_code": "688981.SH", "symbol": "688981", "name": "中芯国际", "industry": "半导体"},
        ],
        "success": True
    }


def get_mock_recommendations(top_n: int = 20, industry: str = None) -> dict:
    """模拟推荐列表"""
    import random
    stocks = [
        {"ts_code": "300750.SZ", "name": "宁德时代", "industry": "电池"},
        {"ts_code": "688981.SH", "name": "中芯国际", "industry": "半导体"},
        {"ts_code": "000858.SZ", "name": "五粮液", "industry": "白酒"},
        {"ts_code": "002594.SZ", "name": "比亚迪", "industry": "汽车"},
        {"ts_code": "600030.SH", "name": "中信证券", "industry": "券商"},
        {"ts_code": "601012.SH", "name": "隆基绿能", "industry": "光伏"},
        {"ts_code": "000001.SZ", "name": "平安银行", "industry": "银行"},
        {"ts_code": "600036.SH", "name": "招商银行", "industry": "银行"},
    ]
    
    recommendations = []
    for stock in stocks[:top_n]:
        score = random.uniform(60, 95)
        rec_type = "STRONG_BUY" if score >= 80 else "BUY" if score >= 60 else "WATCH"
        recommendations.append({
            "ts_code": stock["ts_code"],
            "name": stock["name"],
            "score": round(score, 2),
            "reason": "资金强度良好，主力持续流入",
            "industry": stock["industry"],
            "price": round(random.uniform(20, 500), 2),
            "change_pct": round(random.uniform(-3, 5), 2),
            "net_amount": round(random.uniform(1000, 10000), 2),
            "continuous_days": random.randint(1, 7),
            "recommendation_type": rec_type
        })
    
    return {"data": recommendations, "success": True}


def get_mock_sector_flow() -> dict:
    """模拟板块资金流向"""
    sectors = [
        {"sector_name": "半导体", "net_amount": 15600, "inflow_stock_count": 45, "stock_count": 60, "avg_strength": 0.35},
        {"sector_name": "人工智能", "net_amount": 12300, "inflow_stock_count": 38, "stock_count": 55, "avg_strength": 0.28},
        {"sector_name": "光伏设备", "net_amount": 9800, "inflow_stock_count": 32, "stock_count": 50, "avg_strength": 0.22},
        {"sector_name": "汽车整车", "net_amount": 8500, "inflow_stock_count": 28, "stock_count": 40, "avg_strength": 0.19},
        {"sector_name": "医疗器械", "net_amount": 6200, "inflow_stock_count": 25, "stock_count": 45, "avg_strength": 0.15},
        {"sector_name": "软件开发", "net_amount": 5100, "inflow_stock_count": 22, "stock_count": 50, "avg_strength": 0.12},
        {"sector_name": "电池", "net_amount": 4300, "inflow_stock_count": 20, "stock_count": 35, "avg_strength": 0.10},
        {"sector_name": "通信设备", "net_amount": 3200, "inflow_stock_count": 18, "stock_count": 40, "avg_strength": 0.08},
        {"sector_name": "券商", "net_amount": 2100, "inflow_stock_count": 15, "stock_count": 30, "avg_strength": 0.05},
        {"sector_name": "家电", "net_amount": 1200, "inflow_stock_count": 12, "stock_count": 25, "avg_strength": 0.03},
    ]
    
    for i, s in enumerate(sectors):
        s["rank"] = i + 1
        s["rank_change"] = 0
        s["sector_code"] = ""
        s["change_pct"] = round(random.uniform(0.5, 3.5), 2)
    
    return {"data": sectors, "success": True}


def get_mock_indices() -> dict:
    """模拟指数数据"""
    import random
    indices = [
        {"name": "上证指数", "code": "000001.SH", "point": 3420.25, "change": 1.23, "change_pct": 0.04},
        {"name": "深证成指", "code": "399001.SZ", "point": 11565.82, "change": -45.67, "change_pct": -0.39},
        {"name": "创业板指", "code": "399006.SZ", "point": 2356.31, "change": 28.45, "change_pct": 1.22},
        {"name": "沪深 300", "code": "000300.SH", "point": 4321.56, "change": 12.34, "change_pct": 0.29},
    ]
    
    for idx in indices:
        # 添加一些随机波动
        idx["point"] = round(idx["point"] + random.uniform(-50, 50), 2)
        idx["change"] = round(idx["change"] + random.uniform(-20, 20), 2)
        idx["change_pct"] = round(idx["change_pct"] + random.uniform(-0.1, 0.1), 2)
    
    return {"data": indices, "success": True}


# 挂载静态文件目录（用于前端）
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend', 'dist')
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
