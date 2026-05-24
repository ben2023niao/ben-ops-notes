---
id: "doc-5e33d6623d84"
title: "Agent 工作日志 · admin-public-flow-fixes"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "MySQL", "自动化", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-public-flow-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-public-flow-fixes.md"
sourceSha256: "473f3af757d61dce216dfb40bd34a44ff0803f9bc1c8c0783fb1e791c6334131"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-public-flow-fixes

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-public-flow-fixes.md`

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：Codex
任务：修复后台管理与前台 API 流程对齐问题

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-predict.md`、`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：ADM-211~214、ADM-901~918、LIVE-008、PRED-001~002、PRED-007~009、WALLET-009
- 接口/契约：`docs/api/openapi.yaml`
- 团队可读文档：`AGENTS.md`
- 其他：`docs/agents/logs/2026-05-25-admin-public-flow-review.md`

## 本次目标

1. 让竞猜下单字段兼容 PRD/OpenAPI 的 `option_key` / `amount_diamond`。
2. 修复竞猜下单扣款与写单不在同一事务的问题。
3. 补齐后台创建/结算竞猜活动对 `open_at`、`option_key`、`result_option_key` 的支持。
4. 让直播间浮动竞猜活动只返回 OPEN 活动。
5. 收紧后台直播间管理权限到 super_admin / 已分配 room_admin。
6. 补 `/api/v1/wallet/*-records` 公开路由别名以对齐 OpenAPI。
7. 押注 / 打赏资金写接口切到 JWT fail-closed 校验。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000015_predict_option_key.*.sql` | 新增 `predict_options.option_key` 与 `predict_bets.option_key` |
| `services/go-app/internal/model/predict.go` | 模型补 option_key 字段 |
| `services/go-app/internal/dto/*.go` | DTO 兼容 OpenAPI 字段 |
| `services/go-app/internal/repository/predict/predict.go` | 选项支持按 option_key 查找 |
| `services/go-app/internal/service/predict/service.go` | 押注改为单事务，补限额与 option_key |
| `services/go-app/internal/service/admin/predict.go` | 后台创建/结算兼容契约字段 |
| `services/go-app/internal/repository/user/user.go` | 注册用户时同事务初始化 wallet，避免后台调账/下注链路断裂 |
| `services/go-app/internal/service/live/service.go` | 房间活动只返回 OPEN |
| `services/go-app/internal/service/live/service_test.go` | 增加直播间活动筛选回归测试 |
| `services/go-app/internal/http/middleware/idempotency.go` | 资金写接口优先使用 OpenAPI 标准 `Idempotency-Key`，兼容旧 `X-Idempotency-Key` |
| `services/go-app/internal/http/middleware/cors.go` | CORS 放行标准幂等头 |
| `services/go-app/internal/http/middleware/rbac.go` | 新增房间分配范围校验 |
| `services/go-app/internal/http/router/admin.go` | 房间管理路由收紧权限 |
| `services/go-app/internal/http/router/public.go` | 增加 wallet 记录路由别名 |
| `docs/api/openapi.yaml` | 对齐后台创建、结算、退款的真实响应 schema |

## 核心决策

1. 不修改已发布 migration，新增 000015 做兼容迁移。
2. 后台 API 兼容旧 UI 字段和 OpenAPI 字段，避免打断现有页面。
3. 风控/对账/内容审核 P0 placeholder 本次不伪实现，保留为显式关闭状态。
4. 真实闭环测试发现 MySQL 会把 `[]uint8` 的 `IN ?` 参数当 binary，状态列表统一改用普通整数切片。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 predict option_key 字段和唯一索引 |
| 是否影响账本、事务、幂等或审计 | 是，押注改为 `ledger.PostTx` 与 bet 写入同事务 |
| 是否影响权限 | 是，直播间详情/敏感操作按分配关系限制 |
| 是否影响 OpenAPI | 是，更新后台竞猜创建/结算/退款响应契约 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/...` | 通过 |
| 本地 curl 闭环：后台登录 → 用户注册 → 后台调账 → 后台建盘/开盘 → 前台列表 → 前台下注 → 后台封盘/结算 → 前台注单 → 钱包记录 | 通过，全部 `code=0` |
| `npm run openapi:validate` | 通过 |
| `pnpm --filter @kickoff/admin build` | 通过，有 Vite chunk size warning |
| `python3 scripts/validate-openapi.py` | 通过 |
| `python3 scripts/validate-contract-testing.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-agent-log-boundaries.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `git diff --check` | 通过 |

### 闭环输出摘要

```text
admin_login=0
register=0
adjust=0
create=0
open=0
public_list_found=1
bet=0
close=0
settle=0
settle_data={"activity_id":"21003061786836993","batch_no":"v_21003061786836993","won_count":1,"lost_count":0,"total_payout":900,"settled_bets":1}
my_bets=0
my_bets_count=1
wallet_recharge_records=0
wallet_withdraw_records=0
```

## 风险与待办

1. 风控、对账、内容审核仍是 placeholder，与 PRD P0/v1 必上存在差距。
2. 押注累计消费升级尚未完全落到 `user_consume_total` 形式，需结合现有用户等级模型继续补。
3. 竞猜自动状态流转仍需要 worker/cron 扫描 `open_at` / `close_at`。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 前端可逐步切到 `option_key` / `amount_diamond`，旧 `option_id` / `bet_amount` 仍兼容。
2. 后台创建活动可传 OpenAPI 风格 `name` / `market_type` / `open_at` / `close_at` / `rate`。
3. room_admin 访问 `/admin/rooms/:id/**` 前必须存在 `live_room_admins` 未撤销分配。
