---
id: "doc-25c79bf66aab"
title: "2026-06-02 System Config VXE Row Height"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-vxe-row-height.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-vxe-row-height.md"
sourceSha256: "d8ee61ff06c86b5c1dd14cbd75ef4e3e9f8f5f88830c775f3fb2f9f3db129238"
sourceSystem: "project-doc"
---

# 2026-06-02 System Config VXE Row Height

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-vxe-row-height.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈系统配置说明列仍然被 VXE 表格固定行高裁剪，看不清完整说明。

## Fix

- 按 `apps/admin/CLAUDE.md` 约束继续使用 Vben `useVbenVxeGrid` 和 Element Plus，不引入新组件库。
- 在系统配置表格局部关闭 `showOverflow`。
- 说明列显式 `showOverflow: false`。
- 使用局部 `:deep` 覆盖 VXE body 行/单元格固定高度、ellipsis 和 max-height，让说明内容撑开行高。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
