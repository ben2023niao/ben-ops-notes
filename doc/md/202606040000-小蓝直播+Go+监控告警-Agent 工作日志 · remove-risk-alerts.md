---
id: "doc-80d5ae00ae9b"
title: "Agent 工作日志 · remove-risk-alerts"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "监控告警", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-remove-risk-alerts.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-remove-risk-alerts.md"
sourceSha256: "4f174e5a9a0cec23c329667ed9fb39db3cdc6352f8b49ebc4f5e13294385ac44"
sourceSystem: "project-doc"
---

# Agent 工作日志 · remove-risk-alerts

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-remove-risk-alerts.md`

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：竞猜下线后移除后台风控告警入口

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`ADM-601` ~ `ADM-606`（已下线）
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`

## 本次目标

1. 后台不再展示风控告警菜单和页面。
2. 后端不再暴露 `/api/v1/admin/risk/*` 风控告警接口。
3. 竞猜下注服务不再生成 `R-301` 大额押注风控告警。
4. OpenAPI 和 PRD 同步标记风控告警中心下线。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/router/routes/modules/risk.ts` | 移除风控告警子菜单，仅保留对账和内容审核 |
| `apps/admin/src/api/index.ts` | 移除 risk API client 导出 |
| `apps/admin/src/api/modules/risk.ts` | 删除风控告警 API client |
| `apps/admin/src/views/risk/list.vue` | 删除风控告警页面 |
| `apps/admin/src/locales/langs/*/risk.json` | 删除风控告警页面文案 |
| `services/go-app/internal/http/router/admin.go` | 移除 `/api/v1/admin/risk/*` 路由 |
| `services/go-app/internal/http/adminapi/risk.go` | 删除风控告警 handler |
| `services/go-app/internal/service/admin/risk.go` | 删除风控告警 service |
| `services/go-app/internal/service/admin/risk_test.go` | 删除已下线 service 测试 |
| `services/go-app/internal/model/risk.go` | 删除风控告警运行时 model |
| `services/go-app/internal/dto/admin_modules.go` | 删除风控告警 DTO |
| `services/go-app/internal/http/adminapi/placeholder.go` | 移除风控占位响应，仅保留对账 / 内容审核占位 |
| `services/go-app/internal/service/predict/service.go` | 删除下注后生成 R-301 风控告警逻辑 |
| `docs/api/openapi.yaml` / `packages/contracts/openapi/v1.yaml` | 删除后台风控告警分组、路径和专用 schema |
| `docs/prd/modules/kickoff-admin.md` | 标记 ADM-601~ADM-606 已下线 |

## 边界说明

- 不删除历史 migration 和数据库表，避免破坏已部署环境。
- `risk_admin` 角色保留，继续用于用户冻结 / 解冻 / 重置密码等敏感操作授权。
- 提现订单中的 `risk_score` 字段不属于本次“风控告警中心”，保留。

## 验证记录

- `go test ./internal/http/router ./internal/http/adminapi ./internal/service/predict ./internal/service/admin ./internal/dto ./internal/model`
- `pnpm --filter @kickoff/admin typecheck`
- `npm run check:openapi`
- `npm run check:contract`
- `npm run check:prd`
- `npm run check:engineering-standards`
- `npm run check:capability-gates`
- `npm run check:completion-claim`
- `git diff --check`
