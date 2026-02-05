"""
半岛电视台新闻抓取器

抓取 Al Jazeera 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class AlJazeeraFetcher(BaseFetcher):
    """半岛电视台新闻抓取器"""
    
    RSS_FEEDS = {
        'top': 'https://www.aljazeera.com/xml/rss/all.xml',
    }
    
    def __init__(self):
        super().__init__(
            source_name="Al Jazeera",
            base_url="https://www.aljazeera.com",
            default_delay=1.0
        )
    
    def fetch(self) -> List[Dict]:
        """抓取半岛电视台新闻"""
        all_articles = []
        
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f"[{self.source_name}] RSS 解析警告 ({category}): {feed.bozo_exception}")
                
                articles = self.parse(feed, category)
                all_articles.extend(articles)
                
            except Exception as e:
                logger.error(f"[{self.source_name}] 抓取 {category} 分类时出错: {e}", exc_info=True)
        
        max_news = self.settings.max_news_per_source
        if len(all_articles) > max_news:
            all_articles = all_articles[:max_news]
        
        return all_articles
    
    def parse(self, feed, category: str) -> List[Dict]:
        """解析 RSS"""
        articles = []
        for entry in feed.entries:
            try:
                published_at = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])
                
                content = ''
                if hasattr(entry, 'summary'):
                    content = clean_html(entry.summary)
                elif hasattr(entry, 'description'):
                    content = clean_html(entry.description)
                
                article = {
                    'title': entry.get('title', '').strip(),
                    'url': entry.get('link', '').strip(),
                    'content': content,
                    'published_at': published_at,
                    'category': '国际', # 半岛主要是国际新闻
                    'priority': 7,
                    'tags': [],
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"[{self.source_name}] 解析条目时出错: {e}", exc_info=True)
        return articles
