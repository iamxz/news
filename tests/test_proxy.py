#!/usr/bin/env python
"""
测试代理功能

验证代理配置是否正确
"""
import sys
from src.utils.proxy import get_proxies, test_current_proxy
from src.utils.config import get_settings


def main():
    print("=" * 60)
    print("代理功能测试")
    print("=" * 60)
    
    settings = get_settings()
    
    # 1. 检查配置
    print("\n1. 检查代理配置:")
    print(f"   HTTP_PROXY:  {settings.http_proxy or '未配置'}")
    print(f"   HTTPS_PROXY: {settings.https_proxy or '未配置'}")
    
    # 2. 获取代理字典
    print("\n2. 获取代理字典:")
    proxies = get_proxies()
    if proxies:
        print(f"   {proxies}")
    else:
        print("   未配置代理")
    
    # 3. 测试代理
    print("\n3. 测试代理连接:")
    if test_current_proxy():
        print("   ✅ 代理测试成功")
        return 0
    else:
        if not proxies:
            print("   ℹ️  未配置代理（直连模式）")
            return 0
        else:
            print("   ❌ 代理测试失败")
            return 1


if __name__ == "__main__":
    sys.exit(main())
