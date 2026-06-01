---
id: "doc-d8f6a8e3bb30"
title: "2026-06-02 Admin System Config Category Tabs"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-category-tabs.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-category-tabs.md"
sourceSha256: "b90b9d00f1e1b1bf03232a22352c48fcaecffae40e3c78a3b40e0df709af1fcd"
sourceSystem: "project-doc"
---

# 2026-06-02 Admin System Config Category Tabs

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-system-config-category-tabs.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈后台系统配置页已有配置分类，页面 tab 应直接按分类展示。

## Changes

- 将 `apps/admin/src/views/system/config.vue` 从固定 `充值规则 / 全部配置` tab 改为按 `system_configs.category` 动态生成 tab。
- 切换 tab 时按当前分类请求 `/system/config?category=<category>`。
- 移除重复的分类搜索表单，避免 tab 和筛选条件表达同一件事。
- `wallet` 分类下保留充值规则快捷编辑表单。
- 新增中英文分类显示名，未知分类回退显示原始 category。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
