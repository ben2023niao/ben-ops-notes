---
id: "doc-4bafa36de2eb"
title: "2026-06-02 Admin System Config Remove Recharge Panel"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-remove-recharge-panel.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-remove-recharge-panel.md"
sourceSha256: "22c7afc5aeb3d954051611cf3d02f2f940500d4fb0e7cad4711839ac76af8a02"
sourceSystem: "project-doc"
---

# 2026-06-02 Admin System Config Remove Recharge Panel

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-remove-recharge-panel.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈系统配置页已经拆分 `钱包` / `充值` tab，`充值` tab 内不应再额外展示一块充值规则快捷表单。

## Changes

- 删除系统配置页 `充值` tab 顶部快捷编辑表单。
- 删除对应的充值表单状态、校验、保存逻辑和样式。
- 表格在 tab 未初始化时返回空结果，避免初始请求显示全量配置。
- `充值` tab 仍只展示 `wallet.recharge.*` 配置项，编辑统一走表格行编辑。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
