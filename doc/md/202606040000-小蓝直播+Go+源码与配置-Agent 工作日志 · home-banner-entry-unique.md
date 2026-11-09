---
id: "doc-46320f2397c6"
title: "Agent 工作日志 · home-banner-entry-unique"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-home-banner-entry-unique.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-home-banner-entry-unique.md"
sourceSha256: "296fbfce88d42f0427fa70e0d2f2db3dd4841ee94e41513ea360cff8a68b06be"
sourceSystem: "project-doc"
---

# Agent 工作日志 · home-banner-entry-unique

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20home-banner-entry-unique.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：首页赛事 Banner 入口同赛事唯一化

## 输入资料

- 需求 ID：`ADM-901`、`HOME-002`
- 页面：后台直播间管理 `#/rooms`
- 接口：`POST /api/v1/admin/rooms/{id}/home-banner`、`GET /api/v1/home/today-matches`

## 产品口径

1. 一个赛事可以关联多个直播间。
2. 同一赛事只能有一个直播间作为首页赛事 Banner 的进入入口。
3. 后设置的入口房间会替换该赛事之前设置的入口房间。
4. 首页 Banner 展示赛事信息，点击按钮进入当前入口房间。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/room.go` | 开启首页入口时自动关闭同赛事其它入口房间；创建房间直接开启入口时也执行同样规则 |
| `services/go-app/internal/service/admin/room_test.go` | 增加同赛事其它入口关闭 SQL 回归测试 |
| `apps/admin/src/views/rooms/list.vue` | Banner 配置弹窗增加替换规则说明 |
| `apps/admin/src/locales/langs/*/room.json` | 后台文案从“Banner 推荐”调整为“首页入口”，并说明同赛事唯一 |
| `docs/api/openapi.yaml` / `packages/contracts/openapi/v1.yaml` | 同步接口说明 |
| `docs/prd/modules/kickoff-admin.md` / `docs/prd/modules/kickoff-home.md` | 同步产品口径 |

## 验证记录

- `go test ./internal/service/admin ./internal/http/adminapi`
- `go test ./internal/service/home`
- `pnpm --filter @kickoff/admin typecheck`
- `npm run check:openapi`
- `npm run check:contract`
- `npm run check:prd`
- `npm run check:engineering-standards`
- `npm run check:capability-gates`
- `npm run check:completion-claim`
- `git diff --check`
