---
id: "doc-04740459d69c"
title: "Agent 工作日志 · operator-tip-settlement-breakdown"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-settlement-breakdown.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-settlement-breakdown.md"
sourceSha256: "c2847bf984fc66976d49bf6eec71a8dec2d73d3c29e2a94a8018c6497953570f"
sourceSystem: "project-doc"
---

# Agent 工作日志 · operator-tip-settlement-breakdown

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-settlement-breakdown.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：运营账号送礼展示与主播结算口径拆分

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-live.md`
- 需求 ID：ADM-402、ADM-406、LIVE-007
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/funds-and-ledger.md`、`docs/architecture/data-model.md`、`docs/decisions/ADR-0017-operator-account-finance-boundary.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 运营账号在 C 端和主播端仍按普通礼物展示与广播。
2. 主播结算、GMV、榜单、众筹、奖励继续排除运营账号礼物。
3. 后台场次对账能单独看到结算打赏、运营礼物与礼物总额。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000051_add_tip_settlement_breakdown.*.sql` | 新增 `live_tips.settlement_*` 与 `live_sessions.operator_tip_*` |
| `services/go-app/internal/model/live.go` | 补齐打赏与场次结算字段模型 |
| `services/go-app/internal/service/live/service.go` | 打赏写入拆分展示价值与结算价值 |
| `services/go-app/internal/service/live/service_test.go` | 覆盖运营礼物结算值归零和账本 meta |
| `services/go-app/internal/service/admin/room.go` | 场次历史返回结算/运营/总额拆分 |
| `services/go-app/internal/service/admin/room_test.go` | 覆盖场次历史 SQL 与 DTO 字段 |
| `apps/admin/src/api/modules/room.ts` | 后台房间场次类型补充对账字段 |
| `apps/admin/src/views/rooms/detail.vue` | 房间详情会话历史展示结算打赏、运营礼物、礼物总额 |
| `apps/admin/src/locales/langs/*/room.json` | 后台表头文案 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 同步后台场次字段说明 |
| `docs/architecture/*`、`docs/prd/modules/*`、`docs/decisions/ADR-0017-operator-account-finance-boundary.md` | 修正运营账号礼物财务口径 |

## 核心决策

1. `live_tips.rmb_equiv` 保留礼物展示/审计价值，运营账号不再写 0。
2. `live_tips.settlement_rmb_equiv` 与 `settlement_diamond_amount` 才是主播结算口径；运营账号送礼写 0。
3. `live_sessions` 物化保存本场 `settlement_tip_rmb`、`operator_tip_rmb`、`operator_tip_diamond`，便于后台对账。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-402、ADM-406、LIVE-007 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 新增后台场次字段 `settlement_tip_rmb`、`operator_tip_rmb`、`operator_tip_diamond`、`gross_tip_rmb`；旧 `total_tip_rmb` 保留 |
| 前端字段影响 | 仅后台管理新增字段；C 端/主播端事件名和原字段不改，礼物仍正常展示 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 migration 000051，含 down.sql |
| 是否影响账本、事务、幂等或审计 | 是，账本 meta 增加展示价值与结算价值；复式记账仍在原事务内 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要先执行 migration 000051，再发布服务 |
| 回滚 | 执行 000051 down 后回滚代码 |
| 密钥 | 不涉及 |
| 备份恢复 | 涉及 `live_tips`、`live_sessions` 字段新增，发布前建议保留数据库备份 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | C 端/主播端互动链路不变；结算口径落字段而不是临时过滤 |
| 红队质疑 | 历史运营礼物若已按旧逻辑写入 `rmb_equiv=0`，无法从 DB 恢复原礼物 RMB，只能保证后续新数据准确 |
| 合入判断 | 待测试通过后允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/live ./internal/service/admin ./internal/repository/live` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `pnpm --filter @kickoff/admin run typecheck` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `git diff --check` | 通过 |
