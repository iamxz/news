@echo off
REM Windows 安装脚本

echo ================================================
echo 全球新闻聚合工具 - 安装脚本 (Windows)
echo ================================================
echo.

REM 检查 Python
echo 1. 检查 Python 版本...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM 创建虚拟环境
echo 2. 创建虚拟环境...
if exist venv (
    echo 虚拟环境已存在，是否删除并重新创建? (Y/N)
    set /p recreate=
    if /i "%recreate%"=="Y" (
        rmdir /s /q venv
        python -m venv venv
        echo 虚拟环境已重新创建
    ) else (
        echo 使用现有虚拟环境
    )
) else (
    python -m venv venv
    echo 虚拟环境已创建
)
echo.

REM 激活虚拟环境
echo 3. 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 升级 pip
echo 4. 升级 pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM 安装依赖
echo 5. 安装项目依赖...
echo 这可能需要几分钟...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo 生产依赖已安装
echo.

REM 询问是否安装开发依赖
echo 6. 是否安装开发依赖（测试、格式化工具）? (Y/N)
set /p dev_install=
if /i "%dev_install%"=="Y" (
    pip install -r requirements-dev.txt
    echo 开发依赖已安装
) else (
    echo 跳过开发依赖
)
echo.

REM 创建目录
echo 7. 创建数据目录...
if not exist data mkdir data
if not exist logs mkdir logs
echo 目录已创建
echo.

REM 配置环境变量
echo 8. 配置环境变量...
if not exist .env (
    copy .env.example .env
    echo 已创建 .env 文件
    echo.
    echo 重要: 请编辑 .env 文件并配置以下 API keys:
    echo   - OPENAI_API_KEY（推荐）
    echo   - DEEPL_API_KEY（可选）
    echo.
    echo 至少需要配置一个翻译 API 才能使用翻译功能
    echo.
    echo 是否现在打开 .env 文件进行编辑? (Y/N)
    set /p edit_env=
    if /i "%edit_env%"=="Y" (
        notepad .env
    )
) else (
    echo .env 文件已存在
)
echo.

REM 测试安装
echo 9. 测试安装...
python main.py --help >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 安装测试失败
    pause
    exit /b 1
)
echo 安装测试通过
echo.

REM 完成
echo ================================================
echo 安装完成！
echo ================================================
echo.
echo 下一步操作:
echo.
echo 1. 确保已配置 .env 文件中的 API keys
echo    编辑命令: notepad .env
echo.
echo 2. 激活虚拟环境:
echo    venv\Scripts\activate.bat
echo.
echo 3. 运行应用:
echo    python main.py --help        # 查看帮助
echo    python main.py pipeline      # 运行完整流程
echo    start.bat                    # 使用启动脚本
echo.
echo 4. 查看文档:
echo    type README.md
echo.
echo 提示: 运行 test.bat 进行快速测试
echo.
pause
