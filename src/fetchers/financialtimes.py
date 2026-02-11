"""
金融时报新闻抓取器

Financial Times - 全球最权威的财经新闻媒体
"""
import feedparser
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class FinancialTimesFetcher(BaseFetcher):
    """金融时报抓取器"""
    
    def __init__(self):
        super().__init__('Financial Times', 'https://example.com', 1.0)
        self.rss_url = 'https://www.ft.com/?format=rss'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取新闻"""
        try:
            logger.info(f"开始抓取 {self.source_name}")
            
            feed = feedparser.parse(self.rss_url)
            articles = []
            
            for entry in feed.entries[:20]:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"解析条目失败: {e}")
                    continue
            
            logger.info(f"{self.source_name} 抓取完成: {len(articles)} 条")
            return articles
            
        except Exception as e:
            logger.error(f"{self.source_name} 抓取失败: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[NewsArticle]:
        """解析 RSS 条目"""
        title = entry.get('title', '').strip()
        url = entry.get('link', '')
        
        if not title or not url:
            return None
        
        # 提取内容
        content = ''
        if hasattr(entry, 'summary'):
            soup = BeautifulSoup(entry.summary, 'html.parser')
            content = soup.get_text().strip()
        
        # 解析时间
        published_at = self._parse_date(entry.get('published', ''))
        
        return NewsArticle(
            id=self.generate_id(url),
            title=title,
            content=content,
            source=self.source_name,
            url=url,
            published_at=published_at,
            category='财经',
            priority=8
        )

    def parse(self, raw_data):
        """解析原始数据（兼容基类接口）"""
        return []
    
    def _parse_date(self, date_str):
        """解析日期字符串"""
        from dateutil import parser
        from datetime import datetime
        try:
            if date_str:
                return parser.parse(date_str)
        except:
            pass
        return datetime.now()
    
    def generate_id(self, url):
        """生成新闻ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()

