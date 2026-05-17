#!/usr/bin/env python3
"""
Stackryze 域名注册自动化脚本
使用 Playwright 模拟浏览器操作注册域名
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import yaml
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / 'config.yml'
    
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 替换环境变量
    config = replace_env_vars(config)
    return config


def replace_env_vars(obj):
    """递归替换配置中的环境变量"""
    if isinstance(obj, dict):
        return {k: replace_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        env_var = obj[2:-1]
        return os.environ.get(env_var, obj)
    return obj


async def register_stackryze_domain(config):
    """注册 Stackryze 域名"""
    stackryze_config = config.get('stackryze', {})
    email = stackryze_config.get('email')
    password = stackryze_config.get('password')
    domain_prefix = stackryze_config.get('domain_prefix')
    domain_suffix = stackryze_config.get('domain_suffix', 'indevs.in')
    headless = stackryze_config.get('headless', True)
    timeout = stackryze_config.get('timeout', 30000)
    
    if not all([email, password, domain_prefix]):
        logger.error("缺少必要的配置: email, password, domain_prefix")
        return None
    
    domain_name = f"{domain_prefix}.{domain_suffix}"
    logger.info(f"开始注册域名: {domain_name}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        page.set_default_timeout(timeout)
        
        try:
            # 1. 访问 Stackryze 网站
            logger.info("访问 Stackryze 网站...")
            await page.goto('https://domain.stackryze.com')
            await page.wait_for_load_state('networkidle')
            
            # 2. 点击登录按钮
            logger.info("点击登录按钮...")
            login_button = page.locator('a:has-text("Get Started"), a:has-text("Login"), button:has-text("Login")')
            await login_button.first.click()
            await page.wait_for_load_state('networkidle')
            
            # 3. 选择 GitHub 登录
            logger.info("选择 GitHub 登录...")
            github_button = page.locator('button:has-text("GitHub"), a:has-text("GitHub")')
            await github_button.first.click()
            await page.wait_for_load_state('networkidle')
            
            # 4. 输入 GitHub 凭证
            logger.info("输入 GitHub 凭证...")
            await page.fill('input[name="login"], input[id="login_field"]', email)
            await page.fill('input[name="password"], input[id="password"]', password)
            await page.click('input[name="commit"], button[type="submit"]')
            
            # 5. 处理 GitHub 授权（如果需要）
            try:
                authorize_button = page.locator('button:has-text("Authorize"), input[value="Authorize"]')
                if await authorize_button.is_visible(timeout=5000):
                    await authorize_button.click()
                    logger.info("GitHub 授权完成")
            except PlaywrightTimeout:
                logger.info("无需 GitHub 授权")
            
            await page.wait_for_load_state('networkidle')
            
            # 6. 等待进入控制面板
            logger.info("等待进入控制面板...")
            await page.wait_for_selector('text=Dashboard, text=My Domains, text=Register', timeout=15000)
            
            # 7. 点击注册新域名
            logger.info("点击注册新域名...")
            register_button = page.locator('a:has-text("Register"), button:has-text("Register"), a:has-text("Register New Domain")')
            await register_button.first.click()
            await page.wait_for_load_state('networkidle')
            
            # 8. 输入域名前缀
            logger.info(f"输入域名前缀: {domain_prefix}")
            domain_input = page.locator('input[name="domain"], input[placeholder*="domain"], input[type="text"]')
            await domain_input.first.fill(domain_prefix)
            
            # 9. 选择域名后缀（如果需要）
            try:
                suffix_selector = page.locator('select, [role="combobox"]')
                if await suffix_selector.is_visible(timeout=3000):
                    await suffix_selector.select_option(value=domain_suffix)
                    logger.info(f"选择域名后缀: {domain_suffix}")
            except PlaywrightTimeout:
                logger.info("未找到后缀选择器，使用默认后缀")
            
            # 10. 检查域名可用性
            logger.info("检查域名可用性...")
            check_button = page.locator('button:has-text("Check"), button:has-text("Search"), button:has-text("Verify")')
            await check_button.first.click()
            await page.wait_for_timeout(2000)
            
            # 11. 勾选同意条款
            try:
                terms_checkbox = page.locator('input[type="checkbox"], input[name*="terms"], input[name*="agree"]')
                if await terms_checkbox.is_visible(timeout=3000):
                    await terms_checkbox.check()
                    logger.info("勾选同意条款")
            except PlaywrightTimeout:
                logger.info("未找到条款复选框")
            
            # 12. 点击注册按钮
            logger.info("点击注册按钮...")
            register_submit = page.locator('button:has-text("Register"), button[type="submit"]:has-text("Register")')
            await register_submit.first.click()
            
            # 13. 等待注册完成
            logger.info("等待注册完成...")
            await page.wait_for_timeout(5000)
            
            # 14. 检查注册结果
            success_indicators = [
                'text=success',
                'text=registered',
                'text=congratulations',
                'text=domain added',
                '.alert-success',
                '.success-message'
            ]
            
            for indicator in success_indicators:
                try:
                    if await page.locator(indicator).is_visible(timeout=2000):
                        logger.info(f"域名 {domain_name} 注册成功！")
                        # 截图保存证据
                        await page.screenshot(path='registration_success.png')
                        return domain_name
                except PlaywrightTimeout:
                    continue
            
            # 检查错误信息
            error_indicators = [
                'text=error',
                'text=failed',
                'text=unavailable',
                'text=taken',
                '.alert-danger',
                '.error-message'
            ]
            
            for indicator in error_indicators:
                try:
                    if await page.locator(indicator).is_visible(timeout=1000):
                        error_text = await page.locator(indicator).text_content()
                        logger.error(f"注册失败: {error_text}")
                        await page.screenshot(path='registration_error.png')
                        return None
                except PlaywrightTimeout:
                    continue
            
            # 如果没有明确的成功或失败指示，截图并记录
            logger.warning("无法确定注册状态，截图保存")
            await page.screenshot(path='registration_unknown.png')
            return domain_name
            
        except PlaywrightTimeout as e:
            logger.error(f"操作超时: {e}")
            await page.screenshot(path='timeout_error.png')
            return None
        except Exception as e:
            logger.error(f"注册过程中发生错误: {e}")
            await page.screenshot(path='error.png')
            return None
        finally:
            await browser.close()


async def main():
    """主函数"""
    logger.info("=== Stackryze 域名注册自动化 ===")
    
    # 加载配置
    config = await load_config()
    
    # 注册域名
    domain_name = await register_stackryze_domain(config)
    
    if domain_name:
        logger.info(f"域名注册成功: {domain_name}")
        # 将域名信息写入文件供后续脚本使用
        with open('registered_domain.txt', 'w') as f:
            f.write(domain_name)
        return 0
    else:
        logger.error("域名注册失败")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))