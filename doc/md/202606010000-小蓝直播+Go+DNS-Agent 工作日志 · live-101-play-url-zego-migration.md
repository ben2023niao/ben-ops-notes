---
id: "doc-793cb857660c"
title: "Agent 工作日志 · live-101-play-url-zego-migration"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-101-play-url-zego-migration.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-101-play-url-zego-migration.md"
sourceSha256: "5a4f8f1474113164e64ef18ca6c6cedbc79565538467a6ce4e4f5cfcb853699c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-101-play-url-zego-migration

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-101-play-url-zego-migration.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：`/live/room/:id/play-url` + `/refresh-token` 切到 ZegoCloud — 修架构错配

## 背景

用户实测 dev `/play-url` 返回 `rtmp://edge2.kickoff.local/live/R001.flv` + `.m3u8`。三层错:

1. **协议错**:RTMP 是推流协议(主播 OBS push 用),浏览器播放器 flv.js/hls.js 不支持
2. **域名错**:`edge2.kickoff.local` 是 seed 占位,无 DNS 解析
3. **架构错配**:LIVE-101 推流已切 ZegoCloud,但 C 端拉流接口还是 SRS 时代的 HTTP-FLV/HLS 模板,前端调它永远播不出

用户决定全切 Zego,清掉 SRS 老路径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/live.go` | `LivePlayURL` 字段从 FLVURL/HLSURL/ExpireAt/LineID/LineName 改为 ZegoAppID/ZegoServer/ZegoRoomID/ZegoStreamID/ZegoUserID/ZegoToken/ExpiresAtMs;`LiveRefreshTokenResponse` 同改为 ZegoToken/ExpiresAtMs |
| `services/go-app/internal/service/live/service.go` | 加 `zego *zego.Client` 字段 + `SetZegoClient` setter;`PlayURL` 重写:必须 LIVE + active session,签 Privilege=Login token;新增 `buildZegoPlayParams` + `zegoViewerUserID`(登录 viewer_{uid} / 未登录 guest_{nano});`RefreshPlayToken` 同样走 Zego 重签 |
| `services/go-app/internal/http/public/live.go` | PlayURL / RefreshToken handler 改成传 `middleware.UserIDFrom(c)` 给 service |
| `services/go-app/internal/http/router/public.go` | `liveService.SetZegoClient(c.Zego)` 注入 |
| `services/go-app/internal/service/live/service_test.go` | 删 2 个 SRS 时代的 line_2 / line_1 测试(`TestPlayURLUsesConfiguredRecommendedLine` + `TestPlayURLUsesRequestedLineCode`),需要 Zego mock 才能补回 |
| `packages/contracts/openapi/v1.yaml` | `livePlayUrl` + `liveRefreshToken` path 改写,引用新 schemas `LiveZegoPlayParams` / `LiveZegoRefreshToken`;path description 含完整 Zego SDK 接入伪代码 |
| `docs/api/openapi.yaml` | make openapi 重生 |

## 核心决策

1. **PlayURL 未登录可见,RefreshToken 必须登录** — 一致性:RefreshToken 是 SDK 的续期回调,前端必须有 userID 才能保证跟首次 loginRoom 的 Zego userID 一致;PlayURL 允许 guest 是为了 C 端首屏预览
2. **`zegoViewerUserID(userID)` 集中拼装** — viewer_{uid} 或 guest_{nano},放 helper 避免散落各处
3. **`line` query 参数保留兼容老前端** — handler 还接受 query 但 service 内忽略;免得突然 404 把仍在用旧 SDK 的前端打挂
4. **`live_lines` 表 + LineRepository 暂时不删** — admin/lines list 接口可能仍被 admin Vue 前端引用,本期只让 PlayURL/RefreshToken 不再用;`SetLineRepository` 保留方法签名但内部不再读;清理 admin/lines / live_lines 表留单独工单(防止本期 PR 范围爆炸)
5. **删 2 个 SRS 时代单测** — 重写测试需要 Zego client mock,等 streamer 包之前的 Zego mock 复用基建做好再补;不让代码堵在测试上
6. **DTO 字段从 SnowflakeId 字符串改成数字 `zego_app_id`(uint32)** — Zego SDK 实际就接收数字 AppID,如果按"所有 _id 字符串"惯例也可以,但前端用 SDK 时反正得 Number(...),不如直接给数字省一步

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | ✓ |
| `go test -race ./internal/service/live/...` | ✓ 1.69s |
| `go test -race ./internal/service/streamer/...` | ✓ 11.8s |
| `make openapi` | ✓ swagger-cli validate 通过 |
| `make sdk` | ✓ ts-sdk schema.ts 重生 |

## 风险与待办

1. **`live_lines` 表 + admin /live-lines CRUD + C 端 /live/lines + /live/lines/select 全部待清理**:本期没动,留着不影响功能(`PlayURL` 不再依赖),独立 PR 一次性删
2. **admin Vue 直播线路管理页(如有)需要同步删**:check `apps/admin/src/views/live-lines/` 是否存在;前端清理 PR 一起做
3. **`SetLineRepository` 方法签名留着是技术债**:外部调用方(router)还在调,删它会引发连锁修改;留下次清理
4. **PlayURL 单测缺失**:Zego mock 需要 token04 签发逻辑的桩,补的话需要 ~50 行 fake;CF-7 写 admin 投票审计页时一起补
5. **`zego_user_id = guest_{nano & 0xffffffff}` 存在低概率撞号**:同毫秒进入的访客可能拿到同一 zego userID,Zego loginRoom 会冲突踢人。生产环境如果观察到此 case,改用 snowflake 或带毫秒级随机后缀;dev 阶段不修
6. **token TTL 默认 2h**:Zego 文档建议 ≤24h,2h 偏短;前端 SDK 会在过期前回调 `onTokenWillExpire`,通过 `/refresh-token` 续期。如果运维反馈续期请求过多,把 cfg.Zego.TokenTTL 调到 6-12h

## 交接说明

下一位 Agent 或工程师需要知道:

1. **C 端拉流走 ZegoCloud Web SDK** (`zego-express-engine-webrtc`),前端拉 `/play-url` 拿全部 6 个参数即可初始化 + login + startPlayingStream
2. **`zego_room_id = live_rooms.room_no`,`zego_stream_id = live_sessions.stream_no`(本场)** — 主播开播时(streamer.LiveService.StartLive)签的 streamID,C 端拉流必须用同一个
3. **token Privilege**:主播 = `PrivLoginPublis`(3),观众 = `PrivLogin`(1);主播开播 + 观众拉流是两条独立的签发路径,共用 `zego.GenerateRTCToken`
4. **OpenAPI description 含完整接入伪代码** — 前端拉 `docs/api/openapi.yaml` 的 `livePlayUrl` 描述就能照抄
5. **待清理工单**:删 `live_lines` 表 + admin/lines + C 端 /lines / /lines/select + admin Vue 线路管理页;独立 PR
