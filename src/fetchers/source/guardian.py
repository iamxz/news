"""
卫报新闻抓取器

抓取 The Guardian 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class GuardianFetcher(BaseFetcher):
    """卫报新闻抓取器"""
    
    RSS_FEEDS = {
        'world': 'https://www.theguardian.com/world/rss',
        'uk': 'https://www.theguardian.com/uk-news/rss',
        'technology': 'https://www.theguardian.com/uk/technology/rss',
        'business': 'https://www.theguardian.com/uk/business/rss',
        'science': 'https://www.theguardian.com/science/rss',
    }
    
    def __init__(self):
        super().__init__(
            source_name="The Guardian",
            base_url="https://www.theguardian.com",
            default_delay=1.0
        )
    
    def fetch(self) -> List[Dict]:
        """抓取卫报新闻"""
        all_articles = []
        
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f"[{self.source_name}] RSS 解析警告 ({category}): {feed.bozo_exception}")
                
                articles = self.parse(feed, category)
                all_articles.extend(articles)
                
                logger.info(f"[{self.source_name}] {category} 分类获取到 {len(articles)} 篇新闻")
                
            except Exception as e:
                logger.error(f"[{self.source_name}] 抓取 {category} 分类时出错: {e}", exc_info=True)
        
        max_news = self.settings.max_news_per_source
        if len(all_articles) > max_news:
            logger.info(f"[{self.source_name}] 限制新闻数量: {len(all_articles)} -> {max_news}")
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
                    'category': self._map_category(category),
                    'priority': 7,
                    'tags': self._extract_tags(entry),
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"[{self.source_name}] 解析条目时出错: {e}", exc_info=True)
        return articles
    
    def _map_category(self, rss_category: str) -> str:
        category_map = {
            'world': '国际',
            'uk': '英国',
            'technology': '科技',
            'business': '财经',
            'science': '科学',
        }
        return category_map.get(rss_category, '综合')

    def _extract_tags(self, entry) -> List[str]:
        tags = []
        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term'):
                    tags.append(tag.term)
        return tags[:5]
