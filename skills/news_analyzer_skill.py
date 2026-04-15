#!/usr/bin/env python3
"""
新闻分析Skill

用于分析新闻，生成分类解读，支持命令行调用
"""
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from src.storage.database import db
from src.storage.models import NewsArticle
from src.utils.logger import logger
from skills.utils.skill_helpers import classify_news, generate_summary, format_analysis_result


def analyze_news(category: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
    分析新闻
    
    Args:
        category: 分类，可选值：global, financial, domestic, bloomberg
    
    Returns:
        分析结果，按分类组织
    """
    # 先检查今天是否已抓取
    today_count = db.get_today_articles_count()
    if today_count > 0:
        logger.info(f"今日已抓取 {today_count} 篇新闻，跳过抓取步骤")
    else:
        logger.info("今日尚未抓取新闻，先执行抓取...")
        from skills.news_fetcher_skill import fetch_news
        fetch_news()
    
    # 从数据库获取新闻
    articles = db.get_articles()
    logger.info(f"获取到 {len(articles)} 篇新闻进行分析")
    
    # 分类和分析
    analysis_results = {
        'global': [],      # 全球热点
        'financial': [],   # 金融热点
        'domestic': [],    # 国内大事
        'bloomberg': []    # 彭博新闻
    }
    
    for article in articles:
        # 分类
        news_category = classify_news(article)
        
        # 生成摘要
        summary = generate_summary(article)
        
        # 组织分析结果
        analysis_item = {
            'title': article.title,
            'title_zh': article.title_zh or article.title,
            'source': article.source,
            'published_at': article.published_at.isoformat(),
            'url': article.url,
            'category': news_category,
            'summary': summary
        }
        
        # 添加到对应分类
        if news_category in analysis_results:
            analysis_results[news_category].append(analysis_item)
    
    # 如果指定了分类，只返回该分类的结果
    if category and category in analysis_results:
        return {category: analysis_results[category]}
    
    return analysis_results


def format_output(analysis_results: Dict[str, List[Dict]], output_format: str) -> str:
    """
    格式化输出
    
    Args:
        analysis_results: 分析结果
        output_format: 输出格式，支持 json 和 text
    
    Returns:
        格式化后的输出
    """
    if output_format == 'json':
        return json.dumps(
            analysis_results,
            ensure_ascii=False,
            default=str
        )
    elif output_format == 'text':
        text_output = []
        for category, items in analysis_results.items():
            category_name = {
                'global': '全球热点',
                'financial': '金融热点',
                'domestic': '国内大事',
                'bloomberg': '彭博新闻'
            }.get(category, category)
            
            text_output.append(f"\n=== {category_name} ===")
            text_output.append(f"共 {len(items)} 篇新闻")
            text_output.append("")
            
            for item in items:
                text_output.append(f"标题: {item['title_zh'] or item['title']}")
                text_output.append(f"来源: {item['source']}")
                text_output.append(f"发布时间: {item['published_at']}")
                text_output.append(f"摘要: {item['summary']}")
                text_output.append(f"链接: {item['url']}")
                text_output.append("---")
        
        return '\n'.join(text_output)
    else:
        return f"不支持的输出格式: {output_format}"


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='新闻分析Skill')
    parser.add_argument('--category', choices=['global', 'financial', 'domestic', 'bloomberg'], help='指定分类')
    parser.add_argument('--output', default='json', choices=['json', 'text'], help='输出格式')
    
    args = parser.parse_args()
    
    # 分析新闻
    analysis_results = analyze_news(args.category)
    
    # 格式化输出
    output = format_output(analysis_results, args.output)
    print(output)


if __name__ == '__main__':
    main()