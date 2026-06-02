---
id: "doc-12d2304123ee"
title: "Agent 工作日志 · program-zego-health-sync"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-program-zego-health-sync.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-program-zego-health-sync.md"
sourceSha256: "039cf47258b661394d401c870dccd6e3ae11ed750ca72950c9d3bc73e0354e25"
sourceSystem: "project-doc"
---

# Agent 工作日志 · program-zego-health-sync

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-program-zego-health-sync.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：节目流查询同步 ZEGO 云播放器失败状态

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：`GET /api/v1/admin/rooms/{id}/program`、`GET /api/v1/streamer/rooms/{room_id}/program`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 修复后台显示 `MATCH_STREAM_READY`，但主播端因 ZEGO 云播放器已销毁拿不到 `match_stream_id` 的状态不一致。
2. admin / streamer 查询节目流时同步 ZEGO 云播放器健康状态。
3. 当 ZEGO `Status=6/7/8` 时，节目流状态更新为 `FAILED` 并写入明确错误原因。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 增加 ZEGO 健康同步，失败时落库为 FAILED |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加 ZEGO Destroyed 标记失败与恢复清错单测 |
| `docs/agents/logs/2026-06-03-program-zego-health-sync.md` | 本次工作记录 |

## 核心决策

1. `MATCH_STREAM_READY` 不能只代表历史创建成功，查询时必须用 ZEGO 实时状态校正。
2. ZEGO 不可播错误前缀统一为 `ZEGO 云播放器不可播放:`，与 LSJ 错误前缀分离。
3. 后台刷新、主播端轮询都会触发同一套状态同步，避免两边显示不一致。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 本次不改契约字段，仅修正状态同步行为 |
| 验收口径 | ZEGO Player Destroyed/Ended/ConnectFailed 后，节目流状态返回 FAILED |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方依赖状态同步 / 可观测性 |
| 当前 MVP 边界 | 查询时同步状态，不新增后台 worker 定时巡检 |
| 高风险触发项 | 直播链路 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需部署 go-app 后生效 |
| 密钥 | 使用已有 ZEGO ServerSecret，仅后端调用 |
| 观测 | 失败状态会进入 DB `error_message`，日志沿用现有 ZEGO event_type |
| 回滚 | 回滚本次代码即可恢复旧查询行为 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台和主播端状态不再割裂 |
| 红队质疑 | 查询时调第三方存在延迟；MVP 可接受，后续可加短 TTL 缓存或 worker |
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
| `npm run check:completion-claim` | 通过 |
| `npm run check:ai-gates` | 通过 |
