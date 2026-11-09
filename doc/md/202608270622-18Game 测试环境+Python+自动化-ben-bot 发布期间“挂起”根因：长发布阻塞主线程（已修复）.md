---
id: "doc-99e85f91ffed"
title: "ben-bot 发布期间“挂起”根因：长发布阻塞主线程（已修复）"
date: "2026-08-27T06:22:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-27_0622-%E3%80%90%E6%8E%92%E6%9F%A5%2B%E4%BF%AE%E5%A4%8D%E3%80%91ben-bot%E5%8F%91%E5%B8%83%E6%9C%9F%E9%97%B4%E6%8C%82%E8%B5%B7%E6%A0%B9%E5%9B%A0-%E9%95%BF%E5%8F%91%E5%B8%83%E9%98%BB%E5%A1%9E%E4%B8%BB%E7%BA%BF%E7%A8%8B.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-27_0622-【排查+修复】ben-bot发布期间挂起根因-长发布阻塞主线程.md"
sourceSha256: "7e376bf84f8d6807d8bf4206943345001d1ee389e363729afecac112e212f59c"
sourceSystem: "project-doc"
---

# ben-bot 发布期间“挂起”根因：长发布阻塞主线程（已修复）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608270622-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2B%E8%87%AA%E5%8A%A8%E5%8C%96-ben-bot%20%E5%8F%91%E5%B8%83%E6%9C%9F%E9%97%B4%E2%80%9C%E6%8C%82%E8%B5%B7%E2%80%9D%E6%A0%B9%E5%9B%A0%EF%BC%9A%E9%95%BF%E5%8F%91%E5%B8%83%E9%98%BB%E5%A1%9E%E4%B8%BB%E7%BA%BF%E7%A8%8B%EF%BC%88%E5%B7%B2%E4%BF%AE%E5%A4%8D%EF%BC%89.md)

> 整理日期：2026-08-27 06:22｜日期依据：文件名日期

时间：2026-08-27 06:22
环境标签：ben-bot / 机器人 / 发布 / 52.79.252.255

## 现象

用户再次反馈今天机器人“挂”了。昨日已修复 01:30 无变更重建（今早 01:30 已正确 skip），容器未崩溃、无 OOM，但发布期间机器人仍无响应。

## 根因（本次确认）

`app/benbot/executor.py` 的 `do_exec` 执行发布命令（H5/PC 发版，10-20 分钟）时，用 `delegator.run(block=False)` 后在**回调线程内同步循环读取输出并 `command.block()` 等待完成**。python-telegram-bot 轮询为单线程，发布全程机器人无法处理任何其它消息/按钮 → 表现为“挂”。

现场证据：06:16-06:19 有 2 个 H5 测试发布在跑（b6a77e6、229e2ee，JoliChang 触发），期间机器人无响应；容器/内存/日志正常。

## 处理（根治）

- `do_exec` 的 live 发布改为**后台 daemon 线程**执行（读取输出、编辑进度、`command.block()`、收尾通知都在线程内），回调立即返回 → 发布期间机器人保持响应。
- 非 live 短命令路径不变。
- 已同步运行机（原文件备份 `executor.py.bak.20260827`），重建重启 ben-bot。

注意：本次重启中断了当时 2 个 H5 测试发布（b6a77e6、229e2ee），需要由触发人重新触发。

## 验证

- py_compile 通过；容器重建启动（06:21:32），启动通知 16/17（1 个失败 chat_id=-4099404747 Unauthorized 为存量配置）。
- 旧发布进程已清空（0）。
- 01:30 守卫仍生效（今早 skip rebuild）。

## 遗留

- 清理启动通知中的失效 chat_id（-4099404747）。
- 发布进度消息 MarkdownV2 转义（`Can't parse entities`）仍建议修复（非本次挂起主因）。

## 通知与提交

- 本任务按用户要求不发群通知。
- 本地 Git 已提交（不 Push）。
