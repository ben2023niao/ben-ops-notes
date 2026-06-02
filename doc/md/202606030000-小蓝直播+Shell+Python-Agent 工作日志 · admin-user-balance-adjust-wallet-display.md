---
id: "doc-95951194c8fa"
title: "Agent 工作日志 · admin-user-balance-adjust-wallet-display"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-user-balance-adjust-wallet-display.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-user-balance-adjust-wallet-display.md"
sourceSha256: "ec0aa879cb4d109e891322ea8888ef279cf3f9d4be4f68e8270f86a7e9622ca4"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-user-balance-adjust-wallet-display

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-admin-user-balance-adjust-wallet-display.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：修复后台用户余额调整后钻石余额列表不显示

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-115
- 接口/契约：`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`
- 其他：用户反馈后台 `/users` 页面余额调整后钻石余额不变，但正常充值后会显示。

## 本次目标

1. 查清余额调整后列表不显示钻石的根因。
2. 保证用户列表展示使用钱包权威余额。
3. 保证手工调账后 users 冗余余额与 wallets 同步。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/user.go` | 用户列表批量从 wallets 覆盖余额；手工调账事务内按 ledger AfterBalance 同步 users 冗余余额 |
| `services/go-app/internal/service/admin/user_test.go` | 增加列表余额覆盖单测 |

## 核心决策

1. 钱包余额权威来源是 `wallets` 表，`users.rmb_balance` / `users.diamond_balance` 只是后台展示冗余。
2. 列表页不能只读 users 冗余余额，否则调账、退款等 ledger 路径会显示旧值。
3. 调账同步 users 冗余余额时使用 ledger 返回的 `AfterBalance` 覆盖，不做 `+/- amount`，避免冗余字段旧值导致二次偏差。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 资金主变动仍走 `ledger.PostTx`；本次只同步展示冗余字段 |
| 是否影响 OpenAPI | 不涉及，响应字段未变化 |
| 是否影响部署配置 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./services/go-app/internal/service/admin ./services/go-app/internal/http/adminapi` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 风险与待办

1. 已存在历史调账导致的 users 冗余旧值，会在列表查询时被 wallets 覆盖显示；后续如需数据清洗可单独跑一次同步脚本。
2. C 端个人中心已读 wallets 权威余额，不受 users 冗余旧值影响。
