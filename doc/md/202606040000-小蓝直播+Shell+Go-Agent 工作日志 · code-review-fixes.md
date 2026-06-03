---
id: "doc-17f720c72519"
title: "Agent 工作日志 · code-review-fixes"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-code-review-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-code-review-fixes.md"
sourceSha256: "2e6b8e05eb7c76c353469d04f6f8912d395e6c996a966f5b58e771b730852074"
sourceSystem: "project-doc"
---

# Agent 工作日志 · code-review-fixes

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-code-review-fixes.md`

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：修复 code review 中发现的支付通道、用户号、赛事冲突与充值前端兜底问题

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`ADM-402`、`ADM-914`、`WALLET-002`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/data-model.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后端充值下单、试算、pay-types 接口统一按后台支付通道 enabled 配置做服务端强校验。
2. 后台支付通道页只保留当前真实开放的 4 个通道，移除 USDT 运营入口。
3. 用户列表搜索从 `MOD(id, 1000000)` 改为 `users.user_no` 精确索引搜索。
4. 赛事编号 duplicate key 转业务冲突，避免并发写入时返回 500。
5. H5 充值支付方式加载失败时 fail-closed，不再展示所有通道。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/paymentchannel/paymentchannel.go` | 新增支付通道公共定义、配置 key、JSON set 编解码 |
| `services/go-app/internal/service/admin/payment_channels.go` | 后台支付通道列表/更新改用公共定义，写入事务化，推荐必须先启用 |
| `services/go-app/internal/service/wallet/payment_channels.go` | wallet 侧读取后台 enabled 配置并转换为 Shark pay_type |
| `services/go-app/internal/service/wallet/service.go` | 充值下单与 pay-types 按后台 enabled 配置过滤 |
| `services/go-app/internal/service/wallet/recharge_quote.go` | 充值试算带 pay_type 时校验后台 enabled 配置 |
| `services/go-app/internal/model/user.go` | 新增 `user_no` 字段与 `UserNoFromID` |
| `services/go-app/migrations/000040_add_user_no_to_users.*.sql` | 新增 `users.user_no` 唯一索引与老数据回填 |
| `services/go-app/internal/service/admin/user.go` | 用户列表按 `user_no` 精确搜索，展示优先读落库字段 |
| `services/go-app/internal/service/admin/match.go` | 赛事写入 duplicate key 转 `ErrConflict`，去掉更新路径裸断言 |
| `apps/web/app/composables/useRechargePayment.ts` | pay-types 未成功返回时不展示可选通道 |
| `docs/api/openapi.yaml` / `packages/contracts/openapi/v1.yaml` | 同步支付通道枚举和公开通道 schema |
| `docs/architecture/data-model.md` / `docs/prd/modules/kickoff-admin.md` | 同步 `user_no` 索引和 4 通道运营口径 |

## 核心决策

1. 支付通道后台开关必须服务端强约束，不能只作为前端展示配置。
2. 后台支付通道列表只展示当前能让 C 端真实使用的通道；USDT 后续上线再单独补。
3. 用户号使用 `USR + base36(id)`，避免后 6 位短号撞号，同时保持确定性和可回填。
4. 赛事编号友好预检保留，但最终以数据库唯一索引兜底。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | `ADM-402`、`ADM-914`、`WALLET-002` |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 已更新 `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、DTO 注释 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 `users.user_no` 与 `uk_user_no` |
| 是否影响账本、事务、幂等或审计 | 影响支付通道配置写入，已改为 DB transaction；资金下单新增服务端通道校验 |
| 规范例外与原因 | 无 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/pkg/paymentchannel ./internal/service/admin ./internal/service/wallet ./internal/service/auth` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm run openapi:validate` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run check:prd` | 通过 |
| `npm run check:engineering-standards` | 通过 |
| `npm run check:capability-gates` | 通过 |
| `npm run check:completion-claim` | 通过 |
| `git diff --check` | 通过 |

## 风险与待办

1. `users.user_no` 新迁移上线后需跑 migration；老数据会按 `USR + base36(id)` 回填。
2. `AGENTS.md` 在本次任务开始前已有未提交 memory context 差异，本次未纳入业务变更。
3. USDT 后续上线时需要重新打开 PRD、OpenAPI、后台通道、wallet 校验和资金对账链路。

## 交接说明

1. 前端充值页应以 `/wallet/channels` 和 `/wallet/recharge/pay-types` 的交集为准；任一接口失败都不能展示兜底通道。
2. 后台支付通道页只接受 `alipay`、`wechat`、`union`、`digitalrmb`。
3. 直接调用 `/wallet/recharge/init` 传已关闭 pay_type 会返回业务错误“当前支付方式已关闭，请刷新后重新选择”。
