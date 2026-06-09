---
id: "doc-d9637d23dc9e"
title: "Agent 工作日志 · live-room-always-visible"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "监控告警", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-live-room-always-visible.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-live-room-always-visible.md"
sourceSha256: "1c7e4e226b5b25fb9c8a1fa98b0a175ad2eec63fa73507a7d9f52e804a7f61a3"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-room-always-visible

> 来源文件：`~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-live-room-always-visible.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：直播间常驻展示

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-home.md`
- Admin 通用 PRD：`docs/prd/modules/admin.md`（项目未提供该通用文件；本项目后台 PRD 以 `docs/prd/modules/kickoff-admin.md` 为准）
- 需求 ID：ADM-901、HOME-004
- 接口/契约：`docs/api/openapi.yaml`、`docs/api/admin-api.md`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台直播间管理支持将房间设为/取消常驻展示。
2. `GET /api/v1/home/live-rooms` 返回直播中房间以及常驻房间。
3. C 端获得 `always_visible` 布尔字段，用 `status` 判断是否真正直播中。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000052_add_live_room_always_visible.*.sql` | 新增 `live_rooms.always_visible` 和首页可见列表索引 |
| `services/go-app/internal/model/live.go` | 新增房间常驻字段 |
| `services/go-app/internal/dto/*.go` | admin 和 home DTO 增加 `always_visible` |
| `services/go-app/internal/repository/live/live.go` | 首页直播间查询改为 `LIVE OR always_visible` |
| `services/go-app/internal/service/admin/room.go` | 新增常驻状态切换服务和审计 |
| `services/go-app/internal/http/adminapi/room.go`、`services/go-app/internal/http/router/admin.go` | 新增 admin 常驻切换接口 |
| `apps/admin/src/views/rooms/list.vue` | 新增常驻列和设为/取消常驻按钮 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 同步新增字段与接口契约 |

## 核心决策

1. 常驻展示不改变直播状态机，`status` 仍表达真实开播状态。
2. 首页列表包含 `LIVE` 或 `always_visible=true` 的房间，封禁房间不返回。
3. 前端新增字段为 `always_visible`，无既有字段改名或删除。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 000052 migration 和可见列表复合索引 |
| 是否影响账本、事务、幂等或审计 | 不影响资金；admin 常驻切换写 `admin.room.always_visible` 审计 |
| 后台权限与 ownerService | `POST /api/v1/admin/rooms/{id}/always-visible` 由 `services/go-app` 提供；接口走 admin JWT + `super_admin` 权限 |
| 是否影响前端字段 | 是，新增 `always_visible`；不涉及字段改名 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-901、HOME-004 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-home.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无独立设计图；沿用现有 Vben/Element Plus 后台表格和操作按钮样式 |
| 页面截图 | Playwright smoke screenshot：`output/playwright/admin-rooms-always-visible-1440x900.png`、`output/playwright/admin-rooms-always-visible-375x812.png` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375x812，未带登录态访问 `/rooms` 正常跳转登录页 |
| 桌面/平板视口 | 1440x900，未带登录态访问 `/rooms` 正常跳转登录页 |
| 响应式验收 | 本地 smoke 覆盖 375x812 与 1440x900；业务列表按钮需部署后用有权限账号在后台验收 |
| API 接口路径 | `POST /api/v1/admin/rooms/{id}/always-visible`、`GET /api/v1/home/live-rooms` |
| SEO异常验证/分享/下载渠道 | 不涉及 SEO异常验证/meta；本次只改后台运营表格和后端接口 |
| 后台权限与审计 | `super_admin` 可操作；后端写 `admin.room.always_visible` audit |
| console 是否无 error | 本地未登录 smoke 会触发登录态相关拦截日志；未发现本次组件编译错误 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 常驻字段不改直播状态机，C 端通过 `status` 判断是否直播中，通过 `always_visible` 判断是否常驻展示。 |
| 红队质疑 | 如果把常驻当作直播中，会误显示 LIVE；已在 PRD、OpenAPI、日志和后台确认文案中强调区分。 |
| 合入判断 | 允许合入；需要部署后由 QA 在后台房间列表点击“设为常驻/取消常驻”并验证 C 端首页返回。 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行数据库迁移后发布后端和后台前端 |
| 回滚 | 执行 `000052_add_live_room_always_visible.down.sql` 并回滚应用版本 |
| 密钥 | 不涉及 |
| 观测 | 不涉及新增日志或告警 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/repository/live ./internal/service/home ./internal/service/admin ./internal/service/schedule` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 交接说明

1. C 端首页直播间列表新增 `always_visible`，仍必须以 `status` 判断是否显示 LIVE 态。
2. 后台按钮文案已说明：常驻房间未开播也会展示到 C 端首页。
3. 本次不修改 `apps/web/**`，C 端接入由前端按 OpenAPI 更新。
