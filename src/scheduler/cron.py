"""
定时调度模块

使用 APScheduler 管理定时任务
"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from src.scheduler.jobs import NewsJobs
from src.utils.logger import logger


class NewsScheduler:
    """新闻定时调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = NewsJobs()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        
        # 高优先级新闻：每小时抓取
        self.scheduler.add_job(
            self.jobs.fetch_high_priority_news,
            trigger=IntervalTrigger(hours=1),
            id='fetch_high_priority',
            name='抓取高优先级新闻',
            replace_existing=True
        )
        
        # 中优先级新闻：每6小时抓取
        self.scheduler.add_job(
            self.jobs.fetch_medium_priority_news,
            trigger=IntervalTrigger(hours=6),
            id='fetch_medium_priority',
            name='抓取中优先级新闻',
            replace_existing=True
        )
        
        # 低优先级新闻：每天凌晨2点抓取
        self.scheduler.add_job(
            self.jobs.fetch_low_priority_news,
            trigger=CronTrigger(hour=2, minute=0),
            id='fetch_low_priority',
            name='抓取低优先级新闻',
            replace_existing=True
        )
        
        # 翻译任务：每30分钟运行一次
        self.scheduler.add_job(
            self.jobs.translate_pending_news,
            trigger=IntervalTrigger(minutes=30),
            id='translate_news',
            name='翻译新闻',
            replace_existing=True
        )
        
        # 验证任务：每小时运行一次
        self.scheduler.add_job(
            self.jobs.validate_pending_news,
            trigger=IntervalTrigger(hours=1),
            id='validate_news',
            name='验证新闻',
            replace_existing=True
        )
        
        # 清理任务：每周日凌晨3点运行
        self.scheduler.add_job(
            self.jobs.clean_old_news,
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='clean_old_news',
            name='清理旧新闻',
            replace_existing=True
        )
        
        logger.info("定时任务已设置")
    
    def start(self):
        """启动调度器"""
        logger.info("=" * 60)
        logger.info("启动定时任务调度器")
        logger.info("=" * 60)
        
        # 显示所有任务
        self.print_jobs()
        
        self.scheduler.start()
        logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已停止")
    
    def print_jobs(self):
        """打印所有任务"""
        jobs = self.scheduler.get_jobs()
        
        logger.info("已注册的定时任务:")
        for job in jobs:
            logger.info(f"  - {job.name} (ID: {job.id})")
            logger.info(f"    触发器: {job.trigger}")
    
    async def run_forever(self):
        """持续运行"""
        try:
            # 启动时立即执行一次高优先级抓取
            logger.info("启动时执行初始抓取...")
            await self.jobs.fetch_high_priority_news()
            
            # 保持运行
            while True:
                await asyncio.sleep(3600)  # 每小时检查一次
                
        except KeyboardInterrupt:
            logger.info("收到停止信号")
            self.stop()
