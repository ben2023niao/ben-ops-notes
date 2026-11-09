---
id: "doc-b4eb3b485278"
title: "Agent 工作日志 · lsj-picker-all-types-fallback"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-picker-all-types-fallback.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-picker-all-types-fallback.md"
sourceSha256: "b7351131d5d12e95e8565a504bb07e455d584535ca7d68b83202b609b69afc1b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-picker-all-types-fallback

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-picker-all-types-fallback.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：LSJ 上游直播选择与预览默认聚合全部分类

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md`
- 需求 ID：LIVE-101
- 设计图：不涉及
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：运营打开 LSJ 上游直播选择器时，默认能看到当前可测试的可播放线路，不被足球分类无直播误导
- 接口/契约：复用 `POST /api/v1/admin/sports-live/search`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`.ai-framework/AGENTS.md`
- 项目 Overlay：不涉及
- 其他：真实 LSJ 查询显示 2026-06-03 当前足球/电竞严格可选为 0，篮球存在可选线路

## 本次目标

1. 修正默认只看足球导致运营误以为没有任何可播源的问题。
2. 让赛事选择器默认聚合足球、篮球、电竞，并把可播放线路排到前面。
3. 同步房间详情直播源预览，避免该入口继续硬编码足球。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/matches/list.vue` | LSJ 选择器默认查询全部类型，按可选线路优先排序，优先使用后端 `can_play` |
| `apps/admin/src/views/rooms/detail.vue` | 直播源预览支持全部/足球/篮球/电竞切换，移除固定足球查询 |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 增加“全部”类型文案 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 增加“All”类型文案 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 增加房间预览类型切换与可播放计数文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 增加房间预览类型切换与可播放计数文案 |
| `docs/agents/logs/2026-06-03-lsj-picker-all-types-fallback.md` | 本次工作日志 |

## 核心决策

1. 不放松“可选择”的业务条件，仍以 `can_play` 或 `status=1 && is_played=1 && 源标识完整` 为准。
2. 默认聚合三类 LSJ 上游，解决某一分类没有直播时的运营误判。
3. 房间详情预览和赛事选择器保持同一类型切换口径。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 第三方直播源选择默认聚合多个上游分类，并按可播放优先展示 |
| 哪些内容只属于当前项目 | LSJ 类型值：足球 1、篮球 18、电竞 151 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用为后台运营选择第三方直播源的交互模式 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 否 |
| 是否降低了 Agent 偷懒空间 | 是，记录了默认足球无源时必须聚合类型验证 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md` |
| OpenAPI / Event / DTO | 不变，复用现有 sports-live search 契约 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 未新增或修改接口字段，只改变后台查询组合和展示 |

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
| 结构化证据 | 不涉及 |
| 是否只是 CRUD | 否，后台运营流程修正 |
| 涉及能力 | 权限安全 |
| 不适用项及原因 | 未涉及资金、数据迁移、异步任务 |
| 当前 MVP 边界 | 后台手动选择 LSJ 上游可播线路 |
| 未来迁移成本 | 如 LSJ 增加类型，可扩展类型选项 |
| 升级触发指标 | 运营需要按联赛、开赛时间、可播线路数做更复杂筛选 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 admin 静态构建产物，不影响 Go 服务入口 |
| 回滚 | 回滚本次 commit 即恢复为单分类查询 |
| 密钥 | 不涉及 `.env.example`、secret、第三方 key |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 默认聚合三类并按可播放优先展示，避免足球无源时无法测试 |
| 红队质疑 | 三个分类并发查询会比单分类多 2 个请求，但只在运营手动打开弹窗时触发，MVP 可接受 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现默认全部分类聚合和房间预览同步，并通过 admin 检查 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| 真实 LSJ search 只读查询 | 足球严格可选 0，篮球严格可选 5，电竞严格可选 0 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `git diff --check` | 通过 |
| `npm run check:completion-claim` | 通过 |
| `npm run check:ai-gates` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无设计图，按后台运营表格与弹窗交互优化 |
| 页面截图 | 未生成 PNG screenshot；已完成构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 弹窗宽度沿用现有约束 |
| 公共组件拆分 | 未新增公共组件 |
| API 接口路径 | `POST /api/v1/admin/sports-live/search` |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 只读查询与表单选择，不新增写操作 |
| 根节点是否挂载 | 赛事管理 LSJ 选择弹窗、直播间详情节目流预览 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未做浏览器运行时截图验证 |
| 与设计图主要偏差 | 无设计图 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 当前聚合三类 LSJ 上游，每次打开弹窗最多触发 3 个查询请求。
2. 上游列表仍可能因实时赛事变化而短时间没有可播放线路。
3. 后续可增加“只看可播放”筛选和按联赛/开赛时间搜索。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 不要再把 LSJ 选择默认固定成足球，否则当前测试期会经常误判无源。
2. 房间详情预览此前硬编码 `status=1,type=1`，本次已移除。
3. `can_play` 是后端给前端的统一可播放判断，前端只保留兼容兜底。
