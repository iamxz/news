#!/bin/bash
# 快速启动守护进程脚本

echo "🚀 启动全球新闻聚合守护进程..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，从模板复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
    exit 1
fi

# 启动守护进程
echo "📰 开始运行守护进程..."
echo "   - 高优先级新闻：每小时抓取"
echo "   - 中优先级新闻：每6小时抓取"
echo "   - 低优先级新闻：每天凌晨2点抓取"
echo "   - 自动翻译：每30分钟"
echo "   - 自动验证：每小时"
echo "   - 清理旧新闻：每周日凌晨3点"
echo ""
echo "按 Ctrl+C 停止守护进程"
echo ""

python main.py daemon
