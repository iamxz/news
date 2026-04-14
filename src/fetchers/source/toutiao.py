"""
今日头条热搜抓取器

直接从今日头条官网抓取热搜数据
"""
import hashlib
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from src.fetchers.base import BaseFetcher
from src.storage.models import NewsArticle
from src.utils.logger import logger


class ToutiaoFetcher(BaseFetcher):
    """今日头条热搜抓取器"""

    def __init__(self):
        super().__init__('今日头条', 'https://www.toutiao.com', 2.0, 'zh')
        # 今日头条热搜 API
        self.hotsearch_api = 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo00f01IvTdDAAAIDCuEaCcTJOkDCL93CAAEtXNzCQstAKkzGzG9aN2KkmR06pScDy9w69-ttGUk79nqJplkj6qh.7W.x7Vv-cOfAiSrrFDwNh6fsI.QwT3RxreRjsvzoVMvSalNrm7c'

    async def fetch(self) -> List[NewsArticle]:
        """抓取头条热搜"""
        try:
            logger.info(f"开始抓取今日头条热搜")

            # 发送请求获取 API 数据
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'Referer': 'https://www.toutiao.com/'
            }

            response = self._make_request(self.hotsearch_api, headers=headers)
            if not response:
                logger.error("今日头条热搜 API 请求失败")
                return []

            # 解析 JSON 数据
            try:
                import json
                data = json.loads(response.text)

                # 打印数据结构，以便了解实际结构
                logger.info(f"API 响应数据结构: {list(data.keys())}")
                if 'data' in data:
                    if isinstance(data['data'], dict):
                        logger.info(f"data 字段结构: {list(data['data'].keys())}")
                    else:
                        logger.info(
                            f"data 字段类型: {type(data['data'])}，长度: {len(data['data']) if hasattr(data['data'], '__len__') else 'N/A'}")

                # 尝试不同的路径查找热搜数据
                hot_list = None

                # 首先检查 data 字段是否直接是列表
                if 'data' in data and isinstance(data['data'], list):
                    hot_list = data['data']
                    logger.info(f"data 字段直接是列表，找到 {len(hot_list)} 条热搜")
                else:
                    # 尝试不同的路径
                    search_paths = [
                        ['data', 'hotList'],
                        ['hotList'],
                        ['data', 'list'],
                        ['list'],
                        ['data', 'items'],
                        ['items'],
                        ['data', 'hot_board'],
                        ['hot_board'],
                        ['data', 'hot'],
                        ['hot']
                    ]

                    for path in search_paths:
                        current = data
                        for key in path:
                            if isinstance(current, dict) and key in current:
                                current = current[key]
                            else:
                                break
                        else:
                            if isinstance(current, list) and len(current) > 0:
                                hot_list = current
                                logger.info(
                                    f"从路径 {path} 中找到 {len(hot_list)} 条热搜")
                                break

                if hot_list:
                    articles = []
                    for item in hot_list:
                        # 打印第一条数据的结构，以便了解字段名
                        if not articles:
                            logger.info(f"热搜数据结构: {list(item.keys())}")

                        # 提取热搜信息
                        # 支持大小写不同的字段名
                        title = item.get('title', '').strip(
                        ) or item.get('Title', '').strip()
                        url = item.get('url', '') or item.get('Url', '')
                        hot_score = item.get(
                            'hotValue', '') or item.get('HotValue', '')

                        # 尝试其他可能的字段名
                        if not title:
                            title = item.get('name', '').strip(
                            ) or item.get('Name', '').strip()
                        if not url:
                            url = item.get('link', '') or item.get('Link', '')
                        if not hot_score:
                            hot_score = item.get(
                                'hot', '') or item.get('Hot', '')

                        if title and url:
                            # 处理相对链接
                            if not url.startswith('http'):
                                url = self.base_url + url

                            # 创建新闻条目
                            article_id = self.generate_id(url)
                            published_at = datetime.now()
                            content = f"热度: {hot_score}"

                            article = NewsArticle(
                                id=article_id,
                                title=title,
                                content=content,
                                source=self.source_name,
                                url=url,
                                published_at=published_at,
                                category='热搜',
                                priority=8,
                                tags=['热搜', '头条']
                            )
                            articles.append(article)

                    logger.info(f"今日头条: 抓取到 {len(articles)} 条热搜")
                    return articles
                else:
                    logger.error("API 响应数据结构不正确，未找到热搜数据")
                    return []

            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}")
                return []

        except Exception as e:
            logger.error(f"今日头条抓取失败: {e}", exc_info=True)
            return []

    def _parse_item(self, item) -> Optional[NewsArticle]:
        """解析单条热搜"""
        try:
            # 提取标题
            title = ''

            # 尝试不同的标题选择器
            title_elem = item.select_one('.title')
            if not title_elem:
                title_elem = item.select_one('.hot-title')
            if not title_elem:
                title_elem = item.select_one('a')

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

            if not link:
                # 如果还是没找到链接，使用头条搜索链接
                link = f"https://www.toutiao.com/search/?keyword={title}"

            # 处理相对链接
            if link and not link.startswith('http'):
                link = self.base_url + link

            # 提取热度
            heat = ''

            # 尝试不同的热度选择器
            heat_elem = item.select_one('.hot-value')
            if not heat_elem:
                heat_elem = item.select_one('.heat')
            if not heat_elem:
                heat_elem = item.select_one('.hot-score')

            if heat_elem:
                heat = heat_elem.text.strip()

            # 构建内容
            content = f"热度: {heat}"

            article_id = self.generate_id(link)
            published_at = datetime.now()  # 头条热搜没有具体时间，使用当前时间

            return NewsArticle(
                id=article_id,
                title=title,
                content=content,
                source=self.source_name,
                url=link,
                published_at=published_at,
                category='热搜',
                priority=8,
                tags=['热搜', '头条']
            )

        except Exception as e:
            logger.error(f"解析头条热搜失败: {e}", exc_info=True)
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
