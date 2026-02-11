"""
微博热搜抓取器
"""
import hashlib
from typing import List, Optional
from datetime import datetime
import feedparser
from dateutil import parser as date_parser
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class WeiboFetcher(BaseFetcher):
    """微博热搜抓取器"""
    
    def __init__(self):
        super().__init__('微博热搜', 'https://weibo.com', 2.0)
        # 使用 RSSHub 提供的微博热搜
        self.rss_url = 'https://rsshub.app/weibo/search/hot'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取微博热搜"""
        try:
            feed = feedparser.parse(self.rss_url)
            articles = []
            
            for entry in feed.entries[:20]:
                article = self._parse_entry(entry)
                if article:
                    articles.append(article)
            
            logger.info(f"微博热搜: 抓取到 {len(articles)} 条")
            return articles
            
        except Exception as e:
            logger.error(f"微博热搜抓取失败: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[NewsArticle]:
        """解析单条热搜"""
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            
            if not title or not link:
                return None
            
            article_id = self.generate_id(link)
            published_at = self._parse_date(entry.get('published', ''))
            content = entry.get('description', title)
            
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='热搜',
                priority=8,
                tags=['热搜', '微博'],
                credibility_score=0.70
            )
            
        except Exception as e:
            logger.error(f"解析微博热搜失败: {e}")
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
