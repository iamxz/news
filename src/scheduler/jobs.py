"""
定时任务模块

定义所有定时任务
"""
from datetime import datetime
from src.fetchers import (
    ReutersFetcher, APNewsFetcher, BBCFetcher, BloombergFetcher,
    HackerNewsFetcher, GuardianFetcher, NYTimesFetcher, AlJazeeraFetcher,
    TechCrunchFetcher, ZaobaoFetcher, AFPFetcher, WashingtonPostFetcher,
    FinancialTimesFetcher, EconomistFetcher, ArsTechnicaFetcher,
    TheVergeFetcher, GoogleNewsFetcher, EightWorldFetcher, NHKWorldFetcher,
    AsahiFetcher, MainichiFetcher, JapanTimesFetcher, ShinMinFetcher,
    SCMPFetcher, InitiumFetcher, ToutiaoFetcher, BaiduFetcher, WeiboFetcher,
    RuanyifengFetcher, MITTechReviewFetcher
)
from src.translators import translator_manager
from src.validators import ValidationPipeline
from src.storage.database import Database
from src.utils.logger import logger


class NewsJobs:
    """新闻任务管理"""
    
    def __init__(self):
        self.db = Database()
        self.translator = translator_manager.get_translator()
        self.validator = ValidationPipeline()
        
        # 高优先级新闻源（每小时）
        self.high_priority_fetchers = [
            ReutersFetcher(),
            APNewsFetcher(),
            BBCFetcher(),
            BloombergFetcher(),
            HackerNewsFetcher(),
            AFPFetcher(),
            ToutiaoFetcher(),
            BaiduFetcher(),
            WeiboFetcher(),
        ]
        
        # 中优先级新闻源（每6小时）
        self.medium_priority_fetchers = [
            GuardianFetcher(),
            NYTimesFetcher(),
            AlJazeeraFetcher(),
            TechCrunchFetcher(),
            WashingtonPostFetcher(),
            FinancialTimesFetcher(),
            GoogleNewsFetcher(),
            NHKWorldFetcher(),
            JapanTimesFetcher(),
            SCMPFetcher(),
        ]
        
        # 低优先级新闻源（每天）
        self.low_priority_fetchers = [
            ZaobaoFetcher(),
            EconomistFetcher(),
            ArsTechnicaFetcher(),
            TheVergeFetcher(),
            EightWorldFetcher(),
            AsahiFetcher(),
            MainichiFetcher(),
            ShinMinFetcher(),
            InitiumFetcher(),
            RuanyifengFetcher(),
            MITTechReviewFetcher(),
        ]
    
    async def fetch_high_priority_news(self):
        """抓取高优先级新闻（每小时）"""
        logger.info("=" * 60)
        logger.info("开始抓取高优先级新闻")
        logger.info("=" * 60)
        
        await self._fetch_from_sources(self.high_priority_fetchers)
        
        logger.info("高优先级新闻抓取完成")
    
    async def fetch_medium_priority_news(self):
        """抓取中优先级新闻（每6小时）"""
        logger.info("=" * 60)
        logger.info("开始抓取中优先级新闻")
        logger.info("=" * 60)
        
        await self._fetch_from_sources(self.medium_priority_fetchers)
        
        logger.info("中优先级新闻抓取完成")
    
    async def fetch_low_priority_news(self):
        """抓取低优先级新闻（每天）"""
        logger.info("=" * 60)
        logger.info("开始抓取低优先级新闻")
        logger.info("=" * 60)
        
        await self._fetch_from_sources(self.low_priority_fetchers)
        
        logger.info("低优先级新闻抓取完成")
    
    async def _fetch_from_sources(self, fetchers):
        """从指定新闻源抓取"""
        total = 0
        
        for fetcher in fetchers:
            try:
                articles = await fetcher.fetch()
                
                for article_data in articles:
                    # 保存到数据库
                    article = self.db.save_article(article_data)
                    total += 1
                    
                logger.info(f"[{fetcher.source_name}] 抓取了 {len(articles)} 篇新闻")
                
            except Exception as e:
                logger.error(f"[{fetcher.source_name}] 抓取失败: {e}", exc_info=True)
        
        logger.info(f"本次共抓取 {total} 篇新闻")
    
    async def translate_pending_news(self):
        """翻译待翻译的新闻"""
        logger.info("开始翻译待翻译的新闻")
        
        # 获取未翻译的新闻
        articles = self.db.get_articles(limit=50)
        untranslated = [a for a in articles if not a.title_zh]
        
        if not untranslated:
            logger.info("没有待翻译的新闻")
            return
        
        translated_count = 0
        
        for article in untranslated[:20]:  # 每次最多翻译20篇
            try:
                # 翻译标题
                title_zh = await self.translator.translate(article.title)
                
                # 翻译内容（如果有）
                content_zh = ""
                if article.content:
                    content_zh = await self.translator.translate(article.content[:1000])
                
                # 更新数据库
                self.db.update_translation(article.id, title_zh, content_zh)
                translated_count += 1
                
                logger.debug(f"翻译完成: {article.title[:30]}...")
                
            except Exception as e:
                logger.error(f"翻译失败 [{article.id}]: {e}")
        
        logger.info(f"翻译完成，共 {translated_count} 篇")
    
    async def validate_pending_news(self):
        """验证待验证的新闻"""
        logger.info("开始验证待验证的新闻")
        
        # 获取未验证的新闻
        articles = self.db.get_articles(limit=100)
        unvalidated = [a for a in articles if not a.validated]
        
        if not unvalidated:
            logger.info("没有待验证的新闻")
            return
        
        validated_count = 0
        
        for article in unvalidated[:30]:  # 每次最多验证30篇
            try:
                # 验证
                validated_article = self.validator.validate(article)
                
                # 更新数据库
                self.db.update_validation(
                    validated_article.id,
                    validated_article.credibility_score,
                    validated_article.fact_checked,
                    validated_article.cross_references,
                    validated_article.verification_labels,
                    validated_article.warnings
                )
                validated_count += 1
                
                logger.debug(f"验证完成: {article.title[:30]}...")
                
            except Exception as e:
                logger.error(f"验证失败 [{article.id}]: {e}")
        
        logger.info(f"验证完成，共 {validated_count} 篇")
    
    async def clean_old_news(self):
        """清理旧新闻（30天前）"""
        logger.info("开始清理旧新闻")
        
        deleted = self.db.clean_old_articles(days=30)
        
        logger.info(f"清理完成，删除了 {deleted} 篇旧新闻")
