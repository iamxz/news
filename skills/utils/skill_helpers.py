#!/usr/bin/env python3
"""
Skill辅助函数

提供新闻分类、摘要生成和数据格式化等功能
"""
from typing import Optional, Dict, List
from src.storage.models import NewsArticle


def classify_news(article: NewsArticle) -> str:
    """
    分类新闻
    
    Args:
        article: 新闻文章
    
    Returns:
        分类结果：global（全球热点）、financial（金融热点）、domestic（国内大事）、bloomberg（彭博新闻）
    """
    # 彭博新闻优先分类
    if article.source.lower() == 'bloomberg':
        return 'bloomberg'
    
    # 关键词列表
    global_keywords = ['国际', '全球', '世界', '美国', '欧洲', '亚洲', '外交', '国际关系', '联合国', '峰会']
    financial_keywords = ['金融', '经济', '市场', '股票', '债券', '投资', '贸易', '货币', '通胀', '利率']
    domestic_keywords = ['中国', '国内', '北京', '上海', '政府', '政策', '社会', '民生', '科技', '教育']
    
    # 合并标题和内容进行分类
    text = f"{article.title} {article.content}".lower()
    
    # 计算关键词匹配数
    global_count = sum(1 for keyword in global_keywords if keyword.lower() in text)
    financial_count = sum(1 for keyword in financial_keywords if keyword.lower() in text)
    domestic_count = sum(1 for keyword in domestic_keywords if keyword.lower() in text)
    
    # 确定分类
    max_count = max(global_count, financial_count, domestic_count)
    if max_count == global_count and max_count > 0:
        return 'global'
    elif max_count == financial_count and max_count > 0:
        return 'financial'
    elif max_count == domestic_count and max_count > 0:
        return 'domestic'
    else:
        # 默认分类为全球热点
        return 'global'


def generate_summary(article: NewsArticle) -> str:
    """
    生成新闻摘要
    
    Args:
        article: 新闻文章
    
    Returns:
        新闻摘要
    """
    # 优先使用中文标题和内容
    title = article.title_zh or article.title
    content = article.content_zh or article.content
    
    # 简单的摘要生成逻辑：取前200个字符
    # 实际项目中可以使用更复杂的NLP算法
    summary = content[:200] + '...' if len(content) > 200 else content
    
    return summary


def format_analysis_result(results: Dict[str, List[Dict]]) -> str:
    """
    格式化分析结果
    
    Args:
        results: 分析结果
    
    Returns:
        格式化后的结果
    """
    formatted_result = []
    
    for category, items in results.items():
        category_name = {
            'global': '全球热点',
            'financial': '金融热点',
            'domestic': '国内大事',
            'bloomberg': '彭博新闻'
        }.get(category, category)
        
        formatted_result.append(f"\n=== {category_name} ===")
        formatted_result.append(f"共 {len(items)} 篇新闻")
        formatted_result.append("")
        
        for item in items:
            formatted_result.append(f"标题: {item['title_zh'] or item['title']}")
            formatted_result.append(f"来源: {item['source']}")
            formatted_result.append(f"发布时间: {item['published_at']}")
            formatted_result.append(f"摘要: {item['summary']}")
            formatted_result.append(f"链接: {item['url']}")
            formatted_result.append("---")
    
    return '\n'.join(formatted_result)


def validate_article(article: NewsArticle) -> bool:
    """
    验证新闻文章的有效性
    
    Args:
        article: 新闻文章
    
    Returns:
        是否有效
    """
    return bool(article.title and article.content and article.url)


