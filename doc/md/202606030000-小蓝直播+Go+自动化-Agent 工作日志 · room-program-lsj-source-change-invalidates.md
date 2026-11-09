---
id: "doc-e63c435a4683"
title: "Agent 工作日志 · room-program-lsj-source-change-invalidates"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-lsj-source-change-invalidates.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-lsj-source-change-invalidates.md"
sourceSha256: "0999031c70642e2d06308000170f44971c7fea451cab65b7423171c851db89dd"
sourceSystem: "project-doc"
---

# Agent 工作日志 · room-program-lsj-source-change-invalidates

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20room-program-lsj-source-change-invalidates.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：赛事 LSJ 源变更后让房间节目流刷新可见并提示重建

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md`
- 需求 ID：LIVE-101
- 设计图：不涉及
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：运营在赛事管理改 LSJ 源后，房间详情刷新不能继续表现为旧节目流正常
- 接口/契约：不变
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`.ai-framework/AGENTS.md`
- 项目 Overlay：不涉及
- 其他：用户反馈房间详情刷新后仍看不到赛事管理已换的 LSJ 源变化

## 本次目标

1. 赛事 LSJ 源关键字段变化时，标记使用该源的活动节目流为 `FAILED`。
2. 错误信息明确提示需要在房间节目流中点击“强制重建”。
3. 保持 ZEGO 云播放器不自动热切源，避免后台静默替换运行中流。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 绑定 LSJ 源更新后失效相关活动节目流 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加源关键字段变化判断测试 |
| `docs/agents/logs/2026-06-03-room-program-lsj-source-change-invalidates.md` | 本次工作日志 |

## 核心决策

1. 已创建的 ZEGO 云播放器不会因为赛事源变更自动换 m3u8。
2. 赛事源变更后，活动节目流标记为 `FAILED`，让房间详情刷新后可见。
3. 运营需要点击“强制重建”来结束旧节目流并创建新的 ZEGO 云播放器。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/admin.md` |
| OpenAPI / Event / DTO | 不变 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 响应结构不变，仅更新后端状态同步行为 |

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
| 是否只是 CRUD | 否，直播节目流状态一致性修复 |
| 涉及能力 | 数据一致性 / 可观测性 |
| 不适用项及原因 | 未涉及资金、数据迁移、异步任务 |
| 当前 MVP 边界 | 运营手动强制重建节目流，后端不自动热切 ZEGO 云播放器 |
| 未来迁移成本 | 可扩展为停止旧云播放器或自动重建任务 |
| 升级触发指标 | 运营频繁换源或需要不中断热切流 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 Go 服务 |
| 回滚 | 回滚本次 commit 即恢复源变更不失效活动节目流 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 房间节目流会显示 `FAILED` 和错误信息 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 源变更后不会再让旧节目流看起来正常，刷新即可看到失败提示 |
| 红队质疑 | 只标记 FAILED 不会自动停止 ZEGO 云播放器；这是当前 MVP 的显式人工重建边界 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现 LSJ 源变更后活动节目流失效，并通过测试 |
| 完成裁决 | 待 Reviewer / Owner / QA / CI / Release Manager 裁决 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/liveprogram` | 通过 |
| `go test ./...` | 通过 |
| `git diff --check` | 通过 |
| `npm run check:completion-claim` | 通过 |
| `npm run check:ai-gates` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 不涉及 |
| 页面截图 | 未生成 PNG screenshot；本次为后端状态同步修复 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | 375 x 812 不适用，后台桌面运营页 |
| 桌面/平板视口 | 目标桌面 1440 x 900 |
| 响应式验收 | 不涉及 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | `PUT /api/v1/admin/matches/{id}/lsj-source`、`GET /api/v1/admin/rooms/{id}/program` |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 仍沿用 LSJ 源绑定审计 |
| 根节点是否挂载 | 不涉及 |
| 静态资源是否 200 | 不涉及 |
| console 是否无 error | 不涉及 |
| 与设计图主要偏差 | 无设计图 |
| 合入判断 | 允许合入 |

## 风险与待办

1. 本次只标记节目流失效，不主动停止旧 ZEGO 云播放器。
2. 后续如需要自动重建，应加后台任务和明确审计事件。
3. 如果源只改线路名称也会失效节目流，因为运营看到的线路语义已变化。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `BindMatchLSJSource` 更新已有源时会检查关键字段是否变化。
2. 变化后会把使用该 `source_id` 的活动节目流状态置为 `FAILED`。
3. 房间详情刷新后应提示“赛事 LSJ 源已变更，请在房间节目流点击强制重建”。
