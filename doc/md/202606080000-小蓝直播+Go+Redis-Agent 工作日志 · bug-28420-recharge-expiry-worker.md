---
id: "doc-4a219df75845"
title: "Agent 工作日志 · bug-28420-recharge-expiry-worker"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-bug-28420-recharge-expiry-worker.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-bug-28420-recharge-expiry-worker.md"
sourceSha256: "126353a7ea661b29947ad76b9fad308dd2b390e85cca3f8f160647fb23cc362e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28420-recharge-expiry-worker

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-bug-28420-recharge-expiry-worker.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：修复 Zandao Bug 28420：H5 充值记录中超过 30 分钟未支付订单仍显示支付中

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-007
- 接口/契约：`GET /api/v1/wallet/recharge-records`、`GET /api/v1/wallet/recharge/{order_no}/status`
- Bug：`https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28420`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 排查充值订单 30 分钟超时未失效的完整链路。
2. 修复充值超时延迟队列 worker 启动后立即停止的问题。
3. 增加 worker 生命周期测试，防止再次把非阻塞启动 API 当阻塞 API 使用。

## 数据链路

入口页面 / API：H5 我的-充值记录调用 `GET /api/v1/wallet/recharge-records`。
DTO / service：`internal/http/public/wallet.go` -> `wallet.Service.ListRecharges`。
repository：`wallet.RechargeRepository.List` 从 `recharge_orders` 查询订单。
DB / Redis：`recharge_orders.status` 保存订单状态；Redis asynq 队列保存 `wallet.recharge.expire` 延迟任务。
状态变更：`InitRecharge` 写入 `expires_at = now + 30min` 并投递延迟任务；worker 消费后调用 `MarkExpiredByOrderNo` 把仍为 `PENDING/PAYING` 的订单更新为 `FAILED`。
返回字段：列表返回 `status`，枚举仍为 `PENDING/PAYING/PAID/CANCELLED/REFUNDED/FAILED`。
前端消费：H5 已把 `FAILED` 显示为“超时取消”，本次不涉及前端字段变更。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/worker/recharge_expiry.go` | 修复 asynq server 生命周期，启动后阻塞等待 context 取消，避免立即 shutdown |
| `services/go-app/internal/worker/recharge_expiry_test.go` | 增加 worker 生命周期回归测试 |

## 核心决策

1. 保留 asynq 延迟队列方案，不退回每分钟扫表。
2. 保留启动时 backfill 作为历史未完成订单补投机制。
3. 不新增 `TIMEOUT` 字段；当前公开契约用 `FAILED` 表示超时未支付失败，H5 已正确映射为“超时取消”。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 涉及订单超时审计，沿用已有 `wallet.recharge.timeout_failed` |
| 是否影响前端字段 | 不涉及前端字段变更 |
| 是否影响 OpenAPI / contracts | 不涉及 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重启 `kickoff-worker`，让 asynq consumer 常驻消费 |
| 回滚 | 回滚本次 worker 代码即可，但会恢复超时任务不消费的问题 |
| 密钥 | 不涉及 |
| 观测 | 可通过 `journalctl -u kickoff-worker` 查看 `recharge expiry worker started/stopping` 和 `wallet.recharge.timeout_failed` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/worker ./internal/pkg/jobqueue ./internal/service/wallet ./internal/repository/wallet` | 通过 |
| `go test ./cmd/worker ./internal/worker` | 通过 |
| `go test ./internal/http/public ./internal/http/router` | 失败，原因是既有未提交 `internal/service/admin/data_reset.go` 与 `match.go` 重复定义 `matchNoFormat`，非本次改动引入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 风险与待办

1. dev 部署后需要确认 Redis `asynq:{wallet}:pending` 被消费，DB 中过期 `PENDING/PAYING` 订单降为 0。
2. 如果产品未来要求独立展示 `TIMEOUT`，需要先更新 OpenAPI 和前端契约，再新增状态，不应静默改字段。
