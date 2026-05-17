#!/usr/bin/env python3
"""
测试环境是否正确配置
"""

import sys
import time

def test_python():
    """测试 Python 版本"""
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    return True

def test_packages():
    """测试必要的包"""
    packages = ['playwright', 'requests']
    results = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
            results.append(True)
        except ImportError:
            print(f"❌ {package}: 未安装")
            results.append(False)
    
    return all(results)

def test_playwright_browser():
    """测试 Playwright 浏览器"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✅ Playwright 浏览器: 已安装")
            return True
    except Exception as e:
        print(f"❌ Playwright 浏览器: {e}")
        return False

def test_network():
    """测试网络连接"""
    try:
        import requests
        response = requests.get("https://domain.stackryze.com", timeout=10)
        print(f"✅ 网络连接: 正常 (状态码 {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ 网络连接: {e}")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   环境测试工具                                                     ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("[1/4] 测试 Python...")
    test_python()
    
    print("\n[2/4] 测试依赖包...")
    packages_ok = test_packages()
    
    print("\n[3/4] 测试 Playwright 浏览器...")
    playwright_ok = test_playwright_browser() if packages_ok else False
    
    print("\n[4/4] 测试网络连接...")
    network_ok = test_network()
    
    print("\n" + "="*60)
    print("测试结果总结：")
    print("="*60)
    
    if packages_ok and playwright_ok and network_ok:
        print("✅ 所有测试通过！环境配置正确。")
        print("\n现在可以运行 '一键注册.py' 或 '点击运行.bat' 了。")
    else:
        print("❌ 部分测试失败，请按以下步骤修复：")
        
        if not packages_ok:
            print("\n1. 安装依赖包：")
            print("   pip install playwright requests")
        
        if not playwright_ok:
            print("\n2. 安装 Playwright 浏览器：")
            print("   playwright install chromium")
        
        if not network_ok:
            print("\n3. 检查网络连接：")
            print("   - 确保能访问互联网")
            print("   - 检查防火墙设置")
    
    print("\n" + "="*60)
    input("\n按 Enter 键退出...")

if __name__ == '__main__':
    main()