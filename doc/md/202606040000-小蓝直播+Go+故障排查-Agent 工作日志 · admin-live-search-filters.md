---
id: "doc-0d9853258206"
title: "Agent 工作日志 · admin-live-search-filters"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-admin-live-search-filters.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-admin-live-search-filters.md"
sourceSha256: "9155036883f67cb1623b8b553d49fa385e09e258d421cd77a936bc2cc48528c1"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-live-search-filters

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-live-search-filters.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：修复后台直播间 / 主播管理搜索筛选无效

## 输入资料

- 反馈页面：`/rooms` 直播间管理、主播管理筛选条件
- 需求 ID：`ADM-901`（直播间列表）、`ADM-301`（主播列表）
- 接口契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`

## 问题定位

1. 直播间管理页面没有关键字输入框，且后端 `RoomHandler.List` 未读取 `status`，导致状态筛选无效。
2. 主播管理页面已传 `status`，但后端 `StreamerHandler.List` 固定传 `nil` 给 service，导致接口返回所有状态。
3. 主播搜索前端旧字段为 `keyword`，契约通用搜索字段为 `q`，本次前端改用 `q`，后端保留读取 `keyword` 作为过渡兼容。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/rooms/list.vue` | 增加直播间关键字搜索框，提交 `q` 和 `status` |
| `apps/admin/src/views/streamers/list.vue` | 主播管理关键字搜索改为提交 `q`，保留 `status` |
| `apps/admin/src/api/modules/streamer.ts` | 主播列表查询类型补充 `q` |
| `apps/admin/src/locales/langs/*/room.json` | 增加直播间搜索文案 |
| `apps/admin/src/locales/langs/*/streamer.json` | 补充主播 ID 搜索提示 |
| `services/go-app/internal/http/adminapi/room.go` | 解析直播间 `status`，非法状态返回参数错误 |
| `services/go-app/internal/http/adminapi/streamer.go` | 解析主播 `status`，读取 `q` / `keyword` |
| `services/go-app/internal/service/admin/room.go` | 统一直播间列表过滤，支持标题 / 房间编号 / ID 类字段 |
| `services/go-app/internal/service/admin/streamer.go` | 统一主播列表过滤，支持昵称 / 主播编号 / 主播 ID |
| `services/go-app/internal/http/adminapi/*_test.go` | 增加状态参数解析测试 |
| `services/go-app/internal/service/admin/*_test.go` | 增加列表过滤 SQL 回归测试 |

## 验证记录

- `go test ./internal/http/adminapi ./internal/service/admin`
- `pnpm --filter @kickoff/admin typecheck`
- `npm run check:openapi`
- `npm run check:contract`
- `npm run check:prd`
- `npm run check:engineering-standards`
- `npm run check:capability-gates`
- `npm run check:completion-claim`
- `git diff --check`
