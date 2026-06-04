---
id: "doc-bd07d78976a5"
title: "Agent 工作日志 · dashboard-gmv7d-recharge"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "MySQL", "Redis", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-gmv7d-recharge.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-gmv7d-recharge.md"
sourceSha256: "60f449110253ef5ba3c155097221693728a5dcf40c68e6436a7f42937c3d0deb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dashboard-gmv7d-recharge

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-dashboard-gmv7d-recharge.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复运营总览近 7 日 GMV 走势漏算今日充值

## 输入资料

- 用户反馈：今天 100% 有用户充值，但近 7 日 GMV 走势仍全 0。
- 验证接口：`/api/v1/admin/dashboard/gmv-7d`、`/api/v1/admin/dashboard/kpi`、`/api/v1/admin/orders/recharges`
- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-102
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 判断 GMV 走势是前端读取错误还是后端接口返回错误。
2. 修复后端 GMV7D 聚合，使今日已支付充值出现在趋势曲线。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/dashboard.go` | GMV7D 聚合日期改用 `DATE_FORMAT(..., '%Y-%m-%d') AS day` 并显式映射字段；升级 GMV7D Redis cache key |

## 核心决策

1. `dashboard/kpi` 返回 `today_gmv_rmb=100.00`，充值订单列表存在今日 `PAID 100.00`，但 `dashboard/gmv-7d` 返回全 0，问题在后端 GMV7D 聚合。
2. 原 SQL 使用 `DATE(paid_at) AS d` 再映射到 Go 字符串，日期 key 未命中输出数组的 `YYYY-MM-DD`，导致补零。
3. 改为 MySQL 直接输出 `YYYY-MM-DD` 字符串，并用 `gorm:"column:day"` 显式映射；同时把缓存 key 升级为 `admin:dash:gmv7d:v2` 避免旧 0 缓存影响上线验证。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-102 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及，响应结构不变 |
| 不涉及契约的原因 | 仅修复聚合 SQL 和缓存 key |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `GET /api/v1/admin/dashboard/kpi` | dev 当前返回 `today_gmv_rmb=100.00` |
| `GET /api/v1/admin/orders/recharges?status=PAID&size=20` | dev 存在今日 `PAID 100.00` 充值 |
| `go test ./internal/service/admin ./internal/http/adminapi` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图 |
| API 接口路径 | `/api/v1/admin/dashboard/gmv-7d` |
| 与设计图主要偏差 | 截图曲线全 0；修复后接口会返回今日充值聚合值 |
| 合入判断 | 可合入 |

## 风险与待办

1. 部署后需要等待后端服务更新；缓存 key 已升级，不需要手动清 Redis。
