#!/bin/bash
# 开发脚本 - 提供开发常用命令

set -e

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

show_menu() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🛠️  开发工具菜单"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  1) 🧪 运行测试"
    echo "  2) 📊 测试覆盖率"
    echo "  3) 🎨 格式化代码 (black)"
    echo "  4) 🔍 代码检查 (ruff)"
    echo "  5) 🔎 类型检查 (mypy)"
    echo "  6) ✨ 运行所有检查 (format + lint + type)"
    echo "  7) 📦 构建包"
    echo "  8) 🧹 清理缓存"
    echo "  9) 📝 查看日志"
    echo "  0) 🚪 退出"
    echo ""
    echo -n "请选择 [0-9]: "
}

while true; do
    show_menu
    read -r choice
    echo ""
    
    case $choice in
        1)
            echo "🧪 运行测试..."
            pytest -v
            ;;
        2)
            echo "📊 运行测试并生成覆盖率报告..."
            pytest --cov=src --cov-report=html --cov-report=term
            echo ""
            echo "✓ HTML 报告已生成: htmlcov/index.html"
            echo "  打开命令: open htmlcov/index.html"
            ;;
        3)
            echo "🎨 格式化代码..."
            black .
            echo "✓ 代码格式化完成"
            ;;
        4)
            echo "🔍 运行 ruff 检查..."
            ruff check .
            echo ""
            echo "是否自动修复问题? (y/N)"
            read -r fix
            if [[ "$fix" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                ruff check --fix .
                echo "✓ 已自动修复"
            fi
            ;;
        5)
            echo "🔎 运行类型检查..."
            mypy src/
            ;;
        6)
            echo "✨ 运行所有代码质量检查..."
            echo ""
            echo "1/3 格式化代码..."
            black .
            echo ""
            echo "2/3 Lint 检查..."
            ruff check --fix .
            echo ""
            echo "3/3 类型检查..."
            mypy src/ || true
            echo ""
            echo "✓ 所有检查完成"
            ;;
        7)
            echo "📦 构建包..."
            pip install build
            python -m build
            echo "✓ 构建完成: dist/"
            ;;
        8)
            echo "🧹 清理缓存..."
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -type f -name "*.pyc" -delete 2>/dev/null || true
            find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
            rm -rf htmlcov/ .coverage 2>/dev/null || true
            echo "✓ 缓存已清理"
            ;;
        9)
            echo "📝 查看日志..."
            if [ -f "logs/news.log" ]; then
                tail -f logs/news.log
            else
                echo "⚠️  日志文件不存在"
            fi
            ;;
        0)
            echo "👋 退出开发工具"
            exit 0
            ;;
        *)
            echo "❌ 无效选项"
            ;;
    esac
    
    echo ""
    echo "按回车键继续..."
    read -r
done
