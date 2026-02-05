"""
验证器管理模块

管理所有验证器
"""
from src.validators.credibility import CredibilityValidator
from src.validators.fact_checker import FactChecker
from src.storage.models import NewsArticle
from src.utils.config import get_settings
from src.utils.logger import logger


class ValidationPipeline:
    """验证管道"""
    
    def __init__(self):
        """初始化验证管道"""
        self.settings = get_settings()
        self.validators = []
        self._init_validators()
    
    def _init_validators(self):
        """初始化所有验证器"""
        # 可信度评估（总是启用）
        self.validators.append(CredibilityValidator())
        
        # 事实核查（可配置）
        if self.settings.enable_fact_check:
            self.validators.append(FactChecker())
        
        logger.info(f"验证器已加载: {[v.name for v in self.validators]}")
    
    def validate(self, article: NewsArticle) -> NewsArticle:
        """
        验证单篇新闻
        
        Args:
            article: 新闻文章
        
        Returns:
            验证后的文章
        """
        for validator in self.validators:
            try:
                article = validator.validate(article)
            except Exception as e:
                logger.error(f"验证器 {validator.name} 失败: {e}", exc_info=True)
        
        article.validated = True
        return article
    
    def validate_batch(self, articles: list[NewsArticle]) -> list[NewsArticle]:
        """
        批量验证新闻
        
        Args:
            articles: 新闻列表
        
        Returns:
            验证后的新闻列表
        """
        results = []
        for i, article in enumerate(articles):
            logger.info(f"验证进度: {i+1}/{len(articles)}")
            validated = self.validate(article)
            results.append(validated)
        
        return results


# 全局验证管道实例
validation_pipeline = ValidationPipeline()
