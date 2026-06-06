---
id: "doc-98c20d709e76"
title: "Agent 工作日志 · live-stop-ended-broadcast"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-stop-ended-broadcast.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-stop-ended-broadcast.md"
sourceSha256: "1626c0436ee69ee1a62d82bb7f80fe04503b29bd4cbbd88a74cd9fbb304a1260"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-stop-ended-broadcast

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-stop-ended-broadcast.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：修复主播下播后 C 端收不到 `room.status.ended` 通知

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-012
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈“有了赛事流，主播下播后，用户端收不到下播通知”

## 本次目标

1. 梳理主播主动下播、ZEGO 主播流 stop、心跳超时三条下播链路。
2. 保证正常下播后房间频道广播 `room.status.ended`。
3. 保证赛事流 stop 不会误触发主播下播广播。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/streamer/broadcast.go` | 新增主播端 service 共用的房间结束 WS 广播 helper。 |
| `services/go-app/internal/service/streamer/live.go` | 主播主动下播成功落库后广播 `room.status.ended`。 |
| `services/go-app/internal/service/streamer/webhook.go` | ZEGO 主播流 stop 兜底下播成功后广播 `room.status.ended`。 |
| `services/go-app/internal/http/router/public.go` | 将 WS broadcaster 注入主播 live service 和 zego webhook service。 |
| `services/go-app/internal/service/streamer/live_test.go` | 覆盖主播主动下播广播 payload。 |
| `services/go-app/internal/service/streamer/webhook_test.go` | 覆盖 ZEGO 主播流 stop 广播，以及赛事流 stop 不广播。 |
| `docs/api/openapi.yaml` | 补充 `room.status.ended.reason` 说明。 |
| `packages/contracts/openapi/v1.yaml` | 同步契约说明。 |

## 核心决策

1. 不改 C 端和主播端前端代码；后端继续通过已有房间 WS 频道推送。
2. 下播事件保持同一个事件名 `room.status.ended`，只扩展 `reason` 文档说明，避免破坏前端已有监听。
3. ZEGO stop 回调仍必须校验 stopped stream 等于当前 active host stream；赛事流 stop 不触发房间结束。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-012 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `RoomStatePayload.reason`：`streamer_stop` / `zego_publish_stop` / `streamer_heartbeat_timeout` |
| 不涉及契约的原因 | 涉及 WS event 文档，已更新 OpenAPI 与 contracts。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；保留原有 audit 写入 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需重新构建 Go API / WS 进程 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 观测 | 复用现有 WS 广播链路和直播状态日志 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer` | 通过 |
| `go test ./internal/worker` | 通过 |
| `go test ./internal/http/router` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 风险与待办

1. C 端如果没有监听 `room.status.ended`，仍需要前端按既有 WS 事件接入。
2. 多进程部署时 API 进程通过 Redis publisher 广播，WS 进程需要正常订阅 Redis 房间频道。
