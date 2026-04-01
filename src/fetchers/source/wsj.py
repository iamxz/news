"""
WSJ 新闻抓取器

抓取 Wall Street Journal 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class WSJFetcher(BaseFetcher):
    """WSJ 新闻抓取器"""

    RSS_FEEDS = {
        'world': 'https://feeds.content.dowjones.io/public/rss/RSSWorldNews',
        'markets': 'https://feeds.content.dowjones.io/public/rss/RSSMarketsMain',
        'us_news': 'https://feeds.content.dowjones.io/public/rss/RSSUSnews',
        'technology': 'https://feeds.content.dowjones.io/public/rss/RSSWSJD',
        'business': 'https://feeds.content.dowjones.io/public/rss/WSJcomUSBusiness',
        'opinion': 'https://feeds.content.dowjones.io/public/rss/RSSOpinion',
        'economy': 'https://feeds.content.dowjones.io/public/rss/socialeconomyfeed',
        'politics': 'https://feeds.content.dowjones.io/public/rss/socialpoliticsfeed',
    }

    def __init__(self):
        super().__init__(
            source_name="Wall Street Journal",
            base_url="https://www.wsj.com",
            default_delay=1.0,
            language="en"
        )

    async def fetch(self) -> List[Dict]:
        """
        抓取 WSJ 新闻

        Returns:
            新闻列表
        """
        all_articles = []

        for category, feed_url in self.RSS_FEEDS.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 分类...")

                feed = self._parse_feed(feed_url)

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
                    'tags': [],
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
            'world': '国际',
            'markets': '市场',
            'us_news': '美国新闻',
            'technology': '科技',
            'business': '商业',
            'opinion': '观点',
            'economy': '经济',
            'politics': '政治',
        }
        return category_map.get(rss_category, '综合')
