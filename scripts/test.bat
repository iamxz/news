@echo off
REM Windows 测试脚本

echo ================================================
echo 全球新闻聚合工具 - 快速测试 (Windows)
echo ================================================
echo.

REM 检查 Python 版本
echo 检查 Python 版本...
python --version
echo.

REM 检查虚拟环境
if not exist venv (
    echo 警告: 虚拟环境不存在
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM 检查 .env 文件
if not exist .env (
    echo.
    echo 警告: .env 文件不存在
    echo 请先配置 API keys:
    echo    copy .env.example .env
    echo    然后编辑 .env 文件添加 OPENAI_API_KEY 或 DEEPL_API_KEY
    echo.
    set /p continue=是否继续（某些功能可能不可用）? (Y/N) 
    if /i not "%continue%"=="Y" exit /b 1
)

echo.
echo 运行测试命令...
echo.

REM 显示帮助
echo 1. 显示帮助信息:
python main.py --help
echo.

REM 查看统计
echo 2. 查看统计信息:
python main.py stats
echo.

REM 测试抓取
echo 3. 测试抓取 (Hacker News):
python main.py fetch -s hackernews
echo.

REM 显示新闻
echo 4. 显示最新新闻:
python main.py show -l 5
echo.

echo ================================================
echo 测试完成！
echo ================================================
echo.
echo 更多命令:
echo    python main.py pipeline          # 运行完整流程
echo    python main.py show -m 0.8       # 显示高可信度新闻
echo    python main.py translate         # 翻译新闻
echo    python main.py validate          # 验证新闻
echo.
pause
