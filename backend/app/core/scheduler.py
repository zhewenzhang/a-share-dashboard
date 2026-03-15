"""
定时任务调度器
自动抓取和更新数据
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio

from app.services.data_cache import data_cache


class DataScheduler:
    """数据定时调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        
        # 指数数据更新 - 每 5 分钟
        self.scheduler.add_job(
            func=self._update_indices,
            trigger=IntervalTrigger(minutes=5),
            id='update_indices',
            name='更新指数数据',
            replace_existing=True
        )
        
        # 板块数据更新 - 每 15 分钟
        self.scheduler.add_job(
            func=self._update_sectors,
            trigger=IntervalTrigger(minutes=15),
            id='update_sectors',
            name='更新板块数据',
            replace_existing=True
        )
        
        # 股票数据更新 - 每 30 分钟
        self.scheduler.add_job(
            func=self._update_stocks,
            trigger=IntervalTrigger(minutes=30),
            id='update_stocks',
            name='更新股票数据',
            replace_existing=True
        )
        
        # 资金流向数据更新 - 每 10 分钟
        self.scheduler.add_job(
            func=self._update_capital_flow,
            trigger=IntervalTrigger(minutes=10),
            id='update_capital_flow',
            name='更新资金流向数据',
            replace_existing=True
        )
        
        # 缓存状态清理 - 每天凌晨 2 点
        self.scheduler.add_job(
            func=self._cleanup_old_cache,
            trigger='cron',
            hour=2,
            minute=0,
            id='cleanup_cache',
            name='清理过期缓存',
            replace_existing=True
        )
    
    def _update_indices(self):
        """更新指数数据"""
        try:
            print(f"[{datetime.now()}] 开始更新指数数据...")
            data_cache._update_indices_data()
            print(f"[{datetime.now()}] 指数数据更新完成")
        except Exception as e:
            print(f"[{datetime.now()}] 指数数据更新失败：{e}")
    
    def _update_sectors(self):
        """更新板块数据"""
        try:
            print(f"[{datetime.now()}] 开始更新板块数据...")
            data_cache._update_sectors_data()
            print(f"[{datetime.now()}] 板块数据更新完成")
        except Exception as e:
            print(f"[{datetime.now()}] 板块数据更新失败：{e}")
    
    def _update_stocks(self):
        """更新股票数据"""
        try:
            print(f"[{datetime.now()}] 开始更新股票数据...")
            data_cache._update_stocks_data(top_n=20)
            print(f"[{datetime.now()}] 股票数据更新完成")
        except Exception as e:
            print(f"[{datetime.now()}] 股票数据更新失败：{e}")
    
    def _update_capital_flow(self):
        """更新资金流向数据"""
        try:
            print(f"[{datetime.now()}] 开始更新资金流向数据...")
            # 这里可以实现具体的资金流向更新逻辑
            print(f"[{datetime.now()}] 资金流向数据更新完成")
        except Exception as e:
            print(f"[{datetime.now()}] 资金流向数据更新失败：{e}")
    
    def _cleanup_old_cache(self):
        """清理过期缓存"""
        try:
            print(f"[{datetime.now()}] 开始清理过期缓存...")
            # 清理 7 天前的数据
            from datetime import datetime, timedelta
            from app.db.models import db_manager
            from sqlalchemy import text
            
            session = db_manager.get_session()
            try:
                cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
                
                # 清理旧数据
                tables = ['index_data', 'sector_flow', 'stock_data', 'capital_flow']
                for table in tables:
                    session.execute(
                        text(f"DELETE FROM {table} WHERE trade_date < :cutoff"),
                        {'cutoff': cutoff_date}
                    )
                
                session.commit()
                print(f"[{datetime.now()}] 过期缓存清理完成")
            except Exception as e:
                session.rollback()
                print(f"清理缓存失败：{e}")
            finally:
                session.close()
        except Exception as e:
            print(f"[{datetime.now()}] 清理缓存失败：{e}")
    
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            print(f"[{datetime.now()}] 定时任务调度器已启动")
            print("已注册任务：")
            for job in self.scheduler.get_jobs():
                print(f"  - {job.name}: {job.trigger}")
    
    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print(f"[{datetime.now()}] 定时任务调度器已停止")
    
    def get_jobs(self) -> list:
        """获取所有任务"""
        return [
            {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in self.scheduler.get_jobs()
        ]
    
    def run_job_now(self, job_id: str):
        """立即执行某个任务"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            return True
        return False


# 全局调度器实例
data_scheduler = DataScheduler()
