---
id: "doc-f3807bada708"
title: "Agent 工作日志 · api-contract-alignment"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-api-contract-alignment.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-api-contract-alignment.md"
sourceSha256: "37065f9bd7fa3c733ad7329ac832695eb4475e3b74bb1da2b2e018025f93859c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · api-contract-alignment

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20api-contract-alignment.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：按 OpenAPI 契约修复前台公开 API 返回结构

## 输入资料

- PRD：`docs/prd/product-prd.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：HOME-005、HOME-006、HOME-010、MEM-001、MEM-004、MEM-KYC、LIVE-001、LIVE-007、LIVE-008、LIVE-016、PRED-002、PRED-008、PRED-009、PRED-010、WALLET-002、WALLET-101、WALLET-106、WALLET-107
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/qa/project-acceptance.md`、`docs/quality/code-standards.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：H5 原型仅用于核对展示数据，不修改 `apps/web/**`

## 本次目标

1. 以 OpenAPI 契约为准，修复后端 public API 返回字段、分页包装和缺失路由。
2. 对齐首页、直播、竞猜、钱包、个人中心相关数据结构，避免 H5 依赖契约字段时取不到数据。
3. 列出契约/实现仍需产品或安全确认的点。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/common.go` | 新增通用分页响应 `items + pagination`。 |
| `services/go-app/internal/dto/predict.go` | 竞猜活动、选项、押注 DTO 对齐 `PredictActivity/PredictBet`。 |
| `services/go-app/internal/http/public/predict.go` | 竞猜列表/我的押注改为契约分页结构，支持 `market_type`。 |
| `services/go-app/internal/service/predict/service.go` | 竞猜列表/详情/下注/我的押注映射契约字段并补 options。 |
| `services/go-app/internal/dto/home.go`、`services/go-app/internal/service/home/service.go`、`services/go-app/internal/http/public/home.go` | 首页热门竞猜、我的竞猜改为契约结构。 |
| `services/go-app/internal/dto/member.go`、`services/go-app/internal/service/member/service.go` | 个人资料与 KYC 状态/提交字段对齐契约。 |
| `services/go-app/internal/dto/live.go`、`services/go-app/internal/http/public/live.go`、`services/go-app/internal/service/live/service.go` | 直播间详情、播放地址、续期 token、打赏、房间活动对齐契约。 |
| `services/go-app/internal/http/public/live_lines.go`、`services/go-app/internal/service/live/lines.go` | 直播线路列表改为 `data.items` 并补 `enabled/sort_order`。 |
| `services/go-app/internal/dto/level.go`、`services/go-app/internal/http/public/level.go`、`services/go-app/internal/http/router/public.go` | 新增 `/api/v1/level/config` 公共接口。 |
| `services/go-app/internal/dto/wallet.go`、`services/go-app/internal/http/public/wallet.go`、`services/go-app/internal/service/wallet/service.go` | 提现信息、提交、状态、记录分页字段对齐契约。 |
| `services/go-app/internal/infra/payment/shark/**`、`services/go-app/internal/model/orders.go`、`services/go-app/migrations/000017_recharge_pay_type.*.sql` | 补齐充值 `pay_type` 持久化与 `/api/v1/wallet/recharge/pay-types` 查询依赖；通道未启用时返回空 options 而不是 500。 |
| `services/go-app/internal/dto/admin_modules.go`、`services/go-app/internal/service/admin/payment_channels.go` | 公开充值通道补 `enabled/fee_rate/last_7d_success_rate`。 |
| `services/go-app/internal/http/public/health.go` | `meta/feature-flags` 返回直接 map，去掉旧 `flags` 包装。 |

## 核心决策

1. 本次不改契约，按 `packages/contracts/openapi/v1.yaml` 实现真实返回。
2. `PredictActivityDetail` 收紧为纯 `PredictActivity`，不再额外返回 `rules_md/my_bets`，避免详情接口继续漂移。
3. 资金相关提现接口继续走已绑定支付宝账号查找，避免按明文 `alipay_account` 自动落库。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | HOME-005、HOME-006、HOME-010、MEM-001、MEM-004、LIVE-001、LIVE-007、LIVE-008、LIVE-016、PRED-002、PRED-008、PRED-009、PRED-010、WALLET-002、WALLET-101、WALLET-106、WALLET-107 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/**` |
| 验收证据行 | `docs/qa/project-acceptance.md` |
| 不涉及契约的原因 | 不适用，本次直接按契约修实现。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不新增数据表 / migration / 索引 |
| 是否影响账本、事务、幂等或审计 | 提现/押注/打赏仅调整 DTO 映射，原资金事务、账本、幂等逻辑保持不变。 |
| 规范例外与原因 | `WithdrawSubmitRequest.alipay_account` 按契约接收，但实现只匹配已绑定账号，避免明文账户自动落库。 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，涉及公共 API 契约、资金接口响应、直播接口响应。 |
| 涉及能力 | 数据一致性 / 权限安全 / 资金 / 直播 |
| 当前 MVP 边界 | 播放 URL/token 仍是占位模板；真实 CDN 鉴权待接入直播基础设施。 |
| 高风险触发项 | 资金 / 用户数据 / 生产发布 |
| 能力门禁结论 | 允许合入，需 CI/Reviewer 裁决。 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 仅 Go 服务代码变更，dev 分支自动部署。 |
| 回滚 | 回滚本次提交即可恢复旧响应结构。 |
| 密钥 | 不新增密钥。 |
| 备份恢复 | 不影响数据库结构和备份策略。 |
| 观测 | 不新增指标；错误仍走统一 `response.Fail`。 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 已按契约补齐主要 public API 返回字段、分页包装和缺失路由。 |
| 红队质疑 | `WithdrawSubmitRequest` 直接收 `alipay_account` 与当前加密绑定账户模型存在产品/安全边界差异；KYC `biz_token` 第三方核验链路尚未真正接入。 |
| 合入判断 | 可合入 dev 验证；上述差异需产品/安全后续确认。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已完成后端实现与本地测试，等待 CI、部署和业务验收。 |
| 完成裁决 | 只能由 Reviewer / Owner / QA / CI / Release Manager 给出。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | passed |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | passed |
| `npm run check:openapi` | passed |
| `npm run check:contract` | passed |
| `cd services/go-app && go test ./...` | passed |
| `cd services/go-app && go test ./internal/service/predict ./internal/http/public` | passed |
| `cd services/go-app && go test ./internal/service/wallet ./internal/http/public` | passed |
| staged 补丁应用到临时干净 worktree 后 `cd services/go-app && go test ./...` | passed |

## 前端页面验收

本次不修改 `apps/web/**` H5 前端实现，只按原型和契约修后端 public API。

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | `file:///Users/qx/Downloads/2026.05.23迭代版.html#h5` |
| API 接口路径 | 首页 / 直播间 / 竞猜 / 钱包 / 个人中心 public API |
| mock/fallback 状态与原因 | 播放 URL/token 仍为后端占位模板，待 CDN/SRS 接入。 |
| 合入判断 | 后端可发布，H5 需要前端团队按契约字段接入。 |

## 风险与待办

1. `WALLET-106` 契约要求提交 `alipay_account`，但当前安全模型要求先绑定并加密存储支付宝账号；如需“提交即绑定”，需补产品决策和审计设计。
2. KYC 契约要求 `biz_token`，当前服务只接收该字段，尚未调用第三方实名核验。
3. `match_brief` 目前优先使用竞猜标题，后续建议在 predict service join 比赛/球队生成真实 `法国 vs 阿根廷` 文案。
4. `/api/v1/level/config` 若数据库已有旧种子且缺 L6，不会触发默认七级 fallback，需单独补 level seed。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 契约仍以 `packages/contracts/openapi/v1.yaml` 为准，后端不要再返回旧的 `title/category/total/page` 等漂移结构。
2. 本次未修改 H5 前端，若页面仍拿旧字段，是前端接入任务。
3. 发布到 dev 后建议用真实 token curl 抽验：`/api/v1/predict/activities`、`/api/v1/live/lines`、`/api/v1/me/profile`、`/api/v1/wallet/withdraw/info`。
