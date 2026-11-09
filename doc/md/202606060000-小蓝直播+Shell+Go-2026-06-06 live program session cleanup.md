---
id: "doc-8f0e672fd4ee"
title: "2026-06-06 live program session cleanup"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-live-program-session-cleanup.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-live-program-session-cleanup.md"
sourceSha256: "3941eeeb34ff837c4faf92221207ef9b38be22ea6dc1ceae7cbfb4c63efea361"
sourceSystem: "project-doc"
---

# 2026-06-06 live program session cleanup

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606060000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-2026-06-06%20live%20program%20session%20cleanup.md)

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

## Context

- Reported endpoint: `GET /api/v1/streamer/rooms/22536490118545409/program`.
- Observed response: `status=FAILED`, `zego_player_status=8`, `zego_destroy_reason=3`.
- Admin program details showed the active program still referenced a previous host stream:
  - stale host stream: `rm_R00008_1780744160`
  - current active host stream: `rm_R00008_1780751096`
- Program error also showed LSJ HLS diagnosis: `main: HTTP 404 stream not found; backup: HTTP 404 stream not found`.

## Root Cause

Streamer stop and ZEGO `publish.stop` paths ended `live_sessions` and `live_rooms`, but did not close active `room_program_sessions`. A new live session could then see the previous session's active program row and report a stale ZEGO player state.

## Change

- Added `liverepo.ActiveProgramEnder` and production implementation on `roomRepo`.
- `streamer.LiveService.StopLive` now ends active room programs after room stop.
- `streamer.WebhookService` now ends active room programs when ZEGO `publish.stop` closes a live room.
- Added regression coverage for both stop paths.

## Verification

```bash
cd services/go-app && go test ./internal/service/streamer ./internal/repository/live ./internal/worker
cd services/go-app && go test ./...
```
