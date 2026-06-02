---
id: "doc-7e95d91047cb"
title: "Agent 工作日志 · lsj-ended-source-status-fix"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-ended-source-status-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-ended-source-status-fix.md"
sourceSha256: "9b03cab0fae28ba9812c224b9fb1c7acec0a224451beae02dd2e2a30df87e39e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-ended-source-status-fix

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-ended-source-status-fix.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：修复 LSJ 已结束赛事仍显示直播中/可播放的问题

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`）
- 需求 ID：LIVE-101
- 设计图：无
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：后台状态标签必须区分 LSJ 赛事状态和线路播放状态
- 接口/契约：不改契约，修正既有字段语义
- 团队可读文档：`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：不涉及
- 其他：用户截图显示 LSJ 已结束赛事仍被误判为可播放

## 本次目标

1. 后端刷新节目流时先检查 LSJ 上游赛事状态，已结束或未开始不得继续当作可播放源。
2. 保持 `status` 表示 LSJ 赛事状态，`is_played` 表示有效线路播放状态。
3. 后台赛事 LSJ 选择器禁止选择已结束/未开始赛事的线路。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 先调用 LSJ search 校验赛事状态，再 play 校验 m3u8 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加已结束赛事仍有 is_played=1 时不可播放的回归测试 |
| `apps/admin/src/views/matches/list.vue` | LSJ 选择按钮同时校验赛事直播中和线路已进流 |
| `apps/admin/src/views/rooms/detail.vue` | 房间节目流展示 LSJ 未开始/已结束状态 |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 更新选择器提示与状态文案 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 更新英文文案 |
| `apps/admin/src/locales/langs/zh-CN/room.json` | 增加 LSJ 未开始/已结束文案 |
| `apps/admin/src/locales/langs/en-US/room.json` | 增加英文文案 |

## 核心决策

1. `match_lsj_sources.status` 不再由 `sportsLive/play` 成功与否覆盖为 1；它应来自 LSJ `sportsLive/search` 的赛事状态。
2. `is_played` 存有效播放状态：只有赛事 `status=1` 且线路 `is_played=1` 且 play 返回主 m3u8 时才为 1。
3. LSJ search 暂按足球 type=1 查询；后续如果支持篮球/电竞，需要把赛事类型落库或从房间/赛事配置传入。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 第三方源状态与播放能力分离的建模方式 |
| 哪些内容只属于当前项目 | LSJ 状态码和 ZEGO 节目流关系 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用到第三方直播源接入 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 增加 service 回归测试 |
| 是否降低了 Agent 偷懒空间 | 是，防止只用 play 探测冒充赛事状态 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | 不改契约 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 字段语义修正，响应字段未变化 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 既有 `match_lsj_sources.status/is_played` |
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
| 涉及能力 | 第三方依赖、直播链路一致性 |
| 不适用项及原因 | 不涉及资金、数据库迁移 |
| 当前 MVP 边界 | 只按足球源修正；多体育类型后续扩展 |
| 未来迁移成本 | 需要给 LSJ source 增加 sports type 字段 |
| 升级触发指标 | 篮球/电竞源进入正式运营 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 go-app 和 admin 前端构建产物 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 已结束赛事即使 line.is_played=1 也会被判定为不可播放 |
| 红队质疑 | search 查询失败时仍会 fallback play，不会更新赛事状态；这是为了避免 LSJ search 短暂故障误杀正在直播 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并本地验证 |
| 完成裁决 | 等 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./services/go-app/internal/service/liveprogram ./services/go-app/internal/service/streamer` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `git diff --check` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无独立设计图 |
| 页面截图 | 未生成 PNG screenshot；已完成生产构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 不涉及 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | 不改接口 |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 不改变权限 |
| 根节点是否挂载 | 既有赛事列表和房间管控页 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未做浏览器运行时截图验证 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 当前 LSJ search 按足球 type=1 查询，后续多品类需扩展来源类型。
2. 已经被错误标成直播中的历史数据，需要刷新节目流或重新开播准备后修正。
3. 若 LSJ search 返回延迟但 play 仍可用，本次保留 fallback，避免误杀。

## 交接说明

1. 房间管控页点击「刷新」会触发后端重新校验 LSJ search + play。
2. 已结束赛事应显示 LSJ 赛事状态“已结束”，线路状态“不可播放”，节目流状态会被标为 FAILED。
3. 赛事列表选择 LSJ 源时，已结束/未开始赛事的线路按钮会禁用。
