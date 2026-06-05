---
id: "doc-dfd1bbcb1f99"
title: "Agent 工作日志 · bug-28420-recharge-timeout-worker"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Redis", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-bug-28420-recharge-timeout-worker.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-bug-28420-recharge-timeout-worker.md"
sourceSha256: "762a63b64c158c73a4109f88ab6fd2efd707d54b5cd3fb6a66332e2259eec543"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28420-recharge-timeout-worker

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-bug-28420-recharge-timeout-worker.md`

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

日期：2026-06-06
Agent：Codex
任务：修复禅道 Bug 28420，充值订单超过 30 分钟未完成后自动失效

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-007
- 接口/契约：`GET /api/v1/wallet/recharge-records`，`GET /api/v1/wallet/recharge/{order_no}/status`
- AI/工具控制文件：`AGENTS.md`，`/Users/qx/project/zandao_debug_fix_skills/SKILL.md`
- 其他：禅道 `https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28420`

## 本次目标

1. 充值订单超过 30 分钟仍处于 `PENDING/PAYING` 时自动变更为失效态。
2. 保持现有 OpenAPI/H5 契约不变，继续使用 `FAILED` 表示超时取消展示。
3. 使用 Redis 延迟队列作为主路径，并保留审计与历史订单补投。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/cmd/api/main.go` | API 启动时注入审计 DB，并挂载 asynq 充值过期 worker |
| `services/go-app/go.mod` / `services/go-app/go.sum` | 新增 `github.com/hibiken/asynq` 延迟队列依赖 |
| `services/go-app/internal/pkg/jobqueue/recharge_expiry.go` | 封装 `wallet.recharge.expire` 延迟任务、payload、taskID |
| `services/go-app/internal/pkg/jobqueue/recharge_expiry_test.go` | 覆盖延迟任务 payload / taskID |
| `services/go-app/internal/http/router/public.go` | public 钱包服务注入充值过期队列 client |
| `services/go-app/internal/worker/recharge_expiry.go` | 启动 asynq server，消费单笔充值过期任务，并启动时 backfill 历史未完成订单 |
| `services/go-app/internal/worker/recharge_expiry_test.go` | 覆盖单笔任务 handler 和坏 payload 不重试 |
| `services/go-app/internal/repository/wallet/orders.go` | 单笔过期事务更新、历史未完成订单 backfill 查询、保留批量兜底 |
| `services/go-app/internal/repository/wallet/orders_test.go` | 覆盖过期查询和 backfill 查询范围 |
| `services/go-app/internal/service/wallet/service.go` | 下单成功后投递充值过期延迟任务；投递失败则取消订单并 fail closed |
| `services/go-app/internal/service/wallet/sweeper.go` | 单笔过期消费、历史订单补投、超时审计 |

## 核心决策

1. 当前框架只提供 worker 目录/规则，不提供通用延迟队列；选用 `github.com/hibiken/asynq` 作为 Redis 延迟队列包，并继续遵守 ADR-0012 的 v1 内嵌 worker 架构。
2. 不新增 `TIMEOUT` 枚举，避免破坏已部署 OpenAPI/H5 类型；后端将超时订单标记为现有 `FAILED`，H5 已展示为“超时取消”。
3. 新订单创建后用 `ProcessAt(expires_at)` 投递单笔延迟任务，taskID 使用 `recharge-expiry:{order_no}` 幂等去重；worker 消费时事务内 `SELECT FOR UPDATE`，并写 `wallet.recharge.timeout_failed` 审计。
4. 启动时仅做一次历史未完成订单 backfill，把旧订单补投队列；`SweepExpiredRecharges` 保留为人工/应急兜底，不作为主路径。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | WALLET-007 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / Event / DTO | 不变，仍返回 `RechargeOrderStatus=FAILED` |
| 不涉及契约的原因 | 前端类型和 OpenAPI 已存在 `FAILED`，H5 已把 `FAILED` 渲染为超时取消 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响，`recharge_orders.expires_at` 和 `idx_status_expires` 已存在 |
| 是否影响账本、事务、幂等或审计 | 影响订单状态事务与审计；不写账本，因为未支付订单没有资金入账 |
| 规范例外与原因 | 不适用；已使用 Redis 延迟队列包 asynq，未引入新的外部基础设施 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 异步、数据一致性、审计 |
| 当前 MVP 边界 | asynq server 内嵌在 go-app 进程，使用现有 Redis 做 broker |
| 未来迁移成本 | 可拆到独立 worker 服务，订单状态和 API 契约无需变化 |
| 高风险触发项 | 资金、订单 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `git fetch origin && git status --short && git rev-list --left-right --count HEAD...@{upstream}` | 已执行，本地与 upstream 同步 |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/pkg/jobqueue ./internal/repository/wallet ./internal/service/wallet ./internal/worker` | 通过 |
| `go test ./...` | 通过 |
| `./devtools/framework check` | 通过 |

## 风险与待办

1. asynq 依赖 Redis；Redis 不可用时下单会 fail closed，避免产生不会自动失效的支付单。
2. 超时后如果第三方极晚回调支付成功，当前状态机不会自动入账，应按异常回调/人工对账处理。
3. 若产品后续要求 API 明确返回 `TIMEOUT`，需要单独更新 OpenAPI、DTO、后台和 H5 类型。
