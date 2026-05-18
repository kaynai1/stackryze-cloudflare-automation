@echo off
chcp 65001 >nul
title 全自动 Outlook 注册 v3

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   全自动 Outlook 注册工具 v3                                     ║
echo ║   随机生成信息，自动解决验证码                                      ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install playwright requests
    playwright install chromium
)

echo 启动全自动注册脚本...
echo.

python 全自动Outlook注册v3.py

pause