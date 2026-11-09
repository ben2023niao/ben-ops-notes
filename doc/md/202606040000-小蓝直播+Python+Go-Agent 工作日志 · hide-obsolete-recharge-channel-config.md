---
id: "doc-8289e810a149"
title: "Agent 工作日志 · hide-obsolete-recharge-channel-config"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-hide-obsolete-recharge-channel-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-hide-obsolete-recharge-channel-config.md"
sourceSha256: "f2ebf1c3edccdfc60142a52174edf507519ba186460effe8db6f3374365a11ad"
sourceSystem: "project-doc"
---

# Agent 工作日志 · hide-obsolete-recharge-channel-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20hide-obsolete-recharge-channel-config.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：移除/隐藏充值通道冲突配置

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：ADM-914 / WALLET-002
- 接口/契约：`GET /api/v1/admin/system/config`、`GET /api/v1/admin/payment-channels`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`
- 其他：用户确认 `wallet.recharge.channels.disabled` 属于废配置，避免运营误会。

## 本次目标

1. 清理 `wallet.recharge.channels.disabled` 历史残留配置。
2. 支付通道页托管的配置不再出现在通用系统配置页。
3. 保持 `/orders/payment-channels` 对 `enabled/recommended/fee_rate` 的读取不变。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/system.go` | 系统配置列表隐藏支付通道托管 key |
| `services/go-app/internal/service/admin/system_public_test.go` | 增加隐藏规则单测 |
| `services/go-app/migrations/000039_remove_wallet_recharge_channels_disabled.up.sql` | 删除废配置 `wallet.recharge.channels.disabled` |
| `services/go-app/migrations/000039_remove_wallet_recharge_channels_disabled.down.sql` | rollback 时恢复空废配置占位 |

## 核心决策

1. `wallet.recharge.channels.disabled` 从未被服务端读取，直接 migration 删除。
2. `wallet.recharge.channels.enabled`、`wallet.recharge.channels.recommended`、`wallet.recharge.channels.fee_rate.*` 不是废配置，但归 `/orders/payment-channels` 页面管理；从通用系统配置页隐藏，避免双入口冲突。
3. 充值规则页继续展示金额、上下限、手续费、钻石比例和精确充值包。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 新增数据清理 migration，无表结构变更 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金写操作 |
| 是否影响 OpenAPI | 不涉及，接口字段未变化 |
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

## 风险与待办

1. 部署后需跑 migration，dev 库历史残留的 `wallet.recharge.channels.disabled` 才会物理删除。
2. 运营改支付方式开关、推荐、单通道费率时统一使用“支付通道”页面。
