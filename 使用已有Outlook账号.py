#!/usr/bin/env python3
"""
使用已有的 Outlook 账号注册 Stackryze 域名并托管到 Cloudflare
从 outlook_accounts.txt 读取账号信息
"""

import asyncio
import json
import re
from datetime import datetime

import requests
from playwright.async_api import async_playwright


def read_outlook_accounts():
    """读取已有的 Outlook 账号"""
    accounts = []
    try:
        with open('outlook_accounts.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 解析账号信息
            pattern = r'邮箱: (.+?)\n密码: (.+?)\n姓名: (.+?)\n出生日期: (.+?)\n创建时间: (.+?)\n'
            matches = re.findall(pattern, content)
            
            for match in matches:
                email, password, name, birth_date, created_at = match
                first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
                accounts.append({
                    'email': email.strip(),
                    'password': password.strip(),
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'birth_date': birth_date.strip(),
                    'created_at': created_at.strip()
                })
    except Exception as e:
        print(f"[ERROR] 读取账号失败: {e}")
    
    return accounts


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


async def register_stackryze(account, domain_prefix):
    """使用 Outlook 账号注册 Stackryze"""
    print(f"\n使用账号: {account['email']}")
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
                ], account['email'])
                
                await wait_and_fill(page, [
                    'input[name="password"]',
                    'input[type="password"]'
                ], account['password'])
                
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


def add_to_cloudflare(domain_name, cf_email, cf_api_key):
    """添加域名到 Cloudflare"""
    print(f"\n添加域名到 Cloudflare: {domain_name}")
    
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
    print(f"\n配置 DNS 记录...")
    
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
║   使用已有 Outlook 账号注册 Stackryze 域名                       ║
║   从 outlook_accounts.txt 读取账号信息                           ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 读取账号
    accounts = read_outlook_accounts()
    
    if not accounts:
        print("[ERROR] 没有找到可用的 Outlook 账号")
        print("请先运行 '全自动Outlook注册v3.bat' 注册账号")
        return
    
    print(f"找到 {len(accounts)} 个 Outlook 账号：")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. {account['email']} (创建时间: {account['created_at']})")
    
    # 选择账号
    if len(accounts) == 1:
        selected_account = accounts[0]
        print(f"\n自动选择唯一账号: {selected_account['email']}")
    else:
        choice = input(f"\n请选择账号 (1-{len(accounts)}): ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                selected_account = accounts[index]
            else:
                print("无效选择")
                return
        except ValueError:
            print("请输入数字")
            return
    
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
    print(f"Outlook 账号: {selected_account['email']}")
    print(f"域名: {domain_prefix}.indevs.in")
    print(f"Cloudflare 邮箱: {cf_email}")
    print(f"服务器 IP: {server_ip}")
    print(f"{'='*60}")
    
    confirm = input("\n确认开始注册？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 注册 Stackryze
    domain_name = await register_stackryze(selected_account, domain_prefix)
    if not domain_name:
        print("\n❌ Stackryze 域名注册失败，流程终止")
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
    print("🎉 注册完成！")
    print(f"{'='*60}")
    print(f"""
Outlook 账号: {selected_account['email']}
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
    
    # 保存信息
    with open('registration_info.json', 'w', encoding='utf-8') as f:
        json.dump({
            'outlook': selected_account,
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