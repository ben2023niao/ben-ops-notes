---
id: "doc-ad1cc1985095"
title: "2026-06-06 zego cloud player force rebuild"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-zego-cloud-player-force-rebuild.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-zego-cloud-player-force-rebuild.md"
sourceSha256: "760f89900a9266d17fa4e265d62219fe208bfec8a528a85296ff0c28192c6720"
sourceSystem: "project-doc"
---

# 2026-06-06 zego cloud player force rebuild

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606060000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-2026-06-06%20zego%20cloud%20player%20force%20rebuild.md)

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

## 背景

房间 R00004 在后台房间详情页执行「强制重建」时，LSJ m3u8 已可播放，但 ZEGO 创建云播放器返回：

```text
zego biz code=350006008 msg=app exists the same player, repeat create
```

## 根因

后台开播准备创建 ZEGO 云播放器时：

- `PlayerName` 固定为 `room_<roomID>_match`
- `matchStreamID` 只使用 `roomID + Unix 秒级时间`
- 强制重建成功后没有回收旧 `player_id`

当旧云播放器仍存在，或短时间重复点击强制重建时，会命中 ZEGO 的同 player 重复创建限制。

## 变更

- `matchStreamID` 改为使用 `roomID + program sessionID`，保证每次节目流准备唯一。
- `PlayerName` 改为使用 `roomID + program sessionID`，避免同房间强制重建复用固定名称。
- 强制重建落库成功后，异步最佳努力删除旧 ZEGO `player_id`；删除失败只打日志，不影响新节目流。
- 增加单测覆盖：
  - 云播放器 stream id / player name 使用 session id 唯一化。
  - 强制重建后会清理旧 player。

## 验证

```bash
cd services/go-app
go test ./internal/service/liveprogram
go test ./...
cd ../..
npm run check:openapi
npm run check:contract
python3 scripts/validate-completion-claims.py
```
