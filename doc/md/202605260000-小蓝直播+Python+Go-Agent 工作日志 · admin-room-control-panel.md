---
id: "doc-77e63ec430ed"
title: "Agent 工作日志 · admin-room-control-panel"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "Redis", "监控告警", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-room-control-panel.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-room-control-panel.md"
sourceSha256: "9909c1497c84ce86391627aa84a88769244d1698292f166da4878380fb013777"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-room-control-panel

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-room-control-panel.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：补齐后台直播间控场台

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-904, ADM-906, ADM-907, ADM-908, ADM-909, ADM-917, ADM-918
- 接口/契约：`docs/api/openapi.yaml`, `packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`, `.ai-framework/AGENTS.md`

## 本次目标

1. 后台房间详情页复用 C 端直播间数据，补成 admin 权限下的控场面板。
2. 后端补 admin 弹幕历史、admin 弹幕监控 WS、Redis 在线观众明细。
3. 后台 UI 接入弹幕列表、删除/禁言、切比赛、观众明细、会话历史。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/wsx/hub.go` | 增加 Redis 在线观众集合登记/移除能力 |
| `services/go-app/internal/http/wsapi/handlers.go` | 公共直播 WS 登录观众进出时写入/移除在线集合 |
| `services/go-app/internal/service/admin/room.go` | 增加在线观众明细、后台弹幕历史、弹幕 DTO 丰富 |
| `services/go-app/internal/http/adminapi/room.go` | 增加后台弹幕历史接口，删除弹幕支持 query reason |
| `services/go-app/internal/http/adminapi/room_ws.go` | 增加 admin 房间弹幕监控 WS，校验 admin token 与房间权限 |
| `services/go-app/internal/http/router/admin.go` | 注册 admin 弹幕 REST / WS 路由并注入 Redis |
| `apps/admin/src/api/index.ts` | 增加房间弹幕、会话、监控 WS API client 类型 |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | 增加控场 tab：弹幕监控、在线观众、会话历史、切比赛 |
| `docs/api/openapi.yaml` | 补齐后台弹幕历史契约，更新观众明细字段 |
| `packages/contracts/openapi/v1.yaml` | 同步 OpenAPI 契约 |
| `docs/prd/modules/kickoff-admin.md` | 明确后台控场台不是重做 C 端直播间 |

## 核心决策

1. 在线观众明细以公共直播 WS 的登录用户连接为来源，写入 Redis `live:viewers:{room_id}` sorted set，score 为进入时间毫秒。
2. 后台监控 WS 订阅同一房间广播通道，但使用 admin token 与房间授权校验隔离权限。
3. 大 R 只作为 `spender_tier` 后台运营标签，来源为累计送出打赏钻石，不参与权限、排序或特效。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-904, ADM-906, ADM-907, ADM-908, ADM-909, ADM-917, ADM-918 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `GET /api/v1/admin/rooms/{id}/danmaku`, `GET /api/v1/admin/rooms/{id}/viewers`, `/ws/v1/admin/rooms/{id}/danmaku` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不新增表，复用 `live_rooms`、弹幕月表、`users`、`live_tips`、`live_sessions` 和 Redis |
| 是否影响账本、事务、幂等或审计 | 不改资金；删除弹幕、禁言、推流凭据等沿用现有审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 缓存 / 权限安全 / 实时 WS / 运营控场 |
| 当前 MVP 边界 | 观众明细只统计登录观众；游客仍只参与房间连接数广播 |
| 高风险触发项 | 权限 / 处罚 / 用户数据 |
| 能力门禁结论 | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/admin ./internal/pkg/wsx ./internal/http/adminapi ./internal/http/router` | 通过 |
| `go test ./...` | 通过 |
| `npm --prefix apps/admin run build` | 通过 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
