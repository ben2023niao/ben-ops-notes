---
id: "doc-5c7bd4c019d6"
title: "Agent 工作日志 · streamer-publish-config-preview-token"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-streamer-publish-config-preview-token.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-streamer-publish-config-preview-token.md"
sourceSha256: "8728cf9e6111110b90923e9451f3ec3a26891977860b88b5ffb91db2d6f47824"
sourceSystem: "project-doc"
---

# Agent 工作日志 · streamer-publish-config-preview-token

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20streamer-publish-config-preview-token.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：主播端开播前预览配置补充 Zego Login-only token

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：STR-101 / LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户确认主播开播前需要美颜预览和 LSJ 比赛源预览,前端反馈预览阶段需要 `zego_token`

## 本次目标

1. `GET /api/v1/streamer/rooms/{room_id}/publish-config` 返回开播前 Login-only `zego_token`。
2. 保持该接口不创建 `live_sessions`、不改变房间状态、不返回 `stream_no/session_id`。
3. OpenAPI 明确预览 token 与正式开播 token 的边界。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/streamer.go` | `StreamerPublishConfigResponse` 增加 `zego_token`、`expires_at_ms` |
| `services/go-app/internal/service/streamer/live.go` | `PublishConfig` 签发 Login-only 预览 token;抽出 token signer 接口便于权限测试 |
| `services/go-app/internal/service/streamer/live_test.go` | 增加预览 token 不创建 session、只含 Login 权限的回归测试 |
| `docs/api/openapi.yaml` | 更新接口文档与响应 schema |
| `packages/contracts/openapi/v1.yaml` | 同步契约基线 |

## 核心决策

1. 预览 token 使用 `zego.PrivLogin`,只允许主播端 `loginRoom` 和拉 `match_stream_id`,不能 Publish。
2. 正式开播仍只走 `POST /api/v1/streamer/rooms/{room_id}/start`,该接口创建 session 并返回 Login+Publish token、`stream_no`、`session_id`。
3. 后台 `开播准备` 只负责 LSJ → ZEGO Cloud Player → `match_stream_id`;不作为主播正式开播入口。
4. 不做 DB 变更,不持久化美颜参数。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | STR-101 / LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | `StreamerPublishConfigResponse` |
| 不涉及契约的原因 | 不适用,本次已更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 数据表设计 | 不涉及 DB / migration / 索引 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金;接口只读配置 + token 签发,不写业务状态 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否,涉及主播推拉流权限边界 |
| 涉及能力 | 权限安全 / 第三方 Zego token |
| 当前 MVP 边界 | 单接口签发短期 token,不引入独立 token 服务 |
| 高风险触发项 | 权限 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅 Go API 与文档产物变更 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 复用既有 `APP_ZEGO_*` secret,不新增配置 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增日志/指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 预览 token 只含 Login,避免开播前误拿 Publish 权限 |
| 红队质疑 | 如果前端把预览 token 用于正式推流会失败;契约已明确必须调用 `/start` 换正式 token |
| 合入判断 | 可以合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer -run 'TestLiveService_PublishConfig' -count=1` | 通过 |

## 风险与待办

1. 前端必须区分预览 token 和正式开播 token。
2. 后台“状态强切开播”仍应只作为兜底/测试动作,不要当正常主播开播链路。
3. 文档部署后需要通知前端以 Stoplight operation 深链为准。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 前端先调 `publish-config` 登录房间并预览 LSJ,再调 `program` 拉 `match_stream_id`。
2. 点击正式开播必须调 `/start`,并使用 `/start` 返回的 `stream_no/session_id/zego_token`。
3. 本次无 DB 变更。
