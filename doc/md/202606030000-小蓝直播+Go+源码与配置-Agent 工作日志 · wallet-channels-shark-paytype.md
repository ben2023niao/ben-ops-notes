---
id: "doc-4d73ee1b9c39"
title: "Agent 工作日志 · wallet-channels-shark-paytype"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-shark-paytype.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-shark-paytype.md"
sourceSha256: "6da279ada62c20afded5c0cc09cf76fab021c1fa4ee6bfc93ed079674b1cde0c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · wallet-channels-shark-paytype

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-shark-paytype.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：按大白鲨 getPayType 动态调整 C 端充值支付方式接口

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-002 / WALLET-007
- 接口/契约：`GET /api/v1/wallet/channels`，`GET /api/v1/wallet/recharge/pay-types`
- 其他：大白鲨 API 文档要求下单 `type` 必须使用 `getPayType` 返回值；对应金额无支付方式返回则该金额不可下单。

## 本次目标

1. 确认后台支付通道配置仅负责运营启用、手续费、推荐，不代表三方当前可下单。
2. 让 `/api/v1/wallet/channels` 支持按充值金额返回后台启用通道与大白鲨实时通道的交集。
3. 保持不传金额时旧行为不变，降低前端迁移风险。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/payment_channels.go` | 新增 `PublicViewForAmount`，按金额调用大白鲨 getPayType 并过滤通道 |
| `services/go-app/internal/service/admin/payment_channels_public_test.go` | 覆盖后台 enabled 与大白鲨返回通道取交集 |
| `services/go-app/internal/http/public/config.go` | `/wallet/channels` 读取 `rmb_amount` / `amount` |
| `services/go-app/internal/http/router/public.go` | public router 为支付通道 service 注入大白鲨 client |
| `docs/api/openapi.yaml` | 更新 `walletChannels` 契约 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI |

## 核心决策

1. 后台「支付通道」仍只表达运营开关、费率、推荐状态。
2. C 端展示支付方式时，若传入金额，则以“后台 enabled ∩ 大白鲨 getPayType 返回”为准。
3. `GET /api/v1/wallet/channels` 增加可选 `rmb_amount`，并兼容 `amount`；不带金额保持旧返回。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET-002 / WALLET-007 |
| 模块 PRD | `docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 项目验收 | `docs/qa/project-acceptance.md` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金入账逻辑；仅影响充值前支付方式展示 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方支付依赖、接口契约 |
| 高风险触发项 | 资金 / 订单 |
| 能力门禁结论 | 允许合入；下单前展示与下单校验均受大白鲨实时返回约束 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/admin -run 'TestFilterPublicChannelsByProviderRows'` | 先红后绿 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/router ./services/go-app/internal/http/public` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/router ./services/go-app/internal/http/public ./services/go-app/internal/service/wallet` | 通过 |

## 风险与待办

1. 大白鲨通道返回会实时变化，前端必须按用户输入金额重新请求 `/wallet/channels?rmb_amount=...`。
2. 后台启用某通道不代表所有金额都可用，只代表运营允许展示；最终展示以三方实时交集为准。
3. 支付成功仍依赖大白鲨匹配与回调，需继续观察充值订单回调状态。

## 交接说明

1. 前端充值页选中预设金额或输入自定义金额后，请调用 `GET /api/v1/wallet/channels?rmb_amount=<金额>`。
2. 返回 `channels` 中没有的支付方式不要展示，也不要用于 `/wallet/recharge/init`。
3. 不传金额时接口仍返回后台启用通道列表，仅适合首屏默认展示，不适合最终下单前确认。
