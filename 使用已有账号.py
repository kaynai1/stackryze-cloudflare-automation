#!/usr/bin/env python3
"""
使用已有账号注册 Stackryze 域名并托管到 Cloudflare
支持：
1. 使用已有 Outlook 邮箱
2. 使用 GitHub 账号登录 Stackryze
3. 自动添加到 Cloudflare 并配置 DNS
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


async def register_stackryze_with_outlook(outlook_email, outlook_password, domain_prefix):
    """使用已有 Outlook 邮箱注册 Stackryze"""
    print("\n" + "="*60)
    print("步骤 1: 使用 Outlook 邮箱注册 Stackryze")
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
                print(f"邮箱注册失败: {e}")
                print("请尝试手动登录或使用 GitHub 登录")
                return None
            
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


async def register_stackryze_with_github(github_email, github_password, domain_prefix):
    """使用 GitHub 账号注册 Stackryze"""
    print("\n" + "="*60)
    print("步骤 1: 使用 GitHub 账号注册 Stackryze")
    print("="*60)
    
    print(f"GitHub 账号: {github_email}")
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
            
            # 使用 GitHub 登录
            print("使用 GitHub 登录...")
            await wait_and_click(page, [
                'button:has-text("GitHub")',
                'a:has-text("GitHub")'
            ])
            await page.wait_for_load_state('networkidle')
            
            # 填写 GitHub 登录信息
            print("填写 GitHub 登录信息...")
            await wait_and_fill(page, [
                'input[name="login"]',
                'input[id="login_field"]'
            ], github_email)
            
            await wait_and_fill(page, [
                'input[name="password"]',
                'input[id="password"]'
            ], github_password)
            
            await wait_and_click(page, [
                'input[name="commit"]',
                'button[type="submit"]'
            ])
            await page.wait_for_timeout(5000)
            
            # 检查是否需要授权
            try:
                await wait_and_click(page, [
                    'button:has-text("Authorize")',
                    'input[type="submit"][value="Authorize"]'
                ], timeout=5000)
                await page.wait_for_timeout(3000)
            except:
                pass
            
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
    print("步骤 2: 添加域名到 Cloudflare")
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
    print("步骤 3: 配置 DNS 记录")
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
║   使用已有账号注册 Stackryze 域名并托管到 Cloudflare              ║
║   支持 Outlook 邮箱或 GitHub 账号登录                             ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 选择登录方式
    print("请选择登录方式：")
    print("1. 使用 Outlook 邮箱登录")
    print("2. 使用 GitHub 账号登录")
    print("3. 手动登录（脚本会等待您手动登录）")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == '1':
        # 使用 Outlook 邮箱
        outlook_email = input("\nOutlook 邮箱: ").strip()
        outlook_password = input("Outlook 密码: ").strip()
        
        # 获取域名前缀
        print("\n域名配置：")
        domain_prefix = input("想要的域名前缀 (如 myapp): ").strip()
        
        # 获取 Cloudflare 信息
        print("\n请提供 Cloudflare 信息：")
        cf_email = input("Cloudflare 邮箱: ").strip()
        cf_api_key = input("Cloudflare API Key: ").strip()
        
        # 服务器 IP
        server_ip = input("服务器 IP (默认 192.168.1.1): ").strip()
        if not server_ip:
            server_ip = '192.168.1.1'
        
        # 确认信息
        print(f"\n{'='*60}")
        print("配置信息：")
        print(f"{'='*60}")
        print(f"Outlook 邮箱: {outlook_email}")
        print(f"域名: {domain_prefix}.indevs.in")
        print(f"Cloudflare 邮箱: {cf_email}")
        print(f"服务器 IP: {server_ip}")
        print(f"{'='*60}")
        
        confirm = input("\n确认开始注册？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        # 注册 Stackryze
        domain_name = await register_stackryze_with_outlook(outlook_email, outlook_password, domain_prefix)
        if not domain_name:
            print("\n❌ Stackryze 域名注册失败，流程终止")
            return
        
    elif choice == '2':
        # 使用 GitHub 账号
        github_email = input("\nGitHub 邮箱: ").strip()
        github_password = input("GitHub 密码: ").strip()
        
        # 获取域名前缀
        print("\n域名配置：")
        domain_prefix = input("想要的域名前缀 (如 myapp): ").strip()
        
        # 获取 Cloudflare 信息
        print("\n请提供 Cloudflare 信息：")
        cf_email = input("Cloudflare 邮箱: ").strip()
        cf_api_key = input("Cloudflare API Key: ").strip()
        
        # 服务器 IP
        server_ip = input("服务器 IP (默认 192.168.1.1): ").strip()
        if not server_ip:
            server_ip = '192.168.1.1'
        
        # 确认信息
        print(f"\n{'='*60}")
        print("配置信息：")
        print(f"{'='*60}")
        print(f"GitHub 账号: {github_email}")
        print(f"域名: {domain_prefix}.indevs.in")
        print(f"Cloudflare 邮箱: {cf_email}")
        print(f"服务器 IP: {server_ip}")
        print(f"{'='*60}")
        
        confirm = input("\n确认开始注册？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        # 注册 Stackryze
        domain_name = await register_stackryze_with_github(github_email, github_password, domain_prefix)
        if not domain_name:
            print("\n❌ Stackryze 域名注册失败，流程终止")
            return
        
    elif choice == '3':
        # 手动登录
        print("\n手动登录模式：")
        print("1. 请手动在浏览器中登录 Stackryze")
        print("2. 注册您想要的域名")
        print("3. 完成后输入域名信息")
        
        domain_name = input("\n请输入您注册的域名 (如 myapp.indevs.in): ").strip()
        if not domain_name.endswith('.indevs.in'):
            domain_name = f"{domain_name}.indevs.in"
        
        # 获取 Cloudflare 信息
        print("\n请提供 Cloudflare 信息：")
        cf_email = input("Cloudflare 邮箱: ").strip()
        cf_api_key = input("Cloudflare API Key: ").strip()
        
        # 服务器 IP
        server_ip = input("服务器 IP (默认 192.168.1.1): ").strip()
        if not server_ip:
            server_ip = '192.168.1.1'
        
    else:
        print("无效选择")
        return
    
    # 添加到 Cloudflare
    zone_id = add_to_cloudflare(domain_name, cf_email, cf_api_key)
    if not zone_id:
        print("\n❌ Cloudflare 添加失败，流程终止")
        return
    
    # 配置 DNS
    setup_dns(zone_id, domain_name, cf_email, cf_api_key, server_ip)
    
    # 完成
    print(f"\n{'='*60}")
    print("🎉 全自动注册完成！")
    print(f"{'='*60}")
    print(f"""
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
    with open('registration_info.json', 'w', encoding='utf-8') as f:
        json.dump({
            'domain': domain_name,
            'cloudflare': {
                'zone_id': zone_id,
                'email': cf_email
            },
            'server_ip': server_ip,
            'created_at': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print("所有信息已保存到: registration_info.json")


if __name__ == '__main__':
    asyncio.run(main())