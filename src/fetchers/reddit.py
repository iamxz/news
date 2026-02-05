"""
Reddit 新闻抓取器

抓取 Reddit r/worldnews 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class RedditFetcher(BaseFetcher):
    """Reddit 新闻抓取器"""
    
    RSS_FEEDS = {
        'world': 'https://www.reddit.com/r/worldnews/.rss',
        'technology': 'https://www.reddit.com/r/technology/.rss',
    }
    
    def __init__(self):
        super().__init__(
            source_name="Reddit",
            base_url="https://www.reddit.com",
            default_delay=2.0
        )
    
    def fetch(self) -> List[Dict]:
        all_articles = []
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")
                
                feed = feedparser.parse(feed_url, agent=self.settings.user_agent)
                
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
                elif hasattr(entry, 'content'):
                    content = clean_html(entry.content[0].value)
                
                article = {
                    'title': entry.get('title', '').strip(),
                    'url': entry.get('link', '').strip(),
                    'content': content,
                    'published_at': published_at,
                    'category': self._map_category(category),
                    'priority': 5, # 社交媒体优先级较低
                    'tags': [],
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"[{self.source_name}] 解析条目时出错: {e}", exc_info=True)
        return articles
    
    def _map_category(self, rss_category: str) -> str:
        if rss_category == 'technology':
            return '科技'
        return '国际'
