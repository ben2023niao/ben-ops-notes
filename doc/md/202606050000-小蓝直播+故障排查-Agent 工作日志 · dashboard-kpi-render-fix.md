---
id: "doc-4e3dd038b002"
title: "Agent 工作日志 · dashboard-kpi-render-fix"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-kpi-render-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-kpi-render-fix.md"
sourceSha256: "958927bafba7ffa0dd21c34289c3041a79338c9c65a0469e507c3386e85af4bb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dashboard-kpi-render-fix

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20dashboard-kpi-render-fix.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复运营总览 KPI 接口有数据但页面显示 0

## 输入资料

- 用户反馈：运营总览事件流能显示新数据，但 4 个 KPI 仍为 0。
- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-101
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 判断是接口未返回还是前端读取错误。
2. 修复 KPI 卡片显示真实接口值。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/dashboard/overview.vue` | 移除 KPI 卡片对 `ElStatistic` 默认 slot 的错误用法，改为直接渲染 `card.value` |

## 核心决策

1. 后端接口返回真实 KPI，事件流也能展示，问题定位为前端 KPI 渲染。
2. Element Plus `ElStatistic` 数值依赖 `value` prop，当前默认 slot 不生效导致组件显示默认值 0。
3. KPI 卡片改为普通标题和值 DOM，避免组件默认值覆盖真实数据。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 接口返回正确，只修复前端渲染 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `GET /api/v1/admin/dashboard/kpi` | 已确认返回非 0 的 `online_viewers` 和 `live_room_count` |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图 |
| 响应式验收 | 不改变卡片网格布局 |
| API 接口路径 | `/api/v1/admin/dashboard/kpi` |
| 与设计图主要偏差 | 修复前数值被 `ElStatistic` 默认 0 覆盖；修复后直接显示接口值 |
| 合入判断 | 可合入 |

## 风险与待办

1. 若后续继续使用 `ElStatistic`，必须显式传 `:value`，不要通过默认 slot 传数值。
