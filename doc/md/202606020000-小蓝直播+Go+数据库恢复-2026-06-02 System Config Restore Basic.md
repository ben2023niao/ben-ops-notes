---
id: "doc-bf18268d7529"
title: "2026-06-02 System Config Restore Basic"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-restore-basic.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-restore-basic.md"
sourceSha256: "8c74906a5bcdde87d503546ea1d6556a23d97f21832ab6fb51b098e85de17cb6"
sourceSystem: "project-doc"
---

# 2026-06-02 System Config Restore Basic

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-restore-basic.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户指出系统配置清理过度：不仅后台需要基础配置，部分 API 也依赖 `system_configs`。

## Correction

新增恢复迁移，不恢复竞猜配置，但恢复/保留当前 API 和服务仍使用的配置：

- `home.support_telegram`
- `home.support_email`
- `home.support_hint`
- `wallet.withdraw.min_amount`
- `wallet.withdraw.max_amount`

同时恢复 `home.banner_count` 作为基础运营配置，避免基础 tab 消失。

## Changes

- 新增 `000035_restore_basic_system_configs`。
- `home.support_*` 分类回到 `general`，后台显示为 `基础`。
- `wallet.withdraw.*` 分类为 `wallet`，后台显示为 `钱包`。
- `scripts/seed/seed.sql` 同步恢复基础/钱包配置，不恢复 `predict.*`。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
- `go test ./services/go-app/internal/service/admin ./services/go-app/internal/service/wallet`
