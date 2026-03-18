"""
新闻处理模块

实现新闻清洗和相似度判断功能
"""
from datetime import datetime
from typing import List, Dict, Tuple
import re
import string
from difflib import SequenceMatcher

from src.storage.models import NewsArticle
from src.utils.logger import logger


class NewsProcessor:
    """新闻处理器"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        初始化新闻处理器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值的新闻视为相似
        """
        self.similarity_threshold = similarity_threshold
    
    def clean_article(self, article: NewsArticle) -> NewsArticle:
        """
        清洗新闻文章
        
        Args:
            article: 原始新闻文章
        
        Returns:
            清洗后的新闻文章
        """
        # 清洗标题
        article.title = self._clean_text(article.title)
        if article.title_zh:
            article.title_zh = self._clean_text(article.title_zh)
        if article.title_en:
            article.title_en = self._clean_text(article.title_en)
        
        # 清洗内容
        article.content = self._clean_text(article.content)
        if article.content_zh:
            article.content_zh = self._clean_text(article.content_zh)
        if article.content_en:
            article.content_en = self._clean_text(article.content_en)
        
        # 去除重复标签
        article.tags = list(set(article.tags))
        
        # 标准化分类
        article.category = self._normalize_category(article.category)
        
        return article
    
    def _clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        if not text:
            return text
        
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def _normalize_category(self, category: str) -> str:
        """
        标准化分类
        
        Args:
            category: 原始分类
        
        Returns:
            标准化后的分类
        """
        if not category:
            return '综合'
        
        # 常见分类映射
        category_map = {
            'general': '综合',
            'news': '新闻',
            'politics': '政治',
            'economy': '经济',
            'finance': '金融',
            'technology': '科技',
            'science': '科学',
            'sports': '体育',
            'entertainment': '娱乐',
            'culture': '文化',
            'health': '健康',
            'education': '教育',
            'international': '国际',
            'local': '本地',
            'business': '商业',
            'world': '国际',
            'national': '国内',
            'tech': '科技',
            'sports news': '体育',
            'entertainment news': '娱乐',
            'business news': '商业',
            '政治新闻': '政治',
            '经济新闻': '经济',
            '科技新闻': '科技',
            '体育新闻': '体育',
            '娱乐新闻': '娱乐',
            '国际新闻': '国际',
            '国内新闻': '国内',
            '社会新闻': '社会',
            '军事新闻': '军事',
            '财经新闻': '财经',
            '文化新闻': '文化',
            '教育新闻': '教育',
            '健康新闻': '健康',
            '科技资讯': '科技',
            '体育资讯': '体育',
            '娱乐资讯': '娱乐',
            '财经资讯': '财经',
            '国际资讯': '国际',
            '国内资讯': '国内',
            '社会资讯': '社会',
            '军事资讯': '军事',
            '文化资讯': '文化',
            '教育资讯': '教育',
            '健康资讯': '健康',
        }
        
        category_lower = category.lower()
        for key, value in category_map.items():
            if key.lower() in category_lower:
                return value
        
        return category
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # 使用 SequenceMatcher 计算相似度
            matcher = SequenceMatcher(None, text1, text2)
            similarity = matcher.ratio()
            return similarity
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def group_similar_articles(self, articles: List[NewsArticle]) -> List[List[NewsArticle]]:
        """
        将相似的新闻分组
        
        Args:
            articles: 新闻列表
        
        Returns:
            分组后的新闻列表
        """
        if not articles:
            return []
        
        # 分组结果
        groups = []
        
        for article in articles:
            # 检查是否与现有组相似
            matched = False
            for group in groups:
                # 与组内第一篇新闻比较
                reference_article = group[0]
                
                # 计算标题相似度
                title_similarity = self.calculate_similarity(
                    article.title or article.title_zh or article.title_en,
                    reference_article.title or reference_article.title_zh or reference_article.title_en
                )
                
                # 计算内容相似度（如果内容不为空）
                content_similarity = 0.0
                if article.content or article.content_zh or article.content_en:
                    content_similarity = self.calculate_similarity(
                        article.content or article.content_zh or article.content_en,
                        reference_article.content or reference_article.content_zh or reference_article.content_en
                    )
                
                # 综合相似度
                combined_similarity = (title_similarity * 0.7) + (content_similarity * 0.3)
                
                if combined_similarity >= self.similarity_threshold:
                    group.append(article)
                    matched = True
                    break
            
            if not matched:
                # 创建新组
                groups.append([article])
        
        return groups
    
    def merge_similar_articles(self, articles: List[NewsArticle]) -> NewsArticle:
        """
        合并相似的新闻

        Args:
            articles: 相似新闻列表

        Returns:
            合并后的新闻
        """
        if not articles:
            raise ValueError("新闻列表不能为空")
        if len(articles) == 1:
            return articles[0]

        # 选择发布时间最早的作为基础，用 model_copy 克隆避免逐字段枚举
        base_article = min(articles, key=lambda x: x.published_at)
        merged_article = base_article.model_copy(update={'fetched_at': datetime.now()})

        # 遍历其他新闻，补充缺失字段并合并集合类数据
        for article in articles:
            if article == base_article:
                continue

            # 补充标题和内容（仅填充空缺）
            for field in ('title', 'title_zh', 'title_en', 'content', 'content_zh', 'content_en'):
                if not getattr(merged_article, field) and getattr(article, field):
                    setattr(merged_article, field, getattr(article, field))

            # 合并集合类字段
            merged_article.tags = list(set(merged_article.tags + article.tags))
            merged_article.verification_labels = list(
                set(merged_article.verification_labels + article.verification_labels)
            )
            merged_article.warnings = list(set(merged_article.warnings + article.warnings))

            # 取最高可信度，累计交叉引用
            if article.credibility_score > merged_article.credibility_score:
                merged_article.credibility_score = article.credibility_score
            merged_article.cross_references += article.cross_references + 1

        merged_article.validated = True
        return merged_article
    
    def process_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        处理新闻列表
        
        Args:
            articles: 原始新闻列表
        
        Returns:
            处理后的新闻列表
        """
        if not articles:
            return []
        
        # 清洗新闻
        cleaned_articles = [self.clean_article(article) for article in articles]
        
        # 分组相似新闻
        groups = self.group_similar_articles(cleaned_articles)
        
        # 合并每组相似新闻
        processed_articles = []
        for group in groups:
            if len(group) > 1:
                merged_article = self.merge_similar_articles(group)
                processed_articles.append(merged_article)
                logger.info(f"合并了 {len(group)} 篇相似新闻: {merged_article.title[:50]}...")
            else:
                processed_articles.append(group[0])
        
        logger.info(f"处理完成: 原始 {len(articles)} 篇, 处理后 {len(processed_articles)} 篇")
        return processed_articles


# 全局新闻处理器实例
news_processor = NewsProcessor()
