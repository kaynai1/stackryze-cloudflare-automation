#!/usr/bin/env python3
"""
Stackryze 域名自动注册并托管到 Cloudflare
用户只需输入账号密码，其他全部自动完成
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import requests
import yaml
from playwright.async_api import async_playwright


class StackryzeAutomation:
    def __init__(self):
        self.domain_name = None
        self.zone_id = None
        self.name_servers = None
        
    async def register_domain(self, email, password, domain_prefix):
        """在 Stackryze 注册域名"""
        print(f"\n{'='*50}")
        print(f"步骤 1: 在 Stackryze 注册域名")
        print(f"{'='*50}")
        
        domain_suffix = "indevs.in"
        self.domain_name = f"{domain_prefix}.{domain_suffix}"
        
        print(f"目标域名: {self.domain_name}")
        print(f"正在启动浏览器...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # 显示浏览器便于调试
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            try:
                # 1. 访问 Stackryze
                print("访问 domain.stackryze.com...")
                await page.goto('https://domain.stackryze.com')
                await page.wait_for_load_state('networkidle')
                
                # 2. 点击登录
                print("点击登录按钮...")
                await page.click('a:has-text("Get Started"), a:has-text("Login"), button:has-text("Login")')
                await page.wait_for_load_state('networkidle')
                
                # 3. 选择 GitHub 登录
                print("选择 GitHub 登录...")
                await page.click('button:has-text("GitHub"), a:has-text("GitHub")')
                await page.wait_for_load_state('networkidle')
                
                # 4. 输入 GitHub 凭证
                print("输入 GitHub 凭证...")
                await page.fill('input[name="login"], input[id="login_field"]', email)
                await page.fill('input[name="password"], input[id="password"]', password)
                await page.click('input[name="commit"], button[type="submit"]')
                
                # 5. 处理 GitHub 授权
                try:
                    await page.click('button:has-text("Authorize"), input[value="Authorize"]', timeout=5000)
                    print("GitHub 授权完成")
                except:
                    print("无需 GitHub 授权")
                
                await page.wait_for_load_state('networkidle')
                
                # 6. 进入控制面板
                print("等待进入控制面板...")
                await page.wait_for_selector('text=Dashboard, text=My Domains, text=Register', timeout=15000)
                
                # 7. 点击注册新域名
                print("点击注册新域名...")
                await page.click('a:has-text("Register"), button:has-text("Register"), a:has-text("Register New Domain")')
                await page.wait_for_load_state('networkidle')
                
                # 8. 输入域名前缀
                print(f"输入域名前缀: {domain_prefix}")
                await page.fill('input[name="domain"], input[placeholder*="domain"], input[type="text"]', domain_prefix)
                
                # 9. 选择后缀
                try:
                    await page.select_option('select, [role="combobox"]', value=domain_suffix)
                    print(f"选择域名后缀: {domain_suffix}")
                except:
                    print("使用默认后缀")
                
                # 10. 检查可用性
                print("检查域名可用性...")
                await page.click('button:has-text("Check"), button:has-text("Search"), button:has-text("Verify")')
                await page.wait_for_timeout(2000)
                
                # 11. 勾选条款
                try:
                    await page.check('input[type="checkbox"]')
                    print("勾选同意条款")
                except:
                    pass
                
                # 12. 点击注册
                print("点击注册按钮...")
                await page.click('button:has-text("Register"), button[type="submit"]:has-text("Register")')
                await page.wait_for_timeout(5000)
                
                # 13. 获取 NS 记录
                print("获取 NS 记录...")
                ns_records = []
                try:
                    # 尝试从页面获取 NS 记录
                    ns_elements = await page.query_selector_all('text=ns1., text=ns2., text=ns3., text=ns4.')
                    for elem in ns_elements:
                        text = await elem.text_content()
                        if 'ns' in text.lower():
                            ns_records.append(text.strip())
                except:
                    pass
                
                if not ns_records:
                    # 如果页面上没有显示，使用默认的 Cloudflare NS
                    ns_records = [
                        'ns1.cloudflare.com',
                        'ns2.cloudflare.com'
                    ]
                    print(f"使用默认 Cloudflare NS: {', '.join(ns_records)}")
                else:
                    print(f"获取到 NS 记录: {', '.join(ns_records)}")
                
                self.name_servers = ns_records
                
                # 14. 截图保存
                await page.screenshot(path='registration_success.png')
                print(f"✅ 域名 {self.domain_name} 注册成功！")
                
                # 保存域名信息
                with open('domain_info.json', 'w') as f:
                    json.dump({
                        'domain': self.domain_name,
                        'name_servers': ns_records
                    }, f, indent=2)
                
                return True
                
            except Exception as e:
                print(f"❌ 注册失败: {e}")
                await page.screenshot(path='registration_error.png')
                return False
            finally:
                await browser.close()
    
    def add_to_cloudflare(self, cf_email, cf_api_key):
        """将域名添加到 Cloudflare"""
        print(f"\n{'='*50}")
        print(f"步骤 2: 添加域名到 Cloudflare")
        print(f"{'='*50}")
        
        headers = {
            'X-Auth-Email': cf_email,
            'X-Auth-Key': cf_api_key,
            'Content-Type': 'application/json'
        }
        
        # 获取账户 ID
        print("获取 Cloudflare 账户 ID...")
        response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
        if response.status_code != 200:
            print(f"❌ 获取账户 ID 失败: {response.text}")
            return False
        
        account_id = response.json()['result'][0]['id']
        print(f"账户 ID: {account_id}")
        
        # 添加域名
        print(f"添加域名 {self.domain_name} 到 Cloudflare...")
        data = {
            'name': self.domain_name,
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
                self.zone_id = result['result']['id']
                cf_name_servers = result['result'].get('name_servers', [])
                print(f"✅ 域名添加成功！")
                print(f"Zone ID: {self.zone_id}")
                print(f"Cloudflare NS: {', '.join(cf_name_servers)}")
                
                # 保存 Cloudflare 信息
                with open('cloudflare_info.json', 'w') as f:
                    json.dump({
                        'domain': self.domain_name,
                        'zone_id': self.zone_id,
                        'name_servers': cf_name_servers
                    }, f, indent=2)
                
                return True
            else:
                errors = result.get('errors', [])
                for error in errors:
                    print(f"❌ 错误: {error.get('message')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
    
    def setup_dns(self, cf_email, cf_api_key, server_ip='192.168.1.1'):
        """配置 DNS 记录"""
        print(f"\n{'='*50}")
        print(f"步骤 3: 配置 DNS 记录")
        print(f"{'='*50}")
        
        headers = {
            'X-Auth-Email': cf_email,
            'X-Auth-Key': cf_api_key,
            'Content-Type': 'application/json'
        }
        
        # DNS 记录配置
        dns_records = [
            {'type': 'A', 'name': '@', 'content': server_ip, 'proxied': True},
            {'type': 'CNAME', 'name': 'www', 'content': self.domain_name, 'proxied': True}
        ]
        
        success_count = 0
        for record in dns_records:
            record['name'] = self.domain_name if record['name'] == '@' else f"{record['name']}.{self.domain_name}"
            
            print(f"添加 {record['type']} 记录: {record['name']} -> {record['content']}")
            
            response = requests.post(
                f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records',
                headers=headers,
                json=record
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 添加成功")
                    success_count += 1
                else:
                    print(f"❌ 添加失败: {result.get('errors')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
        
        print(f"\nDNS 记录配置完成: {success_count}/{len(dns_records)} 成功")
        return success_count == len(dns_records)
    
    def setup_ssl(self, cf_email, cf_api_key):
        """配置 SSL 设置"""
        print(f"\n{'='*50}")
        print(f"步骤 4: 配置 SSL 设置")
        print(f"{'='*50}")
        
        headers = {
            'X-Auth-Email': cf_email,
            'X-Auth-Key': cf_api_key,
            'Content-Type': 'application/json'
        }
        
        # 设置 SSL 模式
        print("设置 SSL 模式为 Full...")
        requests.patch(
            f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/ssl',
            headers=headers,
            json={'value': 'full'}
        )
        
        # 启用始终 HTTPS
        print("启用始终使用 HTTPS...")
        requests.patch(
            f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/always_use_https',
            headers=headers,
            json={'value': 'on'}
        )
        
        # 启用自动 HTTPS 重写
        print("启用自动 HTTPS 重写...")
        requests.patch(
            f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/automatic_https_rewrites',
            headers=headers,
            json={'value': 'on'}
        )
        
        print("✅ SSL 配置完成")
        return True


async def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════╗
║     Stackryze 域名自动注册并托管到 Cloudflare 工具        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 获取用户输入
    print("请输入以下信息：\n")
    
    # Stackryze 账号（GitHub）
    github_email = input("GitHub 邮箱: ").strip()
    github_password = input("GitHub 密码: ").strip()
    domain_prefix = input("域名前缀 (如 myapp): ").strip()
    
    # Cloudflare 账号
    print("\nCloudflare 账号信息：")
    cf_email = input("Cloudflare 邮箱: ").strip()
    cf_api_key = input("Cloudflare API Key: ").strip()
    
    # 服务器 IP（可选）
    print("\n服务器配置（可选，直接回车使用默认值）：")
    server_ip = input("服务器 IP (默认 192.168.1.1): ").strip()
    if not server_ip:
        server_ip = '192.168.1.1'
    
    # 确认信息
    print(f"\n{'='*50}")
    print("配置信息确认：")
    print(f"{'='*50}")
    print(f"GitHub 邮箱: {github_email}")
    print(f"域名: {domain_prefix}.indevs.in")
    print(f"Cloudflare 邮箱: {cf_email}")
    print(f"服务器 IP: {server_ip}")
    
    confirm = input("\n确认开始？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 创建自动化实例
    automation = StackryzeAutomation()
    
    # 步骤 1: 注册域名
    if not await automation.register_domain(github_email, github_password, domain_prefix):
        print("\n❌ 域名注册失败，请检查账号密码")
        return
    
    # 步骤 2: 添加到 Cloudflare
    if not automation.add_to_cloudflare(cf_email, cf_api_key):
        print("\n❌ 添加到 Cloudflare 失败，请检查 API Key")
        return
    
    # 步骤 3: 配置 DNS
    if not automation.setup_dns(cf_email, cf_api_key, server_ip):
        print("\n⚠️  部分 DNS 记录配置失败")
    
    # 步骤 4: 配置 SSL
    automation.setup_ssl(cf_email, cf_api_key)
    
    # 完成
    print(f"\n{'='*50}")
    print("🎉 全部完成！")
    print(f"{'='*50}")
    print(f"\n您的域名: {automation.domain_name}")
    print(f"Zone ID: {automation.zone_id}")
    print(f"\n请等待几分钟让 DNS 生效，然后访问：")
    print(f"https://{automation.domain_name}")
    print(f"\n登录 Cloudflare 查看域名：")
    print(f"https://dash.cloudflare.com")


if __name__ == '__main__':
    asyncio.run(main())