"""
事实核查模块

进行基础的事实核查和交叉引用
"""
from src.validators.base import BaseValidator
from src.storage.models import NewsArticle
from src.utils.logger import logger


class FactChecker(BaseValidator):
    """事实核查器"""
    
    def __init__(self):
        super().__init__("事实核查")
    
    def validate(self, article: NewsArticle) -> NewsArticle:
        """
        进行事实核查
        
        Args:
            article: 新闻文章
        
        Returns:
            更新了核查信息的文章
        """
        try:
            # 检查是否包含消息来源
            has_source = self._check_has_source(article)
            
            # 检查是否有具体事实
            has_facts = self._check_has_facts(article)
            
            # 标记核查状态
            article.fact_checked = True
            
            # 添加标签和警告
            if has_source and has_facts:
                article.verification_labels.append("包含明确来源")
            elif not has_source:
                article.warnings.append("⚠️ 未明确标注消息来源")
            
            if not has_facts:
                article.warnings.append("⚠️ 缺乏具体事实支撑")
            
            logger.debug(f"[{self.name}] {article.title[:30]}... 事实核查完成")
            
        except Exception as e:
            logger.error(f"[{self.name}] 核查失败: {e}", exc_info=True)
        
        return article
    
    def _check_has_source(self, article: NewsArticle) -> bool:
        """
        检查是否包含消息来源
        
        Args:
            article: 新闻文章
        
        Returns:
            是否包含来源
        """
        text = f"{article.title} {article.content}".lower()
        
        source_indicators = [
            "according to", "said", "told", "reported", "confirmed",
            "据", "表示", "称", "报道", "证实", "消息人士"
        ]
        
        return any(indicator in text for indicator in source_indicators)
    
    def _check_has_facts(self, article: NewsArticle) -> bool:
        """
        检查是否包含具体事实（数字、日期、地点等）
        
        Args:
            article: 新闻文章
        
        Returns:
            是否包含事实
        """
        import re
        text = f"{article.title} {article.content}"
        
        # 检查是否包含数字
        has_numbers = bool(re.search(r'\d+', text))
        
        # 检查是否包含日期相关词汇
        date_words = ["today", "yesterday", "tomorrow", "this week", "今天", "昨天", "明天", "本周"]
        has_dates = any(word in text.lower() for word in date_words)
        
        # 检查内容长度（太短可能缺乏细节）
        has_detail = len(article.content) > 200
        
        return (has_numbers or has_dates) and has_detail
