#!/usr/bin/env python3
"""
测试 Outlook 注册脚本，捕获详细错误
"""

import asyncio
import sys
import traceback

async def test_outlook_registration():
    """测试 Outlook 注册流程"""
    print("开始测试 Outlook 注册...")
    
    try:
        # 导入 playwright
        from playwright.async_api import async_playwright
        print("[OK] Playwright 导入成功")
        
        # 启动浏览器
        print("启动浏览器...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-web-security',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # 添加反检测脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            """)
            
            page = await context.new_page()
            
            # 访问 Outlook 注册页面
            print("访问 Outlook 注册页面...")
            try:
                await page.goto('https://signup.live.com/signup', wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(5000)
            except Exception as e:
                print(f"[WARNING] 页面加载超时，尝试继续...")
                await page.wait_for_timeout(10000)
            
            # 截图
            await page.screenshot(path='test_outlook_step1.png')
            print("[OK] 页面加载成功，截图已保存: test_outlook_step1.png")
            
            # 检查页面标题
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 检测验证码类型
            print("\n检测验证码类型...")
            
            # 检查 reCAPTCHA
            recaptcha_elements = await page.query_selector_all('iframe[src*="recaptcha"], .g-recaptcha, #recaptcha')
            if recaptcha_elements:
                print(f"[INFO] 检测到 reCAPTCHA: {len(recaptcha_elements)} 个")
                for i, elem in enumerate(recaptcha_elements):
                    src = await elem.get_attribute('src')
                    data_sitekey = await elem.get_attribute('data-sitekey')
                    print(f"  reCAPTCHA {i+1}: src={src}, sitekey={data_sitekey}")
            
            # 检查 hCaptcha
            hcaptcha_elements = await page.query_selector_all('iframe[src*="hcaptcha"], .h-captcha')
            if hcaptcha_elements:
                print(f"[INFO] 检测到 hCaptcha: {len(hcaptcha_elements)} 个")
            
            # 检查其他验证码
            captcha_elements = await page.query_selector_all('iframe[src*="captcha"], #captcha, .captcha')
            if captcha_elements:
                print(f"[INFO] 检测到其他验证码: {len(captcha_elements)} 个")
            
            # 检查短信验证
            phone_elements = await page.query_selector_all('input[type="tel"], input[name*="phone"], input[aria-label*="phone"]')
            if phone_elements:
                print(f"[INFO] 检测到手机号验证: {len(phone_elements)} 个")
            
            # 检查邮箱验证
            email_verify_elements = await page.query_selector_all('input[name*="code"], input[aria-label*="code"], input[placeholder*="code"]')
            if email_verify_elements:
                print(f"[INFO] 检测到邮箱验证码: {len(email_verify_elements)} 个")
            
            # 检查页面内容
            page_content = await page.content()
            if 'captcha' in page_content.lower():
                print("[INFO] 页面包含验证码相关内容")
            
            # 截图当前页面状态
            await page.screenshot(path='test_outlook_step2.png')
            print("[OK] 验证码检测完成，截图已保存: test_outlook_step2.png")
            
            # 等待用户查看
            print("\n浏览器已打开，请查看页面状态...")
            print("按 Enter 键关闭浏览器...")
            input()
            
            await browser.close()
            print("[OK] 测试完成")
            
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        traceback.print_exc()
        return False
    
    return True

def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   Outlook 注册测试工具                                           ║
║   检测验证码问题                                                  ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("[ERROR] 需要 Python 3.8 或更高版本")
        return
    
    # 运行测试
    success = asyncio.run(test_outlook_registration())
    
    if success:
        print("\n[OK] 测试完成，请查看截图了解页面状态")
    else:
        print("\n[ERROR] 测试失败，请查看错误信息")

if __name__ == '__main__':
    main()