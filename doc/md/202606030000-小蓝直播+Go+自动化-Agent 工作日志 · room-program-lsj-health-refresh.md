---
id: "doc-eb918af9123c"
title: "Agent 工作日志 · room-program-lsj-health-refresh"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-lsj-health-refresh.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-lsj-health-refresh.md"
sourceSha256: "b88da4a6594ee7f06a1a1cc13d503998d4faa8f2133bbf8cb8374c4d717054cf"
sourceSystem: "project-doc"
---

# Agent 工作日志 · room-program-lsj-health-refresh

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-room-program-lsj-health-refresh.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：修复房间节目流刷新误判 LSJ 源不可播放

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：房间节目流后台查询与 LSJ 源健康校验，不新增接口
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈房间 `22240179938918401` 可直播预览，但刷新后展示 `LSJ 源不可播放: [10006] LSJ 赛事未直播或已结束`

## 本次目标

1. 修复节目流刷新把 LSJ `play` 的 10006 误判为现有节目流失败的问题。
2. 保持开播准备/强制重建仍然严格依赖 `play.main_url`。
3. 清理历史误判残留的节目流失败原因。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 调整房间节目流刷新健康检查：搜索结果线路 `is_played=1` 时视为已存在节目流健康，清理旧错误；只在搜索无法证明可播时走严格 play 校验。 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加 LSJ 状态已结束但线路可播时不应标失败、历史误判 FAILED 可恢复的回归测试。 |
| `docs/agents/logs/2026-06-03-room-program-lsj-health-refresh.md` | 记录本次修复、验证与边界。 |

## 核心决策

1. `SearchLive` 的 `is_played=1` 作为“已有节目流刷新健康检查”的通过条件。
2. `Play` 仍作为“开播准备/强制重建创建 ZEGO 云播放器”的严格条件。
3. 只自动恢复 `LSJ 源不可播放:` 造成的历史误判；`赛事 LSJ 源已变更，请强制重建` 不自动恢复，避免旧云播放器继续被误用。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及契约变更 |
| 不涉及契约的原因 | 只调整后台服务端刷新健康检查策略，接口字段不变 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；不新增 admin 写接口 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 第三方直播源健康检查、状态一致性 |
| 当前 MVP 边界 | 不新增异步探活任务，仍在房间详情刷新时轻量校验 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需部署 go-app 后生效 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 已有 ZEGO 节目流不应因 LSJ `play` 状态口径误差被错误打失败。 |
| 红队质疑 | 如果源实际不可播但搜索还显示 `is_played=1`，刷新会延迟发现；但已有节目流是否真实可看应以 ZEGO/播放器为准，开播准备仍严格校验。 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/liveprogram` | 通过 |
| `go test ./...` | 通过 |

## 风险与待办

1. 后续可增加独立 ZEGO 流状态探测，避免仅依赖 LSJ 搜索口径。
2. 如果运营强制更换 LSJ 源，仍需使用“强制重建”创建新的 ZEGO 云播放器。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 房间详情刷新是健康检查，不负责重新创建 ZEGO 云播放器。
2. 开播准备/强制重建仍然要求 LSJ `play.main_url` 可用。
3. `LSJ 源不可播放:` 的历史误判会在搜索线路可播时被清理，源变更失败不会自动清理。
