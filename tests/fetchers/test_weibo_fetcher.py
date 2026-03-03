#!/usr/bin/env python3
"""
测试微博热搜抓取器
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fetchers_registry import FETCHERS
from src.storage.database import Database

async def test_weibo_fetch():
    """测试微博热搜抓取"""
    print("开始测试微博热搜抓取...")
    
    # 获取微博抓取器
    if 'weibo' not in FETCHERS:
        print("错误: 微博抓取器未注册")
        return
    
    fetcher = FETCHERS['weibo']()
    
    # 抓取热搜
    try:
        articles = await fetcher.fetch()
        print(f"成功抓取到 {len(articles)} 条微博热搜")
        
        # 打印前50条热搜
        if articles:
            print(f"\n前50条微博热搜:")
            for i, article in enumerate(articles[:50], 1):
                print(f"{i}. {article.title}")
                print(f"   链接: {article.url}")
                print(f"   内容: {article.content}")
                print(f"   时间: {article.published_at}")
                print()
        else:
            print("未抓取到任何热搜")
            
    except Exception as e:
        print(f"抓取失败: {e}")

def test_weibo_fetch_sync():
    """同步测试微博热搜抓取"""
    asyncio.run(test_weibo_fetch())

if __name__ == "__main__":
    asyncio.run(test_weibo_fetch())
