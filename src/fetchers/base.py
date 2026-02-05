"""
抓取器基类

所有新闻源抓取器的基类
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import time

import requests
from bs4 import BeautifulSoup

from src.utils.config import get_settings
from src.utils.helpers import generate_id, is_valid_url
from src.utils.logger import logger
from src.utils.robots import robots_checker


class BaseFetcher(ABC):
    """新闻抓取器基类"""
    
    def __init__(self, source_name: str, base_url: str, default_delay: float = 2.0):
        """
        初始化抓取器
        
        Args:
            source_name: 新闻源名称
            base_url: 基础 URL
            default_delay: 默认请求延迟（秒）
        """
        self.source_name = source_name
        self.base_url = base_url
        self.default_delay = default_delay
        self.settings = get_settings()
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """创建 HTTP 会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.settings.user_agent
        })
        
        # 设置代理
        if self.settings.http_proxy or self.settings.https_proxy:
            session.proxies = {
                'http': self.settings.http_proxy,
                'https': self.settings.https_proxy
            }
        
        return session
    
    def _respect_robots_txt(self, url: str) -> bool:
        """
        检查 robots.txt 是否允许抓取
        
        Args:
            url: 要检查的 URL
        
        Returns:
            是否允许抓取
        """
        return robots_checker.can_fetch(url, self.settings.user_agent)
    
    def _get_delay(self, url: str) -> float:
        """
        获取抓取延迟时间
        
        Args:
            url: URL
        
        Returns:
            延迟秒数
        """
        crawl_delay = robots_checker.get_crawl_delay(url, self.settings.user_agent)
        return crawl_delay if crawl_delay is not None else self.default_delay
    
    def _make_request(self, url: str, method: str = 'GET', check_robots: bool = True, **kwargs) -> Optional[requests.Response]:
        """
        发起 HTTP 请求
        
        Args:
            url: 请求 URL
            method: HTTP 方法
            check_robots: 是否检查 robots.txt（API 请求应设为 False）
            **kwargs: 其他请求参数
        
        Returns:
            响应对象，失败则返回 None
        """
        if check_robots and not self._respect_robots_txt(url):
            logger.warning(f"[{self.source_name}] robots.txt 禁止访问: {url}")
            return None
        
        try:
            # 等待延迟
            delay = self._get_delay(url)
            logger.debug(f"[{self.source_name}] 等待 {delay} 秒后请求: {url}")
            time.sleep(delay)
            
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            
            logger.info(f"[{self.source_name}] 成功请求: {url}")
            return response
            
        except requests.RequestException as e:
            logger.error(f"[{self.source_name}] 请求失败 ({url}): {e}")
            return None
    
    @abstractmethod
    def fetch(self) -> List[Dict]:
        """
        抓取新闻（需要子类实现）
        
        Returns:
            新闻列表
        """
        pass
    
    @abstractmethod
    def parse(self, raw_data) -> List[Dict]:
        """
        解析原始数据（需要子类实现）
        
        Args:
            raw_data: 原始数据
        
        Returns:
            解析后的新闻列表
        """
        pass
    
    def normalize_article(self, article: Dict) -> Dict:
        """
        标准化新闻数据格式
        
        Args:
            article: 原始新闻数据
        
        Returns:
            标准化后的新闻数据
        """
        # 生成唯一 ID
        if 'id' not in article:
            id_source = f"{article.get('url', '')}{article.get('title', '')}"
            article['id'] = generate_id(id_source)
        
        # 确保必需字段存在
        article.setdefault('source', self.source_name)
        article.setdefault('title', '')
        article.setdefault('title_zh', '')
        article.setdefault('content', '')
        article.setdefault('content_zh', '')
        article.setdefault('url', '')
        article.setdefault('published_at', datetime.now())
        article.setdefault('category', 'general')
        article.setdefault('priority', 5)
        article.setdefault('tags', [])
        
        # 验证字段
        article.setdefault('credibility_score', 0.0)
        article.setdefault('fact_checked', False)
        article.setdefault('cross_references', 0)
        article.setdefault('verification_labels', [])
        article.setdefault('warnings', [])
        
        return article
    
    def validate_article(self, article: Dict) -> bool:
        """
        验证新闻数据的有效性
        
        Args:
            article: 新闻数据
        
        Returns:
            是否有效
        """
        # 检查必需字段
        if not article.get('title'):
            logger.warning(f"[{self.source_name}] 新闻缺少标题")
            return False
        
        if not article.get('url') or not is_valid_url(article['url']):
            logger.warning(f"[{self.source_name}] 新闻 URL 无效: {article.get('url')}")
            return False
        
        return True
    
    def run(self) -> List[Dict]:
        """
        运行抓取器
        
        Returns:
            标准化后的新闻列表
        """
        logger.info(f"[{self.source_name}] 开始抓取新闻...")
        
        try:
            # 抓取原始数据
            raw_articles = self.fetch()
            
            if not raw_articles:
                logger.warning(f"[{self.source_name}] 未抓取到任何新闻")
                return []
            
            # 标准化和验证
            valid_articles = []
            for article in raw_articles:
                article = self.normalize_article(article)
                if self.validate_article(article):
                    valid_articles.append(article)
            
            logger.info(
                f"[{self.source_name}] 成功抓取 {len(valid_articles)}/{len(raw_articles)} 篇新闻"
            )
            return valid_articles
            
        except Exception as e:
            logger.error(f"[{self.source_name}] 抓取过程出错: {e}", exc_info=True)
            return []
