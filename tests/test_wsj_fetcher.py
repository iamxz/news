#!/usr/bin/env python3
"""
测试 WSJ 新闻抓取器
"""
import sys
import os

# 添加项目根目录到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fetchers_registry import FETCHERS

def test_wsj_fetch():
    """测试 WSJ 新闻抓取"""
    print("开始测试 WSJ 新闻抓取...")
    
    # 获取 WSJ 抓取器
    if 'wsj' not in FETCHERS:
        print("错误: WSJ 抓取器未注册")
        return
    
    fetcher = FETCHERS['wsj']()
    
    # 抓取新闻
    try:
        articles = fetcher.run()
        print(f"成功抓取到 {len(articles)} 条 WSJ 新闻")
        
        # 打印前10条新闻
        if articles:
            print(f"\n前10条 WSJ 新闻:")
            for i, article in enumerate(articles[:10], 1):
                print(f"{i}. {article['title']}")
                print(f"   链接: {article['url']}")
                print(f"   内容: {article['content'][:100]}...")
                print(f"   分类: {article['category']}")
                print(f"   时间: {article['published_at']}")
                print()
        else:
            print("未抓取到任何新闻")
            
    except Exception as e:
        print(f"抓取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wsj_fetch()
