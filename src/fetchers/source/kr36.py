"""
36氪新闻抓取器

抓取 36氪 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List

import feedparser

from src.fetchers.base import BaseFetcher
from src.utils.helpers import clean_html
from src.utils.logger import logger


class Kr36Fetcher(BaseFetcher):
    """36氪新闻抓取器"""

    RSS_FEEDS = {
        'top': 'https://36kr.com/feed',
    }

    def __init__(self):
        super().__init__(
            source_name="36氪",
            base_url="https://36kr.com",
            default_delay=1.0,
            language="zh"
        )

    async def fetch(self) -> List[Dict]:
        """
        抓取 36氪 新闻

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
                    'title_zh': entry.get('title', '').strip(),
                    'url': entry.get('link', '').strip(),
                    'content': content,
                    'content_zh': content,
                    'published_at': published_at,
                    'category': self._map_category(category),
                    'priority': 6,
                    'tags': self._extract_tags(entry),
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
            'top': '科技',
        }
        return category_map.get(rss_category, '科技')

    def _extract_tags(self, entry) -> List[str]:
        """
        从 RSS 条目中提取标签

        Args:
            entry: RSS 条目

        Returns:
            标签列表
        """
        tags = []

        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term'):
                    tags.append(tag.term)

        return tags[:5]  # 限制标签数量
