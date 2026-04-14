#!/bin/bash
# 运行Skill的脚本
#
# 用于AI系统调用新闻抓取和分析Skills

# 进入项目根目录
cd "$(dirname "$0")/.." || exit 1

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 显示帮助信息
show_help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  fetch     抓取新闻"
    echo "  analyze   分析新闻"
    echo "  help      显示帮助信息"
    echo ""
    echo "Options for fetch:"
    echo "  --sources SOURCES  指定新闻源，多个新闻源用空格分隔"
    echo "  --days DAYS        抓取最近几天的新闻"
    echo "  --output FORMAT    输出格式（json或text）"
    echo ""
    echo "Options for analyze:"
    echo "  --category CATEGORY  指定分类（global, financial, domestic, bloomberg）"
    echo "  --days DAYS          分析最近几天的新闻"
    echo "  --output FORMAT      输出格式（json或text）"
    echo ""
    exit 0
}

# 处理命令
case "$1" in
    fetch)
        shift
        python -m skills.news_fetcher_skill "$@"
        ;;
    analyze)
        shift
        python -m skills.news_analyzer_skill "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_help
        ;;
esac