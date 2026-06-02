---
id: "doc-a7bb2e3e65e4"
title: "admin-room-control-cleanup"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-control-cleanup.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-control-cleanup.md"
sourceSha256: "1fbec13be8ddb146036875fafcc358d702769afeab75702e21f1769ac3617187"
sourceSystem: "project-doc"
---

# admin-room-control-cleanup

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-control-cleanup.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：直播间详情页从 OBS 监控口径收敛为管控页

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（本项目 admin PRD；门禁别名 `docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 接口/契约：`packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`
- 团队可读文档：`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户指出直播间详情页仍有 OBS 推流凭据、监控旧口径，并质疑强制开播和封禁是否仍有意义。

## 本次目标

1. 移除后台房间详情页 OBS 推流凭据展示、查看、轮换入口。
2. 将后台列表入口从“监控”改为“管控”，避免和 OBS 推流监控混淆。
3. 保留强切开播/下播和封禁，但用文案明确它们只是状态/会话兜底，不负责 ZEGO 推流。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/list.vue` | 移除推流码列，入口文案改为管控 |
| `apps/admin/src/views/rooms/detail.vue` | 删除 OBS 推流凭据卡片和相关状态/调用，增加状态强切说明 |
| `apps/admin/src/api/modules/room.ts` | 移除后台包里不再使用的 stream-key API client 方法 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 更新中文运营文案，删除 OBS 推流凭据文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 更新英文文案，删除 OBS 推流凭据文案 |

## 核心决策

1. 当前直播方案为 LSJ -> ZEGO 云播放器 -> match_stream_id，主播 Web SDK 推 host_stream_id；后台不再展示 OBS/SRS 推流凭据。
2. 强切开播/下播保留：后端会更新房间状态、创建/结束后台 session，影响 C 端 LIVE 状态下的互动接口，属于兜底操作。
3. 封禁保留：封禁状态仍会阻断房间展示与互动，是运营风控动作。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（admin 门禁别名：`docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | 本次未改接口契约；现有契约在 `packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 本次只清理后台 UI 和 API client 调用，不变更后端接口行为 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；强切/封禁仍沿用原 admin API 权限与审计链路 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，清理后台直播管控边界 |
| 涉及能力 | 权限安全 / 直播状态管控 |
| 当前 MVP 边界 | 不删除后端 stream-key 历史接口，避免影响 SRS 历史链路；后台页面不再暴露 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 仅后台前端包变化 |
| 回滚 | 回滚本次 commit 可恢复旧入口 |
| 密钥 | 不涉及 `.env` 或第三方密钥 |
| 备份恢复 | 不影响数据库 |
| 观测 | 不新增日志/指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台房间页已无 OBS/推流凭据入口；强切/封禁文案解释清楚其状态边界。 |
| 红队质疑 | 如果删除强切会导致状态卡死时没有兜底；因此保留但降级为状态强切说明。 |
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
| `python3 -m json.tool apps/admin/src/locales/langs/zh-CN/room.json >/dev/null && python3 -m json.tool apps/admin/src/locales/langs/en-US/room.json >/dev/null` | 通过 |
| `rg -n "streamKey|stream-key|OBS|推流码|推流凭据|keyState|rotateStreamKey|revealKey" apps/admin/src/views/rooms apps/admin/src/locales/langs/zh-CN/room.json apps/admin/src/locales/langs/en-US/room.json apps/admin/src/api/modules/room.ts` | 无匹配 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户截图：后台直播间详情页 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 后台桌面管控页，目标视口 1440x900；无独立设计稿尺寸 |
| 页面截图 | 本次未生成新的 `.png`；后台页面沿用现有 Vben/Element Plus 布局，已通过 typecheck / build 验证，截图证据目录为 `docs/qa/screenshots/` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375x812 手机视口不适用，本页面为后台管理桌面运营入口；未修改 C 端/H5 页面 |
| 桌面/平板视口 | 后台管理桌面管控页 |
| 响应式验收 | 不涉及移动端 |
| 公共组件拆分 | 不新增公共组件 |
| API 接口路径 | `POST /api/v1/admin/rooms/{id}/force-start`、`POST /api/v1/admin/rooms/{id}/force-end`、`POST /api/v1/admin/rooms/{id}/ban`、`POST /api/v1/admin/rooms/{id}/unban` |
| SEO异常验证/meta 范围 | 不涉及，后台管理页不面向搜索引擎和分享落地页 |
| mock/fallback 状态与原因 | 不涉及 mock |
| 后台权限与审计 | 沿用现有后台权限与审计；admin API ownerService 为 `services/go-app` |
| 根节点是否挂载 | 未改路由挂载 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未启动浏览器，typecheck/build 无错误 |
| 与设计图主要偏差 | 删除旧 OBS 推流凭据卡片，入口从监控改为管控 |
| 合入判断 | 允许合入，等待 Reviewer / Owner / QA 裁决 |

## 风险与待办

1. 后端 stream-key 历史接口仍保留，后续如确认 SRS/OBS 链路彻底下线，可另起任务做接口契约废弃。
2. “状态强切”不等于 ZEGO 推流，运营需要优先使用「节目流 / 开播准备」。
3. 弹幕 tab 保留“弹幕监控”文案，因为它确实用于查看和处理弹幕。

## 交接说明

1. 后台直播间详情页现在是管控页，不再提供 OBS 推流参数。
2. ZEGO 节目流操作集中在「节目流」模块。
3. 强切/封禁属于后台状态和运营风控兜底。
