---
id: "doc-4d2f5472c919"
title: "Agent 工作日志 · live-102-cf5-tip-cascade-ws-vote-cron"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf5-tip-cascade-ws-vote-cron.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf5-tip-cascade-ws-vote-cron.md"
sourceSha256: "f85e5354ec47f02ed8bdeabea473c462e40ab4cdfc24971f81f4d91cead0acbf"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf5-tip-cascade-ws-vote-cron

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf5-tip-cascade-ws-vote-cron.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-5 — Tip/Danmaku 级联到 stats + 阶段达成 + WS 5 事件广播 + 投票到期 cron

## 输入资料

- 前置:CF-1/2/3/3.5/4 已合并到 dev,投票模型已清理为免费 + 一人限一票
- 用户偏好:文档清晰、前端能照着接 — WS 事件文档放 docs/api/websocket.html
- CF-1 决议:WS 事件命名对齐现有 `live.tip.combo / live.danmaku.received`(无前缀我之前说错,实际是 `live.*` 域)

## 本次目标

打通端到端数据链路 + 实时推送:
1. **Tip 链路级联**:`Service.Tip` 异步累加 `stats.tip_income/total_income` → 重读累计 → 对启用阶段批量判断达成 → 广播 `crowdfund_stage_unlocked` + `crowdfund_progress`
2. **Danmaku 计数**:`SendDanmaku` 异步 `stats.IncDanmakuCount`,主播工作台弹幕数 KPI 不再 0
3. **投票 WS 广播**:`streamer.VoteService.Create` → `vote_started`;`live.VoteService.Cast` → `vote_tick`(重读最新票数推送)
4. **投票到期 cron**:`worker.StartVoteExpiryWorker` 每 5s 扫 `idx_status_ends`,关单 + 算 winner + 广播 `vote_ended`
5. **WS 协议文档**:`docs/api/websocket.html` 加 LIVE-102 五事件表

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/pkg/wsx/protocol.go` | 加 5 个 MessageType 常量(`live.crowdfund.progress` / `live.crowdfund.stage_unlocked` / `live.vote.started` / `live.vote.tick` / `live.vote.ended`)+ 6 个 payload struct(CrowdfundProgress/StageUnlocked + VoteStarted/Tick/Ended + StageBriefWS + OptionBriefWS) |
| `services/go-app/internal/service/live/service.go` | 加 `stats/stages/progress/votes` 字段 + `SetLiveStatsRepos` 注入器;Tip 流程异步 `tipCrowdfundCascade`;SendDanmaku 异步 `stats.IncDanmakuCount` |
| `services/go-app/internal/service/streamer/vote.go` | 加 `ws Broadcaster` 字段 + `SetWSBroadcaster`;Create 后广播 `vote_started`(含 0 票数 options) |
| `services/go-app/internal/service/live/vote.go` | 加 `ws` + `SetWSBroadcaster`;Cast 成功后 `broadcastTick` 重读 vote+options 推 `vote_tick` |
| `services/go-app/internal/worker/vote_expiry.go` | 新增,5s 扫描 `ListExpiredOngoing`,选 votes_count 最高为 winner,平票/0 票 winner=nil;广播 `vote_ended` 含最终快照 |
| `services/go-app/internal/http/router/public.go` | DI 接 `liveService.SetLiveStatsRepos` + `voteSvc/streamerVoteSvc.SetWSBroadcaster`;`worker.StartVoteExpiryWorker(context.Background, db, wsHub, logger)` |
| `docs/api/websocket.html` | 直播间频道下新增 LIVE-102 5 事件表,含字段 + 前端行为指引 |

## 核心决策

1. **WS 命名对齐 `live.*` 域,不是无前缀** — CF-1 我说"无前缀",但实际项目惯例是 `live.tip.combo / live.danmaku.received` 这种 `live.*` 域 + 点分,所以 CF-5 改为 `live.crowdfund.progress / live.vote.started` 等
2. **Tip 级联走 goroutine 异步** — 主事务(ledger.Post + tips.Create)已 commit 返回 200,级联失败只 warn,不影响主流程;5s 超时上下文兜底
3. **Stats 累加用 GORM Expr 原子 UPDATE** — `IncTipIncome` 一句 SQL 同步更新 `tip_income_diamond` 和 `total_income_diamond`,无 RMW 竞争
4. **阶段达成判定循环里读 cumulative 一次** — 不在循环里反复查 stats;`achievedIDs` set 拿一次;`progress.TryAchieve` 用 uk_session_stage 唯一约束兜底,理论上多 goroutine 并发也只一条
5. **vote_tick 没做节流** — 本期每次 cast 都广播;CF-6 接入压测后如发现高并发场景下 WS 推送压力大,再加 1Hz 节流(在 hub 层 batch)
6. **cron 5s 扫描而非每分钟** — 投票到期对前端体验敏感(差几秒就感觉延迟),5s 间隔在 idx_status_ends 索引下 IO 几乎为 0;批 100 条防极端场景
7. **winner 算法:简单多数 + 平票 nil** — 不区分"无人投票"和"平票",一律 winner_option_id=null;前端按 null 显示「无获胜者」即可
8. **MarkEnded 用乐观锁(status=ONGOING)** — cron 多实例 / 同实例重叠扫描时,只有一条更新成功;其他 0 affected 自动跳过
9. **worker 跑在 BuildPublic 内而不是 main** — wsHub 在 BuildPublic 创建,worker 需要它;改 main 签名涉及面太广,直接在 router 装配位置启动 worker(context.Background,跟进程同生命周期)
10. **没改 admin/streamer/zego webhook 链路** — 那些路径不送礼/不发弹幕/不投票,无级联点

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | go build 全过;`go test -race ./service/streamer/... ./service/live/...` 全过(streamer 10.6s + live 1.6s);worker 包暂无单测 |
| 红队质疑 | 1) Tip 级联 goroutine 用 context.Background,如果 db pool 满 5s 后超时,statRow 拿不到 → 阶段不达成,但主 Tip 已成功 — 接受,下次 Tip 会再 try;2) vote_tick 同一秒高频 cast 会发多次,如 1000 用户同秒投同一选项 → 1000 个 WS 帧 — CF-6 压测验证,需要再加节流;3) cron 5s + MarkEnded 乐观锁,极端情况下第一次扫到的 vote 在 MarkEnded 前被并发关掉 → 第二次跳过,没问题 |
| 合入判断 | 入库;数据链路打通,前端拉 WS + REST 立刻有真实数据 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | ✓ |
| `go test -race ./internal/service/streamer/...` | ✓ 10.59s |
| `go test -race ./internal/service/live/...` | ✓ 1.61s |
| `go test -race ./internal/worker/...` | ✓(暂无测试) |

## 风险与待办

1. **没单测 worker.scanOnce / closeOne**:逻辑简单但 winner/tie/0-vote 三分支应该补 table-driven 测试;CF-6 / CF-7 补
2. **vote_tick 高 QPS 节流**:本期没做;实际线上压测看是否需要 1Hz batch(在 wsx.Hub 内或 service 层都可)
3. **stats.unique_visitors / cumulative_views / current_online / peak_concurrent** 仍 0:这些需要 WS Hub 在 Subscribe/Unsubscribe 时调 `SetOnline / IncCumulativeViews / IncUniqueVisitors`;本期仅打通"打赏/弹幕"两条,viewer 计数留给单独工单
4. **`live.vote.tick` 节流后行为变化**:前端文档已经写「不要假设 increment=1」,等节流落地后行为一致,无需再改前端
5. **没接 admin 投票审计页**:CF-7 才补 `/admin/votes` 列表 + 详情

## 交接说明

下一位 Agent 或工程师需要知道:

1. **WS 事件命名约定**:`live.<domain>.<action>`(snake_case 点分)。CF-5 5 事件按此命名;CF-1 我说"无前缀"是错的,以现在 protocol.go 常量为准
2. **stats 累加原子性**:`IncTipIncome / IncVoteIncome / IncDanmakuCount` 都是 GORM Expr 原子 UPDATE,无需调用方加锁
3. **`tipCrowdfundCascade` 是 fire-and-forget goroutine**:错误只打 warn,主调方收到 200 后业务已完成
4. **vote 到期 cron 在 BuildPublic 起**:换部署架构(分离 worker 进程)时,把 `StartVoteExpiryWorker` 挪到独立 cmd 即可,不需改 worker 包内部
5. **前端 WS 接入文档**:`docs/api/websocket.html` 已加 LIVE-102 5 事件,字段 + 前端行为都写了,前端拉 docs 站就能照接
