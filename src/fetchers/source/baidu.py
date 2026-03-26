"""
百度热搜抓取器

直接从百度官网抓取热搜数据
"""
import hashlib
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class BaiduFetcher(BaseFetcher):
    """百度热搜抓取器"""
    
    def __init__(self):
        super().__init__('百度热搜', 'https://www.baidu.com', 2.0)
        # 百度热搜页面
        self.hotsearch_url = 'https://top.baidu.com/board?tab=realtime'
    
    async def fetch(self) -> List[NewsArticle]:
        """抓取百度热搜"""
        try:
            logger.info(f"开始抓取百度热搜")
            
            # 发送请求获取页面
            response = self._make_request(self.hotsearch_url, check_robots=False)
            if not response:
                logger.error("百度热搜页面请求失败")
                return []
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 查找热搜列表
            hot_items = []
            
            # 从 sanRoot 标签获取数据源
            logger.info("从 sanRoot 标签获取数据源")
            san_root = soup.find('div', id='sanRoot')
            if san_root:
                # 查找 sanRoot 内的注释
                for child in san_root.children:
                    if hasattr(child, 'string') and child.string and '//' in child.string:
                        # 提取注释中的数据
                        comment_text = child.string.strip()
                        logger.info(f"找到 sanRoot 注释，长度: {len(comment_text)}")
                        
                        # 尝试从注释中提取 JSON 数据
                        try:
                            import json
                            # 找到 JSON 数据的开始位置
                            start = comment_text.find('{')
                            end = comment_text.rfind('}') + 1
                            if start != -1 and end != -1:
                                json_str = comment_text[start:end]
                                data = json.loads(json_str)
                                
                                # 解析 JSON 数据获取热搜
                                if 'data' in data:
                                    # 尝试不同的数据结构路径
                                    # 路径 1: data -> cards -> content
                                    cards = data.get('data', {}).get('cards', [])
                                    logger.info(f"从 sanRoot 注释中解析到 {len(cards)} 个卡片")
                                    
                                    for card in cards:
                                        # 尝试不同的 content 字段名
                                        contents = card.get('content', [])
                                        if not contents:
                                            contents = card.get('items', [])
                                        if not contents:
                                            contents = card.get('list', [])
                                        
                                        logger.info(f"卡片包含 {len(contents)} 个内容项")
                                        
                                        for content in contents:
                                            # 尝试不同的链接字段名
                                            url = content.get('appUrl', '')
                                            if not url:
                                                url = content.get('url', '')
                                            if not url:
                                                url = content.get('link', '')
                                            
                                            # 尝试不同的标题字段名
                                            title = content.get('title', '').strip()
                                            if not title:
                                                title = content.get('name', '').strip()
                                            if not title:
                                                title = content.get('text', '').strip()
                                            if not title:
                                                title = content.get('desc', '').strip()[:50]  # 从描述中提取前50个字符作为标题
                                            
                                            # 如果还是没有标题，尝试从 URL 中提取
                                            if not title and url:
                                                import urllib.parse
                                                parsed_url = urllib.parse.urlparse(url)
                                                query_params = urllib.parse.parse_qs(parsed_url.query)
                                                if 'wd' in query_params:
                                                    title = query_params['wd'][0].strip()
                                            
                                            # 尝试不同的热度字段名
                                            hot_score = content.get('hotScore', '')
                                            if not hot_score:
                                                hot_score = content.get('hot', '')
                                            if not hot_score:
                                                hot_score = content.get('score', '')
                                            
                                            if title and url:
                                                # 创建一个模拟的 item 对象
                                                from bs4.element import Tag
                                                mock_item = Tag(name='div')
                                                
                                                # 创建链接元素
                                                link_elem = Tag(name='a', attrs={'href': url})
                                                link_elem.string = title
                                                mock_item.append(link_elem)
                                                
                                                # 添加热度信息
                                                if hot_score:
                                                    heat_elem = Tag(name='div', attrs={'class': 'hot-index'})
                                                    heat_elem.string = str(hot_score)
                                                    mock_item.append(heat_elem)
                                                
                                                hot_items.append(mock_item)
                                    
                                    logger.info(f"从 sanRoot 注释中解析到 {len(hot_items)} 条热搜")
                        except Exception as e:
                            logger.error(f"解析 sanRoot 注释失败: {e}", exc_info=True)
            
            # 如果 sanRoot 解析失败，使用备用方案
            if not hot_items:
                logger.info("sanRoot 解析失败，使用备用方案")
                # 查找所有包含链接的元素
                all_links = soup.find_all('a')
                logger.info(f"找到 {len(all_links)} 个链接")
                
                # 过滤出可能的热搜链接
                seen_titles = set()  # 用于去重
                
                for link in all_links[:100]:  # 增加查找范围
                    text = link.text.strip()
                    
                    # 过滤条件：
                    # 1. 文本长度在合理范围内
                    # 2. 不是导航链接
                    # 3. 不是重复的标题
                    # 4. 包含热搜相关关键词
                    if (text and len(text) > 4 and len(text) < 60 and 
                        text not in seen_titles and
                        not any(keyword in text for keyword in ['首页', '登录', '注册', '搜索', '更多', '关于', '联系我们', 'hao123']) and
                        not link.get('href', '').startswith('javascript:')):
                        
                        seen_titles.add(text)
                        # 创建一个模拟的 item 对象
                        from bs4.element import Tag
                        mock_item = Tag(name='div')
                        mock_item.append(link)
                        hot_items.append(mock_item)
                
                logger.info(f"通过链接过滤找到 {len(hot_items)} 条")
            
            # 解析找到的热搜项
            for i, item in enumerate(hot_items[:20]):  # 限制前20条
                article = self._parse_item(item)
                if article:
                    # 根据排名设置优先级，排名越高优先级越高
                    article.priority = 100 - i  # 使用 100 作为基础，确保优先级为正数
                    logger.info(f"百度热搜第 {i+1} 条: {article.title[:20]}... 优先级: {article.priority}")
                    articles.append(article)
            
            logger.info(f"百度热搜: 抓取到 {len(articles)} 条")
            return articles
            
        except Exception as e:
            logger.error(f"百度热搜抓取失败: {e}", exc_info=True)
            return []
    
    def _parse_item(self, item) -> Optional[NewsArticle]:
        """解析单条热搜"""
        try:
            # 提取标题
            title = ''
            
            # 尝试第一种方式
            title_elem = item.select_one('.title-content')
            if not title_elem:
                # 尝试第二种方式
                title_elem = item.select_one('.c-single-text-ellipsis')
            if not title_elem:
                # 尝试第三种方式
                title_elem = item.select_one('a')
            if not title_elem:
                # 尝试第四种方式
                title_elem = item.find('div', class_=lambda x: x and 'title' in x)
            
            if title_elem:
                title = title_elem.text.strip()
            
            if not title:
                return None
            
            # 提取链接
            link = ''
            
            # 尝试从 item 中直接找链接
            link_elem = item.select_one('a')
            if link_elem:
                link = link_elem.get('href', '')
            
            # 如果没找到，尝试从子元素中找
            if not link:
                link_elem = item.find('a')
                if link_elem:
                    link = link_elem.get('href', '')
            
            if not link:
                # 如果还是没找到链接，使用百度搜索链接
                link = f"https://www.baidu.com/s?wd={title}"
            
            # 处理相对链接
            if link and not link.startswith('http'):
                link = self.base_url + link
            
            # 提取热度
            heat = ''
            
            # 尝试第一种方式
            heat_elem = item.select_one('.hot-index')
            if not heat_elem:
                # 尝试第二种方式
                heat_elem = item.find('div', class_=lambda x: x and 'hot' in x and 'index' in x)
            
            if heat_elem:
                heat = heat_elem.text.strip()
            
            # 构建内容
            content = f"热度: {heat}"
            
            article_id = self.generate_id(link)
            published_at = datetime.now()  # 百度热搜没有具体时间，使用当前时间
            
            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='热搜',
                priority=8,
                tags=['热搜', '百度'],
                credibility_score=0.75
            )
            
        except Exception as e:
            logger.error(f"解析百度热搜失败: {e}", exc_info=True)
            return None
    
    def parse(self, raw_data):
        return []
    
    def _parse_date(self, date_str):
        try:
            return date_parser.parse(date_str)
        except:
            return datetime.now()
    
    def generate_id(self, url):
        return hashlib.md5(url.encode()).hexdigest()
