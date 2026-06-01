---
id: "doc-62b92642ea26"
title: "Agent 工作日志 · streamer-sports-live-source-api"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-streamer-sports-live-source-api.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-streamer-sports-live-source-api.md"
sourceSha256: "35ef6a58ad6c668bb5e4604613153477980e4b5982bfec694756142812553aca"
sourceSystem: "project-doc"
---

# Agent 工作日志 · streamer-sports-live-source-api

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-streamer-sports-live-source-api.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：完成主播端体育直播源接口，并记录 LSJ + ZEGO 云播放器目标链路。

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 架构决策：`docs/decisions/ADR-0015-lsj-sports-live-source-backend-ingestion.md`
- 验证资料：LSJ 真实接口、HLS captureStream PoC、HLS playlist 探针、ZEGO 云播放器与 Web 混流文档

## 本次目标

1. 给主播端提供可选体育直播源列表。
2. 给主播端按线路获取 LSJ m3u8 主/备地址。
3. 隐藏 LSJ appid/appkey。
4. 记录后续目标方案：后端调用 ZEGO 云播放器产出 `match_stream_id`，主播端 Web 发起 ZEGO 混流，C 端只拉 `mixed_stream_id`。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/streamer/sports_live_source.go` | 新增主播端体育源 service。 |
| `services/go-app/internal/service/streamer/sports_live_source_test.go` | 新增 service 单测。 |
| `services/go-app/internal/http/streamerapi/sports_live_source.go` | 新增 Gin handler。 |
| `services/go-app/internal/http/router/public.go` | 挂载 `/api/v1/streamer/sports-live*` 路由并按配置注入 LSJ client。 |
| `services/go-app/internal/dto/streamer.go` | 新增主播端体育源 DTO。 |
| `docs/api/openapi.yaml` | 同步主播端体育源 OpenAPI。 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI。 |
| `docs/api/streamer-lsj-zego-cloud-player.md` | 新增前端接入说明，明确 `match_stream_id` / `host_stream_id` / `mixed_stream_id` 分工。 |

## 核心决策

1. 体育源接口只挂主播端鉴权路由，不开放给 C 端。
2. `GET /api/v1/streamer/sports-live` 返回 LSJ 列表并计算 `can_play`。
3. `POST /api/v1/streamer/sports-live/play` 当前用于验证 LSJ 取流能力；目标方案中不应把 LSJ m3u8 返回给前端，而应由后端继续调用 ZEGO 云播放器。
4. 目标播放链路：
   - 后端：LSJ `play` -> ZEGO 云播放器 `CreatePlayer` -> `match_stream_id`。
   - 主播端 Web：拉 `match_stream_id` 预览比赛源，推 `host_stream_id`，发起 ZEGO 混流产出 `mixed_stream_id`。
   - C 端 Web：只拉 `mixed_stream_id`。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | `streamerSportsLiveSearch`、`streamerSportsLivePlay` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响 |
| 密钥 | LSJ appid/appkey 仍只由服务端 env/secret 注入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./...` | 通过 |
| `python3 scripts/validate-openapi.py` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 前端页面验收

本次不修改 `apps/web/**` 或 `apps/live-host/**`。目标方案的主播端后续接入：

1. 调 `GET /api/v1/streamer/sports-live?type=1&page=1&page_size=100` 选择 `can_play=true` 的线路。
2. 调后续新增的 `POST /api/v1/streamer/sports-live/cloud-player/start`，让后端启动 ZEGO 云播放器并返回 `match_stream_id`。
3. 主播端 Web 拉 `match_stream_id` 预览比赛源。
4. 主播端 Web 推自己的 `host_stream_id`。
5. 主播端 Web 用 ZEGO Web SDK 混流 `match_stream_id + host_stream_id -> mixed_stream_id`。
6. C 端只拉 `mixed_stream_id`。

## 风险与待办

1. 当前没有把体育源选择落库，刷新页面后需重新选源；后续可加房间级云播放器配置。
2. `main_url` / `backup_url` 是上游敏感源，目标方案不返回前端，只用于后端启动 ZEGO 云播放器。
3. 需要补 ZEGO 云播放器服务端 API 适配和云播放器任务表。
4. 后台管理闭环尚未完成：运营无法在后台预先绑定直播间与体育源、预览 LSJ 画面、检查 `status/is_played`、强制切换主备源或查看源失效告警。
5. 当前文档接口只有推送并部署到 dev 文档站后才能在 Stoplight 深链里查看；本次需提交并推送 `dev` 分支触发文档更新。
