#!/usr/bin/env python3
"""
DNS 记录配置自动化脚本
使用 Cloudflare API 配置 DNS 记录
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


def get_zone_id(domain_name, headers):
    """获取域名的 Zone ID"""
    response = requests.get(
        f"{CF_API_BASE}/zones",
        headers=headers,
        params={'name': domain_name}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('result'):
            zone_id = data['result'][0]['id']
            logger.info(f"获取到 Zone ID: {zone_id}")
            return zone_id
    
    logger.error(f"获取 Zone ID 失败: {response.text}")
    return None


def create_dns_record(zone_id, record_data, headers):
    """创建 DNS 记录"""
    response = requests.post(
        f"{CF_API_BASE}/zones/{zone_id}/dns_records",
        headers=headers,
        json=record_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            record_id = result['result']['id']
            record_name = result['result']['name']
            record_type = result['result']['type']
            logger.info(f"DNS 记录创建成功: {record_type} {record_name} (ID: {record_id})")
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


def list_dns_records(zone_id, headers):
    """列出所有 DNS 记录"""
    response = requests.get(
        f"{CF_API_BASE}/zones/{zone_id}/dns_records",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            records = data.get('result', [])
            logger.info(f"当前 DNS 记录数量: {len(records)}")
            for record in records:
                logger.info(f"  {record['type']} {record['name']} -> {record['content']}")
            return records
    
    logger.error(f"获取 DNS 记录失败: {response.text}")
    return []


def delete_dns_record(zone_id, record_id, headers):
    """删除 DNS 记录"""
    response = requests.delete(
        f"{CF_API_BASE}/zones/{zone_id}/dns_records/{record_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            logger.info(f"DNS 记录删除成功: {record_id}")
            return True
    
    logger.error(f"删除 DNS 记录失败: {response.text}")
    return False


def setup_ssl_settings(zone_id, config, headers):
    """配置 SSL 设置"""
    cf_config = config.get('cloudflare', {})
    ssl_mode = cf_config.get('ssl_mode', 'full')
    
    # 设置 SSL 模式
    data = {
        'value': ssl_mode
    }
    
    response = requests.patch(
        f"{CF_API_BASE}/zones/{zone_id}/settings/ssl",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            logger.info(f"SSL 模式设置成功: {ssl_mode}")
        else:
            logger.error(f"SSL 模式设置失败: {result.get('errors')}")
    else:
        logger.error(f"SSL 设置请求失败: {response.status_code}")


def setup_always_https(zone_id, config, headers):
    """配置始终使用 HTTPS"""
    cf_config = config.get('cloudflare', {})
    always_https = cf_config.get('always_use_https', True)
    
    data = {
        'value': 'on' if always_https else 'off'
    }
    
    response = requests.patch(
        f"{CF_API_BASE}/zones/{zone_id}/settings/always_use_https",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            logger.info(f"始终使用 HTTPS 设置成功: {always_https}")
        else:
            logger.error(f"始终使用 HTTPS 设置失败: {result.get('errors')}")


def setup_automatic_https_rewrites(zone_id, config, headers):
    """配置自动 HTTPS 重写"""
    cf_config = config.get('cloudflare', {})
    auto_rewrites = cf_config.get('automatic_https_rewrites', True)
    
    data = {
        'value': 'on' if auto_rewrites else 'off'
    }
    
    response = requests.patch(
        f"{CF_API_BASE}/zones/{zone_id}/settings/automatic_https_rewrites",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            logger.info(f"自动 HTTPS 重写设置成功: {auto_rewrites}")
        else:
            logger.error(f"自动 HTTPS 重写设置失败: {result.get('errors')}")


def main():
    """主函数"""
    logger.info("=== DNS 记录配置自动化 ===")
    
    # 加载配置
    config = load_config()
    
    # 读取域名信息
    domain_file = Path('registered_domain.txt')
    zone_file = Path('cloudflare_zone.json')
    
    if zone_file.exists():
        with open(zone_file, 'r') as f:
            zone_data = json.load(f)
            domain_name = zone_data.get('domain')
            zone_id = zone_data.get('zone_id')
    elif domain_file.exists():
        with open(domain_file, 'r') as f:
            domain_name = f.read().strip()
        zone_id = None
    else:
        # 从配置中获取域名
        stackryze_config = config.get('stackryze', {})
        domain_prefix = stackryze_config.get('domain_prefix')
        domain_suffix = stackryze_config.get('domain_suffix', 'indevs.in')
        domain_name = f"{domain_prefix}.{domain_suffix}"
        zone_id = None
    
    if not domain_name:
        logger.error("未找到要配置的域名")
        return 1
    
    logger.info(f"要配置的域名: {domain_name}")
    
    # 获取请求头
    headers = get_headers(config)
    
    # 获取 Zone ID（如果还没有）
    if not zone_id:
        zone_id = get_zone_id(domain_name, headers)
        if not zone_id:
            logger.error("无法获取 Zone ID")
            return 1
    
    # 列出现有 DNS 记录
    existing_records = list_dns_records(zone_id, headers)
    
    # 获取配置的 DNS 记录
    cf_config = config.get('cloudflare', {})
    dns_records = cf_config.get('dns_records', [])
    
    # 创建 DNS 记录
    success_count = 0
    for record in dns_records:
        # 准备记录数据
        record_data = {
            'type': record.get('type'),
            'name': record.get('name'),
            'content': record.get('content'),
            'ttl': record.get('ttl', 1),  # 1 = 自动
            'proxied': record.get('proxied', False)
        }
        
        # 处理根域名
        if record_data['name'] == '@':
            record_data['name'] = domain_name
        
        # 创建记录
        if create_dns_record(zone_id, record_data, headers):
            success_count += 1
    
    logger.info(f"DNS 记录配置完成: {success_count}/{len(dns_records)} 成功")
    
    # 配置 SSL 设置
    setup_ssl_settings(zone_id, config, headers)
    setup_always_https(zone_id, config, headers)
    setup_automatic_https_rewrites(zone_id, config, headers)
    
    # 列出最终的 DNS 记录
    logger.info("最终 DNS 记录:")
    list_dns_records(zone_id, headers)
    
    if success_count == len(dns_records):
        logger.info("所有 DNS 记录配置成功！")
        return 0
    else:
        logger.warning("部分 DNS 记录配置失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())