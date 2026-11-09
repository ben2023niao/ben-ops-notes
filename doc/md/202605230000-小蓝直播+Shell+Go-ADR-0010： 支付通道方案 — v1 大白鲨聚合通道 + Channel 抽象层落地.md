---
id: "doc-03d0292db829"
title: "ADR-0010： 支付通道方案 — v1 大白鲨聚合通道 + Channel 抽象层落地"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "监控告警", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0010-payment-channels.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0010-payment-channels.md"
sourceSha256: "2ce1717882f737e49ec6b840b28fea563b11fd0570ff0635402db904b9a29f26"
sourceSystem: "project-doc"
---

# ADR-0010： 支付通道方案 — v1 大白鲨聚合通道 + Channel 抽象层落地

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605230000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-ADR-0010%EF%BC%9A%20%E6%94%AF%E4%BB%98%E9%80%9A%E9%81%93%E6%96%B9%E6%A1%88%20%E2%80%94%20v1%20%E5%A4%A7%E7%99%BD%E9%B2%A8%E8%81%9A%E5%90%88%E9%80%9A%E9%81%93%20%2B%20Channel%20%E6%8A%BD%E8%B1%A1%E5%B1%82%E8%90%BD%E5%9C%B0.md)

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

| 状态 | **已采纳（v1 = 大白鲨聚合通道）** |
|---|---|
| 日期 | 2026-05-23 初稿 · 2026-05-24 升级 |
| Owner | 产品 / 后端 / 财务 / 运维 |
| 影响范围 | `services/go-app/internal/infra/payment/`、`internal/service/wallet/`、`internal/http/hook/`、`config.go`、生产合规审查 |
| 相关需求 | WALLET-001~008（充值）、WALLET-101~108（提现）、WALLET-301~302（退款，本 ADR 引入）、ADR-0011 §17 |
| 关联 ADR | [ADR-0011](ADR-0011-prd-v0.3-align-prototype-v4.45.md) |

## 1. 背景

ADR-0011 完成 v0.3 PRD 对齐后，钱包业务规则已定：**充值 5% 平台费 + 1:1 折钻 + 提现 5% 平台费**，但**实际通过哪些支付通道收钱、给钱**未定。

原型 v4.03 演示 5 种通道（微信、支付宝、银联、USDT、e-CNY），逐条评估后发现：自签商户号路径过长（公司主体 + ICP + 各通道审核 1-3 月），不可能赶上 2026 世界杯窗口。

## 2. 决策（已敲定）

> v0.3.2 二次清理(2026-05-24 19:00):删除 wechat/alipay/generic 三个**占位通道**(从未接过真实商户号)的 router/handler/service/config/yaml/OpenAPI 全栈代码;`PayConfig` 字段仅保留 `Shark`;`PayChannelConfig` 类型整体删除。理由:大白鲨已覆盖 alipay/wechat/union 等子通道,占位代码空跑只会误导(让人以为支持多通道直签),违反 YAGNI。未来若新增聚合方/直签通道,按本 ADR §2.6 抽象层新建 `infra/payment/<name>/` 包即可,无需复活占位代码。

### 2.1 v1 启用通道：**仅大白鲨支付聚合**（单通道）

理由：
- **唯一在世界杯窗口前能上线**的方案。大白鲨自身已对接 6 种子通道（alipay / wechat / union / usdt / dyhbPay / digitalRmb），相当于一次接入覆盖 PRD 5 种支付方式。
- **接入工时最低**（~2.5d vs 自签 5 通道 × 2-3w）。
- **商户合规风险转移**给大白鲨，我方仅承担 SaaS 集成层风险。
- 接口设计已**支持后续切换**：`Channel` interface + `PayConfig.Shark/Wechat/Alipay/...` 多组并存，将来自签下来直接 swap。

### 2.2 商户号路径：三方聚合（大白鲨）

| 通道 | 路径 | v1 实际 |
|---|---|---|
| 大白鲨 | 商家入驻（含 mercId + appSecret） | ✅ v1 启用 |
| 微信直签 / 支付宝直签 / 银联直签 | 公司主体 + ICP，1-3 月周期 | ❌ 暂缓 |
| USDT 自建钱包 | 独立工时 | ❌ 暂缓（大白鲨已覆盖） |
| e-CNY 银行运营机构 | 接入门槛极高 | ❌ 暂缓 |

### 2.3 签名算法

大白鲨使用 **MD5 拼接固定字段顺序**，与现有 `generic` 通道（HMAC-SHA256）不兼容，故 **独立通道实现**（不复用 generic）。

| 场景 | 签名公式 |
|---|---|
| 下单请求 | `md5(mercId + money + notifyUrl + tradeNo + type + appSecret)` |
| 下单响应 | `md5(oid + payUrl + appSecret)` |
| 付款回调 | `md5(code + mercId + oid + payMoney + tradeNo + appSecret)` |
| 退款回调 | `md5(code + mercId + oid + tradeNo + appSecret)` |
| 支付方式查询 | `md5(mercId + money.join('') + appSecret)`（v1 不接） |
| 获取汇率 | `md5(mercId + pType + appSecret)`（v1 不接） |

> 实现位置：`internal/infra/payment/shark/sign.go`。

### 2.4 容差与对账（v0.3.2 强化：大白鲨规约「以 payMoney 为权威」）

| 维度 | 规则 |
|---|---|
| **入账权威字段** | 所有通道一律按回调 `payMoney`（实际到账）入账，**不**用下单时 `RMBAmount`；钻石 = `floor(payMoney × (1 − 5%))` |
| 扫码通道金额（alipay/wechat/union/digitalRmb） | 严格等值匹配（`payMoney == RMBAmount`）；不一致 → `payment_callbacks.processed=2`，**不入账、不改订单状态**，转人工对账 |
| USDT 子通道 | **v1 暂不上线**（大白鲨 USDT 单位是 USDT 个数，不换算 RMB，与我方业务的 RMB 基线冲突），需要前端 USDT 输入 + 汇率展示 + 入账逻辑改造，留 v1.x 单独评估 |
| 回调超时 | 扫码 30 分钟 / 链上 15 分钟（订单 `expires_at`） |
| 补单 | cron 调 `/queryOrder` 兜底（pending 超 5 分钟轮询） |
| 重复回调 | 三层防护：`payment_callbacks (channel, third_party_no) UNIQUE` + `wallet_journals.idempotency_key UNIQUE`（`recharge_<orderNo>`）+ 订单 `SELECT FOR UPDATE` |
| 对账周期 | T+1 跑批；以 `payment_callbacks` + `recharge_orders` + 大白鲨账单三方对单 |

### 2.5 退款策略：**半人工**

大白鲨的退款回调（`cancelNotifyUrl`）由其客服 + 渠道侧主导，我方**不自动扣钻**。流程：

1. 大白鲨调我方 `POST /api/v1/hooks/payment/shark/refund`
2. 后端 MD5 验签 → 持久化 `payment_callbacks` → `recharge_orders.status = REFUNDED` + 写 `admin_audit_logs`
3. 在 admin 后台生成「退款待调账」工单
4. `finance_admin` 在后台使用现有 `/admin/users/{uid}/wallet/adjust` 接口手工扣回钻石（受 `biz.adjust.max_diamond` 上限保护）

理由：用户可能已用充值的钻石押注/打赏，**自动扣钻会出现钻石负余额**或破坏押注结算，需要人工评估场景后再调账。

> 后续 v1.x 若需自动化，再扩展 `RECHARGE_REFUND_OUT` op_type + 余额不足时的策略（拒收 / 记负 / 冲销）。

### 2.6 抽象层接口（落地版）

```go
// internal/infra/payment/channel.go
type Channel interface {
    Name() string
    Init(ctx context.Context, req *InitRequest) (*PayHint, error)
    Query(ctx context.Context, orderNo string) (*OrderStatus, error)
    VerifyPayCallback(ctx context.Context, rawHeaders, rawBody []byte, sig string) (*Settlement, error)
    VerifyRefundCallback(ctx context.Context, rawHeaders, rawBody []byte, sig string) (*RefundNotice, error)
}

type InitRequest struct {
    OrderNo   string          // 我方 R{snowflake}
    UserID    uint64
    Amount    decimal.Decimal // RMB 元，2 位小数
    Type      string          // 子通道：alipay/wechat/union/usdt/digitalRmb（大白鲨场景）
    ClientIP  string
    DeviceID  string
    NotifyURL string          // 公网回调地址
}

type PayHint struct {
    ThirdPartyNo string   // 通道订单号 oid
    PayURL       string   // 跳转链接 / 收款卡号 JSON
    Mode         string   // url / sdk / card
    Raw          []byte   // 通道响应原文，落 ThirdPartyPayload JSON
}

type Settlement struct {
    OrderNo      string
    ThirdPartyNo string
    PayMoney     decimal.Decimal
    PaidAt       time.Time
    Raw          []byte
}

type RefundNotice struct {
    OrderNo      string
    ThirdPartyNo string
    Raw          []byte
}
```

Service 层只依赖 `Channel` interface；通道注册放 `internal/infra/payment/registry.go`，按 `cfg.Pay.<name>.Enabled` 启用。

v1 只注册 `shark`，无其他通道实现。

## 3. 实施分阶段（v1 实际）

| 阶段 | 范围 | 状态 |
|---|---|---|
| **P0 抽象层骨架** | `infra/payment/channel.go` interface + `shark` 实现 | ✅ 本 PR |
| **P1 大白鲨集成** | 下单 / 付款回调 / 订单查询 / 退款回调 | ✅ 本 PR |
| **P2 第二聚合通道** | 备份通道（如 PingPlusPlus），单点故障容灾 | ⏸ v1.1 视需求 |
| **P3 自签直连通道** | 微信 / 支付宝直签（公司 ICP 下来后） | ⏸ v2 |

## 4. 风险

| 风险 | 缓解 |
|---|---|
| 大白鲨单点故障（聚合方宕机 / 跑路） | (1) 监控付款回调 SLA；(2) P2 引入第二聚合方做主备；(3) 商务侧签 SLA 协议 |
| MD5 签名被授权安全测试者构造（理论碰撞） | (1) `appSecret` 仅从 env 注入不进 git；(2) IP 白名单（大白鲨回调 IP 段）；(3) 二次 `/queryOrder` 反查 |
| 重复回调（网络抖动 / 大白鲨重试） | `wallet_journals.idempotency_key UNIQUE` + 订单 `SELECT FOR UPDATE`（已实现） |
| 子通道金额币种不一致（USDT 转 RMB） | 以大白鲨回调 `payMoney` 为权威；不自己换算 |
| 退款冲销破坏押注结算 | §2.5 半人工策略，财务后台手工调账 |
| 三方对账复杂度 | `payment_callbacks.raw_body` 完整留存 + T+1 跑批 |

## 5. 接入清单（执行项）

- [x] §2 决策点回填完成
- [x] `internal/infra/payment/channel.go` interface 落地
- [x] `internal/infra/payment/shark/` 包实现（sign / client / types / errors）
- [x] `services/go-app/internal/config/config.go` 加 `PayConfig.Shark`
- [x] `services/go-app/config/config.*.yaml` 加 `pay.shark` 占位
- [x] `wallet.InitRecharge` channel=shark 时调 `shark.Init`
- [x] `wallet.MarkRechargeRefundRequested`（标 REFUNDED + 审计）
- [x] `hook.HandleSharkPay` / `HandleSharkRefund` + 路由 `/api/v1/hooks/payment/shark` 和 `/refund`
- [x] OpenAPI 契约：`RechargeInitResponse.pay_mode` + 2 个 hook 路径
- [x] PRD `kickoff-wallet.md` §4.1.2 标注「v1 通道 = 大白鲨」+ §4.4 退款规则
- [x] service 层单测覆盖 happy / 验签失败 / 重复回调幂等 / 退款 / 80002 黑名单 5 路径
- [x] env binding 落地（`bindEnvs` 加 6 个 shark key）+ `config.example.yaml` 标注每个字段对应 env
- [x] router IP 白名单拆分（SRS 路径用 `cfg.SRS.AllowedIPs`，shark 路径用 `cfg.Pay.Shark.AllowedCallerIPs`）
- [x] `validate()` 加 prod 启动前置校验：`pay.shark.enabled=true` 时强制要求 mercId / appSecret / notify_url / allowed_caller_ips 非空，缺项直接拒启动
- [ ] **联调（owner: `@kickoff/backend`，等 mercId/appSecret 注入 env）**：跑通沙箱 ¥6 充值

## 6. 后续动作

- [ ] 联调通过后，把状态 §6 最后一项打勾
- [ ] 生产部署前，财务确认 T+1 对账脚本就位
- [ ] v1.1 视用户量评估是否引入第二聚合方做主备

---

**Reviewer**: `@kickoff/product` + `@kickoff/security` + `@kickoff/devops` + `@kickoff/finance`
