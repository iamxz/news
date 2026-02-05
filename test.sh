#!/bin/bash
# 快速测试脚本

echo "🚀 全球新闻聚合工具 - 快速测试"
echo "================================"
echo ""

# 检查 Python 版本
echo "✓ 检查 Python 版本..."
python3 --version

# 检查依赖
echo ""
echo "✓ 检查依赖是否已安装..."
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，创建中..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/bin/activate

# 提示配置环境变量
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env 文件不存在"
    echo "📝 请先配置 API keys："
    echo "   cp .env.example .env"
    echo "   然后编辑 .env 文件添加 OPENAI_API_KEY 或 DEEPL_API_KEY"
    echo ""
    read -p "是否继续（某些功能可能不可用）? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "✓ 运行测试命令..."
echo ""

# 显示帮助
echo "1️⃣  显示帮助信息："
python main.py --help

echo ""
echo "2️⃣  查看统计信息："
python main.py stats

echo ""
echo "3️⃣  测试抓取（Hacker News）："
python main.py fetch -s hackernews

echo ""
echo "4️⃣  显示最新新闻："
python main.py show -l 5

echo ""
echo "✅ 测试完成！"
echo ""
echo "💡 更多命令："
echo "   python main.py pipeline          # 运行完整流程"
echo "   python main.py show -m 0.8       # 显示高可信度新闻"
echo "   python main.py translate         # 翻译新闻"
echo "   python main.py validate          # 验证新闻"
echo ""
