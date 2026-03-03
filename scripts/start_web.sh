#!/bin/bash
# 启动新闻 Web 服务器

echo "🚀 启动新闻 Web 应用..."
echo "📍 前台地址: http://localhost:4000"
echo "📍 管理后台: http://localhost:4000/admin"
echo ""

# 检查是否安装了 Flask
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️  未检测到 Flask，正在安装..."
    pip install flask
fi

# 启动服务器
python web_server.py
