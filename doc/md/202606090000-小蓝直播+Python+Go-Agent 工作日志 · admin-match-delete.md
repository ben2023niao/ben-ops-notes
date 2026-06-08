---
id: "doc-2d55779d0cb5"
title: "Agent 工作日志 · admin-match-delete"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-match-delete.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-match-delete.md"
sourceSha256: "51c544631a2e71ac25f4db74b0cf3faf66507141fbd7c5d947cc316f010b7359"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-match-delete

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-match-delete.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：后台赛事管理增加受保护删除能力

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-201
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台赛事管理支持删除误录赛事。
2. 删除必须保护直播间、直播历史、节目流和历史竞猜引用。
3. 后台页面提供清晰删除确认文案。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/match.go` | 新增赛事软删除、引用检查、子数据清理和审计 |
| `services/go-app/internal/http/adminapi/match.go` | 新增 `DELETE /matches/{id}` handler |
| `services/go-app/internal/http/router/admin.go` | 注册后台赛事删除路由 |
| `services/go-app/internal/service/admin/match_test.go` | 覆盖删除保护规则 |
| `apps/admin/src/api/modules/match.ts` | 新增后台赛事删除 API client |
| `apps/admin/src/views/matches/list.vue` | 列表增加删除按钮和确认弹窗 |
| `apps/admin/src/locales/langs/*/matches.json` | 新增删除文案 |
| `docs/api/openapi.yaml` | 新增 `adminMatchDelete` 文档 |
| `packages/contracts/openapi/v1.yaml` | 同步契约 |

## 核心决策

1. 使用 GORM 软删除 `matches.deleted_at`，不做物理删除。
2. 进行中、已结束、已关联直播间、已有直播历史、节目流或历史竞猜引用的赛事禁止删除。
3. 允许删除时同步软删赛事 LSJ 绑定和进球记录，并清空淘汰赛对阵图的 `match_id`。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-201 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 新增 `adminMatchDelete`；不涉及 C 端/主播端字段变更 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及，复用既有 `deleted_at` |
| 是否影响账本、事务、幂等或审计 | 不涉及账本；删除写 `admin.match.delete` 审计 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要发布 admin-api 和 admin-web |
| 回滚 | 回滚代码即可；已软删数据可由数据库恢复/人工修正 |
| 密钥 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin -run 'TestValidateMatchDelete'` | 通过 |
| `go test ./internal/service/admin ./internal/http/adminapi ./internal/http/router` | 通过 |
| `go test ./...`（services/go-app） | 通过 |
| `python3 -m json.tool apps/admin/src/locales/langs/zh-CN/matches.json` | 通过 |
| `python3 -m json.tool apps/admin/src/locales/langs/en-US/matches.json` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| API 接口路径 | `DELETE /api/v1/admin/matches/{id}` |
| 后台权限与审计 | 需要后台登录；删除写 `admin.match.delete` |
| 合入判断 | 已实现并通过静态/单元验证，待部署后由 QA 验证页面交互 |

## 风险与待办

1. 删除接口只适合清理误录赛事；正式赛程建议改状态，不建议删除。
2. 已有关联或历史数据时会返回 409，需要运营按提示先解除直播间绑定或保留历史。
