"""
代理工具模块

提供代理配置和测试功能
"""
import requests
from typing import Optional, Dict
from src.utils.config import get_settings
from src.utils.logger import logger


def get_proxies() -> Optional[Dict[str, str]]:
    """
    获取代理配置
    
    Returns:
        代理字典，如果未配置则返回 None
    """
    settings = get_settings()
    
    if not settings.http_proxy and not settings.https_proxy:
        return None
    
    proxies = {}
    if settings.http_proxy:
        proxies['http'] = settings.http_proxy
    if settings.https_proxy:
        proxies['https'] = settings.https_proxy
    
    return proxies


def test_proxy(proxy_url: str, test_url: str = "https://www.google.com") -> bool:
    """
    测试代理是否可用
    
    Args:
        proxy_url: 代理 URL
        test_url: 测试 URL
    
    Returns:
        代理是否可用
    """
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        response = requests.get(
            test_url,
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"代理测试成功: {proxy_url}")
            return True
        else:
            logger.warning(f"代理测试失败: {proxy_url} (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        logger.error(f"代理测试失败: {proxy_url} - {e}")
        return False


def test_current_proxy() -> bool:
    """
    测试当前配置的代理
    
    Returns:
        代理是否可用
    """
    settings = get_settings()
    
    if not settings.http_proxy and not settings.https_proxy:
        logger.info("未配置代理")
        return True
    
    proxy_url = settings.https_proxy or settings.http_proxy
    return test_proxy(proxy_url)
