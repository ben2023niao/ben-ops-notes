---
id: "doc-1faa8d3cced8"
title: "主播端 LSJ + ZEGO 云播放器接入说明"
date: "2026-06-10T00:47:20+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "监控告警", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/streamer-lsj-zego-cloud-player.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/streamer-lsj-zego-cloud-player.md"
sourceSha256: "fedf08eb008cc34d977dc8481f4f7467bc81ab5eec34fbb987750c35be39d387"
sourceSystem: "project-doc"
---

# 主播端 LSJ + ZEGO 云播放器接入说明

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/api/streamer-lsj-zego-cloud-player.md`

> 整理日期：2026-06-10 00:47｜日期依据：文件创建/修改时间

关联需求：LIVE-101
适用端：主播端 Web、C 端 Web、Go 后端

## 目标链路

```text
LSJ 比赛源
  -> Go 后端调用 LSJ play 获取 m3u8
  -> Go 后端调用 ZEGO 云播放器 CreatePlayer
  -> ZEGO 云播放器推比赛流 match_stream_id 到 ZEGO 房间

主播端 Web
  -> 拉 match_stream_id 预览比赛源
  -> 推主播摄像头/麦克风 host_stream_id(start.stream_no)
  -> 使用 ZEGO Web SDK 混流 match_stream_id + host_stream_id
  -> 输出到 mixed_stream_id(推荐复用 start.stream_no)

C 端 Web
  -> 始终只拉 start.stream_no,不因混流切换 stream_id
```

## 三条 ZEGO 流

| 流 | 生产方 | 消费方 | 用途 |
| --- | --- | --- | --- |
| `match_stream_id` | ZEGO 云播放器 | 主播端 Web | 比赛源预览、混流输入 |
| `host_stream_id` | 主播端 Web | ZEGO 混流任务 | 主播摄像头、麦克风、解说；必须等于 `start.stream_no` |
| `mixed_stream_id` | ZEGO 混流任务 | C 端 Web | 混流输出流；推荐复用 `start.stream_no` 保证 C 端不切流 |

C 端不拉 `match_stream_id`，也不拉独立的新混流 ID；整场直播播放 ID 保持 `start.stream_no`。主播端的核心动作是预览比赛源、推自己的流、发起混流并回写混流状态。

## 后台运营流程

LSJ 是当前唯一赛事源。后台不允许手填 m3u8 地址，必须保存 LSJ 线路标识：

```text
app_name
stream_name
```

流程：

1. 后台创建赛事时点击「选择 LSJ 直播」，从 LSJ 上游赛事/线路列表里选择对应比赛源；保存后后端会先创建赛事，再绑定 LSJ 源。
2. 如需调整线路，后台可在赛事列表点击「LSJ源」重新绑定：
   `PUT /api/v1/admin/matches/{id}/lsj-source`
3. 后台创建直播间时关联主播和赛事；这一步只建业务房间和推流密钥，不拉 LSJ，不创建 ZEGO 云播放器。
4. 后台进入直播间详情的「节目流」区域，点击「开播准备」：
   `POST /api/v1/admin/rooms/{id}/prepare-live`
5. 后端实时调用 LSJ `sportsLive/play`，再调用 ZEGO 云播放器 `CreatePlayer`。
6. 后端保存并返回 `match_stream_id`。

后台发起后，主播端再进入房间推自己的流。

后台页面入口：

- 赛事管理：`赛事管理 / 赛事列表 / LSJ源`
- 新建直播间：`直播管理 / 直播间管理 / 新建房间`，关联已绑定 LSJ 源的赛事
- 开播准备：`直播管理 / 直播间管理 / 监控 / 节目流`

后台状态判断：

- 赛事没有 LSJ 源时，直播间不能准备节目流。
- `prepare-live` 成功后，房间节目状态为 `MATCH_STREAM_READY`。
- 主播端 SDK 混流成功并回写后，房间节目状态为 `MIXED_STREAM_READY`。

## 主播端接入顺序

### 1. 获取房间节目配置

主播端 Web 调：

```http
GET /api/v1/streamer/rooms/{room_id}/program
```

返回：

```json
{
  "room_id": "业务直播间 ID",
  "zego_room_id": "ZEGO 房间 ID",
  "match_stream_id": "match_xxx",
  "host_stream_id": null,
  "mixed_stream_id": null,
  "status": "MATCH_STREAM_READY"
}
```

主播端不要选择 LSJ 源，不要接触 LSJ m3u8，不要用 hls.js 播 LSJ 源。

主播端使用字段：

- `zego_room_id`：ZEGO 登录/拉流/推流所在房间。
- `match_stream_id`：比赛源流，主播端拉流预览和混流输入。
- `host_stream_id`：主播自己的摄像头/麦克风流 ID；如果接口为空，前端按现有主播端命名规则生成并推流。
- `mixed_stream_id`：回写后用于确认当前房间已经有最终节目流。

### 2. 主播端拉比赛源预览

主播端 Web 使用 ZEGO Web SDK 拉：

```text
match_stream_id
```

用途：

- 确认比赛源是否正常。
- 作为后续混流输入。

### 3. 主播端推自己的流

主播端 Web 使用现有 ZEGO 推流流程推：

```text
host_stream_id
```

内容：

- 主播摄像头
- 主播麦克风
- 解说音频

### 4. 主播端发起 ZEGO 混流

主播端 Web 使用 ZEGO Web SDK 混流能力：

```text
input:
  match_stream_id
  host_stream_id

output:
  mixed_stream_id(推荐等于 start.stream_no)
```

建议布局：

- `match_stream_id`：全屏主画面。
- `host_stream_id`：右下角或右侧解说小窗。
- 音频：保留比赛音频和主播麦克风；如需压低比赛音量，由前端混流参数控制。

### 5. 主播端回写混流输出

混流成功后，主播端 Web 调：

```http
POST /api/v1/streamer/rooms/{room_id}/mixed-stream
```

入参：

```json
{
  "mixed_stream_id": "start接口返回的stream_no",
  "host_stream_id": "start接口返回的stream_no"
}
```

后端保存 `mixed_stream_id` 并标记当前节目已完成混流。为保证 C 端无缝观看，`mixed_stream_id` 推荐直接复用 `start.stream_no`，不要生成新的 `mix_xxx` 让 C 端切流。

## C 端播放

C 端整场直播只拉稳定播放 ID：

```text
start.stream_no
```

C 端不需要知道 LSJ、`player_id`、`match_stream_id`、`host_stream_id`，也不需要在混流成功后停旧流重拉新流。

实现口径：

- `GET /api/v1/live/room/{room_id}/play-url` 返回 `zego_stream_id`，普通直播和赛事混流都应保持同一个 `start.stream_no`。
- 普通直播可以调用 `mixed-stream` 统一前端流程，但必须传 `mixed_stream_id = host_stream_id = start.stream_no`；后端只做校验和审计，不写赛事节目流表。

## 接口文档深链

后台-赛事管理：

- [adminSportsLiveSearch](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminSportsLiveSearch) - `GET /api/v1/admin/sports-live`
- [adminMatchBindLSJSource](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminMatchBindLSJSource) - `PUT /api/v1/admin/matches/{id}/lsj-source`
- [adminMatchLSJSource](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminMatchLSJSource) - `GET /api/v1/admin/matches/{id}/lsj-source`

后台-直播间管理：

- [adminRoomPrepareLive](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminRoomPrepareLive) - `POST /api/v1/admin/rooms/{id}/prepare-live`
- [adminRoomProgram](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminRoomProgram) - `GET /api/v1/admin/rooms/{id}/program`

主播端-推流：

- [streamerRoomProgram](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/streamerRoomProgram) - `GET /api/v1/streamer/rooms/{room_id}/program`
- [streamerRoomMixedStreamReport](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/streamerRoomMixedStreamReport) - `POST /api/v1/streamer/rooms/{room_id}/mixed-stream`

C 端播放：

- [livePlayUrl](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/livePlayUrl) - `GET /api/v1/live/room/{room_id}/play-url`

`prepare-live` 会创建 ZEGO 云播放器并保存 `player_id`、`match_stream_id`。`DeletePlayer` 已有底层适配，用于真实联调后清理云播放器；业务自动清理 worker 后续再补。

## 前端交付清单

主播端 Web：

1. 进入后台已准备的直播间后，先调 `GET /api/v1/streamer/rooms/{room_id}/program`。
2. 使用 `zego_room_id` 登录 ZEGO 房间。
3. 拉 `match_stream_id` 作为赛事源预览。
4. 按现有 ZEGO 推流能力推主播摄像头/麦克风为 `host_stream_id`。
5. 使用 ZEGO Web SDK 发起混流，输入 `match_stream_id + host_stream_id`，输出 `mixed_stream_id`，推荐等于 `start.stream_no`。
6. 混流成功后调 `POST /api/v1/streamer/rooms/{room_id}/mixed-stream` 回写 `mixed_stream_id` 和 `host_stream_id`。

C 端 Web：

1. 进入房间后调现有播放接口 [livePlayUrl](https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/livePlayUrl)。
2. 对赛事直播，只播放后端返回的稳定 `zego_stream_id`，不要因混流切换 stream ID。
3. 不接触 LSJ m3u8，不拉 `match_stream_id`，不拉 `host_stream_id`。

## 真实联调命令

本地/服务器具备真实密钥时，可跑供应商链路测试：

```bash
cd services/go-app
RUN_REAL_LSJ_ZEGO=1 \
APP_LIVE_SOURCE_LSJ_ENABLED=true \
APP_LIVE_SOURCE_LSJ_BASE_URL=https://zhlsaj.zrr4ij4.site/lsjapi \
APP_LIVE_SOURCE_LSJ_APPID=<lsj_appid> \
APP_LIVE_SOURCE_LSJ_APPKEY=<lsj_appkey> \
APP_ZEGO_APPID=<zego_appid> \
[敏感内容已脱敏] \
go test ./pkg/zego -run TestRealLSJToZegoCloudPlayer -count=1 -v
```

如果当天 `sportsLive/search` 没有可播放比赛，可指定已知线路：

```bash
REAL_LSJ_APP_NAME=<app_name> REAL_LSJ_STREAM_NAME=<stream_name> ...
```

## 注意事项

1. LSJ `main_url` / `backup_url` 是上游敏感源，目标方案不返回前端。
2. `match_stream_id` 是比赛源在 ZEGO 房间内的流 ID，前端可以拉。
3. `mixed_stream_id` 是混流输出流 ID，推荐复用 `start.stream_no`；C 端只拉稳定 `zego_stream_id`。
4. ZEGO 云播放器需要提前开通权限；同一 AppID 默认运行中的云播放器数量有限，需按并发预估申请额度。
5. LSJ 如果只提供普通 HLS，源头延迟仍取决于 HLS 切片窗口；ZEGO 只能降低云播放器转推和房间内分发链路延迟。
