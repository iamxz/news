"""
交互式新闻浏览模块

提供交互式新闻浏览功能，支持：
- 鼠标悬停显示完整标题
- 按数字键查看详细信息
- 上下键导航
- 搜索功能
"""

from typing import List
import os

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live

from src.storage.models import NewsArticle
from src.utils.helpers import truncate_text
from .formatter import _get_credibility_stars, format_article_detail


console = Console()


def interactive_browse(articles: List[NewsArticle], bilingual: bool = False):
    """
    交互式浏览新闻
    
    Args:
        articles: 新闻列表
        bilingual: 是否显示双语标题
    """
    if not articles:
        console.print("[yellow]没有找到新闻[/yellow]")
        return
    
    current_index = 0
    
    while True:
        # 清屏
        console.clear()
        
        # 显示当前新闻列表
        _display_article_list(articles, current_index, bilingual)
        
        # 显示操作提示
        console.print("\n[yellow]操作提示:[/yellow]")
        console.print("  [cyan]↑/↓[/cyan] 上下导航  [cyan]Enter[/cyan] 查看详情  [cyan]q[/cyan] 退出")
        console.print("  [cyan]数字[/cyan] 直接跳转  [cyan]s[/cyan] 搜索  [cyan]h[/cyan] 显示帮助")
        
        # 获取用户输入
        try:
            choice = Prompt.ask("\n请选择操作", default="", show_default=False)
            
            if choice.lower() == 'q':
                break
            elif choice.lower() == 'h':
                _show_help()
            elif choice.lower() == 's':
                _search_articles(articles)
            elif choice == '':
                # Enter键查看当前选中项详情
                _show_article_detail(articles[current_index])
            elif choice.isdigit():
                # 数字键跳转
                index = int(choice) - 1
                if 0 <= index < len(articles):
                    current_index = index
                    _show_article_detail(articles[current_index])
                else:
                    console.print("[red]索引超出范围[/red]")
            elif choice == '↑' or choice.lower() == 'k':
                # 上移
                current_index = max(0, current_index - 1)
            elif choice == '↓' or choice.lower() == 'j':
                # 下移
                current_index = min(len(articles) - 1, current_index + 1)
            else:
                console.print("[red]无效输入[/red]")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


def _display_article_list(articles: List[NewsArticle], current_index: int, bilingual: bool):
    """显示文章列表，高亮当前选中项"""
    
    if bilingual:
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("英文标题", style="blue", no_wrap=False)
        table.add_column("中文标题", style="cyan", no_wrap=False)
        table.add_column("来源", style="green", width=12)
        table.add_column("可信度", justify="center", width=8)
        table.add_column("时间", style="yellow", width=12)
        
        for i, article in enumerate(articles):
            en_title = article.title
            zh_title = article.title_zh or "暂无中文标题"
            
            # 高亮当前选中项
            if i == current_index:
                style = "bold white on blue"
                en_title = f"[{style}]{en_title}[/{style}]"
                zh_title = f"[{style}]{zh_title}[/{style}]"
            
            credibility_stars = _get_credibility_stars(article.credibility_score)
            time_str = article.published_at.strftime("%m-%d %H:%M")
            
            table.add_row(str(i + 1), en_title, zh_title, article.source, 
                         credibility_stars, time_str)
    else:
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("标题", style="cyan", no_wrap=False)
        table.add_column("来源", style="green", width=12)
        table.add_column("可信度", justify="center", width=8)
        table.add_column("时间", style="yellow", width=12)
        
        for i, article in enumerate(articles):
            title = article.title
            
            # 高亮当前选中项
            if i == current_index:
                style = "bold white on blue"
                title = f"[{style}]{title}[/{style}]"
            
            credibility_stars = _get_credibility_stars(article.credibility_score)
            time_str = article.published_at.strftime("%m-%d %H:%M")
            
            table.add_row(str(i + 1), title, article.source, credibility_stars, time_str)
    
    console.print(table)
    console.print(f"\n[current {current_index + 1}/{len(articles)}]")


def _show_article_detail(article: NewsArticle):
    """显示文章详细信息"""
    console.clear()
    format_article_detail(article)
    
    console.print("\n[yellow]按任意键返回列表...[/yellow]")
    try:
        input()
    except KeyboardInterrupt:
        pass


def _search_articles(articles: List[NewsArticle]):
    """搜索文章"""
    keyword = Prompt.ask("请输入搜索关键词")
    
    if not keyword:
        return
    
    # 搜索匹配的文章
    matched_articles = []
    for article in articles:
        if (keyword.lower() in article.title.lower() or 
            (article.title_zh and keyword.lower() in article.title_zh.lower())):
            matched_articles.append(article)
    
    if matched_articles:
        console.print(f"\n[yellow]找到 {len(matched_articles)} 篇匹配的新闻:[/yellow]")
        interactive_browse(matched_articles)
    else:
        console.print("[red]未找到匹配的新闻[/red]")
        input("按回车继续...")


def _show_help():
    """显示帮助信息"""
    help_text = Panel("""
[bright_white]交互式浏览帮助[/bright_white]

[yellow]导航操作:[/yellow]
  ↑/↓ 或 k/j    上下移动选择
  数字键         直接跳转到指定序号
  Enter         查看当前选中项详情
  q             退出浏览

[yellow]搜索功能:[/yellow]
  s             搜索关键词（支持中英文标题）

[yellow]显示模式:[/yellow]
  默认显示      单语标题列表
  双语模式      中英文标题对照显示

[yellow]提示:[/yellow]
  • 当前选中项会高亮显示
  • 完整标题在详情页面查看
  • 支持 Ctrl+C 退出
    """, title="帮助信息", border_style="blue")
    
    console.print(help_text)
    input("按回车继续...")