@echo off
chcp 65001 >nul
title Outlook 邮箱自动注册工具

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   Outlook 邮箱自动注册工具                                        ║
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
    pip install playwright
    playwright install chromium
)

echo 启动 Outlook 注册脚本...
echo.

python 注册Outlook邮箱.py

pause