---
id: "doc-10ec971e2cf3"
title: "Agent 工作日志 · bug-27674-live-viewer-stats"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "MySQL", "Redis", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-27674-live-viewer-stats.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-27674-live-viewer-stats.md"
sourceSha256: "59eef4cae9963289416bdd27d031d15bb2fe07539549f237074944efa4bf376e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-27674-live-viewer-stats

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-27674-live-viewer-stats.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复 ZenTao Bug 27674 - 主播端累计观看和在线观众一直为 0

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-102
- Bug：ZenTao #27674
- 接口/契约：`GET /api/v1/streamer/me/sessions/current/stats`
- AI/工具控制文件：`AGENTS.md`、`aixn-zaodao-bug-fixer`

## 本次目标

1. C 端观众进入直播间后，主播端工作台能看到本场累计观看和在线观众。
2. 同步检查弹幕数、打赏收入、投票收入、下播清零等同链路统计。
3. 保持主播端前端不改，仅修复后端统计写入。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/wsapi/handlers.go` | WS 订阅/退订/断开时同步房间在线人数快照。 |
| `services/go-app/internal/pkg/wsx/hub.go` | 增加房间在线人数读取，优先取 Redis 在线集合，降级本机 channel。 |
| `services/go-app/internal/repository/live/live.go` | 增加 `SetViewerCount`，同步 `live_rooms.viewer_count / peak_viewer_count`。 |
| `services/go-app/internal/service/live/service.go` | 进房累加 `cumulative_views`，登录用户按 session+user 去重累加 `unique_visitors`，同步 `current_online`。 |
| `services/go-app/internal/service/streamer/live.go` | 开播/主动下播重置房间在线快照。 |
| `services/go-app/internal/service/streamer/webhook.go` | Zego 断流下播重置房间在线快照。 |
| `services/go-app/internal/service/hook/srs.go` | SRS publish/unpublish 重置房间在线快照。 |
| `services/go-app/internal/service/live/service_test.go` | 增加进房统计、UV 去重、在线快照同步单测。 |
| `docs/prd/modules/kickoff-live.md` | 补充观看人数统计口径。 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 修正主播工作台 stats 描述。 |

## 核心决策

1. Redis 负责在线集合和 session+user 去重标记，MySQL `live_session_stats` 负责沉淀历史统计。
2. `cumulative_views` 按进房人次累计，重复刷新/重连会累加。
3. `unique_visitors` 仅登录用户按 session+user 去重；游客没有稳定身份，不计入 UV。
4. `current_online` 和 `live_rooms.viewer_count` 是实时快照，下播清零；累计观看和峰值保留。

## 其他统计检查

| 字段 | 结论 |
| --- | --- |
| `danmaku_count` | 已在发送弹幕链路调用 `IncDanmakuCount`。 |
| `tip_income_diamond / total_income_diamond` | 已在打赏链路调用 `IncTipIncome`。 |
| `vote_income_diamond` | 投票当前免费，字段保留但不展示；文档已修正。 |
| `current_online` | 本次补齐 WS 订阅/断开同步。 |
| `live_rooms.viewer_count / peak_viewer_count` | 本次补齐同步和开播/下播重置。 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-102 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 不涉及响应结构变更的原因 | 仅修复统计写入链路和文档描述，字段不变 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 不涉及 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，实时 WS 统计 + 持久化统计链路 |
| 涉及能力 | 数据一致性 / 可观测统计 |
| 高风险触发项 | 不涉及资金写操作 |
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
| `go test ./internal/...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |

## 风险与待办

1. 游客无稳定身份，本次不计入 Redis 在线去重集合和 UV；如产品要求游客也计数，需要设计 guest session ID。
2. 多实例在线人数依赖 Redis 在线集合，Redis 故障时降级为本机 channel 数，仅作为临时兜底。
3. Zandao 当前账号 Web 登录被重定向到改密码页，暂不能回写修复备注和 resolve。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 主播端 stats 接口仍读 `live_session_stats`，本次补齐写入链路。
2. `live_rooms.viewer_count` 是房间展示/排序快照，不是历史统计。
3. Zandao #27674 代码已修复后，需要在账号恢复后补写问题原因、解决方案和验证结果。
