---
id: "doc-4d3c65726d6b"
title: "2026-06-07 live room WS token fallback"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Nginx", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-ws-token-fallback.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-ws-token-fallback.md"
sourceSha256: "c2f1c8fa5af5a5d14fcc6ed5245a47344d19af0a496801c59baa210cc6a36d36"
sourceSystem: "project-doc"
---

# 2026-06-07 live room WS token fallback

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-ws-token-fallback.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：排查 H5 直播间 WebSocket 失败，并修复公开直播间 WS 携带无效 token 时直接断连的问题。

## 输入资料

- 页面：`https://web-dev.54-151-131-132.sslip.io/live/22821611455381505`
- 截图现象：`GET /api/v1/live/room/{room_id}/votes/active 404`，`wss://api-dev.54-151-131-132.sslip.io/ws/v1/live/{room_id}?敏感凭据：[已脱敏] failed`
- 需求 ID：`LIVE-004`
- 接口/契约：`docs/api/conventions.md` WebSocket 公共协议；旧直播间 WS `GET /ws/v1/live/{room_id}` JWT 可选。

## 数据链路

1. H5 直播间进入页读取 `apps/web/app/composables/useLiveSocket.ts`，用当前 C 端 access token 拼接 `/ws/v1/live/{room_id}?敏感凭据：[已脱敏]
2. Nginx `api-dev` 将 `/ws/` 反代到 `kickoff-ws:8082`。
3. `cmd/ws` 装配 `router.BuildPublicWS`，注册 `GET /ws/v1/live/:room_id` 到 `wsapi.Handler.LiveRoom`。
4. `LiveRoom` 解析 room id，然后用 `parseUserID` 解析 query token。
5. 修复前：token 过期、格式错误或 subject 不匹配时，`LiveRoom` 直接 `401`，浏览器 WebSocket 握手失败。
6. 修复后：旧直播间 WS 是公开频道，token 解析失败只降级为游客 `userID=0`，继续完成 WebSocket 升级；钱包/主播 WS 仍强鉴权。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/http/wsapi/handlers.go` | `/ws/v1/live/:room_id` token 解析失败时降级游客，不阻断公开直播间连接。 |
| `services/go-app/internal/http/wsapi/handlers_test.go` | 增加坏 token 不应在升级前返回 401 的回归测试。 |

## 线上排查结论

- `GET /api/v1/live/room/{room_id}/votes/active` 线上返回的是业务错误 `404 + code=20002 当前房间没有进行中的投票`，不是路由丢失。
- `wss://api-dev.../ws/v1/live/{room_id}` 无 token 可正常连接，说明 Nginx 和 `kickoff-ws` 进程可用。
- 携带坏 token 时线上会在握手前返回 `401`，与浏览器控制台 `WebSocket failed` 现象一致。
- 最近远端提交 `3d7f66c feat(live-host): 直播流程调整` 只改 `apps/live-host`，没有改 H5 `apps/web` 的 WS 代码。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 是否影响 OpenAPI REST 契约 | 否，WebSocket 旧入口既有约定为 JWT 可选 |
| 是否影响权限安全 | 放宽范围仅限公开直播间广播频道；不订阅用户私有频道，不影响钱包/主播 WS |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `curl -i https://api-dev.54-151-131-132.sslip.io/api/v1/live/room/22821611455381505/votes/active` | 返回 JSON 业务 404：`code=20002` |
| Node WebSocket 无 token 连接 `/ws/v1/live/22821611455381505` | 可 `open` 后正常关闭 |
| Node WebSocket 坏 token 连接线上旧逻辑 | 复现握手失败；curl 升级头返回 `401` |
| `go test ./internal/http/wsapi -run 'TestLiveRoomFallsBackToGuestWhenTokenInvalid|TestParseUserID|TestParseClientUserID|TestParseStreamerID' -count=1` | 通过 |
| `go test ./internal/http/wsapi ./internal/http/router -count=1` | 通过 |
| `go test ./... -count=1` | 通过 |
| `go vet ./...` | 通过 |

## 风险与回滚

- 风险：过期登录用户会按游客接入旧直播间 WS，不能收到个人频道消息；这是公开频道兜底，优先保证看播不断。
- 回滚：恢复 `LiveRoom` 中 `parseUserID` 失败即 `AbortWithStatus(401)` 的逻辑。
