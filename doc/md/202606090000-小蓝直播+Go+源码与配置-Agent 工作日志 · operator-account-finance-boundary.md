---
id: "doc-8503f47fd2ab"
title: "Agent 工作日志 · operator-account-finance-boundary"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-account-finance-boundary.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-account-finance-boundary.md"
sourceSha256: "689e9e518335ac91657cc62c84c69940c3793bad69b53e26ae06d9603b243c25"
sourceSystem: "project-doc"
---

# Agent 工作日志 · operator-account-finance-boundary

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606090000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20operator-account-finance-boundary.md)

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：用户管理增加运营账号，并隔离运营账号钻石/送礼财务口径

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-live.md`
- 需求 ID：ADM-402、ADM-406、LIVE-007
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/funds-and-ledger.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台用户管理可设置/取消运营账号。
2. 运营账号后台加钻保留账本和审计，但不生成充值订单、不进入真实充值口径。
3. 运营账号前台送礼保留互动和扣钻，但排除真实 GMV、主播收益、排行榜、众筹解锁和奖励。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000049_add_operator_account_tip_flags.*.sql` | 增加 `users.is_operator_account`、`live_tips.is_operator_tip` |
| `services/go-app/internal/service/admin/user.go` | 设置运营账号、调账 meta、运营账号消费档位过滤 |
| `services/go-app/internal/service/live/service.go` | 运营送礼标记、排除真实统计、使用 `platform:operations` |
| `services/go-app/internal/repository/live/*.go`、`services/go-app/internal/service/admin/{room,dashboard}.go` | 礼物榜、当前场次、房间统计、GMV 过滤运营送礼 |
| `apps/admin/src/views/users/list.vue` | 用户列表展示和操作运营账号 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 新增接口和字段说明 |

## 核心决策

1. 运营账号资金不能绕过账本，仍写 `wallet_journals` 和审计。
2. 运营账号对账账户使用 `platform:operations`，避免进入真实收入账户。
3. 每笔送礼使用 `live_tips.is_operator_tip` 做历史快照，用户后续取消运营账号不回算历史。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-402、ADM-406、LIVE-007 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 新增 `adminUserSetOperatorAccount`；新增 `is_operator_account`、`is_operator_tip` |
| 前端字段影响 | 后台新增 `is_operator_account`；C 端打赏响应/弹幕 meta 新增可选 `is_operator_tip`，旧字段未改名未删除 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 000049 up/down |
| 是否影响账本、事务、幂等或审计 | 是，仍走复式账本；设置运营账号和调账写审计 |
| ADR | `docs/decisions/ADR-0017-operator-account-finance-boundary.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin ./internal/service/live ./internal/repository/live ./internal/pkg/wsx ./internal/pkg/ledger` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
