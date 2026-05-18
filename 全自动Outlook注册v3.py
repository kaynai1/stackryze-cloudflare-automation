#!/usr/bin/env python3
"""
全自动 Outlook 注册 v3 - 集成验证码解决服务
支持：
1. 随机生成账号密码、姓名、出生日期
2. 自动填写所有表单
3. 自动解决验证码（需要第三方服务API密钥）
"""

import asyncio
import json
import random
import string
import time
import requests
from datetime import datetime

from playwright.async_api import async_playwright


class CaptchaSolver:
    """验证码解决器"""
    
    def __init__(self, provider='2captcha', api_key=None):
        self.provider = provider
        self.api_key = api_key
        self.base_url = {
            '2captcha': 'http://2captcha.com',
            'anticaptcha': 'https://api.anti-captcha.com'
        }.get(provider)
    
    async def solve_recaptcha_v2(self, site_key, page_url):
        """解决 reCAPTCHA v2"""
        if not self.api_key:
            print("[ERROR] 需要验证码服务API密钥")
            return None
        
        try:
            # 创建任务
            if self.provider == '2captcha':
                return await self._solve_2captcha_recaptcha_v2(site_key, page_url)
            elif self.provider == 'anticaptcha':
                return await self._solve_anticaptcha_recaptcha_v2(site_key, page_url)
        except Exception as e:
            print(f"[ERROR] 验证码解决失败: {e}")
            return None
    
    async def _solve_2captcha_recaptcha_v2(self, site_key, page_url):
        """使用2captcha解决reCAPTCHA v2"""
        # 发送验证码请求
        data = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1
        }
        
        response = requests.post(f'{self.base_url}/in.php', data=data)
        result = response.json()
        
        if result.get('status') != 1:
            print(f"[ERROR] 创建验证码任务失败: {result}")
            return None
        
        task_id = result['request']
        print(f"[INFO] 验证码任务已创建: {task_id}")
        
        # 等待解决
        for i in range(60):  # 最多等待5分钟
            await asyncio.sleep(5)
            response = requests.get(f'{self.base_url}/res.php?key={self.api_key}&action=get&id={task_id}&json=1')
            result = response.json()
            
            if result.get('status') == 1:
                print("[OK] 验证码已解决")
                return result['request']
            elif result.get('request') == 'CAPCHA_NOT_READY':
                print(f"[INFO] 等待验证码解决... ({i+1}/60)")
            else:
                print(f"[ERROR] 验证码解决失败: {result}")
                return None
        
        print("[ERROR] 验证码解决超时")
        return None
    
    async def _solve_anticaptcha_recaptcha_v2(self, site_key, page_url):
        """使用AntiCaptcha解决reCAPTCHA v2"""
        # 创建任务
        task_data = {
            "clientKey": self.api_key,
            "task": {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        
        response = requests.post(f'{self.base_url}/createTask', json=task_data)
        result = response.json()
        
        if result.get('errorId') != 0:
            print(f"[ERROR] 创建验证码任务失败: {result}")
            return None
        
        task_id = result['taskId']
        print(f"[INFO] 验证码任务已创建: {task_id}")
        
        # 等待解决
        for i in range(60):
            await asyncio.sleep(5)
            status_data = {
                "clientKey": self.api_key,
                "taskId": task_id
            }
            response = requests.post(f'{self.base_url}/getTaskResult', json=status_data)
            result = response.json()
            
            if result.get('status') == 'ready':
                print("[OK] 验证码已解决")
                return result['solution']['gRecaptchaResponse']
            elif result.get('errorId') == 0:
                print(f"[INFO] 等待验证码解决... ({i+1}/60)")
            else:
                print(f"[ERROR] 验证码解决失败: {result}")
                return None
        
        print("[ERROR] 验证码解决超时")
        return None


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_password():
    """生成随机密码"""
    uppercase = random.choice(string.ascii_uppercase)
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=4))
    digits = ''.join(random.choices(string.digits, k=2))
    special = random.choice('!@#$%^&*')
    
    password = uppercase + lowercase + digits + special
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_birth_date():
    """生成随机出生日期（18-35岁）"""
    year = random.randint(1989, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return year, month, day


async def wait_and_click(page, selectors, timeout=10000):
    """等待并点击元素"""
    for selector in selectors:
        try:
            element = page.locator(selector)
            if await element.is_visible(timeout=2000):
                await element.click()
                return True
        except:
            continue
    return False


async def wait_and_fill(page, selectors, value, timeout=10000):
    """等待并填写输入框"""
    for selector in selectors:
        try:
            element = page.locator(selector)
            if await element.is_visible(timeout=2000):
                await element.fill(value)
                return True
        except:
            continue
    return False


async def register_outlook(captcha_solver=None):
    """注册 Outlook 邮箱 - 完全自动化"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   Outlook 邮箱全自动注册工具 v3                                   ║
║   随机生成信息，自动解决验证码                                      ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 生成随机信息
    prefix = generate_random_string(10)
    email = f"{prefix}@outlook.com"
    password = generate_password()
    
    first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
                   'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    birth_year, birth_month, birth_day = generate_birth_date()
    
    print(f"\n生成的信息：")
    print(f"邮箱: {email}")
    print(f"密码: {password}")
    print(f"姓名: {first_name} {last_name}")
    print(f"出生日期: {birth_year}-{birth_month:02d}-{birth_day:02d}")
    
    print(f"\n{'='*60}")
    print("正在启动浏览器，请勿关闭窗口...")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        # 使用更真实的浏览器配置
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
        
        try:
            # 访问 Outlook 注册页面
            print("[1/6] 访问 Outlook 注册页面...")
            await page.goto('https://signup.live.com/signup', wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(5000)
            
            # 点击 "获取新邮箱" 或直接开始
            print("[2/6] 准备注册...")
            await wait_and_click(page, [
                'a:has-text("Get a new email address")',
                'a:has-text("获取新的电子邮件地址")',
                'text=Create one',
                'text=No account? Create one',
                'a:has-text("Create")'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入邮箱地址
            print(f"[3/6] 输入邮箱地址: {email}")
            await wait_and_fill(page, [
                'input[name="MemberName"]',
                'input[type="email"]',
                'input[aria-label*="email"]',
                'input[placeholder*="email"]',
                '#MemberName'
            ], email)
            
            # 点击下一步
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("下一步")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入密码
            print(f"[4/6] 输入密码: {password}")
            await wait_and_fill(page, [
                'input[name="Password"]',
                'input[type="password"]',
                'input[aria-label*="password"]',
                'input[placeholder*="password"]',
                '#PasswordInput'
            ], password)
            
            # 点击下一步
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("下一步")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入姓名
            print(f"[5/6] 输入姓名: {first_name} {last_name}")
            
            # 输入名
            await wait_and_fill(page, [
                'input[name="FirstName"]',
                'input[aria-label*="First name"]',
                'input[placeholder*="First"]',
                '#FirstNameInput'
            ], first_name)
            
            # 输入姓
            await wait_and_fill(page, [
                'input[name="LastName"]',
                'input[aria-label*="Last name"]',
                'input[placeholder*="Last"]',
                '#LastNameInput'
            ], last_name)
            
            # 点击下一步
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("下一步")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入出生日期
            print(f"[6/6] 输入出生日期...")
            
            # 选择国家/地区
            await wait_and_click(page, [
                'select[name="Country"]',
                'select[aria-label*="Country"]',
                '#Country'
            ])
            await page.wait_for_timeout(500)
            await wait_and_click(page, ['option[value="US"]', 'text=United States'])
            
            # 选择出生年份
            await wait_and_click(page, [
                'select[name="BirthYear"]',
                'select[aria-label*="Year"]',
                '#BirthYear'
            ])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_year}"]'])
            
            # 选择出生月份
            await wait_and_click(page, [
                'select[name="BirthMonth"]',
                'select[aria-label*="Month"]',
                '#BirthMonth'
            ])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_month}"]'])
            
            # 选择出生日期
            await wait_and_click(page, [
                'select[name="BirthDay"]',
                'select[aria-label*="Day"]',
                '#BirthDay'
            ])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_day}"]'])
            
            # 点击下一步
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("下一步")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 处理验证码
            print("\n" + "="*60)
            print("处理验证码")
            print("="*60)
            
            # 检测验证码类型
            recaptcha_elements = await page.query_selector_all('iframe[src*="recaptcha"], .g-recaptcha')
            hcaptcha_elements = await page.query_selector_all('iframe[src*="hcaptcha"], .h-captcha')
            
            if recaptcha_elements and captcha_solver:
                print("[INFO] 检测到 reCAPTCHA，尝试自动解决...")
                # 获取 sitekey
                site_key = None
                for elem in recaptcha_elements:
                    site_key = await elem.get_attribute('data-sitekey')
                    if site_key:
                        break
                
                if site_key:
                    print(f"[INFO] reCAPTCHA sitekey: {site_key}")
                    solution = await captcha_solver.solve_recaptcha_v2(site_key, page.url)
                    
                    if solution:
                        # 注入验证码解决方案
                        await page.evaluate(f'''
                            document.getElementById('g-recaptcha-response').value = '{solution}';
                            if (typeof ___grecaptcha_cfg !== 'undefined') {{
                                Object.keys(___grecaptcha_cfg.clients).forEach(key => {{
                                    const client = ___grecaptcha_cfg.clients[key];
                                    if (client) {{
                                        Object.keys(client).forEach(prop => {{
                                            const obj = client[prop];
                                            if (obj && obj.callback) {{
                                                obj.callback('{solution}');
                                            }}
                                        }});
                                    }}
                                }});
                            }}
                        ''')
                        print("[OK] 验证码解决方案已注入")
                    else:
                        print("[WARNING] 验证码自动解决失败，需要手动处理")
                        input("请在浏览器中手动完成验证码，然后按 Enter 继续...")
                else:
                    print("[WARNING] 无法获取 reCAPTCHA sitekey")
                    input("请在浏览器中手动完成验证码，然后按 Enter 继续...")
            
            elif hcaptcha_elements:
                print("[INFO] 检测到 hCaptcha，需要手动处理")
                input("请在浏览器中手动完成 hCaptcha 验证码，然后按 Enter 继续...")
            
            else:
                print("[INFO] 未检测到标准验证码，可能需要其他验证方式")
                # 检查是否需要手机验证
                phone_elements = await page.query_selector_all('input[type="tel"], input[name*="phone"]')
                if phone_elements:
                    print("[INFO] 检测到手机号验证")
                    input("请在浏览器中完成手机号验证，然后按 Enter 继续...")
                else:
                    print("[INFO] 继续注册流程...")
            
            # 等待页面跳转
            print("\n等待页面跳转...")
            await page.wait_for_timeout(5000)
            
            # 检查是否需要同意条款
            try:
                await wait_and_click(page, [
                    'button:has-text("Accept")',
                    'button:has-text("I agree")',
                    'button:has-text("同意")',
                    'button:has-text("Yes")',
                    '#idSIButton9'
                ], timeout=5000)
            except:
                pass
            
            await page.wait_for_timeout(3000)
            
            # 截图保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"outlook_success_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"\n截图已保存: {screenshot_path}")
            
            # 检查注册结果
            current_url = page.url
            page_title = await page.title()
            
            print(f"\n当前页面: {current_url}")
            print(f"页面标题: {page_title}")
            
            # 判断是否注册成功
            if any(keyword in current_url.lower() for keyword in ['outlook', 'mail', 'inbox', 'live.com']):
                print(f"\n{'='*60}")
                print("🎉 Outlook 邮箱注册成功！")
                print(f"{'='*60}")
                print(f"\n邮箱: {email}")
                print(f"密码: {password}")
                print(f"姓名: {first_name} {last_name}")
                print(f"出生日期: {birth_year}-{birth_month:02d}-{birth_day:02d}")
                print(f"{'='*60}")
                
                # 保存账号信息
                with open('outlook_accounts.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"邮箱: {email}\n")
                    f.write(f"密码: {password}\n")
                    f.write(f"姓名: {first_name} {last_name}\n")
                    f.write(f"出生日期: {birth_year}-{birth_month:02d}-{birth_day:02d}\n")
                    f.write(f"创建时间: {datetime.now().isoformat()}\n")
                    f.write(f"{'='*60}\n")
                
                print(f"\n账号信息已保存到: outlook_accounts.txt")
                
                await browser.close()
                return {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name
                }
            else:
                print(f"\n⚠️  注册可能未完成")
                print("请检查浏览器状态，手动完成剩余步骤")
                input("\n按 Enter 关闭浏览器...")
                
                await browser.close()
                return None
                
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"outlook_error_{timestamp}.png")
            input("\n按 Enter 关闭浏览器...")
            await browser.close()
            return None


async def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   全自动 Outlook 注册工具 v3                                     ║
║   随机生成信息，自动解决验证码                                      ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 验证码服务配置
    print("验证码服务配置（可选）：")
    print("1. 2captcha (需要API密钥)")
    print("2. AntiCaptcha (需要API密钥)")
    print("3. 不使用验证码服务（手动处理验证码）")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    captcha_solver = None
    if choice == '1':
        api_key = input("请输入 2captcha API密钥: ").strip()
        if api_key:
            captcha_solver = CaptchaSolver(provider='2captcha', api_key=api_key)
    elif choice == '2':
        api_key = input("请输入 AntiCaptcha API密钥: ").strip()
        if api_key:
            captcha_solver = CaptchaSolver(provider='anticaptcha', api_key=api_key)
    
    # 开始注册
    account = await register_outlook(captcha_solver)
    
    if account:
        print(f"\n✅ 注册完成！")
        print(f"\n邮箱: {account['email']}")
        print(f"密码: {account['password']}")
        print(f"\n您可以使用此邮箱注册 Stackryze 账号")
    else:
        print(f"\n❌ 注册失败，请重试")


if __name__ == '__main__':
    asyncio.run(main())