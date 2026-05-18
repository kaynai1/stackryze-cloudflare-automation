#!/usr/bin/env python3
"""
快速测试 Outlook 注册页面加载
"""

import asyncio
from playwright.async_api import async_playwright

async def test():
    print("快速测试 Outlook 注册页面...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 测试页面加载
            print("访问 signup.live.com...")
            await page.goto('https://signup.live.com/signup', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # 截图
            await page.screenshot(path='quick_test.png')
            print("[OK] 页面加载成功，截图已保存: quick_test.png")
            
            # 检查页面标题
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 检查是否有验证码
            recaptcha = await page.query_selector_all('iframe[src*="recaptcha"]')
            hcaptcha = await page.query_selector_all('iframe[src*="hcaptcha"]')
            
            if recaptcha:
                print(f"[INFO] 检测到 reCAPTCHA: {len(recaptcha)} 个")
            if hcaptcha:
                print(f"[INFO] 检测到 hCaptcha: {len(hcaptcha)} 个")
            
            # 检查表单元素
            email_input = await page.query_selector('input[name="MemberName"], input[type="email"]')
            if email_input:
                print("[OK] 找到邮箱输入框")
            
            print("\n测试完成！页面可以正常加载。")
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test())