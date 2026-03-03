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
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://passport.weibo.com/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
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
            
            # 保存页面内容以便分析
            with open('weibo_hot.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("已保存微博热搜页面到 weibo_hot.html")
            
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
            
            for item in hot_list:
                article = self._parse_item(item)
                if article:
                    articles.append(article)
            
            # 如果还是没找到，使用备用方案 - 提取所有链接
            if not articles:
                logger.info("未找到热搜列表，使用备用方案提取链接")
                all_links = soup.find_all('a')
                logger.info(f"找到 {len(all_links)} 个链接")
                
                seen_titles = set()
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
                        # 构建完整链接
                        if not href.startswith('http'):
                            href = f"https://s.weibo.com{href}"
                        
                        # 生成 ID
                        article_id = self.generate_id(href)
                        
                        # 创建新闻对象
                        article = NewsArticle(
                            id=article_id,
                            title=text,
                            content=f"来源: 微博热搜",
                            source=self.source_name,
                            url=href,
                            published_at=datetime.now(),
                            category='热搜',
                            priority=8,
                            tags=['热搜', '微博'],
                            credibility_score=0.70
                        )
                        articles.append(article)
            
        except Exception as e:
            logger.error(f"解析微博热搜 HTML 失败: {e}")
        
        return articles
    
    def _parse_item(self, item) -> Optional[NewsArticle]:
        """解析单条热搜项"""
        try:
            # 提取排名
            rank_elem = item.select_one('td.td-01.ranktop')
            if not rank_elem:
                # 尝试其他可能的排名元素
                rank_elem = item.select_one('td.td-01')
                if not rank_elem:
                    return None
            
            rank = rank_elem.text.strip()
            
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
            content = f"排名: {rank} | 热度: {heat}"
            
            # 生成 ID
            article_id = self.generate_id(full_link)
            
            # 创建新闻对象
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=full_link,
                published_at=datetime.now(),
                category='热搜',
                priority=8,
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
