---
id: "doc-0e20391e863f"
title: "Agent 工作日志 · live-heartbeat-timeout"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-live-heartbeat-timeout.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-live-heartbeat-timeout.md"
sourceSha256: "c2bb7f1baca550fb2a34683dfb9a624d13ee43c93421973513d227ad33fd39d1"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-heartbeat-timeout

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-live-heartbeat-timeout.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：主播端业务心跳与直播间自动下播兜底

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：`LIVE-012`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 架构文档：`docs/architecture/live-streaming-architecture.md`、`docs/architecture/data-model.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：缺陷讨论口径为“主播端断开后,1 分钟内没有业务心跳则切换直播间为下播”

## 本次目标

1. 后端支持主播端通过 `/ws/v1/streamer` 上报直播业务心跳。
2. 后端在 60s 未收到业务心跳时自动结束直播间,避免 C 端继续拿到 `LIVE` 状态。
3. 同步 OpenAPI/契约/架构文档,给前端明确接入字段和频率。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/wsapi/handlers.go` | 新增 `streamer.live.heartbeat` WS 上行处理 |
| `services/go-app/internal/service/streamer/live.go` | 校验主播、房间、session、Zego room/stream 并记录心跳 |
| `services/go-app/internal/dto/streamer.go` | 开播响应新增 `session_id`,供主播端心跳原样回传 |
| `services/go-app/internal/repository/live/live.go` | 新增 `TouchHeartbeat` |
| `services/go-app/internal/worker/live_heartbeat.go` | 新增直播业务心跳超时扫描 worker |
| `services/go-app/internal/model/live.go` | `live_sessions` 增加 `last_heartbeat_at` 映射 |
| `services/go-app/migrations/000044_add_live_session_heartbeat.*.sql` | 新增心跳字段与索引 |
| `apps/live-host/app/composables/useLiveDanmaku.ts` | 主播端 WebSocket 增加 `streamer.live.heartbeat` 发送能力 |
| `apps/live-host/app/composables/useStreamerRooms.ts` | 开播响应类型补充 `session_id` |
| `apps/live-host/app/pages/studio/[room_id].vue` | 开播后每 15s 发送业务心跳,下播/异常/卸载时停止 |
| `docs/api/openapi.yaml` | 新增 WS 心跳协议说明和 payload schema |
| `docs/api/websocket.html` | 新增独立 WebSocket 文档页的主播业务心跳说明 |
| `docs/api/websocket-current.md` | 同步当前实现版 WebSocket 文档 |
| `docs/api/streamer-integration.html` | 同步主播端接入示例和心跳代码 |
| `docs/api/c-end-integration.html` | 说明 C 端无需新增心跳,沿用原有关播事件处理 |
| `docs/api/conventions.md` | 同步 §16 WebSocket 协议约定 |
| `packages/contracts/openapi/v1.yaml` | 同步前端契约说明和 payload schema |
| `docs/architecture/data-model.md` | 同步直播会话字段与索引说明 |
| `docs/architecture/live-streaming-architecture.md` | 同步 ZEGO/WebRTC 断流兜底策略 |

## 核心决策

1. `client.ping` 保持 WebSocket 连接保活,不作为直播业务状态依据。
2. 主播端开播成功后每 15s 发送 `streamer.live.heartbeat`；后端 60s 未收到则自动下播。
3. 开播响应新增 `session_id`，前端可把 `session_id`、`stream_no`、`zego_room_id` 原样放进心跳 payload，减少前端猜测。
4. ZegoCloud `stream_publish.stop` 回调仍是第一优先级；业务心跳 worker 只兜底回调丢失或主播端失联残留 `LIVE` 的场景。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | `LIVE-012` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | `StreamerStartLiveResponse.session_id`、`streamer.live.heartbeat`、`StreamerLiveHeartbeatPayload`、`RoomStatePayload` |
| 验收口径 | 主播业务心跳 60s 超时后,房间状态变为 `ENDED`,房间频道收到 `room.status.ended` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是；新增 `live_sessions.last_heartbeat_at` 和 `idx_status_heartbeat` |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；自动下播写系统审计 `live.heartbeat.timeout_end` |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行 migration；服务启动后自动启动进程内 worker |
| 回滚 | 执行 down migration 删除字段和索引；回滚代码后不再处理业务心跳 |
| 密钥 | 不涉及 |
| 观测 | worker 日志记录启动、扫描失败、单条结束失败；自动下播写审计 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer` | 通过 |
| `go test ./internal/http/wsapi` | 通过 |
| `go test ./internal/worker` | 通过 |
| `go test ./internal/service/live ./internal/service/hook ./internal/service/admin` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:openapi` | 通过 |
| `pnpm --filter @kickoff/live-host typecheck` | 通过 |

## 前端接入说明

1. 主播端 `apps/live-host` 已在开播成功后保存 `session_id`、`stream_no`、`zego_room_id`。
2. 主播端已通过 `/ws/v1/streamer?敏感凭据：[已脱敏] 每 15s 发送 `streamer.live.heartbeat`。
3. 心跳 payload 包含 `room_id`、`session_id`、`zego_room_id`、`zego_stream_id`，其中 `zego_stream_id` 使用开播响应里的 `stream_no`。
4. C 端不需要新增心跳接入；继续沿用原有 `room.status.ended` 关播处理即可。`reason=streamer_heartbeat_timeout` 只用于可选文案区分。
