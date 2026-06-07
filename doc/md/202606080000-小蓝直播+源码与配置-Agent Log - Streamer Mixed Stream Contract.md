---
id: "doc-7841781a70cd"
title: "Agent Log - Streamer Mixed Stream Contract"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-streamer-mixed-stream-contract.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-streamer-mixed-stream-contract.md"
sourceSha256: "3a94631fb6f733daa4ced0d8e68f797fc87366a06924ab9a03285c6f9761b41a"
sourceSystem: "project-doc"
---

# Agent Log - Streamer Mixed Stream Contract

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-streamer-mixed-stream-contract.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

- Date: 2026-06-08
- Scope: LIVE-101 streamer mixed stream documentation
- Request: clarify how frontend should call `streamerRoomMixedStreamReport` when C-end playback must stay seamless.

## Data Chain

`POST /api/v1/streamer/rooms/{room_id}/start` returns `stream_no` -> streamer publishes host stream with `stream_no` -> if `GET /api/v1/streamer/rooms/{room_id}/program` has `match_stream_id`, streamer mixes `match_stream_id + stream_no` -> `POST /api/v1/streamer/rooms/{room_id}/mixed-stream` records mixed readiness -> C-end `GET /api/v1/live/room/{room_id}/play-url` returns stable `zego_stream_id`.

## Decision

For seamless C-end playback, recommend mixed output `mixed_stream_id = start.stream_no`. Normal rooms without `match_stream_id` do not call the mixed-stream report endpoint.

## Changes

- Updated `docs/api/openapi.yaml`.
- Updated `packages/contracts/openapi/v1.yaml`.
- Updated `docs/api/streamer-lsj-zego-cloud-player.md`.
- Updated `docs/api/streamer-integration.html`.

## Frontend Impact

No field name or type changed. The documentation now clarifies that `mixed_stream_id` should normally reuse `start.stream_no`.
