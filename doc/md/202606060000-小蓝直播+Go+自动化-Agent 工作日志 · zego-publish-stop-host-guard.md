---
id: "doc-337c503bbbab"
title: "Agent 工作日志 · zego-publish-stop-host-guard"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-zego-publish-stop-host-guard.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-zego-publish-stop-host-guard.md"
sourceSha256: "98914ed6b7ac94aba51e3cbb74ac861d6f13b8a4b6f52f866ceca2361c76f2d8"
sourceSystem: "project-doc"
---

# Agent 工作日志 · zego-publish-stop-host-guard

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606060000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20zego-publish-stop-host-guard.md)

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

日期：2026-06-06
Agent：Codex
任务：修复 ZEGO 非主播主流 publish.stop 误结束直播间

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101
- 接口/契约：ZEGO webhook `POST /api/v1/zego/webhook`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 排查后台「ZEGO 开播准备 / 强制重建」后主播直播约 60 秒断开的链路。
2. 防止 LSJ 赛事云播放器、混流或旧流的 `publish.stop` 误结束主播直播间。
3. 补充单测覆盖非主播主流 stop 场景。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/streamer/webhook.go` | `publish.stop` 必须匹配当前 active live session 的 `stream_no` 才允许结束直播间 |
| `services/go-app/internal/service/streamer/webhook_test.go` | 补充赛事流 stop 忽略、无 active session 忽略测试 |

## 核心决策

1. ZEGO 房间中同时存在主播主流、赛事云播放器流、混流；`publish.stop` 不能只按 room_no 结束直播间。
2. 只有 `payload.stream_id == live_sessions.stream_no` 才是主播主流停止，才允许收口 room/session/program。
3. 无法找到 active session 时不盲目下播，避免第三方非主流 stop 造成误杀；异常房间可由心跳 worker 或后台强制下播兜底。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不涉及对外契约变更 |
| 不涉及契约的原因 | 仅收紧 ZEGO webhook 内部状态机判断，不改变请求/响应结构 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；保留原有主播主流 stop 审计 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重启 Go API 服务后生效 |
| 回滚 | 回滚本次两个文件即可恢复旧行为 |
| 密钥 | 不涉及 |
| 观测 | 新增非主播主流 stop 被忽略的结构化日志 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer` | 通过 |
| `go test ./internal/service/liveprogram` | 通过 |
| `go test ./internal/worker` | 通过 |
| `go test ./...` | 通过 |

## 风险与待办

1. 前端仍需避免同房间重复 `loginRoom/logoutRoom` 干扰主播主推流。
2. 后续可把赛事流 stop 时的节目流状态主动标记为 `FAILED`，目前由节目流查询时探测 ZEGO/LSJ 后更新。
3. 线上验证时重点观察 `stopped_stream_id` 与 `active_host_stream_id` 日志字段。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 后台 `prepare-live` 生成的是 ZEGO 云播放器赛事流，不等于主播主流。
2. `publish.stop` 现在只认当前 active session 的 `stream_no`。
3. 当前修复不改变前端 API 契约。
