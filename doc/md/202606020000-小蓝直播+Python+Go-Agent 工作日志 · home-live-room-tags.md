---
id: "doc-833ec235dd9a"
title: "Agent 工作日志 · home-live-room-tags"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-home-live-room-tags.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-home-live-room-tags.md"
sourceSha256: "5fe65c9c2b8ca0e4124b07202b068b34b51f1754e811b86f05eb78611583a2ea"
sourceSystem: "project-doc"
---

# Agent 工作日志 · home-live-room-tags

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-home-live-room-tags.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：首页/赛事相关直播接口返回直播间 tags

## 输入资料

- 需求 ID：HOME-016
- 用户反馈：主播端修改直播间 `tags` 后，C 端 `GET /api/v1/home/live-rooms?limit=15` 未返回 `tags` 字段。
- 关联接口：`homeLiveRooms`、`matchLiveRooms`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. C 端首页直播间卡片返回主播端维护的 `tags`。
2. 同一 `HomeLiveRoom` 合约在赛事详情相关直播接口中也保持一致。
3. 同步 OpenAPI / contracts。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/home.go` | `HomeLiveRoomItem` 增加 `tags` 字段 |
| `services/go-app/internal/service/home/service.go` | 首页直播间解析 `live_rooms.tags` JSON |
| `services/go-app/internal/service/home/service_test.go` | 覆盖首页直播间 tags 返回 |
| `services/go-app/internal/service/schedule/service.go` | 赛事相关直播解析 tags |
| `services/go-app/internal/service/schedule/service_test.go` | 覆盖赛事相关直播 tags 返回 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | `HomeLiveRoom` schema 增加 `tags` |

## 核心决策

1. 主播端已有 `UpdateRoom` 保存 `live_rooms.tags`，本次只补 C 端读模型映射。
2. tags JSON 解析失败时返回空数组，避免坏数据影响列表接口。
3. `HomeLiveRoom` 是首页和赛事详情共用合约，两处都补齐。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./services/go-app/internal/service/home ./services/go-app/internal/service/schedule ./services/go-app/internal/http/public` | 通过 |
| `go test ./services/go-app/internal/...` | 通过 |
| `npm run openapi:validate` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate packages/contracts/openapi/v1.yaml` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 交接说明

1. `GET /api/v1/home/live-rooms` 现在返回 `tags: string[]`。
2. `GET /api/v1/match/{match_id}/live-rooms` 也返回同样字段。
3. 前端 shared type 已有 `tags?: string[]`，无需额外类型改造。
