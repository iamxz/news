"""
TechCrunch 新闻抓取器

抓取 TechCrunch 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class TechCrunchFetcher(BaseFetcher):
    """TechCrunch 新闻抓取器"""
    
    RSS_FEEDS = {
        'top': 'https://techcrunch.com/feed/',
    }
    
    def __init__(self):
        super().__init__(
            source_name="TechCrunch",
            base_url="https://techcrunch.com",
            default_delay=1.0
        )
    
    def fetch(self) -> List[Dict]:
        all_articles = []
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f"[{self.source_name}] RSS 解析警告: {feed.bozo_exception}")
                
                articles = self.parse(feed, category)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"[{self.source_name}] 抓取失败: {e}", exc_info=True)
        
        max_news = self.settings.max_news_per_source
        if len(all_articles) > max_news:
            all_articles = all_articles[:max_news]
        return all_articles
    
    def parse(self, feed, category: str) -> List[Dict]:
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
                    'category': '科技',
                    'priority': 7,
                    'tags': self._extract_tags(entry),
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"[{self.source_name}] 解析条目时出错: {e}", exc_info=True)
        return articles

    def _extract_tags(self, entry) -> List[str]:
        tags = []
        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term'):
                    tags.append(tag.term)
        return tags[:5]
