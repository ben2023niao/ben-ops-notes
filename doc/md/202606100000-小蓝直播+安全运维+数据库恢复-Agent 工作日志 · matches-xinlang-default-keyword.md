---
id: "doc-37c88944d260"
title: "Agent 工作日志 · matches-xinlang-default-keyword"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-matches-xinlang-default-keyword.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-matches-xinlang-default-keyword.md"
sourceSha256: "25853d345cbdbb4170804131c7f1c7deb646088567b5b76de580a0d006deb026"
sourceSystem: "project-doc"
---

# Agent 工作日志 · matches-xinlang-default-keyword

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-matches-xinlang-default-keyword.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：赛事列表选源弹窗的新浪电影源默认展示林正英电影

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 设计图：不涉及
- 接口/契约：`GET /api/v1/admin/sports-live`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户指出 `https://admin-dev.54-151-131-132.sslip.io/#/matches` 页面未改

## 本次目标

1. 在赛事列表新建/编辑赛事的上游源选择弹窗中，选择“新浪电影源”后默认展示林正英相关电影。
2. 不增加额外搜索框，保持当前弹窗交互不变。
3. 保持体育源和 LSJ 电影源原有查询行为不变。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/matches/list.vue` | 选择 Xinlang 新浪电影源时自动向 `sports-live` 查询传入 `keyword=林正英` |

## 核心决策

1. 默认关键词只作用于 `type=100` 的新浪电影源。
2. `all` 仍只查询足球、篮球、电竞，不混入电影源。
3. 不修改后端接口契约，不影响直播间已绑定源。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不变 |
| 不涉及契约的原因 | 仅调整后台页面调用参数，不改变 API 字段、路径或响应结构 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 是否影响前端字段变更 | 不涉及前端契约字段变更 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 admin 静态构建产物，需要重新部署 admin-dev |
| 回滚 | 回滚本次提交即可恢复赛事列表选源弹窗默认电影第一页 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 页面 | `#/matches` |
| API 接口路径 | `GET /api/v1/admin/sports-live` |
| 后台权限与审计 | 只读源查询，不新增写操作 |
| 合入判断 | 可以合入 |

## 风险与待办

1. 该默认只作用于赛事列表选源弹窗，不影响已绑定上游源。
2. 线上部署后需验证：打开赛事新建/编辑弹窗，点击选择上游源，再切到“新浪电影源”，列表直接出现林正英电影。
