#!/usr/bin/env python3
"""
全自动注册流程 v2 - 改进版
1. 自动注册 Outlook 邮箱（改进版）
2. 用 Outlook 邮箱注册 Stackryze
3. 注册域名
4. 托管到 Cloudflare
"""

import asyncio
import json
import random
import string
import time
from datetime import datetime

import requests
from playwright.async_api import async_playwright


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


async def register_outlook_email():
    """注册 Outlook 邮箱 - 改进版"""
    print("\n" + "="*60)
    print("步骤 1: 注册 Outlook 邮箱")
    print("="*60)
    
    # 生成随机信息
    prefix = generate_random_string(10)
    email = f"{prefix}@outlook.com"
    password = generate_password()
    
    first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    birth_year, birth_month, birth_day = generate_birth_date()
    
    print(f"生成邮箱: {email}")
    print(f"生成密码: {password}")
    print(f"生成姓名: {first_name} {last_name}")
    
    async with async_playwright() as p:
        # 使用更真实的浏览器配置
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-web-security',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )
        
        # 添加反检测脚本
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}};
        """)
        
        page = await context.new_page()
        
        try:
            # 访问 Outlook 注册页面
            print("访问 Outlook 注册页面...")
            await page.goto('https://signup.live.com/signup', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 点击获取新邮箱
            await wait_and_click(page, [
                'a:has-text("Get a new email address")',
                'a:has-text("获取新的电子邮件地址")',
                'text=Create one',
                'text=No account? Create one'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入邮箱
            print("输入邮箱地址...")
            await wait_and_fill(page, [
                'input[name="MemberName"]',
                'input[type="email"]',
                '#MemberName'
            ], email)
            
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入密码
            print("输入密码...")
            await wait_and_fill(page, [
                'input[name="Password"]',
                'input[type="password"]',
                '#PasswordInput'
            ], password)
            
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入姓名
            print("输入姓名...")
            await wait_and_fill(page, [
                'input[name="FirstName"]',
                'input[aria-label*="First name"]',
                '#FirstNameInput'
            ], first_name)
            
            await wait_and_fill(page, [
                'input[name="LastName"]',
                'input[aria-label*="Last name"]',
                '#LastNameInput'
            ], last_name)
            
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 输入出生日期
            print("输入出生日期...")
            
            # 选择国家
            await wait_and_click(page, ['select[name="Country"]', '#Country'])
            await page.wait_for_timeout(500)
            await wait_and_click(page, ['option[value="US"]'])
            
            # 选择年份
            await wait_and_click(page, ['select[name="BirthYear"]', '#BirthYear'])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_year}"]'])
            
            # 选择月份
            await wait_and_click(page, ['select[name="BirthMonth"]', '#BirthMonth'])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_month}"]'])
            
            # 选择日期
            await wait_and_click(page, ['select[name="BirthDay"]', '#BirthDay'])
            await page.wait_for_timeout(500)
            await wait_and_click(page, [f'option[value="{birth_day}"]'])
            
            await wait_and_click(page, [
                'input[type="submit"]',
                'button:has-text("Next")',
                '#idSIButton9'
            ])
            await page.wait_for_timeout(2000)
            
            # 处理验证
            print("\n⚠️  请在浏览器中完成验证...")
            print("完成后按 Enter 继续...")
            input()
            
            # 等待跳转
            await page.wait_for_timeout(5000)
            
            # 检查结果
            current_url = page.url
            if any(keyword in current_url.lower() for keyword in ['outlook', 'mail', 'inbox', 'live.com']):
                print(f"✅ Outlook 邮箱注册成功: {email}")
                
                # 保存账号信息
                with open('outlook_accounts.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n邮箱: {email}\n密码: {password}\n时间: {datetime.now()}\n")
                
                await browser.close()
                return {'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name}
            else:
                print("❌ Outlook 邮箱注册失败")
                await browser.close()
                return None
                
        except Exception as e:
            print(f"❌ 注册出错: {e}")
            await browser.close()
            return None


async def register_stackryze(outlook_email, outlook_password, domain_prefix):
    """用 Outlook 邮箱注册 Stackryze"""
    print("\n" + "="*60)
    print("步骤 2: 注册 Stackryze 域名")
    print("="*60)
    
    print(f"使用邮箱: {outlook_email}")
    print(f"注册域名: {domain_prefix}.indevs.in")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        try:
            # 访问 Stackryze
            print("访问 domain.stackryze.com...")
            await page.goto('https://domain.stackryze.com')
            await page.wait_for_load_state('networkidle')
            
            # 点击登录
            print("点击登录...")
            await wait_and_click(page, [
                'a:has-text("Get Started")',
                'a:has-text("Login")',
                'button:has-text("Login")'
            ])
            await page.wait_for_load_state('networkidle')
            
            # 尝试邮箱注册
            try:
                await wait_and_click(page, [
                    'a:has-text("Sign up")',
                    'button:has-text("Register")',
                    'a:has-text("Register")'
                ])
                await page.wait_for_timeout(1000)
                
                print("输入邮箱...")
                await wait_and_fill(page, [
                    'input[name="email"]',
                    'input[type="email"]'
                ], outlook_email)
                
                await wait_and_fill(page, [
                    'input[name="password"]',
                    'input[type="password"]'
                ], outlook_password)
                
                await wait_and_click(page, [
                    'button:has-text("Register")',
                    'button:has-text("Sign up")',
                    'input[type="submit"]'
                ])
                await page.wait_for_timeout(3000)
                
                # 检查邮箱验证
                print("检查邮箱验证...")
                print("请检查 Outlook 邮箱，输入验证码（如果有）")
                verification_code = input("验证码（如无需验证直接按 Enter）: ").strip()
                
                if verification_code:
                    await wait_and_fill(page, [
                        'input[name="code"]',
                        'input[type="text"]'
                    ], verification_code)
                    
                    await wait_and_click(page, [
                        'button:has-text("Verify")',
                        'button:has-text("Confirm")'
                    ])
                    await page.wait_for_timeout(2000)
                
            except Exception as e:
                print(f"邮箱注册失败，尝试 GitHub 登录: {e}")
                await wait_and_click(page, [
                    'button:has-text("GitHub")',
                    'a:has-text("GitHub")'
                ])
                await page.wait_for_load_state('networkidle')
                await page.fill('input[name="login"], input[id="login_field"]', outlook_email)
                await page.fill('input[name="password"], input[id="password"]', outlook_password)
                await page.click('input[name="commit"], button[type="submit"]')
                await page.wait_for_timeout(3000)
            
            # 等待进入控制面板
            print("等待进入控制面板...")
            await page.wait_for_selector('text=Dashboard, text=My Domains, text=Register', timeout=15000)
            
            # 注册域名
            print(f"注册域名: {domain_prefix}.indevs.in")
            await wait_and_click(page, [
                'a:has-text("Register")',
                'button:has-text("Register")',
                'a:has-text("Register New Domain")'
            ])
            await page.wait_for_load_state('networkidle')
            
            # 输入域名
            await wait_and_fill(page, [
                'input[name="domain"]',
                'input[placeholder*="domain"]',
                'input[type="text"]'
            ], domain_prefix)
            
            # 选择后缀
            try:
                await page.select_option('select, [role="combobox"]', value='indevs.in')
            except:
                pass
            
            # 检查可用性
            await wait_and_click(page, [
                'button:has-text("Check")',
                'button:has-text("Search")',
                'button:has-text("Verify")'
            ])
            await page.wait_for_timeout(2000)
            
            # 勾选条款
            try:
                await page.check('input[type="checkbox"]')
            except:
                pass
            
            # 点击注册
            await wait_and_click(page, [
                'button:has-text("Register")',
                'button[type="submit"]:has-text("Register")'
            ])
            await page.wait_for_timeout(5000)
            
            # 截图
            await page.screenshot(path='stackryze_success.png')
            
            domain_name = f"{domain_prefix}.indevs.in"
            print(f"✅ Stackryze 域名注册成功: {domain_name}")
            
            await browser.close()
            return domain_name
            
        except Exception as e:
            print(f"❌ Stackryze 注册失败: {e}")
            await page.screenshot(path='stackryze_error.png')
            await browser.close()
            return None


def add_to_cloudflare(domain_name, cf_email, cf_api_key):
    """添加域名到 Cloudflare"""
    print("\n" + "="*60)
    print("步骤 3: 添加域名到 Cloudflare")
    print("="*60)
    
    headers = {
        'X-Auth-Email': cf_email,
        'X-Auth-Key': cf_api_key,
        'Content-Type': 'application/json'
    }
    
    # 获取账户 ID
    print("获取 Cloudflare 账户...")
    response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取账户失败: {response.text}")
        return None
    
    account_id = response.json()['result'][0]['id']
    
    # 添加域名
    print(f"添加域名: {domain_name}")
    data = {
        'name': domain_name,
        'account': {'id': account_id},
        'type': 'full'
    }
    
    response = requests.post(
        'https://api.cloudflare.com/client/v4/zones',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            zone_id = result['result']['id']
            name_servers = result['result'].get('name_servers', [])
            print(f"✅ 域名添加成功！")
            print(f"Zone ID: {zone_id}")
            print(f"Cloudflare NS: {', '.join(name_servers)}")
            return zone_id
    
    print(f"❌ 添加失败: {response.text}")
    return None


def setup_dns(zone_id, domain_name, cf_email, cf_api_key, server_ip='192.168.1.1'):
    """配置 DNS 记录"""
    print("\n" + "="*60)
    print("步骤 4: 配置 DNS 记录")
    print("="*60)
    
    headers = {
        'X-Auth-Email': cf_email,
        'X-Auth-Key': cf_api_key,
        'Content-Type': 'application/json'
    }
    
    records = [
        {'type': 'A', 'name': domain_name, 'content': server_ip, 'proxied': True},
        {'type': 'CNAME', 'name': f'www.{domain_name}', 'content': domain_name, 'proxied': True}
    ]
    
    for record in records:
        print(f"添加 {record['type']} 记录: {record['name']}")
        response = requests.post(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
            headers=headers,
            json=record
        )
        
        if response.status_code == 200:
            if response.json().get('success'):
                print(f"  ✅ 添加成功")
            else:
                print(f"  ❌ 添加失败")
    
    print("✅ DNS 记录配置完成")


async def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   全自动注册流程 v2 - 改进版                                        ║
║   Outlook邮箱 → Stackryze域名 → Cloudflare托管                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 获取 Cloudflare 信息
    print("请提供 Cloudflare 信息：")
    cf_email = input("Cloudflare 邮箱: ").strip()
    cf_api_key = input("Cloudflare API Key: ").strip()
    
    # 域名前缀
    print("\n域名配置：")
    domain_prefix = input("想要的域名前缀 (如 myapp): ").strip()
    
    # 服务器 IP
    server_ip = input("服务器 IP (默认 192.168.1.1): ").strip()
    if not server_ip:
        server_ip = '192.168.1.1'
    
    # 确认信息
    print(f"\n{'='*60}")
    print("配置信息：")
    print(f"{'='*60}")
    print(f"Cloudflare 邮箱: {cf_email}")
    print(f"域名: {domain_prefix}.indevs.in")
    print(f"服务器 IP: {server_ip}")
    print(f"{'='*60}")
    
    confirm = input("\n确认开始全自动注册？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 步骤 1: 注册 Outlook 邮箱
    outlook_account = await register_outlook_email()
    if not outlook_account:
        print("\n❌ Outlook 邮箱注册失败，流程终止")
        return
    
    # 步骤 2: 注册 Stackryze 域名
    domain_name = await register_stackryze(
        outlook_account['email'],
        outlook_account['password'],
        domain_prefix
    )
    if not domain_name:
        print("\n❌ Stackryze 域名注册失败，流程终止")
        return
    
    # 步骤 3: 添加到 Cloudflare
    zone_id = add_to_cloudflare(domain_name, cf_email, cf_api_key)
    if not zone_id:
        print("\n❌ Cloudflare 添加失败，流程终止")
        return
    
    # 步骤 4: 配置 DNS
    setup_dns(zone_id, domain_name, cf_email, cf_api_key, server_ip)
    
    # 完成
    print(f"\n{'='*60}")
    print("🎉 全自动注册完成！")
    print(f"{'='*60}")
    print(f"""
Outlook 邮箱: {outlook_account['email']}
Outlook 密码: {outlook_account['password']}

Stackryze 域名: {domain_name}

Cloudflare Zone ID: {zone_id}

后续步骤：
1. 登录 Stackryze: https://domain.stackryze.com
2. 修改 NS 记录为 Cloudflare 的 NS：
   - ns1.cloudflare.com
   - ns2.cloudflare.com
3. 等待 DNS 生效
4. 访问 https://{domain_name}
""")
    
    # 保存所有信息
    with open('full_registration_info.json', 'w', encoding='utf-8') as f:
        json.dump({
            'outlook': outlook_account,
            'domain': domain_name,
            'cloudflare': {
                'zone_id': zone_id,
                'email': cf_email
            },
            'server_ip': server_ip,
            'created_at': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print("所有信息已保存到: full_registration_info.json")


if __name__ == '__main__':
    asyncio.run(main())