"""
交叉引用验证模块

检查同一事件是否有多个来源报道
"""
from datetime import timedelta
from typing import List
from src.validators.base import BaseValidator
from src.storage.models import NewsArticle
from src.storage.database import Database
from src.utils.logger import logger


class CrossReferenceValidator(BaseValidator):
    """交叉引用验证器"""
    
    def __init__(self):
        super().__init__("交叉引用验证")
        self.db = Database()
        self.similarity_threshold = 0.6  # 标题相似度阈值
    
    def validate(self, article: NewsArticle) -> NewsArticle:
        """
        验证交叉引用
        
        Args:
            article: 新闻文章
        
        Returns:
            更新了交叉引用信息的文章
        """
        try:
            # 查找相似新闻
            similar_articles = self._find_similar_articles(article)
            
            # 统计不同来源数量
            unique_sources = set()
            for similar in similar_articles:
                if similar.source != article.source:
                    unique_sources.add(similar.source)
            
            article.cross_references = len(unique_sources)
            
            # 添加验证标签
            if article.cross_references >= 5:
                article.verification_labels.append("多源确认")
            elif article.cross_references >= 3:
                article.verification_labels.append("已交叉验证")
            elif article.cross_references == 0:
                article.warnings.append("⚠️ 单一来源，尚未被其他媒体证实")
            
            logger.debug(
                f"[{self.name}] {article.title[:30]}... "
                f"找到 {article.cross_references} 个交叉引用"
            )
            
        except Exception as e:
            logger.error(f"[{self.name}] 验证失败: {e}", exc_info=True)
        
        return article
    
    def _find_similar_articles(self, article: NewsArticle) -> List[NewsArticle]:
        """
        查找相似新闻
        
        Args:
            article: 新闻文章
        
        Returns:
            相似新闻列表
        """
        # 获取时间窗口内的新闻（前后24小时）
        time_window_start = article.published_at - timedelta(hours=24)
        time_window_end = article.published_at + timedelta(hours=24)
        
        # 从数据库获取候选新闻
        candidates = self.db.get_articles(
            days=2,  # 最近2天
            limit=500
        )
        
        # 过滤时间窗口
        candidates = [
            c for c in candidates
            if time_window_start <= c.published_at <= time_window_end
            and c.id != article.id
        ]
        
        # 计算相似度
        similar = []
        for candidate in candidates:
            similarity = self._calculate_similarity(article.title, candidate.title)
            if similarity >= self.similarity_threshold:
                similar.append(candidate)
        
        return similar
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度（简单的词重叠方法）
        
        Args:
            text1: 文本1
            text2: 文本2
        
        Returns:
            相似度分数 0.0-1.0
        """
        # 转小写并分词
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # 移除常见停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # 计算 Jaccard 相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
