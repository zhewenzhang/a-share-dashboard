import tushare as ts
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from app.core.config import settings


class TuShareService:
    """TuShare 数据服务"""
    
    def __init__(self):
        self.api = None
        self.token = settings.tushare_token
        self._init_api()
    
    def _init_api(self):
        """初始化 TuShare API"""
        if self.token and self.token != "your_token_here":
            ts.set_token(self.token)
            self.api = ts.pro_api()
    
    def is_available(self) -> bool:
        """检查 API 是否可用"""
        return self.api is not None
    
    def get_moneyflow(self, ts_code: str, trade_date: Optional[str] = None) -> Optional[Dict]:
        """
        获取个股资金流向
        
        Args:
            ts_code: 股票代码，如 '000001.SZ'
            trade_date: 交易日期，如 '20240114'，默认昨天
            
        Returns:
            资金流向数据
        """
        if not self.is_available():
            return None
        
        try:
            if trade_date is None:
                # 默认获取最近交易日
                trade_date = self._get_last_trade_date()
            
            df = self.api.moneyflow(ts_code=ts_code, trade_date=trade_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')[0]
            return None
        except Exception as e:
            print(f"获取资金流向失败：{e}")
            return None
    
    def get_moneyflow_history(self, ts_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        获取个股历史资金流向
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            历史资金流向列表
        """
        if not self.is_available():
            return None
        
        try:
            df = self.api.moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取历史资金流向失败：{e}")
            return None
    
    def get_stock_basic(self) -> Optional[List[Dict]]:
        """
        获取股票基本信息
        
        Returns:
            股票列表
        """
        if not self.is_available():
            return None
        
        try:
            df = self.api.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
            if df is not None:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取股票列表失败：{e}")
            return None
    
    def get_daily(self, ts_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        获取日线行情
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            日线数据
        """
        if not self.is_available():
            return None
        
        try:
            df = self.api.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取日线数据失败：{e}")
            return None
    
    def get_index_basic(self) -> Optional[List[Dict]]:
        """获取指数基本信息"""
        if not self.is_available():
            return None
        
        try:
            df = self.api.index_basic()
            if df is not None:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取指数列表失败：{e}")
            return None
    
    def get_index_daily(self, ts_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取指数日线行情"""
        if not self.is_available():
            return None
        
        try:
            df = self.api.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取指数数据失败：{e}")
            return None
    
    def get_north_flow(self, ts_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        获取北向资金持股数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            北向资金持股数据
        """
        if not self.is_available():
            return None
        
        try:
            df = self.api.north_hold(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取北向资金数据失败：{e}")
            return None
    
    def get_top_list(self, trade_date: str) -> Optional[List[Dict]]:
        """
        获取龙虎榜数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            龙虎榜数据
        """
        if not self.is_available():
            return None
        
        try:
            df = self.api.top_list(trade_date=trade_date)
            if df is not None and len(df) > 0:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取龙虎榜数据失败：{e}")
            return None
    
    def get_ind_classify(self) -> Optional[List[Dict]]:
        """获取行业分类"""
        if not self.is_available():
            return None
        
        try:
            df = self.api.index_classify(src='SW2021', level='L1')
            if df is not None:
                return df.to_dict('records')
            return None
        except Exception as e:
            print(f"获取行业分类失败：{e}")
            return None
    
    def _get_last_trade_date(self) -> str:
        """获取最近交易日（简化版，实际应该查询日历）"""
        today = datetime.now()
        # 简单处理：如果是周末，返回周五
        if today.weekday() == 5:  # 周六
            return (today - timedelta(days=1)).strftime('%Y%m%d')
        elif today.weekday() == 6:  # 周日
            return (today - timedelta(days=2)).strftime('%Y%m%d')
        else:
            return today.strftime('%Y%m%d')


# 全局服务实例
tushare_service = TuShareService()
