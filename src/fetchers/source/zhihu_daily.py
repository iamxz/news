"""知乎日报抓取器"""
import hashlib
from datetime import datetime
from typing import List, Optional

from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class ZhihuDailyFetcher(BaseFetcher):
    """知乎日报抓取器（官方 API）"""

    def __init__(self):
        super().__init__('知乎日报', 'https://daily.zhihu.com', 2.0, 'zh')
        self.api_url = 'https://news-at.zhihu.com/api/4/news/latest'

    async def fetch(self) -> List[NewsArticle]:
        """抓取知乎日报最新文章列表"""
        try:
            response = self._make_request(self.api_url, check_robots=False)
            if not response or response.status_code != 200:
                logger.error(
                    f"知乎日报抓取失败: HTTP {response.status_code if response else 'None'}")
                return []

            data = response.json()
            top_stories = data.get('top_stories', [])
            stories = data.get('stories', [])

            if not top_stories and not stories:
                logger.warning("知乎日报: 未获取到数据或接口结构变化")
                return []

            articles = []
            seen_ids = set()

            # 优先处理置顶文章，赋予更高优先级
            for entry in top_stories:
                story_id = entry.get('id')
                if not story_id or story_id in seen_ids:
                    continue
                seen_ids.add(story_id)
                article = self._parse_entry(entry, is_top=True)
                if article:
                    articles.append(article)

            # 处理普通文章，跳过已收录的置顶文章
            for entry in stories:
                story_id = entry.get('id')
                if not story_id or story_id in seen_ids:
                    continue
                seen_ids.add(story_id)
                article = self._parse_entry(entry, is_top=False)
                if article:
                    articles.append(article)

            logger.info(f"知乎日报: 抓取到 {len(articles)} 条")
            return articles

        except Exception as e:
            logger.error(f"知乎日报抓取失败: {e}")
            return []

    def _parse_entry(self, entry: dict, is_top: bool = False) -> Optional[NewsArticle]:
        """解析单条文章"""
        title = entry.get('title', '').strip()
        story_id = entry.get('id')
        if not title or not story_id:
            return None

        url = f"https://daily.zhihu.com/story/{story_id}"
        article_id = self._generate_id(url)
        content = '知乎日报推荐' if is_top else '知乎日报'
        tags = ['知乎', '日报', '推荐'] if is_top else ['知乎', '日报']

        return NewsArticle(
            id=article_id,
            title=title,
            content=content,
            source=self.source_name,
            url=url,
            published_at=datetime.now(),
            category='日报',
            priority=9 if is_top else 5,
            tags=tags,
            credibility_score=0.9,
        )

    def parse(self, raw_data):
        return []

    def _generate_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
