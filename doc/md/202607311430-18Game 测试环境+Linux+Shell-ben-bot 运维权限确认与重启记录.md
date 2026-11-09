---
id: "doc-56c823a982a1"
title: "ben-bot 运维权限确认与重启记录"
date: "2026-07-31T14:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-31_1430-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E8%BF%90%E7%BB%B4%E6%9D%83%E9%99%90%E7%A1%AE%E8%AE%A4%E4%B8%8E%E9%87%8D%E5%90%AF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-31_1430-【优化+运维记录】ben-bot运维权限确认与重启记录.md"
sourceSha256: "a80eb3223f6f4161c47965d2046d47b16c1503370f759d6cc8803b8c9cdfea55"
sourceSystem: "project-doc"
---

# ben-bot 运维权限确认与重启记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607311430-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-ben-bot%20%E8%BF%90%E7%BB%B4%E6%9D%83%E9%99%90%E7%A1%AE%E8%AE%A4%E4%B8%8E%E9%87%8D%E5%90%AF%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-31 14:30｜日期依据：文件名日期

环境标签：通用

时间：2026-07-31 14:30

## 背景

用户确认以下 Telegram 账号均属于运维成员，需要在 ben-bot 中拥有全部权限：

- `@Ben_Bird`
- `@Daviea2`
- `@jett_yunwei`
- `@melo_sre`
- `@Kermit0824`

## 本次处理结果

- 本地代码已确认 5 个账号均在 `OPS_USERNAMES` 中。
- 服务器代码已确认 5 个账号均在 `OPS_USERNAMES` 中。
- 容器内权限断言通过，5 个账号均识别为 `ops`。
- `ops` 角色具备全部权限，包括测试发布、线上发布、后端与定时任务入口、shell 类运维能力。
- ben-bot 已重启，容器状态正常。

## 服务器核验

部署机：

```text
ubuntu@52.79.252.255
```

服务器目录：

```text
/opt/telegram/18game_devops
```

容器：

```text
ben-bot
```

服务器现场情况：

- ben-bot 容器运行正常。
- 服务器工作区存在较多现场文件，本次没有执行 `git reset`，没有强制覆盖现场。
- 本次不涉及 token、密钥、DNS、CDN、COS、Nginx、数据库和发布脚本变更。

## 权限断言

容器内断言结果：

```text
Ben_Bird: role=ops, shell=True, paths=[True, True, True, True]
Daviea2: role=ops, shell=True, paths=[True, True, True, True]
jett_yunwei: role=ops, shell=True, paths=[True, True, True, True]
melo_sre: role=ops, shell=True, paths=[True, True, True, True]
Kermit0824: role=ops, shell=True, paths=[True, True, True, True]
ASSERT_OK
```

断言覆盖入口：

- `测试环境-游点涩-h5-发版`
- `测试环境-游点涩-pc-发版`
- `线上环境-游点涩-h5-发版`
- `后端与定时任务/线上后端发布`
- shell 类运维能力

## 重启验证

执行：

```bash
sudo docker restart ben-bot
```

验证：

```text
container=ben-bot status=Up
```

启动日志确认：

- 定时任务注册成功。
- 值班事件定时通知注册成功。
- ben-bot started。
- 角色权限说明中，运维列表包含 5 个账号。
- 启动通知目标数为 7，成功 7，失败 0。

## 通知群

本轮按用户要求同步通知以下群：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

`18GAME_ 上线群（正式環境）` 的 `chat_id` 已补充到 `workbench/NOTIFICATION_TARGETS.md`，本轮任务后续通知按三群同步执行。

## 后续注意

- 后续新增运维成员，统一维护 `app/benbot/constants.py` 的 `OPS_USERNAMES`。
- 不要在脚本里为单个用户散落写死权限。
- 修改权限后需要在容器内跑 `get_user_role()` 和 `can_access_script_path()` 断言。
- 重启后查看日志，确认启动通知成功发送。

## 追加排查：按钮点击无响应

时间：2026-07-31 14:35

用户反馈：机器人重启后点击按钮没反应。

排查结果：

- 不是部署错服务器，workbench、`servers.yml` 和历史文档均指向 `52.79.252.255`。
- 服务器上 `ben-bot` 容器运行正常。
- Telegram webhook 为空，当前是 long polling 模式。
- 未发现 polling conflict 抢占报错。
- 根因是 Telegram 当前 `allowed_updates` 不包含 `callback_query`，按钮点击事件不会投递给机器人。

修复方式：

```python
updater.start_polling(allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"])
```

影响范围：

- 只恢复按钮点击事件投递。
- 不修改权限名单。
- 不修改菜单结构。
- 不修改发布脚本。
- 不修改 token、密钥、DNS、CDN、COS、Nginx 或业务配置。

部署与验证：

- 远端原文件已备份：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-callback-query-20260731/main.py.bak
```

- 已单文件同步 `app/benbot/main.py` 到 ben-bot 部署机。
- 第一次以普通用户执行构建脚本时被 Docker socket 权限拒绝，未替换容器。
- 随后使用 `sudo -E ./build_and_run_ben_bot.sh` 正常重建镜像并重建容器。
- 启动日志确认 ben-bot started。
- 启动通知目标 7 个，成功 7，失败 0。
- Telegram `getWebhookInfo` 验证：

```text
allowed_updates = ["message", "callback_query", "my_chat_member", "chat_member"]
```

结论：

- 按钮点击事件已恢复投递到机器人。
- 旧消息上的按钮如果仍卡住，重新发送 `/start` 打开新菜单后再点。
