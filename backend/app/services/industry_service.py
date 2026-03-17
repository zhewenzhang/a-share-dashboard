"""
行业资金流向服务
计算和获取行业级别的资金流向数据
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import db_manager, SectorFlow, DataCacheStatus
from app.services.tushare_service import tushare_service


class IndustryFlowService:
    """行业资金流向服务"""
    
    # 主要行业映射（申万一级行业）
    INDUSTRY_MAP = {
        '801010': '农林牧渔',
        '801020': '基础化工',
        '801030': '钢铁',
        '801040': '有色金属',
        '801050': '建筑材料',
        '801080': '电子',
        '801090': '计算机',
        '801100': '家用电器',
        '801110': '食品饮料',
        '801120': '纺织服装',
        '801130': '轻工制造',
        '801140': '医药生物',
        '801150': '公用事业',
        '801160': '交通运输',
        '801170': '房地产',
        '801180': '商贸零售',
        '801200': '社会服务',
        '801210': '银行',
        '801220': '非银金融',
        '801230': '综合',
        '801710': '建筑材料',
        '801720': '建筑装饰',
        '801730': '电力设备',
        '801740': '机械设备',
        '801750': '国防军工',
        '801760': '汽车',
        '801770': '通信',
        '801780': '煤炭',
        '801790': '石油石化',
        '801880': '汽车',
        '801890': '机械设备'
    }
    
    def __init__(self):
        self.db = db_manager
    
    def _get_session(self) -> Session:
        """获取数据库会话"""
        return self.db.get_session()
    
    def get_industry_flow(self, force_update: bool = False) -> List[Dict]:
        """
        获取行业资金流向排行
        
        Returns:
            行业资金流向列表，按净流入金额排序
        """
        # 检查缓存
        if not force_update:
            cached_data = self._get_cached_industry_flow()
            if cached_data:
                return cached_data
        
        # 从 TuShare 获取数据
        if tushare_service.is_available():
            try:
                data = self._fetch_from_tushare()
                if data:
                    self._save_to_cache(data)
                    return data
            except Exception as e:
                print(f"从 TuShare 获取行业数据失败：{e}")
        
        # 返回模拟数据
        return self._get_mock_industry_flow()
    
    def _fetch_from_tushare(self) -> Optional[List[Dict]]:
        """从 TuShare 获取行业资金流向数据"""
        if not tushare_service.is_available():
            return None
        
        try:
            # 获取交易日历，确定最近交易日
            pro = tushare_service.api
            today = datetime.now().strftime('%Y%m%d')
            
            # 获取行业分类（申万一级）
            industry_df = pro.index_classify(src='SW2021', level='L1')
            if industry_df is None or industry_df.empty:
                return None
            
            results = []
            
            # 遍历每个行业，计算资金流向
            for _, row in industry_df.iterrows():
                industry_code = row['index_code']
                industry_name = row['industry_name']
                
                try:
                    # 获取行业成分股
                    members_df = pro.index_member(index_code=industry_code)
                    if members_df is None or members_df.empty:
                        continue
                    
                    # 获取成分股的资金流向
                    stock_codes = members_df['con_code'].tolist()[:50]  # 限制数量，避免 API 限制
                    
                    total_inflow = 0
                    up_count = 0
                    down_count = 0
                    total_amount = 0
                    
                    # 批量获取资金流向
                    for ts_code in stock_codes:
                        try:
                            flow_df = pro.moneyflow(ts_code=ts_code, trade_date=today)
                            if flow_df is not None and not flow_df.empty:
                                flow_row = flow_df.iloc[0]
                                net_amount = float(flow_row.get('net_mf_amount', 0))
                                total_inflow += net_amount
                                total_amount += abs(net_amount)
                                
                                # 统计涨跌
                                change_pct = float(flow_row.get('pct_change', 0))
                                if change_pct > 0:
                                    up_count += 1
                                elif change_pct < 0:
                                    down_count += 1
                        except Exception as e:
                            continue
                    
                    # 计算行业指标
                    stock_count = len(stock_codes)
                    avg_change = (up_count - down_count) / stock_count * 100 if stock_count > 0 else 0
                    
                    results.append({
                        'industry_code': industry_code,
                        'industry_name': industry_name,
                        'net_amount': total_inflow,
                        'stock_count': stock_count,
                        'up_count': up_count,
                        'down_count': down_count,
                        'avg_change_pct': avg_change,
                        'total_amount': total_amount,
                        'leader_stock': self._get_industry_leader(stock_codes[:10]),
                        'trade_date': today
                    })
                    
                except Exception as e:
                    print(f"处理行业 {industry_name} 失败：{e}")
                    continue
            
            # 按净流入金额排序
            results.sort(key=lambda x: x['net_amount'], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"获取行业资金流向失败：{e}")
            return None
    
    def _get_industry_leader(self, stock_codes: List[str]) -> Optional[Dict]:
        """获取行业龙头股（净流入最多的股票）"""
        if not tushare_service.is_available():
            return None
        
        try:
            pro = tushare_service.api
            today = datetime.now().strftime('%Y%m%d')
            
            leader = None
            max_inflow = -float('inf')
            
            for ts_code in stock_codes:
                try:
                    flow_df = pro.moneyflow(ts_code=ts_code, trade_date=today)
                    if flow_df is not None and not flow_df.empty:
                        net_amount = float(flow_df.iloc[0].get('net_mf_amount', 0))
                        if net_amount > max_inflow:
                            max_inflow = net_amount
                            # 获取股票基本信息
                            stock_df = pro.stock_basic(ts_code=ts_code, fields='ts_code,name')
                            if stock_df is not None and not stock_df.empty:
                                leader = {
                                    'ts_code': ts_code,
                                    'name': stock_df.iloc[0]['name'],
                                    'net_amount': net_amount
                                }
                except:
                    continue
            
            return leader
        except:
            return None
    
    def _get_cached_industry_flow(self) -> Optional[List[Dict]]:
        """从缓存获取行业资金流向"""
        session = self._get_session()
        try:
            # 检查缓存状态
            cache_status = session.query(DataCacheStatus).filter(
                DataCacheStatus.data_type == 'industry_flow'
            ).first()
            
            if not cache_status or not cache_status.last_update:
                return None
            
            # 检查是否过期（15分钟）
            if datetime.now() - cache_status.last_update > timedelta(minutes=15):
                return None
            
            # 从数据库读取
            today = datetime.now().strftime('%Y%m%d')
            records = session.query(SectorFlow).filter(
                SectorFlow.trade_date == today
            ).order_by(SectorFlow.net_amount.desc()).all()
            
            if records:
                return [{
                    'industry_code': r.sector_code,
                    'industry_name': r.sector_name,
                    'net_amount': r.net_amount,
                    'stock_count': r.stock_count,
                    'up_count': r.inflow_stock_count,
                    'avg_change_pct': r.change_pct,
                    'trade_date': r.trade_date
                } for r in records]
            
            return None
        finally:
            session.close()
    
    def _save_to_cache(self, data: List[Dict]):
        """保存到缓存"""
        session = self._get_session()
        try:
            today = datetime.now().strftime('%Y%m%d')
            
            # 保存行业数据
            for item in data:
                sector = session.query(SectorFlow).filter(
                    SectorFlow.sector_code == item['industry_code'],
                    SectorFlow.trade_date == today
                ).first()
                
                if not sector:
                    sector = SectorFlow(
                        sector_code=item['industry_code'],
                        trade_date=today
                    )
                    session.add(sector)
                
                sector.sector_name = item['industry_name']
                sector.net_amount = item['net_amount']
                sector.stock_count = item['stock_count']
                sector.inflow_stock_count = item.get('up_count', 0)
                sector.change_pct = item.get('avg_change_pct', 0)
            
            # 更新缓存状态
            cache_status = session.query(DataCacheStatus).filter(
                DataCacheStatus.data_type == 'industry_flow'
            ).first()
            
            if not cache_status:
                cache_status = DataCacheStatus(data_type='industry_flow', update_interval=15)
                session.add(cache_status)
            
            cache_status.last_update = datetime.now()
            cache_status.record_count = len(data)
            cache_status.status = 'success'
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"保存行业数据失败：{e}")
        finally:
            session.close()
    
    def _get_mock_industry_flow(self) -> List[Dict]:
        """获取模拟行业资金流向数据"""
        mock_data = [
            {
                'industry_code': '801080',
                'industry_name': '电子',
                'net_amount': 2850000000,
                'stock_count': 85,
                'up_count': 62,
                'down_count': 23,
                'avg_change_pct': 2.35,
                'leader_stock': {'ts_code': '688981.SH', 'name': '中芯国际', 'net_amount': 450000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801090',
                'industry_name': '计算机',
                'net_amount': 1920000000,
                'stock_count': 78,
                'up_count': 55,
                'down_count': 23,
                'avg_change_pct': 1.85,
                'leader_stock': {'ts_code': '000938.SZ', 'name': '中芯国际', 'net_amount': 280000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801730',
                'industry_name': '电力设备',
                'net_amount': 1680000000,
                'stock_count': 92,
                'up_count': 68,
                'down_count': 24,
                'avg_change_pct': 1.52,
                'leader_stock': {'ts_code': '300750.SZ', 'name': '宁德时代', 'net_amount': 850000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801760',
                'industry_name': '汽车',
                'net_amount': 1250000000,
                'stock_count': 65,
                'up_count': 48,
                'down_count': 17,
                'avg_change_pct': 1.28,
                'leader_stock': {'ts_code': '002594.SZ', 'name': '比亚迪', 'net_amount': 320000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801140',
                'industry_name': '医药生物',
                'net_amount': 980000000,
                'stock_count': 72,
                'up_count': 51,
                'down_count': 21,
                'avg_change_pct': 0.95,
                'leader_stock': {'ts_code': '600276.SH', 'name': '恒瑞医药', 'net_amount': 180000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801110',
                'industry_name': '食品饮料',
                'net_amount': 650000000,
                'stock_count': 45,
                'up_count': 32,
                'down_count': 13,
                'avg_change_pct': 0.68,
                'leader_stock': {'ts_code': '000858.SZ', 'name': '五粮液', 'net_amount': 210000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801220',
                'industry_name': '非银金融',
                'net_amount': 420000000,
                'stock_count': 38,
                'up_count': 28,
                'down_count': 10,
                'avg_change_pct': 0.45,
                'leader_stock': {'ts_code': '600030.SH', 'name': '中信证券', 'net_amount': 560000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801210',
                'industry_name': '银行',
                'net_amount': -280000000,
                'stock_count': 42,
                'up_count': 18,
                'down_count': 24,
                'avg_change_pct': -0.32,
                'leader_stock': {'ts_code': '600036.SH', 'name': '招商银行', 'net_amount': -120000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801170',
                'industry_name': '房地产',
                'net_amount': -520000000,
                'stock_count': 55,
                'up_count': 22,
                'down_count': 33,
                'avg_change_pct': -0.68,
                'leader_stock': {'ts_code': '000002.SZ', 'name': '万科A', 'net_amount': -180000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            },
            {
                'industry_code': '801780',
                'industry_name': '煤炭',
                'net_amount': -780000000,
                'stock_count': 28,
                'up_count': 12,
                'down_count': 16,
                'avg_change_pct': -1.25,
                'leader_stock': {'ts_code': '601088.SH', 'name': '中国神华', 'net_amount': -220000000},
                'trade_date': datetime.now().strftime('%Y%m%d')
            }
        ]
        
        return mock_data


# 全局服务实例
industry_service = IndustryFlowService()
