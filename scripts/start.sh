#!/bin/bash
# 启动脚本 - 快速启动应用

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 全球新闻聚合工具 - 启动"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo "   请先运行: ./install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "   翻译和验证功能可能不可用"
    echo ""
    echo "是否继续? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        exit 1
    fi
fi

# 显示菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    echo ""
    echo "  1) 🔄 运行完整流程 (抓取 → 翻译 → 验证)"
    echo "  2) 📡 仅抓取新闻"
    echo "  3) 🌐 翻译未翻译的新闻"
    echo "  4) ✅ 验证未验证的新闻"
    echo "  5) 📰 查看新闻列表"
    echo "  6) 📊 查看统计信息"
    echo "  7) 🧹 清理旧新闻"
    echo "  8) 💻 自定义命令"
    echo "  0) 🚪 退出"
    echo ""
    echo -n "请输入选项 [0-8]: "
}

# 主循环
while true; do
    show_menu
    read -r choice
    echo ""
    
    case $choice in
        1)
            echo "🔄 运行完整流程..."
            echo ""
            python main.py pipeline
            ;;
        2)
            echo "请选择新闻源:"
            echo "  1) 全部"
            echo "  2) Reuters (路透社)"
            echo "  3) Hacker News"
            echo ""
            echo -n "请选择 [1-3]: "
            read -r source_choice
            
            case $source_choice in
                1)
                    python main.py fetch
                    ;;
                2)
                    python main.py fetch -s reuters
                    ;;
                3)
                    python main.py fetch -s hackernews
                    ;;
                *)
                    echo "❌ 无效选项"
                    ;;
            esac
            ;;
        3)
            echo "🌐 翻译新闻..."
            echo -n "翻译数量 (默认 10): "
            read -r limit
            limit=${limit:-10}
            python main.py translate -l "$limit"
            ;;
        4)
            echo "✅ 验证新闻..."
            echo -n "验证数量 (默认 10): "
            read -r limit
            limit=${limit:-10}
            python main.py validate -l "$limit"
            ;;
        5)
            echo "📰 查看新闻列表..."
            echo ""
            echo "筛选选项:"
            echo -n "  显示数量 (默认 20): "
            read -r limit
            limit=${limit:-20}
            
            echo -n "  显示模式 (1-普通 2-双语，默认双语): "
            read -r mode
            case $mode in
                1)
                    # 普通模式
                    cmd="python main.py show -l $limit"
                    ;;
                2)
                    # 双语模式
                    cmd="python main.py show -l $limit --bilingual"
                    ;;
                *)
                    # 默认双语模式
                    cmd="python main.py show -l $limit --bilingual"
                    ;;
            esac
            
            echo -n "  最低可信度 (0.0-1.0, 回车跳过): "
            read -r credibility
            [ -n "$credibility" ] && cmd="$cmd -m $credibility"
            
            echo -n "  最近几天 (回车跳过): "
            read -r days
            [ -n "$days" ] && cmd="$cmd -d $days"
            
            eval "$cmd"
            ;;
        6)
            echo "📊 统计信息..."
            python main.py stats
            ;;
        7)
            echo "🧹 清理旧新闻..."
            echo -n "保留最近几天 (默认 30): "
            read -r days
            days=${days:-30}
            python main.py clean -d "$days"
            ;;
        8)
            echo "💻 自定义命令"
            echo ""
            echo "可用命令:"
            python main.py --help
            echo ""
            echo -n "请输入命令 (例: show -s Reuters -l 10): "
            read -r custom_cmd
            python main.py $custom_cmd
            ;;
        0)
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新选择"
            ;;
    esac
    
    echo ""
    echo "按回车键继续..."
    read -r
done
