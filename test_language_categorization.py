#!/usr/bin/env python3
"""
测试抓取器语言分类功能
"""
from src.fetchers.registry import FETCHERS

# 分类抓取器
categorized_fetchers = {
    '国际媒体': [],
    '中文媒体': []
}

for key, fetcher_class in FETCHERS.items():
    try:
        # 创建抓取器实例
        fetcher = fetcher_class()
        # 获取语言字段
        language = getattr(fetcher, 'language', 'en')
        # 根据语言分类
        if language == 'zh':
            categorized_fetchers['中文媒体'].append(key)
        else:
            categorized_fetchers['国际媒体'].append(key)
        print(f"{key}: {language}")
    except Exception as e:
        # 如果创建实例失败，默认归类为国际媒体
        categorized_fetchers['国际媒体'].append(key)
        print(f"{key}: 错误 - {e}")

print('\n中文媒体:')
print(categorized_fetchers['中文媒体'])
print('\n国际媒体:')
print(categorized_fetchers['国际媒体'])
print(f'\n总抓取器数量: {len(FETCHERS)}')
print(f'中文媒体数量: {len(categorized_fetchers["中文媒体"])}')
print(f'国际媒体数量: {len(categorized_fetchers["国际媒体"])}')
