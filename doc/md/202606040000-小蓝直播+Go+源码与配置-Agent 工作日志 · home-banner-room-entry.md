---
id: "doc-6ec186f571a5"
title: "Agent 工作日志 · home-banner-room-entry"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-home-banner-room-entry.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-home-banner-room-entry.md"
sourceSha256: "32571cd1937849c8ad7b66b6efcfca6e8115bbc171febb7447a73b36c0c46a7d"
sourceSystem: "project-doc"
---

# Agent 工作日志 · home-banner-room-entry

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20home-banner-room-entry.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：首页赛事 Banner 改为后台推荐直播间并返回直播间入口

## 输入资料

- PRD：`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`HOME-002`、`HOME-003`、`ADM-901`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/data-model.md`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`

## 本次目标

1. 后台直播间管理增加首页赛事 Banner 推荐配置。
2. `GET /api/v1/home/today-matches` 返回后台推荐直播间绑定的赛事，并携带 `live_room_entry`。
3. H5 首页 Banner 使用后端返回的直播间入口跳转，不再写死 `/live/r-101`。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000041_add_room_home_banner_fields.*.sql` | 新增直播间首页 Banner 推荐字段与索引 |
| `services/go-app/internal/model/live.go` | `LiveRoom` 增加推荐开关、排序、时间窗 |
| `services/go-app/internal/repository/live/live.go` | 新增推荐直播间查询 |
| `services/go-app/internal/service/home/service.go` | 首页推荐赛事改为取推荐直播间并组装 `live_room_entry` |
| `services/go-app/internal/service/admin/room.go` | 新增推荐配置保存、资格校验与 DTO 输出 |
| `docs/api/openapi.yaml` / `packages/contracts/openapi/v1.yaml` | 同步公开接口和后台接口契约 |
| `apps/admin/src/views/rooms/list.vue` | 后台直播间列表增加 Banner 推荐配置入口 |
| `apps/web/app/components/home/HeroCarousel.vue` | 首页 CTA 使用 `live_room_entry.url` |

## 核心决策

1. 推荐配置落在 `live_rooms`，因为运营实际推荐的是“绑定赛事的直播间”。
2. Banner 只展示启用推荐、已绑定赛事、未封禁、主播已审核且在时间窗内的直播间。
3. API 字段命名使用 `live_room_entry`，比通用 `entry` 更直观。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 `000041` up/down |
| 是否影响账本、事务、幂等或审计 | 非资金；后台保存推荐配置写 `admin.room.home_banner` 审计 |
| 是否影响契约 | 是，OpenAPI 和 contracts 已更新 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/live ./internal/service/schedule ./internal/service/streamer` | 已通过 |
| `go test ./internal/service/home ./internal/service/admin ./internal/repository/live` | 已通过 |
| `pnpm --filter @kickoff/admin typecheck` | 已通过 |
| `pnpm --filter @kickoff/web typecheck` | 已通过 |
| `npm run check:openapi` | 已通过 |
| `npm run check:contract` | 已通过 |
