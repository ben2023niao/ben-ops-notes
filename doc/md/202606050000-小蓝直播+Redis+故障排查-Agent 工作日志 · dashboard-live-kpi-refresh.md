---
id: "doc-7356e7f26da2"
title: "Agent 工作日志 · dashboard-live-kpi-refresh"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Redis", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-live-kpi-refresh.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-live-kpi-refresh.md"
sourceSha256: "0e7b66de26a306b2a8e54bbca9f3b09f6178df9532a2a62f401ca98dab4283d5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dashboard-live-kpi-refresh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BRedis%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20dashboard-live-kpi-refresh.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：运营总览直播 KPI 不随真实直播状态刷新

## 输入资料

- 用户反馈：H5 房间 `22536490118545409` 正在直播，但后台运营总览显示直播中房间为 0
- 验证 URL：`https://web-dev.54-151-131-132.sslip.io/live/22536490118545409`
- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-101
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 确认运营总览数据是否来自真实接口。
2. 修复后台运营总览页面打开后不自动刷新导致 KPI 停留在旧值的问题。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/dashboard/overview.vue` | 将看板加载抽为 `loadDashboard`，页面挂载后每 30 秒刷新一次，卸载时清理定时器 |

## 核心决策

1. 后端 dashboard KPI 真实读取 `live_rooms.status = LIVE` 与 `viewer_count`，不是前端 mock。
2. 用户截图中 0 的问题更符合前端标签页打开后只拉一次数据，直播状态变化后页面不刷新。
3. 使用 30 秒轮询，与后端 KPI Redis 缓存 TTL 对齐，避免高频刷接口。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及，接口契约不变 |
| 不涉及契约的原因 | 只调整前端刷新策略 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `GET /api/v1/live/room/22536490118545409` | 返回 `status=LIVE`、`viewer_count=1` |
| `GET /api/v1/admin/dashboard/kpi` | 返回 `online_viewers=2`、`live_room_count=7` |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图 |
| 响应式验收 | 不涉及布局变化 |
| API 接口路径 | `/api/v1/admin/dashboard/kpi` 等 dashboard 现有接口 |
| 与设计图主要偏差 | 截图旧值为 0；修复后页面会周期刷新到后端真实值 |
| 合入判断 | 可合入 |

## 风险与待办

1. 当前是轮询方案；未来如启用后台事件 WS，可改为事件驱动刷新 KPI。
