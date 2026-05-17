#!/usr/bin/env python3
"""
Outlook 邮箱自动注册脚本
自动创建 Outlook/Hotmail 邮箱账号
"""

import asyncio
import random
import string
import time
from datetime import datetime

from playwright.async_api import async_playwright


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_password():
    """生成随机密码"""
    # 密码要求：至少8个字符，包含大写、小写、数字、特殊字符
    uppercase = random.choice(string.ascii_uppercase)
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=4))
    digits = ''.join(random.choices(string.digits, k=2))
    special = random.choice('!@#$%^&*')
    
    password = uppercase + lowercase + digits + special
    # 打乱顺序
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_birth_date():
    """生成随机出生日期（18-35岁）"""
    year = random.randint(1989, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return year, month, day


async def register_outlook():
    """注册 Outlook 邮箱"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║   Outlook 邮箱自动注册工具                                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 获取用户输入
    print("请选择注册方式：\n")
    print("1. 自动生成随机邮箱")
    print("2. 自定义邮箱前缀")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == '2':
        prefix = input("请输入邮箱前缀: ").strip()
        email = f"{prefix}@outlook.com"
    else:
        prefix = generate_random_string(10)
        email = f"{prefix}@outlook.com"
    
    # 生成密码
    password = generate_password()
    
    # 生成出生日期
    birth_year, birth_month, birth_day = generate_birth_date()
    
    # 生成姓名
    first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    print(f"\n{'='*60}")
    print("注册信息：")
    print(f"{'='*60}")
    print(f"邮箱: {email}")
    print(f"密码: {password}")
    print(f"姓名: {first_name} {last_name}")
    print(f"出生日期: {birth_year}-{birth_month:02d}-{birth_day:02d}")
    print(f"{'='*60}")
    
    confirm = input("\n确认开始注册？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return None
    
    print("\n正在启动浏览器...")
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式，便于调试）
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        try:
            # 访问 Outlook 注册页面
            print("访问 Outlook 注册页面...")
            await page.goto('https://signup.live.com/signup')
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载
            await page.wait_for_timeout(2000)
            
            # 点击 "获取新电子邮件地址"
            print("点击获取新邮箱地址...")
            try:
                await page.click('a:has-text("Get a new email address"), a:has-text("获取新的电子邮件地址")')
                await page.wait_for_timeout(1000)
            except:
                print("未找到该选项，可能已在注册页面")
            
            # 输入邮箱地址
            print(f"输入邮箱地址: {email}")
            await page.fill('input[name="MemberName"], input[type="email"]', email)
            
            # 点击下一步
            await page.click('input[type="submit"], button:has-text("Next"), button:has-text("下一步")')
            await page.wait_for_timeout(2000)
            
            # 输入密码
            print(f"输入密码: {password}")
            await page.fill('input[name="Password"], input[type="password"]', password)
            
            # 点击下一步
            await page.click('input[type="submit"], button:has-text("Next"), button:has-text("下一步")')
            await page.wait_for_timeout(2000)
            
            # 输入姓名
            print(f"输入姓名: {first_name} {last_name}")
            await page.fill('input[name="FirstName"], input[aria-label*="First name"], input[placeholder*="First"]', first_name)
            await page.fill('input[name="LastName"], input[aria-label*="Last name"], input[placeholder*="Last"]', last_name)
            
            # 点击下一步
            await page.click('input[type="submit"], button:has-text("Next"), button:has-text("下一步")')
            await page.wait_for_timeout(2000)
            
            # 输入出生日期
            print(f"输入出生日期...")
            
            # 选择国家/地区
            try:
                await page.select_option('select[name="Country"], select[aria-label*="Country"]', value='US')
            except:
                pass
            
            # 选择出生年份
            try:
                await page.select_option('select[name="BirthYear"], select[aria-label*="Year"]', value=str(birth_year))
            except:
                await page.fill('input[name="BirthYear"], input[aria-label*="Year"]', str(birth_year))
            
            # 选择出生月份
            try:
                await page.select_option('select[name="BirthMonth"], select[aria-label*="Month"]', value=str(birth_month))
            except:
                pass
            
            # 选择出生日期
            try:
                await page.select_option('select[name="BirthDay"], select[aria-label*="Day"]', value=str(birth_day))
            except:
                await page.fill('input[name="BirthDay"], input[aria-label*="Day"]', str(birth_day))
            
            # 点击下一步
            await page.click('input[type="submit"], button:has-text("Next"), button:has-text("下一步")')
            await page.wait_for_timeout(2000)
            
            # 处理人机验证
            print("\n⚠️  可能需要手动完成人机验证...")
            print("请在浏览器中完成验证，然后按 Enter 继续...")
            
            # 等待用户手动完成验证
            input()
            
            # 检查是否注册成功
            print("\n检查注册结果...")
            await page.wait_for_timeout(3000)
            
            # 截图保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"outlook_registration_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"截图已保存: {screenshot_path}")
            
            # 检查是否到达收件箱
            current_url = page.url
            if 'inbox' in current_url or 'mail' in current_url or 'outlook' in current_url:
                print(f"\n🎉 Outlook 邮箱注册成功！")
                print(f"\n{'='*60}")
                print("注册信息：")
                print(f"{'='*60}")
                print(f"邮箱: {email}")
                print(f"密码: {password}")
                print(f"{'='*60}")
                
                # 保存账号信息
                account_info = {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
                    'created_at': datetime.now().isoformat()
                }
                
                # 写入文件
                with open('outlook_accounts.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"邮箱: {email}\n")
                    f.write(f"密码: {password}\n")
                    f.write(f"姓名: {first_name} {last_name}\n")
                    f.write(f"出生日期: {birth_year}-{birth_month:02d}-{birth_day:02d}\n")
                    f.write(f"创建时间: {datetime.now().isoformat()}\n")
                    f.write(f"{'='*60}\n")
                
                print(f"\n账号信息已保存到: outlook_accounts.txt")
                
                return account_info
            else:
                print(f"\n⚠️  注册可能未完成，请检查浏览器状态")
                print(f"当前页面: {current_url}")
                return None
            
        except Exception as e:
            print(f"\n❌ 注册过程中发生错误: {e}")
            # 截图保存错误状态
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"outlook_error_{timestamp}.png")
            return None
        finally:
            print("\n按 Enter 关闭浏览器...")
            input()
            await browser.close()


async def main():
    """主函数"""
    account = await register_outlook()
    
    if account:
        print(f"\n✅ 注册完成！")
        print(f"\n您可以使用此邮箱注册 Stackryze 账号")
    else:
        print(f"\n❌ 注册失败，请重试")


if __name__ == '__main__':
    asyncio.run(main())