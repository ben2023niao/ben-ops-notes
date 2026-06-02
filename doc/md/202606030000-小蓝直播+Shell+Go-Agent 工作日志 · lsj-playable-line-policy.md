---
id: "doc-72b6f89baad4"
title: "Agent 工作日志 · lsj-playable-line-policy"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "CDN", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-playable-line-policy.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-playable-line-policy.md"
sourceSha256: "5cfa715aeb169867432a5928ad102cde31b890b0c07885cd6a77119cbc9b65cd"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-playable-line-policy

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-lsj-playable-line-policy.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：LSJ 可播放线路口径从赛事状态改为线路播放能力

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md`
- 需求 ID：LIVE-101
- 设计图：不涉及
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：运营可以选择 LSJ 已进流且能获取播放地址的线路用于 ZEGO 云播放器测试，不被 LSJ 赛事状态误拦截
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`.ai-framework/AGENTS.md`
- 项目 Overlay：不涉及
- 其他：真实 LSJ 返回中存在 `status=2` 但 `is_played=1` 且 play 可测试的线路

## 本次目标

1. 取消 `status=1` 作为后台选择 LSJ 线路的硬门槛。
2. 后端 `can_play` 改为按 `is_played=1` 且 `app_name/stream_name` 完整判断。
3. 房间开播准备不因赛事状态非直播直接失败，最终由 LSJ `sportsLive/play` 是否返回 m3u8 裁决。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/lsj/types.go` | `PlayableStreams()` 不再要求赛事状态为 1 |
| `services/go-app/internal/service/streamer/sports_live_source.go` | `can_play` 改为线路播放能力口径 |
| `services/go-app/internal/service/streamer/sports_live_source_test.go` | 增加已结束但已进流线路仍可选测试 |
| `services/go-app/internal/service/liveprogram/service.go` | 开播准备搜索探测不再用赛事状态阻断 play |
| `services/go-app/internal/service/liveprogram/service_test.go` | 更新 LSJ 搜索探测测试 |
| `apps/admin/src/views/matches/list.vue` | 后台 LSJ 选择器去掉赛事状态硬拦截 |
| `docs/api/openapi.yaml` | 同步 `can_play` 契约说明 |
| `packages/contracts/openapi/v1.yaml` | 同步 `can_play` 契约说明 |
| `docs/agents/logs/2026-06-03-lsj-playable-line-policy.md` | 本次工作日志 |

## 核心决策

1. LSJ `status` 保留展示和记录，不作为后台绑定和测试线路的硬门槛。
2. `can_play` 表示“线路已进流且源标识完整”，实际可播放仍以后端调用 `sportsLive/play` 返回 `main_url` 为准。
3. 开播准备继续保留 play 二次校验，避免不可用源进入 ZEGO 云播放器。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 第三方源状态字段不能替代真实播放能力；最终以 play/拉流结果裁决 |
| 哪些内容只属于当前项目 | LSJ `status` 与 `is_played` 字段语义 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用为第三方直播源接入原则 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 增加后端单测覆盖 |
| 是否降低了 Agent 偷懒空间 | 是，测试固定了不再用赛事状态硬拦截 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 已更新契约说明 |

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
| 是否只是 CRUD | 否，直播源可用性判断口径调整 |
| 涉及能力 | CDN / 权限安全 / 可观测性 |
| 不适用项及原因 | 未涉及资金、数据迁移、异步任务 |
| 当前 MVP 边界 | 运营手动选择 LSJ 线路，后端 play 校验后推 ZEGO |
| 未来迁移成本 | 后续可引入后台异步探测并缓存 play 结果 |
| 升级触发指标 | 源列表请求过慢、play 探测频率过高或上游限流 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 Go 服务和 admin 静态构建产物 |
| 回滚 | 回滚本次 commit 即恢复为 status=1 硬拦截 |
| 密钥 | 不涉及 `.env.example`、secret、第三方 key |
| 备份恢复 | 不涉及 |
| 观测 | LSJ 源状态仍会写入现有 source health 字段 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 能拿到更多真实可拉的 m3u8 线路用于 ZEGO 测试，符合当前联调目标 |
| 红队质疑 | 已结束赛事仍可能只是旧回放或 CDN 残留，因此开播准备必须保留 play 校验；C 端正式上线前应再评估是否需要只看 live |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现按线路播放能力判断，并通过后端、前端、契约检查 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/infra/live/lsj ./internal/service/streamer ./internal/service/liveprogram` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无设计图，按后台运营表格交互调整 |
| 页面截图 | 未生成 PNG screenshot；已完成构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 未改变布局结构 |
| 公共组件拆分 | 未新增公共组件 |
| API 接口路径 | `GET /api/v1/admin/sports-live`、`POST /api/v1/admin/sports-live/play` |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 只读查询与表单选择，不新增写操作 |
| 根节点是否挂载 | 赛事管理 LSJ 选择弹窗 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未做浏览器运行时截图验证 |
| 与设计图主要偏差 | 无设计图 |
| 合入判断 | 允许合入 |

## 风险与待办

1. `status=2` 的线路可能是旧赛事残留；当前允许是为了 ZEGO 联调拿到真实 m3u8。
2. 正式运营前建议增加“只看直播中”筛选开关，而不是恢复硬拦截。
3. 若 LSJ play 对旧源限流或不稳定，需要增加后端异步探测缓存。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `can_play` 现在不代表赛事直播中，只代表线路可用于 play 尝试。
2. 开播准备最终仍依赖 `sportsLive/play` 返回 m3u8。
3. 前端展示的 LSJ 赛事状态只是参考，不能再作为选择禁用条件。
