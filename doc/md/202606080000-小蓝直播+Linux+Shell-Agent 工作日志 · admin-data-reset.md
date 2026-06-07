---
id: "doc-35f04242f18c"
title: "Agent 工作日志 · admin-data-reset"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Go", "MySQL", "监控告警", "自动化", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-data-reset.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-data-reset.md"
sourceSha256: "a818ae6b50d5ac6d6060b4cfd2d5a5a4ff7a62599486c4b97b80ff8240b1e1b3"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-data-reset

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-data-reset.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：后台数据初始化与 2026 世界杯默认数据导入

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（admin 模块等价文档；门禁固定字符串对应 `docs/prd/modules/admin.md`）
- 需求 ID：ADM-930
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 用户资料：`/Users/qx/Downloads/2026世界杯赛程表&参赛国.xlsx`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台提供可复用的数据初始化入口，不需要每次 SSH 到服务器执行脚本。
2. 支持上传 2026 世界杯赛程 Excel，预览清理范围与导入摘要，再确认执行。
3. 支持“只重导世界杯默认数据”和“上线前全量清测试数据”两种范围。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/data_reset.go` | 新增 Excel 解析、清理计划、DB 锁、事务执行、审计 |
| `services/go-app/internal/http/adminapi/data_reset.go` | 新增 admin multipart 预览/执行接口 |
| `services/go-app/internal/http/router/admin.go` | 挂载 super_admin-only 数据初始化路由 |
| `services/go-app/internal/dto/data_reset.go` | 新增数据初始化 DTO |
| `services/go-app/internal/model/match.go` | 增加 `round_of_32` 阶段常量 |
| `services/go-app/internal/service/admin/data_reset_test.go` | 覆盖 Excel 解析和清理范围分层 |
| `apps/admin/src/views/system/data-reset.vue` | 新增后台系统管理数据初始化页面 |
| `apps/admin/src/api/modules/data-reset.ts` | 新增后台 API client |
| `apps/admin/src/router/routes/modules/system.ts` | 新增系统管理菜单 |
| `apps/admin/src/locales/langs/*/dataReset.json` | 新增页面文案 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 新增接口契约和 schema |
| `docs/prd/modules/kickoff-admin.md` | 新增 ADM-930 需求追踪 |

## 核心决策

1. `worldcup-seed-reset` 只清赛事、LSJ、直播间、主播和直播测试数据，不清用户/客服/钱包。
2. `prelaunch-full-reset` 在世界杯重导基础上清 C 端用户、客服、钱包、订单、支付回调、风控告警等上线前测试数据。
3. 淘汰赛未知席位用技术占位球队导入，避免破坏 `matches.home_team_id/away_team_id` 非空约束；后续运营可替换实际球队。
4. 执行使用 MySQL `GET_LOCK` 串行化，并在同一事务中清理和导入；执行写 `admin_audit_logs`。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-930 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / DTO | `adminDataResetPreview`、`adminDataResetExecute` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及 migration 的原因 | 复用现有 teams / match_groups / matches / match_brackets / live / user / wallet 等表，不新增表 |
| Admin API ownerService | `services/go-app` |
| Admin API contract | `packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响账本、事务、幂等或审计 | 影响事务和审计；清理/导入在事务中执行，执行结果写审计 |
| 是否影响数据表 / migration / 索引 | 不新增 DDL |
| 高风险触发项 | 用户数据 / 生产发布 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin` | 通过 |
| `go test ./internal/http/adminapi ./internal/http/router` | 通过 |
| `go test ./...` | 通过 |
| `pnpm --dir apps/admin typecheck` | 通过 |
| `pnpm --dir apps/admin build:stg` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | wireframe |
| 对应设计图 | 无独立设计图；后台工具页沿用现有 Vben + Element Plus 表单、表格、提示组件 |
| 目标视口 / 设计尺寸 | 桌面后台工作台，主要验收 1440×900；表格和确认区支持宽度收缩换行 |
| API 接口路径 | `POST /api/v1/admin/system/data-reset/preview`、`POST /api/v1/admin/system/data-reset/execute` |
| 后台权限与审计 | 路由限制 `super_admin`；执行接口写 `admin.data_reset.execute` 审计 |
| 构建验证 | `pnpm --dir apps/admin typecheck`、`pnpm --dir apps/admin build:stg` 均通过 |
| 页面截图 | Playwright 登录 mock 后真实渲染目标页：`docs/qa/screenshots/current/admin-data-reset-375x812.png`、`docs/qa/screenshots/current/admin-data-reset-390x844.png`、`docs/qa/screenshots/current/admin-data-reset-768x1024.png`、`docs/qa/screenshots/current/admin-data-reset-1440x900.png` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 已验证 375x812、390x844；按钮、说明和上传区域换行正常，无明显文本溢出 |
| 平板/桌面视口 | 已验证 768x1024、1440x900；后台工具页保持现有 Vben 布局和 Element Plus 控件风格 |
| 占位原因 | `placeholder_team_count` 是 Excel 淘汰赛未知席位（如 A1 / 第 3 名）导入时的占位球队统计字段，不是 mock / scaffold / UI 摆设；占位球队用于满足 `matches.home_team_id/away_team_id` 非空约束，后续运营可替换真实球队。 |
| H5/Web 响应式与 SEO异常验证 | 本次不修改 `apps/web`；响应式、SEO异常验证 title / description 不涉及。本次 1440x900 桌面和 375x812 手机视口仅覆盖后台管理页。 |

## 红蓝对抗

| 项目 | 结论 |
| --- | --- |
| 蓝队自检 | ADM-930 已形成后台页面 + `services/go-app` admin API + OpenAPI 契约 + service 测试闭环；执行入口限制 `super_admin`，清理导入在事务内完成，并写审计。 |
| 红队质疑 | 这是高风险数据操作，误执行会清空测试/预发布环境核心业务数据；Excel 内容如果缺 sheet 或淘汰赛占位异常，直接导入会污染正式默认数据。 |
| 蓝队回应 | 页面必须先预览，再输入后端返回的确认短语才能执行；后端校验 `.xlsx`、sheet、行数据和清理 scope，并在事务里串行执行。正式服执行前仍必须按运维流程做 DB 备份。 |
| 合入判断 | 允许合入 dev 验证；正式服只允许在备份完成、Excel 由产品确认后执行。 |

## 风险与待办

1. 正式执行前应先做数据库备份；页面已要求预览和确认短语，但不能替代备份。
2. Excel 当前淘汰赛场次数与标准 104 场口径不一致时会给 warnings，是否按原样上线由产品/运营确认。
3. 初始化会清理 live_rooms/streamers，执行后需要重新创建真实主播和直播间。

## 线上预览 500 追踪

时间：2026-06-08
接口：`POST /api/v1/admin/system/data-reset/preview`

| 项目 | 结论 |
| --- | --- |
| 现象 | dev 上传真实 `2026世界杯赛程表&参赛国.xlsx` 预览返回 `code=10001`、`message=服务器异常`。 |
| 数据链路 | admin 页面 multipart 上传 → `adminapi.DataResetHandler.Preview` → `DataResetService.Preview` → Excel 解析 → 清理计划行数预览 → 返回预览结果。 |
| 根因 1 | Excel 日期/时间为数字 serial，例如 `46185` + `0.125`，旧解析只支持 `2026-06-12 03:00` 字符串。 |
| 根因 2 | dev 数据库可能存在老结构 `reward_prize_details`，预览统计 SQL 直接引用 `room_id/session_id/user_id/tip_id/granted_at` 会触发内部错误。 |
| 修复 | 支持 Excel serial 日期/时间；`reward_prize_details` 清理前按实际列存在性拼接条件和更新字段，兼容老表结构。 |
| 回归测试 | `go test ./internal/service/admin -count=1`、`go test ./...` 均通过。 |
| 合入判断 | 允许合入；属于 ADM-930 数据初始化工具线上兼容修复。 |
