---
id: "doc-6c470602b5f4"
title: "Agent 工作日志 · live-ws-contract-fix"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Redis", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-live-ws-contract-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-live-ws-contract-fix.md"
sourceSha256: "7fc89fe565dac0aebbc448a13bc098c43dcf448d32de3941e203c9b520c47517"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-ws-contract-fix

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-live-ws-contract-fix.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：修复 Web 端反馈的直播间 WebSocket / 弹幕历史接口契约脱节

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-h5.md`
- 需求 ID：LIVE-003、LIVE-004、LIVE-005、LIVE-007
- 设计图：不涉及
- 接口/契约：`packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml` §16
- 团队可读文档：`docs/agents/logs/2026-05-26-web-live-ws-contract-mismatch.md`
- 项目验收：`docs/qa/project-acceptance.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. WebSocket envelope 对齐 `type/msg_id/ts/trace_id/data`。
2. 直播间 WS type 与 payload 对齐 `live.viewer.count.updated`、`live.danmaku.received`、`live.tip.combo`、`live.danmaku.deleted`。
3. 修复弹幕历史接口返回字段与缺月分表 500 问题。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/wsx/*` | WS envelope、type 常量、payload 字段与单测 |
| `services/go-app/internal/http/wsapi/handlers.go` | 进房观看人数推送改为 `viewer_count/peak_count` |
| `services/go-app/internal/http/public/live.go` | 弹幕历史支持 `since_ts` |
| `services/go-app/internal/repository/live/chat.go` | 缺月分表时历史读取降级为空列表 |
| `services/go-app/internal/service/live/service.go` | `LiveDanmaku` DTO 与弹幕/打赏 WS payload 对齐 |
| `services/go-app/internal/service/admin/room.go` | 删除弹幕、房间状态广播 type 对齐 |
| `packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml` | `LiveDanmaku` schema 改为 `msg_id/user/sent_at/sent_ts` |
| `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-h5.md` | 修正旧 `danmaku/ts_ms` PRD 描述，标注 rank_badge 为 P1 |

## 核心决策

1. 弹幕 WS 的 envelope `msg_id` 使用数据库弹幕 ID，保证后续 `live.danmaku.deleted` 能和前端列表对上。
2. `LiveDanmaku` 以 OpenAPI §16 和 Web 端反馈为准，去掉旧的 `id/user_id/created_at_ms` 响应形态。
3. 月分表未预建属于运营/部署状态不完整，但 C 端历史弹幕不应 500；读历史时降级为空列表。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | WS envelope 单测、缺分表读降级模式 |
| 哪些内容只属于当前项目 | Kickoff 直播间 type 码、弹幕 DTO |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用契约优先和单测防回退流程 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay | 不影响 |
| 是否增加了自动校验或 CI 门禁 | 新增 Go 单测 |
| 是否降低了 Agent 偷懒空间 | 是，WS envelope 与 LiveDanmaku 有单测约束 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-003、LIVE-004、LIVE-005、LIVE-007 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-h5.md` |
| OpenAPI / Event / DTO | `packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`、`services/go-app/internal/dto/live.go` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 项目级验收 | `docs/qa/project-acceptance.md` |
| 不涉及契约的原因 | 不适用，本次涉及契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不新增表；只处理既有月分表缺失读降级 |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不新增资金写操作；打赏原资金链路未改动 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，涉及实时协议契约 |
| 涉及能力 | 异步 / 可观测性 / 数据一致性 |
| 当前 MVP 边界 | 不实现 rank_badge、不实现跨月历史 JOIN、不新增 realtime 服务 |
| 高风险触发项 | 用户数据 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重启 `go-app` 后 WS 协议生效 |
| 回滚 | 回滚本次 commit；前端会重新遇到旧协议脱节 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | WS envelope 增加 `trace_id` |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 覆盖 W1/W2/W3：envelope、viewer count、弹幕历史和缺分表降级均有测试或校验 |
| 红队质疑 | `rank_badge` 仍未实现；match/wallet 全量 WS 类型码未在本轮逐项梳理 |
| 合入判断 | 本轮可合入，但日志文件需按项目负责人规则审核后提交 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并本地验证 |
| 完成裁决 | 待 Reviewer / Owner / QA |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run openapi:validate` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |
| `git diff --check` | 通过 |
| `npm run check` | 首次因缺 Agent log 失败；补本日志后需重跑 |

## 前端页面验收

不涉及修改 `apps/web/**`。本次只修后端、后台服务侧 WS 推送、OpenAPI 契约与 PRD 描述。

## 风险与待办

1. `rank_badge` 仍为 P1 扩展，尚未接 Redis 房间打赏排行。
2. 弹幕历史当前只查当前月分表；跨月历史仍按 MVP 边界不做 JOIN。
3. dev 发布后需用 Web 端同一房间重新抓 WS 帧和 curl 验证。

## 交接说明

下一位 Agent 或工程师需要知道：

1. Web 前端按 §16 严格消费，不要在前端写旧字段适配。
2. `LiveDanmaku` 已改为 `msg_id/user/content/color/sent_at/sent_ts`。
3. 提交前需让项目负责人确认本日志是否允许进入 commit。
