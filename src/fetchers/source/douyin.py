"""抖音热榜抓取器"""
import hashlib
import json
from typing import List, Optional
from datetime import datetime
from urllib.parse import quote
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class DouyinFetcher(BaseFetcher):
    """抖音热榜抓取器 (官方接口)"""
    
    def __init__(self):
        super().__init__('抖音热榜', 'https://www.douyin.com', 2.0, 'zh')
        # 官方 Web 接口
        self.api_url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取抖音热榜"""
        try:
            # 模拟 Web 请求参数
            params = {
                'device_platform': 'webapp',
                'aid': '6383',
                'channel': 'channel_pc_web',
                'detail_list': '1',
                'source': '6'
            }
            
            headers = {
                'Referer': 'https://www.douyin.com/hot',
                'Accept': 'application/json, text/plain, */*'
            }
            
            response = self._make_request(self.api_url, params=params, headers=headers, check_robots=False)
            if not response or response.status_code != 200:
                logger.error(f"抖音热榜抓取失败: HTTP {response.status_code if response else 'None'}")
                return []
            
            data = response.json()
            word_list = data.get('data', {}).get('word_list', [])
            
            if not word_list:
                logger.warning("抖音热榜: 未获取到数据或接口结构变化")
                return []
            
            articles = []
            for rank, entry in enumerate(word_list, 1):
                article = self._parse_entry(entry, rank)
                if article:
                    articles.append(article)
            
            logger.info(f"抖音热榜: 抓取到 {len(articles)} 条")
            return articles
            
        except Exception as e:
            logger.error(f"抖音热榜抓取失败: {e}")
            return []
    
    def _parse_entry(self, entry, rank: int) -> Optional[NewsArticle]:
        """解析单条热搜"""
        try:
            word = entry.get('word', '').strip()
            if not word:
                return None
            
            # 构造跳转链接
            link = f"https://www.douyin.com/search/{quote(word)}?type=general"
            
            article_id = self.generate_id(link)
            published_at = datetime.now()
            
            # 提取热度值
            hot_value = entry.get('hot_value', 0)
            label = entry.get('label', 0) # 1: 新, 2: 荐, 3: 热, 4: 爆
            
            # 构造内容描述
            label_text = {1: ' [新]', 2: ' [荐]', 3: ' [热]', 4: ' [爆]'}.get(label, '')
            content = f"抖音热搜第 {rank} 名，热度指数: {hot_value}{label_text}"
            
            return NewsArticle(
                id=article_id,
                title=word,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='热搜',
                priority=max(1, 10 - (rank // 10)), # 根据排名降序设置优先级
                tags=['热搜', '抖音'],
                credibility_score=0.85
            )
            
        except Exception as e:
            logger.error(f"解析抖音热榜条目失败: {e}")
            return None
    
    def parse(self, raw_data):
        return []
    
    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
