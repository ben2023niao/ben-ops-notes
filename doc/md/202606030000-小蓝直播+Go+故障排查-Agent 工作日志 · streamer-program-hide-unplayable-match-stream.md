---
id: "doc-fb9ccda935d2"
title: "Agent 工作日志 · streamer-program-hide-unplayable-match-stream"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-streamer-program-hide-unplayable-match-stream.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-streamer-program-hide-unplayable-match-stream.md"
sourceSha256: "7c6e219f37c47a7a7c0892219053c39f97fbdfcfe580f67c8f1da76f9499954b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · streamer-program-hide-unplayable-match-stream

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20streamer-program-hide-unplayable-match-stream.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：主播端节目流接口隐藏不可播放的赛事流 ID

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：`GET /api/v1/streamer/rooms/{room_id}/program`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 前端不再根据业务 status 猜测赛事流能否播放。
2. 后端实时查询 ZEGO 云播放器状态，只有确认 Status=4 且 StreamID 匹配时才返回 `match_stream_id`。
3. `match_stream_id` 缺失或为空时，主播端不应拉赛事流。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/streamer.go` | 主播端节目流 DTO 将 `match_stream_id` 改为可选，并增加 ZEGO 排障字段 |
| `services/go-app/internal/service/liveprogram/service.go` | `GetStreamerProgram` 接入 ZEGO DescribePlayers 可播探测 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 覆盖可播、已销毁、StreamID 不匹配三类判断 |
| `docs/api/openapi.yaml` | 更新主播端契约 |
| `packages/contracts/openapi/v1.yaml` | 同步契约包 |

## 核心决策

1. 前端播放判断统一改为：存在 `match_stream_id` 才拉赛事源；不存在则等待/提示后台重建。
2. ZEGO 状态字段仅作为排障信息，前端不需要理解状态机。
3. 后台管理接口仍保留原始 `match_stream_id`，便于运营/技术排查；本次只收紧主播端可播放契约。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `StreamerRoomProgram.match_stream_id` 改为可选 |
| 验收口径 | ZEGO Player 非 Playing 或 StreamID 不匹配时，主播端接口不返回 `match_stream_id` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方依赖状态收敛 / 可观测性 |
| 当前 MVP 边界 | 每次主播端查询节目流时实时查询当前 ZEGO Player；未新增缓存 |
| 高风险触发项 | 直播链路 / 第三方 ZEGO |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需部署 go-app 后生效 |
| 密钥 | 使用已有 ZEGO ServerSecret，仅后端调用，不暴露给前端 |
| 观测 | ZEGO DescribePlayers 失败会写 `live.program.zego_player_failed` 日志 |
| 回滚 | 回滚本次代码即可恢复旧字段行为 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 前端不再误拉已销毁/不存在赛事流 |
| 红队质疑 | 如果 ZEGO DescribePlayers 短暂失败，字段会隐藏，主播端需要轮询重试 |
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
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
