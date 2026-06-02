---
id: "doc-8cb642daa82f"
title: "Agent 工作日志 · payment-channel-disable-override"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "MySQL", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-payment-channel-disable-override.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-payment-channel-disable-override.md"
sourceSha256: "f0d0128d5f604e62f7f33434fb2ec725df7aeeeb6a5a78249e5d367c3b7ab5ef"
sourceSystem: "project-doc"
---

# Agent 工作日志 · payment-channel-disable-override

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-payment-channel-disable-override.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：修复支付通道停用与大白鲨实时能力混用冲突

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-914 / WALLET-007
- 接口/契约：`docs/api/openapi.yaml` 中 `adminPaymentChannels` / `adminPaymentChannelUpdate` / `walletChannels`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 修复后台停用支付通道时，三方 provider 实时返回又把通道补回来的问题。
2. 保持 `GET /api/v1/wallet/channels` 契约不变。
3. 明确支付通道状态只由后台运营配置决定，三方能力只用于启用/下单校验。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/payment_channels.go` | 移除列表读取时的大白鲨 provider 自动补齐；后台列表和前台公开通道只读取 `wallet.recharge.channels.enabled`。 |
| `services/go-app/internal/service/admin/payment_channels_public_test.go` | 移除 provider 自动补齐相关旧单测，保留公开通道过滤行为测试。 |

## 核心决策

1. 后台“启用/停用”是运营配置，读取支付通道状态时不得用大白鲨 `getPayType` 实时结果覆盖。
2. 后台“启用”仍保留当前 provider 校验，防止启用后前台马上创建不可用订单；下单前仍按金额查询 provider 可用 pay type。
3. `system_configs` upsert 使用 `ON DUPLICATE KEY UPDATE`，避免 MySQL 同值 UPDATE 返回 `RowsAffected=0` 后误判为不存在并插入重复 key。
4. 不改 OpenAPI 响应字段；这是服务端配置语义修正。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-914 / WALLET-007 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| 项目验收 | `docs/qa/project-acceptance.md` |
| OpenAPI / Event / DTO | 不改契约，仅修正服务端状态计算 |
| 不涉及契约的原因 | 请求/响应字段未变化 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 是否影响数据表 / migration / 索引 | 不新增表；只修正 `system_configs` 既有 key 的写入方式 |
| 是否影响账本、事务、幂等或审计 | 不涉及账本；后台更新仍写审计 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 不是，修正运营配置与第三方实时能力的合并边界 |
| 涉及能力 | 权限安全 / 第三方依赖边界 |
| 高风险触发项 | 资金 / 权限 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重新部署 go-app |
| 回滚 | 回滚本次代码后，可能恢复 provider 自动补齐导致停用状态被覆盖 |
| 密钥 | 不涉及 |
| 观测 | 沿用 trace_id 与 API fail 日志 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 停用不应依赖 provider；应可稳定关闭前台通道。 |
| 红队质疑 | 如果 provider 返回通道但运营未启用，后台和前台都不应显示为启用。 |
| 合入判断 | 可合入，需部署后用后台 PUT 与 `/wallet/channels` 复测。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/admin -run 'PaymentChannel|PaymentChannels|FilterPublicChannels|EnsureProvider' -count=1 -v` | 通过 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/adminapi ./services/go-app/internal/http/router ./services/go-app/internal/http/public ./services/go-app/internal/service/wallet` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `journalctl -u kickoff-admin` trace 复盘 | 线上 500 根因为 `duplicated key not allowed`，触发 SQL 为 `INSERT INTO system_configs ... wallet.recharge.channels.enabled` |

## 风险与待办

1. 部署后必须用真实后台接口复测停用、列表、前台 `/wallet/channels` 三段结果。
2. 后台 UI 后续可增加“第三方当前支持 / 运营启用”两列，避免把二者混成一个状态。
