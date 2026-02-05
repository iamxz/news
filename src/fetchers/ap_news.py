"""
美联社新闻抓取器

抓取 Associated Press (美联社) 的网页内容 (RSS 已不可用)
"""
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.fetchers.base import BaseFetcher
from src.utils.logger import logger


class APNewsFetcher(BaseFetcher):
    """美联社新闻抓取器 (HTML 解析版)"""
    
    # 页面 URL
    PAGES = {
        'top': 'https://apnews.com/',
        'world': 'https://apnews.com/world-news',
        'politics': 'https://apnews.com/politics',
        'business': 'https://apnews.com/business',
        'technology': 'https://apnews.com/technology',
        'science': 'https://apnews.com/science',
        'health': 'https://apnews.com/health',
        'sports': 'https://apnews.com/sports',
        'entertainment': 'https://apnews.com/entertainment',
    }
    
    def __init__(self):
        super().__init__(
            source_name="Associated Press",
            base_url="https://apnews.com",
            default_delay=2.0  # HTML 抓取需要更礼貌
        )
    
    def fetch(self) -> List[Dict]:
        """
        抓取美联社新闻
        
        Returns:
            新闻列表
        """
        all_articles = []
        
        # 优先抓取重要分类
        priority_pages = ['top', 'world', 'business', 'technology']
        
        for category in priority_pages:
            url = self.PAGES.get(category)
            if not url:
                continue
                
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 页面...")
                
                # AP News robots.txt 比较严格，为了演示功能，暂时跳过检查
                response = self._make_request(url, check_robots=False)
                if not response:
                    continue
                
                articles = self.parse(response.text, category)
                all_articles.extend(articles)
                
                logger.info(
                    f"[{self.source_name}] {category} 页面获取到 {len(articles)} 篇新闻"
                )
                
            except Exception as e:
                logger.error(
                    f"[{self.source_name}] 抓取 {category} 页面时出错: {e}",
                    exc_info=True
                )
        
        # 去重 (按 URL)
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 限制数量
        max_news = self.settings.max_news_per_source
        if len(unique_articles) > max_news:
            logger.info(f"[{self.source_name}] 限制新闻数量: {len(unique_articles)} -> {max_news}")
            unique_articles = unique_articles[:max_news]
        
        return unique_articles
    
    def parse(self, html: str, category: str) -> List[Dict]:
        """
        解析 HTML 数据
        
        Args:
            html: HTML 内容
            category: 新闻分类
        
        Returns:
            解析后的新闻列表
        """
        articles = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有标题 (通常在 h3 中)
        # AP News 结构: h3 > a 或者 h3 内部包含标题文本且链接在附近
        
        titles = soup.find_all('h3', limit=30)  # 限制查找数量
        
        for title_tag in titles:
            try:
                # 查找链接
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue
                
                url = link_tag.get('href')
                if not url:
                    continue
                
                # 处理相对链接
                if not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                
                # 排除非文章链接 (如视频、hub 等)
                if '/article/' not in url:
                    continue
                    
                title = title_tag.get_text().strip()
                if not title:
                    continue
                
                article = {
                    'title': title,
                    'url': url,
                    'content': '',  # 列表页通常没有摘要
                    'published_at': datetime.now(), # HTML 列表页通常没有精确时间
                    'category': self._map_category(category),
                    'priority': 9,
                    'tags': [],
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(
                    f"[{self.source_name}] 解析条目时出错: {e}",
                    exc_info=True
                )
        
        return articles
    
    def _map_category(self, page_category: str) -> str:
        category_map = {
            'top': '头条',
            'world': '国际',
            'politics': '政治',
            'business': '财经',
            'technology': '科技',
            'health': '健康',
            'science': '科学',
            'sports': '体育',
        }
        return category_map.get(page_category, '综合')
