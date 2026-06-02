---
id: "doc-68cfeb0a5ce0"
title: "Agent 工作日志 · shark-query-order-numeric-amount"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-query-order-numeric-amount.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-query-order-numeric-amount.md"
sourceSha256: "d76a8ed85f0f4243256a9121c390aca2db2cda8445fb6d5e0061be8486ce03c5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · shark-query-order-numeric-amount

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-shark-query-order-numeric-amount.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：排查大白鲨充值未完成并修复 queryOrder 数字金额解析

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-004 / WALLET-006 / WALLET-007
- 接口契约：`packages/contracts/openapi/v1.yaml`
- 运行环境：dev `https://api-dev.54-151-131-132.sslip.io`
- 用户现象：大白鲨微信支付页显示“未匹配到10金额，请检查稍后再试”

## 排查结论

1. 截图 URL 内部 id `XY20260603184759513293` 不是我方 `recharge_orders.third_party_no`。
2. 18:47 左右对应我方订单为 `R22291681143422977`，金额 `10.00`，通道 `shark/wechat`，第三方号 `WNSY0603184757u7str`，状态仍为待支付。
3. 大白鲨 `queryOrder` 返回 `payStatus=未知`、`notifyStatus=未回调`、`payMoney=0`，说明三方侧也未确认支付成功。
4. dev 日志发现补单 worker 每分钟报错：`json: cannot unmarshal number into Go struct field QueryOrderMsg.msg.money of type string`。
5. 根因之一是大白鲨 `queryOrder` 当前返回 `money/payMoney` 为 JSON number，而我方 SDK 只按 string 解码。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/payment/shark/types.go` | `QueryOrderMsg` 增加自定义 JSON 解码，兼容 number/string 金额 |
| `services/go-app/internal/infra/payment/shark/client_test.go` | 新增数字金额返回格式单测 |

## 资金与审计

| 项目 | 内容 |
| --- | --- |
| 是否改入账逻辑 | 否 |
| 是否改账本 | 否 |
| 是否改回调验签 | 否 |
| 风险边界 | 只修补单查询解析；真正入账仍必须走 `SettleRechargePaid`、订单状态、金额校验与账本事务 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| dev DB 查询 `recharge_orders` / `payment_callbacks` | 截图订单未支付，无成功回调 |
| 大白鲨 `queryOrder` 查询 | `payStatus=未知`、`notifyStatus=未回调`、`payMoney=0` |
| `GET /api/v1/wallet/recharge/pay-types?amount=10` | 当前返回 `digitalRmb`、`wechat` 可用 |
| `go test ./internal/infra/payment/shark ./internal/service/wallet` | 通过 |

## 后续建议

1. 继续用 `10.00` 或 `100.00` 真实支付验证。如果支付页仍报“未匹配金额”，需要把我方订单号、第三方号和支付页内部 `XY...` 发给大白鲨排查下游收银台。
2. 前端应在 `pay-types` 返回空时禁止下单；当前已有查询能力，需联调确认异常时按钮是否禁用。
3. 后台充值订单页可补充 pay URL / 第三方 payload 只读详情，方便运营排查。
