---
id: "doc-797cea400c9c"
title: "ben-bot 重启记录"
date: "2026-08-25T06:25:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-25_0625-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E9%87%8D%E5%90%AF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-25_0625-【运维记录】ben-bot重启记录.md"
sourceSha256: "c8bd032cc7d9de5ae976ef1c738ae70217ec65a165b2c4652b050fe6901c4e32"
sourceSystem: "project-doc"
---

# ben-bot 重启记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-25_0625-【运维记录】ben-bot重启记录.md`

> 整理日期：2026-08-25 06:25｜日期依据：文件名日期

时间：2026-08-25 06:25
环境标签：ben-bot / 机器人 / 52.79.252.255

## 操作

- 执行 `build_and_run_ben_bot.sh` 重建并重启 ben-bot 容器（ben-bot:latest）。

## 验证

- 容器：`ben-bot | Up | ben-bot:latest`。
- 启动日志：`ben-bot started`，角色权限正常（前端/测试/后端/运维/访客）。
- 启动通知：15 个目标，成功=15 失败=0。

## 说明

- 发布入口、前端域名维护、SSL 续签、值班提醒等依赖 ben-bot 的功能已恢复。
- 本次重启无代码变更，仅为恢复/刷新机器人进程。

## 通知与提交

- 步骤 1-2 已发送 `18game运维`。
- 本地 Git 已提交（不 Push）。
