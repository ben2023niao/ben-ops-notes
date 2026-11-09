---
id: "doc-211192cf39de"
title: "Agent 工作日志 · streamer-publish-config"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-streamer-publish-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-streamer-publish-config.md"
sourceSha256: "83b5839f899ae9318c082ca095c7c31f60604ab2f12de9db213ae1f5d200f21b"
sourceSystem: "project-doc"
---

# Agent 工作日志 · streamer-publish-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20streamer-publish-config.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：新增主播端开播前 Zego 初始化配置接口

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：STR-101
- 接口/契约：`GET /api/v1/streamer/rooms/{room_id}/publish-config`
- 验收证据：`docs/qa/acceptance-evidence.md`

## 数据链路

1. 主播进入开播间，前端已有房间 ID。
2. 前端调用 `GET /api/v1/streamer/rooms/{room_id}/publish-config`。
3. 后端 `streamerapi.LiveHandler.PublishConfig` 从登录态取主播 ID，校验 `room_id`。
4. `streamer.LiveService.PublishConfig` 读取 `live_rooms`，校验房间存在、属于当前主播、未封禁。
5. Zego 技术参数来自运行时配置 `cfg.Zego.AppID` / `cfg.Zego.Server`，Zego 房间 ID 来自 `live_rooms.room_no`，Zego 用户 ID 由 `streamer_{streamer_id}` 生成。
6. 接口返回 `zego_app_id` / `zego_server` / `zego_room_id` / `zego_user_id`。
7. 前端使用这些只读参数初始化 Zego engine、本地采集流和美颜 SDK；真正开播仍调用 `POST /api/v1/streamer/rooms/{room_id}/start`。

## 核心决策

1. 新接口只读，不创建 `live_sessions`，不改变 `live_rooms.status`，不签发 `zego_token`，不返回 `stream_no`。
2. 美颜参数由主播端前端默认值和主播本地操作控制，后端不持久化，不新增 DB 字段，不增加后台管理配置。
3. `streamer_{streamer_id}` 的 Zego userID 生成逻辑复用到 `start` 和 `refresh-zego-token`，避免开播前后 userID 不一致。
4. 封禁房间返回冲突错误；非本人房间返回无权错误。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/streamer.go` | 新增 `StreamerPublishConfigResponse` |
| `services/go-app/internal/service/streamer/live.go` | 新增 `PublishConfig` 只读服务方法 |
| `services/go-app/internal/http/streamerapi/live.go` | 新增 handler |
| `services/go-app/internal/http/router/public.go` | 挂载主播端路由 |
| `packages/contracts/openapi/v1.yaml` / `docs/api/openapi.yaml` | 更新接口契约和前端接入说明 |
| `services/go-app/internal/service/streamer/live_test.go` | 新增开播前配置行为测试 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer -run 'TestLiveService_PublishConfig' -count=1` | 先红后绿 |
| `docs/qa/acceptance-evidence.md` | 本次只新增主播端开播前配置接口，不声明项目级完成 |

## 风险与待办

1. 前端需在进入开播间后先调用 `publish-config`，再用返回的 Zego 参数执行 `publisher.preparePreview({ appID, server })` 和美颜初始化。
2. 真正开播仍必须调用 `start` 获取 `zego_token` / `stream_no`；不要用 `publish-config` 结果直接推流。
