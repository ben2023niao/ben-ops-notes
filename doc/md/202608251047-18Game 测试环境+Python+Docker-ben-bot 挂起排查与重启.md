---
id: "doc-ca4a2da06fb0"
title: "ben-bot 挂起排查与重启"
date: "2026-08-25T10:47:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-25_1047-%E3%80%90%E6%8E%92%E6%9F%A5%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E6%8C%82%E8%B5%B7%E6%8E%92%E6%9F%A5%E4%B8%8E%E9%87%8D%E5%90%AF.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-25_1047-【排查+运维记录】ben-bot挂起排查与重启.md"
sourceSha256: "2e5bdce9fad7b97d39ea5442facb4ac51dc533cc419b0f64c76a9f3efe91fd75"
sourceSystem: "project-doc"
---

# ben-bot 挂起排查与重启

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608251047-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BDocker-ben-bot%20%E6%8C%82%E8%B5%B7%E6%8E%92%E6%9F%A5%E4%B8%8E%E9%87%8D%E5%90%AF.md)

> 整理日期：2026-08-25 10:47｜日期依据：文件名日期

时间：2026-08-25 10:47
环境标签：ben-bot / 机器人 / 52.79.252.255

## 现象

用户反馈今天机器人“挂”了 2 次，要求排查并重启。

## 排查结论

1. **容器层正常**：`docker inspect` 显示 RestartCount=0、ExitCode=0、无 OOM、Status=running；宿主内存/负载正常；进程 11 线程存活 → 非崩溃/内存问题。
2. **根因①：每日 01:30 强制重建 ben-bot**。cron `/www/server/cron/06e6c84558f729480a33858c016b40dc` 每天 01:30 执行 `build_and_run_ben_bot.sh` 重建容器（今天 01:30 一次 + 06:25 人工一次 = 2 次重启）。若此时有发布/任务在跑会被中断，用户感知“挂”。
3. **根因②：发布进度消息 MarkdownV2 转义缺陷**。`app/benbot/executor.py` 的 `LiveOutputMessage` 以 `parse_mode="MarkdownV2"` 编辑进度消息，发布输出含未闭合代码块（precode）时 Telegram 拒绝编辑：`Can't parse entities: can't find end of precode entity`，进度卡住并重试（10:26 出现 7 次），表现为机器人“没反应”。

## 处理

- 执行 `build_and_run_ben_bot.sh` 重建重启 ben-bot（ben-bot:latest）。
- 验证：容器 Up、`ben-bot started`、启动通知 16/16 成功。

## 修复建议（待确认执行）

1. 每日 01:30 重建改为“代码有变更才重建”，并在 `build_and_run_ben_bot.sh` 执行前检查是否有进行中发布（进行中则跳过本轮重建），避免中断发布；
2. `LiveOutputMessage` 转义修复：代码块内容做 MarkdownV2 转义，或改用 HTML parse_mode（更稳妥），消除 `Can't parse entities`。

## 通知与提交

- 步骤 1-3 已发送 `18GAME_ 上线群（正式環境）`。
- 本地 Git 已提交（不 Push）。
