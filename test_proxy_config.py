#!/usr/bin/env python3
"""
测试代理配置是否正确工作
"""
import os
import sys
from src.utils.config import get_settings
from src.utils.proxy import get_proxies, test_current_proxy


def test_proxy_config():
    """测试代理配置"""
    print("=== 测试代理配置 ===")
    
    # 获取配置
    settings = get_settings()
    
    print(f"ENABLE_PROXY: {settings.enable_proxy}")
    print(f"HTTP_PROXY: {settings.http_proxy}")
    print(f"HTTPS_PROXY: {settings.https_proxy}")
    
    # 获取代理配置
    proxies = get_proxies()
    print(f"\nget_proxies() 返回: {proxies}")
    
    # 测试当前代理
    print("\n测试当前代理配置:")
    test_current_proxy()
    
    # 测试不同场景
    print("\n=== 测试不同场景 ===")
    
    # 场景1: 禁用代理
    print("\n场景1: 禁用代理")
    os.environ['ENABLE_PROXY'] = 'false'
    # 重新获取配置
    from importlib import reload
    import src.utils.config
    reload(src.utils.config)
    from src.utils.config import get_settings as get_settings_reloaded
    settings_reloaded = get_settings_reloaded()
    print(f"ENABLE_PROXY: {settings_reloaded.enable_proxy}")
    proxies = get_proxies()
    print(f"get_proxies() 返回: {proxies}")
    
    # 场景2: 启用代理
    print("\n场景2: 启用代理")
    os.environ['ENABLE_PROXY'] = 'true'
    reload(src.utils.config)
    settings_reloaded = get_settings_reloaded()
    print(f"ENABLE_PROXY: {settings_reloaded.enable_proxy}")
    proxies = get_proxies()
    print(f"get_proxies() 返回: {proxies}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_proxy_config()
