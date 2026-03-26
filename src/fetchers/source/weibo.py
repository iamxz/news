"""
微博热搜抓取器
"""
import hashlib
import time
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class WeiboFetcher(BaseFetcher):
    """微博热搜抓取器"""
    
    def __init__(self):
        super().__init__('微博热搜', 'https://weibo.com', 2.0)
        # 微博热搜地址
        self.hot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
        # 添加微博需要的 headers
        self.session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'referer': 'https://passport.weibo.com/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'upgrade-insecure-requests': '1'
        })
        # 添加必要的 cookies
        self.session.cookies.update({
            'SUB': '_2AkMe-sOgf8NxqwFRm_gdxWjhZY9wzQ3EieKopjJ7JRMxHRl-yT9xqksotRB6NXrtT8-NIvVRXD0UJF7xQvC2cvJC_aSQ',
            'SUBP': '0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5HwbYYPjGVwnKYVUX64nf4',
            '_s_tentry': 'passport.weibo.com',
            'Apache': '1353565791719.028.1772506264261',
            'SINAGLOBAL': '1353565791719.028.1772506264261',
            'ULV': '1772506264262:1:1:1:1353565791719.028.1772506264261:'
        })
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取微博热搜"""
        try:
            # 使用父类的 _make_request 方法
            response = self._make_request(self.hot_url, check_robots=False)
            if not response:
                logger.error("微博热搜页面请求失败")
                return []
            
            # 尝试再次请求，使用同一个 session
            response = self._make_request(self.hot_url, check_robots=False)
            if not response:
                logger.error("微博热搜页面二次请求失败")
                return []
            
            # 解析 HTML
            articles = self._parse_html(response.text)
            
            logger.info(f"微博热搜: 抓取到 {len(articles)} 条")
            return articles
            
        except Exception as e:
            logger.error(f"微博热搜抓取失败: {e}")
            return []
    
    def _parse_html(self, html: str) -> List[NewsArticle]:
        """解析微博热搜 HTML"""
        articles = []
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # 查找热搜列表 - 尝试多种选择器
            hot_list = []
            
            # 尝试原始选择器
            hot_list = soup.select('#pl_top_realtimehot table tbody tr')
            
            # 如果没找到，尝试其他可能的选择器
            if not hot_list:
                hot_list = soup.select('table tbody tr')
            
            # 如果还是没找到，尝试另一种结构
            if not hot_list:
                hot_list = soup.select('.hot_list tr')
            
            # 如果还是没找到，尝试更通用的选择器
            if not hot_list:
                hot_list = soup.find_all('tr')
            
            logger.info(f"找到 {len(hot_list)} 个热搜项")
            
            # 解析热搜列表
            for i, item in enumerate(hot_list[:50]):  # 限制前50条
                article = self._parse_item(item)
                if article:
                    # 根据索引设置优先级，索引越小优先级越高
                    article.priority = 100 - i  # 使用 100 作为基础，确保优先级为正数
                    logger.info(f"微博热搜第 {i+1} 条: {article.title[:20]}... 优先级: {article.priority}")
                    articles.append(article)
            
            # 如果还是没找到，使用备用方案 - 提取所有链接
            if not articles:
                logger.info("未找到热搜列表，使用备用方案提取链接")
                all_links = soup.find_all('a')
                logger.info(f"找到 {len(all_links)} 个链接")
                
                seen_titles = set()
                filtered_links = []
                
                # 先过滤链接
                for link in all_links[:100]:
                    text = link.text.strip()
                    href = link.get('href', '')
                    
                    # 过滤条件
                    if (text and len(text) > 4 and len(text) < 60 and 
                        text not in seen_titles and
                        not any(keyword in text for keyword in ['首页', '登录', '注册', '搜索', '更多', '关于', '联系我们']) and
                        href and not href.startswith('javascript:') and
                        ('weibo.com' in href or 's.weibo.com' in href)):
                        
                        seen_titles.add(text)
                        filtered_links.append((text, href))
                
                # 然后根据过滤后的顺序设置优先级
                for i, (text, href) in enumerate(filtered_links[:50]):  # 限制前50条
                    # 构建完整链接
                    if not href.startswith('http'):
                        href = f"https://s.weibo.com{href}"
                    
                    # 生成 ID
                    article_id = self.generate_id(href)
                    
                    # 根据索引设置优先级，索引越小优先级越高
                    priority = 100 - i  # 使用 100 作为基础，确保优先级为正数
                    
                    # 创建新闻对象
                    article = NewsArticle(
                        id=article_id,
                        title=text,
                        content=f"来源: 微博热搜",
                        source=self.source_name,
                        url=href,
                        published_at=datetime.now(),
                        category='热搜',
                        priority=priority,
                        tags=['热搜', '微博'],
                        credibility_score=0.70
                    )
                    logger.info(f"微博热搜(备用)第 {i+1} 条: {text[:20]}... 优先级: {priority}")
                    articles.append(article)
            
        except Exception as e:
            logger.error(f"解析微博热搜 HTML 失败: {e}")
        
        return articles
    
    def _parse_item(self, item) -> Optional[NewsArticle]:
        """解析单条热搜项"""
        try:
            # 提取标题和链接
            title_elem = item.select_one('td.td-02 a')
            if not title_elem:
                # 尝试其他可能的标题元素
                title_elem = item.select_one('a')
                if not title_elem:
                    return None
            
            title = title_elem.text.strip()
            link = title_elem.get('href', '')
            
            if not title or not link:
                return None
            
            # 完整链接
            if not link.startswith('http'):
                full_link = f"https://s.weibo.com{link}"
            else:
                full_link = link
            
            # 提取热度
            heat_elem = item.select_one('td.td-02 span')
            if not heat_elem:
                # 尝试其他可能的热度元素
                heat_elem = item.select_one('span')
            heat = heat_elem.text.strip() if heat_elem else ''
            
            # 构建内容
            content = f"热度: {heat}"
            
            # 生成 ID
            article_id = self.generate_id(full_link)
            
            # 创建新闻对象，优先级将在 _parse_html 中设置
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=full_link,
                published_at=datetime.now(),
                category='热搜',
                priority=8,  # 默认优先级，将在 _parse_html 中覆盖
                tags=['热搜', '微博'],
                credibility_score=0.70
            )
            
        except Exception as e:
            logger.error(f"解析微博热搜项失败: {e}")
            return None
    
    def parse(self, raw_data):
        return []
    
    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
