#!/usr/bin/env python3
"""
测试抓取器的代理配置
"""
import sys
from src.fetchers.source.ap_news import APNewsFetcher
from src.utils.config import get_settings


def test_fetcher_proxy():
    """测试抓取器的代理配置"""
    print("=== 测试抓取器的代理配置 ===")
    
    # 获取配置
    settings = get_settings()

    print(f"HTTP_PROXY: {settings.http_proxy}")
    print(f"HTTPS_PROXY: {settings.https_proxy}")
    
    # 创建抓取器实例
    fetcher = APNewsFetcher()
    
    print(f"\n抓取器初始化后:")
    print(f"session.proxies: {fetcher.session.proxies}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_fetcher_proxy()
