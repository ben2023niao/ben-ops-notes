---
id: "doc-f360e09f32bb"
title: "2026-06-02 System Config Cleanup"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-cleanup.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-cleanup.md"
sourceSha256: "db3eec2270531cd23ca2a83a9f2931a9e93a3f14508f6c5bcb3fabcafee3086a"
sourceSystem: "project-doc"
---

# 2026-06-02 System Config Cleanup

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-2026-06-02%20System%20Config%20Cleanup.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈竞猜已下线，系统配置页不应展示竞猜配置；同时后台配置项过多，需要清理当前未被服务读取的历史占位配置。

## Decision

只保留当前服务实际从 `system_configs` 读取的运行时配置：

- `wallet.recharge.*`：充值规则、C 端公开配置、充值下单策略读取。
- `wallet.recharge.channels.*`：支付通道管理动态写入/读取。
- `home.support_*`：匿名客服联系方式读取。

删除历史占位项：

- `predict.*` / `feature.predict.enabled`
- 旧充值 RMB 别名 `wallet.recharge.*_rmb`
- 旧提现/调账占位项
- 未动态读取的直播、安全、首页轮播占位项

## Changes

- 新增 `000034_cleanup_system_configs` 迁移，删除已确认无读取的旧 key，并将客服配置归类到 `support`。
- 精简 `scripts/seed/seed.sql`，只保留客服联系方式；充值配置由 `000031` 维护。
- 后台系统配置 tab 改为按实际配置项生成，`wallet` 只有非充值项时才显示，`recharge` 只有充值项时才显示。
- 删除系统配置页 `predict` 分类显示文案。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
- `go test ./services/go-app/internal/service/admin ./services/go-app/internal/service/wallet`
