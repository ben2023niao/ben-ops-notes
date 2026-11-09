---
id: "doc-a8609bbab99c"
title: "ben-bot 运维任务编排按钮修复与双 Vaultwarden 任务（v1.0.6）"
date: "2026-10-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "CDN", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-26-%E3%80%90%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%8A%9F%E8%83%BD%E3%80%91%E8%BF%90%E7%BB%B4%E4%BB%BB%E5%8A%A1%E7%BC%96%E6%8E%92%E6%8C%89%E9%92%AE%E4%B8%8E%E5%85%A8%E5%B1%80Task%E7%9C%8B%E6%9D%BF.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-26-【机器人功能】运维任务编排按钮与全局Task看板.md"
sourceSha256: "1f5885f1755ac450b4281c61affff99bbd097739462f84597963fdf7b56d41e7"
sourceSystem: "project-doc"
---

# ben-bot 运维任务编排按钮修复与双 Vaultwarden 任务（v1.0.6）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610260000-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-ben-bot%20%E8%BF%90%E7%BB%B4%E4%BB%BB%E5%8A%A1%E7%BC%96%E6%8E%92%E6%8C%89%E9%92%AE%E4%BF%AE%E5%A4%8D%E4%B8%8E%E5%8F%8C%20Vaultwarden%20%E4%BB%BB%E5%8A%A1%EF%BC%88v1.0.6%EF%BC%89.md)

> 整理日期：2026-10-26 00:00｜日期依据：文件名日期

- 时间：2026-10-26（Asia/Manila）
- 环境：游点涩线上 ben-bot
- 运行机：`ubuntu@52.79.252.255`
- 容器：`ben-bot`
- 版本：`v1.0.6`
- 代码提交：`18game_devops/b63add3`
- 结论：任务编排按钮已恢复；最新任务已变更为部署 2 套 Vaultwarden，分别存放账号和密码

## 一、问题现象

点击首页 `🗂 运维任务编排` 后没有可见反应。

检查确认：

- 首页按钮存在，callback 为 `tasks:board`；
- callback 已进入 `shortcut_cb` 的 `tasks` 分支；
- 权限正常，不是按钮缺失或账号权限问题；
- Telegram 日志明确报错：

```text
Can't parse entities: character '.' is reserved and must be escaped with the preceding '\'
```

## 二、根因

任务看板和任务详情使用 Telegram `MarkdownV2` 渲染。编号原本直接生成：

```text
1. 任务名称
2. 任务名称
```

`MarkdownV2` 中 `.` 是保留字符，必须转义为 `1\.`、`2\.`。原实现只转义了任务标题和正文，没有转义列表编号。

因此 callback 已响应，但 `answer_callback()` 之后的 `edit_text()` 失败，用户看到的就是“点击没反应”。

## 三、修复内容

### 1. MarkdownV2 编号转义

修复文件：

- `devops/python/ben-bot/app/benbot/task_board.py`

任务看板和任务详情的一级编号统一通过 `escape_markdown_v2()` 生成：

```text
1\. 🔐 任务名称
2\. 任务名称
```

二级项目符号不受影响。

### 2. 最新任务变更为双 Vaultwarden

任务数据文件：

- `devops/python/ben-bot/app/benbot/ops_tasks.json`

原最新任务“18Mod 项目账号与 CDN 基建”变更为：

```text
全项目账号密码安全服务 - 部署 2 套 Vaultwarden
```

部署要求：

- 使用 Docker 分开部署 2 套 Vaultwarden；
- 第 1 套只存账号，由 `@jett_yunwei` 负责；
- 第 2 套只存密码，由 `@Kermit0824` 负责；
- 两套服务使用独立域名、容器、volume 和访问入口；
- Vaultwarden 仅监听 `203.0.113.1:8080`，外层由 Nginx 提供 HTTPS 与访问验证；
- 启用 Google Authenticator / 验证器应用 TOTP 2FA；
- 覆盖游点涩、老司机短视频、18Mod、1game-UGC影游平台、视频处理与存储项目；
- `@melomeloo1009 @fyb99 @Vesper688` 配合完成分类、补录和迁移；
- `@jett_yunwei` 负责整理老旧、废弃账号，重点核对 msb 与物理机房历史账号；
- 两套服务验收后分别导出 JSON 备份，发送文件给机器人保存。

Docker 参考：

```bash
docker run -d \
  --name vaultwarden \
  --restart unless-stopped \
  -p 203.0.113.1:8080:80 \
  -v vaultwarden_data:/data \
  -e DOMAIN="https://实际域名" \
  vaultwarden/server:latest
```

上线后进入“设置 → 安全 → 两步登录”，选择验证器应用并扫码绑定 TOTP。

### 3. 任务范围

看板保留原有其余 4 项任务，最新到最旧为：

1. 全项目账号密码安全服务 - 部署 2 套 Vaultwarden
2. 老司机短视频 - 域名申请与 CDN 配置
3. 1game-UGC影游平台 - 测试环境、基础设施与统一门户
4. 视频处理与存储专用服务器
5. HTML 落地页部署与域名配置

## 四、安全与变更控制

- 本次只同步 ben-bot 的 `task_board.py`、`ops_tasks.json`、`constants.py` 和 README；
- 运行机仓库存在历史脏工作区，本次没有执行 `git reset`、`git clean` 或全量覆盖；
- 修改前文件备份在运行机：

```text
/root/benbot-vaultwarden-20261026-1412/
```

- 同步后本地与线上 3 个运行文件 SHA256 完全一致；
- 文件权限保持 `root:root 644`；
- 未输出、写入或提交任何 Telegram Token、密码或私钥。

## 五、验证结果

### 本地验证

- 7 项单元测试通过；
- Python 编译通过；
- JSON 校验通过；
- `git diff --check` 通过；
- 看板正文 621 字；
- Vaultwarden 详情 1458 字；
- 首页任务按钮 6 行，符合 Telegram 限制；
- 看板和详情均不存在未转义的一级编号。

### 线上验证

- `ben-bot` 容器重建成功，状态 running；
- 容器内版本为 `v1.0.6`；
- 容器内确认看板、详情、按钮和任务内容正确；
- 已向“18GAME_ 上线群（正式環境）”发送任务看板，消息 ID `14018`；
- 实际执行“任务看板 → Vaultwarden 详情 → 任务看板”两次 `editMessageText`，均成功；
- 不再出现 `character '.' is reserved` 报错。

## 六、后续要求

- Vaultwarden 部署属于下周任务，当前先完成平台代码更新；
- 两套 Vaultwarden 必须保持账号与密码分离，不能共用同一个 volume；
- 不得直接暴露 Vaultwarden 应用端口；
- 恢复码必须离线保存，不能只保存在 Vaultwarden 自身；
- 新增、迁移或停用账号后，负责人需要同步更新任务状态；
- 后续再调整任务内容时只维护 `ops_tasks.json`，并运行 `test_task_board.py`。
