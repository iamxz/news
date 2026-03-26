"""
Linux.do 新闻抓取器
"""
from typing import Dict, List, Optional
import feedparser
from dateutil import parser as date_parser
from src.fetchers.base import BaseFetcher
from src.utils.logger import logger


class LinuxDoFetcher(BaseFetcher):
    """Linux.do 新闻抓取器"""
    
    def __init__(self):
        """初始化抓取器"""
        super().__init__(
            source_name="linuxdo",
            base_url="https://linux.do",
            default_delay=1.0,
            language="zh"
        )
        self.rss_url = "https://linux.do/latest.rss"
    
    async def fetch(self) -> List[Dict]:
        """抓取新闻"""
        try:
            # 使用 feedparser 解析 RSS 源
            feed = feedparser.parse(self.rss_url)
            articles = []
            
            for entry in feed.entries[:20]:  # 限制获取前 20 条
                article = self._parse_entry(entry)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"[{self.source_name}] 抓取失败: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[Dict]:
        """解析单个 RSS 条目"""
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            published = entry.get('published', '')
            
            if not title or not link:
                return None
            
            # 解析发布时间
            published_at = None
            if published:
                try:
                    published_at = date_parser.parse(published)
                except:
                    pass
            
            # 构建新闻对象
            article = {
                'title': title,
                'url': link,
                'published_at': published_at
            }
            
            return article
            
        except Exception as e:
            logger.error(f"[{self.source_name}] 解析条目失败: {e}")
            return None
    
    def parse(self, raw_data) -> List[Dict]:
        """解析原始数据（未使用，因为使用 RSS）"""
        return []