"""
验证器基类

所有新闻验证器的基类
"""
from abc import ABC, abstractmethod

from src.storage.models import NewsArticle
from src.utils.logger import logger


class BaseValidator(ABC):
    """验证器基类"""
    
    def __init__(self, name: str):
        """
        初始化验证器
        
        Args:
            name: 验证器名称
        """
        self.name = name
    
    @abstractmethod
    def validate(self, article: NewsArticle) -> NewsArticle:
        """
        验证新闻（需要子类实现）
        
        Args:
            article: 新闻文章
        
        Returns:
            更新后的新闻文章
        """
        pass
    
    def validate_batch(self, articles: list[NewsArticle]) -> list[NewsArticle]:
        """
        批量验证新闻
        
        Args:
            articles: 新闻列表
        
        Returns:
            验证后的新闻列表
        """
        results = []
        for article in articles:
            try:
                validated = self.validate(article)
                results.append(validated)
            except Exception as e:
                logger.error(f"[{self.name}] 验证新闻失败: {e}", exc_info=True)
                results.append(article)
        
        return results
