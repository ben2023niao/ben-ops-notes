---
id: "doc-0cc3175d6ca9"
title: "Agent 工作日志 · live-102-cf1-stats-crowdfund-vote-foundation"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Docker", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf1-stats-crowdfund-vote-foundation.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf1-stats-crowdfund-vote-foundation.md"
sourceSha256: "e02fc1995caf156b8b22892b9032469b43962589bf8c00fa2ec66a818400e123"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf1-stats-crowdfund-vote-foundation

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf1-stats-crowdfund-vote-foundation.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-1 — 直播工作台数据 + 众筹解锁 + 投票 三模块的 DB / model / repo / DTO / OpenAPI schemas 基础层

## 输入资料

- PRD：`docs/prd/modules/kickoff-host.md`(主播端工作台,待补 LIVE-102 章节)
- 需求 ID：LIVE-102(CF-1 ~ CF-7 共 7 个 commit)
- 设计图：用户提供的原型截图(主播工作台 / 用户众筹弹窗 / 投票创建 modal)
- 视觉要点：左上四 KPI 卡 + 进度条三阶段;C 端众筹弹窗 + 投票 modal 含「一人限一票」副标题 + 5/10/20 分钟时长
- 接口/契约：`packages/contracts/openapi/v1.yaml` 新增 components/schemas 14 个
- 团队可读文档：本日志 + 后续 `docs/contracts/crowdfund-vote.md`(CF-6)
- AI/工具控制文件：`CLAUDE.md` §5.6 严格模式
- 项目 Overlay：v0.3.6 直播能力扩展
- 其他：用户拍板 Q1=A(本场会话累计)、Q2=A(全局阶段共用)、Q3=B(ii)(VOTE_TOKEN 礼物 + 一人限一票)

## 本次目标

1. 落地 6 张新表 + 1 张表扩展 + 1 条 seed 的 DDL(migration 000027 up/down,本地真实跑通含 down/re-up)
2. 落地对应 GORM model / Repository 接口 + 实现 / DTO(admin + streamer + public 三视角)
3. 同步 OpenAPI v1.yaml schemas(14 个),跑 `make openapi` + `make sdk`,docs 站 schemas 一栏前端可立即引用

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000027_create_stats_crowdfund_vote_tables.up.sql` | 6 表 + live_tips ALTER + VOTE_TOKEN seed |
| `services/go-app/migrations/000027_create_stats_crowdfund_vote_tables.down.sql` | 逆序回退,含 seed DELETE + ALTER DROP |
| `services/go-app/internal/model/live_stats.go` | LiveSessionStats |
| `services/go-app/internal/model/crowdfund.go` | CrowdfundStage + LiveSessionCrowdfundProgress |
| `services/go-app/internal/model/live_vote.go` | LiveVote + Option + Ballot + 时长/状态常量 |
| `services/go-app/internal/model/live.go` | LiveTip 加 Source + VoteID + GiftCodeVoteToken 保留 code |
| `services/go-app/internal/repository/crowdfund/stage_repo.go` | 阶段全局 CRUD(admin 维护) |
| `services/go-app/internal/repository/live/stats.go` | 原子 UPDATE 累加(Inc Tip/Vote/Danmaku/Online) |
| `services/go-app/internal/repository/live/crowdfund_progress.go` | TryAchieve uk_session_stage 去重 |
| `services/go-app/internal/repository/live/vote.go` | 创建/查询/CastBallot 事务(uk_vote_user 一人一票) |
| `services/go-app/internal/dto/crowdfund.go` | admin/public 阶段 + 进度聚合 DTO |
| `services/go-app/internal/dto/live_stats.go` | 主播 + admin 数据总览 DTO |
| `services/go-app/internal/dto/live_vote.go` | 主播发起 + 公共详情 + admin 审计 + 投票请求/结果 DTO |
| `packages/contracts/openapi/v1.yaml` | 14 个新 schema:StreamerSessionStats / AdminSessionStats(+Detail) / AdminCrowdfundStage(+Input/Patch) / CrowdfundStagePublic / CrowdfundAchievement / CrowdfundProgressView / StreamerVoteCreateRequest / VoteOptionPublic / VoteDetailPublic / VoteCastRequest / VoteCastResult / AdminVoteSummary / AdminVoteBallot |
| `docs/api/openapi.yaml` | `make openapi` 重生产物 |
| `packages/ts-sdk/src/generated/schema.ts` | `make sdk` 重生(gitignored,本次不入库) |

## 核心决策

1. **冗余字段 `live_session_stats.total_income_diamond = tip + vote`** — 工作台读单行 P99 < 5ms;一致性靠 service 层同时 UPDATE 三个字段保证(单语句多 SET,原子)。备选纯 SUM live_tips 被否决:每次开播主页查询都打 DB,QPS 高场景压力大。
2. **`live_votes.cost_diamond` + `vote_gift_id` 快照** — 运营改 VOTE_TOKEN 价格后,**进行中**的投票仍按发起时的价继续收,避免用户中途投票被涨价坑。
3. **VOTE_TOKEN 是 `gift_catalog` 的保留礼物**(code='vote_token', id=24027000000000001) — 复用现有送礼链路(钱包扣 + live_tips 落账 + 审计 + 风控),零新链路;`live_tips.source=2 + vote_id` 区分场景。
4. **`uk_vote_user` 一人限一票硬约束** — 业务侧 INSERT 命中唯一键即视为重复,不需要分布式锁;`CastBallot` 返回 `(_, false, nil)` 让 service 层幂等返回旧票据。
5. **阶段配置快照到 progress 表全部字段** — 防止运营改阶段配置后历史失真;阶段达成靠 `uk_session_stage` 唯一约束去重,天然防双重达成。
6. **`crowdfund_progress.TryAchieve` 兜底字符串匹配 "Duplicate entry"** — `gorm.ErrDuplicatedKey` 老配置可能不触发,字符串兜底保证不漏判。

## 框架价值判断

- 复用 economy 模块(ADM-410)的 gift_catalog 加一个保留 SKU,零成本接入投票计费
- 复用 live_tips 现有钱包/审计/风控链路,投票券和打赏走同一管线
- snowflake.NextID 复用,id 生成不增加新组件
- 没有引入新依赖(无 cron / message queue / 分布式锁)

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 全部 27 个 migration 跑通(临时库 kickoff_cf1_verify);down 单步回退干净;re-up 幂等;seed VOTE_TOKEN 落库;live_tips ALTER 增列 source + vote_id + idx_source_vote 全部生效 |
| 红队质疑 | 1) `live_session_stats` 用 session_id 作 PK 不带 snowflake,跨场聚合时不能 ORDER BY 主键 — 影响小,已用 `idx_streamer_started` 兜底;2) `live_votes.cost_diamond` 是个字段冗余,运营误改 VOTE_TOKEN 价不会影响历史但会让主播工作台看到的「投票收入」推断与 live_tips SUM 不一致 — 接受,vote_income_diamond 一切以 live_session_stats 为准;3) `crowdfund_progress` 表 stage_name/action_text/threshold 三字段都快照,占空间 — 单场上限 ~10 行,可接受 |
| 合入判断 | 仅 CF-1(基础层),无对外接口暴露,无业务流影响,可入库;handler/service/WS/admin Vue 在后续 commit 增量补 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified(DDL up/down/re-up + 产物 schema 生成 + go build ./... 通过) |
| Project Decision | pending-review |
| 完成申请 | siggod 已实现 CF-1 全部代码,已在本地真实 DB 跑通 up/down/re-up 验证 DDL,已跑 make openapi + make sdk 同步契约 |
| 完成裁决 | 待 Owner 审 commit,如无意见进入 CF-2(admin crowdfund stages CRUD + service + handler + admin Vue 页面) |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...`(services/go-app) | ✓ 全部包编译通过 |
| `make openapi` | ✓ docs/api/openapi.yaml 重生 + swagger-cli validate 通过 |
| `make sdk` | ✓ packages/ts-sdk/src/generated/schema.ts 重生,含 LIVE-102 全部新类型 |
| `migrate -path services/go-app/migrations -database '...kickoff_cf1_verify...' up` | ✓ 1/u → 27/u 顺序全成功,最后一步 467ms |
| `migrate ... down 1` | ✓ 27/d 回退干净(55ms);live_session_stats / crowdfund_stages / live_votes 三表 SHOW TABLES 不返回;live_tips.source / vote_id 字段 SHOW COLUMNS 不返回;gift_catalog vote_token seed SELECT 不返回 |
| `migrate ... up`(再次) | ✓ 27/u 再跑成功(幂等);vote_token seed 重新落,live_tips.source(default=1, MUL) + vote_id(nullable) 重新加 |

## 前端页面验收

本次不涉及 `apps/admin/**` / `apps/web/**`(纯后端基础层 + 契约层);admin Vue 阶段管理页在 CF-2 落地,届时单独走 UI 验收。

## 风险与待办

1. 本地主 DB `kickoff` schema_migrations 处于 version=1 dirty=1 异常状态(历史遗留,非本次引入);CF-2 落 service/handler 之前需要清理,需用户在自己终端跑 `DROP DATABASE kickoff; CREATE DATABASE kickoff CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;` 之后再 `make migrate-up` 重建(本机 docker 卷无生产数据)
2. `kickoff_cf1_verify` 临时验证 DB 残留(无害,下次手工 DROP)
3. CF-2 起需要为 admin crowdfund stages CRUD 增加 RolePermissionSeeder 权限点(`crowdfund:read` / `crowdfund:write`),CF-2 commit 一并补
4. WS 事件(`crowdfund_progress` / `crowdfund_stage_unlocked` / `vote_started` / `vote_tick` / `vote_ended`)在 CF-5 落地,届时需补 `docs/api/websocket.html`
5. 用户「我的礼物记录」UI 显示投票券时,前端需要按 `live_tips.source=2 + vote_id` 做特殊标记(关联到具体投票活动),待 PRD 补充

## 交接说明

下一位 Agent 或工程师需要知道:

1. **不要直接改 `docs/api/openapi.yaml`** — 改 `packages/contracts/openapi/v1.yaml` 然后 `make openapi`(项目级 CLAUDE.md 红线)
2. **VOTE_TOKEN 是保留礼物** — code='vote_token',运营可在 admin gift_catalog 改价/icon/特效,但不能删 code 或改 code 字符串(业务侧硬编码 `model.GiftCodeVoteToken` 查找);CF-2 admin Vue 在删除/编辑 gift 时需加二次确认
3. **`live_session_stats` 增量累加全部用 `gorm.Expr` 原子 UPDATE** — service 层不要用先 SELECT 再 UPDATE 的 RMW 模式
4. **`CastBallot` 返回 `(ballotID, isNew bool, err)` 三元** — service 层判 `!isNew` 时直接幂等返回,不要再查一次
5. **WS 事件 prefix 无前缀**(`crowdfund_progress` / `vote_tick` 等),保持与现有 `TypeDanmaku` / `TypeTip` 一致;**阶段配置 snapshot 到 session**(开播时拍快照,本场不变)
