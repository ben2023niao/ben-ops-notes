---
id: "doc-337e53e2b36f"
title: "Agent Log： Shark Web Device Type"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-web-device-type.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-web-device-type.md"
sourceSha256: "a10dd37b993d6946ffc9702dbf3ebe2d07a4847a4db449197cc6882e11eb219e"
sourceSystem: "project-doc"
---

# Agent Log： Shark Web Device Type

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-web-device-type.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

- Date: 2026-06-03
- Scope: WALLET-007 / Shark recharge
- Author: Codex

## Background

大白鲨后台显示 Web 端 iPhone Safari 充值订单的 `deviceType=ios`。当前产品 C 端是 Web/H5，不是原生 iOS App；如果仅按 User-Agent 上报 `ios`，可能让三方通道按 App/iOS 场景做路由或风控。

## Change

- `POST /api/v1/wallet/recharge/init` 将 `X-Client-Platform` 透传给 wallet service。
- Shark `deviceType` 生成规则调整：
  - `X-Client-Platform=web/h5/admin` → `pc`
  - `X-Client-Platform=ios` → `ios`
  - `X-Client-Platform=android` → `android`
  - header 缺失时保留 User-Agent fallback

## Validation

```bash
go test ./internal/service/wallet ./internal/http/public
```

Passed.
