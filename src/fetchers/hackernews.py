"""
Hacker News 抓取器

使用 Hacker News 官方 API 抓取热点科技新闻
"""
from datetime import datetime
from typing import Dict, List
import time

from src.fetchers.base import BaseFetcher
from src.utils.logger import logger


class HackerNewsFetcher(BaseFetcher):
    """Hacker News 抓取器"""
    
    API_BASE = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self):
        super().__init__(
            source_name="Hacker News",
            base_url="https://news.ycombinator.com",
            default_delay=0.5  # API 可以更快
        )
    
    def fetch(self) -> List[Dict]:
        """
        抓取 Hacker News 热点新闻
        
        Returns:
            新闻列表
        """
        try:
            # 获取热点新闻 ID 列表（API 不需要检查 robots.txt）
            response = self._make_request(f"{self.API_BASE}/topstories.json", check_robots=False)
            if not response:
                return []
            
            story_ids = response.json()
            
            # 限制数量
            max_stories = min(self.settings.max_news_per_source, 30)
            story_ids = story_ids[:max_stories]
            
            logger.info(f"[{self.source_name}] 获取到 {len(story_ids)} 个故事 ID")
            
            # 获取每个故事的详细信息
            articles = []
            for story_id in story_ids:
                article = self._fetch_story(story_id)
                if article:
                    articles.append(article)
                time.sleep(0.1)  # 轻微延迟避免过载
            
            return self.parse(articles)
            
        except Exception as e:
            logger.error(f"[{self.source_name}] 抓取失败: {e}", exc_info=True)
            return []
    
    def _fetch_story(self, story_id: int) -> Dict:
        """
        获取单个故事的详细信息
        
        Args:
            story_id: 故事 ID
        
        Returns:
            故事数据
        """
        try:
            response = self._make_request(f"{self.API_BASE}/item/{story_id}.json", check_robots=False)
            if not response:
                return None
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"[{self.source_name}] 获取故事 {story_id} 失败: {e}")
            return None
    
    def parse(self, raw_data: List[Dict]) -> List[Dict]:
        """
        解析 Hacker News API 数据
        
        Args:
            raw_data: API 返回的数据列表
        
        Returns:
            解析后的新闻列表
        """
        articles = []
        
        for story in raw_data:
            if not story:
                continue
            
            try:
                # 只处理有 URL 的故事
                url = story.get('url')
                if not url:
                    # 如果没有外部链接，使用 HN 讨论页面
                    story_id = story.get('id')
                    url = f"https://news.ycombinator.com/item?id={story_id}"
                
                # 解析时间
                timestamp = story.get('time', 0)
                published_at = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
                
                # 构建内容
                content = story.get('text', '')
                if not content:
                    # 如果没有内容，使用标题作为内容
                    content = f"HN 积分: {story.get('score', 0)} | 评论: {story.get('descendants', 0)}"
                
                article = {
                    'title': story.get('title', '').strip(),
                    'url': url,
                    'content': content,
                    'published_at': published_at,
                    'category': '科技',
                    'priority': self._calculate_priority(story),
                    'tags': ['hacker-news', '科技'],
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"[{self.source_name}] 解析故事时出错: {e}", exc_info=True)
        
        return articles
    
    def _calculate_priority(self, story: Dict) -> int:
        """
        根据故事的分数和评论数计算优先级
        
        Args:
            story: 故事数据
        
        Returns:
            优先级 (1-10)
        """
        score = story.get('score', 0)
        comments = story.get('descendants', 0)
        
        # 综合分数和评论数
        combined_score = score + (comments * 0.5)
        
        if combined_score >= 500:
            return 10
        elif combined_score >= 300:
            return 9
        elif combined_score >= 200:
            return 8
        elif combined_score >= 100:
            return 7
        elif combined_score >= 50:
            return 6
        else:
            return 5
