---
id: "doc-98476d6e1237"
title: "Agent 工作日志：主播端开播/下播 + Zego webhook D2"
date: "2026-05-31T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-live-d2.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-live-d2.md"
sourceSha256: "d7bfda793d5db6e4b04e6e31ab63ae9a8751d7159727ff2db2ad68884aa7cb5c"
sourceSystem: "project-doc"
---

# Agent 工作日志：主播端开播/下播 + Zego webhook D2

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-streamer-live-d2.md`

> 整理日期：2026-05-31 00:00｜日期依据：文件名日期

日期:2026-05-31
Agent:siggod / go-app
任务:实现主播端房间列表/改资料/开播/下播/刷新 Zego token + ZegoCloud 服务端事件回调

## 输入资料

- PRD:`docs/prd/modules/kickoff-auth.md` §主播端、`docs/prd/modules/kickoff-admin.md` §直播运营
- 需求 ID:LIVE-101 D2(三端联调主流程 D 阶段第 2 步)
- 接口/契约:`packages/contracts/openapi/v1.yaml`
  - `/api/v1/streamer/me/rooms`(GET)
  - `/api/v1/streamer/rooms/{room_id}`(PATCH)
  - `/api/v1/streamer/rooms/{room_id}/start`(POST)
  - `/api/v1/streamer/rooms/{room_id}/stop`(POST)
  - `/api/v1/streamer/rooms/{room_id}/refresh-zego-token`(POST)
  - `/api/v1/zego/webhook`(POST)
- 上游 commit:`133f6da feat(streamer): 主播端鉴权 5 接口 + 独立 JWT subject [LIVE-101 D1]`

## 本次目标

1. 主播端房间 CRUD-light(看/改) + 开播/下播 + Zego token 刷新
2. 接 ZegoCloud webhook,publish.stop 兜底关流(主播没点下播直接断流场景)
3. ZegoConfig 落 yaml + env,Container 持 *zego.Client(占位时 nil)
4. service 层单测覆盖 happy/状态拦截/越权/Zego 未配置/签名错误/时间戳过旧

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `internal/config/config.go` | 新增 ZegoConfig(AppID/ServerSecret/CallbackSecret/Server/TokenTTL) |
| `internal/config/loader.go` | bindEnv zego.app_id/server_secret/callback_secret/server/token_ttl |
| `internal/infra/infra.go` | Container.Zego;buildZego 配置不全时 logger.Warn 后返 nil |
| `config/config.example.yaml` `config.dev.yaml` `config.local.yaml` | 加 zego: 区块,server_secret 走 env |
| `internal/model/live.go` | LiveRoom 加 Tags(JSON),LiveSession 加 StreamNo(对接 B 段 migration) |
| `internal/repository/live/live.go` | 加 ListByStreamer / UpdateProfile(streamer_id 二次校验防越权) |
| `internal/service/streamer/live.go` | NEW:ListMyRooms/UpdateRoom/StartLive/StopLive/RefreshZegoToken,乐观锁切状态 + session + Zego token |
| `internal/service/streamer/webhook.go` | NEW:WebhookService HandleWebhookBody;publish.start 仅审计,publish.stop 兜底 LIVE→ENDED |
| `internal/service/streamer/live_test.go` | NEW:12 个单测覆盖 5 个 API 全部分支 |
| `internal/service/streamer/webhook_test.go` | NEW:7 个单测覆盖 publish.start/stop/坏签名/过旧时间戳/zego nil |
| `internal/http/streamerapi/live.go` | NEW:5 个 handler |
| `internal/http/streamerapi/webhook.go` | NEW:zego webhook handler,401/200 分流 |
| `internal/http/router/public.go` | 装配 streamerLiveSvc + zegoWebhookSvc,注册 6 个路由 |
| `internal/dto/streamer.go` | 加 StreamerRoomItem/UpdateRoomRequest/StartLiveResponse/RefreshZegoTokenResponse |
| `internal/service/home/service_test.go` `internal/service/schedule/service_test.go` `internal/service/live/service_test.go` | fakeRoomRepo 补 ListByStreamer/UpdateProfile stub(接口扩张连带) |

## 核心决策

1. **开播失败回滚**:Zego token 签发失败时回滚房间状态 + MarkEnded session,保证不出现"房间 LIVE 但没 session / 没有 token"的悬挂状态
2. **publish.stop 用 room_no 反查**:StartLive 里 zegoRoomID = row.RoomNo,webhook payload.room_id 即对应回 room_no,无需新增 zego↔room 映射表
3. **webhook 业务异常返 200**:仅签名/时间戳错误返 401(让 ZegoCloud console 日志可追),业务异常(房间不存在、DB 抖动)返 200 + log,避免 Zego 重试雪崩
4. **dev/local Zego 占位**:AppID==0 || ServerSecret 长度!=32 → Container.Zego = nil,service 层降级到 ErrFeatureClosed,不阻塞其他模块开发
5. **Tags JSON 字符串**:LiveRoom.Tags 用 string(GORM 视作 raw),业务层 json.Marshal/Unmarshal;避免引 datatypes.JSON 依赖
6. **stream_no 命名**:`rm_<room_no>_<unix_sec>` 简单可追,无需外接序列号生成器

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器,还是项目资产 | 项目资产 + zego 适配模式可外推 |
| 哪些内容可复用到下一个项目 | Container.Zego nil 降级模式、webhook 签名/时间戳防重放检查 |
| 哪些内容只属于当前项目 | live_rooms 状态机/room_no 命名/stream_no 生成规则 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 是,可外推到 push notification / SMS / KYC 等任意需要 webhook 验签的第三方对接 |
| 是否涉及 Scale Profile:mvp / growth / scale / enterprise | mvp |
| 是否影响项目 Overlay:project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 单测 +19 个 case |
| 是否降低了 Agent 偷懒空间 | 否 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 D2 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-auth.md` §主播端 + kickoff-admin.md §运营违规告警 |
| OpenAPI / Event / DTO | `packages/contracts/openapi/v1.yaml` `/api/v1/streamer/me/rooms` 等 6 个 |
| 验收证据行 | 待 D smoke 阶段补 |
| 不涉及契约的原因 | 涉及,A 段已加 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | B 段已加 `live_rooms.tags` + `live_sessions.stream_no` + uk_stream_no |
| 是否使用表设计模板 | 是 |
| 是否影响账本、事务、幂等或审计 | 影响审计:audit.Log 4 处(room.update/live.start/live.stop + zego.publish.start/stop) |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 权限安全 + 异步(webhook 兜底) + 数据一致性(开播失败回滚) |
| 高风险触发项 | 直播状态 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 cmd/api binary,新增 6 个路由,需重启 |
| 回滚 | git revert + 不存在依赖的 schema 变化(B 段独立 commit,本期未改 schema) |
| 密钥 | 新增 APP_ZEGO_APP_ID / APP_ZEGO_SERVER_SECRET / APP_ZEGO_CALLBACK_SECRET(prod 必填) |
| 备份恢复 | 不影响 |
| 观测 | audit_logs 多 4 类 action;Zego nil 时启动 log.Warn |
| Runbook | 待 D smoke 阶段补 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | webhook 签名 + 时间戳防重放;UpdateProfile streamer_id 二次校验防越权;开播失败完整回滚 |
| 红队质疑 | webhook 业务异常返 200 隐藏故障,需运维监控 audit_logs.action="zego.publish.stop" 是否长期未到达;主播 SDK 上报 room_id 与 room_no 字面相等是约定,若 SDK 端拼错则 webhook 找不到 room → 由 zego.publish.stop find room failed warn 兜底告警 |
| 合入判断 | 合入(单测 19 个 case 已覆盖以上风险路径) |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented(代码 + 单测过,smoke 在 D 末尾) |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | 通过 |
| `go vet ./...` | 通过 |
| `go test -race -count=1 ./internal/service/streamer/...` | ok 20s,本期 +19 个 case 全过 |
| `go test -count=1 ./internal/service/home/... ./internal/service/schedule/... ./internal/service/live/...` | 全过(stub 兼容验证) |

## 风险与待办

1. webhook 业务异常返 200 需 monitor 兜底,Runbook 在 D smoke 阶段补
2. ZegoCloud REST KickUser 已在 pkg/zego/rest.go 写好,但本期未接 admin 用(留 D3/v1.x)
3. publish.start 仅审计,未做"必须先有 streamer.live.start 才允许 publish.start"的对账;v1.x 上线观察期再加

## 交接说明

下一位 Agent / 工程师需要知道:

1. ZegoCloud Console 配置回调 URL:`https://api-dev.../api/v1/zego/webhook`,签名 敏感凭据：[已脱敏] fallback 到 APP_ZEGO_SERVER_SECRET)
2. 前端 SDK 拿到 StartLiveResponse 后,用 `zego_app_id` + `zego_server` 初始化 ZegoExpressEngine,用 `zego_token` 走 loginRoom(zego_room_id, {userID: zego_user_id, ...}),再 startPublishingStream(stream_no)
3. token 2h 过期前,SDK onTokenWillExpire → 前端调 `/refresh-zego-token` 拿新 token,SDK renewToken 即可,不用重连
4. D3 待做:弹幕敏感词缓存 + admin 创建主播返 init_password
