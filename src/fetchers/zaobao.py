"""
联合早报新闻抓取器

抓取 联合早报 的网页内容
"""
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.fetchers.base import BaseFetcher
from src.utils.logger import logger


class ZaobaoFetcher(BaseFetcher):
    """联合早报新闻抓取器"""
    
    PAGES = {
        'world': 'https://www.zaobao.com.sg/realtime/world',
        'china': 'https://www.zaobao.com.sg/realtime/china',
        'singapore': 'https://www.zaobao.com.sg/realtime/singapore',
    }
    
    def __init__(self):
        super().__init__(
            source_name="联合早报",
            base_url="https://www.zaobao.com.sg",
            default_delay=2.0
        )
    
    def fetch(self) -> List[Dict]:
        all_articles = []
        for category, url in self.PAGES.items():
            try:
                logger.info(f"[{self.source_name}] 抓取 {category} 页面...")
                # 联合早报可能有反爬，且是 HTML
                response = self._make_request(url, check_robots=False)
                if not response:
                    continue
                articles = self.parse(response.text, category)
                all_articles.extend(articles)
                logger.info(f"[{self.source_name}] {category} 页面获取到 {len(articles)} 篇新闻")
            except Exception as e:
                logger.error(f"[{self.source_name}] 抓取 {category} 页面时出错: {e}", exc_info=True)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        max_news = self.settings.max_news_per_source
        if len(unique_articles) > max_news:
            unique_articles = unique_articles[:max_news]
        return unique_articles
    
    def parse(self, html: str, category: str) -> List[Dict]:
        articles = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有带有链接的 a 标签
        # 过滤包含 /realtime/ 的链接
        links = soup.find_all('a')
        for link in links:
            try:
                url = link.get('href')
                if not url or '/realtime/' not in url:
                    continue
                
                title = link.get_text().strip()
                if len(title) < 8: # 标题太短跳过
                    continue
                
                if not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                
                # 简单去重
                if any(a['url'] == url for a in articles):
                    continue

                article = {
                    'title': title,
                    'title_zh': title, # 中文源
                    'url': url,
                    'content': '',
                    'content_zh': '',
                    'published_at': datetime.now(),
                    'category': self._map_category(category),
                    'priority': 6,
                    'tags': [],
                    'translated': True,
                }
                articles.append(article)
            except Exception:
                continue
                
        return articles[:20]
    
    def _map_category(self, page_category: str) -> str:
        category_map = {
            'world': '国际',
            'china': '中国',
            'singapore': '新加坡',
        }
        return category_map.get(page_category, '综合')
