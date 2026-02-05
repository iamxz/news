"""
命令行格式化模块

使用 Rich 库格式化新闻展示
"""
from datetime import datetime
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import box

from src.storage.models import NewsArticle
from src.utils.helpers import truncate_text


console = Console()


def format_article_list(articles: List[NewsArticle], show_index: bool = True, bilingual: bool = False, detail_view: bool = False):
    """
    格式化新闻列表
    
    Args:
        articles: 新闻列表
        show_index: 是否显示序号
        bilingual: 是否显示双语标题
    """
    if not articles:
        console.print("[yellow]没有找到新闻[/yellow]")
        return
    
    if bilingual:
        # 双语标题表格
        table = Table(show_header=True, header_style="bold magenta")
        
        if show_index:
            table.add_column("#", style="dim", width=4)
        table.add_column("英文标题", style="blue", no_wrap=False, width=40)
        table.add_column("中文标题", style="cyan", no_wrap=False, width=40)
        table.add_column("来源", style="green", width=15)
        table.add_column("可信度", justify="center", width=8)
        table.add_column("时间", style="yellow", width=16)
        
        for i, article in enumerate(articles, 1):
            # 截断标题
            en_title = truncate_text(article.title, 50)
            zh_title = truncate_text(article.title_zh or "暂无中文标题", 50)
            
            # 可信度星级
            credibility_stars = _get_credibility_stars(article.credibility_score)
            
            # 时间
            time_str = article.published_at.strftime("%m-%d %H:%M")
            
            row = [en_title, zh_title, article.source, credibility_stars, time_str]
            if show_index:
                row.insert(0, str(i))
            
            table.add_row(*row)
    else:
        # 单语标题表格（默认）
        table = Table(show_header=True, header_style="bold magenta")
        
        if show_index:
            table.add_column("#", style="dim", width=4)
        table.add_column("标题", style="cyan", no_wrap=False, width=50)
        table.add_column("来源", style="green", width=15)
        table.add_column("可信度", justify="center", width=8)
        table.add_column("时间", style="yellow", width=16)
        
        for i, article in enumerate(articles, 1):
            # 截断标题
            title = truncate_text(article.title, 60)
            
            # 可信度星级
            credibility_stars = _get_credibility_stars(article.credibility_score)
            
            # 时间
            time_str = article.published_at.strftime("%m-%d %H:%M")
            
            row = [title, article.source, credibility_stars, time_str]
            if show_index:
                row.insert(0, str(i))
            
            table.add_row(*row)
    
    console.print(table)
    console.print(f"\n共 {len(articles)} 篇新闻\n")


def format_article_detail(article: NewsArticle):
    """
    格式化新闻详情
    
    Args:
        article: 新闻文章
    """
    console.print("\n" + "━" * 80 + "\n")
    
    # 标题
    title_text = Text(article.title, style="bold cyan")
    if article.title_zh:
        title_text.append(f"\n{article.title_zh}", style="bold white")
    console.print(title_text)
    
    console.print()
    
    # 基本信息
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="dim")
    info_table.add_column()
    
    info_table.add_row("🌐 来源", f"[green]{article.source}[/green]")
    info_table.add_row("🔗 链接", f"[blue]{article.url}[/blue]")
    info_table.add_row("🕒 时间", article.published_at.strftime("%Y-%m-%d %H:%M:%S"))
    info_table.add_row("📁 分类", article.category)
    
    console.print(info_table)
    console.print()
    
    # 验证信息
    console.print("[bold]📊 验证信息[/bold]")
    
    verify_table = Table(show_header=False, box=None, padding=(0, 2))
    verify_table.add_column(style="dim")
    verify_table.add_column()
    
    credibility_stars = _get_credibility_stars(article.credibility_score)
    verify_table.add_row(
        "可信度评分",
        f"{credibility_stars} {article.credibility_score:.2f}/1.0"
    )
    
    if article.cross_references > 0:
        verify_table.add_row(
            "交叉引用",
            f"[cyan]{article.cross_references}[/cyan] 个来源"
        )
    
    console.print(verify_table)
    console.print()
    
    # 验证标签
    if article.verification_labels:
        labels_text = " ".join([f"[green]✅ {label}[/green]" for label in article.verification_labels])
        console.print(labels_text)
        console.print()
    
    # 警告信息
    if article.warnings:
        console.print("[bold yellow]⚠️  警告：[/bold yellow]")
        for warning in article.warnings:
            console.print(f"  • [yellow]{warning}[/yellow]")
        console.print()
    
    # 内容
    console.print("[bold]📰 内容[/bold]\n")
    
    if article.content_zh and article.content:
        # 双语显示
        console.print("[dim]原文：[/dim]")
        console.print(Panel(article.content, border_style="blue"))
        console.print()
        console.print("[dim]中文：[/dim]")
        console.print(Panel(article.content_zh, border_style="cyan"))
    elif article.content_zh:
        console.print(Panel(article.content_zh, border_style="cyan"))
    elif article.content:
        console.print(Panel(article.content, border_style="blue"))
    else:
        console.print("[dim]暂无内容[/dim]")
    
    console.print("\n" + "━" * 80 + "\n")


def format_statistics(stats: dict):
    """
    格式化统计信息
    
    Args:
        stats: 统计信息字典
    """
    console.print("\n[bold cyan]📊 数据库统计[/bold cyan]\n")
    
    # 总览
    console.print(f"总新闻数：[green]{stats.get('total', 0)}[/green]")
    console.print(f"已翻译：[cyan]{stats.get('translated', 0)}[/cyan]")
    console.print(f"已验证：[yellow]{stats.get('validated', 0)}[/yellow]")
    console.print()
    
    # 按来源统计
    if stats.get('by_source'):
        table = Table(title="各新闻源统计", show_header=True)
        table.add_column("新闻源", style="cyan")
        table.add_column("数量", justify="right", style="green")
        
        for source, count in sorted(
            stats['by_source'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            table.add_row(source, str(count))
        
        console.print(table)
    
    console.print()


def _get_credibility_stars(score: float) -> str:
    """
    将可信度评分转换为星级显示
    
    Args:
        score: 可信度评分 (0.0-1.0)
    
    Returns:
        星级字符串
    """
    if score >= 0.90:
        return "[green]★★★★★[/green]"
    elif score >= 0.75:
        return "[green]★★★★[/green]☆"
    elif score >= 0.60:
        return "[yellow]★★★[/yellow]☆☆"
    elif score >= 0.45:
        return "[yellow]★★[/yellow]☆☆☆"
    else:
        return "[red]★[/red]☆☆☆☆"





def print_success(message: str):
    """打印成功消息"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """打印错误消息"""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """打印警告消息"""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str):
    """打印信息"""
    console.print(f"[cyan]ℹ[/cyan] {message}")
