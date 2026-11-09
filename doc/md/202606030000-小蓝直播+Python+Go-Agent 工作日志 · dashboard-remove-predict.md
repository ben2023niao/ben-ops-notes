---
id: "doc-48abcf0e550e"
title: "Agent 工作日志 · dashboard-remove-predict"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-dashboard-remove-predict.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-dashboard-remove-predict.md"
sourceSha256: "26b9030e7abe1b2bea244719c155b0502c600325059099cfe17c2fc1680b2adc"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dashboard-remove-predict

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20dashboard-remove-predict.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：运营总览去除竞猜数据展示与聚合

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`
- 其他：用户反馈 `/analytics` 运营总览已无竞猜业务，不应继续展示竞猜指标。

## 本次目标

1. 后台运营总览页面移除今日押注、进行中竞猜、押注趋势。
2. 后端看板聚合不再查询竞猜表。
3. OpenAPI 与 contracts 去除看板 KPI 的竞猜字段。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/dashboard/overview.vue` | 移除竞猜 KPI 卡片与 GMV 图中的押注曲线 |
| `apps/admin/src/api/modules/dashboard.ts` | 移除看板 DTO 中的竞猜字段 |
| `apps/admin/src/locales/langs/zh-CN/dashboard.json` | 移除中文竞猜文案 |
| `apps/admin/src/locales/langs/en-US/dashboard.json` | 移除英文竞猜文案 |
| `services/go-app/internal/dto/admin_modules.go` | 移除看板响应 DTO 中的竞猜字段 |
| `services/go-app/internal/service/admin/dashboard.go` | 移除 KPI、GMV7D、Events24h 对竞猜表的聚合 |
| `docs/api/openapi.yaml` | 同步看板 KPI 契约字段 |
| `packages/contracts/openapi/v1.yaml` | 同步看板 KPI 契约字段 |

## 核心决策

1. 竞猜业务已下线，运营总览不再读 `predict_bets` / `predict_activities`。
2. 看板 KPI 保留今日 GMV、今日新增用户、在线观众、直播中房间四项。
3. 近 7 日 GMV 走势只保留充值 RMB 和打赏 RMB。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金写操作 |
| 是否影响部署配置 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/adminapi` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 风险与待办

1. 前端部署后需在 `/analytics` 确认只显示四个 KPI 和两条 GMV 曲线。
2. 旧竞猜模块的其他后台入口不在本次范围。
