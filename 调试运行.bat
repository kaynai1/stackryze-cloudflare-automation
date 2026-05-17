@echo off
chcp 65001 >nul
title 调试运行 - Stackryze 域名自动注册工具

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   调试模式运行                                                   ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 检查 Python...
python --version
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH！
    echo 请安装 Python 并勾选 "Add Python to PATH"
    goto :error
)

echo.
echo [2/5] 检查 pip...
pip --version
if errorlevel 1 (
    echo [错误] pip 未安装！
    goto :error
)

echo.
echo [3/5] 检查依赖包...
pip show playwright
if errorlevel 1 (
    echo [提示] 正在安装 playwright...
    pip install playwright
)

pip show requests
if errorlevel 1 (
    echo [提示] 正在安装 requests...
    pip install requests
)

echo.
echo [4/5] 检查 Playwright 浏览器...
python -c "from playwright.sync_api import sync_playwright; print('Playwright 已安装')"
if errorlevel 1 (
    echo [提示] 正在安装 Playwright 浏览器...
    playwright install chromium
)

echo.
echo [5/5] 运行脚本...
echo ───────────────────────────────────────────────────────────────────
echo.

python 一键注册.py

echo.
echo ───────────────────────────────────────────────────────────────────
echo 脚本已退出
goto :end

:error
echo.
echo ───────────────────────────────────────────────────────────────────
echo 发生错误，请检查上述信息
echo ───────────────────────────────────────────────────────────────────

:end
echo.
echo 按任意键退出...
pause >nul