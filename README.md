# Stackryze 域名自动注册并托管到 Cloudflare

一键完成：输入账号密码 → 自动注册域名 → 自动托管到 Cloudflare

## 两种使用方式

### 方式一：GitHub Actions（推荐）

只需 3 步，无需安装任何软件：

#### 1. 打开仓库
https://github.com/kaynai1/stackryze-cloudflare-automation

#### 2. 点击 Actions 标签
选择 **一键注册 Stackryze 域名并托管到 Cloudflare**

#### 3. 点击 Run workflow，填写信息

| 字段 | 说明 | 示例 |
|------|------|------|
| GitHub 邮箱 | Stackryze 登录用的 GitHub 邮箱 | user@example.com |
| GitHub 密码 | Stackryze 登录用的 GitHub 密码 | your_password |
| 域名前缀 | 你想要的域名前缀 | myapp |
| Cloudflare 邮箱 | Cloudflare 账号邮箱 | user@example.com |
| Cloudflare API Key | Cloudflare Global API Key | 1234567890abcdef... |
| 服务器 IP | 你的服务器 IP（可选） | 192.168.1.1 |

**点击 Run workflow 后，等待 3-5 分钟即可完成！**

---

### 方式二：本地运行

#### 1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

#### 2. 运行脚本
```bash
python auto_register.py
```

#### 3. 输入信息
按提示输入账号密码即可

**Windows 用户可以直接双击 `run.bat` 运行**

---

## 运行结果

成功后你会得到：
- ✅ 免费域名：`你的前缀.indevs.in`
- ✅ 已托管到 Cloudflare
- ✅ DNS 记录已配置
- ✅ SSL 证书已启用
- ✅ HTTPS 已开启

## 查看结果

1. 登录 https://dash.cloudflare.com
2. 在 Home 页面可以看到新域名
3. 等待几分钟后访问：`https://你的前缀.indevs.in`

## 获取 Cloudflare API Key

1. 登录 https://dash.cloudflare.com/profile/api-tokens
2. 点击 **Create Token**
3. 选择 **Edit zone DNS** 模板
4. 权限设置：Zone → DNS → Edit
5. 创建并复制 Token

## 常见问题

**Q: 域名已被注册怎么办？**
A: 换一个域名前缀重试，如 `myapp2`、`myproject`

**Q: 登录失败怎么办？**
A: 检查 GitHub 邮箱和密码是否正确

**Q: 如何查看运行日志？**
A: GitHub Actions → 点击运行的工作流 → 查看详细日志

## 文件说明

```
├── auto_register.py      # 主脚本
├── run.bat               # Windows 一键运行
├── requirements.txt      # Python 依赖
├── .github/workflows/    # GitHub Action
└── README.md             # 说明文档
```

## 相关链接

- Stackryze 官网：https://domain.stackryze.com
- Cloudflare Dashboard：https://dash.cloudflare.com
- 仓库地址：https://github.com/kaynai1/stackryze-cloudflare-automation