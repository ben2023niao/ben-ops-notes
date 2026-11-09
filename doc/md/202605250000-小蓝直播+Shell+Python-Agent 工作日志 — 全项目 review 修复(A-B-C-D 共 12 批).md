---
id: "doc-79bd64efe426"
title: "Agent 工作日志 — 全项目 review 修复(A/B/C/D 共 12 批)"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Kubernetes", "Nginx", "Redis", "监控告警"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-review-batch3-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-review-batch3-fix.md"
sourceSha256: "9e19057dbed9777467f74bb8074de4e65bb9506c84369bd3ac12cfef3d5dcf7f"
sourceSystem: "project-doc"
---

# Agent 工作日志 — 全项目 review 修复(A/B/C/D 共 12 批)

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605250000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%E2%80%94%20%E5%85%A8%E9%A1%B9%E7%9B%AE%20review%20%E4%BF%AE%E5%A4%8D%28A-B-C-D%20%E5%85%B1%2012%20%E6%89%B9%29.md)

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期:2026-05-25
Agent:Claude(Opus 4.7)
任务:基于 4-reviewer 报告(go / security / silent-failure / code-quality),修全部专业性问题,不动业务

## 触发

用户在 commit 21b9508 后要求"整个项目 review",4 个 reviewer 并行扫描后给出 ~22 条 P0-P2 问题。
用户决定:"全部都要修"。

## 批次组织(12 批 + 1 门禁批)

按"领域聚合 + 单批可独立验证"原则分组:

| 批 | 主题 | 涉及文件 |
|---|---|---|
| **A·1** | SumDaily 精度修复 + monthlyUsed 不吞 error | repo/wallet/orders.go, service/wallet/service.go |
| **A·2** | MarkRefunded 原子 UPDATE + fallback logger | repo/wallet/orders.go, service/wallet/service.go |
| **A·3** | bank_account nil check 简化 | service/wallet/bank_account.go |
| **B·1** | shark.QueryOrder 一致性 + 签名校验 + 3 case 单测 | infra/payment/shark/{client,sign,types,client_test}.go |
| **B·2** | hook/payment.go JSON 解析失败 return + rawBody LimitReader 1MB | http/hook/{payment,srs}.go, service/hook/payment.go |
| **B·3** | MarkVerified/MarkProcessed 包装 logger.Error | service/hook/payment.go |
| **C·1** | router SetTrustedProxies 防 X-Forwarded-For 绕过 | config/config.go, http/router/{public,admin}.go |
| **C·2** | RechargeStatus 补 Channel + tryDecrypt/AES/PostTx audit | dto/wallet.go, service/wallet/{service,bank_account}.go, http/router/public.go |
| **C·3** | 钱包写接口 JWT fail-closed + ratelimit account 维度 | http/middleware/{auth,ratelimit}.go, http/router/public.go |
| **D·1** | 删手写 stringsLower/containsAny/indexOf 用 strings 标准库 | service/wallet/service.go |
| **D·2** | InitRecharge 拆 callSharkTopay + writeStringSet sort + Status 命名一致化 | service/wallet/service.go, service/admin/payment_channels.go, dto/wallet.go |
| **D·3** | 访问日志 path → FullPath + EncKey startup validation + monthly multiplier 可配 | http/middleware/logger.go, config/config.go, service/wallet/service.go |

## 关键修复细节

### 资金安全(批 A + 部分 D)

1. **SumDaily 精度**:`float64` → `decimal.Decimal`,接口签名升级,3 处调用方同步重构。修复"4999.99 元被截 4999"导致的超额提现绕过路径。
2. **monthlyUsed**:`_ := SumDaily(...)` 改 `mErr` + `logger.Warn`,DB 异常前端显示"本月已提 0"会误导,必须有告警痕迹。
3. **MarkRefunded TOCTOU**:消除"SELECT 再 UPDATE"窗口,改为单条原子 UPDATE + RowsAffected 三态判别(成功/幂等/不存在)。
4. **UpdateThirdParty `_ = err`** + **MarkCancelled `_ = err`** 静默 → 三处全部 `logger.Error/Warn` 留痕,退款回调按 OID 匹配的必要前置。

### 大白鲨支付安全(批 B)

5. **QueryOrder 中间人防御** 三层:
   - 一致性校验(mercId / tradeNo 不匹配 → ErrSign)
   - 响应签名乐观校验(Msg.Sign 非空时强制 VerifyQueryOrderResponse)
   - 加 3 case 单测:RejectsMismatchedTradeNo / RejectsMismatchedMercID / WithSignVerifies
6. **回调 LimitReader 1 MiB**:防 OOM 授权安全测试。
7. **回调 JSON 解析失败立即落库 + return**:避免空 cb 污染去重表;旧版会用空 OID/TradeNo 走签名校验,污染 payment_callbacks。
8. **MarkVerified/MarkProcessed 包装 markVerifiedSafe/markProcessedSafe**:DB 抖动时 Error 级日志(原版 `_ =` 静默,导致状态永停留 PENDING,对账失明)。

### 鉴权 / 限流 / 契约(批 C)

9. **router.SetTrustedProxies**:配置驱动(`cfg.Server.TrustedProxies`),默认空 → ClientIP 永远用 RemoteAddr,防 X-Forwarded-For 伪造。
10. **JWTUserFailClosed**:钱包写接口(InitRecharge/CancelRecharge/SubmitWithdraw)单独挂 fail-closed,Redis 故障时拒绝;读接口仍走 fail-open。
11. **LoginAccountKey 真实实现**:从 body 读 account + NopCloser 回填,挂到 register/login 路由,5 次/min/账号补 IP 维度防爆破盲区。
12. **RechargeStatus 补 Channel 字段**:契约修复;PayType 因 model 缺列暂留 omitempty + 注释 TODO。
13. **tryDecrypt 失败加 Error 日志**(FINANCE RISK 标记):空姓名打款是真实风险。
14. **AES 构造失败加 Warn**:`aes, _ = NewAES(...)` 静默改为带错误日志。
15. **PostTx 后补 audit.Log**:充值结算 + 提现申请 两处事件级审计,跨表追溯。

### 代码质量(批 D)

16. **删 30 行手写 stringsLower / containsAny / indexOf** → 用 strings 标准库。
17. **writeStringSet 排序** sort.Strings:相同集合 → 相同 JSON,对账日志无噪音。
18. **RechargeStatus / WithdrawStatus 完整前缀重命名**,旧名 Deprecated 别名保留,新代码强制明确表达意图(原版 `StatusPending` 与 `WStatusPending` 值同名易调错)。
19. **InitRecharge 拆 callSharkTopay**:88 行 → 主流程 ~30 行 + helper 35 行,出栈分支独立。
20. **AccessLog path 默认用 FullPath()**:模板路径,无 PII;只 5xx 时追加 path_raw 含真实参数。
21. **EncKey startup validation**:长度 ≠ 32 / NewAES 失败均带 Error 日志,运营可在启动日志定位。
22. **MonthlyLimitMultiplier 可配**:消除 service.go 的 magic `10`,加 DefaultMonthlyMultiplier=10 兜底。

## 留作 follow-up(本批未拆)

- **SubmitWithdraw / UpsertBanner 完整拆分**:函数行数仍超 80,但拆分破坏性大、需要独立 PR review。当前可读性已通过命名 / 注释改善。
- **RechargeOrder model 加 pay_type 列**:需 migration,RechargeStatusResponse.PayType 暂留空。
- **JWT user scope 默认 fail-open → 全 fail-closed**:涉及非资金接口的 Redis 故障 SLA 决策,需运营确认。

## 测试 / 门禁

```
$ go build ./...        # 通过
$ go vet ./...          # 通过
$ go test -race -count=1 ./internal/...
ok   kickoff/go-app/internal/config             1.426s
ok   kickoff/go-app/internal/infra/payment/shark 1.358s
ok   kickoff/go-app/internal/pkg/ledger         1.663s
ok   kickoff/go-app/internal/service/admin      1.637s
ok   kickoff/go-app/internal/service/hook       2.665s
ok   kickoff/go-app/internal/service/member     2.362s
ok   kickoff/go-app/internal/service/wallet     1.959s
(全绿,含 race detector)

$ npm run check:openapi               # 通过
$ python3 scripts/validate-prd.py     # 通过(187 rows / 229 module IDs)
$ python3 scripts/validate-engineering-standards.py  # 通过
```

## 修改文件清单

### Go 代码(17 文件)

| 文件 | 改动类型 |
|---|---|
| `config/config.go` | +ServerConfig.TrustedProxies +WithdrawBizConfig.MonthlyLimitMultiplier +DefaultMonthlyMultiplier |
| `dto/wallet.go` | +Recharge/Withdraw Status 完整前缀常量,Deprecated 别名保留 |
| `repository/wallet/orders.go` | SumDaily/SumDailyTx 返回 decimal.Decimal;MarkRefunded 原子 UPDATE;+decimal import |
| `service/wallet/service.go` | callSharkTopay 拆出;monthlyUsed/MarkCancelled/UpdateThirdParty 加 logger;PostTx 后 audit.Log;Channel 字段填充;monthly multiplier 可配;删 stringsLower 等;+strings/audit/logger/zap import |
| `service/wallet/bank_account.go` | tryDecrypt 加 ctx + Error 日志;nil check 简化;+logger/zap import |
| `service/hook/payment.go` | HandleSharkPay/Refund JSON 解析失败立即落库;MarkVerified/MarkProcessed 包装 markVerifiedSafe/markProcessedSafe Error 日志 |
| `service/admin/payment_channels.go` | writeStringSet 排序;+sort import |
| `infra/payment/shark/client.go` | QueryOrder 一致性校验 + 乐观签名校验 |
| `infra/payment/shark/sign.go` | +VerifyQueryOrderResponse |
| `infra/payment/shark/types.go` | QueryOrderMsg +Sign 字段 |
| `infra/payment/shark/client_test.go` | +3 case(TradeNo/MercID 不一致 / 强签名)+ newTestClientWithSecret helper |
| `http/hook/payment.go` | readAll 加 LimitReader 1 MiB + ok 返回;maxCallbackBodyBytes 常量 |
| `http/hook/srs.go` | 跟着改 readAll 4 处调用 |
| `http/middleware/auth.go` | +JWTUserFailClosed + jwtMiddleware 提取 |
| `http/middleware/ratelimit.go` | LoginAccountKey 真实实现(body 复读 + 4 KiB 上限);+bytes/encoding/json/io import + maxLoginBodyBytes |
| `http/middleware/logger.go` | path 默认 FullPath();5xx 补 path_raw |
| `http/router/public.go` | SetTrustedProxies;EncKey startup 校验加 logger;requireUserAuthStrict 挂钱包写接口;loginAccountLimit 挂 register/login |
| `http/router/admin.go` | SetTrustedProxies;+context/zap/logger import |

### 文档

| 文件 | 改动 |
|---|---|
| `docs/agents/logs/2026-05-25-review-batch3-fix.md` | **新增** 本日志 |

## 设计决策摘录(供后续 Reviewer)

1. **decimal 精度全链路**:金额相关接口签名一律用 `decimal.Decimal`,禁止任何 float64 接 SUM/聚合。
2. **白名单写死 + 兜底默认值**:`publicChannels` / `publicConfigDefaults` / `publicChannels` 都写在 service 层不依赖 DB 标记字段,双重防泄漏。
3. **fail-closed 仅资金写接口**:JWTUserFailClosed 是性能 / 安全权衡 — 读接口 Redis 故障时降级放行,写接口严格拒绝。
4. **静默失败 → Error 日志 + helper 包装**:`markVerifiedSafe/markProcessedSafe` / `callSharkTopay` 等集中错误处理,主流程更可读。
5. **Deprecated alias 保留**:`StatusPending` / `WStatusPending` 暂不删,避免外部代码 break;新代码用完整前缀。

## 交接

下一位开发需要知道:

- **生产 trusted_proxies 必填**:k8s/nginx 环境在 yaml 配 `server.trusted_proxies: ["203.0.113.1/8"]`,否则 ClientIP 永远是 nginx 内网 IP,业务逻辑会失真。
- **withdraw.monthly_limit_multiplier 可调**:不配则走默认 10,符合 PRD §4.2.4。
- **AccessLog path 字段已变**:接日志查询的 dashboard 若按精确 path 过滤,需改用 path 模板(`/api/v1/wallet/recharge/:order_no/status`)或读 path_raw(仅 5xx)。
- **Status 常量重命名**:旧 `dto.StatusPending` / `dto.WStatusPending` 仍可用但 Deprecated,新代码用 `dto.RechargeStatusPending` / `dto.WithdrawStatusPending`。
- **RechargeOrder.PayType 缺列**:RechargeStatusResponse.PayType 暂返回空;补列需 migration。
- **SubmitWithdraw / UpsertBanner 仍偏长**:本批仅最小授权安全测试改 monthly 常量,完整拆分留 follow-up PR。
