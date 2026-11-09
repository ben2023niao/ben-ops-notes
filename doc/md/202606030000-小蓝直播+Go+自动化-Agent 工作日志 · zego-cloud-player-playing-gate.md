---
id: "doc-3058786387d1"
title: "Agent 工作日志 · zego-cloud-player-playing-gate"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-zego-cloud-player-playing-gate.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-zego-cloud-player-playing-gate.md"
sourceSha256: "1a9ce8c6aa3e5844d62373bd4b30061f24090e9e1deb54a2aa80f7e27e2a02a5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · zego-cloud-player-playing-gate

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20zego-cloud-player-playing-gate.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：ZEGO 云播放器创建后确认 Playing 再返回主播端

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101
- 接口/契约：`POST /api/v1/admin/rooms/{id}/prepare-live`、`GET /api/v1/streamer/rooms/{room_id}/program`
- 团队可读文档：`docs/api/streamer-lsj-zego-cloud-player.md`
- 第三方文档：ZEGOCLOUD Cloud Player `CreatePlayer`、`DescribePlayers`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户反馈主播端拉 `match_stream_id` 报 ZEGO `err=1004 stream does not exist`

## 本次目标

1. 不再把 `CreatePlayer` 成功直接视为赛事流可拉。
2. 后端在开播准备/强制重建阶段轮询 `DescribePlayers`，确认云播放器状态为 Playing 后再保存并返回 `MATCH_STREAM_READY`。
3. 如果云播放器连接媒体失败、播放结束、已销毁或超时，直接让开播准备失败，并尽力删除新建 player，避免占用 ZEGO 额度。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/pkg/zego/cloud_player.go` | 新增 `DescribeCloudPlayers` 封装和云播放器状态常量。 |
| `services/go-app/pkg/zego/cloud_player_test.go` | 新增 `DescribePlayers` 请求与响应解析测试。 |
| `services/go-app/pkg/zego/cloud_player_real_test.go` | 真实联调测试新增创建后轮询到 Playing 的验证。 |
| `services/go-app/internal/service/liveprogram/service.go` | `PrepareLive` 创建云播放器后等待状态 Playing；失败时删除 player 并返回错误。 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 新增云播放器 Playing/连接失败状态判断测试。 |
| `docs/agents/logs/2026-06-03-zego-cloud-player-playing-gate.md` | 记录本次修复与验证。 |

## 核心决策

1. `CreatePlayer` 只代表 ZEGO 接受任务，不代表 `match_stream_id` 已在房间内可拉。
2. `DescribePlayers.Status = 4` 才能把节目流暴露给主播端。
3. 状态 6/7/8 或超时都视为不可用，避免前端拿到不存在的流继续拉。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不新增字段，接口行为收紧 |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；沿用已有 prepare-live 审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 第三方直播源、ZEGO 云播放器状态一致性 |
| 当前 MVP 边界 | 使用同步短轮询确认 Playing；后续可接 ZEGO 回调做异步状态机 |
| 高风险触发项 | 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要部署 go-app 后生效 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及新增密钥 |
| 备份恢复 | 不涉及 |
| 观测 | 失败会通过 prepare-live 错误直接暴露给后台 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | `MATCH_STREAM_READY` 现在表示 ZEGO 云播放器已进入 Playing，不再是假 ready。 |
| 红队质疑 | 同步等待会增加开播准备耗时；但比返回不可拉流更可控，后续可用回调改异步。 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./pkg/zego ./internal/service/liveprogram` | 通过 |
| `go test ./...` | 通过 |
| 真实 dev curl `GET /api/v1/streamer/rooms/22240179938918401/program` | 复现当前线上返回 `MATCH_STREAM_READY` 但主播端 SDK 报 `stream does not exist`；本地无 ZEGO/LSJ 密钥，真实 `RUN_REAL_LSJ_ZEGO=1` 待部署机执行 |

## 风险与待办

1. 当前等待窗口为 12 秒，如 LSJ/HLS 启动更慢，后台会看到明确失败，需要重试或改异步。
2. 后续应接入 ZEGO Cloud Player 回调，把状态变化落库。
3. 部署后需在 dev 重新强制重建，确认主播端能拉新 `match_stream_id`。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `CreatePlayer` 成功不是可拉流证明。
2. `DescribePlayers.Status = 4` 才是云播放器正在推流。
3. 主播端拿到 `MATCH_STREAM_READY` 后再拉 `match_stream_id`，如果后台开播准备失败，不要继续使用旧 stream id。
