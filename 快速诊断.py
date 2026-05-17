#!/usr/bin/env python3
"""
快速诊断脚本 - 找出问题所在
"""

import sys
import os
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_python():
    """检查 Python"""
    print_header("检查 Python")
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    
    # 检查版本
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python 版本符合要求")
        return True
    else:
        print("❌ Python 版本过低，需要 3.8 或更高版本")
        return False

def check_pip():
    """检查 pip"""
    print_header("检查 pip")
    try:
        import pip
        print(f"pip 版本: {pip.__version__}")
        print("✅ pip 已安装")
        return True
    except ImportError:
        print("❌ pip 未安装")
        return False

def check_packages():
    """检查依赖包"""
    print_header("检查依赖包")
    
    packages = {
        'playwright': 'playwright',
        'requests': 'requests'
    }
    
    all_ok = True
    for name, package in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name}: 未安装")
            all_ok = False
    
    return all_ok

def check_playwright_browser():
    """检查 Playwright 浏览器"""
    print_header("检查 Playwright 浏览器")
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright 模块已导入")
        
        # 尝试启动浏览器
        print("正在测试浏览器启动...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✅ 浏览器启动成功")
            return True
    except Exception as e:
        print(f"❌ 浏览器启动失败: {e}")
        return False

def check_network():
    """检查网络连接"""
    print_header("检查网络连接")
    
    urls = [
        ("domain.stackryze.com", "https://domain.stackryze.com"),
        ("github.com", "https://github.com"),
        ("api.cloudflare.com", "https://api.cloudflare.com")
    ]
    
    all_ok = True
    for name, url in urls:
        try:
            import requests
            response = requests.get(url, timeout=10)
            print(f"✅ {name}: 连接正常 (状态码 {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: 连接失败 ({e})")
            all_ok = False
    
    return all_ok

def check_permissions():
    """检查文件权限"""
    print_header("检查文件权限")
    
    # 检查当前目录是否可写
    try:
        test_file = "test_permission.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ 当前目录可写")
        return True
    except Exception as e:
        print(f"❌ 当前目录不可写: {e}")
        return False

def provide_solutions(results):
    """提供解决方案"""
    print_header("诊断结果和解决方案")
    
    if all(results.values()):
        print("🎉 所有检查通过！环境配置正确。")
        print("\n现在可以运行以下命令：")
        print("  - 双击 '点击运行.bat'")
        print("  - 或运行 'python 一键注册.py'")
        return
    
    print("❌ 发现问题，请按以下步骤修复：\n")
    
    if not results['python']:
        print("1. 【Python 问题】")
        print("   - 访问 https://www.python.org/downloads/")
        print("   - 下载 Python 3.10 或更高版本")
        print("   - 安装时务必勾选 'Add Python to PATH'")
        print("   - 安装完成后重新运行此脚本\n")
    
    if not results['packages']:
        print("2. 【依赖包问题】")
        print("   - 运行以下命令安装依赖：")
        print("     pip install playwright requests\n")
    
    if not results['playwright']:
        print("3. 【Playwright 浏览器问题】")
        print("   - 运行以下命令安装浏览器：")
        print("     playwright install chromium\n")
    
    if not results['network']:
        print("4. 【网络连接问题】")
        print("   - 检查网络连接是否正常")
        print("   - 确保能访问 https://domain.stackryze.com")
        print("   - 检查防火墙设置\n")
    
    print("【快速修复】")
    print("   运行以下命令一键修复：")
    print("   pip install playwright requests")
    print("   playwright install chromium")
    print("\n   或双击 '修复环境.bat' 自动修复")

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   快速诊断工具 - 找出问题所在                                     ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'python': check_python(),
        'pip': check_pip(),
        'packages': check_packages(),
        'playwright': check_playwright_browser(),
        'network': check_network(),
        'permissions': check_permissions()
    }
    
    provide_solutions(results)
    
    print("\n" + "="*60)
    input("\n按 Enter 键退出...")

if __name__ == '__main__':
    main()