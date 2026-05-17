# Stackryze to Cloudflare 自动化工具

自动将 Stackryze 域名注册并托管到 Cloudflare，无需手动操作。

## 功能特性

- 自动注册 Stackryze 域名（通过网页自动化）
- 自动将域名添加到 Cloudflare
- 自动配置 DNS 记录
- 支持 GitHub Actions 自动运行
- 安全的凭证管理

## 项目结构

```
├── .github/
│   └── workflows/
│       └── auto-register.yml      # GitHub Action 工作流
├── scripts/
│   ├── register_stackryze.py      # Stackryze 域名注册脚本
│   ├── add_to_cloudflare.py       # Cloudflare 域名添加脚本
│   └── setup_dns.py               # DNS 配置脚本
├── requirements.txt               # Python 依赖
├── config.example.yml             # 配置文件示例
└── README.md                      # 项目说明
```

## 前置要求

1. **Stackryze 账号**：需要 GitHub 账号登录
2. **Cloudflare 账号**：需要 Global API Key 或 API Token
3. **GitHub 仓库**：用于运行 GitHub Actions

## 配置说明

### GitHub Secrets 设置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加以下密钥：

```
STACKRYZE_EMAIL          # Stackryze 登录邮箱
STACKRYZE_PASSWORD       # Stackryze 登录密码
CLOUDFLARE_EMAIL         # Cloudflare 账号邮箱
CLOUDFLARE_API_KEY       # Cloudflare Global API Key
# 或者使用 API Token（推荐）
CLOUDFLARE_API_TOKEN     # Cloudflare API Token
```

### 配置文件

复制 `config.example.yml` 为 `config.yml` 并修改配置：

```yaml
stackryze:
  domain_suffix: "indevs.in"  # 可选: indevs.in, sryze.cc
  domain_prefix: "myapp"      # 域名前缀

cloudflare:
  zone_name: "myapp.indevs.in"
  dns_records:
    - type: "A"
      name: "@"
      content: "192.168.1.1"
      proxied: true
    - type: "CNAME"
      name: "www"
      content: "myapp.indevs.in"
      proxied: true
```

## 使用方法

### 1. 手动触发

在 GitHub 仓库的 Actions 页面，选择 "Auto Register Stackryze Domain" 工作流，点击 "Run workflow"。

### 2. 定时触发

工作流配置为每天 UTC 00:00 自动运行（可修改 cron 表达式）。

### 3. 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 运行测试
python scripts/register_stackryze.py
python scripts/add_to_cloudflare.py
```

## 注意事项

1. **域名限制**：每个 Stackryze 账号最多可注册 6 个域名
2. **频率限制**：Cloudflare API 有调用频率限制
3. **安全建议**：使用 GitHub Secrets 存储敏感信息
4. **浏览器自动化**：Stackryze 使用 GitHub 登录，需要处理 OAuth 流程

## 故障排除

### 常见问题

1. **登录失败**：检查邮箱和密码是否正确
2. **域名已存在**：尝试不同的域名前缀
3. **Cloudflare API 错误**：检查 API Key/Token 权限
4. **Playwright 超时**：增加超时时间或检查网络连接

## 开发计划

- [ ] 支持批量域名注册
- [ ] 添加域名续期功能
- [ ] 支持自定义 DNS 记录
- [ ] 添加 Slack/邮件通知
- [ ] 支持更多域名后缀

## 许可证

MIT License