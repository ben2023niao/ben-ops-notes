---
id: "doc-5e1e4ca3a0a1"
title: "当前 WebSocket 实现文档"
date: "2026-06-02T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Nginx", "监控告警", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/websocket-current.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/websocket-current.md"
sourceSha256: "8fd40ce58777d5e9f4ab0668076e7b08cf98db61fa202af8ac7b853b443713e5"
sourceSystem: "project-doc"
---

# 当前 WebSocket 实现文档

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BNginx-%E5%BD%93%E5%89%8D%20WebSocket%20%E5%AE%9E%E7%8E%B0%E6%96%87%E6%A1%A3.md)

> 整理日期：2026-06-02 00:00｜日期依据：正文日期

> 生成日期：2026-06-02
> 范围：基于 `services/go-app` 当前代码实现审计，不包含契约中声明但代码未实际广播的事件。

## 结论

- 当前没有单独推送“礼物实时榜单列表”的 WS 事件。
- 直播间送礼成功后，服务端只推 `live.tip.combo` 单次/连击增量，字段为 `user_id`、`nickname`、`combo_count`、`diamond_amount`。
- 完整礼物榜数据只通过 HTTP 拉取：`GET /api/v1/live/room/{room_id}/tip-rank?limit=10`。
- 前端如果要维护实时榜，目前应使用：进房先拉 `/tip-rank` 初始榜，再用 `live.tip.combo` 增量累加本地榜单。
- 主播端开播后必须通过 `/ws/v1/streamer` 每 15s 上报 `streamer.live.heartbeat`；后端 60s 未收到会自动下播并广播 `room.status.ended`。

## 连接地址

Dev 环境外部地址仍为 `wss://api-dev.54-151-131-132.sslip.io/ws/v1/...`；nginx 按 `/ws/` 路径转发到独立 `kickoff-ws:8082`，REST 仍转发到 `kickoff-api:8080`。

### C 端统一入口（推荐）

| 通道 | 地址 | 鉴权 | 订阅频道 | 说明 |
|---|---|---|---|---|
| C 端统一连接 | `/ws/v1/client?敏感凭据：[已脱敏] | 可选 | 登录用户自动订阅 `user:{user_id}`；客户端可通过 `client.subscribe` 订阅 `room:{room_id}` / `match:{match_id}` | 新版 H5/Web 只接这一条。游客可连接但不能订阅 `user:*`；`user:*` 只能由服务端根据 C 端 JWT 自动订阅 |
| 主播端统一连接 | `/ws/v1/streamer?敏感凭据：[已脱敏] | 必填主播 JWT | 主播端可通过 `client.subscribe` 订阅 `room:{room_id}` / `match:{match_id}` | 新版主播工作台只接这一条；不订阅 `user:*` 钱包个人频道 |

订阅直播间：

```json
{
  "type": "client.subscribe",
  "data": {
    "channels": ["room:22012996385505281"]
  }
}
```

退订直播间：

```json
{
  "type": "client.unsubscribe",
  "data": {
    "channels": ["room:22012996385505281"]
  }
}
```

服务端订阅确认：

```json
{
  "type": "server.subscribed",
  "data": {
    "channels": ["room:22012996385505281"]
  }
}
```

服务端退订确认：

```json
{
  "type": "server.unsubscribed",
  "data": {
    "channels": ["room:22012996385505281"]
  }
}
```

### Public API

| 通道 | 地址 | 鉴权 | 订阅频道 | 说明 |
|---|---|---|---|---|
| 直播间（兼容旧版） | `/ws/v1/live/{room_id}?敏感凭据：[已脱敏] | 可选 | `room:{room_id}`；登录用户额外订阅 `user:{user_id}` | Deprecated：新版 H5/Web 不再接这条 |
| 钱包（兼容旧版） | `/ws/v1/wallet?敏感凭据：[已脱敏] | 必填 C 端用户 JWT | `user:{user_id}` | Deprecated：新版 H5/Web 不再接这条 |
| 比赛（兼容旧版） | `/ws/v1/match/{match_id}?敏感凭据：[已脱敏] | 可选 | `match:{match_id}` | Deprecated：新版 H5/Web 不再接这条 |

### Admin API

| 通道 | 地址 | 鉴权 | 订阅频道 | 说明 |
|---|---|---|---|---|
| 房间监控 | `/api/v1/admin/ws/rooms/{id}/danmaku?敏感凭据：[已脱敏] | 必填 Admin JWT + 房间权限 | `room:{id}` | 后台同源部署推荐路径，复用 admin `/api` 反代；`/ws/v1/admin/rooms/{id}/danmaku` 保留兼容本地代理 |

## Envelope 格式

服务端推送统一为 JSON：

```json
{
  "type": "live.danmaku.received",
  "msg_id": "uuid-or-business-id",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {}
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | string | 事件类型 |
| `msg_id` | string | 消息 ID。弹幕事件使用弹幕业务 ID，其余多为 UUID |
| `ts` | int64 | 服务端发送时间，Unix ms |
| `trace_id` | string | 链路 ID；请求上下文没有时自动生成 UUID |
| `data` | object | 事件 payload |

## 心跳

服务端会用 WebSocket ping frame 保活，周期约 54 秒。业务层也支持客户端发送：

```json
{
  "type": "client.ping",
  "ts": 1719404400000,
  "data": {}
}
```

服务端返回：

```json
{
  "type": "server.pong",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "uuid",
  "data": {}
}
```

`client.ping` 只用于 WebSocket 连接保活，不会更新直播间状态。
弹幕发送仍走 HTTP；主播端直播业务状态使用下面的 `streamer.live.heartbeat`。

## 主播端业务心跳

主播端开播成功后，在 `/ws/v1/streamer?敏感凭据：[已脱敏] 上每 15s 发送：

```json
{
  "type": "streamer.live.heartbeat",
  "data": {
    "room_id": "9001",
    "session_id": "10001",
    "zego_room_id": "R001",
    "zego_stream_id": "rm_R001_10001"
  }
}
```

字段说明：

| 字段 | 是否必传 | 说明 |
|---|---|---|
| `room_id` | 必传 | 直播间 ID；后端校验该房间是否属于当前主播且状态为 `LIVE` |
| `session_id` | 建议传 | 开播接口 `StreamerStartLiveResponse.session_id`；传了会校验是否等于当前 active session |
| `zego_room_id` | 建议传 | 开播接口 `zego_room_id`；传了会校验是否等于 `live_rooms.room_no` |
| `zego_stream_id` | 建议传 | 开播接口 `stream_no`；传了会校验是否等于当前 `live_sessions.stream_no` |

后端连续 60s 未收到主播业务心跳时，会把直播间置为 `ENDED`，并向 `room:{room_id}` 广播：

```json
{
  "type": "room.status.ended",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "room_id": "9001",
    "status": "ENDED",
    "reason": "streamer_heartbeat_timeout"
  }
}
```

C 端不需要上报该心跳；如果已经处理 `room.status.ended` 关播事件，则无需新增接入。`reason=streamer_heartbeat_timeout` 只用于可选文案区分。

## 直播间事件

以下事件广播到 `room:{room_id}`。C 端通过 `/ws/v1/client` 发送 `client.subscribe` 订阅；旧 `/ws/v1/live/{room_id}` 和 admin 房间监控 WS 仍可收到。

### `live.danmaku.received`

触发：用户通过 HTTP `POST /api/v1/live/room/{room_id}/danmaku` 发送弹幕成功。

```json
{
  "type": "live.danmaku.received",
  "msg_id": "1234567890",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "user_id": "10001",
    "nickname": "alex",
    "color": "#ffffff",
    "content": "进球了",
    "sent_ts": 1719404400000
  }
}
```

### `live.tip.combo`

触发：用户通过 HTTP `POST /api/v1/live/room/{room_id}/tip` 送礼/打赏成功。

注意：这是单次送礼增量，不是礼物榜列表。

```json
{
  "type": "live.tip.combo",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "user_id": "10001",
    "nickname": "alex",
    "combo_count": 3,
    "diamond_amount": 300
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `user_id` | string | 送礼用户 ID |
| `nickname` | string | 展示名 |
| `combo_count` | int | 本次数量/连击数，对应请求 quantity |
| `diamond_amount` | int64 | 本次礼物钻石总额 |

### `wallet.balance.updated`

触发：送礼成功后，服务端会同时向送礼用户的 `user:{user_id}` 私发余额变更。登录用户连接直播间 WS 时也会订阅自己的 user channel，所以可能在直播间 WS 连接中收到该事件。

```json
{
  "type": "wallet.balance.updated",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "rmb_balance": "",
    "diamond_balance": 9900,
    "reason": "tip"
  }
}
```

### `live.viewer.count.updated`

触发：用户连接直播间 WS 时，服务端立即向房间广播一次当前连接数。当前实现没有定时 30s 推送。

```json
{
  "type": "live.viewer.count.updated",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "viewer_count": 12,
    "peak_count": 12
  }
}
```

### `live.crowdfund.progress`

触发：送礼成功后异步累加本场收入，并广播当前众筹累计进度。

```json
{
  "type": "live.crowdfund.progress",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "session_id": "20001",
    "cumulative_diamond": 8888,
    "next_stage": {
      "id": "30001",
      "stage_no": 2,
      "name": "主播唱歌",
      "threshold_diamond": 18888,
      "action_text": "唱一首指定歌曲"
    }
  }
}
```

`next_stage` 可省略，表示所有阶段均已达成。

### `live.crowdfund.stage_unlocked`

触发：送礼后本场累计金额首次达到某个众筹阶段阈值。

```json
{
  "type": "live.crowdfund.stage_unlocked",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "session_id": "20001",
    "stage": {
      "id": "30001",
      "stage_no": 1,
      "name": "主播唱歌",
      "threshold_diamond": 8888,
      "action_text": "唱一首指定歌曲"
    },
    "amount_at_achieved": 9000,
    "achieved_at_ms": 1719404400000
  }
}
```

### `live.vote.started`

触发：主播端发起投票成功。

```json
{
  "type": "live.vote.started",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "vote_id": "40001",
    "title": "谁是本场 MVP?",
    "duration_sec": 600,
    "started_at_ms": 1719404400000,
    "ends_at_ms": 1719405000000,
    "options": [
      {
        "id": "50001",
        "option_no": 1,
        "name": "梅西",
        "votes_count": 0
      }
    ]
  }
}
```

### `live.vote.tick`

触发：用户投票成功或重复投票幂等返回后，服务端广播该选项当前票数和总票数。

```json
{
  "type": "live.vote.tick",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "vote_id": "40001",
    "option_id": "50001",
    "votes_count": 12,
    "total_votes": 31
  }
}
```

### `live.vote.ended`

触发：投票到期 worker 关单后广播。

```json
{
  "type": "live.vote.ended",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "vote_id": "40001",
    "winner_option_id": "50001",
    "total_votes": 31,
    "ended_at_ms": 1719405000000,
    "options": [
      {
        "id": "50001",
        "option_no": 1,
        "name": "梅西",
        "votes_count": 12
      }
    ]
  }
}
```

`winner_option_id` 可省略，表示平票或无人投票。

### `live.system.notice`

触发：主播工作台推送房间话术。

```json
{
  "type": "live.system.notice",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "level": "info",
    "text": "欢迎进场",
    "source": "streamer_push",
    "duration_ms": 5000
  }
}
```

### `live.danmaku.deleted`

触发：admin 删除房间弹幕后广播。

```json
{
  "type": "live.danmaku.deleted",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "msg_id": "1234567890",
    "by_admin": true,
    "reason": ""
  }
}
```

### `room.status.live`

触发：admin 强制开播。

```json
{
  "type": "room.status.live",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "room_id": "10001",
    "status": "LIVE",
    "reason": "manual"
  }
}
```

### `room.status.ended`

触发：admin 强制关播；或主播业务心跳 60s 超时自动下播。

```json
{
  "type": "room.status.ended",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "room_id": "10001",
    "status": "ENDED",
    "reason": "manual"
  }
}
```

业务心跳超时自动下播时，`reason` 为 `streamer_heartbeat_timeout`。

### `room.banned`

触发：admin 封禁房间。

```json
{
  "type": "room.banned",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "room_id": "10001",
    "status": "BANNED",
    "reason": "violation"
  }
}
```

## 钱包事件

以下事件发送到 `user:{user_id}`。C 端登录连接 `/ws/v1/client` 后由服务端自动订阅；旧 `/ws/v1/wallet` 仍可收到。

### `wallet.balance.updated`

触发：余额相关业务变更。当前有两种 payload 形态：

送礼/下注链路会携带余额快照：

```json
{
  "type": "wallet.balance.updated",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "rmb_balance": "",
    "diamond_balance": 9900,
    "reason": "tip"
  }
}
```

钱包服务通用余额变更只携带 reason，客户端收到后应重新拉余额：

```json
{
  "type": "wallet.balance.updated",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "reason": "recharge"
  }
}
```

`reason` 当前代码注释列出的取值：`recharge`、`withdraw`、`bet`、`tip`、`refund`、`admin_adjust`。

### `wallet.recharge.success`

触发：充值到账。

```json
{
  "type": "wallet.recharge.success",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "order_no": "R202606020001",
    "rmb_amount": "100.00",
    "diamond_amount": 95,
    "paid_at_ms": 1719404400000
  }
}
```

### `wallet.recharge.refunded`

触发：充值退款或进入半人工待调账。

```json
{
  "type": "wallet.recharge.refunded",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "order_no": "R202606020001",
    "rmb_amount": "100.00",
    "reason": "manual_review_pending"
  }
}
```

### `wallet.withdraw.submitted`

触发：提现申请提交成功。

```json
{
  "type": "wallet.withdraw.submitted",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "order_no": "W202606020001",
    "rmb_amount": "100.00"
  }
}
```

### `wallet.recharge.failed`

代码中定义了事件常量，但当前未找到实际广播调用。

## 比赛事件

以下事件广播到 `match:{match_id}`。C 端通过 `/ws/v1/client` 发送 `client.subscribe` 订阅；旧 `/ws/v1/match/{match_id}` 仍可收到。

### `match_score`

触发：admin 更新比分。

```json
{
  "type": "match_score",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "match_id": "60001",
    "home_score": 1,
    "away_score": 0,
    "status": "LIVE"
  }
}
```

### `match_state`

触发：admin 标记比赛结束。

```json
{
  "type": "match_state",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "match_id": "60001",
    "status": "ENDED",
    "result": "home_win"
  }
}
```

### `match_phase`

触发：admin 手动切换比赛阶段。

```json
{
  "type": "match_phase",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "match_id": "60001",
    "phase": "first_half",
    "minute": 12,
    "stoppage": 0
  }
}
```

### `match_goal`

触发：admin 录入进球事件。

```json
{
  "type": "match_goal",
  "msg_id": "uuid",
  "ts": 1719404400000,
  "trace_id": "trace-id",
  "data": {
    "match_id": "60001",
    "team_id": "70001",
    "minute": 36,
    "stoppage": 0,
    "player_name": "Messi",
    "assist_name": "Di Maria",
    "goal_type": "normal",
    "home_score": 1,
    "away_score": 0
  }
}
```

## 当前代码中存在但未实际推送的事件

| 事件 | 当前状态 |
|---|---|
| `live.enter.normal` | 有常量和 payload，但当前未找到广播调用 |
| `live.viewer.leave` | 有常量和 payload，注释标明 v1 不主动推 |
| `client.danmaku.send` | 有常量，但 read loop 不处理；弹幕走 HTTP |
| `wallet.recharge.failed` | 有常量，当前未找到广播调用 |
| `live.tip.rank.updated` / `live.gift.rank.updated` | 当前没有这类事件常量，也没有广播调用 |
| `/ws/v1/_stats` | handler 中有方法，但 public router 当前未挂载 |

## 礼物榜当前数据来源

HTTP 接口：

```http
GET /api/v1/live/room/{room_id}/tip-rank?limit=10
```

响应 `data`：

```json
{
  "session_id": "20001",
  "room_id": "10001",
  "items": [
    {
      "rank": 1,
      "user_id": "10001",
      "nickname": "alex",
      "avatar_url": "https://example.com/avatar.png",
      "diamond_amount": 3000,
      "tip_count": 2,
      "gift_count": 3,
      "last_tip_at_ms": 1719404400000
    }
  ]
}
```

排序规则来自 repository SQL：

1. 按用户聚合当前 active session 的 `live_tips`。
2. `SUM(diamond_amount)` 倒序。
3. 金额相同按最近送礼时间升序。
4. `limit` 默认 10，最大 50。

如果需要服务端直接推完整榜单，需要新增事件类型和广播调用；当前代码尚未实现。
