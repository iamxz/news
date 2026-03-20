"""
MIT Technology Review 抓取器
"""
import hashlib
from typing import List, Optional
from datetime import datetime
import feedparser
from dateutil import parser as date_parser
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class MITTechReviewFetcher(BaseFetcher):
    """MIT Technology Review 抓取器"""
    
    def __init__(self):
        super().__init__('MIT Technology Review', 'https://www.technologyreview.com', 2.0)
        self.rss_url = 'https://www.technologyreview.com/feed/'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取科技文章"""
        try:
            feed = feedparser.parse(self.rss_url)
            articles = []
            
            for entry in feed.entries[:15]:
                article = self._parse_entry(entry)
                if article:
                    articles.append(article)
            
            logger.info(f"MIT Tech Review: 抓取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"MIT Tech Review 抓取失败: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[NewsArticle]:
        """解析单篇文章"""
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            
            if not title or not link:
                return None
            
            article_id = self.generate_id(link)
            published_at = self._parse_date(entry.get('published', ''))
            content = entry.get('summary', title)
            
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='科技',
                priority=7,
                tags=['科技', '创新', 'AI'],
                credibility_score=0.90
            )
            
        except Exception as e:
            logger.error(f"解析 MIT Tech Review 失败: {e}")
            return None
    
    def parse(self, raw_data):
        return []
    
    def _parse_date(self, date_str):
        try:
            return date_parser.parse(date_str)
        except:
            return datetime.now()
    
    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
