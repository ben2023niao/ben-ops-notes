---
id: "doc-dc91147bfe9a"
title: "Agent 工作日志 · live-102-cf3-5-vote-free-revert"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "MySQL", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf3-5-vote-free-revert.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf3-5-vote-free-revert.md"
sourceSha256: "4addd8485d92b13dc3632b69a94e4d7addde0348a319c69a1858c0911bb8bfe2"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf3-5-vote-free-revert

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf3-5-vote-free-revert.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-3.5 修订 — 投票回归免费(一人限一票),清理 B(ii) "投票券" 过度设计

## 输入资料

- 前置 commit:CF-1(a0d3e99) / CF-2(7f93f83) / CF-3(1d7f7cb) 已合并
- 用户拍板:
  - Q1=A:主播工作台「投票收入」KPI 删除,缩成三栏(累计观看 / 在线 / 累计收入)
  - Q2=B:`live_session_stats.vote_income_diamond` 字段保留备用(未来若做单选项加注扩展可激活,8 字节代价小)
  - Q3=A(我推荐替代 Q3=B):forward-only migration 000028,**不动** a0d3e99 commit,避免 force push 影响同事

## 本次目标

撤销 B(ii) "VOTE_TOKEN 礼物 + 投票券扣钻" 过度设计,投票回归"免费 + 一人限一票"。
原型 modal 副标题已明确写「观众参与投票,一人限一票」— 钻石/礼物概念是我之前过度引申。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000028_drop_vote_payment_fields.up.sql` | ALTER 3 表 DROP 6 字段/2 索引 + DELETE VOTE_TOKEN seed |
| `services/go-app/migrations/000028_drop_vote_payment_fields.down.sql` | 反向 ADD + INSERT(仅紧急回退用) |
| `services/go-app/internal/model/live.go` | LiveTip 删 Source/VoteID + 删常量 LiveTipSourceTip/Vote/GiftCodeVoteToken |
| `services/go-app/internal/model/live_vote.go` | LiveVote 删 CostDiamond/VoteGiftID;LiveVoteBallot 删 DiamondPaid/TipID |
| `services/go-app/internal/dto/live_vote.go` | VoteDetailPublic 删 cost_diamond/vote_gift_id/vote_gift_code;VoteCastResult 删 diamond_consumed;AdminVoteSummary 删 cost_diamond;AdminVoteBallot 删 diamond_paid/tip_id |
| `services/go-app/internal/dto/live_stats.go` | StreamerSessionStats / AdminSessionStatsItem 删 vote_income_diamond |
| `services/go-app/internal/service/streamer/workbench.go` | CurrentStats / HistorySessions 不再返 vote_income_diamond |
| `packages/contracts/openapi/v1.yaml` | StreamerSessionStats / AdminSessionStats / VoteDetailPublic / VoteCastResult / AdminVoteSummary / AdminVoteBallot 同步减字段 |
| `docs/api/openapi.yaml` | `make openapi` 重生产物 |

## 核心决策

1. **forward-only 000028 而非 force push 000027** — Q3 用户初选 B(force push),我推荐改 A 因为 a0d3e99 已 push,force push 会让所有同事 `git pull` 失败;000028 减字段在新部署等价干净,只是 `schema_migrations` 历史多一行 27/28,无业务影响。**用户接受 A**
2. **保留 `live_session_stats.vote_income_diamond` 字段(Q2=B)** — 单字段 8 字节,未来若做"对某选项加注送礼"扩展可直接复用,不破坏 stats schema;repo 已经有 `IncVoteIncome` 方法保留但当前无人调
3. **删主播工作台「投票收入」KPI(Q1=A)** — 原型四栏改三栏,DTO / OpenAPI 直接删字段;前端按新 schema 接 UI
4. **`live_vote_ballots` 移除 tip_id / uk_tip 唯一约束** — 票据不再关联送礼;`uk_vote_user` 一人限一票约束保留
5. **`voteRepo.CastBallot` 事务保留** — 票据 INSERT + option votes_count UPDATE + vote total_votes UPDATE 仍需事务保证一致性,只是不再有"扣钻"链路;实现里没引用过 b.TipID/DiamondPaid 字段,无需改 repo 代码

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | migration 28 up→down→re-up 三循环全跑通;关键字段 `cost_diamond` / `tip_id` / `source` / VOTE_TOKEN seed 全部 SHOW/SELECT 不返回;`vote_income_diamond` 字段保留 ✓ |
| 红队质疑 | 1) `vote_income_diamond` 永远 0 — 接受,字段成本极小,扩展时不用改 schema;2) `voteRepo.CastBallot` 还在用事务但只剩 3 个 UPDATE 一个 INSERT — 接受,事务保证 ballot 落库 + 计数累加原子,本来就该如此 |
| 合入判断 | go build + go test -race 全过(streamer service 12.4s);migration 三循环干净;可入库 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified |
| Project Decision | pending-review |
| 完成裁决 | 待 Owner 审 commit 后进入 CF-4(主播端发起投票 + C 端投票 — 这次全部走免费 + 一人限一票路径,不再走 Tip 链路) |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | ✓ |
| `go test -race ./...`(services/go-app) | ✓ streamer service 12.4s,其余包正常 |
| `make openapi` | ✓ swagger-cli validate 通过 |
| `make sdk` | ✓ ts-sdk schema.ts 重生,旧字段在 generated types 里消失 |
| migration 28 up | ✓ 74ms |
| migration 28 down | ✓ 59ms(回到 27 状态,字段重新出现) |
| migration 28 re-up | ✓ 66ms 幂等 |
| DB 抽检 | ✓ `cost_diamond` / `tip_id` / `source` 三字段 SHOW COLUMNS 空;VOTE_TOKEN seed SELECT 空;`vote_income_diamond` 保留 |

## 风险与待办

1. **CF-4 开干前** 需要先在主库 `kickoff` 上同步跑 28 — 但你之前已经在自己终端跑过 `make migrate-up`(应该到 27);CF-4 启动前再跑一次自动到 28
2. **dev 服务器** 部署时跑 27 → 28 等价于「跑 27 不带这些字段」,但 binlog 里会保留两次 ALTER 的痕迹;生产环境如果未来上线时还在这个状态,直接合并 27/28 成一条 migration 更干净(production-only 优化,本期不做)
3. **前端 admin 阶段管理页**(CF-2 那个 crowdfund-stages.vue)不受影响 — 它只引用 AdminCrowdfundStage 系列 schema
4. **前端如有 mock 用过 cost_diamond / vote_gift_code 等字段**,需要同步删除 mock(CF-4 接 paths 时一并验证)

## 交接说明

下一位 Agent 或工程师需要知道:

1. **投票模型最终态**:`LiveVote(无 cost_diamond / vote_gift_id)` + `LiveVoteOption(纯文字)` + `LiveVoteBallot(VoteID/OptionID/UserID/CreatedAt 4 列)` — 极简
2. **`vote_income_diamond` 留作扩展点**:未来要做"对某选项加注送礼"时,在 Tip service 中复用 `StatsRepo.IncVoteIncome` 累加;现在无人调
3. **CF-4 范围**:主播端 `POST /streamer/live/votes`(发起)、C 端 `GET /live/rooms/{id}/votes/active`(查活动)、C 端 `POST /live/rooms/{id}/votes/{vote_id}/cast`(免费投一票,body 只有 `option_id`)
4. **CastBallot 重复投票语义**:用户已投过任一选项,再调 cast 返回 `is_new=false` + 旧 ballot,**不允许改投**(uk_vote_user 唯一约束硬保证)
