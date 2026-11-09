---
id: "doc-88c2e6fdc6bd"
title: "Agent Log： Shark Init Pay Type Gate"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-init-paytype-gate.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-init-paytype-gate.md"
sourceSha256: "9ef1130cabb768b17a6c15684c446de293de26a49b485e1a142642793c6fb659"
sourceSystem: "project-doc"
---

# Agent Log： Shark Init Pay Type Gate

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20Log%EF%BC%9A%20Shark%20Init%20Pay%20Type%20Gate.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

- Date: 2026-06-03
- Scope: WALLET-007 / Shark recharge
- Author: Codex

## Background

大白鲨文档说明：通过 `getPayType` 获取支付方式后，`topay` 下单接口中的 `type` 必须使用返回值中的 `type`；如果对应金额无支付方式返回，则该金额不可下单。

## Change

`InitRecharge` 在创建本地充值订单和调用 `topay` 之前，新增后端强校验：

1. 先用规范化金额调用 Shark `getPayType`。
2. 确认当前 `rmb_amount` 对应返回列表中存在请求的 `pay_type`。
3. 若未返回或该 `type` 被后台禁用，拒绝创建支付订单，提示前端刷新支付方式后重选。

这避免只依赖前端曾经查询过的支付方式，减少动态通道变化时生成不可支付 `payUrl` 的概率。

## Validation

```bash
go test ./internal/infra/payment/shark ./internal/service/wallet
```

Passed.
