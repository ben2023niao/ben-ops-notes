---
id: "doc-8cb47bed6e80"
title: "shark-payment-recharge"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shark-payment-recharge.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shark-payment-recharge.md"
sourceSha256: "d6d6482fac5dd6ad16fb04511934469bb8ae2006bc45852781be8a2b19f165e2"
sourceSystem: "project-doc"
---

# shark-payment-recharge

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shark-payment-recharge.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：按 `nsy_o.pdf` 大白鲨支付接口文档 v1.1.0 完善充值接入

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-001、WALLET-002、WALLET-005、WALLET-006、WALLET-007、WALLET-302、ADM-502、ADM-507
- 接口/契约：`packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`
- 其他：本地支付通道对接资料 PDF

## 本次目标

1. 对齐大白鲨 v1.1.0 支付方式查询、下单、回调、订单查询字段。
2. 完善充值订单子通道 `pay_type` 落库和后台展示。
3. 给财务后台补支付回调流水查看入口，便于处理失败回调和金额不一致。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/payment/shark/*` | 新增 `getPayType` 请求/响应类型、客户端方法和测试 |
| `services/go-app/internal/service/wallet/service.go` | 充值订单保存 `pay_type`，新增可用支付方式查询 |
| `services/go-app/internal/http/public/wallet.go` | 新增 `GET /api/v1/wallet/recharge/pay-types` |
| `services/go-app/migrations/000017_recharge_pay_type.*.sql` | 为 `recharge_orders` 增加 `pay_type` 和索引 |
| `services/go-app/internal/service/admin/order.go` | 新增支付回调流水列表 |
| `apps/admin/src/views/orders/PaymentCallbackListView.vue` | 新增后台支付回调页面 |
| `packages/contracts/openapi/v1.yaml` / `docs/api/openapi.yaml` | 对齐充值字段、支付方式查询和回调流水契约 |
| `docs/architecture/data-model.md` | 更新充值订单索引说明 |

## 核心决策

1. `pay_type` 独立存储，不再只依赖第三方 payload，保证后台和用户记录可直接展示子通道。
2. 支付方式查询直接走大白鲨 `getPayType`，同时用本地 `enabled_types` 白名单过滤返回值。
3. 回调失败不在业务接口吞没，落 `payment_callbacks.processed=2` 后由后台财务页面筛选处理。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 `000017_recharge_pay_type` |
| 是否影响账本、事务、幂等或审计 | 入账事务不变；新增回调可视化 |
| 数据表设计 | 新增字段走新 migration，未改已发布 migration |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/infra/payment/shark ./internal/service/wallet ./internal/service/admin ./internal/http/public ./internal/http/adminapi` | 通过 |
| `go test ./...` | 通过 |
| `pnpm --filter @kickoff/admin build` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm run check` | 通过 |

## 风险与待办

1. 生产需要执行 `000017_recharge_pay_type` migration 后再部署新服务。
2. 大白鲨真实网关联调仍需用正式商户号、密钥、回调白名单做 staging 验证。
3. 首充 14 天提现冷却和自动扫超时订单调度仍属于后续充值/提现闭环增强项。
