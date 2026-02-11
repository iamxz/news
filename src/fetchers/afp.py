"""
法新社（AFP）新闻抓取器

抓取 AFP 的 RSS 订阅
"""
from datetime import datetime
from typing import Dict, List
import feedparser
from src.fetchers.base import BaseFetcher
from src.utils.logger import logger


class AFPFetcher(BaseFetcher):
    """法新社新闻抓取器"""
    
    RSS_FEEDS = {
        'world': 'https://www.afp.com/en/rss',
    }
    
    def __init__(self):
        super().__init__(
            source_name="AFP",
            base_url="https://www.afp.com",
            default_delay=2.0
        )
    
    async def fetch(self) -> List[Dict]:
        """抓取 AFP 新闻"""
        articles = []
        
        for category, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:self.max_articles]:
                    article = self._parse_entry(entry, category)
                    if article:
                        articles.append(article)
                        
                logger.info(f"[AFP] 从 {category} 抓取了 {len(feed.entries[:self.max_articles])} 篇新闻")
                
            except Exception as e:
                logger.error(f"[AFP] 抓取 {category} 失败: {e}")
        
        return articles
    
    def _parse_entry(self, entry, category: str) -> Dict:
        """解析 RSS 条目"""
        try:
            published = entry.get('published_parsed')
            pub_date = datetime(*published[:6]) if published else datetime.now()
            
            return self.create_article(
                title=entry.get('title', ''),
                content=entry.get('summary', ''),
                url=entry.get('link', ''),
                published_at=pub_date,
                category=category,
                priority=9  # 通讯社高优先级
            )
        except Exception as e:
            logger.error(f"[AFP] 解析条目失败: {e}")
            return None
