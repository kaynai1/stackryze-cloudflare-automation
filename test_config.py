#!/usr/bin/env python3
"""
配置测试脚本
验证配置文件和环境变量是否正确设置
"""

import os
import sys
from pathlib import Path

import yaml


def test_config():
    """测试配置文件"""
    print("=== 测试配置文件 ===")
    
    # 检查配置文件是否存在
    config_path = Path('config.yml')
    if not config_path.exists():
        print("❌ 配置文件不存在: config.yml")
        print("请复制 config.example.yml 为 config.yml 并修改配置")
        return False
    
    # 加载配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False
    
    # 检查必要的配置项
    stackryze_config = config.get('stackryze', {})
    cloudflare_config = config.get('cloudflare', {})
    
    # 检查 Stackryze 配置
    required_stackryze = ['email', 'password', 'domain_prefix']
    for key in required_stackryze:
        value = stackryze_config.get(key)
        if not value or value.startswith('${'):
            print(f"❌ Stackryze 配置缺失: {key}")
            return False
        else:
            print(f"✅ Stackryze.{key}: 已配置")
    
    # 检查 Cloudflare 配置
    has_api_token = bool(cloudflare_config.get('api_token')) and not cloudflare_config.get('api_token', '').startswith('${')
    has_api_key = bool(cloudflare_config.get('api_key')) and not cloudflare_config.get('api_key', '').startswith('${')
    
    if not has_api_token and not has_api_key:
        print("❌ Cloudflare 认证信息缺失: 需要 api_token 或 api_key")
        return False
    
    if has_api_token:
        print("✅ Cloudflare.api_token: 已配置")
    else:
        print("✅ Cloudflare.api_key: 已配置")
        if not cloudflare_config.get('email') or cloudflare_config.get('email', '').startswith('${'):
            print("❌ Cloudflare.email 缺失（使用 api_key 时需要）")
            return False
        print("✅ Cloudflare.email: 已配置")
    
    return True


def test_environment():
    """测试环境变量"""
    print("\n=== 测试环境变量 ===")
    
    # 检查环境变量
    env_vars = [
        'STACKRYZE_EMAIL',
        'STACKRYZE_PASSWORD',
        'CLOUDFLARE_API_TOKEN',
        'CLOUDFLARE_API_KEY'
    ]
    
    all_set = True
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: 已设置")
        else:
            print(f"⚠️  {var}: 未设置（可能从配置文件读取）")
    
    return True


def test_dependencies():
    """测试依赖"""
    print("\n=== 测试依赖 ===")
    
    required_packages = [
        'playwright',
        'requests',
        'yaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的依赖: pip install {' '.join(missing_packages)}")
        return False
    
    return True


def test_cloudflare_connection():
    """测试 Cloudflare 连接"""
    print("\n=== 测试 Cloudflare 连接 ===")
    
    try:
        import requests
        response = requests.get("https://api.cloudflare.com/client/v4/user")
        if response.status_code == 200:
            print("✅ Cloudflare API 连接正常")
            return True
        else:
            print(f"❌ Cloudflare API 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cloudflare API 连接失败: {e}")
        return False


def main():
    """主测试函数"""
    print("Stackryze to Cloudflare 自动化工具 - 配置测试")
    print("=" * 50)
    
    tests = [
        ("配置文件", test_config),
        ("环境变量", test_environment),
        ("依赖包", test_dependencies),
        ("Cloudflare 连接", test_cloudflare_connection)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 测试出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！可以开始使用自动化工具。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置和环境。")
        return 1


if __name__ == '__main__':
    sys.exit(main())