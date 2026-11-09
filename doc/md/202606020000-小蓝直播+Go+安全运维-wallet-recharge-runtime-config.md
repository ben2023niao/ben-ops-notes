---
id: "doc-cb1c7c9bfacb"
title: "wallet-recharge-runtime-config"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-wallet-recharge-runtime-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-wallet-recharge-runtime-config.md"
sourceSha256: "3d709dc0f7b164fecf6e393936dfacb853e56463e9266b150fba3ac183f4ebbc"
sourceSystem: "project-doc"
---

# wallet-recharge-runtime-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-wallet-recharge-runtime-config.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：充值规则改为后台系统配置驱动，支持测试阶段 0.01 RMB = 1 钻

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`、`docs/prd/modules/kickoff-admin.md`（项目 admin PRD；门禁映射 `docs/prd/modules/admin.md`）
- 需求 ID：WALLET-011、ADM-914
- 接口/契约：`GET /api/v1/system/config`、`GET /api/v1/wallet/recharge/breakdown`、`POST /api/v1/wallet/recharge/init`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户确认测试阶段希望通过后台配置手续费、充值比例和 0.01 测试金额，不再走 env 临时开关。

## 本次目标

1. 后台 `system_configs` 能维护充值手续费、钻石比例、金额上下限、预设金额和精确充值包。
2. 充值试算、下单、支付回调入账、支付方式查询全部读取后台配置。
3. 前端公开配置返回小数金额字段和精确充值包，兼容旧整数字段。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/wallet/recharge_policy.go` | 新增充值规则读取和解析 |
| `services/go-app/internal/service/wallet/recharge_breakdown.go` | 计算逻辑支持手续费、比例和精确充值包 |
| `services/go-app/internal/service/wallet/service.go` | 下单、回调入账、pay-types 校验改读运行时配置 |
| `services/go-app/internal/service/wallet/recharge_quote.go` | 充值试算改读运行时配置 |
| `services/go-app/internal/service/admin/system.go` | 公开系统配置增加 decimal 字段和 packages |
| `services/go-app/internal/service/admin/payment_channels.go` | 启用通道前的大白鲨探测金额优先读后台最小金额 |
| `services/go-app/migrations/000031_seed_wallet_recharge_configs.*.sql` | seed 充值规则配置项 |
| `docs/api/openapi.yaml` / `packages/contracts/openapi/v1.yaml` | 同步公开配置契约 |
| `docs/prd/modules/kickoff-wallet.md` / `docs/prd/modules/kickoff-admin.md` / `docs/architecture/data-model.md` | 更新产品和数据模型口径 |
| `apps/admin/src/views/system/config.vue` | 系统配置页拆分 tab，新增充值规则表单 |
| `apps/admin/src/locales/langs/*/system.json` | 新增充值规则 tab 文案 |

## 核心决策

1. 不破坏旧 JSON 字段类型：保留 `recharge_min_amount`、`recharge_amount_options` 整数字段，新增 `*_rmb` 字符串字段支持 `0.01`。
2. `0.01 = 1 钻` 通过 `wallet.recharge.packages` 精确匹配实现；普通金额继续按 `floor((amount - fee) * diamond_rmb_rate)` 计算。
3. YAML / env 仅作为 DB 缺配置时的 fallback；上线运行口径以后台 `system_configs` 为准。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET-011、ADM-914 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-wallet.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`PublicWalletConfig` |
| ownerService | `services/go-app` |
| 验收证据 | `docs/qa/acceptance-evidence.md` |
| 项目级验收 | `docs/qa/project-acceptance.md` |
| 不涉及契约的原因 | 已更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 数据表设计 | 新增 seed migration，未改表结构 |
| 是否影响数据表 / migration / 索引 | 是，新增 `000031_seed_wallet_recharge_configs` up/down |
| 是否影响账本、事务、幂等或审计 | 是，充值回调入账钻石数读取后台规则；原订单幂等和账本事务保持不变 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 数据一致性 / 迁移 / 权限安全 |
| 当前 MVP 边界 | 只支持充值全局规则和精确金额包；不做按用户、按活动、按首充差异化 |
| 高风险触发项 | 资金 / 订单 / 收益 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行 migration 000031；无需新增 env |
| 回滚 | 回滚 migration 删除 6 个 `wallet.recharge.*` 配置，服务回退 YAML 默认 |
| 密钥 | 不涉及 |
| 观测 | 不新增日志；错误配置会在充值试算/下单时返回参数错误 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台配置可实现手续费 0、最小充值 0.01、0.01 精确入账 1 钻；入口为 `系统管理 / 系统配置 / 充值规则` |
| 红队质疑 | 直接修改旧字段类型会破坏前端，已改为新增 decimal 字符串字段 |
| 合入判断 | 可提交 reviewer 验收 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/wallet ./internal/service/admin` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| Playwright preview `http://localhost:4173/system/config` | 路由可加载；未登录跳转 `/auth/login`；本地 preview `/api/v1/admin/auth/login` 代理返回 502，无法进入内页 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及，后台运营配置页按现有 Vben + Element Plus 表单风格 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 后台桌面 1440×900；小视口 768px 以下单列 |
| 页面截图 | `.playwright-cli/page-2026-06-02T07-06-33-706Z.png`（375×812 登录拦截页）、`.playwright-cli/page-2026-06-02T07-05-18-239Z.png`（1440×900 登录拦截页） |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` 未新增，页面非 completed 视觉验收项 |
| 真实手机视口 | Playwright 375×812 已验证路由加载到登录拦截页；本地 preview 登录 API 返回 502，未进入系统配置内页 |
| 桌面/平板视口 | Playwright 1440×900 已验证路由加载到登录拦截页；表单实现为 2 列响应式布局，小视口降为 1 列 |
| API 接口路径 | `GET /api/v1/admin/system/config?category=wallet`、`PUT /api/v1/admin/system/config/{key}` |
| 后台权限与审计 | 保存按钮限制 `finance_admin` / `super_admin`；后端沿用 `admin.system.config_update` 审计 |
| SEO异常验证/meta | 不涉及 SEO异常验证/meta，后台管理登录后页面不参与搜索收录 |
| 合入判断 | 允许提交 reviewer 验收 |

## 交接说明

1. 测试阶段后台配置建议：`platform_fee_rate=0`、`min_amount=0.01`、`amount_options=["0.01","1","10","50"]`、`packages=[{"amount_rmb":"0.01","diamond_amount":1}]`。
2. 后台入口为 `系统管理 / 系统配置 / 充值规则`，不用进入通用 KV 表逐项查找。
3. 前端充值页应优先使用 `recharge_amount_options_rmb`、`recharge_min_amount_rmb`、`recharge_max_amount_rmb` 和 `/wallet/recharge/breakdown` 返回的 `diamond_amount`。
4. 生产恢复默认时，把手续费改回 `0.05`、最小金额改回 `10`，并清空 `recharge_packages`。
