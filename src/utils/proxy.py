"""
代理工具模块

提供代理配置和测试功能
"""
import requests
from typing import Optional, Dict
from src.utils.config import get_settings
from src.utils.logger import logger


def get_proxies() -> Dict[str, str]:
    """
    获取代理配置
    
    Returns:
        代理字典，如果未配置则返回空字典
    """
    settings = get_settings()
    
    if not settings.http_proxy and not settings.https_proxy:
        return {}
    
    proxies = {}
    if settings.http_proxy:
        proxies['http'] = settings.http_proxy
    if settings.https_proxy:
        proxies['https'] = settings.https_proxy
    
    return proxies


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
