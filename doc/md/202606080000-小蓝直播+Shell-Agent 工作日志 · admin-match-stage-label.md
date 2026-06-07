---
id: "doc-8e6143ba8583"
title: "Agent 工作日志 · admin-match-stage-label"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-match-stage-label.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-match-stage-label.md"
sourceSha256: "af2a653b90861a09c71effa37ebd086875622ec8bb63777d0f9586360729db3e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-match-stage-label

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-admin-match-stage-label.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：后台赛事列表阶段枚举展示修正

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-930
- 页面：`https://admin-dev.54-151-131-132.sslip.io/#/matches`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`

## 本次目标

1. 后台赛事列表不再直接展示 `group_stage` 等后端枚举值。
2. 阶段筛选、新建、编辑改为下拉选择，避免运营手填技术枚举。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/matches/list.vue` | 增加赛事阶段选项和展示 formatter；阶段输入改为 Select |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 增加中文阶段文案并调整帮助说明 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 增加英文阶段文案并调整帮助说明 |

## 核心决策

1. 不改后端 API；后端继续返回 OpenAPI 定义的 snake_case 阶段枚举。
2. 后台 UI 负责将枚举转换为运营可读文案。
3. 未识别的历史阶段值兜底原样显示，避免旧数据无法展示。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-930 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及契约变更 |
| 是否影响前端字段 | 不涉及字段改名、删除或类型变化 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 未新增测试文件；admin 当前没有前端单测脚本，用 typecheck/build 验证 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:stg` | 通过 |

## 风险与待办

1. 仅后台页面显示修正，不影响 C 端和主播端。
2. 若后端未来新增阶段枚举，需要同步补充后台阶段选项和中英文文案。
