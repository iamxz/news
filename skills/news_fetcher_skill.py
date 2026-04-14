#!/usr/bin/env python3
"""
新闻抓取Skill

用于抓取所有新闻源的新闻，支持命令行调用
"""
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Optional

from src.fetchers.registry import FETCHERS
from src.storage.database import db
from src.storage.models import NewsArticle
from src.utils.logger import logger


def fetch_news(sources: Optional[List[str]] = None) -> List[NewsArticle]:
    """
    抓取新闻
    
    Args:
        sources: 新闻源列表，None表示所有新闻源
    
    Returns:
        新闻列表
    """
    articles = []
    
    # 获取要使用的抓取器
    if sources:
        # 验证指定的新闻源是否存在
        valid_sources = []
        for source in sources:
            if source in FETCHERS:
                valid_sources.append(source)
            else:
                logger.warning(f"新闻源 {source} 不存在")
        fetchers_to_use = {k: FETCHERS[k] for k in valid_sources}
    else:
        fetchers_to_use = FETCHERS
    
    logger.info(f"开始抓取 {len(fetchers_to_use)} 个新闻源的新闻")
    
    # 抓取每个新闻源的新闻
    for source_name, fetcher_class in fetchers_to_use.items():
        try:
            logger.info(f"开始抓取 {source_name} 的新闻")
            fetcher = fetcher_class()
            fetched_articles = fetcher.run()
            
            # 转换为 NewsArticle 对象
            for article_data in fetched_articles:
                article = NewsArticle.from_dict(article_data, fetcher)
                articles.append(article)
            
            logger.info(f"成功抓取 {source_name} 的 {len(fetched_articles)} 篇新闻")
        except Exception as e:
            logger.error(f"抓取 {source_name} 的新闻失败: {e}")
    
    # 保存到数据库
    if articles:
        saved_count = db.save_articles(articles)
        logger.info(f"成功保存 {saved_count}/{len(articles)} 篇新闻到数据库")
    
    return articles


def format_output(articles: List[NewsArticle], output_format: str) -> str:
    """
    格式化输出
    
    Args:
        articles: 新闻列表
        output_format: 输出格式，支持 json 和 text
    
    Returns:
        格式化后的输出
    """
    if output_format == 'json':
        return json.dumps(
            [article.dict() for article in articles],
            ensure_ascii=False,
            default=str
        )
    elif output_format == 'text':
        text_output = []
        for article in articles:
            text_output.append(f"标题: {article.title}")
            text_output.append(f"来源: {article.source}")
            text_output.append(f"发布时间: {article.published_at}")
            text_output.append(f"链接: {article.url}")
            text_output.append("---")
        return '\n'.join(text_output)
    else:
        return f"不支持的输出格式: {output_format}"


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='新闻抓取Skill')
    parser.add_argument('--sources', nargs='+', help='指定新闻源，多个新闻源用空格分隔')
    parser.add_argument('--output', default='json', choices=['json', 'text'], help='输出格式')
    
    args = parser.parse_args()
    
    # 抓取新闻
    articles = fetch_news(args.sources)
    
    # 格式化输出
    output = format_output(articles, args.output)
    print(output)


if __name__ == '__main__':
    main()