---
id: "doc-bd18eb7f62af"
title: "Agent 工作日志 · bug-28377-hide-match-goal-entry"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28377-hide-match-goal-entry.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28377-hide-match-goal-entry.md"
sourceSha256: "7dce7a6be772db1f6d1dc44be22dd29c1d8c6670690c2d57ca11ca16a61265af"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28377-hide-match-goal-entry

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20bug-28377-hide-match-goal-entry.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：Zandao Bug 28377 隐藏后台赛事列表加进球入口

## 输入资料

- Zandao：`https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28377`
- 需求 ID：`ADM-204`
- PRD：`docs/prd/modules/kickoff-admin.md`
- 页面：`apps/admin/src/views/matches/list.vue`

## 问题原因

后台赛事列表操作列展示了“加进球”入口，但当前运营后台还没有明确的消费闭环说明，容易让测试和运营误以为该功能已完整交付。

## 解决方案

仅隐藏赛事列表操作列中的“加进球”按钮入口，保留 `GoalModal`、表单、API 调用和多语言文案，后续确认需要启用时可直接移除模板中的 `v-if="false"`。

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `git diff --check` | 通过 |
