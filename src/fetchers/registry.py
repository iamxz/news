"""
全球新闻聚合工具

新闻源注册中心
"""
import re
from src.fetchers import *

# 所有可用的新闻源抓取器
FETCHERS = {}

# 先获取所有全局变量的副本，避免遍历过程中修改字典
globals_copy = list(globals().items())

# 遍历所有导入的抓取器
for name, obj in globals_copy:
    # 只处理类，且类名以 Fetcher 结尾，排除 BaseFetcher
    if isinstance(obj, type) and name.endswith('Fetcher') and name != 'BaseFetcher':
        # 将驼峰命名转换为小写下划线命名
        # 例如: ReutersFetcher -> reuters, HackerNewsFetcher -> hackernews
        key = re.sub(r'([a-z0-9])([A-Z])', r'\1\2', name)
        key = re.sub(r'([A-Z])([A-Z][a-z])', r'\1\2', name)
        key = key.lower()
        # 去掉 Fetcher 后缀
        key = key[:-7]  # 7 是 'Fetcher' 的长度
        
        # 添加到 FETCHERS 字典
        FETCHERS[key] = obj
