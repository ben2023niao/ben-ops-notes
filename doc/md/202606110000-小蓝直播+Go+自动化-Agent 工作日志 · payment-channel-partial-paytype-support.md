---
id: "doc-dfd1bcc72889"
title: "Agent 工作日志 · payment-channel-partial-paytype-support"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-payment-channel-partial-paytype-support.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-payment-channel-partial-paytype-support.md"
sourceSha256: "975fdb899c1709d9b30b4c668cad5ddbbe32597eab11a3062a865f9dcb0183de"
sourceSystem: "project-doc"
---

# Agent 工作日志 · payment-channel-partial-paytype-support

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20payment-channel-partial-paytype-support.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：后台启用支付通道放宽大白鲨金额校验

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：ADM-914、WALLET-002
- 接口/契约：`PUT /api/v1/admin/payment-channels/{code}`、`GET /api/v1/wallet/recharge/pay-types`
- 团队可读文档：`docs/qa/project-acceptance.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：后台启用 `union` 时提示“大白鲨当前金额50不支持银联 / 某支付平台”

## 本次目标

1. 后台启用支付子通道时，不再要求所有探测金额都支持该 pay_type。
2. 大白鲨只要至少一个探测金额返回该 pay_type，就允许运营启用。
3. C 端具体金额是否可用仍由 `/wallet/recharge/pay-types` 实时按金额过滤。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/payment_channels.go` | 放宽 `ensureProviderSupportsChannel` 校验口径 |
| `services/go-app/internal/service/admin/payment_channels_public_test.go` | 更新测试，覆盖部分金额支持仍允许启用 |

## 核心决策

1. 不完全移除第三方支持校验：完全不支持该 pay_type 时仍拒绝启用，避免运营误开无效通道。
2. 去掉“所有金额都必须支持”的强限制：不同金额可用支付方式由三方动态决定，不应阻塞全局通道开关。
3. 不改 C 端字段和 OpenAPI：现有 `pay-types` 已按金额过滤，前端继续以它为准展示可下单方式。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-914、WALLET-002 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / Event / DTO | 未改契约；只调整后台启用校验行为 |
| 是否影响前端字段 | 不涉及前端字段变更 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 不影响账本；后台成功启用仍走原审计 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，第三方支付能力校验口径调整 |
| 涉及能力 | 权限安全 / 第三方依赖 / 生产发布 |
| 高风险触发项 | 资金 / 订单 / 生产发布 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin` | 通过 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 解决后台启用 `union` 被 50 元探测金额误拦截的问题，同时保留完全不支持时拒绝启用 |
| 红队质疑 | 启用通道不代表所有金额都可下单；需要 C 端继续按金额查询 `/wallet/recharge/pay-types` |
| 合入判断 | 可以合入，部署后在后台重新启用银联验证 |

## 风险与待办

1. 启用 `union` 后，C 端仍必须按金额调用 `/wallet/recharge/pay-types`，例如 50 元可能仍不显示银联。
2. 如果某通道所有探测金额都不返回，后台仍会拒绝启用。
3. 部署后需在后台重新点启用 `union` 验证。
