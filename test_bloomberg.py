#!/usr/bin/env python3
"""
测试彭博社新闻抓取器
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetchers.bloomberg import BloombergFetcher
from src.utils.logger import logger


def test_bloomberg_fetcher():
    """测试彭博社抓取器"""
    print("开始测试彭博社新闻抓取器...")
    
    # 创建抓取器实例
    fetcher = BloombergFetcher()
    
    try:
        # 运行抓取
        articles = fetcher.run()
        
        print(f"成功抓取到 {len(articles)} 篇新闻")
        
        # 显示前几篇新闻的标题
        for i, article in enumerate(articles[:5]):
            print(f"\n新闻 {i+1}:")
            print(f"  标题: {article.get('title', 'N/A')}")
            print(f"  链接: {article.get('url', 'N/A')}")
            print(f"  分类: {article.get('category', 'N/A')}")
            print(f"  时间: {article.get('published_at', 'N/A')}")
            print(f"  优先级: {article.get('priority', 'N/A')}")
            print(f"  可信度: {article.get('credibility_score', 'N/A')}")
        
        return articles
        
    except Exception as e:
        logger.error(f"测试彭博社抓取器时出错: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    articles = test_bloomberg_fetcher()
    print(f"\n测试完成，共获取 {len(articles)} 篇新闻")