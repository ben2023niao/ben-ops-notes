---
id: "doc-0b557bcadc17"
title: "Agent 工作日志 — 补 P0 公开读接口(wallet/channels + config/system)"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-public-config-channels.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-public-config-channels.md"
sourceSha256: "4c121489b6e2c85028ae82d922f9c3d905780874a09053fa9a25ef6f50faf994"
sourceSystem: "project-doc"
---

# Agent 工作日志 — 补 P0 公开读接口(wallet/channels + config/system)

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-public-config-channels.md`

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期:2026-05-24
Agent:Claude(Opus 4.7)
任务:基于 B1-B6 审计 + 原型核对,补 2 个前端 codegen 必需的公开读接口

## 触发

上一轮审计(`2026-05-24-wallet-audit-b1to6.md`)指出 admin 配置接口缺对应 public 读接口。
对照原型(2026.05.23迭代版.html)后用户决策:

- ✅ **做**:充值子通道列表 + 平台费率/金额预设/上下限(system_config 白名单)
- ❌ **不做**:等级 L0-L6 七级特权表(原型未定义特权权限)、MVP/事件流、礼物 SKU、第三方登录 等(已写入 CLAUDE.md `v1 范围外功能`)
- ⚖️ 同时强调:**本项目只做后端 API**,不做前端 UI、不评估纯前端能力(已写入 CLAUDE.md `项目角色边界`)

## 本次改动

### 1. CLAUDE.md 新增两节

- `项目角色边界(强制)`:明确只做后端 API,看到原型有但不确定后端要不要做的功能 → **先问用户**
- `v1 范围外功能`:把决策落地的 9 个不做项目列表化,避免下次会话再误判

### 2. 新增 2 个公开读接口

| 接口 | 用途 | 数据源 |
|---|---|---|
| `GET /api/v1/config/system` | 平台费率 / 充值金额预设 / 上下限 | system_configs 白名单(6 个 key) |
| `GET /api/v1/wallet/channels` | 当前可用充值子通道 4 选 1 | system_configs `wallet.recharge.channels.enabled/recommended` |

### 3. 关键设计

#### system_config 白名单(`SystemService.PublicView`)
- 白名单 **写死在 service 层** publicConfigDefaults map,不依赖 DB `is_sensitive`(双重保险)
- 6 个 key + 兜底默认值,DB 缺 key 走 default(全新部署也能拿到完整结构)
- 一次 SELECT IN 拉所有 keys,Go 端按类型反序列化(string / int / int_array)
- 默认值与 PRD 对齐:platform_fee_rate=0.05 / amount_options=[6,30,100,300,500,2000] / min=6/max=50000 / withdraw_min=10/max=5000

#### channels 公开视图(`PaymentChannelsService.PublicView`)
- 复用 admin service,加 `publicChannels` 白名单变量(alipay / wechat / union / digitalrmb)
- **不在白名单的(usdt_*)即使 enabled 也不返回** — 防止运营误操作泄漏 USDT 选项(ADR-0010 v0.3.2 暂缓)
- 访问策略验证 `fee_rate`(敏感) + `last_7d_success_rate`(内部运营)
- 顺序遵循 publicChannels 定义,前端按数组顺序渲染

#### 测试可测性
- 把 PublicView 的核心逻辑解耦为纯函数:
  - `buildPublicSystemConfig(vals map[string]string) → *PublicSystemConfigResponse`
  - `filterPublicChannels(enabled, recommended map[string]bool) → []PublicPaymentChannelItem`
- 无 sqlmock 依赖,纯函数表驱动测试

## 修改文件清单

### Go 代码
| 文件 | 改动 |
|---|---|
| `internal/dto/admin_modules.go` | +DTO:`PublicPaymentChannelItem` / `PublicPaymentChannelsResponse` / `PublicWalletConfig` / `PublicSystemConfigResponse` |
| `internal/service/admin/payment_channels.go` | +`publicChannels` 白名单 + `PublicView()` + `filterPublicChannels()` 纯函数 |
| `internal/service/admin/system.go` | +`publicConfigDefaults` 兜底 + `PublicView()` + `buildPublicSystemConfig()` 纯函数 |
| `internal/http/public/config.go` | **新增** — `SystemConfigHandler` + `WalletChannelsHandler` |
| `internal/http/router/public.go` | +装配 systemService / paymentChannelsSvc + 挂 `/config/system` `/wallet/channels` 两路由 |
| `internal/service/admin/system_public_test.go` | **新增** — 6 个 case(全 default / 全 override / 部分覆盖 / 空字符串 fallback / 非法 JSON / 非法 int) |
| `internal/service/admin/payment_channels_public_test.go` | **新增** — 6 个 case(全启用顺序 / USDT 过滤 / enabled 优先级 / 推荐但未启用 / 空 enabled / 中文 name) |

### 文档
| 文件 | 改动 |
|---|---|
| `CLAUDE.md` | +`项目角色边界`(强制)+ `v1 范围外功能`(9 项)两节 |
| `docs/api/openapi.yaml` | +2 路径(`/api/v1/config/system` `/api/v1/wallet/channels`)+ 2 schema(`PublicSystemConfig` `PaymentChannelPublicItem`) |
| `docs/agents/logs/2026-05-24-public-config-channels.md` | **新增** 本日志 |

## 测试

```
$ go test -race -count=1 ./internal/service/admin/...
ok   kickoff/go-app/internal/service/admin   1.755s

$ go test -race -count=1 ./internal/...
ok   kickoff/go-app/internal/service/admin   ...
ok   kickoff/go-app/internal/service/hook    ...
ok   kickoff/go-app/internal/service/member  ...
ok   kickoff/go-app/internal/service/wallet  ...
ok   kickoff/go-app/internal/pkg/ledger      ...
ok   kickoff/go-app/internal/infra/payment/shark ...
```

`go test -race ./internal/...` 全绿。

## 门禁

- ✅ `go build ./...`
- ✅ `go vet ./...`
- ✅ `python3 scripts/validate-prd.py`(187 rows / 229 module IDs)
- ✅ `python3 scripts/validate-engineering-standards.py`
- ✅ `npm run check:openapi`

## 设计决策摘录(供后续 Reviewer)

1. **白名单写死在代码而非 is_sensitive 列**
   - is_sensitive 是运营可编辑字段,误标=泄漏 AppSecret
   - 白名单写死意味着新增字段必须改代码 + code review,门槛更高
2. **不在白名单的子通道即使 enabled 也不返回**
   - 运营在 admin 改 `channels.enabled = ["alipay","usdt_trc20"]` 时,前端永远拿不到 USDT
   - PRD/ADR 决策的优先级 > 运营配置
3. **DB 缺 key 走默认值,不报错**
   - 全新部署 / migration 跑了 seed 没跑也能用
   - 前端 .map / .replace 不会因 undefined 炸
4. **核心逻辑解耦成纯函数**
   - 项目无 sqlmock 基础设施,纯函数 + 表驱动是最低成本可测路径
   - `buildPublicSystemConfig` / `filterPublicChannels` 12 个 case 覆盖正向 + 边界 + 容错

## 待办(留下一轮)

1. **联调 ¥6 大白鲨充值**(凭据到位后)
2. **前端 codegen**:OpenAPI 已就绪,前端可直接生成 SDK 对接 2 个新接口
3. **运营 seed 数据**:`wallet.recharge.channels.enabled` 初始值建议落 `["alipay","wechat","union","digitalrmb"]`,否则默认空集合 → 前端拿不到任何通道(开发期可手动 INSERT,生产期走 admin UI 配置)
4. **system_configs 现有 admin UPDATE** 不会自动 seed 新 key 默认值,后续如新增白名单 key 需评估是否要补 migration / seed

## 交接

下一位开发/前端工程师需要知道:

- **新增 2 个公开端点**:
  - `GET /api/v1/config/system` → 拿平台费率 + 充值金额预设 + 上下限
  - `GET /api/v1/wallet/channels` → 拿当前可用子通道列表(alipay/wechat/union/digitalrmb)
- **前端可以开始 codegen 对接钱包页**:OpenAPI 已就绪
- **USDT v1 不上线**:即使运营开启也不会出现在 `/wallet/channels` 返回中
- **system_configs 默认值**:见 `internal/service/admin/system.go` `publicConfigDefaults`,新增/修改白名单需同步改默认值
- **决策落地**:`CLAUDE.md` 已记录 9 个 v1 不做项目,后续会话不会再被误读
