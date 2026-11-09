---
id: "doc-31556fbccf38"
title: "Agent 工作日志 · lsj-picker-live-type-filter"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-picker-live-type-filter.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-picker-live-type-filter.md"
sourceSha256: "7665ccd24485de0c1217beaddc00a93f7d84605836e6cc009fe403044cf71ffb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-picker-live-type-filter

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-picker-live-type-filter.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：LSJ 上游直播选择器增加赛事类型切换与可选线路计数

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md`
- 需求 ID：LIVE-101
- 设计图：不涉及
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：后台运营在选择 LSJ 上游直播时能切换足球、篮球、电竞，并直接看到当前可选线路数量
- 接口/契约：复用 `POST /api/v1/admin/sports-live/search`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`.ai-framework/AGENTS.md`
- 项目 Overlay：不涉及
- 其他：真实 LSJ search 结果显示 2026-06-03 当前足球无可选线路，篮球存在可选线路

## 本次目标

1. 修正后台只查询 LSJ 足球导致运营看不到可播源的问题。
2. 保持选择规则：只有上游赛事直播中且线路已进流时才允许绑定。
3. 同步中英文文案并完成 admin 构建验证。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/matches/list.vue` | LSJ 选择弹窗增加足球、篮球、电竞切换，并显示当前可选线路数量 |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 更新中文说明与类型文案 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 更新英文说明与类型文案 |
| `docs/agents/logs/2026-06-03-lsj-picker-live-type-filter.md` | 本次工作日志 |

## 核心决策

1. 不放宽可选条件，仍要求 `status=1` 且线路 `is_played=1` 且源标识完整。
2. 将 LSJ 的 `type` 暴露为运营可切换选项，避免只查足球时误判“没有任何可播源”。
3. 只改后台管理界面，不改 OpenAPI 和后端接口。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 第三方直播源选择器需要展示上游分类和可用性计数 |
| 哪些内容只属于当前项目 | LSJ 类型值：足球 1、篮球 18、电竞 151 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可作为后台运营选择第三方直播源的通用交互模式 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 否 |
| 是否降低了 Agent 偷懒空间 | 是，日志记录了真实上游分类差异，避免再次只查足球 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md` |
| OpenAPI / Event / DTO | 不变，复用现有 sports-live search 契约 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 未新增或修改接口字段，只改变后台请求参数入口 |

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
| 当前 MVP 边界 | 后台可手动选择 LSJ 上游分类与可播线路 |
| 未来迁移成本 | 如 LSJ 增加类型，可扩展类型选项 |
| 升级触发指标 | 运营需要更多上游分类或自动推荐可播线路 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 admin 静态构建产物，不影响 Go 服务入口 |
| 回滚 | 回滚本次 commit 即恢复为只查足球 |
| 密钥 | 不涉及 `.env.example`、secret、第三方 key |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 已保留严格可选条件，避免绑定已结束但 CDN 还可拉的旧 HLS |
| 红队质疑 | 如果上游当天只有篮球可播，只查足球会让运营误判系统不可用 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现后台类型切换和可选线路计数，并通过 admin 检查 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `git diff --check` | 通过 |
| `npm run check:completion-claim` | 通过 |
| `npm run check:ai-gates` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无设计图，按后台运营表格交互优化 |
| 页面截图 | 未生成 PNG screenshot；已完成构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 弹窗宽度继续使用 `min(1080px, calc(100vw - 32px))` |
| 公共组件拆分 | 未新增公共组件 |
| API 接口路径 | `POST /api/v1/admin/sports-live/search` |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 只读查询与表单选择，不新增写操作 |
| 根节点是否挂载 | 是，位于赛事管理页 LSJ 选择弹窗 |
| 静态资源是否 200 | 构建通过，待部署验证 |
| console 是否无 error | 构建阶段未发现错误 |
| 与设计图主要偏差 | 无设计图 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 当前只暴露 LSJ 文档中已知类型：足球、篮球、电竞。
2. 上游 `is_played=1` 但 `status!=1` 的旧源仍会被拦截，这是有意行为。
3. 部署后需要运营在弹窗切到篮球验证真实可选线路。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 2026-06-03 真实 LSJ 足球列表没有可选线路，篮球列表有可选线路。
2. 若后续要自动推荐源，可以在后台默认查询多个类型并合并展示。
3. 房间开播准备仍会再次调用 play 校验，前端选择只是第一道筛选。
