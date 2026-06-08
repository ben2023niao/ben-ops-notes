---
id: "doc-99dbe0d53134"
title: "Agent 工作日志 · operator-tip-crowdfund-boundary"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-crowdfund-boundary.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-crowdfund-boundary.md"
sourceSha256: "14b4f9860979756b3a30ccdcd3526c79391db87bd8777cbc74c43fb868be833e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · operator-tip-crowdfund-boundary

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-crowdfund-boundary.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：运营账号礼物进入众筹进度，但继续排除奖励和主播结算

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`LIVE-007`、`LIVE-102`、`ADM-402`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/funds-and-ledger.md`、`docs/decisions/ADR-0017-operator-account-finance-boundary.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户确认“运营用户在 C 端显示正常，众筹加上去，奖励不用，结算区分清楚”

## 本次目标

1. 运营账号送礼继续按普通礼物做 C 端/主播端互动展示。
2. 运营账号送礼进入众筹解锁进度。
3. 运营账号送礼不进入奖励派发、真实 GMV、主播结算和消费档位。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/live/service.go` | 收口打赏后置动作；运营礼物进入众筹，奖励和结算仍排除 |
| `services/go-app/internal/service/live/service_test.go` | 增加运营礼物众筹/奖励/结算边界测试 |
| `services/go-app/internal/repository/live/stats.go` | 明确统计口径为互动打赏，含运营账号礼物 |
| `docs/api/openapi.yaml` | 更新运营礼物口径说明 |
| `packages/contracts/openapi/v1.yaml` | 同步契约说明 |
| `docs/architecture/funds-and-ledger.md` | 更新资金与结算边界 |
| `docs/prd/modules/kickoff-live.md` | 更新直播打赏结算口径 |
| `docs/prd/modules/kickoff-admin.md` | 更新运营账号管理口径 |
| `docs/decisions/ADR-0017-operator-account-finance-boundary.md` | 更新 ADR 结论 |

## 核心决策

1. 众筹属于直播间互动氛围口径，运营账号礼物应计入。
2. 奖励属于用户真实消费权益，运营账号礼物不得触发。
3. 主播结算使用 `settlement_*` 口径，运营礼物单列展示但结算金额为 0。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | `LIVE-007`、`LIVE-102`、`ADM-402` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 前端字段影响 | 无字段删除/改名；仅同步说明字段口径。C 端/主播端展示逻辑不需要因运营账号做特殊处理 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不改打赏主事务；运营礼物账本和审计沿用既有逻辑 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 统计 / 数据一致性 / 资金口径隔离 |
| 高风险触发项 | 扣费 / 收益 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅后端逻辑和文档变更，不改服务入口 |
| 回滚 | 回滚本次提交即可恢复运营礼物不进众筹的旧口径 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 运营礼物进入众筹进度，符合互动展示口径；奖励派发仍由 `!isOperatorTip` 和 `SumDiamondBySessionUser` 过滤保护 |
| 红队质疑 | `live_session_stats.tip_income_diamond` 现在是互动口径，不可用于主播结算；结算必须继续使用 `settlement_*` 字段 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/live ./services/go-app/internal/repository/live ./services/go-app/internal/service/reward ./services/go-app/internal/service/streamer` | 通过 |
| `go test ./services/go-app/...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

不涉及 `apps/web/**`、`apps/mobile/**`、`apps/admin/**` 文件修改。

## 风险与待办

1. 后续主播结算报表必须继续使用 `settlement_*` 字段，不能使用互动统计字段。
2. 如未来要隐藏 C 端响应中的 `is_operator_tip` 字段，需要单独做一次公开契约调整。

## 交接说明

1. 运营账号礼物：榜单和众筹进度计入，奖励和结算不计入。
2. 前端无需为了运营账号改展示逻辑。
3. 后台对账看 `settlement_tip_rmb`、`operator_tip_rmb`、`gross_tip_rmb` 三个口径。
