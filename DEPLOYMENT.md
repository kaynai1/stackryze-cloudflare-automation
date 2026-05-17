# 部署指南

本文档将指导您如何部署和使用 Stackryze to Cloudflare 自动化工具。

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repository-url>
cd stackryze-cloudflare-automation
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库中设置以下 Secrets：

1. 进入仓库页面 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret" 添加以下密钥：

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `STACKRYZE_EMAIL` | Stackryze 登录邮箱 | `user@example.com` |
| `STACKRYZE_PASSWORD` | Stackryze 登录密码 | `your_password` |
| `CLOUDFLARE_EMAIL` | Cloudflare 账号邮箱 | `user@example.com` |
| `CLOUDFLARE_API_KEY` | Cloudflare Global API Key | `1234567890abcdef...` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Token（推荐） | `your_api_token` |

### 3. 获取 Cloudflare API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击右上角头像 → "My Profile"
3. 选择 "API Tokens" 标签
4. 点击 "Create Token"
5. 选择 "Edit zone DNS" 模板
6. 配置权限：
   - Permissions: Zone - DNS - Edit
   - Zone Resources: Include - Specific zone - 选择你的域名
7. 点击 "Continue to summary" → "Create Token"
8. 复制生成的 Token

### 4. 运行 GitHub Action

#### 手动触发

1. 进入仓库页面 → Actions
2. 选择 "Auto Register Stackryze Domain to Cloudflare"
3. 点击 "Run workflow"
4. 填写参数：
   - `domain_prefix`: 域名前缀（如 `myapp`）
   - `domain_suffix`: 域名后缀（选择 `indevs.in` 或 `sryze.cc`）
5. 点击 "Run workflow" 按钮

#### 定时触发

工作流已配置为每天 UTC 00:00 自动运行。如需修改，编辑 `.github/workflows/auto-register.yml`：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天 UTC 00:00
  # - cron: '0 */12 * * *'  # 每12小时
  # - cron: '0 0 * * 1'  # 每周一
```

### 5. 查看结果

1. 在 Actions 页面查看工作流运行状态
2. 点击具体的运行查看详细日志
3. 下载 "automation-logs" 查看详细日志和截图

## 本地测试

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，填入实际值
```

### 3. 测试配置

```bash
python test_config.py
```

### 4. 运行脚本

```bash
# 1. 注册 Stackryze 域名
python scripts/register_stackryze.py

# 2. 添加域名到 Cloudflare
python scripts/add_to_cloudflare.py

# 3. 配置 DNS 记录
python scripts/setup_dns.py
```

## 故障排除

### 常见问题

#### 1. GitHub Action 运行失败

**问题**: 工作流运行失败，日志显示认证错误

**解决方案**:
- 检查 GitHub Secrets 是否正确设置
- 确保 Secret 名称与代码中一致
- 检查 API Token 是否过期

#### 2. Stackryze 登录失败

**问题**: Playwright 无法登录 Stackryze

**解决方案**:
- 检查邮箱和密码是否正确
- 确保 GitHub 账号可以正常登录
- 增加超时时间：在 `config.yml` 中设置 `timeout: 60000`

#### 3. Cloudflare API 错误

**问题**: 添加域名时返回 403 错误

**解决方案**:
- 检查 API Token 权限
- 确保 Token 有 "Edit zone DNS" 权限
- 检查账户是否有添加域名的权限

#### 4. 域名已存在

**问题**: 提示域名已被注册

**解决方案**:
- 尝试不同的域名前缀
- 检查是否已经注册过该域名
- 等待24小时后重试

### 调试技巧

#### 启用详细日志

在 `config.yml` 中设置：

```yaml
logging:
  level: "DEBUG"
```

#### 截图调试

Playwright 脚本会在失败时自动截图。查看 `*.png` 文件了解失败时的页面状态。

#### 手动测试 Playwright

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 显示浏览器
    page = browser.new_page()
    page.goto('https://domain.stackryze.com')
    # 手动操作...
    browser.close()
```

## 安全注意事项

1. **永远不要**将密码或 API Key 提交到代码仓库
2. 使用 GitHub Secrets 存储敏感信息
3. 定期轮换 API Token
4. 限制 API Token 的权限范围
5. 监控 GitHub Actions 的运行日志

## 高级配置

### 自定义 DNS 记录

编辑 `config.yml` 中的 `dns_records` 部分：

```yaml
cloudflare:
  dns_records:
    - type: "A"
      name: "@"
      content: "192.168.1.1"
      proxied: true
    - type: "MX"
      name: "@"
      content: "mail.example.com"
      priority: 10
    - type: "TXT"
      name: "@"
      content: "v=spf1 include:example.com ~all"
```

### 批量注册

修改工作流输入，支持批量域名：

```yaml
inputs:
  domain_list:
    description: '域名列表（每行一个）'
    required: true
```

### 通知配置

配置 Slack 或邮件通知：

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
```

## 更新日志

### v1.0.0 (2026-05-17)
- 初始版本发布
- 支持 Stackryze 域名自动注册
- 支持 Cloudflare 域名自动添加
- 支持 DNS 记录自动配置
- 支持 GitHub Actions 自动运行

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 许可证

MIT License