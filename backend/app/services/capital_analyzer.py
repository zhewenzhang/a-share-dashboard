from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel


class CapitalFlowData(BaseModel):
    """资金流向数据模型"""
    ts_code: str
    trade_date: str
    close: float = 0.0           # 收盘价
    change_pct: float = 0.0      # 涨跌幅
    buy_sm_amount: float = 0.0   # 小单买入金额
    buy_big_amount: float = 0.0  # 大单买入金额
    buy_elg_amount: float = 0.0  # 特大单买入金额
    sell_sm_amount: float = 0.0  # 小单卖出金额
    sell_big_amount: float = 0.0 # 大单卖出金额
    sell_elg_amount: float = 0.0 # 特大单卖出金额
    
    @property
    def net_amount(self) -> float:
        """净流入金额"""
        return (self.buy_elg_amount + self.buy_big_amount) - (self.sell_elg_amount + self.sell_big_amount)
    
    @property
    def net_amount_all(self) -> float:
        """全部净流入（含小单）"""
        return (self.buy_elg_amount + self.buy_big_amount + self.buy_sm_amount) - \
               (self.sell_elg_amount + self.sell_big_amount + self.sell_sm_amount)
    
    @property
    def total_turnover(self) -> float:
        """总成交额"""
        return (self.buy_elg_amount + self.buy_big_amount + self.buy_sm_amount + 
                self.sell_elg_amount + self.sell_big_amount + self.sell_sm_amount)
    
    @property
    def main_flow_ratio(self) -> float:
        """主力净流入占比"""
        if self.total_turnover == 0:
            return 0.0
        return self.net_amount / self.total_turnover
    
    @property
    def is_main_inflow(self) -> bool:
        """是否主力净流入"""
        return self.net_amount > 0


class CapitalStrengthResult(BaseModel):
    """资金强度评分结果"""
    ts_code: str
    name: str
    score: float                  # 综合评分 0-100
    capital_score: float          # 资金面评分
    continuity_score: float       # 连续性评分
    acceleration_score: float     # 加速度评分
    net_amount: float             # 净流入金额
    main_flow_ratio: float        # 主力净流入占比
    continuous_days: int          # 连续净流入天数
    change_pct: float             # 涨跌幅
    industry: str = ""            # 所属行业


class StockRecommendation(BaseModel):
    """股票推荐"""
    ts_code: str
    name: str
    score: float
    reason: str
    industry: str
    price: float
    change_pct: float
    net_amount: float
    continuous_days: int
    recommendation_type: str      # STRONG_BUY / BUY / WATCH


class SectorFlow(BaseModel):
    """板块资金流向"""
    sector_name: str
    sector_code: str
    net_amount: float
    change_pct: float
    stock_count: int
    inflow_stock_count: int     # 净流入股票数
    avg_strength: float          # 平均资金强度
    rank: int                    # 排名
    rank_change: int             # 排名变化


class CapitalAnalyzer:
    """资金分析引擎"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    def calc_capital_strength(
        self, 
        current: CapitalFlowData, 
        history: Optional[List[CapitalFlowData]] = None,
        north_flow_change: float = 0.0
    ) -> CapitalStrengthResult:
        """
        计算资金强度评分
        
        评分因子:
        1. 主力净流入占比 (40%)
        2. 净流入连续性 (30%)
        3. 资金流入加速度 (20%)
        4. 北向资金持股变化 (10%)
        """
        # 1. 主力净流入占比评分 (0-100)
        main_flow_ratio = current.main_flow_ratio
        capital_score = min(100, max(0, (main_flow_ratio + 0.3) * 100))  # 30% 以上为满分
        
        # 2. 连续性评分
        continuous_days = 0
        if history:
            for data in history:
                if data.is_main_inflow:
                    continuous_days += 1
                else:
                    break
        continuity_score = min(100, continuous_days * 20)  # 连续 5 天满分
        
        # 3. 加速度评分
        acceleration_score = 50  # 默认中等
        if history and len(history) >= 2:
            prev_net = history[0].net_amount if history else 0
            curr_net = current.net_amount
            if prev_net > 0:
                acceleration = (curr_net - prev_net) / abs(prev_net)
                acceleration_score = min(100, max(0, (acceleration + 1) * 50))
        
        # 4. 北向资金变化评分
        north_score = min(100, max(0, (north_flow_change + 0.5) * 100))  # 0.5% 以上满分
        
        # 综合评分
        total_score = (
            capital_score * 0.4 +
            continuity_score * 0.3 +
            acceleration_score * 0.2 +
            north_score * 0.1
        )
        
        return CapitalStrengthResult(
            ts_code=current.ts_code,
            name="",
            score=round(total_score, 2),
            capital_score=round(capital_score, 2),
            continuity_score=round(continuity_score, 2),
            acceleration_score=round(acceleration_score, 2),
            net_amount=current.net_amount,
            main_flow_ratio=round(main_flow_ratio, 4),
            continuous_days=continuous_days,
            change_pct=current.change_pct,
            industry=""
        )
    
    def analyze_stocks(
        self, 
        stock_data: List[Dict],
        history_data: Dict[str, List[CapitalFlowData]] = None
    ) -> List[CapitalStrengthResult]:
        """批量分析股票资金强度"""
        results = []
        
        for data in stock_data:
            try:
                flow = CapitalFlowData(**data)
                history = history_data.get(flow.ts_code, []) if history_data else []
                
                result = self.calc_capital_strength(flow, history)
                results.append(result)
            except Exception as e:
                print(f"分析股票失败 {data.get('ts_code')}: {e}")
                continue
        
        # 按评分排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def generate_recommendations(
        self, 
        results: List[CapitalStrengthResult],
        top_n: int = 20
    ) -> List[StockRecommendation]:
        """生成股票推荐"""
        recommendations = []
        
        for result in results[:top_n]:
            # 确定推荐类型
            if result.score >= 80:
                rec_type = "STRONG_BUY"
                reason = "资金强度极高，连续主力净流入"
            elif result.score >= 60:
                rec_type = "BUY"
                reason = "资金强度良好，主力持续流入"
            elif result.score >= 40:
                rec_type = "WATCH"
                reason = "资金面中性，持续观察"
            else:
                continue  # 不推荐低分股票
            
            recommendations.append(StockRecommendation(
                ts_code=result.ts_code,
                name=result.name,
                score=result.score,
                reason=reason,
                industry=result.industry,
                price=0.0,
                change_pct=result.change_pct,
                net_amount=result.net_amount,
                continuous_days=result.continuous_days,
                recommendation_type=rec_type
            ))
        
        return recommendations
    
    def analyze_sectors(
        self,
        sector_stocks: Dict[str, List[CapitalFlowData]]
    ) -> List[SectorFlow]:
        """分析板块资金流向"""
        sector_results = []
        
        for sector_name, stocks in sector_stocks.items():
            if not stocks:
                continue
            
            total_net = sum(s.net_amount for s in stocks)
            inflow_count = sum(1 for s in stocks if s.is_main_inflow)
            avg_strength = sum(s.main_flow_ratio for s in stocks) / len(stocks)
            
            sector_results.append(SectorFlow(
                sector_name=sector_name,
                sector_code="",
                net_amount=total_net,
                change_pct=0.0,
                stock_count=len(stocks),
                inflow_stock_count=inflow_count,
                avg_strength=round(avg_strength, 4),
                rank=0,
                rank_change=0
            ))
        
        # 按净流入排序
        sector_results.sort(key=lambda x: x.net_amount, reverse=True)
        
        # 设置排名
        for i, sector in enumerate(sector_results):
            sector.rank = i + 1
        
        return sector_results


# 全局分析器实例
capital_analyzer = CapitalAnalyzer()
