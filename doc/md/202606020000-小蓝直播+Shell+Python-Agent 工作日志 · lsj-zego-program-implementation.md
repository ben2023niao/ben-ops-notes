---
id: "doc-4e06ce5ab085"
title: "Agent 工作日志 · lsj-zego-program-implementation"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-program-implementation.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-program-implementation.md"
sourceSha256: "a82cfb223e8cbbb3deb2d0e52fc327d928a44cb682fc15af946a82187b04bb9b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-zego-program-implementation

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-zego-program-implementation.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：LIVE-101 LSJ + ZEGO 云播放器节目流后端实现。

## 背景

最终流程已明确：

1. LSJ 是唯一赛事直播源。
2. 后台给赛事绑定 LSJ `app_name` / `stream_name`。
3. 后台创建直播间时关联赛事。
4. 后台发起 `prepare-live`，后端实时调用 LSJ `play` 获取 m3u8，再调用 ZEGO 云播放器 `CreatePlayer`。
5. 后端保存并返回 `match_stream_id`。
6. 主播端 Web 拉 `match_stream_id`，自己推摄像头/麦克风 `host_stream_id`，然后用 ZEGO Web SDK 混流。
7. 主播端回写 `mixed_stream_id`，C 端只拉 `mixed_stream_id`。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000030_create_lsj_program_tables.up.sql` | 新增赛事 LSJ 源绑定表、房间节目流 session 表。 |
| `services/go-app/migrations/000030_create_lsj_program_tables.down.sql` | 回滚上述两张表。 |
| `services/go-app/internal/model/match.go` | 新增 `MatchLSJSource` model。 |
| `services/go-app/internal/model/live.go` | 新增 `RoomProgramSession` model。 |
| `services/go-app/pkg/zego/cloud_player.go` | 新增 ZEGO 云播放器 `CreatePlayer` / `DeletePlayer` 适配。 |
| `services/go-app/internal/service/liveprogram/service.go` | 新增节目流业务服务。 |
| `services/go-app/internal/service/live/service.go` | C 端 `play-url` 优先返回 active program 的 `mixed_stream_id`；无 mixed 时 fallback 到原 `stream_no`。 |
| `services/go-app/internal/http/adminapi/program.go` | 新增后台节目流 handler。 |
| `services/go-app/internal/http/streamerapi/program.go` | 新增主播端节目流 handler。 |
| `services/go-app/internal/http/router/admin.go` | 挂载后台赛事源和 prepare-live 路由。 |
| `services/go-app/internal/http/router/public.go` | 挂载主播端 program 和 mixed-stream 路由。 |
| `docs/api/streamer-lsj-zego-cloud-player.md` | 更新前端接入说明和真实测试命令。 |

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `go test ./pkg/zego ./internal/service/liveprogram` | 通过 |
| `go test ./internal/service/live` | 通过 |
| `go test ./...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 真实测试状态

本机环境未注入 `APP_LIVE_SOURCE_LSJ_*` 和 `APP_ZEGO_*`，因此本机未执行真实云播放器创建。

已新增默认跳过的真实供应商测试：

```bash
RUN_REAL_LSJ_ZEGO=1 go test ./pkg/zego -run TestRealLSJToZegoCloudPlayer -count=1 -v
```

该测试会实际调用 LSJ `sportsLive/play`、ZEGO `CreatePlayer`，并在测试结束时调用 `DeletePlayer` 清理。

dev 服务器公网接口真实验证：

| 步骤 | 结果 |
| --- | --- |
| 主播端 `/api/v1/streamer/sports-live?status=1&type=1` | 返回 1 条可播放 LSJ 线路：`app_name=sla`、`stream_name=1-6a1602d02e7f84ab1d46bfa3`。 |
| 后台 `PUT /api/v1/admin/matches/21011670562242561/lsj-source` | 通过，赛事成功绑定 LSJ 源。 |
| 后台 `POST /api/v1/admin/rooms/22000938818469889/prepare-live` | LSJ 取流通过，ZEGO `CreatePlayer` 失败。 |
| ZEGO 返回 | `350006006 app is not registered`，`request_id=9175981121582684269`。 |
| 后台 `GET /api/v1/admin/rooms/22000938818469889/program` | 返回“直播间尚未准备节目流”，确认没有落下脏 session。 |

结论：当前失败点不在 LSJ，也不是后端参数格式；ZEGO 官方文档中 `350006006` 对应云播放器服务未开通/权限未激活，需要在即构控制台或联系即构支持开通当前 AppID 的 Cloud Player。
