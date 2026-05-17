#!/usr/bin/env python3
"""
Cloudflare 域名添加自动化脚本
使用 Cloudflare API 添加域名到 Cloudflare 账户
"""

import json
import logging
import os
import sys
from pathlib import Path

import requests
import yaml

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

# Cloudflare API 基础 URL
CF_API_BASE = "https://api.cloudflare.com/client/v4"


def load_config():
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


def get_headers(config):
    """获取 Cloudflare API 请求头"""
    cf_config = config.get('cloudflare', {})
    api_token = cf_config.get('api_token')
    api_key = cf_config.get('api_key')
    email = cf_config.get('email')
    
    if api_token:
        return {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    elif api_key and email:
        return {
            'X-Auth-Email': email,
            'X-Auth-Key': api_key,
            'Content-Type': 'application/json'
        }
    else:
        logger.error("缺少 Cloudflare 认证信息")
        sys.exit(1)


def get_account_id(headers):
    """获取 Cloudflare 账户 ID"""
    response = requests.get(f"{CF_API_BASE}/accounts", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('result'):
            account_id = data['result'][0]['id']
            logger.info(f"获取到账户 ID: {account_id}")
            return account_id
    
    logger.error(f"获取账户 ID 失败: {response.text}")
    return None


def add_zone_to_cloudflare(domain_name, config):
    """将域名添加到 Cloudflare"""
    headers = get_headers(config)
    cf_config = config.get('cloudflare', {})
    
    # 获取账户 ID
    account_id = cf_config.get('account_id') or get_account_id(headers)
    if not account_id:
        logger.error("无法获取账户 ID")
        return False
    
    # 准备请求数据
    data = {
        'name': domain_name,
        'account': {
            'id': account_id
        },
        'type': 'full',
        'jump_start': True  # 自动扫描 DNS 记录
    }
    
    logger.info(f"正在添加域名 {domain_name} 到 Cloudflare...")
    
    # 发送请求
    response = requests.post(
        f"{CF_API_BASE}/zones",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            zone_id = result['result']['id']
            name_servers = result['result'].get('name_servers', [])
            
            logger.info(f"域名添加成功！")
            logger.info(f"Zone ID: {zone_id}")
            logger.info(f"Name Servers: {', '.join(name_servers)}")
            
            # 保存 Zone ID 供后续使用
            with open('cloudflare_zone.json', 'w') as f:
                json.dump({
                    'domain': domain_name,
                    'zone_id': zone_id,
                    'name_servers': name_servers
                }, f, indent=2)
            
            return True
        else:
            errors = result.get('errors', [])
            for error in errors:
                logger.error(f"API 错误: {error.get('message')}")
            return False
    else:
        logger.error(f"请求失败，状态码: {response.status_code}")
        logger.error(f"响应内容: {response.text}")
        return False


def update_stackryze_nameservers(domain_name, nameservers):
    """更新 Stackryze 的 NS 记录（这部分可能需要网页自动化）"""
    logger.info(f"需要手动更新 Stackryze 的 NS 记录: {', '.join(nameservers)}")
    logger.info("请登录 domain.stackryze.com 更新域名的 NS 记录")
    
    # 注意：这部分可能需要使用 Playwright 进行网页自动化
    # 因为 Stackryze 可能没有提供 API
    return True


def main():
    """主函数"""
    logger.info("=== Cloudflare 域名添加自动化 ===")
    
    # 加载配置
    config = load_config()
    
    # 读取注册的域名
    domain_file = Path('registered_domain.txt')
    if domain_file.exists():
        with open(domain_file, 'r') as f:
            domain_name = f.read().strip()
    else:
        # 从配置中获取域名
        stackryze_config = config.get('stackryze', {})
        domain_prefix = stackryze_config.get('domain_prefix')
        domain_suffix = stackryze_config.get('domain_suffix', 'indevs.in')
        domain_name = f"{domain_prefix}.{domain_suffix}"
    
    if not domain_name:
        logger.error("未找到要添加的域名")
        return 1
    
    logger.info(f"要添加的域名: {domain_name}")
    
    # 添加域名到 Cloudflare
    if add_zone_to_cloudflare(domain_name, config):
        logger.info("域名添加到 Cloudflare 成功")
        
        # 读取 Cloudflare 返回的 NS 记录
        zone_file = Path('cloudflare_zone.json')
        if zone_file.exists():
            with open(zone_file, 'r') as f:
                zone_data = json.load(f)
                nameservers = zone_data.get('name_servers', [])
                
                if nameservers:
                    # 更新 Stackryze 的 NS 记录
                    update_stackryze_nameservers(domain_name, nameservers)
        
        return 0
    else:
        logger.error("域名添加到 Cloudflare 失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())