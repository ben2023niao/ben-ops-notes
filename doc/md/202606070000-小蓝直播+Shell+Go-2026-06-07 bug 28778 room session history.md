---
id: "doc-3ac19f47a0d9"
title: "2026-06-07 bug 28778 room session history"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Redis", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28778-room-session-history.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28778-room-session-history.md"
sourceSha256: "453d06cfa0b72035456f8c81ebbca8cd5fd02a64ef315c61420a94b3808fc314"
sourceSystem: "project-doc"
---

# 2026-06-07 bug 28778 room session history

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28778-room-session-history.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：修复禅道 Bug #28778，后台直播间管控页会话历史记录数据不正确。

## 输入资料

- 禅道：`https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28778`
- 页面：后台管理 / 直播管理 / 直播间管理 / 管控 / 会话历史
- 接口：`GET /api/v1/admin/rooms/{id}/sessions`
- 需求 ID：`ADM-917`

## 数据链路

1. 后台页面 `apps/admin/src/views/rooms/detail.vue` 的会话历史 tab 调用 `roomApi.sessions()`。
2. Admin API 路径为 `/api/v1/admin/rooms/{id}/sessions`。
3. 路由进入 `adminapi.RoomHandler.Sessions`，再调用 `admin.RoomService.Sessions`。
4. 修复前服务层直接返回 `live_sessions` GORM model。
5. 实际会话增量统计写入 `live_session_stats`，打赏流水 source of truth 是 `live_tips`，弹幕持久化在月分表 `live_chat_messages_YYYYMM`，但历史列表没有读取这些统计来源。
6. 修复后服务层返回专用 `dto.AdminRoomSession`，字段保持后台前端现有契约；统计从 `live_session_stats` 和 `live_tips` 聚合，旧数据兜底 `live_sessions` 原字段。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/admin_modules.go` | 新增 `AdminRoomSession` DTO，输出 snake_case 字段。 |
| `services/go-app/internal/service/admin/room.go` | 会话历史改用统计查询：join `live_session_stats`，聚合 `live_tips`。 |
| `services/go-app/internal/service/admin/room_test.go` | 增加 SQL 来源和 DTO 映射测试。 |
| `docs/api/openapi.yaml` | `adminRoomSessions` 响应改为 `AdminRoomSession`。 |
| `packages/contracts/openapi/v1.yaml` | 同步契约副本。 |

## 根因

- `live_sessions.peak_viewers / total_tip_rmb / total_chat` 是历史冗余字段，当前业务增量没有持续维护。
- Admin 会话历史接口直接返回 `model.LiveSession`，既读到了未维护的 0 值，也没有稳定 JSON tag 契约。

## 解决方案

- 查询会话列表时仍以 `live_sessions` 作为分页主表。
- `duration_sec`、`peak_viewers`、`total_chat` 优先使用 `live_session_stats`，并兜底 `live_sessions` 原字段。
- `total_tip_rmb` 优先按 `live_tips.rmb_equiv` 聚合，兜底 `live_session_stats.tip_income_diamond` 和 `live_sessions.total_tip_rmb`。
- 返回专用 DTO，保持后台前端读取的 `id/start_at/duration_sec/peak_viewers/total_tip_rmb/total_chat` 字段。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| dev 库等价 SQL 查询 R00006 | 有真实流水的 session 返回 `11.00` 打赏、`1` 弹幕、峰值在线 `3` |
| `go test ./internal/service/admin -run 'TestRoomSessionsSelectQueryUsesStatsAndTipAggregate|TestAdminRoomSessionToDTOUsesStatsFields' -count=1` | 通过 |
| `go test ./internal/service/admin -count=1` | 通过 |
| `go test ./... -count=1` | 通过 |
| `go vet ./...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 运维影响

- 不涉及 DB migration、Redis 结构、密钥或部署配置。
- 部署后历史接口可直接读取已存在的 `live_session_stats` 和 `live_tips` 数据，无需补数据脚本。
