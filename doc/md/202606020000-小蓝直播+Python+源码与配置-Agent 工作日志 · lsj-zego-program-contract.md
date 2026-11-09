---
id: "doc-51dc797e5e04"
title: "Agent 工作日志 · lsj-zego-program-contract"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-program-contract.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-program-contract.md"
sourceSha256: "e4f48d4daacd36ff355eb3f4b5e13d60592e288409ed68aca4774a3e6264cf6c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-zego-program-contract

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-zego-program-contract.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：LIVE-101 LSJ + ZEGO 云播放器节目流契约先行。

## 背景

方案已明确：

1. LSJ 是唯一赛事直播源，不支持后台手填 m3u8。
2. 后台创建赛事后绑定 LSJ `app_name` / `stream_name`。
3. 创建直播间必须关联主播和赛事。
4. 后台发起开播准备，后端调用 LSJ `play` 并启动 ZEGO 云播放器，生成 `match_stream_id`。
5. 主播端进入房间后拉 `match_stream_id`，推自己的 `host_stream_id`，用 ZEGO Web SDK 混流生成 `mixed_stream_id`。
6. C 端只拉 `mixed_stream_id`。

## 本次范围

本次只做契约和文档，不实现业务代码。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docs/api/openapi.yaml` | 新增后台赛事 LSJ 源绑定、后台房间 prepare-live、主播节目配置、主播混流回写契约。 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI。 |
| `docs/api/streamer-lsj-zego-cloud-player.md` | 更新前端接入说明为后台主导流程。 |
| `docs/decisions/ADR-0015-lsj-sports-live-source-backend-ingestion.md` | 同步后台发起开播准备和唯一 LSJ 源决策。 |

## 新增 Operation

| operationId | 方法与路径 | 用途 |
| --- | --- | --- |
| `adminMatchBindLSJSource` | `PUT /api/v1/admin/matches/{id}/lsj-source` | 后台给赛事绑定 LSJ 线路。 |
| `adminMatchLSJSource` | `GET /api/v1/admin/matches/{id}/lsj-source` | 后台查看赛事绑定的 LSJ 线路。 |
| `adminRoomPrepareLive` | `POST /api/v1/admin/rooms/{id}/prepare-live` | 后台发起开播准备，后端启动 ZEGO 云播放器。 |
| `adminRoomProgram` | `GET /api/v1/admin/rooms/{id}/program` | 后台查看房间节目流状态。 |
| `streamerRoomProgram` | `GET /api/v1/streamer/rooms/{room_id}/program` | 主播端获取 `match_stream_id`。 |
| `streamerRoomMixedStreamReport` | `POST /api/v1/streamer/rooms/{room_id}/mixed-stream` | 主播端回写 `mixed_stream_id`。 |

## 验证记录

| 命令 | 结果 |
| --- | --- |
| `python3 scripts/validate-openapi.py` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 下一步

1. 数据模型：赛事 LSJ 源绑定表、房间节目流 session 表。
2. 后端适配：ZEGO 云播放器 `CreatePlayer` / `DeletePlayer` / 查询状态。
3. 后台实现：绑定源、prepare-live、节目状态查看。
4. 主播端实现：program 查询、mixed-stream 回写。
5. C 端播放：`play-url` 在有 `mixed_stream_id` 时优先返回最终节目流。
