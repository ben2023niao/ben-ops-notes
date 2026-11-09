---
id: "doc-694698f3ebff"
title: "Agent 工作日志 · dashboard-streamer-top-streams"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-streamer-top-streams.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-streamer-top-streams.md"
sourceSha256: "64a43ed92d431e7c80bf53d0e61f818befcb33430f3f27b70de6f7e1f6b5fe47"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dashboard-streamer-top-streams

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20dashboard-streamer-top-streams.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复运营总览主播 Top 开播场次全为 0

## 输入资料

- 用户反馈：主播打赏 Top 10 中“开播场次”全部为 0。
- 验证接口：`/api/v1/admin/streamers/top?limit=10`、`/api/v1/admin/rooms/{id}/sessions`
- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-104
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 判断开播场次是测试假数据还是统计未维护。
2. 修复主播 Top 榜开播场次统计口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/dashboard.go` | `StreamersTop` 从 `live_sessions` 实时聚合开播场次；升级 Top 榜缓存 key |

## 核心决策

1. `streamers/top` 对“足球解说大师”返回 `total_streams=0`，但该房间 `sessions` 接口已有 9 条场次，说明不是假数据，是 Top 接口读了未维护的物化列。
2. `streamers.total_streams` 当前没有被开播/下播链路维护，不适合作为看板来源。
3. Top 榜继续按 `streamers.total_tip_rmb` 排序，开播场次改为 `live_sessions` 按 `streamer_id` 实时 `COUNT(*)` 聚合。
4. 缓存 key 升级为 `admin:dash:top:v2:{limit}`，部署后不读旧的 0 缓存。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-104 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及，响应结构不变 |
| 不涉及契约的原因 | 只修复服务端统计来源 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `GET /api/v1/admin/rooms/22536490118545409/sessions?size=20` | dev 当前返回 9 条直播场次 |
| `go test ./internal/service/admin ./internal/http/adminapi` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图 |
| API 接口路径 | `/api/v1/admin/streamers/top` |
| 与设计图主要偏差 | 截图开播场次全 0；修复后按 `live_sessions` 聚合真实场次 |
| 合入判断 | 可合入 |

## 风险与待办

1. 如未来要求“仅统计已结束场次”或“只统计当天场次”，需要产品确认后调整 `COUNT(*)` 过滤条件。
