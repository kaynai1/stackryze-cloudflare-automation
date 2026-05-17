# 使用指南

## 快速开始（3步完成）

### 第1步：配置 GitHub Secrets

1. 打开仓库：https://github.com/kaynai1/stackryze-cloudflare-automation
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 添加以下3个密钥：

#### Secret 1: STACKRYZE_EMAIL
```
名称: STACKRYZE_EMAIL
值: 你的Stackryze登录邮箱（GitHub邮箱）
```

#### Secret 2: STACKRYZE_PASSWORD
```
名称: STACKRYZE_PASSWORD
值: 你的Stackryze登录密码
```

#### Secret 3: CLOUDFLARE_API_TOKEN
```
名称: CLOUDFLARE_API_TOKEN
值: 你的Cloudflare API Token（获取方法见下方）
```

### 第2步：获取 Cloudflare API Token

1. 打开 https://dash.cloudflare.com/profile/api-tokens
2. 点击 **Create Token**
3. 选择 **Edit zone DNS** 模板
4. 配置权限：
   - Permissions: Zone → DNS → Edit
   - Zone Resources: Include → All zones
5. 点击 **Continue to summary** → **Create Token**
6. **复制**生成的 Token（只显示一次）

### 第3步：运行自动化

1. 打开仓库：https://github.com/kaynai1/stackryze-cloudflare-automation
2. 点击 **Actions** 标签
3. 左侧选择 **Auto Register Stackryze Domain to Cloudflare**
4. 点击 **Run workflow**
5. 填写参数：
   - **domain_prefix**: 输入你想要的域名前缀（如 `myapp`、`blog`、`api`）
   - **domain_suffix**: 选择 `indevs.in`（推荐）
6. 点击 **Run workflow** 按钮

## 等待运行完成

1. 点击正在运行的工作流
2. 查看 **register-domain** 任务的详细日志
3. 等待所有步骤完成（约3-5分钟）

## 运行结果

### 成功后你会得到：
- ✅ 一个免费域名：`你的前缀.indevs.in`
- ✅ 域名已托管到 Cloudflare
- ✅ DNS 记录已自动配置
- ✅ SSL 证书已启用

### 查看结果：
1. 登录 Cloudflare Dashboard：https://dash.cloudflare.com
2. 在 **Home** 页面可以看到新添加的域名
3. 点击域名可以管理 DNS 记录

## 常见问题

### Q1: 提示 "域名已被注册" 怎么办？
A: 换一个域名前缀重试，如 `myapp2`、`myproject` 等

### Q2: Stackryze 登录失败怎么办？
A: 检查邮箱和密码是否正确，确保能正常登录 https://domain.stackryze.com

### Q3: Cloudflare 添加域名失败怎么办？
A: 检查 API Token 权限是否正确，确保有 "Edit zone DNS" 权限

### Q4: 如何查看运行日志？
A: Actions → 点击运行的工作流 → 点击 register-domain → 查看详细日志

## 高级用法

### 批量注册多个域名
多次运行工作流，使用不同的域名前缀

### 自定义 DNS 记录
编辑仓库中的 `config.example.yml` 文件，修改 DNS 记录配置

### 定时自动运行
工作流已配置每天自动运行，可以在 `.github/workflows/auto-register.yml` 中修改时间

## 相关链接

- Stackryze 官网：https://domain.stackryze.com
- Cloudflare Dashboard：https://dash.cloudflare.com
- 仓库地址：https://github.com/kaynai1/stackryze-cloudflare-automation