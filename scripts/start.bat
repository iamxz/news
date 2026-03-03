@echo off
REM Windows 启动脚本

echo ================================================
echo 全球新闻聚合工具 - 启动 (Windows)
echo ================================================
echo.

REM 检查虚拟环境
if not exist venv (
    echo 错误: 虚拟环境不存在
    echo 请先运行: install.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查 .env 文件
if not exist .env (
    echo 警告: .env 文件不存在
    echo 翻译和验证功能可能不可用
    echo.
    echo 是否继续? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" exit /b 1
)

:menu
echo.
echo 请选择操作:
echo.
echo   1) 运行完整流程 (抓取 -^> 翻译 -^> 验证)
echo   2) 仅抓取新闻
echo   3) 翻译未翻译的新闻
echo   4) 验证未验证的新闻
echo   5) 查看新闻列表
echo   6) 查看统计信息
echo   7) 清理旧新闻
echo   8) 自定义命令
echo   0) 退出
echo.
set /p choice=请输入选项 [0-8]: 

if "%choice%"=="1" goto pipeline
if "%choice%"=="2" goto fetch
if "%choice%"=="3" goto translate
if "%choice%"=="4" goto validate
if "%choice%"=="5" goto show
if "%choice%"=="6" goto stats
if "%choice%"=="7" goto clean
if "%choice%"=="8" goto custom
if "%choice%"=="0" goto exit
echo 无效选项，请重新选择
goto menu

:pipeline
echo.
echo 运行完整流程...
echo.
python main.py pipeline
goto continue

:fetch
echo.
echo 请选择新闻源:
echo   1) 全部
echo   2) Reuters (路透社)
echo   3) Hacker News
echo.
set /p source_choice=请选择 [1-3]: 

if "%source_choice%"=="1" (
    python main.py fetch
) else if "%source_choice%"=="2" (
    python main.py fetch -s reuters
) else if "%source_choice%"=="3" (
    python main.py fetch -s hackernews
) else (
    echo 无效选项
)
goto continue

:translate
echo.
set /p limit=翻译数量 (默认 10): 
if "%limit%"=="" set limit=10
python main.py translate -l %limit%
goto continue

:validate
echo.
set /p limit=验证数量 (默认 10): 
if "%limit%"=="" set limit=10
python main.py validate -l %limit%
goto continue

:show
echo.
echo 查看新闻列表...
echo.
set /p limit=显示数量 (默认 20): 
if "%limit%"=="" set limit=20

echo 显示模式:
echo 1 - 普通模式
echo 2 - 双语模式
set /p mode=请选择 [1-2] (默认 2): 
if "%mode%"=="" set mode=2

set /p credibility=最低可信度 (0.0-1.0, 回车跳过): 
set /p days=最近几天 (回车跳过): 

if "%mode%"=="1" (
    set cmd=python main.py show -l %limit%
) else (
    set cmd=python main.py show -l %limit% --bilingual
)

if not "%credibility%"=="" set cmd=%cmd% -m %credibility%
if not "%days%"=="" set cmd=%cmd% -d %days%

%cmd%
goto continue

:stats
echo.
python main.py stats
goto continue

:clean
echo.
set /p days=保留最近几天 (默认 30): 
if "%days%"=="" set days=30
python main.py clean -d %days%
goto continue

:custom
echo.
echo 自定义命令
echo.
echo 可用命令:
python main.py --help
echo.
set /p custom_cmd=请输入命令 (例: show -s Reuters -l 10): 
python main.py %custom_cmd%
goto continue

:continue
echo.
pause
goto menu

:exit
echo 再见！
exit /b 0
