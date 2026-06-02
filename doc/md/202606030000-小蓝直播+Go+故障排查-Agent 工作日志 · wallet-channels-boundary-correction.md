---
id: "doc-0ec16f8158e6"
title: "Agent 工作日志 · wallet-channels-boundary-correction"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-boundary-correction.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-boundary-correction.md"
sourceSha256: "78f0a0b7613d95252e354e6fe30963e28259034d73f4f44b67287e0050943af1"
sourceSystem: "project-doc"
---

# Agent 工作日志 · wallet-channels-boundary-correction

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-wallet-channels-boundary-correction.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：纠正充值支付通道接口职责边界

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-002 / WALLET-007
- 接口/契约：`GET /api/v1/wallet/channels`，`GET /api/v1/wallet/recharge/pay-types`
- 项目验收：`docs/qa/project-acceptance.md`

## 本次目标

1. 恢复 `/api/v1/wallet/channels` 只表达后台支付通道配置。
2. 保留 `/api/v1/wallet/recharge/pay-types` 作为大白鲨 getPayType 实时能力查询接口。
3. 移除 `walletChannels` 中错误加入的金额 query 参数，避免前端误用。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/public/config.go` | 恢复 `/wallet/channels` 只调用 `PublicView` |
| `services/go-app/internal/http/router/public.go` | 移除 public payment channel service 的大白鲨实时 checker 注入 |
| `services/go-app/internal/service/admin/payment_channels.go` | 移除按金额过滤 public channel 的逻辑 |
| `services/go-app/internal/service/admin/payment_channels_public_test.go` | 移除错误职责边界下的交集测试 |
| `docs/api/openapi.yaml` | 移除 `walletChannels` 的 `rmb_amount` / `amount` 参数 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI |

## 核心决策

1. `/wallet/channels`：后台运营配置视角，只返回后台启用且 public 白名单允许的支付通道。
2. `/wallet/recharge/pay-types`：大白鲨实时能力视角，按金额返回三方当前支持的支付方式。
3. 前端最终展示支付方式时，应取两者交集；下单接口仍会再次校验大白鲨实时可用性。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/router ./services/go-app/internal/http/public ./services/go-app/internal/service/wallet` | 通过 |

## 风险与待办

1. 前端不能只看 `/wallet/recharge/pay-types`，否则会绕过后台开关。
2. 前端也不能只看 `/wallet/channels`，否则可能展示大白鲨当前金额不可用的通道。
3. 更稳妥的后续方案是新增一个明确命名的聚合接口，例如 `/api/v1/wallet/recharge/available-channels?amount=50.00`，由后端返回最终交集，避免前端重复实现合并规则。
