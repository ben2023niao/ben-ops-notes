---
id: "doc-d52c82db6a97"
title: "Agent 工作日志 · bug-27597-schedule-days-window"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-bug-27597-schedule-days-window.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-bug-27597-schedule-days-window.md"
sourceSha256: "0b2c3388160ff0d80e40395af905d6ac84d6e665c897098a4332111f6b22c6f7"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-27597-schedule-days-window

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-bug-27597-schedule-days-window.md`

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：修复 ZenTao Bug 27597 - 赛程日期视图接口赛事数据不齐全

## 输入资料

- PRD：`docs/prd/modules/kickoff-schedule.md`
- 需求 ID：SCHED-001
- Bug：ZenTao #27597
- 接口/契约：`GET /api/v1/schedule/days`
- AI/工具控制文件：`AGENTS.md`、`aixn-zaodao-bug-fixer`

## 本次目标

1. 修复 `GET /api/v1/schedule/days` 无参调用只返回当前日期附近赛事的问题。
2. 保留 `from/to` 显式日期过滤能力。
3. 同步 OpenAPI、contract 和 PRD 默认返回口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/public/schedule.go` | 将无参默认查询窗口从“今天起 7 天”改为 2026 全年赛事窗口。 |
| `services/go-app/internal/http/public/schedule_test.go` | 增加默认窗口和显式过滤单测。 |
| `docs/api/openapi.yaml` | 补充 `scheduleDays` 默认返回说明。 |
| `packages/contracts/openapi/v1.yaml` | 同步契约说明。 |
| `docs/prd/modules/kickoff-schedule.md` | 补充 SCHED-001 默认返回 2026 全年后台赛事。 |

## 核心决策

1. 不引入新分页参数，避免扩大接口契约变更；当前 H5 需要完整日期视图。
2. 无参默认覆盖 2026-01-01 至 2026-12-31，解决已配置历史/未来赛事缺失。
3. 传入 `from/to` 时仍按调用方指定范围过滤，兼容已有调用。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | SCHED-001 |
| 模块 PRD | `docs/prd/modules/kickoff-schedule.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 不涉及契约字段变更的原因 | 仅调整无参默认查询窗口和文档说明，响应结构不变 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 不涉及 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，公开赛程聚合接口默认窗口修复 |
| 涉及能力 | 不适用 |
| 高风险触发项 | 不涉及 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 go-app 服务二进制 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/http/public ./internal/service/schedule ./internal/repository/match` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应页面 | H5 赛程页 |
| 页面截图 | 未截图；本次为后端接口默认窗口修复 |
| API 接口路径 | `GET /api/v1/schedule/days` |
| 合入判断 | 可合入 |

## 风险与待办

1. 若后续赛事不只覆盖 2026 年，需要产品补充赛事赛季/赛事 ID 过滤规则。
2. 若赛事数量扩大到多赛季，应新增分页或赛季参数，而不是继续扩大默认窗口。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `schedule/days` 无参现在返回 2026 全年后台配置赛事。
2. `from/to` 过滤行为保留，`to` 仍按包含整天处理。
3. 本次未改响应结构，H5 不需要改调用参数。
