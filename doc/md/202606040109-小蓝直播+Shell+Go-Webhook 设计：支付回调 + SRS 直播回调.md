---
id: "doc-25dd949e497b"
title: "Webhook 设计：支付回调 + SRS 直播回调"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Nginx", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/webhook-design.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/webhook-design.md"
sourceSha256: "c05f8cd3d407b1a0682c550ea0ebe778194324e9aa2bab0162d1c44cabe34b15"
sourceSystem: "project-doc"
---

# Webhook 设计：支付回调 + SRS 直播回调

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Webhook%20%E8%AE%BE%E8%AE%A1%EF%BC%9A%E6%94%AF%E4%BB%98%E5%9B%9E%E8%B0%83%20%2B%20SRS%20%E7%9B%B4%E6%92%AD%E5%9B%9E%E8%B0%83.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

> 对齐 contracts `/api/v1/hooks/*` 7 个接口（payment 3 + srs 4）。
> 资金安全 + 直播鉴权两个最关键的外部回调入口，必须严格按本文实现。

---

## 1. 总体原则

| 原则 | 落地 |
|---|---|
| **快响应慢处理** | < 100ms 返回 200，业务可异步落地，避免重试风暴 |
| **必持久化原文** | 所有 hook 一进门就写 `payment_callbacks` 表，验签/处理失败也存（审计依据）|
| **必验签** | HMAC-SHA256 / RSA2，密钥从 env 读取 |
| **必幂等** | 资金类用 `wallet_journals.idempotency_key`；SRS 类用业务状态机+乐观锁 |
| **失败可重放** | `payment_callbacks.processed=2` 由定时任务扫描重跑 |
| **fail-open vs fail-close** | 支付回调签名失败 → fail-close（不入账）；SRS 鉴权失败 → fail-close（拒绝推流）|

---

## 2. 支付回调（payment_callback）

### 2.1 接口

| 路径 | 通道 | 验签算法 | 密钥 env |
|---|---|---|---|
| `POST /api/v1/hooks/payment/wechat` | 微信支付 | HMAC-SHA256 + 证书 | `APP_PAY_WECHAT_KEY` |
| `POST /api/v1/hooks/payment/alipay` | 支付宝 | RSA2 (body.sign) | `APP_PAY_ALIPAY_PUBKEY` |
| `POST /api/v1/hooks/payment/generic` | 通用通道（联调用） | HMAC-SHA256(body) | `APP_PAY_GENERIC_KEY` |

**本期实现**：`generic` 完整链路；wechat/alipay 占位（持久化原文 + verified=0 + 返回 200，后续接入真通道时填验签）。

### 2.2 数据流（5 步）

```
┌─────────────────────┐
│   第三方支付平台     │
└──────────┬──────────┘
           │ POST /api/v1/hooks/payment/generic
           │ Header:  X-Signature: <hex>
           │ Body:    {"channel_no":"wx_xxx","order_no":"R20...","amount":"100.00","status":"PAID","paid_at":...}
           ↓
┌─────────────────────────────────────────────────┐
│  hookPaymentCallback handler                    │
│                                                 │
│  STEP 1. 持久化原文                              │
│  ─────────────────                              │
│  INSERT payment_callbacks (                     │
│    channel="generic",                           │
│    callback_type="recharge",                    │
│    third_party_no, order_no,                    │
│    raw_headers, raw_body, signature,            │
│    verified=0, processed=0)                     │
│                                                 │
│  STEP 2. 验签                                    │
│  ───────                                        │
│  expected = HMAC-SHA256(body, APP_PAY_KEY)      │
│  if expected != X-Signature:                    │
│    UPDATE payment_callbacks SET verified=2      │
│    return 200 {"code":0,"message":"ok"}         │
│    （即使签名失败也返回 200，避免第三方重试，    │
│       排查走 verified=2 审计）                   │
│                                                 │
│  STEP 3. 去重                                    │
│  ──────                                         │
│  if payment_callbacks WHERE                     │
│     channel + third_party_no 已存在 processed=1 │
│  → 直接 ACK，不再入账                            │
│                                                 │
│  STEP 4. 业务入账（幂等保护）                    │
│  ─────────                                      │
│  walletService.SettleRechargePaid(              │
│    order_no, channel_no, paid_at)               │
│                                                 │
│  内部:                                          │
│    - SELECT recharge_orders WHERE order_no=...  │
│    - if status == PAID → return nil（幂等）     │
│    - MarkPaid(status: 1→3)                      │
│    - ledger.Post(                               │
│        idempotency_key = "recharge_" + order_no │
│        Direction = IN, Currency = Diamond,      │
│        Entries = [user:UID Debit, platform:     │
│                   recharge Credit])             │
│                                                 │
│  STEP 5. 标记完成                                │
│  ────────                                       │
│  UPDATE payment_callbacks SET                   │
│    verified = 1, processed = 1,                 │
│    processed_at = NOW(3)                        │
│  return 200 {"code":0,"message":"ok"}           │
└─────────────────────────────────────────────────┘
```

### 2.3 错误处理矩阵

| 场景 | HTTP | code | verified | processed | 是否重试 |
|---|---|---|---|---|---|
| 正常入账 | 200 | 0 | 1 | 1 | 否 |
| 签名错误 | 200 | 0 | 2 | 0 | 否（人工查 verified=2）|
| 订单不存在 | 200 | 0 | 1 | 2 | 否（持久化原文留证）|
| 订单已支付（重复回调）| 200 | 0 | 1 | 1 | 否（幂等成功）|
| 入账失败（DB 抖动）| 200 | 0 | 1 | 2 | 是（cron 重扫 processed=2）|

**关键决策**：所有情况都返回 HTTP 200 + body code=0，**让第三方满意，自己背责任**。失败的处理结果记在 `processed` 字段，由我们的 cron 重试，不让第三方触发雪崩。

### 2.4 验签算法（generic）

```go
// 请求头：X-Signature: <hex>
// 请求体：raw bytes（不重新编排）
// 密钥：env APP_PAY_GENERIC_KEY (32 bytes recommended)

mac := hmac.New(sha256.New, []byte(secret))
mac.Write(rawBody)
expected := hex.EncodeToString(mac.Sum(nil))

if !hmac.Equal([]byte(expected), []byte(headerSig)) {
    // 验签失败
}
```

**注意**：用 `hmac.Equal` 而非 `==`，防 timing attack。

---

## 3. SRS 直播回调

### 3.1 接口

| 路径 | 触发时机 | 是否阻塞 |
|---|---|---|
| `POST /api/v1/hooks/srs/on_publish` | OBS 开始推流 | **阻塞**：code !=0 SRS 拒绝推流 |
| `POST /api/v1/hooks/srs/on_unpublish` | OBS 断开推流 | 非阻塞，只是通知 |
| `POST /api/v1/hooks/srs/on_dvr` | 录像分片落盘 | 非阻塞 |
| `POST /api/v1/hooks/srs/on_snapshot` | 截图生成 | 非阻塞 |

### 3.2 SRS 请求格式

SRS 固定格式（不可定制）：

```json
{
  "action": "on_publish",
  "client_id": "abcd1234",
  "ip": "203.0.113.1",
  "vhost": "__defaultVhost__",
  "app": "live",
  "stream": "room_R0001_keyabc",
  "param": "?敏感凭据：[已脱敏]
}
```

`stream` 字段约定格式：`room_{ROOM_NO}_key{STREAM_KEY_LAST_8_HEX}`，或更严：完整密钥放在 `param` 的 query。

### 3.3 on_publish 鉴权流程

```
1. 持久化到 payment_callbacks (channel=srs, callback_type=on_publish)
2. 校验源 IP 在白名单（env APP_SRS_ALLOWED_IPS）—— 不在白名单 → code:403
3. 解析 stream + param 提取 stream_key
4. SELECT live_stream_keys WHERE stream_key=? AND active=1
5. 不存在 / 非 active → code:401（rotated 的 key 自然被拒）
6. 校验 live_rooms.status：
   - 1=未开播 → 允许
   - 2=已在直播 → code:409（同房间不允许并发推流）
   - 4=封禁 → code:403
7. 创建 live_sessions(room_id, streamer_id, status=1, start_at=NOW)
8. UPDATE live_rooms SET status=2, last_start_at=NOW
9. processed=1，返回 200 {"code":0}
```

**关键点**：SRS 只看 body 里的 `code`，**code==0 才放行推流**。HTTP status 必须 200，否则 SRS 当作错误重试。

### 3.4 on_unpublish 流程

```
1. 持久化原文
2. 找最新的 live_sessions WHERE room_id=? AND status=1 ORDER BY start_at DESC LIMIT 1
3. 不存在 → 直接返回 200 {"code":0}（幂等：忽略孤儿 unpublish）
4. UPDATE live_sessions:
     status=2(已结束), end_at=NOW, duration_sec=NOW-start_at
5. UPDATE live_rooms SET status=3(已结束), last_end_at=NOW
6. 异步任务（本期不实现）：
     - 统计本场打赏总额 → live_sessions.total_tip_rmb
     - 统计本场弹幕数 → live_sessions.total_chat
     - 统计峰值在线 → live_sessions.peak_viewers
7. 返回 200 {"code":0}
```

### 3.5 on_dvr / on_snapshot

本期实现：仅持久化原文 + 返回 200。后续接入 OSS 时取出 file 字段同步到房间封面/录像表。

### 3.6 SRS 配置（参考）

```nginx
# srs.conf
vhost __defaultVhost__ {
    http_hooks {
        enabled         on;
        on_publish      http://kickoff-api/api/v1/hooks/srs/on_publish;
        on_unpublish    http://kickoff-api/api/v1/hooks/srs/on_unpublish;
        on_dvr          http://kickoff-api/api/v1/hooks/srs/on_dvr;
        on_snapshot     http://kickoff-api/api/v1/hooks/srs/on_snapshot;
    }
    dvr {
        enabled         on;
        dvr_path        /opt/srs/objs/nginx/html/dvr/[app]/[stream]/[2006]/[01]/[02]/[15].[04].[05].[999].flv;
        dvr_plan        session;
    }
}
```

### 3.7 鉴权策略

| 层 | 措施 |
|---|---|
| L1 网络 | SRS 部署在内网；nginx/ingress 限制 hook 接口来源 IP |
| L2 应用 | `APP_SRS_ALLOWED_IPS` env 白名单二次校验 |
| L3 业务 | stream_key 是密钥（DB 落盘 + 后台轮换） |

SRS 原生不支持 HMAC 签名头。如果要更强签名，可以：
- 在 SRS 前架一层 nginx，nginx 计算签名注入到 hook 请求
- 或者在 stream_key 里嵌时间戳 + HMAC，提高对抗回放的成本

本期实现 L1+L2+L3。

---

## 4. 数据库表使用

### 4.1 payment_callbacks（所有 hook 共用）

```sql
INSERT payment_callbacks (
  id, channel, callback_type,
  third_party_no, order_no,
  raw_headers, raw_body, signature,
  verified, processed,
  client_ip, received_at
)
```

| 字段 | 取值（payment）| 取值（srs）|
|---|---|---|
| channel | wechat/alipay/generic | srs |
| callback_type | recharge | on_publish/on_unpublish/on_dvr/on_snapshot |
| third_party_no | 微信/支付宝交易号 | SRS client_id |
| order_no | 我们的 recharge order_no | SRS stream（路径） |
| raw_headers | HTTP 头 JSON | 同 |
| raw_body | 请求体原文 | 同 |
| signature | 签名字符串 | 空（SRS 无签名）|
| verified | 0/1/2 | 1（不验签，靠 IP 白名单）|
| processed | 0/1/2 | 0/1/2 |

### 4.2 资金链路（payment）

依赖 `recharge_orders` + `wallets` + `wallet_journals` + `wallet_journal_entries`，全部已有 DDL。

### 4.3 直播链路（srs）

依赖 `live_rooms` + `live_sessions` + `live_stream_keys`，全部已有 DDL。

---

## 5. 实现清单

### 5.1 新增文件

```
internal/
├── http/hook/
│   ├── payment.go          payment generic + wechat + alipay handler
│   └── srs.go              srs on_publish/on_unpublish/on_dvr/on_snapshot handler
├── service/hook/
│   ├── payment.go          支付回调业务（验签 → 入账）
│   └── srs.go              直播回调业务（鉴权 → 状态机）
├── repository/hook/
│   └── callback.go         payment_callbacks 表读写
├── repository/live/
│   └── live.go             live_rooms / live_sessions / live_stream_keys
└── model/
    ├── live.go             live 域 GORM 实体
    └── callback.go         payment_callbacks
```

### 5.2 复用现有

- `pkg/cryptox.HMACSHA256Hex`（验签）
- `pkg/ledger.Post`（充值入账）
- `service/wallet.SettleRechargePaid`（资金端口，hook service 调用）
- `pkg/snowflake`（session/callback id）

### 5.3 router 装配

```go
// 内网 hook，不挂业务限流 / 不挂业务 auth
hook := r.Group("/api/v1/hooks")
hook.POST("/payment/wechat",   srcIPCheckMW, paymentH.Wechat)
hook.POST("/payment/alipay",   srcIPCheckMW, paymentH.Alipay)
hook.POST("/payment/generic",  srcIPCheckMW, paymentH.Generic)

hook.POST("/srs/on_publish",   srsIPCheckMW, srsH.OnPublish)
hook.POST("/srs/on_unpublish", srsIPCheckMW, srsH.OnUnpublish)
hook.POST("/srs/on_dvr",       srsIPCheckMW, srsH.OnDvr)
hook.POST("/srs/on_snapshot",  srsIPCheckMW, srsH.OnSnapshot)
```

`srcIPCheckMW` 二选一：env 配置允许的 IP 列表，不在白名单 → 403。

---

## 6. 配置补充

```yaml
# config/config.local.yaml
pay:
  wechat:
    enabled: false      # 本期占位
    merchant_id: ""
  alipay:
    enabled: false
    app_id: ""
  generic:
    enabled: true       # 联调用

srs:
  allowed_ips:           # CIDR / 单 IP 都支持
    - "203.0.113.1/32"
    - "203.0.113.1/8"
```

敏感密钥走 env：
- `APP_PAY_GENERIC_KEY`（32 字节）
- `APP_PAY_WECHAT_KEY`（后续）
- `APP_PAY_ALIPAY_PUBKEY`（后续）

---

## 7. 测试矩阵

| 场景 | hook | 期望 |
|---|---|---|
| 正常充值回调 | payment/generic | DB: recharge.status=PAID, wallet.diamond +N, ledger 配平 |
| 错误签名 | payment/generic | 200 + verified=2 + 余额不变 |
| 重复回调 | payment/generic | 200 + processed=1（幂等），余额不变第二次 |
| 订单不存在 | payment/generic | 200 + verified=1 + processed=2，留证 |
| OBS 推流（正确 key）| srs/on_publish | code:0 + session 创建 + room.status=2 |
| OBS 推流（错 key）| srs/on_publish | code:401 + SRS 拒推 |
| OBS 推流（同房间并发）| srs/on_publish | code:409 拒第二条 |
| OBS 断开 | srs/on_unpublish | session.status=2 + room.status=3 |
| 非白名单 IP | 任何 hook | 403（不进业务）|
