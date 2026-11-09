---
id: "doc-b5d8fb85808a"
title: "Agent 工作日志 · bug-28370-danmaku-guest-name"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "监控告警"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28370-danmaku-guest-name.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28370-danmaku-guest-name.md"
sourceSha256: "0b6141a6280d5166b162bf50bc1c127f3d78e6ad974676ab6b5a9f815abceb9e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28370-danmaku-guest-name

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20bug-28370-danmaku-guest-name.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：Zandao Bug 28370 弹幕监控空用户显示游客

## 输入资料

- Zandao：`https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28370`
- 需求 ID：`ADM-907`
- PRD：`docs/prd/modules/kickoff-admin.md`
- 页面：`apps/admin/src/views/rooms/detail.vue`

## 问题原因

后台直播间详情的弹幕监控表格直接展示 `username` 字段；历史接口或实时 WS 数据里 `username` 为空时，用户列会显示为空白。

## 解决方案

新增弹幕用户展示兜底：当 `username` 为空或全空白时显示“游客”，并同步中英文 locale。禁言弹窗里的用户名称也使用同一兜底，避免提示文案为空。

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `git diff --check` | 通过 |
