#!/usr/bin/env python3
"""
测试抓取器的代理配置
"""
import os
import sys
from src.fetchers.source.ap_news import APNewsFetcher
from src.utils.config import get_settings


def test_fetcher_proxy():
    """测试抓取器的代理配置"""
    print("=== 测试抓取器的代理配置 ===")
    
    # 获取配置
    settings = get_settings()
    
    print(f"ENABLE_PROXY: {settings.enable_proxy}")
    print(f"HTTP_PROXY: {settings.http_proxy}")
    print(f"HTTPS_PROXY: {settings.https_proxy}")
    
    # 创建抓取器实例
    fetcher = APNewsFetcher()
    
    print(f"\n抓取器初始化后:")
    print(f"settings.enable_proxy: {fetcher.settings.enable_proxy}")
    print(f"session.proxies: {fetcher.session.proxies}")
    
    # 测试不同场景
    print("\n=== 测试不同场景 ===")
    
    # 场景1: 禁用代理
    print("\n场景1: 禁用代理")
    os.environ['ENABLE_PROXY'] = 'false'
    # 重新加载配置
    from importlib import reload
    import src.utils.config
    reload(src.utils.config)
    from src.utils.config import get_settings as get_settings_reloaded
    settings_reloaded = get_settings_reloaded()
    print(f"settings.enable_proxy: {settings_reloaded.enable_proxy}")
    # 创建新的抓取器实例
    fetcher1 = APNewsFetcher()
    print(f"session.proxies: {fetcher1.session.proxies}")
    
    # 场景2: 启用代理
    print("\n场景2: 启用代理")
    os.environ['ENABLE_PROXY'] = 'true'
    reload(src.utils.config)
    settings_reloaded = get_settings_reloaded()
    print(f"settings.enable_proxy: {settings_reloaded.enable_proxy}")
    # 创建新的抓取器实例
    fetcher2 = APNewsFetcher()
    print(f"session.proxies: {fetcher2.session.proxies}")
    
    # 场景3: 禁用代理（再次测试）
    print("\n场景3: 禁用代理（再次测试）")
    os.environ['ENABLE_PROXY'] = 'false'
    reload(src.utils.config)
    settings_reloaded = get_settings_reloaded()
    print(f"settings.enable_proxy: {settings_reloaded.enable_proxy}")
    # 创建新的抓取器实例
    fetcher3 = APNewsFetcher()
    print(f"session.proxies: {fetcher3.session.proxies}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_fetcher_proxy()
