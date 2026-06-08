---
id: "doc-61d359918708"
title: "Agent 工作日志 · live-session-viewer-reset"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Redis", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-live-session-viewer-reset.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-live-session-viewer-reset.md"
sourceSha256: "97e11da59d649a531e3c249eda0691d68f708d1c11e4884fed495c4dd3272ef9"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-session-viewer-reset

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-live-session-viewer-reset.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：修复主播当前场次在线人数继承房间历史残留

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-102
- 接口/契约：`GET /api/v1/streamer/me/sessions/current/stats`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户提供 streamer current stats curl，反馈刚开播即显示 13 人在线，要求单个房间每次开播分开统计。

## 本次目标

1. 梳理 current stats 在线人数数据链路。
2. 修复新直播场次继承 `live:viewers:{room_id}` 残留的问题。
3. 用回归测试固定开播时清理房间在线集合的行为。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/wsx/hub.go` | 新增 `ClearRoomViewers`，清理 room 维度在线 Redis ZSET。 |
| `services/go-app/internal/service/live/service.go` | 同步在线人数时按当前 session `start_at` 过滤 Redis viewer ZSET，避免旧场次残留写入新 session。 |
| `services/go-app/internal/service/streamer/live.go` | 主播新开播和主动下播时清理 Redis 在线集合，并重置房间当前在线快照。 |
| `services/go-app/internal/http/router/public.go` | 将 WS hub 作为 room viewer tracker 注入主播直播服务。 |
| `services/go-app/internal/service/admin/room.go` | 后台强制开播时重置 `viewer_count` 并清理 Redis 在线集合。 |
| `services/go-app/internal/service/streamer/live_test.go` | 增加 Redis 残留 viewer 集合的回归测试。 |
| `services/go-app/internal/service/live/service_test.go` | 增加在线同步只统计当前 session viewer 的回归测试。 |

## 核心决策

1. `live_session_stats` 仍按 `session_id` 保存本场统计，不改变表结构。
2. WS 在线集合当前仍是 room 维度 `live:viewers:{room_id}`，因此在新场次边界主动清理，并在同步时按 session `start_at` 过滤，避免旧连接残留写回新 session。
3. 不改公开 API 字段，前端无需调整；当前修复是后端运行态缓存生命周期问题。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-102 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不变；接口仍返回 `current_online` / `cumulative_views` 等原字段。 |
| 不涉及契约的原因 | 只修 Redis 在线集合清理和房间快照重置，不新增/删除/改名字段。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；后台强制开播原审计保留。 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 统计 / 缓存 / 实时在线 |
| 当前 MVP 边界 | 保持 room 维度 WS 在线集合，开播/下播边界清理；暂不重构为 session 维度 WS key。 |
| 未来迁移成本 | 若需要跨 session 保留观众重入语义，可将 WS track 迁移到 `live:viewers:{session_id}` 并让 wsapi 查询 active session 后登记。 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重启 api/ws 服务加载新代码。 |
| 回滚 | 回滚本次代码即可；无 migration。 |
| 密钥 | 不涉及 |
| 观测 | 新增 Redis 清理失败 warn 日志：`clear room viewers failed`。 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 当前接口读取 `live_session_stats.current_online`，问题来源于 WS Redis room viewer set 残留在新场次被同步回 stats。 |
| 红队质疑 | 只在开播清理是否足够？本次同时在主播主动下播和后台强制开播清理，并在同步写 stats 前按当前 session 开始时间过滤 Redis ZSET。 |
| 合入判断 | 可以合入；无 API/DB 兼容风险。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/validate-runtime-environment.py` | passed |
| `python3 scripts/validate-prd.py` | passed |
| `python3 scripts/validate-engineering-standards.py` | passed |
| `python3 scripts/validate-capability-gates.py` | passed |
| `python3 scripts/validate-completion-claims.py` | passed |
| `go test ./internal/service/streamer -run TestLiveService_StartLiveClearsStaleRoomViewers -count=1` | passed |
| `go test ./internal/service/live -run 'TestSyncRoomViewerStats' -count=1` | passed |
| `go test ./internal/pkg/wsx ./internal/service/streamer ./internal/service/live` | passed |
| `go test ./internal/service/admin` | passed |
| `go test ./...` | passed |

## 风险与待办

1. dev 环境部署后需要用真实房间复测：下播后重新开播，`current_online` 应从 0 开始。
2. 当前没有改为 session 维度 WS key；如后续要严格区分“房间订阅”和“本场观看”，需要改 wsapi 登记链路。
3. 如果 Zego webhook/worker 异常终止直播，当前新开播仍会清理残留；但后台结束后在线列表即时清空可另行增强。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 数据链路：C 端 WS 订阅 room → `live:viewers:{room_id}` → `SyncRoomViewerStats` → `live_session_stats.current_online` → 主播 current stats。
2. 本次只处理缓存生命周期，不修改 `GET /api/v1/streamer/me/sessions/current/stats` 返回字段。
3. 部署后如果仍出现刚开播在线人数非 0，优先检查是否复用了旧 active session，而不是新建 session。
