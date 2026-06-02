---
id: "doc-0c1327b39c6f"
title: "lsj-program-health-check"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-program-health-check.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-program-health-check.md"
sourceSha256: "04aef9dbfdbafb731df196ea4b1a5f4c8bc61bd36f5746716607cf5fdbfff71b"
sourceSystem: "project-doc"
---

# lsj-program-health-check

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-program-health-check.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：节目流刷新校验 LSJ 上游可播状态

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（本项目 admin PRD；门禁别名 `docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户指出节目流已准备后，如果 LSJ 源失效或没有直播，后台不能只显示本地 `MATCH_STREAM_READY`。

## 本次目标

1. `prepare-live` 调 LSJ play 成功/失败都写回 `match_lsj_sources.status/is_played/last_checked_at`。
2. 后台管控页刷新节目流时重新探测 LSJ play；不可播则把节目流标记为 `FAILED` 并返回失败原因。
3. 管控页展示 LSJ 赛事状态、线路状态、检查时间和失败原因。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 新增 LSJ play 探测、源状态回写、刷新节目流健康检查 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 覆盖 LSJ play 探测分类和错误截断 |
| `apps/admin/src/api/modules/room.ts` | RoomProgramSession 类型补 `error_message` |
| `apps/admin/src/views/rooms/detail.vue` | 展示 LSJ 状态/is_played/检查时间/失败原因 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 新增 LSJ 健康状态中文文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 新增 LSJ 健康状态英文文案 |

## 核心决策

1. LSJ `sportsLive/play` 是当前唯一真实可播探测点；绑定时保存的状态只能作为初始参考。
2. `MATCH_STREAM_READY` 不是永久状态，后台刷新会复查 LSJ；复查失败后本地节目流转 `FAILED`。
3. 主播端接口不主动刷 LSJ，避免高频外部调用；后台管控页刷新承担运营校验职责。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（admin 门禁别名：`docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` 已有 `source.status/is_played/last_checked_at_ms/error_message` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 本次使用既有契约字段，仅补实现与展示 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 migration，复用 `match_lsj_sources` 和 `room_program_sessions.error_message/status` |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；prepare-live 审计保持原逻辑 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，涉及第三方直播源健康状态与后台管控 |
| 涉及能力 | 第三方依赖 / 可观测性 / 直播状态一致性 |
| 当前 MVP 边界 | 仅在 prepare-live 和后台刷新时探测 LSJ，不做后台定时巡检 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 需要部署 go-app 和 admin 前端 |
| 回滚 | 回滚本次 commit 即恢复为只读本地节目流状态 |
| 密钥 | 不涉及 `.env` 或第三方密钥 |
| 备份恢复 | 不影响数据库结构 |
| 观测 | 增加可见的 LSJ 检查时间和失败原因 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | `MATCH_STREAM_READY` 后刷新会重新校验 LSJ play，不会继续只展示本地缓存状态。 |
| 红队质疑 | LSJ play 短暂失败可能把节目流标 FAILED；运营可用「强制重建」重新创建云播放器。 |
| 合入判断 | 允许合入，等待 Reviewer / Owner / QA 最终裁决。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并提交验证命令结果，等待 Reviewer / Owner / QA 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/liveprogram` | 通过 |
| `go test ./services/go-app/internal/service/liveprogram ./services/go-app/internal/http/adminapi ./services/go-app/internal/http/streamerapi` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图：后台直播间管控页节目流区 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 后台桌面管控页，目标视口 1440x900；无独立设计稿尺寸 |
| 页面截图 | 本次未生成新的 `.png`；已通过 typecheck / build 验证，截图证据目录为 `docs/qa/screenshots/` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375x812 手机视口不适用，本页面为后台管理桌面运营入口；未修改 C 端/H5 页面 |
| 桌面/平板视口 | 后台管理桌面管控页 |
| 响应式验收 | 不涉及移动端 |
| 公共组件拆分 | 不新增公共组件 |
| API 接口路径 | `GET /api/v1/admin/rooms/{id}/program`、`POST /api/v1/admin/rooms/{id}/prepare-live` |
| SEO异常验证/meta 范围 | 不涉及，后台管理页不面向搜索引擎和分享落地页 |
| mock/fallback 状态与原因 | 不涉及 mock |
| 后台权限与审计 | 沿用现有后台权限；admin API ownerService 为 `services/go-app` |
| 根节点是否挂载 | 未改路由挂载 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未启动浏览器，typecheck/build 无错误 |
| 与设计图主要偏差 | 新增 LSJ 状态、线路状态、检查时间、失败原因展示 |
| 合入判断 | 允许合入，等待 Reviewer / Owner / QA 裁决 |

## 风险与待办

1. 当前不是定时巡检；只有 prepare-live 和后台刷新时会探测 LSJ。
2. `FAILED` 后如果 LSJ 恢复，运营需要点「强制重建」重新创建云播放器。
3. 后续可增加后台列表角标或定时任务，但这超出本次 MVP 修复范围。

## 交接说明

1. 后台节目流刷新现在会真实调用 LSJ play。
2. LSJ 不可播时节目流显示 `FAILED`，并展示失败原因。
3. 主播端仍以 `streamerRoomProgram` 返回状态为准，前端不应在 `FAILED` 时继续混流。
