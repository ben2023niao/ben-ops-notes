---
id: "doc-3f8a7208b706"
title: "Agent 工作日志 · admin-room-lsj-source-preview"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-lsj-source-preview.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-room-lsj-source-preview.md"
sourceSha256: "2ff25f6eb671867bbf9e8edef67f2fe5f191f882d9a73bfd6b4dea952b5de897"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-room-lsj-source-preview

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-room-lsj-source-preview.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：后台房间管控页增加 LSJ 直播源参数查看、清晰度线路查看与 m3u8 预览播放

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 设计图：无独立设计图，按现有后台 Element Plus/Vben 页面模式扩展
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：在房间管控页「节目流」区域增加只读诊断入口，不改变开播准备主流程
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：Stoplight operation `adminSportsLivePlay`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：不涉及
- 其他：后台页面 URL `/rooms/:id`

## 本次目标

1. 后台支持通过 LSJ `app_name` + `stream_name` 获取真实 m3u8 播放地址。
2. 房间管控页展示当前节目流绑定的 LSJ 源参数、可选线路/清晰度、推送到 ZEGO 的输入线路。
3. 后台页面支持直接预览 LSJ m3u8，便于确认上游源质量和 ZEGO 云播放器输入质量。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/adminapi/sports_live_source.go` | 增加后台 LSJ play handler |
| `services/go-app/internal/http/router/admin.go` | 注册 `POST /api/v1/admin/sports-live/play` |
| `docs/api/openapi.yaml` | 增加 `adminSportsLivePlay` 契约 |
| `packages/contracts/openapi/v1.yaml` | 同步 OpenAPI 契约 |
| `apps/admin/src/api/modules/match.ts` | 增加后台 sportsLivePlay API client |
| `apps/admin/src/views/rooms/detail.vue` | 增加节目流源预览弹窗和 HLS 播放器 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 增加中文文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 增加英文文案 |
| `apps/admin/package.json`、`pnpm-lock.yaml` | admin 显式依赖 `hls.js` |

## 核心决策

1. 后台 m3u8 预览走后端 `POST /api/v1/admin/sports-live/play`，不允许页面手填或绕过 LSJ 协议。
2. “推送到 ZEGO 的清晰度”按当前节目流绑定的 LSJ 线路展示；ZEGO 云播放器输入就是该线路生成的 `match_stream_id`。
3. Chrome 不能原生稳定播放 HLS，后台引入 `hls.js` 做预览播放；同时保留主/备 m3u8 复制能力。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 后台第三方直播源预览与诊断模式 |
| 哪些内容只属于当前项目 | LSJ 字段、ZEGO 节目流关系 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用接口契约和后台诊断入口模式 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 否，复用现有 OpenAPI/Contract/typecheck/build |
| 是否降低了 Agent 偷懒空间 | 是，页面直接展示真实 LSJ play 状态与 m3u8 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | `adminSportsLivePlay` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 已更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | `docs/qa/architecture-capability-evidence.json` |
| 是否只是 CRUD | 否 |
| 涉及能力 | 第三方依赖、直播源诊断、权限安全 |
| 不适用项及原因 | 不涉及资金、数据库迁移 |
| 当前 MVP 边界 | 仅后台诊断预览，不做录制/转码质量分析 |
| 未来迁移成本 | 后续可增加 ZEGO 云播放器查询质量接口 |
| 升级触发指标 | 运营需要多源、多清晰度自动切换 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 admin 前端构建产物和 go-app 路由 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不新增密钥，继续使用既有 LSJ env |
| 备份恢复 | 不涉及 |
| 观测 | 不新增指标 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台 play 接口复用既有 LSJ service，页面展示当前绑定线路和可选线路 |
| 红队质疑 | 仅靠前端播放无法证明 ZEGO 输出清晰度；当前只能证明 ZEGO 输入源线路，后续如需输出质量需接 ZEGO 查询能力 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并完成本地验证 |
| 完成裁决 | 等 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/http/adminapi ./services/go-app/internal/service/streamer` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `git diff --check` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无独立设计图，沿用后台房间管控页风格 |
| 页面截图 | 未生成 PNG screenshot；已完成 `pnpm --filter @kickoff/admin build:prod` 生产构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页，不作为 C 端手机页面验收 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 弹窗宽度 980px，表格支持溢出提示 |
| 公共组件拆分 | 变更局限于房间详情页 |
| API 接口路径 | `POST /api/v1/admin/sports-live/play` |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不使用 mock，接口依赖真实 LSJ 配置 |
| 后台权限与审计 | 继承 adminBearer 和后台权限中间件；只读诊断接口不写审计 |
| 根节点是否挂载 | 页面既有路由 `/rooms/:id` |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未做浏览器运行时截图验证 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 当前展示的是 ZEGO 云播放器输入线路，不是 ZEGO 输出端码率/分辨率探测。
2. LSJ 上游列表按足球 type=1/status=1 查询，非足球赛事后续需要后台按赛事类型透传。
3. 若 LSJ m3u8 跨域策略变化，浏览器预览可能失败，但 m3u8 复制仍可用于外部播放器验证。

## 交接说明

1. 前端可在房间管控页节目流区域点击「直播源预览」检查 LSJ 可选线路。
2. 新接口文档深链：`https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminSportsLivePlay`。
3. 运营看到的 ZEGO 推流清晰度应理解为当前绑定 LSJ 线路被推成 `match_stream_id`。
