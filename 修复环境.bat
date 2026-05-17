@echo off
chcp 65001 >nul
title 修复环境 - Stackryze 域名自动注册工具

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   修复环境工具                                                     ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

echo [步骤 1] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装！
    echo.
    echo 请按以下步骤安装 Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载 Python 3.10 或更高版本
    echo 3. 运行安装程序
    echo 4. 重要：勾选 "Add Python to PATH"！
    echo 5. 点击 "Install Now"
    echo.
    echo 安装完成后重新运行此脚本。
    pause
    exit /b 1
)
echo [成功] Python 已安装

echo.
echo [步骤 2] 安装依赖包...
echo 正在安装 playwright 和 requests...
pip install playwright requests
if errorlevel 1 (
    echo [错误] 安装失败！
    pause
    exit /b 1
)
echo [成功] 依赖包安装完成

echo.
echo [步骤 3] 安装 Playwright 浏览器...
echo 正在安装 Chromium 浏览器（可能需要几分钟）...
playwright install chromium
if errorlevel 1 (
    echo [错误] 浏览器安装失败！
    pause
    exit /b 1
)
echo [成功] 浏览器安装完成

echo.
echo [步骤 4] 测试环境...
python 测试环境.py

echo.
echo ═══════════════════════════════════════════════════════════════════
echo 环境修复完成！
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 现在可以运行以下命令：
echo   - 双击 "点击运行.bat" 开始注册域名
echo   - 或运行 "python 一键注册.py"
echo.
pause