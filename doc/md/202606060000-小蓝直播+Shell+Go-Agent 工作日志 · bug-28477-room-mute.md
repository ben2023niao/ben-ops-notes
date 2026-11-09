---
id: "doc-d7e5a244f16f"
title: "Agent 工作日志 · bug-28477-room-mute"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "MySQL", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-bug-28477-room-mute.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-bug-28477-room-mute.md"
sourceSha256: "48e4b644c5fbc83523b05cad282dc196cda85d145039f18c757e884840308f7c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28477-room-mute

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606060000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20bug-28477-room-mute.md)

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

日期：2026-06-06
Agent：Codex
任务：修复 Zandao Bug #28477 后台直播间管控禁言失败

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-909
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 数据模型：`docs/architecture/data-model.md`
- 团队可读文档：`docs/qa/project-acceptance.md`
- AI/工具控制文件：`AGENTS.md`
- 缺陷来源：Zandao Bug #28477，后台直播间管理「管控」在线观众禁言接口提示缺少 `live_room_bans` 表。

## 本次目标

1. 后台禁言操作不再因为缺少表失败。
2. 被禁言用户在对应直播间发送弹幕时被后端拦截。
3. OpenAPI / contracts 与后台真实请求字段一致。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000045_create_live_room_bans.up.sql` | 新增房间级禁言表 |
| `services/go-app/migrations/000045_create_live_room_bans.down.sql` | 新增回滚脚本 |
| `services/go-app/internal/service/admin/room.go` | 后台禁言 upsert 写入禁言表，重复禁言更新过期时间、原因和操作者 |
| `services/go-app/internal/service/live/service.go` | C 端发弹幕前查询房间级禁言并返回 `20405` |
| `services/go-app/internal/pkg/errcode/errcode.go` | 新增 `ErrUserMuted` 错误码 |
| `docs/api/openapi.yaml` | `adminRoomMute` 请求字段改为 `duration_ms` |
| `packages/contracts/openapi/v1.yaml` | 同步契约字段 |
| `docs/architecture/data-model.md` | 补充 `live_room_bans` 已落地数据模型 |

## 核心决策

1. `live_room_bans` 采用 `UNIQUE(room_id,user_id)`，同一房间同一用户只保留当前禁言配置，重复禁言走 upsert。
2. 禁言历史不在业务表堆多条记录，后台操作历史通过 `admin_audit_logs` 保留。
3. 发弹幕路径只拦截未删除且未过期的房间级禁言，不引入全局用户禁言。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 是，新增 `000045_create_live_room_bans`，包含雪花 ID、软删除、创建/更新时间、唯一键和查询索引 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；后台禁言继续写 `admin_audit_logs` |
| 规范例外与原因 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 补表后后台禁言接口可写入数据；C 端发弹幕读取同一表，避免只让按钮成功但禁言不生效。 |
| 红队质疑 | 如果只补表不补发言拦截，用户仍可继续发弹幕；如果唯一键包含 `deleted_at`，MySQL 多 NULL 会导致 upsert 失效。 |
| 合入判断 | 允许合入；需部署时执行新增 migration。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/pkg/errcode ./internal/service/live ./internal/service/admin` | 通过 |
| `go test ./...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `./devtools/framework check` | 通过 |

## 风险与待办

1. 上线必须执行 `000045` migration，否则旧库仍会缺少禁言表。
2. 当前仅实现房间级禁言；如后续要做全局禁言，应新增独立模型和后台入口。

## 完成申请与裁决

| 项目 | 结论 |
| --- | --- |
| Agent Claim | verified |
| Project Decision | pending-review，项目级闭环以 `docs/qa/project-acceptance.md` 和 QA 回归为准 |
