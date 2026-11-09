---
id: "doc-c1962c8bb4cf"
title: "admin-room-cover-upload"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "CDN", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-cover-upload.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-cover-upload.md"
sourceSha256: "2c4c4126a1f7f027210f1df13638a355f49d3f9c8ae90f43ca428b3e4be34961"
sourceSystem: "project-doc"
---

# admin-room-cover-upload

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BCDN-admin-room-cover-upload.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：后台直播间封面改为上传并补齐前端消费契约

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（本项目 admin PRD；门禁别名 `docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈后台新建直播间不能让运营手填封面链接，封面需要走已实现上传系统，并且 API 回调/返回需要有封面字段。

## 本次目标

1. 后台直播间创建弹窗将封面从手填 URL 改为上传。
2. 创建直播间请求继续携带可选 `cover_url`，未上传时允许为空。
3. 后端 admin / C 端 / 主播端相关 room 契约明确封面字段消费路径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/list.vue` | 新建直播间弹窗增加封面上传、预览和校验，移除手填封面链接输入 |
| `apps/admin/src/api/modules/room.ts` | AdminRoomItem 补 `cover_url` 类型 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 新增封面上传中文文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 新增封面上传英文文案 |
| `services/go-app/internal/dto/admin_modules.go` | AdminRoomItem 返回 `cover_url` |
| `services/go-app/internal/service/admin/room.go` | admin room DTO 映射 `cover_url` |
| `services/go-app/internal/dto/live.go` | C 端直播间详情增加 `cover_url` |
| `services/go-app/internal/service/live/service.go` | C 端详情同时返回 `cover_url` / `thumb_url` |
| `services/go-app/internal/service/admin/room_test.go` | 覆盖 admin room DTO 封面映射 |
| `services/go-app/internal/service/live/service_test.go` | 覆盖 C 端详情封面映射 |
| `docs/api/openapi.yaml` | LiveRoom schema 补 `cover_url` |
| `packages/contracts/openapi/v1.yaml` | contracts 同步 LiveRoom `cover_url` |

## 核心决策

1. 上传入口复用现有 `POST /api/v1/admin/upload`，scene 使用 `room_cover`。
2. 数据字段仍统一使用 `live_rooms.cover_url`，`thumb_url` 仅作为 C 端卡片/详情兼容别名。
3. 封面可为空；后台未上传时不传 `cover_url`，不阻断建房。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（admin 门禁别名：`docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/*` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 已涉及并更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及，复用已有 `live_rooms.cover_url` |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；上传和建房沿用现有后台接口 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，涉及后台配置到 C 端/主播端消费契约 |
| 涉及能力 | CDN / 对象存储上传 / 权限安全 |
| 当前 MVP 边界 | 封面只上传和回显，不新增裁剪、压缩或多尺寸派生 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 仅前后端代码和 OpenAPI 文档变化，不新增服务入口 |
| 回滚 | 回滚本次 commit 即可恢复为手填链接 |
| 密钥 | 不涉及 `.env` 或第三方密钥 |
| 备份恢复 | 不影响数据库结构 |
| 观测 | 不新增日志/指标 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并提交验证命令结果，等待 Reviewer / Owner / QA 裁决 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台运营不再手填封面链接，上传 scene 复用现有 `room_cover`；后端 admin / C 端详情均补齐 `cover_url`。 |
| 红队质疑 | 若 C 端只读 `thumb_url`，是否会断？结论：不会，`thumb_url` 仍继续由 `cover_url` 映射。 |
| 合入判断 | 允许合入，等待 Reviewer / Owner / QA 最终裁决。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/service/live ./services/go-app/internal/service/home ./services/go-app/internal/service/streamer` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图：后台新建直播间弹窗 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 后台桌面弹窗，目标视口 1440x900；无独立设计稿尺寸 |
| 页面截图 | 本次未生成新的 `.png`；后台弹窗沿用现有 Vben/Element Plus 结构，已通过 typecheck / build 验证，截图证据目录为 `docs/qa/screenshots/` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 桌面/平板视口 | 后台管理桌面弹窗 |
| 真实手机视口 | 375x812 手机视口不适用，本页面为后台管理桌面运营入口；未修改 C 端/H5 页面 |
| 响应式验收 | 不涉及移动端 |
| API 接口路径 | `POST /api/v1/admin/upload`、`POST /api/v1/admin/rooms`、`GET /api/v1/live/rooms/{room_id}`、主播端房间列表 |
| SEO异常验证/meta 范围 | 不涉及，后台管理弹窗不面向搜索引擎和分享落地页 |
| 后台权限与审计 | 沿用现有后台上传和建房权限；admin API ownerService 为 `services/go-app` |
| 与设计图主要偏差 | 将手填封面链接改为上传按钮 + 预览 |
| 合入判断 | 允许合入，等待 Reviewer / Owner / QA 裁决 |

## 风险与待办

1. 上传后不做图片裁剪，多尺寸封面可后续按 CDN/对象存储策略扩展。
2. 如果前端 C 端只读取 `thumb_url`，当前仍保持兼容；如果读取 `cover_url`，本次已补齐。
3. 主播端已通过 `cover_url` 房间字段消费；后台创建封面与主播端修改房间封面写同一字段。

## 交接说明

1. 后台运营创建直播间时不再手填封面 URL，只上传图片。
2. `cover_url` 是源字段，`thumb_url` 是兼容别名。
3. C 端直播间卡片/详情、主播端房间资料都应使用该封面字段。
