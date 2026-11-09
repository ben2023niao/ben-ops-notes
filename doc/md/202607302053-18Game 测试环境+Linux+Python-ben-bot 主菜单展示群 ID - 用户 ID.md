---
id: "doc-f48e082f27e2"
title: "ben-bot 主菜单展示群 ID / 用户 ID"
date: "2026-07-30T20:53:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_2053-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E4%B8%BB%E8%8F%9C%E5%8D%95%E5%B1%95%E7%A4%BA%E7%BE%A4ID%E7%94%A8%E6%88%B7ID.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_2053-【优化+运维记录】ben-bot主菜单展示群ID用户ID.md"
sourceSha256: "87dd4a8d833df78c99c8b7952c5b35fbafc64cb68e4bff9a233b00035dfff6e3"
sourceSystem: "project-doc"
---

# ben-bot 主菜单展示群 ID / 用户 ID

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607302053-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-ben-bot%20%E4%B8%BB%E8%8F%9C%E5%8D%95%E5%B1%95%E7%A4%BA%E7%BE%A4%20ID%20-%20%E7%94%A8%E6%88%B7%20ID.md)

> 整理日期：2026-07-30 20:53｜日期依据：文件名日期

环境标签：通用

时间：2026-07-30 20:53

分类：优化、运维记录、ben-bot、workbench

## 1. 背景

后续配置 Telegram 群通知、广播、话题群通知时，经常需要确认当前聊天的 `chat_id` 和操作人的 `user_id`。

这次按最新要求调整为：不单独做按钮，直接在 `/start` 主菜单的 `当前信息` 区块里展示 ID。

## 2. 使用方式

在群里：

```text
/start@game18_report_bot
```

在私聊里：

```text
/start
```

机器人会在主菜单里显示：

```text
当前信息
- 用户
- 用户ID
- 身份
- 权限
- 聊天ID
- 聊天类型
- 群名称
- 话题ID
```

说明：

- 在群里，`聊天ID` 就是当前群的 `chat_id`。
- 在私聊里，`聊天ID` 就是当前私聊 ID。
- 普通群或私聊没有话题时，不显示 `话题ID`。
- 论坛话题群如果需要固定通知到某个话题，需要同时记录 `聊天ID` 和 `话题ID`。

## 3. 当前菜单示例

```text
当前信息
- 用户：@Ben_Bird
- 用户ID：6922329530
- 身份：运维
- 权限：全部权限。
- 聊天ID：-1003929303643
- 聊天类型：supergroup
- 群名称：稳定备案域名+腾讯云原厂
```

## 4. 本次代码改动

修改文件：

```text
devops/python/ben-bot/app/benbot/home.py
devops/python/ben-bot/app/benbot/handlers/callbacks.py
devops/python/ben-bot/app/benbot/handlers/start.py
devops/python/ben-bot/app/benbot/main.py
devops/python/ben-bot/app/benbot/chat_identity.py
```

核心变化：

- `home.py` 的 `build_start_message()` 支持从当前消息读取聊天信息。
- `/start` 主菜单 `当前信息` 增加用户 ID、聊天 ID、聊天类型、群名称、话题 ID。
- 已撤掉首页 `查看群/用户ID` 按钮。
- 已撤掉 `info:chat` 按钮回调。
- 保留 `/id`、`/id@game18_report_bot` 作为隐藏兜底命令，不显示在主菜单按钮里。

## 5. 安全说明

- 只展示 Telegram 公开 ID 信息。
- 不读取服务器配置。
- 不输出 token、Secret Key、私钥、cookie、env 原文。
- 不修改发布、S3、COS、CDN、Nginx、DNS。

## 6. 部署记录

ben-bot 部署机：

```text
ubuntu@52.79.252.255
```

服务器仓库路径：

```text
/opt/telegram/18game_devops
```

机器人目录：

```text
/opt/telegram/18game_devops/devops/python/ben-bot
```

远程现场状态：

- 远程仓库存在大量历史现场改动，本次未执行 `git pull`。
- 为避免覆盖现场，本次只精确同步目标文件。
- 同步前已备份远程原文件。

远程备份目录：

```text
/opt/telegram/18game_devops/.codex-backup/benbot-chat-id-button-20260730204937/
/opt/telegram/18game_devops/.codex-backup/benbot-chat-id-command-20260730205803/
```

## 7. 验证记录

本地验证：

```text
python3 -m py_compile devops/python/ben-bot/app/benbot/chat_identity.py devops/python/ben-bot/app/benbot/home.py devops/python/ben-bot/app/benbot/handlers/callbacks.py devops/python/ben-bot/app/benbot/handlers/start.py devops/python/ben-bot/app/benbot/main.py
git diff --check
```

结果：

```text
通过
```

容器内验证：

```text
HAS_INFO_BUTTON=False
HAS_START_CHAT_ID=True
HAS_CHAT_ID_HANDLER=True
```

容器状态：

```text
ben-bot | ben-bot:latest | Up
```

## 8. 回滚方式

如需回滚：

```text
从备份目录恢复对应 py 文件
重新执行 build_and_run_ben_bot.sh
```

## 9. 飞机群通知

已按步骤通知：

```text
稳定备案域名+腾讯云原厂
```
