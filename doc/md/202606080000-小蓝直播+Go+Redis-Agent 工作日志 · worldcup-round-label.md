---
id: "doc-b522f83239b5"
title: "Agent 工作日志 · worldcup-round-label"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-worldcup-round-label.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-worldcup-round-label.md"
sourceSha256: "33ff7168a3c701022bb5e32b7a0f3f07ba5cffe1a455e9d0ad62d1968ec1b31d"
sourceSystem: "project-doc"
---

# Agent 工作日志 · worldcup-round-label

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606080000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BRedis-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20worldcup-round-label.md)

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：世界杯赛程导入轮次口径修正

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-930
- Excel：`/Users/qx/Downloads/2026世界杯赛程表&参赛国.xlsx`
- 页面：`https://admin-dev.54-151-131-132.sslip.io/#/matches`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`

## 本次目标

1. 按 Excel “轮次”列口径展示赛事轮次。
2. 小组赛轮次解析失败时阻断导入，不再静默写入 0。
3. 后台赛事列表显示“小组赛第一轮 / 1/16决赛”等运营可读文案。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/data_reset.go` | 小组赛轮次解析改为严格校验，失败返回 Excel 行号 |
| `services/go-app/internal/service/admin/match.go` | admin 赛事列表增加 `round_label` |
| `services/go-app/internal/service/admin/data_reset_test.go` | 覆盖小组赛轮次解析 |
| `services/go-app/internal/service/admin/match_test.go` | 覆盖世界杯轮次展示文案 |
| `apps/admin/src/api/modules/match.ts` | AdminMatchItem 增加 `round_label` |
| `apps/admin/src/views/matches/list.vue` | 列表阶段列改为轮次展示，优先使用 `round_label` |
| `apps/admin/src/locales/langs/zh-CN/matches.json` | 同步中文轮次文案 |
| `apps/admin/src/locales/langs/en-US/matches.json` | 同步英文轮次文案 |
| `docs/api/openapi.yaml` | 记录 `round_label` 字段 |
| `packages/contracts/openapi/v1.yaml` | 同步 contract |

## 核心决策

1. `stage` 继续保存标准枚举，避免破坏赛程、首页、分组赛逻辑。
2. `round` 保存结构化轮次数字，`round_label` 负责还原 Excel 可读轮次。
3. 后台列表展示 `round_label`，未知旧数据保留兜底展示。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-930 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | Admin 赛事列表增加非破坏字段 `round_label` |
| 是否影响前端字段 | 新增字段，不删除不改名；后台已接入 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin -run 'Test(ParseWorldcup|ParseGroupRound|MatchRoundLabel|BuildMatch|MatchStatus|MatchWriteError|DataReset|RedisCleanup|CleanupPlan|WrapDataReset|ParseExcel|RewardPrize)'` | 通过 |
| `go test ./internal/service/admin` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:stg` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 风险与待办

1. 已导入的历史数据如果小组赛 `round=0`，需要重新执行数据初始化才会修正为第一/二/三轮。
2. 后续新增赛事阶段时，需要补充 `matchRoundLabel` 和后台 locale。
