---
id: "doc-6a3ea49dcf6f"
title: "Agent 工作日志 · live-102-cf4-vote-streamer-create-public-cast"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf4-vote-streamer-create-public-cast.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf4-vote-streamer-create-public-cast.md"
sourceSha256: "bf705e18cb8e61279f35104c2dcc7b75dd63aed8d4fce20f2962813d141cc176"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf4-vote-streamer-create-public-cast

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf4-vote-streamer-create-public-cast.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-4 — 主播端发起投票 + C 端查看 / 投票 三接口(免费 / 一人限一票)

## 输入资料

- 前置:CF-1 / CF-2 / CF-3 / CF-3.5(投票模型清理)已合并到 dev
- 用户拍板:投票免费,不消耗钻石/礼物,一人限一票
- 用户强调:文档注释要清晰易懂,前端按 docs 站就能接

## 本次目标

3 个接口落地 + 在 OpenAPI paths 写详细注释(业务规则 + 前端接入要点 + 错误码),前端拉 docs 站就能接 UI:

| Method | Path | 鉴权 | 说明 |
| --- | --- | --- | --- |
| POST | `/api/v1/streamer/votes` | streamerBearer | 主播在工作台发起投票 |
| GET | `/api/v1/live/room/{room_id}/votes/active` | 未登录可见 | C 端查当前房间 ongoing 投票 + 已投选项 |
| POST | `/api/v1/live/room/{room_id}/votes/{vote_id}/cast` | bearerAuth(C 端) | 投票(一人限一票,幂等) |

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/streamer/vote.go` | 新增 VoteService.Create(校验时长 + active session + 同房间无并发活动 + 事务建 vote + options) |
| `services/go-app/internal/service/streamer/workbench.go` | 把 findCurrentSession 抽到包级 helper `findStreamerActiveSession` 共用 |
| `services/go-app/internal/http/streamerapi/vote.go` | 新增 VoteHandler.Create |
| `services/go-app/internal/service/live/vote.go` | 新增 VoteService.GetActive / Cast,含选项归属校验 + 幂等返回旧票据 |
| `services/go-app/internal/http/public/vote.go` | 新增 VoteHandler.GetActive / Cast,room_id + vote_id 路径参数校验 |
| `services/go-app/internal/http/router/public.go` | DI 接 2 个 svc/handler;主播 `POST /streamer/votes`;C 端 `live.GET /room/:room_id/votes/active` + `live.POST /room/:room_id/votes/:vote_id/cast` |
| `packages/contracts/openapi/v1.yaml` | 3 paths 带详细 description(### 业务规则 + ### 前端接入要点 + 错误码) |
| `docs/api/openapi.yaml` | make openapi 重生产物 |

## 核心决策

1. **主播端路径用 `/streamer/votes`(不带 room_id)** — 主播登录后只可能一个房间在 LIVE,后端从 active session 推断 room_id,前端少传一个参数
2. **C 端路径对齐项目惯例 `/live/room/:room_id/...`**(单数 room + `room_id` 参数名) — CF-1 OpenAPI 我曾写成 `/live/rooms/{id}/`,本次纠正
3. **GetActive 未登录可见** — 跟现有 `/live/room/:room_id` 详情/弹幕历史一致,C 端首屏渲染投票卡不需要先登录;`my_vote_option_id` 在未登录时为 null
4. **Cast 必须登录** — 一人限一票必须挂用户身份;走标准 `requireUserAuth` 中间件
5. **重复 cast 幂等返回**(`is_new=false` + 旧 ballot_id + 旧 option_id)而不是报错 — 前端反复点不需要做防抖,UI 显示「您已投过 XX」即可
6. **option 归属校验在 service 层做**(`optionBelongsToVote`) — 防止用户伪造 option_id 投到其他 vote;repo 层不做校验保持简单
7. **voteToDetailPublic 在 streamer 和 live 两包各写一份** — 跨包共用要么抽 dto 要么提包级 helper,本期为避免引入新 helper 包,接受 ~30 行重复;两份字段一致,后续 schema 改动需同步
8. **没有"取消"接口** — 跟 CF-3.5 原型一致,主播只有"开始活动",到期自然结束(CF-5 cron 关单)

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | ✓ |
| `go test -race ./internal/service/streamer/...` | ✓ 10.6s,Auth/Live/Vote/Webhook/Workbench 全过 |
| `go test -race ./internal/service/live/...` | ✓ 1.7s |
| `make openapi` | ✓ swagger-cli validate 通过 |
| `make sdk` | ✓ ts-sdk schema.ts 重生,3 个新 operationId(streamerVoteCreate / liveRoomActiveVote / liveRoomVoteCast)|

## 文档注释覆盖度

每条 path 的 description 都包含:
- **业务规则**(状态机 / 唯一性 / 时长限制 / 鉴权)
- **前端接入要点**(什么时候调 / 怎么处理返回 / 错误码做什么)
- **WS 事件提示**(GetActive 注释里说"靠 vote_started/tick/ended 增量更新,不要轮询")

## 风险与待办

1. **没有 WS 广播** — `vote_started`(创建)/ `vote_tick`(每次 cast) / `vote_ended`(到期)三个事件在 CF-5 落地;CF-4 前端临时方案:Cast 成功后自己本地累加票数,GetActive 拉一次就够(不要轮询消耗)
2. **没有自动到期机制** — `vote.status` 在 ends_at 后不会自动变,CF-5 引入定时扫描 `idx_status_ends` 关单;在那之前如果用户在 ends_at 之后 cast,会返回成功(因 status 仍 ONGOING)— 接受,影响小,CF-5 修
3. **没有 admin 后台 vote 管理页** — CF-7 才补 `/admin/votes` 列表(审计用);CF-4 阶段 admin 无法看历史投票
4. **`findMyOption` 用 ListBallots+1000 上限自己过滤** — 数据量小可接受,等量大再加 `FindBallotByUserAndVote` repo 方法
5. **测试覆盖**:vote 模块 happy/重复投/选项不属于 vote 等路径**没单测**;CF-5 引入 cron 时统一补集成测

## 交接说明

下一位 Agent 或工程师需要知道:

1. **同房间唯一 active vote** 是业务侧约束(service 层 Pre-check),不是 DB 唯一约束;并发创建有理论上的窗口,但概率极小(主播单端发起),CF-5 加 Redis SETNX 兜底如有必要
2. **CastBallot 三步事务** 已经在 CF-1 voteRepo 实现:插 ballot + 选项 votes_count + vote total_votes;一致性已经保证
3. **WS 事件命名**(下次 CF-5)按 CF-1 决议无前缀:`vote_started` / `vote_tick` / `vote_ended` / `crowdfund_progress` / `crowdfund_stage_unlocked`
4. **docs 站接入指南**:前端拉 `admin-dev.54-151-131-132.sslip.io/docs`,
   - 「主播端-工作台」分组下 `streamerVoteCreate` 是发起投票
   - 「C 端-直播间」分组下 `liveRoomActiveVote` / `liveRoomVoteCast` 是 C 端两接口
   description 里有完整业务规则 + 前端接入要点,直接照着接即可
