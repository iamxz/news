"""
全球新闻聚合命令行工具

主程序入口
"""
import sys
from pathlib import Path

import click
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.fetchers.reuters import ReutersFetcher
from src.fetchers.hackernews import HackerNewsFetcher
from src.fetchers.bloomberg import BloombergFetcher
from src.fetchers.ap_news import APNewsFetcher
from src.fetchers.bbc import BBCFetcher
from src.fetchers.guardian import GuardianFetcher
from src.fetchers.nytimes import NYTimesFetcher
from src.fetchers.aljazeera import AlJazeeraFetcher
from src.fetchers.techcrunch import TechCrunchFetcher
from src.fetchers.reddit import RedditFetcher
from src.storage.database import db
from src.storage.models import NewsArticle
from src.translators import translator_manager
from src.validators import validation_pipeline
from src.display.formatter import (
    format_article_list,
    format_article_detail,
    format_statistics,
    print_success,
    print_error,
    print_warning,
    print_info,
    console
)
from src.utils.config import get_settings
from src.utils.logger import setup_logger, logger


# 设置日志
settings = get_settings()
setup_logger(level=settings.log_level)


# 可用的抓取器
FETCHERS = {
    'reuters': ReutersFetcher,
    'hackernews': HackerNewsFetcher,
    'bloomberg': BloombergFetcher,
    'apnews': APNewsFetcher,
    'bbc': BBCFetcher,
    'guardian': GuardianFetcher,
    'nytimes': NYTimesFetcher,
    'aljazeera': AlJazeeraFetcher,
    'techcrunch': TechCrunchFetcher,
    'reddit': RedditFetcher,
}


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    🌍 全球新闻聚合工具
    
    每日自动抓取全球热点新闻，提供中英双语展示和真实性验证
    """
    pass


@cli.command()
@click.option('--source', '-s', multiple=True, help='指定新闻源（可多选）')
@click.option('--translate', '-t', is_flag=True, help='抓取后立即翻译')
@click.option('--validate', '-v', is_flag=True, help='抓取后立即验证')
def fetch(source, translate, validate):
    """
    抓取新闻
    
    示例：
      news fetch                        # 抓取所有新闻源
      news fetch -s reuters -s hackernews  # 抓取指定来源
      news fetch -t -v                  # 抓取、翻译并验证
    """
    # 确定要抓取的新闻源
    if source:
        sources_to_fetch = [s for s in source if s in FETCHERS]
        if not sources_to_fetch:
            print_error(f"无效的新闻源。可用: {', '.join(FETCHERS.keys())}")
            return
    else:
        sources_to_fetch = list(FETCHERS.keys())
    
    print_info(f"准备抓取: {', '.join(sources_to_fetch)}")
    
    all_articles = []
    
    # 抓取新闻
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for source_name in sources_to_fetch:
            task = progress.add_task(f"抓取 {source_name}...", total=None)
            
            try:
                fetcher_class = FETCHERS[source_name]
                fetcher = fetcher_class()
                articles = fetcher.run()
                
                if articles:
                    all_articles.extend(articles)
                    print_success(f"{source_name}: 抓取到 {len(articles)} 篇新闻")
                else:
                    print_warning(f"{source_name}: 未抓取到新闻")
                
            except Exception as e:
                print_error(f"{source_name}: 抓取失败 - {e}")
                logger.error(f"抓取失败: {e}", exc_info=True)
            
            progress.remove_task(task)
    
    if not all_articles:
        print_warning("没有抓取到任何新闻")
        return
    
    # 保存到数据库
    print_info(f"保存 {len(all_articles)} 篇新闻到数据库...")
    articles_to_save = [NewsArticle(**article) for article in all_articles]
    saved_count = db.save_articles(articles_to_save)
    print_success(f"成功保存 {saved_count}/{len(all_articles)} 篇新闻")
    
    # 翻译
    if translate:
        print_info("开始翻译...")
        _translate_articles(limit=saved_count)
    
    # 验证
    if validate:
        print_info("开始验证...")
        _validate_articles(limit=saved_count)


@cli.command()
@click.option('--limit', '-l', default=10, help='翻译数量限制')
def translate(limit):
    """
    翻译未翻译的新闻
    
    示例：
      news translate           # 翻译 10 篇
      news translate -l 50     # 翻译 50 篇
    """
    _translate_articles(limit)


def _translate_articles(limit: int = 10):
    """翻译文章的内部函数"""
    # 获取未翻译的新闻
    articles = db.get_untranslated_articles(limit)
    
    if not articles:
        print_info("没有需要翻译的新闻")
        return
    
    print_info(f"找到 {len(articles)} 篇未翻译的新闻")
    
    # 翻译
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("翻译中...", total=len(articles))
        
        for i, article in enumerate(articles):
            try:
                # 翻译标题
                if article.title and not article.title_zh:
                    article.title_zh = translator_manager.translate(article.title)
                
                # 翻译内容
                if article.content and not article.content_zh:
                    article.content_zh = translator_manager.translate(article.content)
                
                # 标记为已翻译
                article.translated = True
                
                # 保存
                db.save_article(article)
                
                progress.update(task, advance=1)
                
            except Exception as e:
                print_error(f"翻译失败 ({article.title[:30]}...): {e}")
                logger.error(f"翻译失败: {e}", exc_info=True)
    
    print_success(f"翻译完成: {len(articles)} 篇")


@cli.command()
@click.option('--limit', '-l', default=10, help='验证数量限制')
def validate(limit):
    """
    验证未验证的新闻
    
    示例：
      news validate           # 验证 10 篇
      news validate -l 50     # 验证 50 篇
    """
    _validate_articles(limit)


def _validate_articles(limit: int = 10):
    """验证文章的内部函数"""
    # 获取未验证的新闻
    articles = db.get_unvalidated_articles(limit)
    
    if not articles:
        print_info("没有需要验证的新闻")
        return
    
    print_info(f"找到 {len(articles)} 篇未验证的新闻")
    
    # 验证
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("验证中...", total=len(articles))
        
        for article in articles:
            try:
                # 验证
                validated_article = validation_pipeline.validate(article)
                
                # 保存
                db.save_article(validated_article)
                
                progress.update(task, advance=1)
                
            except Exception as e:
                print_error(f"验证失败 ({article.title[:30]}...): {e}")
                logger.error(f"验证失败: {e}", exc_info=True)
    
    print_success(f"验证完成: {len(articles)} 篇")


@cli.command()
@click.option('--limit', '-l', default=20, help='显示数量')
@click.option('--source', '-s', help='筛选新闻源')
@click.option('--category', '-c', help='筛选分类')
@click.option('--min-credibility', '-m', type=float, help='最低可信度')
@click.option('--days', '-d', type=int, help='最近几天的新闻')
@click.option('--bilingual', '-b', is_flag=True, help='显示中英文双语标题')
@click.option('--detail-view', is_flag=True, help='详细视图模式（显示完整标题）')
@click.option('--interactive', '-i', is_flag=True, help='交互式查看模式')
@click.option('--web', '-w', is_flag=True, help='在浏览器中查看新闻（推荐）')
def show(limit, source, category, min_credibility, days, bilingual, detail_view, interactive, web):
    """
    显示新闻列表
    
    示例：
      news show                          # 显示最新 20 篇
      news show -l 50                    # 显示 50 篇
      news show -s Reuters               # 显示路透社新闻
      news show -c 科技                  # 显示科技新闻
      news show -m 0.8                   # 显示高可信度新闻
      news show -d 7                     # 显示最近 7 天的新闻
      news show -b                       # 显示中英文双语标题
      news show -i                       # 交互式查看模式
      news show -w                       # 网页查看模式
    """
    articles = db.get_articles(
        limit=limit,
        source=source,
        category=category,
        min_credibility=min_credibility,
        days=days
    )
    
    if not articles:
        print_warning("没有找到符合条件的新闻")
        return
    
    if web:
        # 使用网页查看模式
        from src.display.web_viewer import generate_and_open_report
        generate_and_open_report(articles)
    elif interactive:
        # 使用交互式查看模式
        from src.display.interactive import interactive_browse
        interactive_browse(articles, bilingual=bilingual)
    else:
        # 使用普通列表显示
        format_article_list(articles, bilingual=bilingual, detail_view=detail_view)


@cli.command()
@click.argument('article_id')
def detail(article_id):
    """
    显示新闻详情
    
    示例：
      news detail abc123
    """
    article = db.get_article(article_id)
    
    if not article:
        print_error(f"未找到新闻: {article_id}")
        return
    
    format_article_detail(article)


@cli.command()
def stats():
    """
    显示数据库统计信息
    
    示例：
      news stats
    """
    statistics = db.get_statistics()
    format_statistics(statistics)


@cli.command()
@click.option('--days', '-d', default=30, help='保留最近几天的新闻')
@click.confirmation_option(prompt='确定要删除旧新闻吗？')
def clean(days):
    """
    清理旧新闻
    
    示例：
      news clean              # 删除 30 天前的新闻
      news clean -d 7         # 删除 7 天前的新闻
    """
    deleted = db.delete_old_articles(days)
    print_success(f"删除了 {deleted} 条旧新闻（{days} 天前）")


@cli.command()
@click.option('--source', '-s', multiple=True, help='指定新闻源')
def pipeline(source):
    """
    运行完整流程：抓取 -> 翻译 -> 验证
    
    示例：
      news pipeline                        # 完整流程
      news pipeline -s reuters             # 指定新闻源
    """
    print_info("🚀 开始运行完整流程...")
    console.print()
    
    # 1. 抓取
    console.rule("[bold blue]步骤 1: 抓取新闻[/bold blue]")
    # 直接调用 fetch 命令的业务逻辑
    if source:
        sources_to_fetch = [s for s in source if s in FETCHERS]
        if not sources_to_fetch:
            print_error(f"无效的新闻源。可用: {', '.join(FETCHERS.keys())}")
            return
    else:
        sources_to_fetch = list(FETCHERS.keys())
    
    print_info(f"准备抓取: {', '.join(sources_to_fetch)}")
    
    all_articles = []
    
    # 抓取新闻
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for source_name in sources_to_fetch:
            task = progress.add_task(f"抓取 {source_name}...", total=None)
            
            try:
                fetcher_class = FETCHERS[source_name]
                fetcher = fetcher_class()
                articles = fetcher.run()
                
                if articles:
                    all_articles.extend(articles)
                    print_success(f"{source_name}: 抓取到 {len(articles)} 篇新闻")
                else:
                    print_warning(f"{source_name}: 未抓取到新闻")
                
            except Exception as e:
                print_error(f"{source_name}: 抓取失败 - {e}")
                logger.error(f"抓取失败: {e}", exc_info=True)
            
            progress.remove_task(task)
    
    if not all_articles:
        print_warning("没有抓取到任何新闻")
    else:
        # 保存到数据库
        print_info(f"保存 {len(all_articles)} 篇新闻到数据库...")
        articles_to_save = [NewsArticle(**article) for article in all_articles]
        saved_count = db.save_articles(articles_to_save)
        print_success(f"成功保存 {saved_count}/{len(all_articles)} 篇新闻")
    
    console.print()
    
    # 2. 翻译
    console.rule("[bold green]步骤 2: 翻译新闻[/bold green]")
    _translate_articles(limit=50)
    console.print()
    
    # 3. 验证
    console.rule("[bold yellow]步骤 3: 验证新闻[/bold yellow]")
    _validate_articles(limit=50)
    console.print()
    
    # 4. 显示统计
    console.rule("[bold magenta]步骤 4: 统计信息[/bold magenta]")
    stats.invoke(click.Context(stats))
    
    print_success("✅ 完整流程执行完毕！")


def main():
    """主函数"""
    try:
        cli()
    except KeyboardInterrupt:
        print_warning("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print_error(f"发生错误: {e}")
        logger.error(f"程序错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
