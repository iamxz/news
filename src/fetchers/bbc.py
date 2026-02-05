"""
BBC 新闻抓取器

抓取 BBC News 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class BBCFetcher(BaseFetcher):
    """BBC 新闻抓取器"""
    
    RSS_FEEDS = {
        'top': 'http://feeds.bbci.co.uk/news/rss.xml',
        'world': 'http://feeds.bbci.co.uk/news/world/rss.xml',
        'technology': 'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'business': 'http://feeds.bbci.co.uk/news/business/rss.xml',
        'science_and_environment': 'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        'entertainment_and_arts': 'http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
        'health': 'http://feeds.bbci.co.uk/news/health/rss.xml',
    }
    
    def __init__(self):
        super().__init__(
            source_name="BBC News",
            base_url="https://www.bbc.com/news",
            default_delay=1.0
        )
    
    def fetch(self) -> List[Dict]:
        """
        抓取 BBC 新闻
        
        Returns:
            新闻列表
        """
        all_articles = []
        
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")
                
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(
                        f"[{self.source_name}] RSS 解析警告 ({category}): {feed.bozo_exception}"
                    )
                
                articles = self.parse(feed, category)
                all_articles.extend(articles)
                
                logger.info(
                    f"[{self.source_name}] {category} 分类获取到 {len(articles)} 篇新闻"
                )
                
            except Exception as e:
                logger.error(
                    f"[{self.source_name}] 抓取 {category} 分类时出错: {e}",
                    exc_info=True
                )
        
        # 限制数量
        max_news = self.settings.max_news_per_source
        if len(all_articles) > max_news:
            logger.info(f"[{self.source_name}] 限制新闻数量: {len(all_articles)} -> {max_news}")
            all_articles = all_articles[:max_news]
        
        return all_articles
    
    def parse(self, feed, category: str) -> List[Dict]:
        """
        解析 RSS feed 数据
        
        Args:
            feed: feedparser 返回的 feed 对象
            category: 新闻分类
        
        Returns:
            解析后的新闻列表
        """
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
                    'priority': 8,
                    'tags': [], # BBC RSS 通常不带 tags
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(
                    f"[{self.source_name}] 解析条目时出错: {e}",
                    exc_info=True
                )
        
        return articles
    
    def _map_category(self, rss_category: str) -> str:
        category_map = {
            'top': '头条',
            'world': '国际',
            'technology': '科技',
            'business': '财经',
            'science_and_environment': '科学',
            'entertainment_and_arts': '娱乐',
            'health': '健康',
        }
        return category_map.get(rss_category, '综合')
