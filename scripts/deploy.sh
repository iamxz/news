#!/bin/bash
# 部署脚本 - 用于生产环境部署

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 全球新闻聚合工具 - 部署脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否在生产环境
echo "⚠️  警告: 这是生产环境部署脚本"
echo ""
echo "确认要部署到生产环境吗? (yes/no)"
read -r confirm

if [ "$confirm" != "yes" ]; then
    echo "取消部署"
    exit 0
fi

echo ""
echo "1️⃣  拉取最新代码..."
if [ -d ".git" ]; then
    git pull
    echo "✓ 代码已更新"
else
    echo "⚠️  不是 git 仓库，跳过"
fi

echo ""
echo "2️⃣  备份数据库..."
if [ -f "data/news.db" ]; then
    backup_file="data/news.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp data/news.db "$backup_file"
    echo "✓ 数据库已备份到: $backup_file"
else
    echo "⚠️  数据库文件不存在"
fi

echo ""
echo "3️⃣  创建/激活虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✓ 虚拟环境已激活"

echo ""
echo "4️⃣  更新依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ 依赖已更新"

echo ""
echo "5️⃣  运行数据库迁移（如有）..."
# 这里添加数据库迁移命令
echo "⊘ 暂无迁移"

echo ""
echo "6️⃣  清理旧数据..."
python main.py clean -d 30 || true
echo "✓ 旧数据已清理"

echo ""
echo "7️⃣  测试应用..."
python main.py stats
echo "✓ 应用测试通过"

echo ""
echo "8️⃣  设置定时任务..."
echo "是否设置 crontab 定时任务? (y/N)"
read -r setup_cron

if [[ "$setup_cron" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 创建 cron 脚本
    cat > "$SCRIPT_DIR/cron_job.sh" << EOF
#!/bin/bash
cd $SCRIPT_DIR
source venv/bin/activate
python main.py pipeline >> logs/cron.log 2>&1
EOF
    
    chmod +x "$SCRIPT_DIR/cron_job.sh"
    
    echo ""
    echo "请手动添加以下 crontab 任务:"
    echo ""
    echo "# 每天凌晨 2 点运行"
    echo "0 2 * * * $SCRIPT_DIR/cron_job.sh"
    echo ""
    echo "# 每 6 小时运行一次"
    echo "0 */6 * * * $SCRIPT_DIR/cron_job.sh"
    echo ""
    echo "添加命令: crontab -e"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 部署信息:"
echo "  - 数据库备份: $backup_file"
echo "  - 应用路径: $(pwd)"
echo "  - Python: $(which python)"
echo ""
echo "📊 查看统计: python main.py stats"
echo "📰 查看新闻: python main.py show"
echo "📝 查看日志: tail -f logs/cron.log"
echo ""
