---
id: "doc-7b108661d771"
title: "Agent 工作日志 · hide-legacy-live-lines-entry"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "CDN", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-hide-legacy-live-lines-entry.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-hide-legacy-live-lines-entry.md"
sourceSha256: "dbbed3c22cd27d9ec6fa192adb77c7bdcdbade33a41da856e39fb8ca7657694b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · hide-legacy-live-lines-entry

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20hide-legacy-live-lines-entry.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：访问策略验证后台旧 CDN 直播线路入口

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`）
- 需求 ID：ADM-912 / LIVE-101
- 设计图：无
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：只访问策略验证旧入口，不新增页面
- 接口/契约：不改契约，旧接口保留
- 团队可读文档：`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：不涉及
- 其他：ZEGO 主链路已替代旧 CDN 线路配置

## 本次目标

1. 后台菜单和路由不再暴露「直播线路」旧入口。
2. 保留旧页面和接口代码，避免破坏历史数据和未来恢复能力。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/router/routes/modules/contents.ts` | 注释访问策略验证 `/live-lines` 路由入口 |

## 核心决策

1. LIVE-101 后 C 端拉流统一走 ZegoCloud SDK，旧 `live_lines` 不参与当前播放链路。
2. 仅访问策略验证入口，不删除 API / migration / DTO，降低回滚风险。
3. ZEGO 的线路/质量能力不等同于后台手动维护每房间 CDN 地址。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 |
| 哪些内容可复用到下一个项目 | 废弃功能先隐藏入口、保留代码的过渡方式 |
| 哪些内容只属于当前项目 | live_lines 与 ZEGO 主链路切换 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可作为功能下线过渡模式 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 否 |
| 是否降低了 Agent 偷懒空间 | 是，避免运营误用旧入口 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-912 / LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（后台模块；兼容门禁引用 `docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | 不改契约 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 仅访问策略验证后台入口，接口暂保留兼容 |

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
| 涉及能力 | 直播链路、后台运营入口 |
| 不适用项及原因 | 不涉及资金、数据库、第三方密钥 |
| 当前 MVP 边界 | 只访问策略验证入口，不清理旧表和旧接口 |
| 未来迁移成本 | 后续确认完全废弃后可删接口和 migration 依赖 |
| 升级触发指标 | 需要重新支持自建 CDN 线路时恢复 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 admin 前端构建产物 |
| 回滚 | 回滚本次 commit 即可恢复入口 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 路由入口已注释，旧页面不会出现在菜单和直接路由中 |
| 红队质疑 | 旧 API 仍存在，若有人直接调用仍可用；这是有意保留兼容而不是彻底下线 |
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
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `git diff --check` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 无独立设计图 |
| 页面截图 | 未生成 PNG screenshot；本次为访问策略验证菜单/路由入口，已完成生产构建验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 不涉及 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | 不改接口 |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 入口访问策略验证，不改变权限 |
| 根节点是否挂载 | `/live-lines` 路由已访问策略验证 |
| 静态资源是否 200 | 生产构建通过 |
| console 是否无 error | 未做浏览器运行时截图验证 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 旧 admin/public live-lines API 仍保留，后续确认完全废弃后再做契约下线。
2. 如前端仍有旧 C 端线路 UI，需要同步告知其只是展示/统计，不影响 ZEGO 播放。
3. 如未来需要 ZEGO 输出侧质量选择，应按 ZEGO 转码/双流能力重新设计，不复用旧 CDN edge_url。

## 交接说明

1. 后台左侧「内容管理 / 直播线路」已访问策略验证。
2. 当前体育直播主链路以 LSJ 源线路 + ZEGO 云播放器/混流为准。
3. 旧 `live_lines` 表和接口暂时保留兼容。
