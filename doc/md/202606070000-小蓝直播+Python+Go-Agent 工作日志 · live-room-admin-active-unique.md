---
id: "doc-552430cdfea9"
title: "Agent 工作日志 · live-room-admin-active-unique"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "MySQL", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-admin-active-unique.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-admin-active-unique.md"
sourceSha256: "a408c3823e211b01f4092d501b71ad31296d44526f54c1b72d54281449d7f85f"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-room-admin-active-unique

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-live-room-admin-active-unique.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：修复 `live_room_admins` 活跃房管授权可重复的问题

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-915
- 接口/契约：不改接口；仅修正 DB 约束与服务端写入幂等语义
- 团队可读文档：`docs/architecture/data-model.md`
- 其他：dev 实库确认 `live_room_admins` 存在 1 组活跃重复授权

## 本次目标

1. 清理历史重复活跃房管授权。
2. 用 DB 唯一约束阻断未来重复活跃授权。
3. 服务层授权写入改成数据库 upsert，避免并发下 Count 后 Insert 的竞态。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000046_fix_live_room_admin_active_unique.up.sql` | 清理重复活跃授权，增加 `active_key` 生成列与唯一索引 |
| `services/go-app/migrations/000046_fix_live_room_admin_active_unique.down.sql` | 回滚 `active_key` 约束并恢复旧索引 |
| `services/go-app/internal/service/admin/room.go` | 房管分配改为 `INSERT ... ON DUPLICATE KEY UPDATE id = id` |
| `services/go-app/internal/service/admin/room_test.go` | 覆盖 upsert SQL 与 migration 静态检查 |
| `docs/architecture/data-model.md` | 更新 `live_room_admins` 索引说明 |

## 核心决策

1. 不继续使用 `UNIQUE(room_id, admin_id, revoked_at)`，因为 MySQL UNIQUE 允许多条 `NULL`。
2. 使用生成列 `active_key`，活跃时为 `room_id:admin_id`，撤销后为 `NULL`，由 MySQL 自动维护。
3. migration 清理重复行时保留最早授权记录，后续重复记录设置为已撤销；撤销时间按行号错开毫秒，避免旧唯一键冲突。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-915 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及，接口路径和响应不变 |
| 不涉及契约的原因 | 修复服务端数据一致性约束，不改变 API 契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 是，新增 000046 up/down migration |
| 是否影响账本、事务、幂等或审计 | 不影响资金账本；影响房管授权幂等语义 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要随后端部署执行 migration up |
| 回滚 | `migrate down 1` 可恢复旧 schema；up 中被撤销的重复授权不会自动恢复 |
| 密钥 | 不涉及 |
| 备份恢复 | migration 会更新 `live_room_admins.revoked_at`，生产执行前建议确认备份 |
| 观测 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | DB 约束兜底，服务层 upsert，避免并发重复授权 |
| 红队质疑 | migration 会撤销重复授权；这是修复脏数据所需，但上线前应在目标环境先查重复组 |
| 合入判断 | 允许进入 review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin -run 'TestAssignRoomAdminQueryUsesDatabaseUpsertGuard|TestLiveRoomAdminActiveUniqueMigration' -count=1` | 通过 |
| `go test ./internal/service/admin -count=1` | 通过 |
| dev MySQL 临时库执行 000046 up/down smoke test | 通过；重复活跃组变为 0，生成列与唯一索引存在，down 可执行 |
| `go test ./... -count=1` | 通过 |
| `go vet ./...` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |

## 风险与待办

1. 其他 `UNIQUE(..., deleted_at)` 表仍是潜在同类风险，本次只修复已确认中招的 `live_room_admins`。
2. dev 实库当前重复组会在部署 migration 时被自动清理。
3. 若生产已存在更多重复活跃授权，migration 会保留最早一条，撤销后续重复记录。
