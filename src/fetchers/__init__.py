"""新闻抓取器模块"""

import os
import importlib
import inspect

# 动态导入 source 目录下的所有抓取器
__all__ = []

# 获取 source 目录路径
current_dir = os.path.dirname(__file__)
source_dir = os.path.join(current_dir, 'source')

# 遍历 source 目录下的所有文件
for filename in os.listdir(source_dir):
    # 只处理 .py 文件
    if filename.endswith('.py'):
        # 获取模块名（去掉 .py 后缀）
        module_name = filename[:-3]
        # 导入模块
        module = importlib.import_module(f'.source.{module_name}', package=__name__)
        
        # 遍历模块中的所有属性
        for name, obj in inspect.getmembers(module):
            # 只添加类，且类名以 Fetcher 结尾，排除 BaseFetcher
            if inspect.isclass(obj) and name.endswith('Fetcher') and name != 'BaseFetcher':
                # 将类添加到当前模块的命名空间
                globals()[name] = obj
                # 将类名添加到 __all__ 列表
                __all__.append(name)
