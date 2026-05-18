@echo off
chcp 65001 >nul
title 使用已有 Outlook 账号注册 Stackryze

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   使用已有 Outlook 账号注册 Stackryze 域名                       ║
echo ║   从 outlook_accounts.txt 读取账号信息                           ║
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

echo 启动注册脚本...
echo.

python 使用已有Outlook账号.py

pause