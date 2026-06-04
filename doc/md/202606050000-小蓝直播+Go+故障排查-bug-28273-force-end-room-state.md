---
id: "doc-36daa49c0ed5"
title: "bug-28273-force-end-room-state"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-force-end-room-state.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-force-end-room-state.md"
sourceSha256: "44bbf8dc0bd9add8958ddcfbd87f0f5e726331988e4cbf39f313bf33ef6be4a5"
sourceSystem: "project-doc"
---

# bug-28273-force-end-room-state

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-force-end-room-state.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复 Zandao Bug 28273 后台强制关播后 H5 和主播端仍显示直播中

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-912
- 接口/契约：`POST /api/v1/admin/rooms/{id}/force-end`，operationId `adminRoomForceEnd`
- 其他：Zandao Bug 28273

## 本次目标

1. 后台强制关播后，后端直播间状态、直播场次、节目流会话和统计在线数保持一致。
2. 保留既有 WS `room.status.ended` 通知，不改接口形态。
3. 增加针对状态收口 SQL 的回归测试。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/room.go` | 强制关播事务补齐 live_session_stats、room_program_sessions、live_rooms.viewer_count 更新 |
| `services/go-app/internal/service/admin/room_test.go` | 增加强制关播关联表 SQL 和时长计算回归测试 |

## 核心决策

1. 不新增接口，不改请求/响应契约，仅修正 ADM-912 的服务端状态闭环。
2. 保留强制关播场次状态为 `LiveSessionStatusAborted`，符合后台强制处置语义。
3. 将 active 节目流会话置为 `ENDED` 且 `active=0`、`active_key=NULL`，避免公开播放接口继续选择旧 mixed stream。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-912 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 契约不变；继续使用 `adminRoomForceEnd` 与 `room.status.ended` |
| 不涉及契约的原因 | 只修正强制关播后的内部数据一致性，不改变接口字段 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 保留原审计；加强同一事务内状态一致性 |
| 规范例外与原因 | 不涉及 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 数据一致性 / 直播状态管理 / 审计 |
| 当前 MVP 边界 | 强制关播负责服务端权威状态收口；H5/主播端实时 UI 仍依赖既有事件或下一次接口刷新 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 后端服务部署生效 |
| 回滚 | 回滚本次代码即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增日志指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 强制关播后 public play-url 不应再拿到 active mixed stream，后台 KPI 不应继续把房间算在线 |
| 红队质疑 | 如果客户端完全不处理 `room.status.ended`，已打开页面仍可能等到流 DELETE 或刷新后才更新；本次遵守仓库边界未改 H5/主播端前端 |
| 合入判断 | 可合入后端修复 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 项目验收证据 | `docs/qa/project-acceptance.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin ./internal/service/live ./internal/service/liveprogram ./internal/http/adminapi` | 通过 |

## 风险与待办

1. H5 已有 ZEGO `roomStreamUpdate(DELETE)` 遮罩逻辑，但没有消费 `room.status.ended`；若 QA 要求秒级 UI 切换，需要前端团队接入该事件。
2. 主播端房间列表有缓存；强制关播后再次请求后端会拿到 ENDED，已打开页面的即时提醒需要主播端增加轮询或 WS。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 本次只改后端 ADM-912 状态闭环。
2. `room_program_sessions.active=0` 是 public play-url 不再选旧 mixed stream 的关键。
3. 如继续处理前端即时刷新，应按仓库规则先获得修改 `apps/web/**` 或 `apps/live-host/**` 的明确授权。
