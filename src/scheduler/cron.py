"""
定时调度模块

使用 APScheduler 管理定时任务
"""
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from src.scheduler.jobs import NewsJobs
from src.utils.logger import logger


class NewsScheduler:
    """新闻定时调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = NewsJobs()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        
        # 高优先级新闻：每小时抓取
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.fetch_high_priority_news],
            trigger=IntervalTrigger(hours=1),
            id='fetch_high_priority',
            name='抓取高优先级新闻',
            replace_existing=True
        )
        
        # 中优先级新闻：每6小时抓取
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.fetch_medium_priority_news],
            trigger=IntervalTrigger(hours=6),
            id='fetch_medium_priority',
            name='抓取中优先级新闻',
            replace_existing=True
        )
        
        # 低优先级新闻：每天凌晨2点抓取
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.fetch_low_priority_news],
            trigger=CronTrigger(hour=2, minute=0),
            id='fetch_low_priority',
            name='抓取低优先级新闻',
            replace_existing=True
        )
        
        # 翻译任务：每30分钟运行一次
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.translate_pending_news],
            trigger=IntervalTrigger(minutes=30),
            id='translate_news',
            name='翻译新闻',
            replace_existing=True
        )
        
        # 验证任务：每小时运行一次
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.validate_pending_news],
            trigger=IntervalTrigger(hours=1),
            id='validate_news',
            name='验证新闻',
            replace_existing=True
        )
        
        # 清理任务：每周日凌晨3点运行
        self.scheduler.add_job(
            self._run_async_job,
            args=[self.jobs.clean_old_news],
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='clean_old_news',
            name='清理旧新闻',
            replace_existing=True
        )
        
        logger.info("定时任务已设置")
    
    def _run_async_job(self, coro_func):
        """在新的事件循环中运行异步任务"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro_func())
            loop.close()
        except Exception as e:
            logger.error(f"执行任务失败: {e}", exc_info=True)
    
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


# 全局调度器实例
_scheduler = None


def start_scheduler():
    """启动定时任务调度器"""
    global _scheduler
    if _scheduler is None:
        _scheduler = NewsScheduler()
        _scheduler.start()
        logger.info("定时任务调度器已启动")
    else:
        logger.warning("调度器已经在运行中")


def stop_scheduler():
    """停止定时任务调度器"""
    global _scheduler
    if _scheduler is not None:
        _scheduler.stop()
        _scheduler = None
        logger.info("定时任务调度器已停止")
    else:
        logger.warning("调度器未运行")


def get_scheduler_status():
    """获取调度器状态"""
    global _scheduler
    if _scheduler is not None and _scheduler.scheduler.running:
        jobs = _scheduler.scheduler.get_jobs()
        return {
            'running': True,
            'jobs_count': len(jobs),
            'jobs': [{'id': job.id, 'name': job.name, 'next_run': str(job.next_run_time)} for job in jobs]
        }
    else:
        return {
            'running': False,
            'jobs_count': 0,
            'jobs': []
        }

