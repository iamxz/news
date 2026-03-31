"""
定时任务模块

定义所有定时任务
"""
from datetime import datetime
from src.fetchers.registry import FETCHERS

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
        
        # 动态获取所有抓取器并按中文优先排序
        self.all_fetchers = self._get_all_fetchers_sorted()
    

    
    async def _fetch_from_sources(self, fetchers):
        """从指定新闻源抓取"""
        total = 0

        for fetcher in fetchers:
            try:
                articles = await fetcher.fetch()

                from src.storage.models import NewsArticle
                for article_dict in articles:
                    article_dict = fetcher.normalize_article(article_dict)
                    if not fetcher.validate_article(article_dict):
                        continue
                    # 使用 from_dict 统一转换，消除重复逻辑
                    article_obj = NewsArticle.from_dict(article_dict, fetcher)
                    if self.db.save_article(article_obj):
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
    
    def _get_all_fetchers_sorted(self):
        """动态获取所有抓取器并按中文优先排序"""
        # 实例化所有抓取器
        fetchers = [fetcher_class() for fetcher_class in FETCHERS.values()]
        
        # 按中文优先排序
        def sort_key(fetcher):
            # 使用抓取器的 language 字段来判断
            language = getattr(fetcher, 'language', 'en')
            if language == 'zh':
                return (0, fetcher.source_name)
            else:
                return (1, fetcher.source_name)
        
        # 排序
        fetchers.sort(key=sort_key)
        return fetchers
    
    async def fetch_all_news(self):
        """抓取所有新闻源"""
        logger.info("=" * 60)
        logger.info("开始抓取所有新闻源")
        logger.info("=" * 60)
        
        await self._fetch_from_sources(self.all_fetchers)
        
        logger.info("所有新闻源抓取完成")
    
    async def clean_old_news(self):
        """清理旧新闻（30天前）"""
        logger.info("开始清理旧新闻")
        
        deleted = self.db.clean_old_articles(days=30)
        
        logger.info(f"清理完成，删除了 {deleted} 篇旧新闻")
