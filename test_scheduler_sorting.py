#!/usr/bin/env python3
"""
测试抓取器排序功能
"""
from src.scheduler.jobs import NewsJobs

# 创建 NewsJobs 实例
jobs = NewsJobs()

# 获取排序后的抓取器
fetchers = jobs.all_fetchers

print("排序后的抓取器（中文优先）:")
print("-" * 60)

# 打印抓取器及其语言
for i, fetcher in enumerate(fetchers):
    language = getattr(fetcher, 'language', 'en')
    print(f"{i+1}. {fetcher.source_name} (语言: {language})")

print("-" * 60)
print(f"总抓取器数量: {len(fetchers)}")
