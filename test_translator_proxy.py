#!/usr/bin/env python3
"""
测试翻译器的代理配置
"""
import os
import sys
from src.translators.baidu import BaiduTranslator
from src.translators.google import GoogleTranslator
from src.utils.config import get_settings
from src.utils.proxy import get_proxies


def test_translator_proxy():
    """测试翻译器的代理配置"""
    print("=== 测试翻译器的代理配置 ===")
    
    # 获取配置
    settings = get_settings()
    
    print(f"ENABLE_PROXY: {settings.enable_proxy}")
    print(f"HTTP_PROXY: {settings.http_proxy}")
    print(f"HTTPS_PROXY: {settings.https_proxy}")
    
    # 测试 get_proxies 函数
    print(f"\nget_proxies() 返回: {get_proxies()}")
    
    # 创建翻译器实例
    baidu_translator = BaiduTranslator()
    google_translator = GoogleTranslator()
    
    print(f"\n百度翻译器:")
    print(f"proxies: {baidu_translator.proxies}")
    
    print(f"\nGoogle翻译器:")
    print(f"proxies: {google_translator.proxies}")
    
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
    print(f"get_proxies() 返回: {get_proxies()}")
    
    # 场景2: 启用代理
    print("\n场景2: 启用代理")
    os.environ['ENABLE_PROXY'] = 'true'
    reload(src.utils.config)
    settings_reloaded = get_settings_reloaded()
    print(f"settings.enable_proxy: {settings_reloaded.enable_proxy}")
    print(f"get_proxies() 返回: {get_proxies()}")
    
    # 场景3: 禁用代理（再次测试）
    print("\n场景3: 禁用代理（再次测试）")
    os.environ['ENABLE_PROXY'] = 'false'
    reload(src.utils.config)
    settings_reloaded = get_settings_reloaded()
    print(f"settings.enable_proxy: {settings_reloaded.enable_proxy}")
    print(f"get_proxies() 返回: {get_proxies()}")
    
    print("\n=== 测试完成 ===")
    print("修复验证: 当 ENABLE_PROXY=false 时，get_proxies() 应返回空字典 {}")


if __name__ == "__main__":
    test_translator_proxy()
