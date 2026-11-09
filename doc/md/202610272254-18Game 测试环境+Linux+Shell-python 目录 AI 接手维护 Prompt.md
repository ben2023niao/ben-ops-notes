---
id: "doc-b996913db0c1"
title: "python 目录 AI 接手维护 Prompt"
date: "2026-10-27T22:54:15+08:00"
dateSource: "文件创建/修改时间"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "自动化", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/doc/prompt.md"
sourcePath: "~/Desktop/18game_devops/devops/python/doc/prompt.md"
sourceSha256: "3c2c18a6fcff9bdda7c8357db56cf149ba1e39b92595149cfa1745fe06337646"
sourceSystem: "project-doc"
---

# python 目录 AI 接手维护 Prompt

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610272254-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-python%20%E7%9B%AE%E5%BD%95%20AI%20%E6%8E%A5%E6%89%8B%E7%BB%B4%E6%8A%A4%20Prompt.md)

> 整理日期：2026-10-27 22:54｜日期依据：文件创建/修改时间

你正在接手 `devops/python` 目录。这个目录下面不是一个单一 Python 包，而是多个彼此独立的小项目集合。每个一级子目录都应被当作独立项目处理，不要跨项目随意共用依赖、部署脚本或配置。

## 0. 关联文档

- 仓库总入口：`.github/copilot-prompt-instructions.md`
- 服务器上下文：`devops/ai_context/doc/prompt.md`
- Bash 运维脚本：`devops/bash/doc/prompt.md`
- PHP 工具站：`devops/php/doc/prompt.md`
- 运维导航站：`devops/work.youdianse.com/doc/prompt.md`
- 周报生成：`work-运维部工作进度-周报/doc/prompt.md`

`devops/python` 是 Python 项目的总索引。进入具体子项目后必须再读该子项目自己的 `doc/prompt.md`；涉及服务器、容器、线上路径时再回到 `ai_context` 校验。

## 1. 目录定位

- 目录路径：`devops/python`
- 类型：多个 Python 项目集合
- 当前一级项目：
  - `18game`
  - `ben-bot`
  - `dns_monitor`
  - `dns_monitor_pywebio`
  - `s3-manager-app-apk`
  - `telegram`

每个项目都有自己的用途、依赖、运行方式和安全边界。详细说明应优先读取各自的 `doc/prompt.md`。

## 2. 子项目索引

### `18game`

临时模拟工具项目。

- 核心脚本：`sim_user.py`
- 用途：模拟不同地区和运营商用户提交线路测速结果。
- 文档：`devops/python/18game/doc/prompt.md`

### `ben-bot`

Telegram 运维机器人项目。

- 入口：`app/bot.py`
- 主包：`app/benbot`
- 菜单脚本：`data/scripts`
- 部署：`build_and_run_ben_bot.sh`
- 容器：`ben-bot`
- 文档：`devops/python/ben-bot/doc/prompt.md`

重点事实：

- H5 测试发布和线上发布是根按钮。
- 测试 H5 发布公共可执行。
- 线上 H5 发布运维专属。
- 脱敏配置查看公共可执行。
- `/sh`、上传、下载运维专属。

### `dns_monitor`

Flask API 版 DNS 污染 + SNI 阻断检测服务。

- 核心文件：`dns_monitor/app.py`
- 端口：`59000`
- 部署：`deploy_dns_monitor.sh`
- 文档：`devops/python/dns_monitor/doc/prompt.md`

注意：`deploy_dns_monitor.sh` 可能会重写 `dns_monitor/app.py`，改检测逻辑时要同步检查。

### `dns_monitor_pywebio`

PyWebIO 可视化 DNS 检测平台。

- 核心文件：`dns_monitor/app.py`
- 端口：`59999`
- 部署：`deploy_dns_monitor.sh` 或 `docker compose up -d --build`
- 文档：`devops/python/dns_monitor_pywebio/doc/prompt.md`

### `s3-manager-app-apk`

FastAPI + S3 + Telegram 的文件管理后台集合。

- 子项目：
  - `s3-manager-18gane-prod`
  - `s3-manager-18gane-test`
  - `s3-manager-xcp-prod`
- 每个子项目有自己的 `app.py`、`Dockerfile`、`deploy.sh`
- 文档：`devops/python/s3-manager-app-apk/doc/prompt.md`

注意：历史代码/脚本可能有明文凭证，维护时不要复制或扩散。

### `telegram`

FastAPI Telegram Relay Webhook 服务。

- 入口：`main.py`
- 端口：`49152`
- 容器：`telegram-relay`
- 部署：`restart_telegram.sh`
- 文档：`devops/python/telegram/doc/prompt.md`

## 3. 总体安全规则

`devops/python` 下多个项目接触 Telegram、AWS、SSH、S3、服务器配置和发布流程。维护时必须：

- 不读取或输出 `.env`、私钥、凭证 CSV 的真实内容。
- 不把 token、AWS key、SSH key 写进 prompt、README 或提交信息。
- 不把线上发布权限随意放开。
- 不把生产配置原文写入日志或文档。
- 提交前先检查 `git status --short --branch`，避免混入无关删除或未跟踪文件。

## 4. 推荐接手流程

收到用户需求时：

1. 判断用户指的是哪个子项目。
2. 进入对应项目目录。
3. 先读该项目 `doc/prompt.md`。
4. 再读 README、入口文件、部署脚本。
5. 小范围修改。
6. 运行该项目自己的验证命令。
7. 如果用户要求部署，再按对应项目文档部署。

## 5. 常用验证命令

### Python 语法检查

```bash
python3 -m py_compile <file.py>
```

### Shell 脚本检查

```bash
bash -n <script.sh>
```

### Docker 状态

```bash
docker ps
docker logs --tail 100 <container>
```

## 6. 工作区提醒

这个仓库可能长期存在：

- 用户未跟踪周报草稿
- 历史目录删除状态
- 运行日志
- 上传附件

不要因为要提交某个 Python 项目，就把整个仓库的变更一起 `git add -A`。应只暂存目标文件。

## 7. AI 接手原则

- 每个子目录是独立项目。
- 优先读项目自己的 `doc/prompt.md`。
- 不确定时先只读检查。
- 修改部署脚本前确认运行环境。
- 修改涉及凭证的逻辑时优先改成环境变量。
- 最终回复要说清楚影响哪个子项目，而不是笼统说“python 已修改”。
