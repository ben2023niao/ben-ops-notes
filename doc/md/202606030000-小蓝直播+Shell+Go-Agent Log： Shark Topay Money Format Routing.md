---
id: "doc-0f9816050554"
title: "Agent Log： Shark Topay Money Format Routing"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-topay-money-format.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-topay-money-format.md"
sourceSha256: "fd9a25dfc74fa760bbfe8912edef66b64960abe05302ed43f0f7c44bc6ee96f7"
sourceSystem: "project-doc"
---

# Agent Log： Shark Topay Money Format Routing

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20Log%EF%BC%9A%20Shark%20Topay%20Money%20Format%20Routing.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

- Date: 2026-06-03
- Scope: WALLET-007 / payment shark recharge
- Author: Codex

## Background

用户反馈大白鲨微信支付页显示“未匹配到 10 金额”，大白鲨后台订单存在但 `payStatus=未知`、`notifyStatus=未回调`。

## Document Check

Reviewed `/Users/qx/Downloads/大白鲨API文档.pdf`.

- `topay` endpoint: `POST /api/shark/topay`.
- `money` is a string, unit RMB/USDT, maximum two decimal places.
- `topay` sign: `md5(mercId + money + notifyUrl + tradeNo + type + appSecret)`.
- Callback is only sent after successful user payment.
- Callback success response must be plain text `success`.
- `getPayType` returns supported pay types for requested amounts; unsupported amounts should not be ordered.

## Verification

On dev server, the callback URL is reachable:

```text
https://api-dev.54-151-131-132.sslip.io/api/v1/hooks/payment/shark
```

An unsigned manual POST reached the handler and returned `success` while logging invalid signature, proving routing is open.

Manual gateway probes showed:

- `getPayType` accepts both `10` and `10.00` for WeChat.
- `topay money=10 type=wechat` returned a normal gateway URL.
- `topay money=10.00 type=wechat` returned the same cashier URL family shown in the user screenshot, which then reported amount mismatch.
- `topay money=100` and `topay money=100.00` both returned normal gateway URLs, so this is an amount/downstream-route compatibility issue rather than a global signing failure.

## Change

Backend no longer sends fixed two-decimal strings to Shark `topay` / `getPayType`.

- Before: `amount.StringFixed(2)` produced `10.00`.
- After: `amount.Round(2).String()` produces `10`, `100`, `10.5`, `10.01`.

The request sign continues to use exactly the money string sent in the request body.

## Validation

```bash
go test ./internal/infra/payment/shark ./internal/service/wallet
```

Passed.
