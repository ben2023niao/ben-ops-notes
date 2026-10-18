---
id: "doc-36873d6bbacf"
title: "Token 与 AI 接入"
date: "2026-10-19T20:33:45+08:00"
dateSource: "文件创建/修改时间"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/workbench-kit-%E9%80%9A%E7%94%A8AI%E5%B7%A5%E4%BD%9C%E5%8F%B0/docs/06-Token%E4%B8%8EAI%E6%8E%A5%E5%85%A5.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/workbench-kit-通用AI工作台/docs/06-Token与AI接入.md"
sourceSha256: "5c7ed47abb8ec8d9de30faaa008593b7ca3df5ccb6edc6b0e96e68ec23497b8f"
sourceSystem: "project-doc"
---

# Token 与 AI 接入

> 来源文件：`~/Projects/work/ops/devops/devops-bkl/workbench-kit-通用AI工作台/docs/06-Token与AI接入.md`

> 整理日期：2026-10-19 20:33｜日期依据：文件创建/修改时间

## 1. 先分清三类 Token

| 类型 | 用途 | 典型变量 | 权限 |
| --- | --- | --- | --- |
| AI API Key | 调模型 | `OPENAI_API_KEY`、`DEEPSEEK_API_KEY` | 按量计费，泄露会被盗刷 |
| Telegram Bot Token | 发通知 | `TELEGRAM_API_TOKEN` | 可控制机器人，泄露可被冒用 |
| GitLab PAT | 拉代码 / CI / API | `GITLAB_TOKEN` | 按 scope，泄露可改仓库 |

三类都不要提交到 Git。

## 2. 存放原则

```text
优先级：系统环境变量 > 本地 .env（已 gitignore）> 密码管理器
禁止：代码默认值、README、群消息、截图、提交历史
```

推荐目录：

```text
~/.config/workbench/ai.env          个人 AI Key
<project>/workbench/notify.env      项目通知配置（已 gitignore）
```

权限：

```bash
chmod 600 ~/.config/workbench/ai.env
chmod 600 workbench/notify.env
```

## 3. AI API Key

### 3.1 常见变量

```bash
export [敏感内容已脱敏]
export OPENAI_BASE_URL="https://api.openai.com/v1"

export [敏感内容已脱敏]
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

export [敏感内容已脱敏]
```

本地模型（Ollama）通常不需要 Key：

```bash
export OLLAMA_BASE_URL="http://203.0.113.1:11434"
```

### 3.2 加载方式

临时：

```bash
set -a
source ~/.config/workbench/ai.env
set +a
```

每次开终端自动加载（zsh）：

```bash
# ~/.zshrc
[ -f "$HOME/.config/workbench/ai.env" ] && set -a && source "$HOME/.config/workbench/ai.env" && set +a
```

### 3.3 验证 Key

不要用 `echo $KEY`。直接发一个最小请求：

```bash
curl -sS https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | head -c 300
```

返回模型列表或权限错误，说明 Key 能被识别。

DeepSeek（OpenAI 兼容）：

```bash
curl -sS https://api.deepseek.com/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  | head -c 300
```

### 3.4 OpenAI 兼容服务

很多服务都兼容 OpenAI 的 `/v1/chat/completions`：

| 服务 | Base URL 示例 | 说明 |
| --- | --- | --- |
| OpenAI | `https://api.openai.com/v1` | 官方 |
| DeepSeek | `https://api.deepseek.com` | 性价比高 |
| Ollama | `http://203.0.113.1:11434/v1` | 本地 |
| vLLM | `http://内网:8000/v1` | 自建 |
| LM Studio | `http://203.0.113.1:1234/v1` | 本地桌面 |

只要插件支持 “OpenAI Compatible”，就可以填 Base URL + Key + Model。

## 4. VS Code 里怎么接

### 4.1 GitHub Copilot

- 安装 `github.copilot`、`github.copilot-chat`
- 登录 GitHub 账号
- 不需要自己填 API Key
- 企业版由组织统一管理

### 4.2 Continue

1. 安装 `continue.continue`
2. 打开 Continue 侧边栏 → Settings
3. 选 Provider：
   - OpenAI
   - Anthropic
   - OpenAI Compatible（DeepSeek / vLLM / Ollama）
   - Ollama
4. 填 Base URL、Model、API Key
5. Key 放插件密钥存储或引用环境变量

示例思路（字段名以插件当前版本为准）：

```yaml
models:
  - name: deepseek-chat
    provider: openai
    apiBase: https://api.deepseek.com
    敏感凭据：[已脱敏]
    model: deepseek-chat
```

如果插件不认环境变量语法，就在设置页填 Key，并把配置文件加入 `.gitignore`。

### 4.3 Cline

1. 安装 Cline
2. 选 API Provider：OpenAI Compatible
3. Base URL：例如 `https://api.deepseek.com`
4. API Key：填对应 Key
5. Model：填服务商提供的模型名

Cline 能自动改文件、跑命令。第一次用建议：

- 开新分支
- 先让它输出 plan
- 每一步看 diff
- 高风险命令人工确认

### 4.4 Codex

两种常见方式：

1. 账号登录（按你使用的 Codex 客户端提示）
2. 环境变量 `OPENAI_API_KEY`

在项目根目录放 `AGENTS.md`，Codex 会按规则读取。

### 4.5 本地模型

Ollama：

```bash
ollama serve
ollama pull qwen2.5-coder
```

插件里选 Ollama，Base URL `http://203.0.113.1:11434`，Model `qwen2.5-coder`。

优点：不花钱、数据不出内网。
缺点：复杂任务能力取决于模型和机器。

## 5. Telegram 机器人

### 5.1 创建机器人

1. Telegram 搜 `@BotFather`
2. `/newbot`
3. 填名称和用户名
4. 保存 token（只保存到密码管理器或 `notify.env`）

### 5.2 拉进群

1. 把机器人拉进目标群
2. 给机器人发消息权限
3. 在群里发一条消息
4. 获取 chat_id：

```bash
curl -sS "https://api.telegram.org/bot$TELEGRAM_API_TOKEN/getUpdates" \
  | python3 -m json.tool | grep -E '"id"|"title"|"type"'
```

群 chat_id 通常是负数，supergroup 以 `-100` 开头。

### 5.3 配置

```bash
cp workbench/notify.env.example workbench/notify.env
chmod 600 workbench/notify.env
```

```dotenv
[敏感内容已脱敏] token>
TELEGRAM_CHAT_ID=<chat id>
```

### 5.4 验证

```bash
python3 workbench/scripts/notify.py --verify-chat
python3 workbench/scripts/notify.py --title "测试" --text "通知链路正常"
```

### 5.5 通知规范

- 每步一次，不刷屏
- 标题固定：`【项目名｜任务名】步骤 N ...`
- 不发密码、token、连接串、完整 URL 签名
- 发失败要记录，不能假装成功

## 6. GitLab Token

### 6.1 创建 PAT

GitLab → 用户设置 → Access Tokens：

- Name：`workbench-local`
- Expiration：30 天或 90 天
- Scopes：
  - `read_repository`：只拉代码
  - `write_repository`：要推送
  - `api`：要调 API / CI

最小权限原则：只给当前任务需要的 scope。

### 6.2 本地使用

不要把 token 写进 remote URL。用 credential helper：

```bash
git config --global credential.helper osxkeychain   # macOS
# 或
git config --global credential.helper store         # Linux，注意文件权限
```

第一次 push 输入用户名和 PAT，之后由系统保存。

### 6.3 GitLab CI

在项目 Settings → CI/CD → Variables：

- Key：`GITLAB_TOKEN`
- Value：PAT
- Masked：是
- Protected：是（只给受保护分支）

流水线里用 `$GITLAB_TOKEN`，不要写进 `.gitlab-ci.yml`。

## 7. 密钥管理进阶

### 7.1 direnv

项目目录放 `.envrc`（加入 `.gitignore`）：

```bash
export [敏感内容已脱敏]
```

进入目录自动加载，离开自动卸载。

### 7.2 密码管理器 CLI

1Password：

```bash
export [敏感内容已脱敏]
```

Bitwarden：

```bash
export [敏感内容已脱敏]
```

### 7.3 轮换

- AI Key：怀疑泄露立即在服务商后台吊销
- Telegram：BotFather `/revoke`
- GitLab：Access Tokens 页面 Revoke
- 轮换后更新本地 `notify.env` / CI 变量

## 8. 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 401 Unauthorized | Key 错、过期、带空格 | 重新复制，检查环境变量 |
| 403 Forbidden | 权限不足 / 地区限制 | 检查 scope、账号、网络 |
| 429 Too Many Requests | 限流 / 余额不足 | 降频、换 Key、看账单 |
| chat not found | chat_id 错 / 机器人不在群 | 重新 getUpdates，拉机器人进群 |
| 通知 400 | 消息太长 / HTML 不合法 | 截断、去掉特殊标签 |
| Git push 403 | PAT 无 `write_repository` | 重新建 token |
| Git push 要求密码 | 用了 PAT 但没走 credential helper | 配置 helper，用户名填 GitLab 用户名 |

## 9. 安全检查清单

- [ ] `git status` 没有 `.env`、`notify.env`、密钥、证书
- [ ] `.gitignore` 包含 `.env`、`notify.env`、`*.pem`、`*.key`
- [ ] 代码里没有硬编码 token
- [ ] 通知内容不含秘密
- [ ] CI 变量是 Masked + Protected
- [ ] PAT 有过期时间
- [ ] 离职 / 换人后立即轮换
