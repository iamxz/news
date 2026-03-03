#!/bin/bash
# 安装脚本 - 自动设置项目环境

set -e  # 遇到错误立即退出

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌍 全球新闻聚合工具 - 安装脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 Python 版本
echo "1️⃣  检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "   请先安装 Python 3.10 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ 错误: Python 版本过低"
    echo "   当前版本: $PYTHON_VERSION"
    echo "   需要版本: >= $REQUIRED_VERSION"
    exit 1
fi

echo "✓ Python 版本: $PYTHON_VERSION"

# 检查 pip
echo ""
echo "2️⃣  检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3"
    exit 1
fi
echo "✓ pip 已安装"

# 创建虚拟环境
echo ""
echo "3️⃣  创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，是否删除并重新创建? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ 虚拟环境已重新创建"
    else
        echo "✓ 使用现有虚拟环境"
    fi
else
    python3 -m venv venv
    echo "✓ 虚拟环境已创建"
fi

# 激活虚拟环境
echo ""
echo "4️⃣  激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 升级 pip
echo ""
echo "5️⃣  升级 pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip 已升级"

# 安装依赖
echo ""
echo "6️⃣  安装项目依赖..."
echo "   这可能需要几分钟..."
pip install -r requirements.txt
echo "✓ 生产依赖已安装"

# 询问是否安装开发依赖
echo ""
echo "7️⃣  是否安装开发依赖（测试、格式化工具）? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    pip install -r requirements-dev.txt
    echo "✓ 开发依赖已安装"
else
    echo "⊘ 跳过开发依赖"
fi

# 创建必要的目录
echo ""
echo "8️⃣  创建数据目录..."
mkdir -p data
mkdir -p logs
echo "✓ 目录已创建"

# 配置环境变量
echo ""
echo "9️⃣  配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ 已创建 .env 文件"
    echo ""
    echo "⚠️  重要: 请编辑 .env 文件并配置以下 API keys:"
    echo "   - OPENAI_API_KEY（推荐）"
    echo "   - DEEPL_API_KEY（可选）"
    echo ""
    echo "   至少需要配置一个翻译 API 才能使用翻译功能"
    echo ""
    
    # 询问是否现在配置
    echo "是否现在打开 .env 文件进行编辑? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✓ .env 文件已存在"
fi

# 测试安装
echo ""
echo "🔟 测试安装..."
if python main.py --help > /dev/null 2>&1; then
    echo "✓ 安装测试通过"
else
    echo "❌ 安装测试失败"
    echo "   请检查错误信息"
    exit 1
fi

# 完成
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 安装完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 下一步操作:"
echo ""
echo "1. 确保已配置 .env 文件中的 API keys"
echo "   编辑命令: nano .env"
echo ""
echo "2. 激活虚拟环境:"
echo "   source venv/bin/activate"
echo ""
echo "3. 运行应用:"
echo "   python main.py --help        # 查看帮助"
echo "   python main.py pipeline      # 运行完整流程"
echo "   ./start.sh                   # 使用启动脚本"
echo ""
echo "4. 查看文档:"
echo "   cat README.md"
echo ""
echo "💡 提示: 运行 ./test.sh 进行快速测试"
echo ""
