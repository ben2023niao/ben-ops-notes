---
id: "doc-51e74c48af00"
title: "Kickoff 钱包（充值 / 提现 / 兑换） 模块 PRD"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "监控告警", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-wallet.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/prd/modules/kickoff-wallet.md"
sourceSha256: "e4218367a46dfd5dd3ce56c5da5dddd9322b92d6584d767bfde23ef966c8aaa4"
sourceSystem: "project-doc"
---

# Kickoff 钱包（充值 / 提现 / 兑换） 模块 PRD

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605230000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Kickoff%20%E9%92%B1%E5%8C%85%EF%BC%88%E5%85%85%E5%80%BC%20-%20%E6%8F%90%E7%8E%B0%20-%20%E5%85%91%E6%8D%A2%EF%BC%89%20%E6%A8%A1%E5%9D%97%20PRD.md)

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

模块：`kickoff-wallet`
端：Web / H5
Owner：`@kickoff/backend`
状态：已确认
对应原型页面：`#page-recharge`、`#page-recharge-qr`、`#page-withdraw`、`#page-exchange`

> **⚠ v0.3 变更（2026-05-23 对齐原型 v4.45）**：
> 1. **兑换模块（§3.3 / §4.3）整体删除**：原型 v4.18 已下线 RMB ⇄ 钻石兑换功能，钱包只保留充值 / 提现两条路径；
> 2. **充值比例改为 `RMB 1 : 💎 1`**：原"1 RMB = 10 💎 + 5 赠送"规则废弃，统一 1:1 入账；
> 3. **平台手续费统一 5%**：充值扣 5% 后 1:1 折算为 💎；提现扣 5% 后到账（原提现 2% 废弃）；
> 4. **支付通道（v0.3.2 敲定）**：v1 仅启用**大白鲨聚合通道**（详见 [ADR-0010](../../decisions/ADR-0010-payment-channels.md)）。大白鲨自身覆盖 5 种子通道（alipay / wechat / union / usdt / digitalRmb），后端调用入口统一 channel=`shark`，子类型走 `type` 字段；通道抽象层在 `internal/infra/payment/` 实现，后续切换/并存其他聚合方无需改 service 层。
> 5. **退款流程（v0.3.2 引入）**：见 §4.4。大白鲨退款回调进入后落「半人工调账」流程，**不自动扣减用户钻石**，由 `finance_admin` 在后台手工调账（避免冲销用户已花掉的钻石）。

## 1. 模块目标

钱包是 Kickoff 的**资金核心**，覆盖资金进出。本模块定义：

1. **充值流程**：金额选择 → 通道选择 → 唤起二维码 / 链上转账 → 状态轮询 → 扣 5% 平台费 → 1:1 折算钻石到账
2. **提现流程**：金额选择 → 仅支付宝通道 → 扣 5% 平台费 → 风控 → 审核 → 到账
3. **资金一致性**：所有资金动作走账本表 + 钱包余额表 同事务

## 2. 用户角色

| 角色 | 说明 |
| --- | --- |
| 已登录用户 | 全功能 |
| 未登录用户 | 不可访问，跳登录 |
| KYC 用户 | 提现 > 1000 RMB 或月累计 > 5000 RMB 必须完成实名 |

## 3. 需求列表

### 3.1 充值（Recharge）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| WALLET-001 | 金额选择（6 个预设 + 自定义） | P0 | 已确认 | 10/30/50/100/300/500，可输入自定义 |
| WALLET-002 | 支付方式选择（通道适配） | P0 | 已确认 | **v1 = 大白鲨聚合通道**（见 ADR-0010 §2.1）；调用入口统一 channel=`shark`、子类型走 `type` 字段；v0.3.2 前端 system_config 只暴露 `alipay / wechat / union / digitalRmb` 4 个子通道；**USDT 子通道 v1 暂不上线**（货币单位不换算 RMB，待 v1.x 评估） |
| WALLET-003 | 手续费明细预览（金额 / 5% 平台费 / 实际到账 / 💎 入账） | P0 | 已确认 | 充值页实时计算并展示 4 行明细 |
| WALLET-004 | 下一步生成二维码（QR） / 链上充值地址 | P0 | 已确认 | 30 分钟有效期；链上通道展示 USDT 地址 + 实时汇率 |
| WALLET-005 | 状态轮询（支付中/成功/失败） | P0 | 已确认 | 通常 30s 内到账；链上 1-15 min |
| WALLET-006 | 充值成功 → 1:1 折算钻石入账 + 通知 | P0 | 已确认 | 💎 = floor((amount × (1 − 5%))) |
| WALLET-007 | 充值失败兜底（超时/取消） | P0 | 已确认 | 引导用户重新发起或联系客服 |
| WALLET-008 | 充值协议（首次充值 14 天不可提现） | P0 | 已确认 | "已阅读并同意"勾选 |

### 3.2 提现（Withdraw）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| WALLET-101 | 显示可提现余额 | P0 | 已确认 | = 余额 - 冻结 - 首充冷却 |
| WALLET-102 | 提现金额输入 + 快捷比例（25/50/最大） | P0 | 已确认 | 最小 10 RMB、最大 = 可提现 |
| WALLET-103 | 提现通道（仅支付宝） | P0 | 已确认 | 用户输入支付宝账号 |
| WALLET-104 | 手续费明细（金额/渠道费/平台费 5%/到账） | P0 | 已确认 | 平台费 5%；渠道费 0 |
| WALLET-105 | 风控提示（首充冷却/限额/KYC） | P0 | 已确认 | 5 条提示 |
| WALLET-106 | 申请提现 → 创建订单 → 转人工/自动审核 | P0 | 已确认 | 低风险自动放行；高风险人工审核 |
| WALLET-107 | 提现状态推送（处理中/已到账/驳回） | P0 | 已确认 | 站内信 + 邮件 |
| WALLET-108 | 提现成功 → 钱包扣减 + 第三方转账 | P0 | 已确认 | 扣减发生在审核通过瞬间 |

### 3.3 退款（v0.3.2 新增 · 由大白鲨通道触发）

| ID | 标题 | 优先级 | 状态 | 验收摘要 |
| --- | --- | --- | --- | --- |
| WALLET-301 | 接收大白鲨退款回调 | P0 | 已确认 | MD5 验签通过 → 落 `payment_callbacks` → 订单标 `REFUNDED` → 写 `admin_audit_logs` |
| WALLET-302 | 退款待调账工单 | P0 | 已确认 | `finance_admin` 在后台通过现有调账接口手工扣回钻石，受 `biz.adjust.max_diamond` 上限保护；**不自动扣减** |

> **§3.4 兑换（Exchange）已删除**（v0.3 / 对齐原型 v4.18）：
> 钱包不再提供 RMB ⇄ 钻石互转功能；充值即按 1:1 折算钻石、提现走独立通道。
> 历史 ID `WALLET-201` ~ `WALLET-206` 永久作废，**不再分配给新需求**。

## 4. 业务规则

### 4.1 充值

1. **金额范围**：单次 10 - 50,000 RMB；< 10 不允许；> 50,000 引导拆单。
2. **支付通道（v1 = 大白鲨）**：后端调用入口统一 `channel = shark`，子类型通过大白鲨 `type` 字段（alipay / wechat / union / usdt / dyhbPay / digitalRmb）选择；前端展示哪些子类型由 `system_config` 控制。详见 [ADR-0010](../../decisions/ADR-0010-payment-channels.md)。
3. **平台手续费**：统一 5%；`net = amount × (1 − 5%)`；渠道费 0（若启用 USDT 则 gas/网络费由用户自付）。
4. **钻石入账比例**：`RMB 1 : 💎 1`；`💎 = floor(net)`（向下取整避免精度问题）。
   - 示例：充值 ¥100 → 平台费 ¥5 → 实际入账 ¥95 → 💎 95。
   - 默认示例：充值 ¥50 → 平台费 ¥2.5 → 实际入账 ¥47.5 → 💎 47。
   - 运营可在后台 `system_configs` 调整 `wallet.recharge.platform_fee_rate`、`wallet.recharge.diamond_rmb_rate`、`wallet.recharge.min_amount`、`wallet.recharge.max_amount`、`wallet.recharge.amount_options` 和 `wallet.recharge.packages`。
   - `wallet.recharge.packages` 为精确充值包，命中 `amount_rmb` 时直接按 `diamond_amount` 入账；测试阶段可配置 `[{"amount_rmb":"0.01","diamond_amount":1}]`，并把手续费率设为 `0`、最小充值设为 `0.01`。
   - **v0.3.2 重要**：`amount` 一律取通道回调的 `payMoney`（实际到账），**不**取下单时的 `RMBAmount`。扫码通道两值不等时 → 标记 `payment_callbacks.processed=2`，**不入账**，转人工对账（避免大白鲨拆单 / 渠道扣量场景下的资金错账）。
5. **二维码 / 链上地址有效期**：扫码通道 30 分钟；链上通道 15 分钟。超时订单标记 "超时失败"，可重发。
6. **状态轮询**：前端每 3s 查一次订单状态；服务端通道回调 → 同步状态。
7. **到账延迟**：扫码通道理论上回调即到账（< 30s）；链上通道 1-15 min（按链拥堵）。30s / 15min 未到账显示对应 loading；超过显示"长时间未到账，请联系客服"。
8. **链上容差**：链上通道（USDT 类）实际到账金额与下单金额 ±5% 内视为成功；超出范围进入人工对账。
9. **协议约束**：用户必须勾选"首次充值后 14 天内不可提现 · 已阅读并同意充值协议"。
10. **首充冷却**：首次充值后 14 天内，已充值金额对应的 RMB 不能提现，但可用钻石押注。
11. **充值审计**：所有充值订单记审计（订单创建、回调到账、超时失败、链上容差处理）。

### 4.2 提现

1. **金额范围**：最小 10 RMB；最大 = 可提现金额。
2. **可提现 = 余额 - 冻结 - 首充 14 天内的金额**。
3. **手续费**：平台 5%；渠道 0；用户实际到账 = 金额 × 95%。
4. **限额**：单日 ≤ 5,000 RMB；单月 ≤ 50,000 RMB。
5. **KYC**：单笔 > 1,000 RMB 或 月累计 > 5,000 RMB 必须先完成实名认证。
6. **风控审核**：每次提现申请走风控引擎打分：
   - 低风险（评分 < 30）：自动放行，发起转账
   - 中风险（30 ≤ 评分 < 70）：进入"待审核"队列，运营 24h 内人工
   - 高风险（评分 ≥ 70）：自动驳回 + 通知用户原因（提供申诉入口）
7. **首充 14 天约束**：申请时若首充 < 14 天 → 直接驳回 + 提示具体可申请日期。
8. **多笔小额套现防护**：同一支付宝账号 24h 内 ≥ 5 笔提现 → 风控告警（**原型评审版未定义此规则**，待产品评审后补入并分配规则 ID）。
9. **资金锁**：提现申请创建瞬间 → 钱包冻结对应金额；审核通过 → 实际扣减并转账；驳回 → 解冻。
10. **审计**：提现申请、审核、放行、驳回、转账成功/失败 全程审计。

### 4.3 资金一致性

**所有资金操作必须遵守的不变式**：

```text
Σ(账本流入 RMB) + 期初 RMB = Σ(账本流出 RMB) + 当前 RMB
Σ(账本流入 💎) + 期初 💎 = Σ(账本流出 💎) + 当前 💎
```

**op_type 分类**（v0.3 已删除全部 `EXCHANGE_*` 与 `RECHARGE_BONUS_OUT`）：

| op_type | 方向 | 货币 | 触发 |
| --- | --- | --- | --- |
| RECHARGE_IN | + | 💎 | 默认按 `floor((amount - fee) × diamond_rmb_rate)` 入账；命中后台精确充值包时按 `diamond_amount` 入账 |
| RECHARGE_FEE_OUT | - | RMB | 充值平台费，默认 5%，可在后台系统配置设为 0 |
| WITHDRAW_FREEZE | 冻结 | RMB | 提现申请，冻结金额 |
| WITHDRAW_OUT | - | RMB | 提现审核通过，实际扣减 |
| WITHDRAW_FEE_OUT | - | RMB | 提现平台费 5% |
| WITHDRAW_UNFREEZE | 解冻 | RMB | 提现驳回，解除冻结 |
| BET_OUT | - | 💎 | 押注扣钻 |
| BET_IN | + | 💎 | 派彩入账 |
| BET_REFUND | + | 💎 | 退单回退 |
| TIP_OUT | - | 💎 | 打赏扣钻 |

**对账**：T+1 跑批，按 op_type 分组校验账本平衡。

### 4.4 退款（v0.3.2 新增 · 大白鲨通道）

1. **触发源**：仅大白鲨退款回调（`POST /api/v1/hooks/payment/shark/refund`）— 我方**不主动发起退款**，由大白鲨客服 / 渠道侧确认无误后通知。
2. **验签**：MD5(`code + mercId + oid + tradeNo + appSecret`) 与请求体 `sign` 一致；失败 → 仅落 `payment_callbacks.processed = 2`，**不入账、不改订单**。
3. **去重**：以 `(channel='shark', third_party_no=oid)` 唯一性查 `payment_callbacks`；命中已 OK 的回调 → 当前回调标记 `deduplicated` 直接 200。
4. **入账策略（半人工）**：
   - 标记 `recharge_orders.status = REFUNDED`（5），写 `refunded_at`；
   - 写 `admin_audit_logs`（action=`recharge.refund_request`），含 oid / tradeNo / payMoney / 触发 IP；
   - **不**自动出账钻石 — 由 `finance_admin` 在后台用 `/api/v1/admin/users/{uid}/wallet/adjust` 接口手工扣钻；
   - 调账受 `biz.adjust.max_diamond` 上限保护；超上限拆批。
5. **不变式**：用户钻石余额可能因「已花掉」而不足以扣回原值，此时由财务评估场景（坏账核销 / 部分追扣 / 全额放弃），**永远不允许**钱包余额变负。
6. **响应**：大白鲨要求纯文本 `success`（不是 JSON）；失败也返回 `success`（按其规范），真实结果记 `payment_callbacks.processed`。
7. **审计**：所有退款回调（含验签失败）落 `payment_callbacks` 留底；财务调账走现有 `audit.Log` 通道。

## 5. 边界与异常

| 场景 | 系统行为 | 提示/状态 |
| --- | --- | --- |
| 充值二维码超时 | 标记失败 | "二维码已超时，请重新发起" |
| 充值通道回调延迟 | loading 持续 | 3 分钟后显示"长时间未到账，请联系客服" |
| 充值通道回调失败但实际到账 | 对账时发现差异 → 自动补单 | 用户侧无感（已到账） |
| 提现首充未满 14 天 | 阻止申请 | "首次充值后 14 天可申请，约 2026-07-24" |
| 提现单日超限 | 阻止申请 | "今日提现已达上限 5,000 RMB" |
| 提现单月超限 | 阻止申请 | "本月提现已达上限 50,000 RMB" |
| 提现 KYC 未完成 | 阻止申请并跳实名页 | "单笔超过 1,000 RMB 需先完成实名" |
| 提现支付宝账号不匹配 | 第三方转账失败 → 退回到账 | 系统消息 |
| 链上充值实际金额超过容差（±5%） | 进入人工对账 | "充值金额异常，已转人工，预计 24h 内处理" |

## 6. 权限与风控

1. 需登录；提现需 KYC（按阈值）。
2. **审计**：充值/提现全部审计。
3. **风控规则**（仅列原型评审版已定义）：
   - R-204 异常充提链路：充值 24h 内提现 ≥ 80% 余额 → 高风险
   - 短期多笔小额提现、单一支付宝绑定多账户 属技术架构识别的潜在缺口，**原型评审版未定义**，待产品评审后再补入并分配规则 ID
4. **风控决策**：自动放行 / 人工审核 / 自动驳回 三档。

## 7. 数据对象

| 对象 | Owner | 说明 |
| --- | --- | --- |
| `user_wallet` | `services/go-app` | RMB + 钻石余额（含 frozen） |
| `recharge_order` | `services/go-app` | 充值订单（含通道、链上 tx_hash、容差判定） |
| `withdraw_order` | `services/go-app` | 提现订单（含风控评分、审核状态） |
| `wallet_ledger` | `services/go-app` | 资金账本（按 op_type 分） |
| `payment_channel_log` | `services/go-app` | 通道回调原始日志 |
| `kyc_record` | `services/go-app` | 实名记录 |

> `exchange_order` 表 v0.3 删除（兑换功能下线，原表数据若已迁移走归档库）。

### 7.1 关键索引

> 见下方表格；此处保留锚点供 §7.2/7.3 引用。

### 7.2 充值通道枚举（`recharge_order.channel`，v0.3.1）

| 取值 | 渠道 | 通道类型 | 是否 v0.3.1 v1 上线 |
|---|---|---|---|
| `wechat` | 微信支付 | 扫码 / H5 | 待 ADR-0010 决策 |
| `alipay` | 支付宝 | 扫码 / H5 | 待 ADR-0010 决策 |
| `union` | 银联 / 某支付平台 | 扫码 / H5 | 待 ADR-0010 决策 |
| `usdt_trc20` | USDT (TRC20) | 链上 + 容差匹配 | 待 ADR-0010 决策 |
| `usdt_erc20` | USDT (ERC20) | 链上 + 容差匹配 | 待 ADR-0010 决策 |
| `digitalrmb` | 数字人民币 e-CNY | 扫码 / 钱包跳转 | 待 ADR-0010 决策 |

> v0.3.1 PRD 仅锁定**字段命名与展示规则**；实际开通顺序、签约通道、合规审查由 [ADR-0010](../../decisions/ADR-0010-payment-channels.md) 决定。已开通的 channel 在 `system_configs` 中通过 `wallet.recharge.channels.enabled` 列控制开关。

### 7.3 充值订单状态机（`recharge_order.status`，v0.3.1）

| 取值 | 触发 | 终态 | 前端展示 |
|---|---|---|---|
| `paying` | 用户点"立即支付"创建订单 | 否 | ⏳ 支付中（灰） |
| `chain_confirming` | USDT 链上探测到交易但确认数 < 阈值 | 否 | ⛓ 链上确认中（蓝；USDT 专属） |
| `success` | 渠道回调 / 链上确认达标 → 记账 commit | 是 | ✓ 已到账（绿） |
| `timeout` | 创建后 30 分钟未支付（扫码）/ 15 分钟未到账（链上） | 是 | ✗ 超时取消（红） |
| `failed` | 渠道侧返回失败 / 容差不匹配 | 是 | ✗ 失败（红） |
| `refunded` | 已成功订单事后退款（运营 / 用户申诉） | 是 | ↩ 已退款（灰，金额前缀 "—"） |

**状态转换合法路径**：
- `paying → success | timeout | failed`
- `paying → chain_confirming → success | failed`（USDT 专属）
- `success → refunded`（运营审批，单独事务，写新 ledger 行）

**幂等键**：`(channel, third_party_no)` 唯一约束 + 内部 `idempotency_key` 兜底。

| 表 | 索引 |
| --- | --- |
| `recharge_order` | `(user_id, created_at desc)`、`(status, created_at)` |
| `withdraw_order` | `(user_id, created_at desc)`、`(status, created_at)`、`(risk_score desc, status)` |
| `wallet_ledger` | `(user_id, created_at desc)`、`(op_type, created_at)` |

## 8. API/事件契约

### 8.1 充值

| 需求 ID | 契约 | Owner Service | 状态 |
| --- | --- | --- | --- |
| WALLET-001~004 | `POST /api/v1/wallet/recharge/init` | `services/go-app` | 待设计 |
| WALLET-005 | `GET /api/v1/wallet/recharge/{order_no}/status` | `services/go-app` | 待设计 |
| WALLET-006 | `POST /api/v1/wallet/recharge/callback`（微信/支付宝异步通知） | `services/go-app` | 待设计 |
| WALLET-009（v0.3.1） | `GET /api/v1/me/recharge-records?page&size&status&channel` 充值记录（含 status + channel 字段） | `services/go-app` | 待实现 |
| WALLET-010（v0.3.1） | `GET /api/v1/wallet/recharge/breakdown?amount={n}&channel={c}` 返回 `{amount_rmb, fee_rate, fee_rmb, net_rmb, diamond_amount, pay_type}` 用于 H5 充值 modal 实时展示；USDT v0.3.2 暂不开放 | `services/go-app` | 已实现 |
| Admin (v0.3.1) | `GET /api/v1/admin/payment-channels` 返回 6 通道开关 + 费率；`PUT /api/v1/admin/payment-channels/{code}` body `{enabled, fee_rate?, recommended?}` | `services/go-app` | 待 ADR-0010 |
| WALLET-011（v0.3.3） | `GET /api/v1/system/config` 返回充值金额、费率、钻石比例和精确充值包；后台通过系统配置维护 | `services/go-app` | 已实现 |

### 8.2 提现

| 需求 ID | 契约 | Owner Service | 状态 |
| --- | --- | --- | --- |
| WALLET-101 | `GET /api/v1/wallet/withdraw/info` | `services/go-app` | 已实现 |
| WALLET-106 | `POST /api/v1/wallet/withdraw/submit` | `services/go-app` | 已实现 |
| WALLET-107 | `GET /api/v1/wallet/withdraw/{order_no}/status` | `services/go-app` | 待设计 |
| Admin | `POST /api/v1/admin/withdraw/{order_no}/approve` | `services/go-app` | 待设计 |
| Admin | `POST /api/v1/admin/withdraw/{order_no}/reject` | `services/go-app` | 待设计 |

> §8.3 兑换 API（`POST /api/v1/wallet/exchange` 等）v0.3 已废弃，路由不再保留。

## 9. 验收标准

| 需求 ID | 验收标准 |
| --- | --- |
| WALLET-001 | 默认金额预设可选；自定义金额范围由 `wallet.recharge.min_amount` / `wallet.recharge.max_amount` 控制，支持测试值 0.01 RMB |
| WALLET-003 | 默认配置下输入 100 → 实时显示：金额 ¥100 / 平台费 ¥5 / 实际入账 ¥95 / 钻石到账 95 💎；手续费设 0 后 1 RMB → 1 💎 |
| WALLET-004 | 点击下一步 → 生成订单 + 二维码 / 链上地址；扫码 30 分钟 / 链上 15 分钟过期 |
| WALLET-005 | 扫码通道回调到账 30s 内前端切到 "充值成功"；链上通道 1-15 min |
| WALLET-006 | 充值成功后按后台充值规则计算钻石并入账；默认 `floor(amount × 0.95)`，精确充值包可覆盖为 `0.01 RMB = 1 💎` |
| WALLET-102 | 输入 50 → 显示快捷比例可选 25%/50%/最大 |
| WALLET-104 | 100 RMB → 手续费 5 RMB，到账 95 RMB |
| WALLET-106 | 低风险申请 → 24h 内到账；高风险 → 驳回 + 告知原因 |
| WALLET-108 | 审核通过瞬间 frozen → 0；`WITHDRAW_OUT` + `WITHDRAW_FEE_OUT` 记账；第三方转账触发 |

## 10. 测试要求

1. **单元测试**：金额校验、5% 手续费计算（向下取整边界）、限额校验、KYC 阈值判定、链上容差 ±5% 判定
2. **集成测试**：完整充值（含通道回调）、完整提现（含审核）全事务一致性
3. **回调测试**：模拟通道回调（包括重复回调、乱序回调、伪造回调签名、链上 reorg）
4. **风控测试**：低/中/高三档风控决策路径
5. **对账测试**：跑一天后 T+1 对账，差异率 ≤ 0.05%
6. **E2E**：充值 → 押注 → 派彩 → 提现 整链路
7. **压测**：充值发起 300 QPS / 提现 50 QPS 持续 1 分钟

## 11. 待确认问题

| 问题 | Owner | 截止时间 | 状态 |
| --- | --- | --- | --- |
| 充值通道（微信 / 支付宝 / 银联 / USDT / e-CNY 哪几条 v1 启用） | `@kickoff/devops` | 2026-05-29 | 待确认 |
| 提现通道（支付宝商家批量付款 vs 第三方代付） | `@kickoff/devops` | 2026-05-29 | 待确认 |
| KYC 服务商（阿里云实人 vs 腾讯云 vs 自建） | `@kickoff/security` | 2026-05-29 | 待确认 |
| USDT 汇率源（CMC / Binance / Coingecko）与锁定窗口（v4.03 原型用 10 min） | `@kickoff/backend` | 2026-05-29 | 待确认 |
| 链上容差 ±5% 是否细化到分通道（TRC20 / ERC20 / BEP20 gas 波动不同） | `@kickoff/backend` | 2026-06-01 | 待确认 |
| 5% 手续费是否运营可配（如首充免手续费、VIP 折扣） | `@kickoff/product` | 2026-05-25 | 待确认 |
| 风控引擎自建 vs 接第三方（如蚂蚁风控） | `@kickoff/security` | 2026-06-01 | 待确认 |
