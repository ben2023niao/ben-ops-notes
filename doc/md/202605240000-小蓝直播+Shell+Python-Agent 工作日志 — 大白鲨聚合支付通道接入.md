---
id: "doc-d529da882be5"
title: "Agent 工作日志 — 大白鲨聚合支付通道接入"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "监控告警", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-shark-payment-integration.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-shark-payment-integration.md"
sourceSha256: "b0af59e59fbf60a5f064e683c9970ef2bf7b5c672eb801f43bb2e9c8a2c3a4f5"
sourceSystem: "project-doc"
---

# Agent 工作日志 — 大白鲨聚合支付通道接入

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%E2%80%94%20%E5%A4%A7%E7%99%BD%E9%B2%A8%E8%81%9A%E5%90%88%E6%94%AF%E4%BB%98%E9%80%9A%E9%81%93%E6%8E%A5%E5%85%A5.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：Claude（Opus 4.7）
任务：按大白鲨支付-接口文档 v1.1.0 完成支付模块接入；顺带核对原型钻石比例

## 输入资料

- PRD：[docs/prd/modules/kickoff-wallet.md](../../prd/modules/kickoff-wallet.md) v0.3.2
- 需求 ID：WALLET-001 / 002 / 003 / 006 / 301 / 302
- 设计原型：用户共享的 `2026.05.23迭代版.html`（设计稿，非项目内文件）
- 接口/契约：用户共享的 PDF「大白鲨支付-接口文档 v1.1.0」+ [docs/api/openapi.yaml](../../api/openapi.yaml)
- AI 控制文件：[AGENTS.md](../../../AGENTS.md) §2 项目专有红线（资金类强制复式记账 + ADR + 审计 + 测试）
- 项目 Overlay：[ADR-0010](../../decisions/ADR-0010-payment-channels.md)（原"草稿（占位）"）、[ADR-0011](../../decisions/ADR-0011-prd-v0.3-align-prototype-v4.45.md)

## 本次目标

1. 核对原型钻石比例（充值 vs 兑换 vs 提现）是否一致 — 用户问的"顺便看一下"
2. 落地大白鲨支付通道（v1 唯一通道），打通：下单 /topay → 付款回调 notifyUrl → 退款回调 cancelNotifyUrl → 订单查询 /queryOrder
3. 把 ADR-0010 从"草稿"升级为"已采纳"，回填决策点；PRD wallet 模块补退款规则

## 核心决策（与用户确认 4 个问题）

| # | 问题 | 用户答案 | 落地动作 |
|---|---|---|---|
| 1 | 大白鲨是 v1 唯一通道还是多通道之一 | **唯一通道** | PayConfig.Shark 单独一份；ADR-0010 §2.1 锁定；前端 system_config 只暴露大白鲨子通道 |
| 2 | 接入哪些接口 | **/topay + notifyUrl + /queryOrder + cancelNotifyUrl 全要** | 4 个全实现；Topay/QueryOrder 出向、SharkPay/SharkRefund 入向 |
| 3 | 是否已有沙箱凭据 | **已有** | 写代码 + 单测；联调由 user 跑 |
| 4 | 原型 `#page-exchange` 是否删 | **删（推荐）** | 项目内前端是 Nuxt（apps/）暂无 exchange 实现；原型 HTML 在设计稿仓库，需设计同步删除 |

## 衍生关键决策（auto mode 下我直接拍板）

5. **退款策略 = 半人工**：MD5 验签后只标 REFUNDED + 写审计，**不自动扣钻**；finance_admin 在后台用现有 `/admin/users/{uid}/wallet/adjust` 接口手工调账。理由：用户可能已花掉钻石，自动扣会出现负余额。
6. **大白鲨规约 #2「以 payMoney 为权威」强制落地**：`SettleRechargePaid` 签名加 `payMoney decimal.Decimal` 参数；扫码通道严格等值校验，不等 → ErrAmountMismatch → `payment_callbacks.processed=2` 人工对账（不入账）。钻石按 `floor(payMoney × 0.95)` 重算。
7. **USDT 子通道 v1 暂不上线**：大白鲨规约 #3 明确 USDT 不换 RMB，与我方业务的 RMB 基线冲突，留 v1.x。

## 钻石比例核对结论

**业务规则已统一为 `1 RMB → 1 💎`（扣 5% 平台费后向下取整）**：

| 来源 | 状态 |
|---|---|
| PRD `kickoff-wallet.md` §4.1.4 | ✅ |
| `config.RechargeBizConfig.PlatformFeeRate = 0.05` | ✅ |
| `service/wallet/recharge_breakdown.go` + 单测 | ✅ |
| 原型 `#page-recharge` HTML fee-breakdown | ✅ ¥50 → 手续费 2.5 → 入账 47.5 → 💎 47 |
| 原型 H5 充值/扫码/提现 modal | ✅ |

**原型残留矛盾**（需设计同步修正，不阻塞接入）：
- 原型 `#page-exchange` 兑换页仍是旧规则 `1 RMB = 10 💎` + 20% 兑换手续费。但 PRD v0.3 已永久删除兑换（WALLET-201~206 作废），后端也已下线 `Exchange/Quota` 方法。**原型这一节应删除**。
- 原型旧 `product-prd.md` 引用 `1 RMB = 10 💎`（line 106/138/179）— 老 PRD 残留，`kickoff-wallet.md` 已修正为 v0.3 规则。

## 修改文件

### 文档与契约

| 文件 | 说明 |
|---|---|
| `docs/decisions/ADR-0010-payment-channels.md` | 状态草稿→已采纳；§2.1 锁 v1=大白鲨；§2.4 强化「payMoney 权威」+ USDT v1 暂不上线；§2.5 半人工退款策略；§2.6 落地 Channel interface 草图；§5 接入清单全部勾选 |
| `docs/prd/modules/kickoff-wallet.md` | v0.3 顶部说明扩展为 v0.3.2；WALLET-002 标注通道；新增 §3.3 退款（WALLET-301/302）；§4.1.2 改为大白鲨；§4.1.4 加"payMoney 优先"条款；新增 §4.4 退款流程 7 条规则 |
| `docs/api/openapi.yaml` | `RechargeInitRequest` 加 channel=shark enum + pay_type；`RechargeOrder` 加 pay_type/pay_mode/refunded_at；新增 2 个 hook 路径（/hooks/payment/shark + /shark/refund）+ 2 个 schema（SharkPayCallback / SharkRefundCallback） |

### Go 代码

| 文件 | 说明 |
|---|---|
| `services/go-app/internal/config/config.go` | `PayConfig` 加 `Shark SharkChannelConfig{MercID,AppSecret,Gateway,NotifyURL,CancelNotifyURL,HTTPTimeout,EnabledTypes,AllowedCallerIPs}` |
| `services/go-app/config/config.example.yaml` | 加 `pay.shark` 占位 + 安全注释（AppSecret 必须 env 注入） |
| `services/go-app/config/config.local.yaml` | local 默认 enabled:false；联调时手工切 |
| `services/go-app/internal/infra/payment/shark/types.go` | DTO：TopayRequest/Response/Info、PayCallback、RefundCallback、QueryOrder*、子通道/模式常量 |
| `services/go-app/internal/infra/payment/shark/sign.go` | MD5 签名：SignTopayRequest / VerifyTopayResponse / VerifyPayCallback / VerifyRefundCallback / SignPayTypeQuery / SignRateQuery；恒定时间比较；大小写不敏感 |
| `services/go-app/internal/infra/payment/shark/sign_test.go` | 6 个签名场景的「字段顺序对锁」测试（防回归） |
| `services/go-app/internal/infra/payment/shark/errors.go` | 业务错误码映射（200/400/80001/80002/40001/40002）+ sentinel errors |
| `services/go-app/internal/infra/payment/shark/client.go` | HTTP 出向客户端：Topay / QueryOrder；type 白名单校验；超时 8s |
| `services/go-app/internal/infra/payment/shark/client_test.go` | httptest 模拟大白鲨网关；覆盖 happy / blacklisted / type 不允许 / 签名失败 / 网络错误 / 40002 / queryOrder |
| `services/go-app/internal/dto/wallet.go` | `RechargeInitRequest` 加 channel enum 含 shark + PayType；`RechargeInitResponse` 加 PayType/PayMode/ThirdPartyNo |
| `services/go-app/internal/repository/wallet/orders.go` | RechargeRepository 加 `FindByOrderNoAny` / `MarkRefunded` / `UpdateThirdParty`；MarkRefunded 内置幂等 |
| `services/go-app/internal/service/wallet/service.go` | 加 `SetSharkClient`；改 `InitRecharge` channel=shark 调 Topay 落 pay_url+oid，失败标 CANCELLED；**升级 `SettleRechargePaid` 签名加 `payMoney`**，扫码通道严格匹配 → `ErrAmountMismatch`；钻石按 payMoney 重算；新增 `MarkRechargeRefundRequested` 半人工退款 |
| `services/go-app/internal/service/wallet/settle_shark_test.go` | payMoney≤0 拒收 + ErrAmountMismatch sentinel 防 wrap 误判测试 |
| `services/go-app/internal/service/hook/payment.go` | 加 import shark + decimal；改 generic 通道传 amount→decimal；新增 `HandleSharkPay` / `HandleSharkRefund` / `parseSharkTime`；全链路：持久化 → 验签 → 去重 → 业务入账（透传 ErrAmountMismatch 为 processed=2） |
| `services/go-app/internal/service/hook/payment_shark_test.go` | `parseSharkTime` 表驱动测试（RFC3339 / ISO8601 / fallback） |
| `services/go-app/internal/http/hook/payment.go` | 加 `SharkPay` / `SharkRefund` handler，按规约返回纯文本 `success` |
| `services/go-app/internal/http/router/public.go` | router 装配 shark client（按 Enabled 启用，缺密钥告警跳过）；路由 `POST /api/v1/hooks/payment/shark` + `/shark/refund` |

## 测试结果

```
$ go test -race -count=1 ./internal/...
ok   kickoff/go-app/internal/infra/payment/shark   1.278s
ok   kickoff/go-app/internal/pkg/ledger            2.193s
ok   kickoff/go-app/internal/service/hook          1.587s
ok   kickoff/go-app/internal/service/member        2.501s
ok   kickoff/go-app/internal/service/wallet        1.884s
```

`go test -race ./internal/...` 全绿，无新增警告。

## 门禁

- ✅ `python3 scripts/validate-prd.py` — Requirement rows: 187; module IDs: 229
- ✅ `python3 scripts/validate-engineering-standards.py`
- ✅ `python3 scripts/validate-capability-gates.py`
- ✅ `python3 scripts/validate-completion-claims.py`
- ✅ `npm run check:openapi`
- ⏸ `check:contract`、`check:mr-gates`：未跑（无 SDK 同步需求；MR 阶段再跑）

## 框架价值判断

`internal/infra/payment/shark/` 是新增的独立包，命名空间清晰，可单测、零业务依赖。后续若引入第二聚合通道（如 PingPlusPlus），按相同结构开新包，service 层只需调 `SetXxxClient`，符合 ADR-0010 §2.6 Channel interface 落地路径。

## 风险与待办

1. **未联调**：代码就绪，但未跑沙箱真实回调。需要 user 在 env 注入 `APP_PAY_SHARK_APP_SECRET` + 切 `pay.shark.enabled=true`，用沙箱 `mercId=10001` 跑 ¥6 充值 + 验证回调链路。
2. **`ErrAmountMismatch` 端到端未测**：靠纯函数单测 + sentinel 防 wrap 测试覆盖了"识别错误"路径，但"hook 把它落 processed=2"的链路只能联调验证。
**附加清理(2026-05-24 19:00)** — 删除 wechat/alipay/generic 三个占位通道全栈代码:
- router 3 条路由 + handler 3 个方法 + hook service 7 个函数/类型(GenericRequest/HandleGeneric/dispatchGeneric/verifyGeneric/HandleWechat/HandleAlipay/handlePlaceholder)
- `config.PayChannelConfig` 类型整体删除;`PayConfig` 字段只保留 `Shark`
- `config.example.yaml` / `config.local.yaml` 删 wechat/alipay/generic 段
- `loader.bindEnvs` 删 `pay.wechat.sign_key` / `pay.alipay.pub_key` / `pay.generic.sign_key`
- `dto.RechargeInitRequest.Channel` enum 收窄为 `[shark]`;`PayType` 改为必填
- `openapi.yaml` 删 `/pay/v1/callback/{wechat,alipay,generic}` 3 个路径定义

理由:这 3 个是 v0.2 占位代码,从未接过真实商户号,留着只会让人误以为「项目支持多通道」。
ADR-0010 §2 顶部加变更说明。

---

3. ~~**大白鲨回调 IP 白名单为空**~~ — **已修(2026-05-24 18:40)**:
   - router 拆分:`hooks/payment/shark` + `/shark/refund` 用 `cfg.Pay.Shark.AllowedCallerIPs`,SRS 路径继续用 `cfg.SRS.AllowedIPs`
   - `loader.validate()`:prod 启用 shark 时,`allowed_caller_ips` 为空直接拒绝启动(fail-closed)
   - user 只需在生产 yaml 填 `pay.shark.allowed_caller_ips: ["IP-段1","IP-段2"]` 即可,从大白鲨商户后台拿 IP 段。
4. **退款工单**：PRD §4.4 / WALLET-302 写了"在后台生成退款待调账工单"，但实际 admin 后台还没这个工单页。当前只能靠 `payment_callbacks` + `recharge_orders.status=REFUNDED` 关联查询给财务看，**需要 admin 前端补一个工单页**（独立任务）。
5. **原型 #page-exchange 残留**：原型 HTML 在设计稿仓库，本次未触达。需通知设计同学按 PRD v0.3 / ADR-0011 删除该节。

## 交接说明

1. **联调走流程**（拿到大白鲨沙箱凭据后）：
   - 把 `APP_PAY_SHARK_MERC_ID` + `APP_PAY_SHARK_APP_SECRET` 注入 env
   - `config.local.yaml` 切 `pay.shark.enabled: true`
   - 启动 api：`make api`
   - 调 `POST /api/v1/wallet/recharge/init` body `{"channel":"shark","pay_type":"alipay","rmb_amount":"6.00"}`
   - 拿到 `pay_url` 在沙箱付款
   - 验证 `payment_callbacks` 落入 + `recharge_orders.status=PAID` + `wallet_journals` 入账（💎 = 5，按 6×0.95=5.7 → floor）
2. **生产部署 checklist**：
   - [ ] env 注入 `APP_PAY_SHARK_APP_SECRET`（不入 git）
   - [ ] 替换 `notify_url` / `cancel_notify_url` 为生产域名
   - [ ] 拿大白鲨回调 IP 段填 `allowed_caller_ips`，并改 router 用 Pay.Shark.AllowedCallerIPs 而不是 SRS 的（见风险 #3）
   - [ ] 提前与大白鲨商户走通沙箱 ¥6 充值 → 回调 → 钻石入账
3. **后续 v1.x 启用 USDT 子通道**：要改 `SettleRechargePaid` 的扫码严格匹配为 USDT ±5% 容差；前端需要 USDT 输入框 + 汇率展示；ADR-0010 §2.4 已留位。
