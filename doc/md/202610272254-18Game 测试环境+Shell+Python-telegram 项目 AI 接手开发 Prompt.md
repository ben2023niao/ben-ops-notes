---
id: "doc-37b23c5bf190"
title: "telegram 项目 AI 接手开发 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "监控告警", "自动化", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/telegram/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/telegram/doc/prompt.md"
sourceSha256: "f76162ddaf6bdcbcc1518c4ec2866361cfdaa83c39019385f746cf6a2da2c84b"
sourceSystem: "project-doc"
---

# telegram 项目 AI 接手开发 Prompt

> 来源文件：`~/Desktop/18game_devops/devops/python/telegram/doc/prompt.md`

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/python/telegram` 项目。这个项目是一个轻量 Telegram Relay 服务：对外提供 HTTP Webhook，接收告警或消息 JSON，然后调用 Telegram Bot API 转发到固定群组。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- Python 项目总索引：`devops/python/doc/prompt.md`
- ben-bot 机器人：`devops/python/ben-bot/doc/prompt.md`
- PHP 工具站通知：`devops/php/doc/prompt.md`
- Bash 脚本通知：`devops/bash/doc/prompt.md`

这个项目是通用 Telegram Relay，不是 ben-bot 菜单机器人。需要“按钮、权限、脚本执行、发版”的任务去 ben-bot；需要“外部 HTTP webhook 转发消息”的任务才优先看这里。

## 1. 项目定位

- 项目目录：`devops/python/telegram`
- 服务类型：FastAPI HTTP Webhook
- 容器名：`telegram-relay`
- 端口：`49152`
- 入口文件：`main.py`
- 部署脚本：`restart_telegram.sh`
- Compose 文件：`docker-compose.yml`
- 环境配置：`.env`

注意：`.env` 里通常包含 Telegram token 和 chat id。不要在回复、文档或提交信息里复制真实值。

## 2. 当前结构

```text
telegram/
├── Dockerfile
├── README.md
├── docker-compose.yml
├── main.py
├── requirements.txt
├── restart.log
├── restart_telegram.sh
├── .env
└── doc/
    └── prompt.md
```

## 3. 核心功能

`main.py` 提供：

```text
POST /telegram-webhook
```

支持的请求体格式：

```json
{
  "text": {
    "content": "报警信息内容"
  }
}
```

也支持：

```json
{
  "content": "报警信息内容"
}
```

或：

```json
{
  "message": "报警信息内容"
}
```

或：

```json
{
  "msg": "报警信息内容"
}
```

如果都解析不到，服务会把原始 JSON 转成字符串发送。

发送限制：

- 消息超过 4000 字符会截断并追加 `...[truncated]`。
- Telegram 发送接口使用 `sendMessage`。
- `parse_mode` 当前为 `HTML`。

## 4. 环境变量

必填：

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

服务启动时会检查这两个变量。缺失会直接抛出 RuntimeError。

配置来源：

- `docker-compose.yml` 使用 `env_file: .env`
- 本地直接运行时需要 shell 环境里导出

示例格式：

```env
[敏感内容已脱敏]
TELEGRAM_CHAT_ID=your_chat_id
```

不要把真实 token 写进 prompt、README 示例或 commit message。

## 5. 代码地图

### `main.py`

关键对象：

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `app = FastAPI()`
- `AliyunPayload`
- `aliyun_webhook()`

处理流程：

1. 尝试解析 JSON。
2. 解析失败时读取 raw body。
3. 从常见字段里提取内容。
4. 内容过长则截断。
5. 调用 Telegram Bot API。
6. 发送失败则返回 HTTP 500。
7. 成功返回 `{"status": "ok"}`。

当前 `AliyunPayload` 模型没有被路由直接使用，属于可清理或后续扩展点。

### `Dockerfile`

- 基于 `python:3.11-slim`
- 安装 `requirements.txt`
- 复制项目到 `/app`
- 暴露 `49152`
- 使用 uvicorn 启动 `main:app`

### `docker-compose.yml`

- service：`telegram-relay`
- container：`telegram-relay`
- restart：`always`
- 端口映射：`49152:49152`
- 从 `.env` 加载环境变量

### `restart_telegram.sh`

自动化流程：

1. 进入脚本所在目录。
2. 检查 `Dockerfile` 和 `docker-compose.yml`。
3. `docker build -t telegram-relay:latest .`
4. `docker compose down -v`
5. `docker compose up -d`
6. 打印容器状态。
7. 日志追加到 `restart.log`。

## 6. 运行方式

本地开发：

```bash
cd devops/python/telegram
pip install -r requirements.txt
export [敏感内容已脱敏]
export TELEGRAM_CHAT_ID="..."
uvicorn main:app --host 0.0.0.0 --port 49152
```

Docker 部署：

```bash
cd devops/python/telegram
bash restart_telegram.sh
```

测试请求：

```bash
curl -X POST http://203.0.113.1:49152/telegram-webhook \
  -H "Content-Type: application/json" \
  -d '{"text": {"content": "测试报警"}}'
```

## 7. 二次开发建议

### 增加健康检查

建议新增：

```text
GET /health
```

返回：

```json
{"status": "ok"}
```

这样容器和外部探活更方便。

### 支持更多告警格式

在 `aliyun_webhook()` 的解析逻辑里增加字段即可。常见来源：

- 阿里云告警
- Prometheus Alertmanager
- Grafana webhook
- 自定义 CI/CD 通知

### Telegram HTML 转义

当前 `parse_mode = "HTML"`。如果外部传入 `<`、`>`、`&`，可能导致 Telegram HTML 解析异常。建议后续引入：

```python
import html
content = html.escape(content)
```

如果用户希望支持富文本，则需要明确区分可信 HTML 和普通文本。

### 支持多群转发

当前 `TELEGRAM_CHAT_ID` 是单个值。可扩展为逗号分隔：

```text
TELEGRAM_CHAT_IDS=-100xxx,-100yyy
```

发送时循环调用 Telegram API。

### 增加鉴权

当前 webhook 没有鉴权。生产环境建议增加：

- URL token
- Header token
- Basic Auth
- IP allowlist

不要硬编码密钥，使用环境变量。

## 8. 常见坑

### 容器启动失败

检查：

```bash
docker logs telegram-relay
cat restart.log
```

常见原因：

- `.env` 不存在。
- `TELEGRAM_BOT_TOKEN` 缺失。
- `TELEGRAM_CHAT_ID` 缺失。
- 端口占用。

### 请求成功但群里没消息

检查：

- bot 是否在目标群。
- chat id 是否正确。
- bot 是否有发消息权限。
- Telegram API 是否返回 400/401/403。

### Telegram send failed

服务会返回 HTTP 500，错误在响应 detail 中。常见原因：

- token 错误。
- chat id 错误。
- 文本 HTML parse_mode 解析失败。
- 网络无法访问 Telegram API。

### restart.log 过大

`restart_telegram.sh` 会追加日志。需要定期清理：

```bash
: > devops/python/telegram/restart.log
```

## 9. 验证清单

语法：

```bash
python3 -m py_compile devops/python/telegram/main.py
bash -n devops/python/telegram/restart_telegram.sh
```

容器：

```bash
cd devops/python/telegram
bash restart_telegram.sh
docker ps | grep telegram-relay
docker logs --tail 100 telegram-relay
```

接口：

```bash
curl -s -X POST http://203.0.113.1:49152/telegram-webhook \
  -H "Content-Type: application/json" \
  -d '{"content": "hello"}'
```

预期：

```json
{"status":"ok"}
```

## 10. 安全边界

- 不要读取或输出 `.env` 真实内容。
- 不要把真实 bot token 写进文档。
- 不要默认开放公网 webhook 而没有鉴权，除非用户确认网络层已有防护。
- 不要把外部传入 HTML 原样发送到 Telegram，除非确认来源可信。
- 不要把 `restart.log` 中可能包含的敏感信息提交。

## 11. AI 接手流程

1. 先读 `main.py` 和 `README.md`。
2. 判断需求是解析格式、发送逻辑、部署、鉴权还是文档。
3. 修改后跑 `py_compile` 和 `bash -n`。
4. 如果涉及容器，执行 `restart_telegram.sh`。
5. 用 curl 验证 `/telegram-webhook`。
6. 回复用户时不要暴露 token/chat id，只说已读取环境变量。
