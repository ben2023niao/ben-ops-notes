---
id: "doc-bdd65513f4f5"
title: "Agent 工作日志 · bug-27603-hide-bet-orders-menu"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-27603-hide-bet-orders-menu.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-27603-hide-bet-orders-menu.md"
sourceSha256: "277062898abaa54dc5292609fd8b25d0240164f6a177efb785df16dcfff0606b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-27603-hide-bet-orders-menu

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20bug-27603-hide-bet-orders-menu.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：修复 ZenTao Bug 27603 - 财务管理去掉押注订单菜单

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-501 / ADM-506
- Bug：ZenTao #27603
- AI/工具控制文件：`AGENTS.md`、`aixn-zaodao-bug-fixer`

## 本次目标

1. 财务管理左侧子菜单不再展示“押注订单”。
2. 同步后台 PRD 中竞猜下线后的订单中心口径。
3. 不删除后端历史接口和页面文件，避免扩大影响面。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/router/routes/modules/finance.ts` | 移除 `BetOrders` 静态路由，财务菜单不再展示押注订单。 |
| `docs/prd/modules/kickoff-admin.md` | 标记 ADM-501 / ADM-506 已下线，并补充财务菜单展示口径。 |

## 核心决策

1. 当前版本竞猜功能已下线，因此押注订单不应作为财务菜单入口展示。
2. 本次只隐藏后台菜单入口，不删除订单 API、类型和历史页面，降低回归风险。
3. 财务菜单保留充值订单、提现订单、支付回调、支付通道。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-501 / ADM-506 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及契约变更 |
| 不涉及契约的原因 | 仅调整后台静态菜单入口，未改接口和响应结构 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 不涉及 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，后台菜单配置调整 |
| 涉及能力 | 不适用 |
| 高风险触发项 | 不涉及资金写操作 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 admin 前端构建产物 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `rg "BetOrders|/orders/bets|page\\.finance\\.bets" apps/admin/src/router/routes/modules/finance.ts` | 无匹配 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应页面 | 后台财务管理左侧菜单 |
| 页面截图 | 未截图；本次通过静态路由检查和类型检查验证 |
| API 接口路径 | 不变 |
| 合入判断 | 可合入 |

## 风险与待办

1. 历史押注订单页面和 API 仍保留，当前只是从菜单隐藏。
2. 如果产品要求彻底下线竞猜后台能力，需要另开任务清理 predict 页面、订单 API 和相关权限。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 财务菜单不再挂载 `BetOrders`。
2. 本次未删除 `apps/admin/src/views/orders/bets.vue` 和 `/api/v1/admin/orders/bets`。
3. 竞猜相关全量清理不在本次 Bug 范围内。
