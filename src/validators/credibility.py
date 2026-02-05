"""
可信度评估模块

评估新闻的可信度
"""
import re
from typing import Dict

from src.validators.base import BaseValidator
from src.storage.models import NewsArticle
from src.utils.logger import logger


# 新闻源基础可信度评分
SOURCE_CREDIBILITY = {
    # 通讯社 (0.95-1.0)
    "Reuters": 0.98,
    "Associated Press": 0.97,
    "AFP": 0.96,
    
    # 主流媒体 (0.85-0.95)
    "BBC News": 0.92,
    "The Guardian": 0.88,
    "The New York Times": 0.90,
    "The Washington Post": 0.89,
    "Financial Times": 0.91,
    "The Economist": 0.90,
    "Al Jazeera": 0.85,
    "NHK World": 0.90,
    "The Japan Times": 0.87,
    "The Asahi Shimbun": 0.86,
    "The Mainichi": 0.86,
    
    # 新加坡媒体 (0.85-0.90)
    "Lianhe Zaobao": 0.88,
    "8World": 0.85,
    
    # 科技媒体 (0.75-0.85)
    "TechCrunch": 0.80,
    "The Verge": 0.78,
    "Ars Technica": 0.82,
    
    # 社交聚合 (0.60-0.75)
    "Hacker News": 0.70,
    "Reddit": 0.65,
    "Google News": 0.70,
}


class CredibilityValidator(BaseValidator):
    """可信度评估器"""
    
    def __init__(self):
        super().__init__("可信度评估")
        self.emotion_words = [
            "惊人", "震惊", "疯狂", "难以置信", "不可思议", "绝对", "肯定",
            "amazing", "shocking", "crazy", "unbelievable", "absolutely"
        ]
    
    def validate(self, article: NewsArticle) -> NewsArticle:
        """
        评估新闻可信度
        
        Args:
            article: 新闻文章
        
        Returns:
            更新了可信度评分的文章
        """
        try:
            # 基础可信度（来自新闻源）
            base_score = self._get_source_credibility(article.source)
            
            # 内容完整性评分
            completeness_score = self._assess_completeness(article)
            
            # 语言特征评分
            language_score = self._assess_language(article)
            
            # 综合评分
            credibility_score = (
                base_score * 0.6 +
                completeness_score * 0.2 +
                language_score * 0.2
            )
            
            article.credibility_score = round(credibility_score, 2)
            
            # 添加验证标签
            if credibility_score >= 0.85:
                article.verification_labels.append("高可信度")
            elif credibility_score >= 0.70:
                article.verification_labels.append("较可信")
            elif credibility_score >= 0.50:
                article.verification_labels.append("中等可信度")
            else:
                article.warnings.append("⚠️ 可信度较低，建议谨慎对待")
            
            logger.debug(
                f"[{self.name}] {article.title[:30]}... 可信度: {credibility_score:.2f}"
            )
            
        except Exception as e:
            logger.error(f"[{self.name}] 评估失败: {e}", exc_info=True)
        
        return article
    
    def _get_source_credibility(self, source: str) -> float:
        """
        获取新闻源的基础可信度
        
        Args:
            source: 新闻源名称
        
        Returns:
            可信度评分 (0.0-1.0)
        """
        return SOURCE_CREDIBILITY.get(source, 0.60)  # 默认 0.60
    
    def _assess_completeness(self, article: NewsArticle) -> float:
        """
        评估内容完整性
        
        Args:
            article: 新闻文章
        
        Returns:
            完整性评分 (0.0-1.0)
        """
        score = 0.5  # 基础分
        
        # 有标题
        if article.title and len(article.title) > 10:
            score += 0.1
        
        # 有内容
        if article.content and len(article.content) > 100:
            score += 0.2
        
        # 有 URL
        if article.url:
            score += 0.1
        
        # 有发布时间
        if article.published_at:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_language(self, article: NewsArticle) -> float:
        """
        评估语言特征（检测情绪化、夸张等）
        
        Args:
            article: 新闻文章
        
        Returns:
            语言评分 (0.0-1.0)，分数越高越客观
        """
        score = 1.0
        text = f"{article.title} {article.content}"
        
        # 检测情绪化词汇
        emotion_count = sum(1 for word in self.emotion_words if word.lower() in text.lower())
        if emotion_count > 0:
            score -= min(emotion_count * 0.1, 0.3)
            article.warnings.append("⚠️ 检测到情绪化表述")
        
        # 检测标题党（标题中过多感叹号或问号）
        if article.title:
            exclamation_count = article.title.count('!') + article.title.count('！')
            question_count = article.title.count('?') + article.title.count('？')
            
            if exclamation_count > 1 or question_count > 1:
                score -= 0.15
                article.warnings.append("⚠️ 标题可能存在夸大")
        
        # 检测全大写词汇（英文）
        if article.title:
            upper_words = re.findall(r'\b[A-Z]{3,}\b', article.title)
            if len(upper_words) > 2:
                score -= 0.1
        
        return max(score, 0.0)
