---
id: "doc-4c3b9d466d1d"
title: "Agent 工作日志 · payment-channel-provider-validation"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-channel-provider-validation.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-channel-provider-validation.md"
sourceSha256: "a4f0366335798b87b3bdb0b99728e336e4398a40e2e37de936c2f961631facb5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · payment-channel-provider-validation

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20payment-channel-provider-validation.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：后台启用支付通道前校验大白鲨可用性

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：ADM-914、WALLET-002
- 接口/契约：`PUT /api/v1/admin/payment-channels/{code}`、`GET /api/v1/wallet/recharge/pay-types`
- 其他：测试机 `getPayType` 返回 `wechat/digitalRmb`，后台启用 `alipay` 后 C 端会展示但实际下单失败

## 本次目标

1. 后台启用 C 端公开支付通道前，校验大白鲨当前是否返回该 pay_type。
2. 第三方不支持时拒绝启用，避免 C 端展示不可下单入口。
3. 保持本地开发和第三方未配置环境不被强制阻塞。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/payment_channels.go` | 新增可选 PayTypeChecker；启用公开通道前查询大白鲨 `getPayType` |
| `services/go-app/internal/service/admin/payment_channels_public_test.go` | 覆盖支持、拒绝、不注入校验器、非公开通道跳过校验 |
| `services/go-app/internal/http/router/admin.go` | admin 进程启用 Shark 配置时注入 Shark client，校验金额使用充值最小金额 |

## 核心决策

1. 校验只发生在 `enabled=true` 时；关闭通道、设置推荐、改费率不依赖第三方。
2. Shark 未配置或本地环境未注入 checker 时不阻塞配置，保持开发便利。
3. 第三方返回中不包含该 pay_type 时返回 `ErrParam`，HTTP 400，明确提示“请先联系支付方开通”。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-914、WALLET-002 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / Event / DTO | 未改请求/响应结构 |
| 不涉及契约的原因 | 仅收紧已有 PUT 接口的业务校验 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 后台写操作仍走原审计；不支持时不写配置、不写审计成功 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 权限安全 / 第三方依赖 / 生产发布 / 资金 |
| 高风险触发项 | 资金 / 订单 / 生产发布 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin ./internal/http/adminapi ./internal/http/router` | 通过 |

## 风险与待办

1. 部署后复测启用 `alipay`，应返回 400 且不写入 `/wallet/channels`。
2. 如果大白鲨后续开通支付宝，再次启用应通过。
