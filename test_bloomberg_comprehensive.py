#!/usr/bin/env python3
"""
全面测试彭博社新闻抓取器
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetchers.bloomberg import BloombergFetcher
from src.utils.logger import logger
import time


def test_bloomberg_fetcher_comprehensive():
    """全面测试彭博社抓取器"""
    print("="*60)
    print("开始全面测试彭博社新闻抓取器...")
    print("="*60)
    
    # 创建抓取器实例
    fetcher = BloombergFetcher()
    
    try:
        print(f"正在连接到: {fetcher.base_url}")
        print(f"使用 User-Agent: {fetcher.session.headers.get('User-Agent', 'Default')}")
        print()
        
        # 运行抓取
        start_time = time.time()
        articles = fetcher.run()
        end_time = time.time()
        
        print(f"✅ 成功抓取到 {len(articles)} 篇新闻")
        print(f"⏱️  抓取耗时: {end_time - start_time:.2f} 秒")
        
        if articles:
            print("\n📈 抓取统计:")
            categories = {}
            for article in articles:
                cat = article.get('category', '未知')
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in categories.items():
                print(f"  {cat}: {count} 篇")
        
        # 显示前几篇新闻的详细信息
        print(f"\n📰 前 5 篇新闻详情:")
        print("-"*60)
        
        for i, article in enumerate(articles[:5]):
            print(f"\n【第 {i+1} 篇】")
            print(f"标题: {article.get('title', 'N/A')}")
            print(f"链接: {article.get('url', 'N/A')}")
            print(f"分类: {article.get('category', 'N/A')}")
            print(f"时间: {article.get('published_at', 'N/A')}")
            print(f"优先级: {article.get('priority', 'N/A')}")
            print(f"标签: {', '.join(article.get('tags', []))}")
            
            content_preview = article.get('content', '')[:200] + "..." if len(article.get('content', '')) > 200 else article.get('content', '')
            print(f"内容预览: {content_preview}")
        
        print("\n" + "="*60)
        print("✅ 彭博社抓取器测试完成!")
        print("="*60)
        
        return articles
        
    except Exception as e:
        logger.error(f"❌ 测试彭博社抓取器时出错: {e}", exc_info=True)
        return []


def test_individual_sources():
    """测试各个RSS源"""
    print("\n🔍 测试各个RSS源...")
    
    fetcher = BloombergFetcher()
    
    for category, feed_url in fetcher.RSS_FEEDS.items():
        print(f"\n测试 {category} 源: {feed_url}")
        try:
            import feedparser
            feed = feedparser.parse(feed_url)
            print(f"  ✅ 成功连接，获取到 {len(feed.entries)} 个项目")
            if feed.bozo:
                print(f"  ⚠️  解析警告: {feed.bozo_exception}")
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")


if __name__ == "__main__":
    articles = test_bloomberg_fetcher_comprehensive()
    
    # 额外测试各个RSS源
    test_individual_sources()
    
    print(f"\n总结: 共获取 {len(articles)} 篇新闻")
    
    # 如果需要通过命令行参数来执行特定功能，可以添加如下代码
    if len(sys.argv) > 1:
        if sys.argv[1] == "validate":
            # 可以在这里添加验证功能
            print("\n验证功能待实现...")