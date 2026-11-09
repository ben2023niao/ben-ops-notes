---
id: "doc-06b3444b5279"
title: "Kickoff API 公共规范（接口约定）"
date: "2026-05-22T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Nginx", "CDN", "DNS", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/conventions.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/conventions.md"
sourceSha256: "cb28719de927dab99a62264f975f5ac78fe4f450f49e6360e552dfc0c6a748f7"
sourceSystem: "project-doc"
---

# Kickoff API 公共规范（接口约定）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605220000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BNginx-Kickoff%20API%20%E5%85%AC%E5%85%B1%E8%A7%84%E8%8C%83%EF%BC%88%E6%8E%A5%E5%8F%A3%E7%BA%A6%E5%AE%9A%EF%BC%89.md)

> 整理日期：2026-05-22 00:00｜日期依据：正文日期

> 版本：v1.0（2026-05-22）
> 适用范围：v1 全部业务接口、WebSocket 推送、第三方回调
> 配套：[`docs/prd/`](../prd/) 业务需求 + [`docs/architecture/`](../architecture/) 技术架构 + `packages/contracts/openapi/v1.yaml`（待生成）
>
> 本文档是后端实现、前端集成、Apifox 契约的**唯一权威基线**。OpenAPI 契约据此生成，所有接口必须符合本规范，违反需走 ADR。

## 目录

```
§0  环境与域名（测试 / 预发 / 生产）
§1  总则与设计原则
§2  鉴权与 Token
§3  公共 Request Header
§4  公共 Query 参数
§5  公共 Request Body 包装
§6  公共响应 envelope
§7  错误码全表（5 位正整数）
§8  HTTP 状态码映射
§9  公共字段类型规范（ID / 金额 / 时间 / 掩码）
§10 公共枚举类型字典
§11 分页规范（offset 统一）
§12 限流规范
§13 幂等规范
§14 重试规范
§15 签名规范（支付回调）
§16 WebSocket 公共协议 + 类型码全表
§17 埋点公共结构
§18 安全约束（HTTPS / CORS / CSP）
§19 OpenAPI 文件规范（含 x-prd-id / x-apifox-* 扩展）
§20 字段命名规范
```

---

## §0 环境与域名

### 0.1 Dev（测试环境，当前可用）

物理机：单台 EC2 `54.151.131.132`（新加坡 ap-southeast-1），nginx 反代到本机各服务。

| 子域 | 用途 | 端口（内部） | 备注 |
| --- | --- | --- | --- |
| `https://api-dev.54-151-131-132.sslip.io` | **C 端 Public API + WebSocket 同域入口** | REST → `kickoff-api:8080`；`/ws/*` → `kickoff-ws:8082` | 前端 URL 不变，nginx 按路径拆到不同 Go 进程 |
| `https://admin-dev.54-151-131-132.sslip.io` | **Admin UI + Admin API + API 文档站** | nginx → 静态/`kickoff-admin:8081` | `/` Admin UI / `/api/v1/admin/*` Admin API / `/docs/*` Stoplight Elements |
| `https://upload-dev.54-151-131-132.sslip.io` | **静态资源**（用户上传的图片回显）| nginx 直 serve `/opt/kickoff/services/go-app/uploads/` | 不走后端,纯静态 |

WebSocket：`wss://api-dev.54-151-131-132.sslip.io/ws/v1/client?敏感凭据：[已脱敏] 转发到 `kickoff-ws:8082`）

> sslip.io 是免 DNS 解析的工具域名：`A.B.C.D.sslip.io` 自动解析到 `A.B.C.D`。等正式域名落地后直接迁移,业务代码不动。

### 0.2 Staging（预发，未启用）

未开服。上线前补：`https://api-staging.kickoff.tv` / `https://admin-staging.kickoff.tv` 等。

### 0.3 Production（生产，域名未定）

正式域名待运营/法务确认后补。备选方案：
- 候选 1：`kickoff.tv`（已注册 `[邮箱已脱敏]` 邮箱，但实际 DNS 未指向任何 IP）
- 候选 2：业务方提供的国别域名

**所有代码 / 配置 / 文档目前均不应硬编码正式域名**。等域名定后只改 `services/go-app/config/config.prod.yaml` + `packages/contracts/openapi/v1.yaml#servers` 两处。

### 0.4 访问方式

| 用户 | 入口 |
| --- | --- |
| 前端调 API | `https://api-dev.54-151-131-132.sslip.io/api/v1/...`（带 `Authorization: Bearer <jwt>`）|
| 运营登录后台 | 浏览器访问 `https://admin-dev.54-151-131-132.sslip.io/` |
| 看接口文档 | 浏览器访问 `https://admin-dev.54-151-131-132.sslip.io/docs/` |
| 查图片资源 | `https://upload-dev.54-151-131-132.sslip.io/<相对路径>`（由上传接口返回完整 URL）|

证书：dev 环境用 sslip.io 子域 + Let's Encrypt 自动签发。

---

## §1 总则与设计原则

1. **接口风格**：REST + JSON over HTTPS；实时推送用 WebSocket
2. **API 版本**：URL 路径前缀 `/api/v1/`；不在 Header 或 query 里区分版本
3. **统一响应**：HTTP 状态码 + body 业务码**双轨**
   - HTTP 4xx/5xx：transport / 协议层错误（参数错 / 鉴权失败 / 限流 / 服务异常）
   - HTTP 200 + body.code≠0：业务层错误（余额不足 / 押注超限 / 已封盘）
   - HTTP 200 + body.code=0：业务成功
4. **字符编码**：UTF-8
5. **字段命名**：snake_case（含 JSON / URL query / Header 自定义部分）
6. **时间统一**：服务端时间戳 UTC，序列化时按 ISO 8601 + Unix ms 双字段
7. **不允许**：
   - 不使用 GET 做修改（GET 必须幂等只读）
   - 不在响应 body 里返回敏感原文（手机号 / 密码 / token 必须掩码或返回时只显式发一次）
   - 不在 URL query 里传 token（必须走 `Authorization` Header）

---

## §2 鉴权与 Token

### 2.1 JWT 双 Token

| Token | 用途 | 有效期 | 存储位置（前端） |
| --- | --- | --- | --- |
| `access_token` | 调用 API | **2 小时** | localStorage / sessionStorage |
| `refresh_token` | 刷新 access | **30 天**；绑定设备指纹 | localStorage（推荐 HttpOnly Cookie，但 v1 简化） |

### 2.2 鉴权流程

```
1. 登录 → POST /auth/login → 返回 { access_token, refresh_token, expires_in }
2. 每次 API 调用：Authorization: Bearer <access_token>
3. access_token 过期 → 401 + body.code=30002
4. 前端用 refresh_token → POST /auth/refresh → 拿新 access
5. refresh_token 也过期 → 跳登录页
```

前端对接约定：

- `401 + code=30002`：仅代表 access token 过期；前端必须静默调用 `POST /api/v1/auth/refresh` 并重放原请求一次。
- `401 + code=30003`：代表 token 签名、格式、类型或登录态异常；前端应清理本地登录态并引导重新登录，不做 refresh 重试。
- `POST /api/v1/auth/refresh` 本身失败时不得递归刷新；清理登录态并提示重新登录。
- 多个接口同时收到 `30002` 时，前端应做 single-flight，复用同一个 refresh 请求，避免并发轮换 refresh token。

### 2.3 后台鉴权

后台 API（`/api/v1/admin/**`）独立 audience：

- `access` 1h / `refresh` 8h
- 强制 2FA（TOTP）
- IP 白名单（按账号配置）

### 2.4 推流鉴权

主播不持有任何 JWT。OBS 推流时 SRS / 云直播校验 stream_key HMAC，业务侧不暴露。

---

## §3 公共 Request Header

| Header | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Authorization` | 鉴权接口必填 | `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | JWT；C 端用户、后台、不同 audience |
| `Idempotency-Key` | **资金写接口必填** | `Idempotency-Key: 5e2d4f8a-...-...` | UUID v4；24h 内同 UID + 同 key 视为同一请求 |
| `X-Trace-Id` | 可选 | `X-Trace-Id: 1a2b3c4d` | 客户端生成；服务端 echo 回响应 envelope |
| `X-Device-Fingerprint` | 注册 / 登录 / 敏感操作必填 | `X-Device-Fingerprint: dfp_a1b2c3` | 客户端指纹哈希（fingerprint.js 等） |
| `X-Client-Version` | 推荐 | `web-1.2.3` / `h5-1.2.3` | 客户端版本，便于兼容性判定 |
| `X-Client-Platform` | 推荐 | `web` / `h5` / `admin` | 客户端平台 |
| `Accept-Language` | 可选 | `zh-CN` | v1 仅 zh-CN |
| `Content-Type` | POST/PUT 必填 | `application/json; charset=utf-8` | — |
| `Accept` | 可选 | `application/json` | — |

### 3.1 资金写接口的强制 Header

充值 / 提现 / 兑换 / 押注 / 打赏 5 类接口必填：

- `Authorization`
- `Idempotency-Key`
- `X-Device-Fingerprint`

缺失任一 → HTTP 400 + body.code=10001（或 10006 当 `Idempotency-Key` 缺失）。

---

## §4 公共 Query 参数

### 4.1 分页（offset 统一）

```
GET /api/v1/me/recharge-records?page=1&size=20&sort=created_at:desc
```

| 参数 | 类型 | 默认 | 范围 | 说明 |
| --- | --- | --- | --- | --- |
| `page` | int | 1 | ≥ 1 | 页码 |
| `size` | int | 20 | 1 - 100 | 单页条数 |
| `sort` | string | 业务默认 | `<field>:asc\|desc` | 排序字段，逗号分隔多字段 |

### 4.2 时间范围筛选

```
GET /api/v1/admin/orders/bets?from=2026-07-13&to=2026-07-15
GET /api/v1/admin/orders/bets?from_ts=1719404400000&to_ts=1719491000000
```

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `from` | string ISO 8601 date | 起（含） |
| `to` | string ISO 8601 date | 止（含） |
| `from_ts` | int64 | Unix ms 时间戳起（含） |
| `to_ts` | int64 | Unix ms 时间戳止（含） |

ISO 与 ts 二选一传，同时传以 `*_ts` 为准。

### 4.3 状态筛选

```
GET /api/v1/predict/activities?status=ing       # 单状态
GET /api/v1/predict/activities?status=ing,wait  # 多状态（逗号分隔）
```

状态字符串按各模块的标准枚举（§10）。

### 4.4 搜索

```
GET /api/v1/admin/users?q=user2891
```

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `q` | string | 全文搜索关键字，按业务字段（用户名 / ID / 手机号末 4 位 等） |

### 4.5 字段筛选

不开放 `fields=` 字段裁剪（v1 不做）；接口返回完整 schema。

---

## §5 公共 Request Body 包装

### 5.1 一般接口

不强制 envelope，直接业务字段：

```json
POST /api/v1/auth/register
{
  "account": "alex_kk",
  "nickname": "Alex",
  "password": "abc12345",
  "agree_18plus": true
}
```

### 5.2 资金写接口

幂等键走 Header（`Idempotency-Key`），body 仍是业务字段：

```http
POST /api/v1/predict/bet
Idempotency-Key: 5e2d4f8a-1b2c-4d5e-9f0a-1b2c3d4e5f6a
```

```json
{
  "activity_id": "1234567890",
  "option_key": "france_win",
  "amount_diamond": 5000
}
```

### 5.3 文件上传（v1 仅头像 / 运营素材）

`multipart/form-data`：

```http
POST /api/v1/me/avatar
Content-Type: multipart/form-data; boundary=...

--boundary
Content-Disposition: form-data; name="file"; filename="avatar.jpg"
Content-Type: image/jpeg

<binary>
--boundary--
```

服务端二次校验 magic number + 大小（头像 < 2MB）。

---

## §6 公共响应 envelope

### 6.1 标准 envelope

**所有 HTTP 200 响应**统一结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... },
  "trace_id": "1a2b3c4d5e6f",
  "timestamp": 1719404400000
}
```

| 字段 | 类型 | 必返 | 说明 |
| --- | --- | --- | --- |
| `code` | int | 是 | 业务码；`0` 成功，**正整数 5 位**为错误（如 `20101`） |
| `message` | string | 是 | 中文消息；成功时 `ok`，错误时给用户友好提示 |
| `data` | object \| array \| null | 是 | 业务数据；错误时为 `null` |
| `trace_id` | string | 是 | 链路追踪 ID；服务端生成或 echo 客户端 `X-Trace-Id` |
| `timestamp` | int64 | 是 | 服务端响应时间 Unix ms |

### 6.2 HTTP 4xx/5xx 响应

仍按 envelope 结构返回（不裸返错误字符串）：

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "code": 30001,
  "message": "未登录",
  "data": null,
  "trace_id": "abc",
  "timestamp": 1719404400000
}
```

### 6.3 多字段校验错误

`data` 携带 `errors` 数组：

```json
{
  "code": 10001,
  "message": "请求参数错误",
  "data": {
    "errors": [
      { "field": "password", "code": 10003, "message": "密码格式不符" },
      { "field": "account", "code": 10004, "message": "账号已被注册" }
    ]
  },
  "trace_id": "abc",
  "timestamp": 1719404400000
}
```

---

## §7 错误码全表（5 位 + 负号）

### 7.1 规范

- 成功：`0`
- 错误：**正整数 5 位**，按段划分（与 PRD `product-prd.md §6.5` 一致）
- 大段：
  - `1xxxx` 系统错误（含参数 / 限流 / 服务异常 / 通道）
  - `2xxxx` 业务错误（资金 / 押注 / 直播 / 兑换 等）
  - `3xxxx` 权限错误（未登录 / 未实名 / 等级 / 冻结）

客户端判定：

```ts
if (resp.code === 0) { /* 成功 */ }
else { /* 失败，按 resp.code 区分系统错/业务错/权限错 */ }
```

Go 端常量：

```go
const (
    OK                     = 0
    ErrParam               = 10001
    ErrInsufficientBalance = 20101
    ErrUnauthorized        = 30001
)
```

### 7.2 系统错误（1xxxx）

| 业务码 | HTTP | 含义 | 用户提示 |
| --- | --- | --- | --- |
| `10001` | 400 | 参数缺失 / 格式错 | 请求参数错误 |
| `10002` | 400 | 参数值越界 | 参数取值非法 |
| `10003` | 400 | 字段格式不符（如密码） | 字段格式错误 |
| `10004` | 409 | 资源冲突（账号已注册等） | 资源已存在 |
| `10005` | 415 | Content-Type 错误 | 内容类型错误 |
| `10006` | 400 | 幂等键缺失 | 幂等键缺失 |
| `10007` | 409 | 幂等键冲突（同 key 不同 body） | 幂等键冲突 |
| `10404` | 404 | 资源不存在 | 资源不存在 |
| `10408` | 408 | 请求超时 | 请求超时 |
| `10429` | 429 | 限流 | 请求过于频繁 |
| `10500` | 500 | 服务端异常 | 服务异常，请稍后重试 |
| `10502` | 502 | 上游服务不可用 | 网关错误 |
| `10503` | 503 | 服务降级 | 服务暂时不可用 |
| `10504` | 504 | 上游超时 | 上游超时 |
| `10901` | 503 | 支付通道异常 | 支付通道暂不可用 |
| `10902` | 503 | 短信通道异常 | 验证码发送失败（v0.2 已无验证码，预留） |
| `10903` | 503 | 直播源站异常 | 直播暂不可用 |
| `10904` | 503 | CDN 异常 | 直播加载失败 |

### 7.3 业务错误（2xxxx）

#### 钱包 / 资金（201xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20101` | 200 | RMB 余额不足 |
| `20102` | 200 | 钻石余额不足 |
| `20103` | 200 | 提现金额超日限额（5000 RMB） |
| `20104` | 200 | 提现金额超月限额（50000 RMB） |
| `20105` | 200 | 首充冷却期内不可提现（14 天） |
| `20106` | 200 | KYC 未完成，超过单笔免实名阈值 |
| `20107` | 200 | 提现订单已处理（不可撤销） |
| `20108` | 200 | 充值订单已超时 |
| `20109` | 200 | 充值订单已支付 |
| `20110` | 200 | 兑换日次数超限（反向 5 次/天） |
| `20111` | 200 | 兑换金额超范围 |

#### 押注 / 竞猜（202xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20201` | 200 | 活动已封盘 |
| `20202` | 200 | 活动状态不允许押注（未开始 / 已开奖等） |
| `20203` | 200 | 单次押注金额超全局或活动上限 |
| `20204` | 200 | 今日累计押注超全局风控上限 |
| `20205` | 200 | 押注金额低于最低 100 钻 |
| `20206` | 200 | 押注金额高于单次最高 50000 钻 |
| `20207` | 200 | 活动不存在 |
| `20208` | 200 | 选项不存在 |
| `20209` | 200 | 活动已被退单 |
| `20210` | 200 | 主播禁止参与押注（防内幕） |

#### 打赏（203xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20301` | 200 | 房间未开播 |
| `20302` | 200 | 房间已被封禁 |
| `20303` | 200 | 打赏频率超限（连击合并外） |

#### 弹幕（204xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20401` | 200 | 弹幕功能关闭 |
| `20402` | 200 | 弹幕字数超统一上限 |
| `20403` | 200 | 弹幕频率超限（< 3s/条） |
| `20404` | 200 | 弹幕命中敏感词 |
| `20405` | 200 | 用户已被禁言 |

#### 直播间 / 主播（205xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20501` | 200 | 房间不存在 |
| `20502` | 200 | 房间未开播 |
| `20503` | 200 | 房间已被封禁 |
| `20504` | 200 | 推流凭据失效（被轮换） |
| `20505` | 200 | 主播多设备并发拒绝（R-108） |

#### 比赛（206xx）

| 业务码 | HTTP | 含义 |
| --- | --- | --- |
| `20601` | 200 | 比赛不存在 |
| `20602` | 200 | 比赛状态错误（已结束改比分等） |

### 7.4 权限错误（3xxxx）

| 业务码 | HTTP | 含义 | 用户提示 |
| --- | --- | --- | --- |
| `30001` | 401 | 未登录 / token 缺失 | 请先登录 |
| `30002` | 401 | token 过期 | 登录已过期，请重新登录 |
| `30003` | 401 | token 无效 | 登录态异常 |
| `30004` | 401 | refresh token 无效 / 已撤销 | 请重新登录 |
| `30005` | 401 | 设备指纹不匹配 | 设备已变更，请重新登录 |
| `30006` | 401 | 账号被其他设备顶号 | 账号已在其他设备登录 |
| `30007` | 403 | 未实名（KYC） | 请先完成实名认证 |
| `30008` | 403 | 历史保留，不再用于等级特权 | 请联系客服 |
| `30009` | 403 | 账号已冻结 | 账号已冻结，请联系客服 |
| `30010` | 403 | 账号已封禁 | 账号已封禁，请联系客服 |
| `30011` | 403 | 未勾选 18+ 协议 | 请阅读并同意用户协议 |
| `30101` | 403 | 后台无权限（RBAC） | 无权限访问 |
| `30102` | 403 | 后台无房间权限（房间管理员） | 无该房间权限 |
| `30103` | 403 | 后台 2FA 未通过 | 请完成二次验证 |
| `30104` | 403 | 后台 IP 非白名单 | IP 不在白名单 |

### 7.5 错误码使用规范

1. HTTP 状态码与业务码**双轨**对应，互不替代
2. 错误码**只增不删**，废弃的错误码标记 `deprecated` 但保留段位
3. 新增错误码必须先在本表登记后才能写入代码
4. 错误码字典由 `internal/pkg/kit/errcode/codes.go` 统一定义，前端从 OpenAPI 生成 TS 常量

---

## §8 HTTP 状态码映射

| HTTP | 用法 | 典型场景 |
| --- | --- | --- |
| 200 | 业务成功 OR 业务失败 | 详见 body.code |
| 201 | 资源创建成功 | 注册成功（可选；v1 用 200） |
| 204 | 无内容 | 删除成功，无返回（v1 不用） |
| 301 / 302 | 重定向 | 不在 API 使用 |
| 304 | 缓存未变更 | ETag（v2 引入，v1 不用） |
| 400 | 请求参数错 | 字段缺失 / 格式错 / Content-Type 错 |
| 401 | 未鉴权 | token 缺失 / 过期 / 无效 |
| 403 | 已鉴权但无权限 | RBAC / 等级 / 冻结 / 实名 |
| 404 | 资源不存在 | 用户 / 订单 / 比赛 不存在 |
| 408 | 请求超时（罕用） | 长轮询超时 |
| 409 | 资源冲突 | 账号已注册 / 幂等键冲突 |
| 415 | Content-Type 不支持 | 上传错误格式 |
| 422 | 校验失败（v1 不用，用 400） | — |
| 429 | 限流 | IP / UID 超频 |
| 500 | 服务端异常 | panic / 未捕获 |
| 502 | 网关错误 | 上游 service 不可用 |
| 503 | 服务降级 | 通道异常 / 直播源站异常 |
| 504 | 上游超时 | DB / 外部 API 超时 |

---

## §9 公共字段类型规范

### 9.1 ID 类（雪花 BIGINT）

**所有 BIGINT ID 在 JSON 中用 string 传**，避免 JS 精度丢失。

```json
{
  "user_id": "1234567890123456789",
  "bet_id": "9876543210987654321",
  "activity_id": "1111222233334444555"
}
```

OpenAPI schema：

```yaml
UserId:
  type: string
  pattern: '^[0-9]+$'
  example: "1234567890123456789"
  description: 雪花 ID，64 位整数序列化为 string
```

Go 端 json tag：

```go
type User struct {
    ID int64 `json:"id,string"`
}
```

### 9.2 金额类

| 货币 | DB 类型 | JSON 类型 | JSON 示例 | 说明 |
| --- | --- | --- | --- | --- |
| RMB | DECIMAL(14,2) | **string** | `"234.50"` | 必精确到 2 位小数 |
| 钻石 | BIGINT | **number** | `52400` | 整数语义；安全在 JS Number 范围 |

OpenAPI schema：

```yaml
MoneyRMB:
  type: string
  pattern: '^[0-9]+(\.[0-9]{2})?$'
  example: "234.50"
  description: RMB 金额，DECIMAL(14,2) 序列化为 string

MoneyDiamond:
  type: integer
  format: int64
  minimum: 0
  example: 52400
  description: 钻石数量，整数
```

**钻石总池量极大**时（如全平台奖池）若 > 2^53，则**升级为 string**。v1 单池不超 2^32 钻石，无风险。

### 9.3 时间类（双字段）

ISO 8601 字符串 + Unix 毫秒时间戳同时返回：

```json
{
  "created_at": "2026-07-15T03:00:00+08:00",
  "created_ts": 1719404400000
}
```

| 字段后缀 | 类型 | 说明 |
| --- | --- | --- |
| `_at` | string (ISO 8601) | 人读 |
| `_ts` | int64 (Unix ms) | 机读 |

请求中接受任一格式：

| Query | 含义 |
| --- | --- |
| `from=2026-07-15` | ISO date |
| `from=2026-07-15T03:00:00+08:00` | ISO datetime |
| `from_ts=1719404400000` | Unix ms |

### 9.4 枚举类

UPPER_SNAKE_CASE 英文 + 中文 `description`：

```yaml
OrderStatus:
  type: string
  enum: [PENDING_PAYMENT, PAID, COMPLETED, TIMEOUT, CANCELLED]
  description: |
    订单状态：
    - PENDING_PAYMENT: 待支付
    - PAID: 已支付
    - COMPLETED: 已完成（含记账）
    - TIMEOUT: 超时
    - CANCELLED: 已取消
```

### 9.5 布尔类

```json
{ "is_first_recharge": true, "agree_18plus": true }
```

字段名前缀 `is_` / `has_` / `can_` / `agree_`。

### 9.6 掩码字段

敏感字段在响应中**自动掩码**，需查看完整值通过专用接口：

| 字段 | 掩码格式 | 完整值接口 |
| --- | --- | --- |
| `phone` | `138****1234` | 仅后台超管，专用接口 + 审计 |
| `email` | `abc****@gmail.com` | 同上 |
| `alipay_account` | `ali****@gmail.com` | 后台财务 / 房间管理员（提现订单视图） |
| `id_card` | `110105******1234` | 仅后台超管 |
| `bank_card` | `**** **** **** 1234` | — |
| `stream_key` | `sk_****_****_***184` | 仅房间管理员可查（专用接口 + 二次确认） |

字段命名约定：

```json
{
  "phone_masked": "138****1234",  // 默认掩码
  "phone": null                    // 默认不返回
}
```

完整值响应：

```json
{ "phone": "[敏感内容已脱敏]" }
```

### 9.7 空值

- 缺失字段用 `null`（不用空字符串 `""`、空数组 `[]`、不返回）
- 数组类字段**没有数据时返回空数组 `[]`**（不返回 null）
- OpenAPI 中明确 `nullable: true`

---

## §10 公共枚举类型字典

### 10.1 货币

```
RMB | DIAMOND
```

### 10.2 用户状态

```
ACTIVE (正常) | FROZEN (冻结) | BANNED (封禁) | DELETED (已注销)
```

### 10.4 充值订单状态

```
PENDING_PAYMENT | PAID | COMPLETED | TIMEOUT | CANCELLED | PAID_BUT_FAIL_LEDGER
```

### 10.5 提现订单状态

```
SUBMITTED | UNDER_REVIEW | AUTO_APPROVED | APPROVED | REJECTED | TRANSFERRING | TRANSFERRED | TRANSFER_FAILED
```

### 10.6 押注订单状态

```
PLACED | PENDING_SETTLE | WON | LOST | REFUNDED | SETTLE_FAILED
```

### 10.7 竞猜活动状态

```
DRAFT (草稿) | UPCOMING (未开始) | OPEN (进行中) | CLOSED (待开奖) | SETTLED (已开奖) | REFUNDED (已退单)
```

### 10.8 比赛状态

```
SCHEDULED (未开赛) | LIVE (进行中) | ENDED (已结束) | CANCELLED (已取消)
```

### 10.9 比赛阶段

```
GROUP | R16 | QF | SF | THIRD_PLACE | FINAL | FRIENDLY
```

### 10.10 直播间状态

```
PREPARING (筹备) | LIVE (直播中) | DISCONNECTED (断流) | ENDED (已结束) | BANNED (封禁)
```

### 10.11 主播状态

```
ON_DUTY (在班) | RESTING (休息) | BANNED (封禁) | PENDING_REVIEW (待审) | TERMINATED (离职)
```

### 10.12 房间类型

```
THEME (主题房) | PUBLIC (公共房)
```

### 10.13 后台角色

```
super | ops | room_admin | finance | risk | moderator
```

### 10.14 风控严重度

```
LOW | MED | HIGH
```

### 10.15 风控告警状态

```
PENDING | HANDLING | RESOLVED | IGNORED
```

### 10.16 通道（v0.2 抽象）

```
（待 ADR-0010 决定具体清单，OpenAPI 字段为 string 不写死 enum）
```

---

## §11 分页规范（offset 统一）

### 11.1 请求

```
GET /api/v1/me/recharge-records?page=1&size=20&sort=created_at:desc
```

| 参数 | 类型 | 默认 | 范围 |
| --- | --- | --- | --- |
| `page` | int | 1 | ≥ 1 |
| `size` | int | 20 | 1 - 100 |
| `sort` | string | 业务默认 | `<field>:asc\|desc`，多字段逗号分隔 |

### 11.2 响应

```json
{
  "code": 0,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1234,
      "total_pages": 62,
      "has_more": true
    }
  },
  ...
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `items` | array | 列表数据 |
| `pagination.page` | int | 当前页码 |
| `pagination.size` | int | 当前页大小 |
| `pagination.total` | int | 总条数 |
| `pagination.total_pages` | int | 总页数 = `ceil(total/size)` |
| `pagination.has_more` | bool | 是否有下一页 |

### 11.3 大数据集场景

`total` 查询慢（如审计日志千万级）：

- 仅返回 `has_more`，省略 `total` / `total_pages`
- OpenAPI schema 中标记 `total: nullable`

---

## §12 限流规范

### 12.1 默认策略

| 维度 | 默认 | 备注 |
| --- | --- | --- |
| 全局 IP | 60 req/min | 防 抗压能力测试 |
| UID 维度 | 30 req/min/API | 防滥用 |
| 押注接口 | 5 req/s/UID | 防刷单 |
| 弹幕入站 | 1 req/3s/UID | 客户端节流 |
| 打赏接口 | 10 req/s/UID（连击合并） | — |
| 充值发起 | 5 req/min/UID + 5 req/min/IP | 防恶意刷单 |
| 登录失败 | 5 次/账号 → 5min 锁定 | 双维度（账号 + IP） |
| 注册 | 同设备 24h ≤ 5 次 / 同 IP ≤ 10 次 | 防垃圾账号 |
| WebSocket 连接 | 单 UID ≤ 5 个并发 WS 连接 | — |

### 12.2 限流响应

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json
```

```json
{
  "code": 10429,
  "message": "请求过于频繁",
  "data": {
    "retry_after_sec": 60
  },
  "trace_id": "abc",
  "timestamp": 1719404400000
}
```

`Retry-After` Header（HTTP 标准）+ body.data.retry_after_sec（业务字段）双轨。

### 12.3 限流算法

- 滑动窗口 + Redis ZSET（精确）
- 关键资金接口走 singleflight 防击穿

---

## §13 幂等规范

### 13.1 强制范围

**资金写接口必须**：

- POST `/wallet/recharge/init`
- POST `/wallet/withdraw/submit`
- POST `/wallet/exchange`
- POST `/predict/bet`
- POST `/live/room/{id}/tip`

### 13.2 协议

客户端：

```http
POST /api/v1/predict/bet
Idempotency-Key: 5e2d4f8a-1b2c-4d5e-9f0a-1b2c3d4e5f6a
```

- 必为 UUID v4 或同等熵的字符串（16-64 字符）
- 单次请求生成一次，重试时**复用同一 key**
- 24h 内同 UID + 同 key 视为同一请求

服务端：

1. Redis `SETNX idem:{uid}:{key} 1 EX 86400` 失败 → 查首次结果返回
2. DB UNIQUE `(user_id, idempotency_key)` 双保险
3. 同 key 不同 body → 409 + `10007`

### 13.3 客户端重试

- 自动重试网络错误（5xx / timeout）；UI 不显示
- 业务错误（4xx / 200 + code≠0）不自动重试
- 重试间隔：指数退避 1s / 3s / 9s 最多 3 次
- 重试时 `Idempotency-Key` 不变

---

## §14 重试规范（客户端）

| 错误类型 | 是否重试 | 间隔 | 上限 |
| --- | --- | --- | --- |
| 网络错误（无响应） | 是 | 1s/3s/9s | 3 次 |
| HTTP 500/502/503/504 | 是（幂等接口） | 1s/3s/9s | 3 次 |
| HTTP 408 | 是（幂等接口） | 1s | 3 次 |
| HTTP 429（带 Retry-After） | 是 | 按 Retry-After | 1 次 |
| HTTP 401（access 过期） | 是 | 调 refresh 后立即重试 | 1 次 |
| HTTP 4xx 其他 | **否** | — | — |
| HTTP 200 + body.code≠0 | **否**（业务错误，提示用户） | — | — |

---

## §15 签名规范（支付回调）

> v0.2 支付通道方案 TBD。本节按"通用三方回调"约定：

### 15.1 微信支付（v3）

```http
POST /pay/v1/callback/wechat
Wechatpay-Signature: <base64>
Wechatpay-Timestamp: 1719404400
Wechatpay-Nonce: <random>
Wechatpay-Serial: <cert_serial>
```

验签：`Signature = sign(timestamp || \n || nonce || \n || body, platform_pubkey)`

### 15.2 支付宝（RSA2）

```http
POST /pay/v1/callback/alipay
```

Body 含 `sign` / `sign_type` 字段；验签算法 RSA2。

### 15.3 第三方聚合通道（占位）

通用约定：

| Header | 说明 |
| --- | --- |
| `X-Channel` | 通道标识 |
| `X-Signature` | HMAC-SHA256（key + nonce + ts + body） |
| `X-Timestamp` | Unix s |
| `X-Nonce` | 16+ 字符随机 |

服务端校验：
- 时间偏差 < 5min
- Nonce 24h 内不可重用（Redis SET）
- Signature 验签

---

## §16 WebSocket 公共协议 + 类型码全表

### 16.1 通道清单

| 通道 | URL | 说明 | 鉴权 |
| --- | --- | --- | --- |
| C 端统一连接 | `/ws/v1/client` | H5/Web 统一入口；登录用户自动订阅个人通知，进入页面后上行订阅直播间/比赛 | JWT 可选（query string `?敏感凭据：[已脱敏] |
| 主播端统一连接 | `/ws/v1/streamer` | 主播工作台统一入口；订阅直播间/比赛事件 | 主播 JWT |
| 直播间（Deprecated） | `/ws/v1/live/{room_id}` | 旧 H5 兼容入口；新版不再接 | JWT 可选 |
| 钱包（Deprecated） | `/ws/v1/wallet` | 旧 H5 兼容入口；新版不再接 | JWT |
| 比赛（Deprecated） | `/ws/v1/match/{match_id}` | 旧 H5 兼容入口；新版不再接 | JWT 可选 |
| 后台事件流 | `/ws/v1/admin/events` | 风控告警 / 对账差异 / KPI 实时 | Admin JWT |
| 房间管理员监控 | `/api/v1/admin/ws/rooms/{id}/danmaku` | 房间弹幕 / 观众进出 / 打赏；后台同源部署推荐路径 | Admin JWT + 房间权限 |

### 16.2 鉴权

```
ws://kickoff.tv/ws/v1/client?敏感凭据：[已脱敏]
```

- 鉴权失败：连接关闭，close code `4001`
- 鉴权过期：连接关闭，close code `4002`（客户端拿 refresh 后重连）

### 16.3 消息 envelope（双向通用）

```json
{
  "type": "live.danmaku.received",
  "msg_id": "01H9XYZ-...-ABC",
  "ts": 1719404400123,
  "trace_id": "abc123",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 类型码（见 §16.6） |
| `msg_id` | string | 消息唯一 ID（ULID / UUID），客户端去重 |
| `ts` | int64 | 服务端 Unix ms |
| `trace_id` | string | 链路追踪 |
| `data` | object | 类型相关 payload |

### 16.4 心跳

- 客户端每 **30s** 发 `client.ping`
- 服务端 5s 内回 `server.pong`
- 客户端 60s 无 pong → 视为断开 → 重连
- `client.ping` 只用于 WebSocket 连接保活,**不更新直播间状态**
- 主播端开播成功后,还必须每 **15s** 在 `/ws/v1/streamer` 发送 `streamer.live.heartbeat`
- 后端连续 **60s** 未收到主播业务心跳时,自动把直播间置为 `ENDED`,并向房间频道广播 `room.status.ended`,其中 `reason=streamer_heartbeat_timeout`

```json
{ "type": "client.ping", "ts": 1719404400000 }
{ "type": "server.pong", "ts": 1719404400123 }
```

主播业务心跳示例:

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

### 16.5 重连规则

| 事件 | 客户端行为 |
| --- | --- |
| 网络断开 | 指数退避：1s / 3s / 9s / 30s / 60s |
| 最多重试 | 10 次 |
| 每次重连 | 重新鉴权（带最新 access token） |
| 服务端关闭（close code 4xxx） | 视 code 决定（详见 §16.7） |

重连后服务端**不补推**断开期间的消息（除关键资金类，走 `/wallet/notifications` HTTP 拉取兜底）。

### 16.6 类型码全表

> 命名规则：`<channel>.<entity>.<action>`，全小写下划线 + 点分隔。

#### 通用控制（双向）

| 类型码 | 方向 | 说明 |
| --- | --- | --- |
| `client.ping` | C → S | 心跳 |
| `server.pong` | S → C | 心跳应答 |
| `client.subscribe` | C → S | 订阅公开频道，只允许 `room:{room_id}` / `match:{match_id}` |
| `client.unsubscribe` | C → S | 退订公开频道 |
| `streamer.live.heartbeat` | 主播 → S | 主播开播后的业务心跳；每 15s 发送一次，60s 超时自动下播 |
| `server.subscribed` | S → C | 订阅确认 |
| `server.unsubscribed` | S → C | 退订确认 |
| `server.error` | S → C | 错误（鉴权失败 / 参数错） |
| `server.kicked` | S → C | 服务端踢下线（顶号 / 封禁） |

`client.subscribe` payload：

```json
{
  "type": "client.subscribe",
  "data": {
    "channels": ["room:12345", "match:67890"]
  }
}
```

安全规则：

- `user:{user_id}` 只能由服务端根据登录 JWT 自动订阅，客户端手动订阅会返回 `server.error`。
- 游客可以连接 `/ws/v1/client`，但只能订阅 `room:*` / `match:*`。
- 主播端连接 `/ws/v1/streamer`，必须使用主播 JWT，只能订阅 `room:*` / `match:*`。
- 主播业务心跳 `streamer.live.heartbeat` 只接受 `/ws/v1/streamer` 的主播 JWT；后端会校验该主播是否拥有 `room_id`、房间是否 `LIVE`、当前 active session 是否匹配。
- 资金操作、打赏、发弹幕仍走 HTTP；WS 只做实时推送和订阅控制。

`server.error` payload：

```json
{
  "type": "server.error",
  "data": {
    "code": 30001,
    "message": "鉴权失败",
    "close": true
  }
}
```

#### 直播间频道 `room:{room_id}`（S → C，经 `/ws/v1/client` 订阅）

| 类型码 | 触发 | data 关键字段 |
| --- | --- | --- |
| `live.danmaku.received` | 收到弹幕（含打赏：`gift_id>0` 时携带 `gift_name / gift_icon_url / quantity / diamond_amount / combo_count`） | `user_id, nickname, color, content, sent_ts, gift_id?, gift_name?, gift_icon_url?, quantity?, diamond_amount?, combo_count?` |
| `live.enter.normal` | 普通进场提示 | `user_id, nickname, is_guest` |

> **重要说明**：
> - 等级特权已下线，不做等级进场差异化或全平台等级广播。
> - **v1 不做"离场推送"**（原型未画，主流直播平台也不推离场）
> - 打赏 v0.4 起合并到 `live.danmaku.received`（不再有独立 `live.tip.combo`），前端按 `gift_id > 0` 判别是否打赏。
| `live.viewer.count.updated` | 观看人数 / 峰值人数（30s 批量推全房间） | `viewer_count, peak_count` |
| `live.system.notice` | 系统消息（房间内） | `level (info/warn), text` |
| `live.muted.notify` | 你被禁言 | `mute_until_ts, reason` |
| `live.user.muted` | 其他用户被禁言 | `user_id, nickname` |
| `live.danmaku.deleted` | 弹幕被删除 | `msg_id, by_admin` |
| `room.status.live` | 房间开播 | `room_id, status, reason?` |
| `room.status.disconnected` | 断流 | `session_id, disconnected_at` |
| `room.status.recovered` | 断流恢复 | `session_id, recovered_at` |
| `room.status.ended` | 关播 | `room_id, status, reason?` |
| `room.title.updated` | 房间标题改了 | `old_title, new_title, by_admin` |
| `room.match.changed` | 关联比赛切换 | `old_match_id, new_match_id` |
| `room.banned` | 房间被封禁 | `reason, until_ts` |

#### 直播间上行（C → S）

| 类型码 | 说明 | data 字段 |
| --- | --- | --- |
| `client.danmaku.send` | 发弹幕（兼 HTTP 兜底；主链路推荐 HTTP POST） | `content` |

弹幕发送默认走 HTTP POST `/live/room/{id}/danmaku`，WS 不强制承担。

#### 钱包个人频道 `user:{user_id}`（S → C，经登录 JWT 自动订阅）

| 类型码 | 触发 | data 字段 |
| --- | --- | --- |
| `wallet.balance.updated` | 余额变动（任何原因） | `rmb_balance, diamond_balance` |
| `wallet.recharge.success` | 充值到账 | `order_no, amount_rmb, bonus_diamond, balance_rmb_after` |
| `wallet.recharge.failed` | 充值失败 | `order_no, reason` |
| `wallet.withdraw.submitted` | 提现申请提交（自己端） | `order_no, amount_rmb` |
| `wallet.withdraw.approved` | 提现放行 | `order_no, amount_rmb` |
| `wallet.withdraw.rejected` | 提现驳回 | `order_no, reason` |
| `wallet.withdraw.success` | 提现到账 | `order_no, actual_amount_rmb` |
| `wallet.withdraw.failed` | 提现转账失败 | `order_no, reason` |
| `wallet.exchange.success` | 兑换成功 | `direction, from_amount, to_amount` |
| `wallet.bet.placed` | 押注成功（含余额变动） | `bet_id, activity_id, amount_diamond, balance_diamond_after` |
| `wallet.bet.settled` | 派彩入账 | `bet_id, payout_diamond, balance_diamond_after, is_winner` |
| `wallet.bet.refunded` | 退单到账 | `bet_id, amount_diamond, balance_diamond_after` |
| `wallet.tip.committed` | 打赏成功（自己端） | `room_id, diamond_amount, balance_diamond_after` |
| `wallet.notification.received` | 站内信 | `title, body, link, severity (info/warn/important)` |

#### 比赛频道 `match:{match_id}`（S → C，经 `/ws/v1/client` 订阅）

| 类型码 | 触发 | data 字段 |
| --- | --- | --- |
| `match.score.updated` | 比分变化（运营录入） | `match_id, score_home, score_away, period` |
| `match.goal.added` | 新增进球 | `match_id, minute, team_code, player, score_home_after, score_away_after` |
| `match.status.changed` | 状态变化 | `match_id, old_status, new_status` |
| `match.mvp.published` | MVP 公布 | `match_id, mvp_player, mvp_team` |

#### 用户个人事件（S → C，经登录 JWT 自动订阅）

| 类型码 | 触发 | data 字段 |
| --- | --- | --- |
| `user.system.announcement` | 系统公告 | `title, body, link, severity` |
| `user.profile.updated` | 后台调整你的资料 | `fields_changed: [...]` |
| `user.frozen` | 账号被冻结 | `reason` |
| `user.unfrozen` | 账号被解冻 | — |

#### 后台事件流 `/ws/v1/admin/events`（S → Admin）

| 类型码 | 触发 | data 字段 |
| --- | --- | --- |
| `admin.risk.alert.new` | 新增风控告警 | `alert_id, rule_id, severity, target_type, target_id` |
| `admin.recon.diff.new` | 对账新差异 | `recon_date, channel, diff_count, diff_amount` |
| `admin.streamer.live` | 主播开播 | `streamer_id, room_id, match_id, started_at` |
| `admin.streamer.ended` | 主播下播 | `streamer_id, session_id, ended_at` |
| `admin.streamer.disconnected` | 主播断流 | `streamer_id, session_id` |
| `admin.payment.callback.failed` | 支付回调失败 | `channel, order_no, reason` |
| `admin.withdraw.high_risk` | 提现高风险新单 | `order_no, user_id, amount_rmb, risk_score` |
| `admin.dashboard.kpi.updated` | 看板 KPI 实时 | `gmv_today, online_users, live_streamers, bets_today` |
| `admin.system.alert` | 系统告警（DB/Redis/Kafka 异常） | `severity, source, message` |

#### 房间管理员监控 `/api/v1/admin/ws/rooms/{id}/danmaku`（S → Admin）

| 类型码 | 触发 | data 字段 |
| --- | --- | --- |
| `admin.room.danmaku` | 房间弹幕（实时） | `msg_id, user_id, nickname, content, forbidden_hit` |
| `admin.room.viewer.enter` | 任意观众进场（**服务端节流：5s 聚合，超量降级为 "N 人进入"**） | `user_id, nickname` 或 `aggregated_count` |
| `admin.room.viewer.leave` | 任意观众离场（**服务端节流：同上**） | `user_id, stay_seconds` 或 `aggregated_count` |
| `admin.room.tip.received` | 打赏到房间 | `user_id, nickname, diamond_amount, combo_count` |
| `admin.room.stats` | 房间实时统计（10s 刷新） | `viewer_count, peak_count, danmaku_count, gmv_diamond` |

### 16.7 WebSocket Close Code

| Code | 含义 | 客户端动作 |
| --- | --- | --- |
| 1000 | 正常关闭 | 不重连（用户主动） |
| 1001 | 远端离开 | 不重连 |
| 1006 | 异常断开 | 自动重连 |
| 1011 | 服务端错误 | 自动重连 |
| **4001** | 鉴权失败（自定义） | 跳登录页 |
| **4002** | 鉴权过期（自定义） | refresh 后重连 |
| **4003** | 无订阅权限 | 不重连，UI 提示 |
| **4004** | 通道不存在 | 不重连 |
| **4429** | 限流（自定义） | 60s 后重连 |
| **4500** | 服务端错误 | 自动重连 |

### 16.8 客户端实现要点

```ts
// 伪代码
class KickoffWebSocket {
  connect(channel: string, 敏感凭据：[已脱敏] { ... }
  on(type: string, handler: (data) => void) { ... }
  send(type: string, data: object) { ... }
  reconnect() { /* 指数退避 + 重新鉴权 */ }
  dedupe(msg_id: string): boolean { /* 24h LRU */ }
}
```

- 必须有消息去重（按 `msg_id`）
- 心跳必须有
- 重连必须重新鉴权
- 关键资金类消息可能丢失 → HTTP 兜底拉取

---

## §17 埋点公共结构

### 17.1 事件结构

```json
{
  "event": "predict_bet_submit",
  "ts": 1719404400000,
  "trace_id": "abc",
  "session_id": "browser_session_uuid",
  "user_id": "1234",
  "device_fp": "dfp_xxx",
  "client_version": "web-1.2.3",
  "platform": "web",
  "ua": "Mozilla/5.0 ...",
  "ip": "auto-by-server",
  "ref": "previous_page_url_or_source",
  "props": {
    "activity_id": "act_xxx",
    "option": "france_win",
    "amount": 1000,
    "rate": 1.85
  }
}
```

### 17.2 上报方式

| 方式 | 触发 |
| --- | --- |
| **服务端中间件**自动上报 | 进入接口（自动带请求字段） |
| 客户端 SDK 主动上报 | 页面浏览 / 点击 / 性能 / 错误 |

### 17.3 事件命名

`<domain>_<action>_<object>`，全小写下划线。30 个核心事件清单见 `docs/api/tracking-events.md`（后续生成）。

---

## §18 安全约束

### 18.1 传输

- HTTPS 强制（TLS 1.2+）
- HSTS 一年
- WebSocket 用 wss://

### 18.2 CORS

C 端 API CORS 仅允许：

```
https://kickoff.tv
https://m.kickoff.tv
https://www.kickoff.tv
```

后台 API 不允许跨域（同源）。

### 18.3 CSP（前端）

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.kickoff.tv;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' wss://kickoff.tv https://api.kickoff.tv;
  frame-ancestors 'none';
```

### 18.4 XSS / CSRF

- 弹幕 / 昵称 / 房间标题 HTML escape
- 后台所有写操作带 CSRF token（双提交）
- C 端 API 用 JWT 不用 Cookie → CSRF 风险低

### 18.5 限制

- 请求 body 最大 1MB（文件上传单独 endpoint）
- URL 长度 ≤ 2048
- 单 Header 长度 ≤ 8KB
- WebSocket 单消息 ≤ 4KB

---

## §19 OpenAPI 文件规范

### 19.1 版本

OpenAPI **3.0.3**（Apifox 完全支持）。不用 3.1（webhook 不稳定）。

### 19.2 文件组织

```
packages/contracts/openapi/
├── v1.yaml                  # 主入口（单文件，Apifox 直接导入）
├── README.md                # 维护规范
└── examples/                # 关键接口示例
```

### 19.3 必填扩展字段

每个 operation：

```yaml
/api/v1/predict/bet:
  post:
    tags: [predict]
    summary: 押注下单
    operationId: predictBet
    x-prd-id: PRED-002             # 关联 PRD 需求 ID
    x-apifox-folder: 竞猜/押注       # Apifox 分组展示
    x-idempotent: true             # 标记幂等接口
    x-rate-limit: 5/s/uid          # 限流规则
    ...
```

### 19.4 命名规则

- `operationId`：camelCase，如 `predictBet` / `walletRecharge` / `adminWithdrawApprove`
- `tags`：小写单词，按 PRD 模块（auth / home / live / schedule / match / predict / member / wallet / admin / hooks / ws）
- schema：PascalCase，如 `PlaceBetRequest` / `PlaceBetResponse` / `Money` / `Pagination`
- 路径：snake_case 资源名 + 复数（user**s** / orders / activities）

### 19.5 强制结构

每个 operation 必有：

- `summary`：中文简短描述
- `description`：详细说明（可空）
- `tags`：至少 1 个
- `operationId`：唯一
- `x-prd-id`：关联 PRD
- 请求 schema（如有 body / query / params）
- `responses` 至少：200 + 400 + 401 + 429 + 500

### 19.6 通用响应（统一引用）

```yaml
components:
  responses:
    Success200:         { ... }
    ErrParam:           { ... }  # 400 10001
    ErrUnauth:          { ... }  # 401 30001
    ErrForbidden:       { ... }  # 403 30007
    ErrNotFound:        { ... }  # 404 10404
    ErrConflict:        { ... }  # 409 10004 / 10007
    ErrRateLimit:       { ... }  # 429 10429
    ErrServer:          { ... }  # 500 10500
```

### 19.7 共享 Schema

```yaml
components:
  schemas:
    # 通用基础
    SnowflakeId: { type: string, pattern: '^[0-9]+$' }
    MoneyRMB:    { type: string, pattern: '^[0-9]+(\.[0-9]{2})?$' }
    MoneyDiamond:{ type: integer, format: int64, minimum: 0 }
    Timestamp:   { type: integer, format: int64 }
    Iso8601:     { type: string, format: date-time }
    Pagination:  { ... }

    # 通用 envelope
    ApiEnvelope: { ... }
    ApiError:    { ... }

    # 业务对象
    User:         { ... }
    Wallet:       { ... }
    Match:        { ... }
    PredictActivity:  { ... }
    PredictBet:   { ... }
    LiveRoom:     { ... }
    Streamer:     { ... }
    RechargeOrder:{ ... }
    WithdrawOrder:{ ... }
    Danmaku:      { ... }
    RiskAlert:    { ... }
    ...
```

### 19.8 安全方案

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: C 端用户 JWT
    adminBearer:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: 后台管理员 JWT
    idempotencyKey:
      type: apiKey
      in: header
      name: Idempotency-Key
      description: 幂等键 UUID v4

security:
  - bearerAuth: []
```

---

## §20 字段命名规范

| 类别 | 规则 | 示例 |
| --- | --- | --- |
| JSON 字段 | snake_case | `user_id`, `created_at`, `bet_amount` |
| URL Path | snake_case 资源名 | `/predict/activities/{id}/options` |
| URL Query | snake_case | `?from_ts=xxx&page=1` |
| Header（标准） | 按 IANA 标准 | `Authorization`, `Content-Type`, `Idempotency-Key` |
| Header（自定义） | X- + Title-Case | `X-Trace-Id`, `X-Device-Fingerprint` |
| WebSocket 类型码 | snake_case + 点分隔 | `live.danmaku.received` |
| 错误码常量 | `ErrXxxYyy` Go 风格 | `ErrInsufficientBalance = 20101` |
| 枚举值 | UPPER_SNAKE_CASE | `PENDING_PAYMENT` |

---

## 附录 A：变更记录

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| v1.0 | 2026-05-22 | 初版，覆盖 §1-§20 全部内容 |

## 附录 B：与 PRD 的关系

- 错误码 / 状态机 / 权限 来自 PRD 各模块定义
- 限流阈值 来自 PRD `product-prd.md §6.4` + 各模块
- WebSocket 推送类型 来自 PRD 各模块 + 技术文档 `architecture/messaging-strategy.md`
- 任何业务规则缺口 → 必须回写 PRD，不在本文档独立扩展
