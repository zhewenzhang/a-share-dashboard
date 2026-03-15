"""
数据缓存服务
实现数据的缓存、读取和自动更新
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import pandas as pd

from app.db.models import (
    db_manager, IndexData, SectorFlow, StockData, 
    CapitalFlow, DataCacheStatus
)
from app.services.tushare_service import tushare_service


class DataCacheService:
    """数据缓存服务"""
    
    # 更新间隔配置（分钟）
    UPDATE_INTERVALS = {
        'indices': 5,      # 指数数据每 5 分钟
        'sectors': 15,     # 板块数据每 15 分钟
        'stocks': 30,      # 个股数据每 30 分钟
        'capital_flow': 10  # 资金流向每 10 分钟
    }
    
    def __init__(self):
        self.db = db_manager
    
    def _get_session(self) -> Session:
        """获取数据库会话"""
        return self.db.get_session()
    
    def _update_cache_status(self, data_type: str, status: str, 
                            error_message: str = None, record_count: int = None):
        """更新缓存状态"""
        session = self._get_session()
        try:
            cache_status = session.query(DataCacheStatus).filter(
                DataCacheStatus.data_type == data_type
            ).first()
            
            if not cache_status:
                cache_status = DataCacheStatus(
                    data_type=data_type,
                    update_interval=self.UPDATE_INTERVALS.get(data_type, 60)
                )
                session.add(cache_status)
            
            if status == 'success':
                cache_status.last_update = datetime.now()
                cache_status.next_update = datetime.now() + timedelta(
                    minutes=cache_status.update_interval
                )
                if record_count is not None:
                    cache_status.record_count = record_count
            
            cache_status.status = status
            if error_message:
                cache_status.error_message = error_message
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"更新缓存状态失败：{e}")
        finally:
            session.close()
    
    def _is_cache_valid(self, data_type: str) -> bool:
        """检查缓存是否有效"""
        session = self._get_session()
        try:
            cache_status = session.query(DataCacheStatus).filter(
                DataCacheStatus.data_type == data_type
            ).first()
            
            if not cache_status or not cache_status.last_update:
                return False
            
            # 检查是否超过更新间隔
            interval = self.UPDATE_INTERVALS.get(data_type, 60)
            next_update = cache_status.last_update + timedelta(minutes=interval)
            
            return datetime.now() < next_update
        finally:
            session.close()
    
    # ==================== 指数数据 ====================
    
    def get_indices(self, force_update: bool = False) -> List[Dict]:
        """
        获取指数数据
        优先从缓存读取，缓存过期则自动更新
        """
        if not force_update and self._is_cache_valid('indices'):
            return self._get_indices_from_cache()
        
        return self._update_indices_data()
    
    def _get_indices_from_cache(self) -> List[Dict]:
        """从缓存获取指数数据"""
        session = self._get_session()
        try:
            today = datetime.now().strftime('%Y%m%d')
            records = session.query(IndexData).filter(
                IndexData.trade_date == today
            ).all()
            
            return [r.to_dict() for r in records]
        finally:
            session.close()
    
    def _update_indices_data(self) -> List[Dict]:
        """更新指数数据"""
        self._update_cache_status('indices', 'updating')
        
        if not tushare_service.is_available():
            self._update_cache_status('indices', 'error', 'TuShare 未配置')
            return self._get_indices_from_cache() or self._get_mock_indices()
        
        try:
            indices = ["000001.SH", "399001.SZ", "399006.SZ", "000300.SH"]
            idx_map = {
                "000001.SH": "上证指数",
                "399001.SZ": "深证成指",
                "399006.SZ": "创业板指",
                "000300.SH": "沪深 300"
            }
            
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            
            results = []
            session = self._get_session()
            
            for idx in indices:
                try:
                    df = tushare_service.api.index_daily(
                        ts_code=idx, 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    if df is not None and not df.empty:
                        row = df.iloc[0]
                        
                        # 保存到数据库
                        index_data = session.query(IndexData).filter(
                            IndexData.ts_code == idx,
                            IndexData.trade_date == row['trade_date']
                        ).first()
                        
                        if not index_data:
                            index_data = IndexData(
                                ts_code=idx,
                                trade_date=row['trade_date']
                            )
                            session.add(index_data)
                        
                        index_data.name = idx_map.get(idx, idx)
                        index_data.close = float(row['close'])
                        index_data.open = float(row.get('open', 0))
                        index_data.high = float(row.get('high', 0))
                        index_data.low = float(row.get('low', 0))
                        index_data.change = float(row.get('change', 0))
                        index_data.change_pct = float(row.get('pct_chg', 0))
                        index_data.volume = float(row.get('vol', 0))
                        index_data.amount = float(row.get('amount', 0))
                        
                        results.append(index_data.to_dict())
                except Exception as e:
                    print(f"获取指数 {idx} 失败：{e}")
                    continue
            
            session.commit()
            self._update_cache_status('indices', 'success', record_count=len(results))
            return results
            
        except Exception as e:
            self._update_cache_status('indices', 'error', str(e))
            return self._get_indices_from_cache() or self._get_mock_indices()
        finally:
            if 'session' in locals():
                session.close()
    
    def _get_mock_indices(self) -> List[Dict]:
        """获取模拟指数数据"""
        return [
            {"ts_code": "000001.SH", "name": "上证指数", "close": 3420.25, "change": 12.34, "change_pct": 0.36, "volume": 4567890123},
            {"ts_code": "399001.SZ", "name": "深证成指", "close": 11565.82, "change": -45.67, "change_pct": -0.39, "volume": 5678901234},
            {"ts_code": "399006.SZ", "name": "创业板指", "close": 2356.31, "change": 28.45, "change_pct": 1.22, "volume": 2345678901},
            {"ts_code": "000300.SH", "name": "沪深 300", "close": 4321.56, "change": 15.34, "change_pct": 0.36, "volume": 3456789012}
        ]
    
    # ==================== 板块数据 ====================
    
    def get_sectors(self, force_update: bool = False) -> List[Dict]:
        """获取板块资金流向"""
        if not force_update and self._is_cache_valid('sectors'):
            return self._get_sectors_from_cache()
        
        return self._update_sectors_data()
    
    def _get_sectors_from_cache(self) -> List[Dict]:
        """从缓存获取板块数据"""
        session = self._get_session()
        try:
            today = datetime.now().strftime('%Y%m%d')
            records = session.query(SectorFlow).filter(
                SectorFlow.trade_date == today
            ).order_by(desc(SectorFlow.net_amount)).limit(10).all()
            
            return [r.to_dict() for r in records]
        finally:
            session.close()
    
    def _update_sectors_data(self) -> List[Dict]:
        """更新板块数据"""
        self._update_cache_status('sectors', 'updating')
        
        # 由于 TuShare 板块数据需要高级权限，这里使用模拟数据
        # 实际项目中可以接入其他数据源
        mock_sectors = [
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
        ]
        
        self._update_cache_status('sectors', 'success', record_count=len(mock_sectors))
        return mock_sectors
    
    # ==================== 股票推荐数据 ====================
    
    def get_recommendations(self, top_n: int = 20, force_update: bool = False) -> List[Dict]:
        """获取股票推荐"""
        if not force_update and self._is_cache_valid('stocks'):
            return self._get_stocks_from_cache(top_n)
        
        return self._update_stocks_data(top_n)
    
    def _get_stocks_from_cache(self, top_n: int) -> List[Dict]:
        """从缓存获取股票数据"""
        session = self._get_session()
        try:
            today = datetime.now().strftime('%Y%m%d')
            records = session.query(StockData).filter(
                StockData.trade_date == today
            ).order_by(desc(StockData.score)).limit(top_n).all()
            
            return [r.to_dict() for r in records]
        finally:
            session.close()
    
    def _update_stocks_data(self, top_n: int) -> List[Dict]:
        """更新股票数据"""
        self._update_cache_status('stocks', 'updating')
        
        # 模拟推荐数据
        mock_stocks = [
            {"ts_code": "300750.SZ", "name": "宁德时代", "price": 412.56, "change_pct": 2.34, "score": 92.5, "net_amount": 85000000, "continuous_days": 5, "industry": "电池", "recommendation_type": "STRONG_BUY"},
            {"ts_code": "688981.SH", "name": "中芯国际", "price": 52.38, "change_pct": 4.56, "score": 88.3, "net_amount": 123000000, "continuous_days": 4, "industry": "半导体", "recommendation_type": "STRONG_BUY"},
            {"ts_code": "000858.SZ", "name": "五粮液", "price": 168.92, "change_pct": 0.87, "score": 75.2, "net_amount": 21000000, "continuous_days": 3, "industry": "白酒", "recommendation_type": "BUY"},
            {"ts_code": "002594.SZ", "name": "比亚迪", "price": 268.45, "change_pct": -1.23, "score": 72.8, "net_amount": -32000000, "continuous_days": 2, "industry": "汽车", "recommendation_type": "BUY"},
            {"ts_code": "600030.SH", "name": "中信证券", "price": 28.92, "change_pct": 1.23, "score": 68.5, "net_amount": 56000000, "continuous_days": 3, "industry": "券商", "recommendation_type": "BUY"}
        ]
        
        self._update_cache_status('stocks', 'success', record_count=len(mock_stocks))
        return mock_stocks[:top_n]
    
    # ==================== 缓存状态 ====================
    
    def get_cache_status(self) -> Dict[str, Any]:
        """获取所有缓存状态"""
        session = self._get_session()
        try:
            statuses = session.query(DataCacheStatus).all()
            return {
                s.data_type: s.to_dict() for s in statuses
            }
        finally:
            session.close()
    
    def clear_cache(self, data_type: str = None):
        """清除缓存"""
        session = self._get_session()
        try:
            if data_type:
                # 清除特定类型的缓存状态
                cache_status = session.query(DataCacheStatus).filter(
                    DataCacheStatus.data_type == data_type
                ).first()
                if cache_status:
                    cache_status.last_update = None
                    cache_status.status = 'pending'
            else:
                # 清除所有缓存状态
                session.query(DataCacheStatus).update({
                    'last_update': None,
                    'status': 'pending'
                })
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"清除缓存失败：{e}")
        finally:
            session.close()


# 全局缓存服务实例
data_cache = DataCacheService()
