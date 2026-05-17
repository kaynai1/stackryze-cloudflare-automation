@echo off
chcp 65001 >nul
title Stackryze 域名自动注册工具

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   Stackryze 域名 → 自动托管到 Cloudflare                         ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装 Python
    echo 3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 检查依赖
echo [1/2] 检查依赖...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo [2/2] 安装依赖（首次运行需要）...
    pip install -r requirements.txt
    playwright install chromium
) else (
    echo [2/2] 依赖已安装
)

echo.
echo ───────────────────────────────────────────────────────────────────
echo 启动自动化脚本...
echo ───────────────────────────────────────────────────────────────────
echo.

python 一键注册.py

echo.
echo 按任意键退出...
pause >nul