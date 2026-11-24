"""
CLI 入口

被 pyproject.toml 注册为 news 命令。
"""
import sys

from src.utils.logger import logger


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: news <命令>")
        print("可用命令: fetch translate validate show stats pipeline clean")
        print("提示: 也可通过 Makefile 运行: make <命令>")
        sys.exit(1)

    cmd = args[0]
    logger.info(f"执行命令: {cmd}")

    if cmd == "fetch":
        from skills.news_fetcher_skill import fetch_news
        fetch_news()
    elif cmd == "show":
        from src.storage.database import db
        articles = db.get_articles()
        for a in articles:
            print(f"[{a.source}] {a.title}")
    else:
        print(f"命令 '{cmd}' 尚未实现")
        print("请使用 Makefile 命令: make {cmd}")

if __name__ == "__main__":
    main()