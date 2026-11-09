---
id: "doc-dce1e65093de"
title: "Agent 工作日志 · payment-config-smoke"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-config-smoke.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-config-smoke.md"
sourceSha256: "fd9d1c721c222224840abbd564f59c1b30149c734c5cd5bcd7f6f40c424f36d9"
sourceSystem: "project-doc"
---

# Agent 工作日志 · payment-config-smoke

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20payment-config-smoke.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：检查 dev 支付配置并做充值 smoke test。

## 检查结论

dev 当前支付未就绪：

1. `GET /api/v1/wallet/channels` 返回 `channels: []`，后台支付通道开关全部关闭。
2. `GET /api/v1/wallet/recharge/pay-types?amount=10` 返回 `types: []`。
3. C 端真实发起 `POST /api/v1/wallet/recharge/init`，`pay_type=alipay/wechat/union/digitalRmb` 均返回 `10007 支付通道未启用，请稍后再试`。

这说明 Go 服务当前未注入 Shark client。通常原因是 dev 服务器 `/opt/kickoff/.env` 里大白鲨配置未开启或缺项。

## 缺少配置

dev 服务器 `/opt/kickoff/.env` 至少需要：

```bash
APP_PAY_SHARK_ENABLED=true
APP_PAY_SHARK_MERC_ID=<商户号>
[敏感内容已脱敏]
APP_PAY_SHARK_GATEWAY=<大白鲨网关>
APP_PAY_SHARK_NOTIFY_URL=https://api-dev.54-151-131-132.sslip.io/api/v1/hooks/payment/shark
APP_PAY_SHARK_CANCEL_NOTIFY_URL=https://api-dev.54-151-131-132.sslip.io/api/v1/hooks/payment/shark/refund
APP_PAY_SHARK_HTTP_TIMEOUT=8s
```

生产还必须在 yaml 中配置 `pay.shark.allowed_caller_ips`。

## 发现并修复

公开支付通道接口之前会返回数字人民币 code=`digitalrmb`，但充值下单 DTO 要求大白鲨 pay_type=`digitalRmb`。这会导致前端按 `/wallet/channels` 返回值传参时被后端 400 拦截。

已修复为：

- 后台配置仍使用 `digitalrmb`。
- C 端公开接口返回 `digitalRmb`，可直接作为 `POST /wallet/recharge/init.pay_type`。

## 验证

| 命令 | 结果 |
| --- | --- |
| `go test ./internal/service/admin ./...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| mandatory validators | 通过 |
