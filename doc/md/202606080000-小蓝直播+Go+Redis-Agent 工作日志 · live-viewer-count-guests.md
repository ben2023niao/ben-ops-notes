---
id: "doc-8dd3617bdc02"
title: "Agent 工作日志 · live-viewer-count-guests"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-live-viewer-count-guests.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-live-viewer-count-guests.md"
sourceSha256: "d52678372cfd1fa031a38ce64adea0cb5b04aa7dcf73970a938b37fe2153f53d"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-viewer-count-guests

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-live-viewer-count-guests.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：在线观众统计包含游客连接

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-001 / ADM-907
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 修复直播间在线观众不统计游客的问题。
2. 保持 C 端 WS 事件名和 `viewer_count` 字段不变。
3. 同步后台观众列表接口说明，明确游客占位返回。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/wsx/client.go` | 为每条 WS 连接生成连接 ID，游客按连接去重。 |
| `services/go-app/internal/pkg/wsx/hub.go` | 在线观众 Redis member 改为 `user:{id}` / `guest:{connection_id}`，并兼容历史数字 user_id。 |
| `services/go-app/internal/http/wsapi/handlers.go` | 统一入口和旧直播间 WS 入口都使用 viewer member 追踪在线人数。 |
| `services/go-app/internal/service/admin/room.go` | 后台在线观众列表兼容游客 member，游客显示为“游客”。 |
| `services/go-app/internal/pkg/wsx/hub_test.go` | 覆盖游客计入在线人数和离开扣减。 |
| `services/go-app/internal/service/admin/room_test.go` | 覆盖后台游客在线列表不依赖 DB。 |
| `docs/prd/modules/kickoff-live.md` | 明确在线观众包含游客连接，独立访客仍按登录用户去重。 |
| `docs/prd/modules/kickoff-admin.md` | ADM-907 口径同步为登录用户和游客连接。 |
| `docs/api/openapi.yaml` | 后台观众列表 schema 更新，`viewer_count` 描述包含游客。 |
| `packages/contracts/openapi/v1.yaml` | 契约副本同步后台观众列表 schema。 |

## 核心决策

1. 在线人数表达“当前有多少人在看”，应包含游客连接。
2. 登录用户仍按 `user_id` 去重，同一用户多开不重复累计在线人数。
3. 游客没有稳定账号身份，按 WS 连接 ID 计数；断开或退订直播间时扣减。
4. `unique_visitors` 仍只按 session + 登录用户去重，游客不计独立用户，避免用户统计被匿名流量污染。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-001 / ADM-907 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | C 端 WS `live.viewer.count.updated` 字段不变；后台 `adminRoomViewers` 文档更新 |
| 前端字段变更 | 不涉及字段改名；前端继续读取 `viewer_count` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 是否影响 C 端前端代码 | 不修改 `apps/web/**` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/pkg/wsx ./internal/http/wsapi ./internal/service/admin` | 通过 |
| `go test ./internal/service/live ./internal/service/streamer ./internal/pkg/wsx ./internal/http/wsapi ./internal/service/admin` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 风险与待办

1. Redis 中历史纯数字 member 已兼容读取，部署后旧在线记录会自然过期。
2. 单实例无 Redis fallback 仍按本机 channel 连接数统计，和历史行为一致。
3. 前端无需改字段，但应知道 `viewer_count` 现在包含游客。
