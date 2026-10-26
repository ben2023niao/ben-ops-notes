---
id: "doc-0434fcea17cb"
title: "php 目录 AI 接手维护 Prompt"
date: "2026-10-27T22:54:14+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "监控告警", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/php/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/php/doc/prompt.md"
sourceSha256: "e84728a6660c6464b9db158c5331214fcd745ce81320acb57e8fc3e0c2167062"
sourceSystem: "project-doc"
---

# php 目录 AI 接手维护 Prompt

> 来源文件：`~/Desktop/18game_devops/devops/php/doc/prompt.md`

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/php` 项目。这个目录是一个 PHP 8.3 容器化运维工具站，包含 Boce 余额/批量检测、Glances 监控展示、DNS/成本相关页面和若干历史工具脚本。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- Bash 辅助脚本：`devops/bash/doc/prompt.md`
- Telegram Relay：`devops/python/telegram/doc/prompt.md`
- 运维导航站入口：`devops/work.youdianse.com/doc/prompt.md`

这个项目是独立 PHP 工具站；如果页面入口要展示给运维同事，还要同步检查 `work.youdianse.com` 导航；如果涉及服务器部署路径或容器名，以 `ai_context` 中记录为准。

## 1. 项目定位

- 目录路径：`devops/php`
- 运行形态：Docker 容器
- 镜像基础：`php:8.3-cli-alpine3.20`
- 容器服务：PHP 内置服务器
- 容器端口：`8080`
- 默认镜像：`php-app:latest`
- 默认容器：`php-server`
- 入口目录：`public/`
- 公共库：`src/lib.php`
- 全局配置：`conf/config.php`

## 2. 当前结构

```text
php/
├── Dockerfile
├── README.md
├── deploy.sh
├── update.sh
├── conf/
│   └── config.php
├── src/
│   └── lib.php
├── public/
│   ├── index.php
│   ├── boce_balance.php
│   ├── boce_check_api.php
│   ├── dns.php
│   ├── dns_check.php
│   ├── glances.php
│   ├── glances-18game.php
│   ├── glances-php.php
│   ├── 项目成本管理.php
│   ├── 18game项目成本预估.html
│   ├── 黑客代码瀑布.php
│   └── 其他历史脚本
└── doc/
    └── prompt.md
```

注意：`public/add_ssh_key.key` 这类文件名暗示可能包含敏感 SSH key，不要读取、复制或写入文档。

## 3. 核心功能

### Boce 余额查询

- 路径：`/boce_balance.php`
- 用途：查询 Boce 账户余额和波点
- 支持 `?format=json`

### Boce 批量检测

- 路径：`/boce_check_api.php`
- 参数：`hosts=域名1,域名2,...`
- 用途：批量检测域名，异常可推送 Telegram

### Glances 监控

- 路径：`/glances.php`
- 相关变体：
  - `glances-18game.php`
  - `glances-php.php`
  - `glances_data/glances.php`
- 用途：抓取并展示服务器监控数据

### 导航与工具入口

- 路径：`/index.php`
- 用途：项目导航、余额卡片、批量检测表单和工具入口

### 其他历史工具

`public/` 下还有 DNS、成本报表、SSH key 添加、视觉页面等历史脚本。维护前必须先读代码并确认是否仍在使用。

## 4. 配置规则

README 说明所有敏感配置优先从环境变量读取：

- `BOCE_API_KEY`
- `TG_BOT_TOKEN`
- `TG_CHAT_ID`
- `CONSUMED_PER_HOST`

`deploy.sh` 会自动收集并传入：

- 明确变量：`BOCE_API_KEY`、`TG_BOT_TOKEN`、`TG_CHAT_ID`、`CONSUMED_PER_HOST`
- 其他以 `BOCE_` 或 `TG_` 开头的变量

不要把生产 API key 或 Telegram token 写进代码、README、prompt 或提交信息。

## 5. Docker 和部署

### `Dockerfile`

行为：

- 基于 PHP 8.3 Alpine
- 安装 curl 扩展
- 复制 `public/`、`src/`、`conf/`
- 创建可写目录
- 暴露 `8080`
- 健康检查 `http://localhost:8080/`
- 使用 PHP 内置服务器启动

### `deploy.sh`

支持操作：

```bash
./deploy.sh build
./deploy.sh start
./deploy.sh rebuild
./deploy.sh stop
./deploy.sh remove
./deploy.sh logs
./deploy.sh status
```

容器启动时会挂载：

- 项目目录到 `/app`
- `logs` 到 `/app/logs`
- `data` 到 `/app/data`

### `update.sh`

这是服务器上的绝对路径更新脚本，逻辑是：

1. 进入 `/opt/18game_devops/devops`
2. `git pull origin main`
3. 进入 `/opt/18game_devops/devops/php`
4. 执行 `bash deploy.sh rebuild`

修改前确认服务器实际路径仍然一致。

## 6. 公共函数

`src/lib.php` 提供：

- `http_get($url, $timeout = 10)`
- `safe_json_decode($text)`
- `normalize_hosts($input)`
- `send_telegram_message_simple($tgApi, $chatId, $text)`

新增接口时优先复用这些函数，不要在每个 PHP 文件里重复写 curl/JSON/Telegram 逻辑。

## 7. 二次开发建议

### 新增 API 页面

1. 在 `public/` 下新增 PHP 文件。
2. 如需配置，从环境变量读取。
3. 公共逻辑放 `src/lib.php`。
4. 在 `index.php` 加入口。
5. 更新 README 和本 prompt。

### 新增环境变量

1. 在 `conf/config.php` 或对应脚本里读取。
2. 在 `deploy.sh` 确认会传入容器。
3. 文档只写变量名，不写值。

### 修改 Glances 监控

先确认数据来源和写入路径。`Dockerfile` 中创建了 `/app/glances_data`，`public` 也被设置可写。不要让监控数据无限增长。

### 修改 Boce 检测

注意：

- 域名输入要经过 `normalize_hosts()`。
- 外部 API 调用要设置 timeout。
- 余额不足或检测异常时，Telegram 推送要避免刷屏。

## 8. 安全边界

- 不读取或输出 `public/add_ssh_key.key` 内容。
- 不提交 API key、TG token、SSH key。
- 不把接口改成任意命令执行。
- 不把 PHP 内置服务器暴露给不可信公网，除非有外层防护。
- 新增写文件功能时限制目录，避免路径穿越。
- 对用户输入的域名、URL、文件名做校验。

## 9. 验证清单

PHP 语法：

```bash
find devops/php -name '*.php' -print0 | xargs -0 -n1 php -l
```

Shell 语法：

```bash
bash -n devops/php/deploy.sh
bash -n devops/php/update.sh
```

容器验证：

```bash
cd devops/php
./deploy.sh rebuild
./deploy.sh status
./deploy.sh logs
curl -I http://localhost:8080/
```

接口验证：

```bash
curl "http://localhost:8080/boce_balance.php?format=json"
curl -G "http://localhost:8080/boce_check_api.php" --data-urlencode "hosts=example.com"
```

如果缺少真实 API key，只做语法和页面加载验证，不要伪造成功。

## 10. 常见坑

### 容器启动但访问旧代码

`deploy.sh` 挂载宿主目录到 `/app`，因此宿主代码会覆盖镜像内 COPY 的代码。确认当前目录是否正确。

### 环境变量没传入

检查：

```bash
docker exec php-server env | grep -E 'BOCE_|TG_|CONSUMED'
```

不要在回复里贴出真实值。

### 端口冲突

默认宿主端口是 `8080`。如需修改，改 `deploy.sh` 的 `PORT`。

### Telegram 推送失败

检查 token/chat id 是否存在、bot 是否在群里、消息是否太长。

## 11. AI 接手流程

1. 先读 `README.md`、`deploy.sh`、目标 PHP 文件。
2. 不读取敏感 key 文件。
3. 判断是页面问题、API 问题、容器问题还是配置问题。
4. 小范围修改。
5. 跑 `php -l` 和 `bash -n`。
6. 如需部署，执行 `deploy.sh rebuild`。
7. 最终回复说明修改文件、验证结果和是否需要配置真实环境变量。
