---
id: "doc-fa8db4ceb830"
title: "Agent Log - Ordinary Live Mixed Stream Report"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-ordinary-live-mixed-stream-report.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-ordinary-live-mixed-stream-report.md"
sourceSha256: "f20344e894314e73bfe6b361eeec68b62d6d5d12720693e8a8ab48a813336644"
sourceSystem: "project-doc"
---

# Agent Log - Ordinary Live Mixed Stream Report

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-ordinary-live-mixed-stream-report.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

- Date: 2026-06-08
- Scope: LIVE-101 streamer mixed-stream compatibility
- Request: allow ordinary live rooms without `match_stream_id` to call `POST /api/v1/streamer/rooms/{room_id}/mixed-stream` so streamer frontend can use one fixed stream ID flow.

## Data Chain

`POST /api/v1/streamer/rooms/{room_id}/mixed-stream` -> `streamerapi.ProgramHandler.ReportMixedStream` -> `liveprogram.Service.ReportMixedStream` -> `ensureStreamerRoom` -> `loadActiveProgram` / `loadActiveHostStreamID` -> `room_program_sessions` for sports program sessions, `live_sessions.stream_no` for ordinary live -> `StreamerRoomProgram` response -> streamer frontend.

## Decision

Allow ordinary live reports only when `mixed_stream_id == host_stream_id == current live_sessions.stream_no`. If no `room_program_sessions` row exists, the backend validates the stable stream ID, writes audit/logs, returns a `LIVE` program DTO, and does not create or update sports program data.

## Changes

- Added ordinary live compatibility branch in `ReportMixedStream`.
- Added validation helper that rejects different mixed output IDs for ordinary live.
- Added unit coverage for stable stream validation and ordinary live response DTO.
- Updated OpenAPI and streamer integration docs.

## Frontend Impact

No field name or type changed. Frontend may now call `mixed-stream` for ordinary live too, passing both IDs as `start.stream_no`.
