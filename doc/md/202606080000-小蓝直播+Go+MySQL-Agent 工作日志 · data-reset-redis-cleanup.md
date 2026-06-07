---
id: "doc-09bad0b82653"
title: "Agent 工作日志 · data-reset-redis-cleanup"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "MySQL", "Redis", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-redis-cleanup.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-redis-cleanup.md"
sourceSha256: "8beb1dd6f3f18822fdf26df944f639b9e7801611493bb2ddfc81e0fad975a367"
sourceSystem: "project-doc"
---

# Agent 工作日志 · data-reset-redis-cleanup

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-redis-cleanup.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：数据初始化清理补充 Redis 运行时缓存

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-930
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户确认数据清理需要考虑缓存状态

## 本次目标

1. 数据初始化预览和执行纳入 Redis 清理项。
2. 按初始化范围精准清理，禁止 `FLUSHDB`。
3. 保留 `jti:revoked:*` 安全黑名单，避免影响后台 token 撤销状态。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/data_reset.go` | `DataResetService` 注入 Redis，预览/执行清理 Redis key pattern |
| `services/go-app/internal/http/router/admin.go` | admin router 创建数据重置服务时传入 Redis client |
| `services/go-app/internal/service/admin/data_reset_test.go` | 增加 Redis scope、预览计数、删除边界测试 |
| `docs/api/openapi.yaml` | 补充数据初始化会返回 Redis 清理项的说明 |
| `packages/contracts/openapi/v1.yaml` | 同步 OpenAPI contract 说明 |

## 核心决策

1. 不使用 `FLUSHDB`，只通过 `SCAN + DEL` 删除明确业务前缀。
2. `worldcup-seed-reset` 只清直播/看板/弹幕/旧竞猜锁等与重导赛事相关状态。
3. `prelaunch-full-reset` 额外清幂等键、限流计数、C 端和主播 token 撤销时间戳。
4. `jti:revoked:*` 不清，因为该 key 无法按 subject 区分，误删会削弱后台安全黑名单。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-930 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 更新 OpenAPI 描述；未新增字段 |
| 不涉及契约的原因 | 响应结构不变，仅 `cleanup.table` 允许返回 `redis:<pattern>` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 涉及幂等缓存清理；执行失败仍写审计 |
| 是否影响前端字段 | 不涉及字段改名或字段删除 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 缓存 / 权限安全 / 数据一致性 |
| 当前 MVP 边界 | 后台 super_admin 手动执行上线前数据初始化 |
| 高风险触发项 | 用户数据 / 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不影响部署入口；服务重启后生效 |
| 回滚 | 回滚本提交即可恢复为仅清 DB |
| 密钥 | 不涉及 |
| 备份恢复 | 清理 Redis 运行时状态，不替代 MySQL 备份 |
| 观测 | Redis 清理失败会返回错误并写审计失败记录 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin -run 'Test(DataReset|RedisCleanup|CleanupPlan|WrapDataReset|ParseWorldcup|ParseExcel|RewardPrize)'` | 通过 |
| `go test ./internal/http/router` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 风险与待办

1. Redis 清理与 MySQL 不能组成同一原子事务；当前策略为 DB 成功后清 Redis，失败则返回错误并写审计。
2. 异步队列不是缓存，本次没有直接清 `asynq:*`，避免破坏 worker 队列结构。

## 交接说明

1. 后台预览结果中 `cleanup.table` 可能出现 `redis:admin:dash:*` 这类条目。
2. 前端无需改字段结构，只按已有 cleanup 列表展示即可。
