---
id: "doc-17dd20671520"
title: "Kickoff WebSocket 协议"
date: "2026-06-06T17:35:52+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Redis", "监控告警", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/websocket.html"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/websocket.html"
sourceSha256: "3c8c1a2b837177d83fd82ea3dd828ac37a3bc4eea52eab5332c9c2027c0d9a17"
sourceSystem: "project-doc"
---

# Kickoff WebSocket 协议

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606061735-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BRedis%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-Kickoff%20WebSocket%20%E5%8D%8F%E8%AE%AE.md)

> 整理日期：2026-06-06 17:35｜日期依据：文件创建/修改时间

对齐 `docs/api/conventions.md §16` + PRD v0.2。本页面是 WebSocket 实时推送的权威说明。HTTP REST API 见 [API 文档](index.html)。

**原则**：WebSocket 仅承担**实时推送**和少量**实时态上行**（心跳/已读/输入中）。所有**资金类操作必须走 HTTP**（押注/打赏/充值/提现），WS 只做事后通知（如"押注成功"、"派彩到账"）。

## 协议总览

| 项 | 值 |
| --- | --- |
| 协议 | WebSocket（RFC 6455） |
| 传输 | JSON 文本帧（非二进制） |
| 鉴权 | JWT，连接时通过 query string `?敏感凭据：[已脱敏] 传入 |
| 消息格式 | [统一 envelope](#envelope)：`{ type, msg_id, ts, data }` |
| 心跳间隔 | 客户端每 **30s** 发 `client.ping` |
| 断连超时 | 客户端 60s 无 `server.pong` → 重连 |
| 主播业务心跳 | 主播端开播后每 **15s** 发 `streamer.live.heartbeat`；60s 未收到则后端自动下播 |
| 消息去重 | 客户端按 `msg_id` 24h LRU 去重 |
| 重连 | 指数退避 1/3/9/30/60s，最多 10 次，重连必须重新鉴权 |
| 断线补推 | 不补推（关键资金类用 HTTP 兜底拉取） |
| 单消息大小 | ≤ 4 KB |
| 单 UID 并发连接 | ≤ 5 |

## 6 个通道

| 通道 | URL | 用途 | 鉴权 |
| --- | --- | --- | --- |
| C 端统一连接 | `/ws/v1/client` | H5/Web 统一入口；登录用户自动接收钱包/个人通知，进入页面后订阅 room/match | JWT 可选 |
| 主播端统一连接 | `/ws/v1/streamer` | 主播工作台统一入口；订阅 room/match 接收弹幕、打赏、话术、投票/众筹事件 | 主播 JWT |
| 直播间（Deprecated） | `/ws/v1/live/{room_id}` | 旧 H5 兼容入口；新版不再接 | JWT 可选 |
| 钱包（Deprecated） | `/ws/v1/wallet` | 旧 H5 兼容入口；新版不再接 | JWT |
| 比赛（Deprecated） | `/ws/v1/match/{match_id}` | 旧 H5 兼容入口；新版不再接 | JWT 可选 |
| 后台事件流 | `/ws/v1/admin/events` | 风控告警 / 对账差异 / KPI 实时 | Admin JWT |
| 房间管理员监控 | `/ws/v1/admin/rooms/{id}/danmaku` | 房间弹幕 / 观众进出 / 打赏 | Admin JWT + 房间权限 |

## 鉴权与连接

```
// JavaScript 示例
const 敏感凭据：[已脱敏]
const ws = new WebSocket(`wss://api.kickoff.tv/ws/v1/client?敏感凭据：[已脱敏]

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'client.subscribe', data: { channels: [`room:${roomId}`] } }));
};
ws.onmessage = (ev) => handleMessage(JSON.parse(ev.data));
ws.onclose = (ev) => handleClose(ev.code, ev.reason);
ws.onerror = (e) => console.error(e);
```

**失败立即关闭**：鉴权失败服务端推送 `server.error` 后用 close code `4001` 主动断开。客户端应跳登录页，不重连。

## 消息 envelope

所有 WS 消息（上行 + 下行）统一结构：

```
{
  "type": "live.danmaku.received",
  "msg_id": "01H9XYZ-7B3K-4N2P-...-ABC",
  "ts": 1719404400123,
  "trace_id": "abc123def456",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 类型码（snake_case + 点分隔，如 `live.danmaku.received`） |
| `msg_id` | string | 消息唯一 ID（ULID / UUID），客户端 24h LRU 去重 |
| `ts` | int64 | 服务端 Unix 毫秒时间戳 |
| `trace_id` | string | 链路追踪 ID（可选） |
| `data` | object | 类型相关 payload |

## 心跳

客户端每 **30 秒**发一次 `client.ping`：

```
// 上行（客户端 → 服务端）
{ "type": "client.ping", "ts": 1719404400000 }

// 下行（服务端 → 客户端）
{ "type": "server.pong", "ts": 1719404400123 }
```

客户端 60s 内未收到 `server.pong` → 视为断开 → 触发重连。

**注意**：`client.ping` 只用于 WebSocket 连接保活，不会更新直播间状态。主播是否还在直播，必须看下面的主播业务心跳。

### 主播业务心跳 `streamer.live.heartbeat`

主播端开播成功后，必须在 `/ws/v1/streamer?敏感凭据：[已脱敏] 上每 **15 秒**发送一次：

```
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

| 字段 | 是否必传 | 说明 |
| --- | --- | --- |
| `room_id` | 必传 | 直播间 ID；后端校验该房间是否属于当前主播且状态为 `LIVE` |
| `session_id` | 建议传 | 开播接口 `StreamerStartLiveResponse.session_id`；传了会校验是否等于当前 active session |
| `zego_room_id` | 建议传 | 开播接口 `zego_room_id`；传了会校验是否等于 `live_rooms.room_no` |
| `zego_stream_id` | 建议传 | 开播接口 `stream_no`；传了会校验是否等于当前 `live_sessions.stream_no` |

 后端连续 **60 秒**未收到主播业务心跳时，会把直播间置为 `ENDED`，并向 `room:{room_id}` 广播原有的 `room.status.ended`，`reason=streamer_heartbeat_timeout`。C 端不需要上报心跳；如果已经处理关播事件，则无需新增接入，`reason` 只用于可选文案区分。

## 重连规则

| 事件 | 客户端行为 |
| --- | --- |
| 网络断开 / 心跳超时 | 指数退避：1s / 3s / 9s / 30s / 60s |
| 最多重试 | 10 次 |
| 每次重连 | 重新鉴权（带最新 access token，过期先 refresh） |
| 服务端关闭（close code 4xxx） | 视 code 决定（详见下表） |
| 用户主动关闭 | 不重连 |

**不补推**：服务端重连后**不补推断开期间的消息**。关键资金类（充值到账 / 派彩）走 HTTP `/wallet/notifications` 兜底拉取。

## WebSocket Close Code

| Code | 含义 | 客户端动作 |
| --- | --- | --- |
| 1000 | 正常关闭 | 不重连（用户主动） |
| 1001 | 远端离开（关闭浏览器） | 不重连 |
| 1006 | 异常断开 | 自动重连 |
| 1011 | 服务端错误 | 自动重连 |
| **4001** | 鉴权失败 | 跳登录页 |
| **4002** | 鉴权过期 | refresh 后重连 |
| **4003** | 无订阅权限 | 不重连，UI 提示 |
| **4004** | 通道不存在 | 不重连 |
| **4006** | 顶号下线 | 跳登录页（账号已在其他设备登录） |
| **4429** | 限流 | 60s 后重连 |
| **4500** | 服务端错误 | 自动重连 |

## 类型码：通用控制（双向）

| 类型码 | 方向 | 说明 |
| --- | --- | --- |
| `client.ping` | 客户端→服务端 | 心跳 |
| `server.pong` | 服务端→客户端 | 心跳应答 |
| `client.subscribe` | 客户端→服务端 | 订阅子主题 |
| `client.unsubscribe` | 客户端→服务端 | 退订 |
| `streamer.live.heartbeat` | 主播端→服务端 | 主播开播后的业务心跳；每 15s 发送，60s 超时自动下播 |
| `server.error` | 服务端→客户端 | 错误（含 code/message/close 字段） |
| `server.kicked` | 服务端→客户端 | 服务端踢下线（顶号 / 封禁），随后断开 |

```
// server.error 示例
{
  "type": "server.error",
  "data": {
    "code": 30001,
    "message": "鉴权失败",
    "close": true
  }
}
```

## 类型码：直播间频道 `room:{room_id}`

**进场推送**（等级特权已下线，不做等级差异化）：

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `live.enter.normal` | 普通进场 | user_id, nickname |
| `live.enter.banner` | L4 进场（全屏轻 banner） | 同上 |
| `live.enter.fullscreen` | L5 进场（全屏中级特效） | 同上 |
| `live.enter.global` | L6 进场（**全平台震撼广播 + 跨房间**） | user_id, nickname, level, source_room_id |

**L0 游客不推进场**（PRD §3.1 等级特权已规定，进场提示 = "—"）。

**v1 不做离场推送**（原型未画；主流直播平台也不推离场）。

**弹幕 / 系统 / 状态**：

| 类型码 | 方向 | 说明 |
| --- | --- | --- |
| `live.danmaku.received` | 服务端→客户端 | 收到弹幕 |
| `client.danmaku.send` | 客户端→服务端 | 发弹幕（HTTP 兜底为主，WS 可选） |
| `live.tip.combo` | 服务端→客户端 | 打赏连击 banner（user_id, combo_count, diamond_amount） |
| `live.viewer.count.updated` | 服务端→客户端 | 观看人数 + 峰值（30s 批量推全房间） |
| `live.system.notice` | 服务端→客户端 | 系统消息（房间内升级广播 / 风控提示） |
| `live.muted.notify` | 服务端→客户端 | 你被禁言（mute_until_ts, reason） |
| `live.user.muted` | 服务端→客户端 | 其他用户被禁言 |
| `live.danmaku.deleted` | 服务端→客户端 | 弹幕被删除 |
| `room.status.live` | 服务端→客户端 | 房间开播 |
| `room.status.disconnected` | 服务端→客户端 | 断流 |
| `room.status.recovered` | 服务端→客户端 | 断流恢复 |
| `room.status.ended` | 服务端→客户端 | 关播 |
| `room.title.updated` | 服务端→客户端 | 房间标题改了（运营改） |
| `room.match.changed` | 服务端→客户端 | 关联比赛切换 |
| `room.banned` | 服务端→客户端 | 房间被封禁 |

```
// room.status.ended 示例；业务心跳超时时 reason 固定为 streamer_heartbeat_timeout
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

### LIVE-102 众筹解锁 + 投票(房间频道)

属于 `room:{room_id}` 同一频道；C 端通过 `/ws/v1/client` 发送 `client.subscribe` 订阅即可,无需额外鉴权。

| 类型码 | 触发 | data 关键字段 / 前端行为 |
| --- | --- | --- |
| `live.crowdfund.progress` | 每次有人送礼后(可能节流) | `session_id, cumulative_diamond, next_stage?{id,stage_no,name,threshold_diamond,action_text}` *前端*：用 `cumulative_diamond` 直接覆盖进度条,**不要假设 increment**；`next_stage=null` 表示全部阶段已达成。 |
| `live.crowdfund.stage_unlocked` | 本场累计第一次达到某阶段阈值 | `session_id, stage{...}, amount_at_achieved, achieved_at_ms` *前端*：弹「主播 XX 已解锁」toast + 已达成阶段卡片打勾；主播侧同步播 toast 提醒履约。同一阶段同一 session 仅广播 1 次(uk_session_stage)。 |
| `live.vote.started` | 主播发起新投票后立即推 | `vote_id, title, duration_sec, started_at_ms, ends_at_ms, options[{id, option_no, name, votes_count=0}]` *前端*：渲染投票卡 + 倒计时；同房间只可能有一个 ongoing 投票。 |
| `live.vote.tick` | 每次 C 端 cast 后 | `vote_id, option_id, votes_count, total_votes` *前端*：按 option_id 用 `votes_count` 直接覆盖该项票数,**不要做 +1**(同一秒可能合并)；`total_votes` 同步覆盖。 |
| `live.vote.ended` | 到期(cron 5s 扫描) / 主播下播 | `vote_id, winner_option_id?, total_votes, ended_at_ms, options[{...final tally}]` *前端*：展示获奖选项 + 最终票数排行；`winner_option_id=null` 表示平票或 0 票。状态切到 ended 后**不再允许 cast**(后端会拒)。 |

## 类型码：钱包个人频道 `user:{user_id}`

当前用户的资金事件流。所有钱包变动都会在这里推送一次。

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `wallet.balance.updated` | 余额变动（任何原因） | rmb_balance, diamond_balance |
| `wallet.recharge.success` | 充值到账 | order_no, amount_rmb, bonus_diamond, balance_rmb_after |
| `wallet.recharge.failed` | 充值失败 | order_no, reason |
| `wallet.withdraw.submitted` | 提现申请提交 | order_no, amount_rmb |
| `wallet.withdraw.approved` | 提现放行 | order_no, amount_rmb |
| `wallet.withdraw.rejected` | 提现驳回 | order_no, reason |
| `wallet.withdraw.success` | 提现到账 | order_no, actual_amount_rmb |
| `wallet.withdraw.failed` | 提现转账失败 | order_no, reason |
| `wallet.exchange.success` | 兑换成功 | direction, from_amount, to_amount |
| `wallet.bet.placed` | 押注成功 | bet_id, activity_id, amount_diamond, balance_diamond_after |
| `wallet.bet.settled` | 派彩入账 | bet_id, payout_diamond, balance_diamond_after, is_winner |
| `wallet.bet.refunded` | 退单到账 | bet_id, amount_diamond, balance_diamond_after |
| `wallet.tip.committed` | 打赏成功（自己端） | room_id, diamond_amount, balance_diamond_after |
| `wallet.notification.received` | 站内信 | title, body, link, severity |

## 类型码：比赛频道 `match:{match_id}`

由运营在后台手动录入触发（v0.2 无第三方数据源，仅比分 + 进球）。

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `match.score.updated` | 比分变化 | match_id, score_home, score_away, period |
| `match.goal.added` | 新增进球 | match_id, minute, team_code, player, score_home_after, score_away_after |
| `match.status.changed` | 状态变化（未开赛/进行中/已结束） | match_id, old_status, new_status |
| `match.mvp.published` | MVP 公布 | match_id, mvp_player, mvp_team |

## 类型码：用户个人事件

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `user.system.announcement` | 系统公告 | title, body, link, severity |
| `user.profile.updated` | 后台调整你的资料 | fields_changed: [...] |
| `user.frozen` | 账号被冻结 | reason |
| `user.unfrozen` | 账号被解冻 | — |

## 类型码：后台事件流 `/ws/v1/admin/events` 仅后台

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `admin.risk.alert.new` | 新增风控告警 | alert_id, rule_id, severity, target_type, target_id |
| `admin.recon.diff.new` | 对账新差异 | recon_date, channel, diff_count, diff_amount |
| `admin.streamer.live` | 主播开播 | streamer_id, room_id, match_id, started_at |
| `admin.streamer.ended` | 主播下播 | streamer_id, session_id, ended_at |
| `admin.streamer.disconnected` | 主播断流 | streamer_id, session_id |
| `admin.payment.callback.failed` | 支付回调失败 | channel, order_no, reason |
| `admin.withdraw.high_risk` | 提现高风险新单 | order_no, user_id, amount_rmb, risk_score |
| `admin.dashboard.kpi.updated` | 看板 KPI 实时 | gmv_today, online_users, live_streamers, bets_today |
| `admin.system.alert` | 系统告警（DB/Redis/Kafka 异常） | severity, source, message |

## 类型码：房间管理员监控 `/ws/v1/admin/rooms/{id}/danmaku` 仅后台

| 类型码 | 触发 | data 关键字段 / 节流 |
| --- | --- | --- |
| `admin.room.danmaku` | 房间弹幕实时 | msg_id, user_id, nickname, content, forbidden_hit |
| `admin.room.viewer.enter` | 任意观众进场 | **5s 服务端聚合**，超量降级为 "N 人进入" |
| `admin.room.viewer.leave` | 任意观众离场 | 同上节流 |
| `admin.room.tip.received` | 打赏到房间 | user_id, nickname, diamond_amount, combo_count |
| `admin.room.stats` | 房间实时统计 | viewer_count, peak_count, danmaku_count, gmv_diamond（10s 刷新） |

## 客户端实现要点

1. **必须有 msg_id 去重**：用 LRU（24h，10000 条容量）
2. **必须有心跳**：30s 间隔，60s 超时
3. **必须重新鉴权后重连**：每次重连前 refresh access token
4. **关键资金类有 HTTP 兜底**：派彩到账 / 充值到账 等不要单靠 WS（断线丢失风险）
5. **大 R 进场是关键业务**：房间管理员侧必须能 100% 收到（不要节流过滤掉）
6. **错误处理**：收到 `server.error` 时按 code 处理（30001 跳登录 / 10429 重试）

## 消息去重

```
class WsMessageDedupe {
    constructor(capacity = 10000, ttlMs = 24 * 3600 * 1000) {
        this.cache = new Map();   // msg_id → ts
        this.capacity = capacity;
        this.ttlMs = ttlMs;
    }
    isDuplicate(msgId) {
        const now = Date.now();
        // 清理过期
        if (this.cache.size > this.capacity) {
            for (const [k, v] of this.cache) {
                if (now - v > this.ttlMs) this.cache.delete(k);
                if (this.cache.size < this.capacity * 0.8) break;
            }
        }
        if (this.cache.has(msgId)) return true;
        this.cache.set(msgId, now);
        return false;
    }
}
```

## 完整客户端示例（TypeScript 伪代码）

```
class KickoffWebSocket {
    private ws: WebSocket | null = null;
    private retryCount = 0;
    private retryDelays = [1000, 3000, 9000, 30000, 60000];
    private maxRetries = 10;
    private heartbeatTimer: number | null = null;
    private pongTimeout: number | null = null;
    private dedupe = new WsMessageDedupe();
    private handlers = new Map<string, (data: any) => void>();

    constructor(
        private channels: string[],     // 如 ['room:12345']
        private [敏感内容已脱敏] => Promise<string>,
    ) {}

    async connect() {
        const 敏感凭据：[已脱敏] this.getToken();
        const url = `wss://api.kickoff.tv/ws/v1/client?敏感凭据：[已脱敏]
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('[WS] connected', this.channels);
            this.retryCount = 0;
            this.ws?.send(JSON.stringify({ type: 'client.subscribe', data: { channels: this.channels } }));
            this.startHeartbeat();
        };

        this.ws.onmessage = (ev) => {
            const msg = JSON.parse(ev.data);

            // 心跳应答
            if (msg.type === 'server.pong') {
                this.clearPongTimeout();
                return;
            }

            // 消息去重
            if (msg.msg_id && this.dedupe.isDuplicate(msg.msg_id)) return;

            // 错误处理
            if (msg.type === 'server.error') {
                this.handleError(msg.data);
                return;
            }

            // 顶号
            if (msg.type === 'server.kicked') {
                this.cleanup();
                window.location.href = '/login?reason=kicked';
                return;
            }

            // 业务事件分发
            const handler = this.handlers.get(msg.type);
            if (handler) handler(msg.data);
        };

        this.ws.onclose = (ev) => {
            this.cleanup();
            console.log('[WS] closed', ev.code, ev.reason);

            switch (ev.code) {
                case 1000:        // 正常关闭
                case 1001:        // 用户离开
                    return;       // 不重连
                case 4001:        // 鉴权失败
                    window.location.href = '/login';
                    return;
                case 4002:        // 鉴权过期
                    this.reconnect(0);  // refresh 后立即重连
                    return;
                case 4003:        // 无订阅权限
                case 4004:        // 通道不存在
                    return;       // 不重连
                case 4006:        // 顶号
                    window.location.href = '/login?reason=kicked';
                    return;
                case 4429:        // 限流
                    setTimeout(() => this.reconnect(), 60000);
                    return;
                default:
                    this.reconnect();
            }
        };
    }

    on(type: string, handler: (data: any) => void) {
        this.handlers.set(type, handler);
    }

    private startHeartbeat() {
        this.heartbeatTimer = window.setInterval(() => {
            this.ws?.send(JSON.stringify({ type: 'client.ping', ts: Date.now() }));
            this.pongTimeout = window.setTimeout(() => {
                console.warn('[WS] pong timeout, reconnecting');
                this.ws?.close();
            }, 60000);
        }, 30000);
    }

    private clearPongTimeout() {
        if (this.pongTimeout) {
            clearTimeout(this.pongTimeout);
            this.pongTimeout = null;
        }
    }

    private reconnect(forcedDelayMs?: number) {
        if (this.retryCount >= this.maxRetries) {
            console.error('[WS] max retries reached');
            return;
        }
        const delay = forcedDelayMs ?? this.retryDelays[Math.min(this.retryCount, this.retryDelays.length - 1)];
        this.retryCount++;
        setTimeout(() => this.connect(), delay);
    }

    private cleanup() {
        if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
        this.clearPongTimeout();
    }

    private handleError(data: { code: number, message: string, close?: boolean }) {
        console.error('[WS] server.error', data);
        // 按错误码处理（30001 跳登录等）
    }
}

// 使用
const ws = new KickoffWebSocket([`room:${roomId}`], async () => {
    return await refreshTokenIfNeeded();
});

ws.on('live.danmaku.received', (data) => {
    appendDanmaku(data);
});
ws.on('live.enter.global', (data) => {
    showGlobalBroadcast(data);
});

await ws.connect();
```

**对接清单**：

 ✓ 鉴权（JWT query token）

 ✓ 心跳（30s ping + 60s pong timeout）

 ✓ 重连（指数退避 + 重新鉴权）

 ✓ msg_id 去重（24h LRU）

 ✓ Close code 分类处理

 ✓ server.error 错误码映射

 ✓ 关键资金类 HTTP 兜底

 版本：v1.0 · 2026-05-22 · 对齐 PRD v0.2 + conventions.md §16 · 类型码总数 65 个
