---
id: "doc-c0ee184b79b7"
title: "Agent 工作日志 · member-wallet-api-alignment"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-member-wallet-api-alignment.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-member-wallet-api-alignment.md"
sourceSha256: "0df48686eb9d024f5ed3a29d5c4c5263c3342a73f95fa3f5dfa2f1e940340bc4"
sourceSystem: "project-doc"
---

# Agent 工作日志 · member-wallet-api-alignment

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-member-wallet-api-alignment.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：个人中心接口对齐：钱包、充值、提现、头像上传

## 输入资料

- PRD：`docs/prd/modules/kickoff-member.md`、`docs/prd/modules/kickoff-wallet.md`、`docs/prd/modules/kickoff-h5.md`
- 需求 ID：MEM-003、MEM-012、WALLET-010、WALLET-101、WALLET-106、H5-022、H5-029
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/qa/project-acceptance.md`、`docs/quality/code-standards.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：H5 原型 `file:///Users/qx/Downloads/2026.05.23迭代版.html#h5`，本次只修后端/契约/后台可用 API，不修改 `apps/web/**`

## 本次目标

1. 将 H5 个人中心钱包卡口径明确为“钻石主余额 + 累计充值”，不再通过 `me/profile.wallet` 暴露 RMB 余额/冻结/可提现字段。
2. 补齐充值确认页所需的充值拆算接口，支持 RMB 到钻石的展示计算。
3. 提现信息接口补齐账户状态、可提现状态和冻结原因，提现下单按平台手续费生成真实 `fee/actual` 金额。
4. 修复 `POST /api/v1/me/avatar`：按契约接收 multipart `file`，落存储后回写 `users.avatar_url`。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/wallet.go` | 新增充值拆算响应；提现信息补 `account_status/can_withdraw/withdraw_disabled_reason`。 |
| `services/go-app/internal/http/public/wallet.go` | 新增充值拆算 handler，兼容 `amount/rmb_amount` 与 `channel/pay_type` 入参。 |
| `services/go-app/internal/http/router/public.go` | 注册 `/api/v1/wallet/recharge/breakdown` 公共接口。 |
| `services/go-app/internal/service/wallet/recharge_quote.go` | 新增充值拆算服务，禁用未开放的 USDT。 |
| `services/go-app/internal/service/wallet/withdraw_breakdown.go` | 新增提现手续费、到账金额、账本分录和冻结状态判断 helper。 |
| `services/go-app/internal/service/wallet/service.go` | 提现信息/提现提交对齐冻结状态和平台手续费规则。 |
| `services/go-app/internal/service/wallet/*_test.go` | 补充值拆算、USDT 禁用、提现手续费和冻结状态单测。 |
| `services/go-app/internal/http/public/member.go` | 头像上传 handler 从 JSON URL 改为 multipart `file`。 |
| `services/go-app/internal/service/member/avatar_upload.go` | 新增头像文件校验、存储、回写头像 URL 的服务逻辑。 |
| `services/go-app/internal/http/public/member_avatar_test.go` | 覆盖 multipart 头像上传闭环。 |
| `docs/api/openapi.yaml` | 更新公开 OpenAPI。 |
| `packages/contracts/openapi/v1.yaml` | 同步契约文件。 |
| `docs/prd/modules/kickoff-member.md` | 个人中心钱包卡改为钻石口径。 |
| `docs/prd/modules/kickoff-wallet.md` | 标记充值拆算、提现信息和提现提交为已实现。 |
| `docs/prd/modules/kickoff-h5.md` | 对齐 H5 钱包页接口说明。 |
| `docs/prd/requirements.md`、`docs/prd/requirements.index.json` | MEM-003 名称改为钻石钱包卡。 |

## 核心决策

1. H5 个人中心 `/api/v1/me/profile` 只消费钻石钱包字段和 `cumulative_recharge_rmb`；RMB 可提现信息放到 `/api/v1/wallet/withdraw/info`，避免把内部 RMB 钱包字段全部暴露给 H5。
2. 充值确认页使用独立拆算接口 `/api/v1/wallet/recharge/breakdown`，不创建订单，避免“仅预览金额”误生成支付订单。
3. USDT 在当前版本未开放，接口直接返回功能关闭错误，不用假数据。
4. 提现按 `biz.withdraw.platform_fee_rate` 计算平台手续费，账本分录拆成用户扣款、平台应付和平台手续费。
5. 头像上传以 OpenAPI 为准，不再接受 JSON `{avatar_url}`；后端只接受 JPG/PNG/WebP 文件并生成平台存储 URL。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | MEM-003、MEM-012、WALLET-010、WALLET-101、WALLET-106、H5-022、H5-029 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-member.md`、`docs/prd/modules/kickoff-wallet.md`、`docs/prd/modules/kickoff-h5.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/wallet.go` |
| 验收证据行 | `docs/qa/project-acceptance.md` |
| 不涉及契约的原因 | 不适用，本次新增并更新契约。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不新增数据表 / migration / 索引 |
| 是否影响账本、事务、幂等或审计 | 影响提现账本分录计算；未新增 admin 写操作，不涉及审计日志。 |
| 规范例外与原因 | 无。 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，涉及资金展示口径、提现账本金额和公开 API 契约。 |
| 涉及能力 | 数据一致性 / 权限安全 / 资金 |
| 当前 MVP 边界 | USDT 充值暂未开放；充值拆算仅预览金额，不创建订单。 |
| 高风险触发项 | 资金 / 用户数据 |
| 能力门禁结论 | 允许合入，需 Reviewer / CI 裁决。 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | Go 服务接口变更，dev 分支自动部署后生效。 |
| 回滚 | 回滚本次提交即可恢复旧接口和提现手续费行为。 |
| 密钥 | 不新增密钥。 |
| 备份恢复 | 不影响数据库结构和备份策略。 |
| 观测 | 不新增指标；错误仍走统一响应。 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | H5 个人中心钱包字段已收敛为钻石主余额；累计充值仍按成功充值 RMB 展示；充值确认页、提现页、头像上传所需接口已补齐并覆盖单测。 |
| 红队质疑 | 提现真实支付出款仍依赖后续支付通道接入；本次只保证订单、钱包冻结和账本金额正确。 |
| 合入判断 | 可进入 dev 验证；本日志需 Owner 审核后再提交。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已完成后端实现、契约和本地测试，等待 Owner 审核日志与发布裁决。 |
| 完成裁决 | 只能由 Reviewer / Owner / QA / CI / Release Manager 给出。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | passed |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | passed |
| `cd services/go-app && go test ./internal/service/wallet ./internal/dto ./internal/http/public` | passed |
| `cd services/go-app && go test ./internal/service/member ./internal/http/public` | passed |
| `cd services/go-app && go test ./...` | passed |
| `npm run openapi:validate && npm run check:contract` | passed |
| `npm run check` | passed |

## 前端页面验收

本次不修改 `apps/web/**` H5 前端实现，只按原型和契约修后端 public API。

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | `file:///Users/qx/Downloads/2026.05.23迭代版.html#h5` |
| API 接口路径 | `/api/v1/me/profile`、`/api/v1/me/avatar`、`/api/v1/wallet/recharge/breakdown`、`/api/v1/wallet/withdraw/info`、`/api/v1/wallet/withdraw` |
| mock/fallback 状态与原因 | USDT 未开放，接口明确返回功能关闭。 |
| 合入判断 | 后端可发布，H5 需要前端团队按契约字段接入。 |

## 风险与待办

1. 远端 `dev` 已有前端钱包钻石口径提交，本次后端提交前需要 rebase 到最新 `dev`。
2. 提现支付通道真实出款接入后，需要补回调和出款失败退款闭环。
3. 本日志属于 `docs/agents/logs/**`，需 Owner 审核后才能提交。

## 交接说明

下一位 Agent 或工程师需要知道：

1. H5 个人中心主余额展示以 `diamond_balance/diamond_withdrawable/diamond_frozen` 为准；累计充值用 `cumulative_recharge_rmb`；提现弹窗 RMB 可提现额用 `/api/v1/wallet/withdraw/info`。
2. 充值拆算接口只用于前端预览，真正下单仍走充值创建订单接口。
3. 提现提交现在会按配置扣平台手续费，并把手续费写入提现订单与账本分录。
