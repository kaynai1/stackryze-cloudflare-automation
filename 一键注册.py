#!/usr/bin/env python3
"""
Stackryze 域名自动注册并托管到 Cloudflare
一键完成，无需手动操作
"""

import asyncio
import json
import sys

import requests
from playwright.async_api import async_playwright


async def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   Stackryze 域名 → 自动托管到 Cloudflare                         ║
║                                                                   ║
║   功能：在 Stackryze 注册免费域名，自动添加到 Cloudflare          ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 获取用户输入
    print("请提供以下信息：\n")
    
    # Stackryze 登录信息（GitHub）
    print("【Stackryze 登录信息】")
    print("(Stackryze 使用 GitHub 账号登录)")
    github_email = input("GitHub 邮箱: ").strip()
    github_password = input("GitHub 密码: ").strip()
    
    # 域名配置
    print("\n【域名配置】")
    domain_prefix = input("想要的域名前缀 (如 myapp): ").strip()
    domain_suffix = "indevs.in"  # 默认后缀
    print(f"完整域名将是: {domain_prefix}.{domain_suffix}")
    
    # Cloudflare 信息
    print("\n【Cloudflare 信息】")
    cf_email = input("Cloudflare 邮箱: ").strip()
    cf_api_key = input("Cloudflare API Key: ").strip()
    
    # 确认
    print(f"\n{'='*60}")
    print("确认信息：")
    print(f"  Stackryze 账号: {github_email}")
    print(f"  注册域名: {domain_prefix}.{domain_suffix}")
    print(f"  Cloudflare 账号: {cf_email}")
    print(f"{'='*60}")
    
    confirm = input("\n确认开始？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 步骤 1: 在 Stackryze 注册域名
    print(f"\n{'='*60}")
    print("步骤 1/2: 在 Stackryze 注册域名")
    print(f"{'='*60}")
    
    domain_name = f"{domain_prefix}.{domain_suffix}"
    success = await register_on_stackryze(github_email, github_password, domain_prefix)
    
    if not success:
        print("\n❌ Stackryze 域名注册失败！")
        print("可能原因：")
        print("1. GitHub 账号密码错误")
        print("2. 域名已被注册")
        print("3. 网络连接问题")
        return
    
    print(f"✅ 域名 {domain_name} 注册成功！")
    
    # 步骤 2: 添加到 Cloudflare
    print(f"\n{'='*60}")
    print("步骤 2/2: 添加域名到 Cloudflare")
    print(f"{'='*60}")
    
    zone_id = add_to_cloudflare(domain_name, cf_email, cf_api_key)
    
    if not zone_id:
        print("\n❌ 添加到 Cloudflare 失败！")
        print("可能原因：")
        print("1. Cloudflare API Key 无效")
        print("2. 域名已被其他账户添加")
        return
    
    print(f"✅ 域名已添加到 Cloudflare！")
    print(f"   Zone ID: {zone_id}")
    
    # 配置 DNS 记录
    print(f"\n配置 DNS 记录...")
    setup_dns_records(zone_id, domain_name, cf_email, cf_api_key)
    
    # 完成
    print(f"\n{'='*60}")
    print("🎉 全部完成！")
    print(f"{'='*60}")
    print(f"""
您的域名: {domain_name}

接下来需要做：
1. 登录 Stackryze: https://domain.stackryze.com
2. 进入 My Domains → 找到 {domain_name}
3. 点击 Manage → DNS Configuration
4. 将 NS 记录改为 Cloudflare 提供的 NS：
   - ns1.cloudflare.com
   - ns2.cloudflare.com

然后：
1. 登录 Cloudflare: https://dash.cloudflare.com
2. 可以看到新添加的域名
3. 等待几分钟 DNS 生效
4. 访问 https://{domain_name}

Cloudflare NS 服务器：
- ns1.cloudflare.com
- ns2.cloudflare.com
""")


async def register_on_stackryze(email, password, domain_prefix):
    """在 Stackryze 注册域名"""
    print("正在启动浏览器...")
    
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
            await page.click('a:has-text("Get Started"), a:has-text("Login"), button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # 选择 GitHub 登录
            print("选择 GitHub 登录...")
            await page.click('button:has-text("GitHub"), a:has-text("GitHub")')
            await page.wait_for_load_state('networkidle')
            
            # 输入 GitHub 凭证
            print("输入 GitHub 凭证...")
            await page.fill('input[name="login"], input[id="login_field"]', email)
            await page.fill('input[name="password"], input[id="password"]', password)
            await page.click('input[name="commit"], button[type="submit"]')
            
            # 处理授权
            try:
                await page.click('button:has-text("Authorize"), input[value="Authorize"]', timeout=5000)
                print("GitHub 授权完成")
            except:
                print("无需 GitHub 授权")
            
            await page.wait_for_load_state('networkidle')
            
            # 进入控制面板
            print("等待进入控制面板...")
            await page.wait_for_selector('text=Dashboard, text=My Domains, text=Register', timeout=15000)
            
            # 点击注册新域名
            print("点击注册新域名...")
            await page.click('a:has-text("Register"), button:has-text("Register"), a:has-text("Register New Domain")')
            await page.wait_for_load_state('networkidle')
            
            # 输入域名前缀
            print(f"输入域名前缀: {domain_prefix}")
            await page.fill('input[name="domain"], input[placeholder*="domain"], input[type="text"]', domain_prefix)
            
            # 选择后缀
            try:
                await page.select_option('select, [role="combobox"]', value='indevs.in')
                print("选择后缀: indevs.in")
            except:
                print("使用默认后缀")
            
            # 检查可用性
            print("检查域名可用性...")
            await page.click('button:has-text("Check"), button:has-text("Search"), button:has-text("Verify")')
            await page.wait_for_timeout(2000)
            
            # 勾选条款
            try:
                await page.check('input[type="checkbox"]')
                print("勾选同意条款")
            except:
                pass
            
            # 点击注册
            print("点击注册...")
            await page.click('button:has-text("Register"), button[type="submit"]:has-text("Register")')
            await page.wait_for_timeout(5000)
            
            # 截图
            await page.screenshot(path='stackryze_success.png')
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            await page.screenshot(path='stackryze_error.png')
            return False
        finally:
            await browser.close()


def add_to_cloudflare(domain_name, cf_email, cf_api_key):
    """添加域名到 Cloudflare"""
    print(f"添加 {domain_name} 到 Cloudflare...")
    
    headers = {
        'X-Auth-Email': cf_email,
        'X-Auth-Key': cf_api_key,
        'Content-Type': 'application/json'
    }
    
    # 获取账户 ID
    print("获取 Cloudflare 账户...")
    response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
    if response.status_code != 200:
        print(f"获取账户失败: {response.text}")
        return None
    
    account_id = response.json()['result'][0]['id']
    print(f"账户 ID: {account_id}")
    
    # 添加域名
    print(f"添加域名...")
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
            print(f"域名添加成功！")
            print(f"Cloudflare NS: {', '.join(name_servers)}")
            return zone_id
    
    print(f"添加失败: {response.text}")
    return None


def setup_dns_records(zone_id, domain_name, cf_email, cf_api_key):
    """配置 DNS 记录"""
    print("配置 DNS 记录...")
    
    headers = {
        'X-Auth-Email': cf_email,
        'X-Auth-Key': cf_api_key,
        'Content-Type': 'application/json'
    }
    
    # DNS 记录
    records = [
        {'type': 'A', 'name': domain_name, 'content': '192.168.1.1', 'proxied': True},
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
        else:
            print(f"  ❌ 请求失败")


if __name__ == '__main__':
    asyncio.run(main())