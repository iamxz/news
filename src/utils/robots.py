"""
robots.txt 解析模块

解析和遵守网站的 robots.txt 规则
"""
import urllib.robotparser
from typing import Optional
from urllib.parse import urljoin

from src.utils.logger import logger


class RobotsChecker:
    """robots.txt 检查器"""
    
    def __init__(self):
        self._parsers = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        检查是否允许抓取指定 URL
        
        Args:
            url: 要检查的 URL
            user_agent: User-Agent 字符串
        
        Returns:
            是否允许抓取
        """
        try:
            # 获取域名的 robots.txt URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(base_url, "/robots.txt")
            
            # 如果还没有解析过这个域名的 robots.txt，解析它
            if robots_url not in self._parsers:
                parser = urllib.robotparser.RobotFileParser()
                parser.set_url(robots_url)
                try:
                    parser.read()
                    self._parsers[robots_url] = parser
                    logger.debug(f"已加载 robots.txt: {robots_url}")
                except Exception as e:
                    logger.warning(f"无法读取 robots.txt ({robots_url}): {e}")
                    # 如果无法读取 robots.txt，默认允许抓取
                    return True
            
            parser = self._parsers[robots_url]
            can_fetch = parser.can_fetch(user_agent, url)
            
            if not can_fetch:
                logger.warning(f"robots.txt 禁止抓取: {url}")
            
            return can_fetch
            
        except Exception as e:
            logger.error(f"检查 robots.txt 时出错: {e}")
            # 出错时默认允许抓取
            return True
    
    def get_crawl_delay(self, url: str, user_agent: str = "*") -> Optional[float]:
        """
        获取建议的抓取延迟时间
        
        Args:
            url: URL
            user_agent: User-Agent 字符串
        
        Returns:
            延迟秒数，如果未指定则返回 None
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(base_url, "/robots.txt")
            
            if robots_url in self._parsers:
                parser = self._parsers[robots_url]
                delay = parser.crawl_delay(user_agent)
                return delay
            
            return None
            
        except Exception as e:
            logger.error(f"获取 crawl delay 时出错: {e}")
            return None


# 全局实例
robots_checker = RobotsChecker()
