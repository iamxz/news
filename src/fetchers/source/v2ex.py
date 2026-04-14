"""
V2EX 抓取器
"""
import hashlib
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class V2EXFetcher(BaseFetcher):
    """V2EX 抓取器"""
    
    def __init__(self):
        super().__init__('V2EX', 'https://www.v2ex.com', 2.0, 'zh')
        # V2EX 热点页面
        self.hot_url = 'https://www.v2ex.com/?tab=hot'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取 V2EX 热点"""
        try:
            response = self._make_request(self.hot_url)
            if not response:
                return []
            
            articles = self.parse(response.text)
            logger.info(f"V2EX: 抓取到 {len(articles)} 条热点")
            return articles
            
        except Exception as e:
            logger.error(f"V2EX 抓取失败: {e}")
            return []
    
    def parse(self, raw_data) -> List[NewsArticle]:
        """解析 V2EX 热点页面"""
        articles = []
        try:
            soup = BeautifulSoup(raw_data, 'lxml')
            
            # 查找热点帖子
            for item in soup.select('.item_title'):
                article = self._parse_item(item)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"解析 V2EX 页面失败: {e}")
            return []
    
    def _parse_item(self, item) -> Optional[NewsArticle]:
        """解析单条热点"""
        try:
            # 标题和链接
            title_elem = item.select_one('a.topic-link')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            link = title_elem.get('href', '')
            
            if not title or not link:
                return None
            
            # 完整链接
            if not link.startswith('http'):
                link = f"{self.base_url}{link}"
            
            article_id = self.generate_id(link)
            
            # 发布时间
            published_at = datetime.now()
            
            # 内容（使用标题作为内容）
            content = title
            
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='科技',
                priority=7,
                tags=['科技', 'V2EX']
            )
            
        except Exception as e:
            logger.error(f"解析 V2EX 热点失败: {e}")
            return None
    
    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
