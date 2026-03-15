"""
数据缓存模型
使用 SQLAlchemy 定义数据表结构
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

Base = declarative_base()

class IndexData(Base):
    """指数数据缓存"""
    __tablename__ = 'index_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, index=True)
    name = Column(String(50))
    trade_date = Column(String(8), nullable=False, index=True)
    close = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    change = Column(Float)
    change_pct = Column(Float)
    volume = Column(Float)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_index_ts_date', 'ts_code', 'trade_date', unique=True),
    )
    
    def to_dict(self) -> Dict:
        return {
            'ts_code': self.ts_code,
            'name': self.name,
            'trade_date': self.trade_date,
            'close': self.close,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'change': self.change,
            'change_pct': self.change_pct,
            'volume': self.volume,
            'amount': self.amount
        }


class SectorFlow(Base):
    """板块资金流向缓存"""
    __tablename__ = 'sector_flow'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sector_code = Column(String(20), nullable=False, index=True)
    sector_name = Column(String(50))
    trade_date = Column(String(8), nullable=False, index=True)
    net_amount = Column(Float)  # 净流入金额
    change_pct = Column(Float)  # 涨跌幅
    stock_count = Column(Integer)  # 股票数量
    inflow_stock_count = Column(Integer)  # 净流入股票数
    avg_strength = Column(Float)  # 平均资金强度
    rank = Column(Integer)  # 排名
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_sector_code_date', 'sector_code', 'trade_date', unique=True),
    )
    
    def to_dict(self) -> Dict:
        return {
            'sector_code': self.sector_code,
            'sector_name': self.sector_name,
            'trade_date': self.trade_date,
            'net_amount': self.net_amount,
            'change_pct': self.change_pct,
            'stock_count': self.stock_count,
            'inflow_stock_count': self.inflow_stock_count,
            'avg_strength': self.avg_strength,
            'rank': self.rank
        }


class StockData(Base):
    """个股数据缓存"""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, index=True)
    name = Column(String(50))
    industry = Column(String(50))
    trade_date = Column(String(8), nullable=False, index=True)
    close = Column(Float)
    change_pct = Column(Float)
    score = Column(Float)  # 资金强度评分
    net_amount = Column(Float)  # 主力净流入
    continuous_days = Column(Integer)  # 连续流入天数
    recommendation_type = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_stock_ts_date', 'ts_code', 'trade_date', unique=True),
        Index('idx_stock_score', 'score'),
    )
    
    def to_dict(self) -> Dict:
        return {
            'ts_code': self.ts_code,
            'name': self.name,
            'industry': self.industry,
            'trade_date': self.trade_date,
            'close': self.close,
            'change_pct': self.change_pct,
            'score': self.score,
            'net_amount': self.net_amount,
            'continuous_days': self.continuous_days,
            'recommendation_type': self.recommendation_type
        }


class CapitalFlow(Base):
    """个股资金流向缓存"""
    __tablename__ = 'capital_flow'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, index=True)
    trade_date = Column(String(8), nullable=False, index=True)
    close = Column(Float)
    change_pct = Column(Float)
    buy_sm_amount = Column(Float)  # 小单买入
    buy_big_amount = Column(Float)  # 大单买入
    buy_elg_amount = Column(Float)  # 特大单买入
    sell_sm_amount = Column(Float)  # 小单卖出
    sell_big_amount = Column(Float)  # 大单卖出
    sell_elg_amount = Column(Float)  # 特大单卖出
    net_amount = Column(Float)  # 净流入
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_capital_ts_date', 'ts_code', 'trade_date', unique=True),
    )
    
    def to_dict(self) -> Dict:
        return {
            'ts_code': self.ts_code,
            'trade_date': self.trade_date,
            'close': self.close,
            'change_pct': self.change_pct,
            'buy_sm_amount': self.buy_sm_amount,
            'buy_big_amount': self.buy_big_amount,
            'buy_elg_amount': self.buy_elg_amount,
            'sell_sm_amount': self.sell_sm_amount,
            'sell_big_amount': self.sell_big_amount,
            'sell_elg_amount': self.sell_elg_amount,
            'net_amount': self.net_amount
        }


class DataCacheStatus(Base):
    """数据缓存状态记录"""
    __tablename__ = 'cache_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_type = Column(String(50), nullable=False, unique=True)  # indices, sectors, stocks
    last_update = Column(DateTime)
    next_update = Column(DateTime)
    update_interval = Column(Integer)  # 更新间隔（分钟）
    record_count = Column(Integer, default=0)
    status = Column(String(20), default='pending')  # pending, updating, success, error
    error_message = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'data_type': self.data_type,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'next_update': self.next_update.isoformat() if self.next_update else None,
            'update_interval': self.update_interval,
            'record_count': self.record_count,
            'status': self.status,
            'error_message': self.error_message
        }


# 数据库连接管理
class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_url: str = "sqlite:///./data/ashare.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


# 全局数据库实例
db_manager = DatabaseManager()
