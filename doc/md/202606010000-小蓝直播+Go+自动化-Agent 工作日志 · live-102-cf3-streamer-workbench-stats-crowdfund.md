---
id: "doc-26cbd455a116"
title: "Agent 工作日志 · live-102-cf3-streamer-workbench-stats-crowdfund"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf3-streamer-workbench-stats-crowdfund-history.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-102-cf3-streamer-workbench-stats-crowdfund-history.md"
sourceSha256: "c7537a3323647c21fd273731ee8e4346cb762494dee9a186f95e4910d88b6025"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-102-cf3-streamer-workbench-stats-crowdfund

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606010000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-102-cf3-streamer-workbench-stats-crowdfund.md)

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：siggod
任务：LIVE-102 CF-3 — 主播工作台 3 接口(本场实时数据 + 本场众筹进度 + 历史场次)+ Start/StopLive 集成 stats

## 输入资料

- 前置:CF-1(DB/model/repo/DTO/schemas)+ CF-2(admin 阶段 CRUD)已合并
- 设计图:主播工作台原型左上四 KPI + 进度条三阶段
- AI 控制文件:`CLAUDE.md` §5.6 严格模式

## 本次目标

1. `LiveService.StartLive` / `StopLive` 接入 `StatsRepository`:开播插 0 值 stats 行,下播写 ended_at + duration
2. `WebhookService.onPublishStop` 兜底场景(主播没点下播,Zego 5s 检测断流)也关 stats 行
3. 主播工作台 3 个 GET 接口走 `/api/v1/streamer/me/sessions/current/*` + `/history`
4. OpenAPI v1.yaml 加 3 paths,跑 make openapi/sdk 同步,前端 docs 站 "主播端-工作台" 分组出现

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/streamer/live.go` | 加 `stats` 字段 + `SetStatsRepo` 注入器;StartLive 落 stats 零值行;StopLive 关 stats |
| `services/go-app/internal/service/streamer/webhook.go` | 加 `stats` 字段 + 注入器;断流兜底关 stats |
| `services/go-app/internal/service/streamer/workbench.go` | 新增 WorkbenchService(CurrentStats / CurrentCrowdfund / HistorySessions) |
| `services/go-app/internal/http/streamerapi/workbench.go` | 3 个 gin handler;复用 `middleware.UserIDFrom` 拿主播 ID |
| `services/go-app/internal/http/router/public.go` | DI(stats repo + workbench svc/handler)+ 3 路由挂 `streamerGrp.authed` |
| `packages/contracts/openapi/v1.yaml` | 3 paths:`streamerCurrentSessionStats/Crowdfund/HistorySessions`,tag `主播端-工作台` |
| `docs/api/openapi.yaml` | make openapi 重生产物(9148 行) |

## 核心决策

1. **不引入 session 级阶段 snapshot 表** — 推翻 CF-1 agent log 里"开播时 snapshot 阶段到 session 上下文"的方案。理由:
   - 已达成阶段在 `live_session_crowdfund_progress` 表的字段已经全字段快照(stage_name / threshold / action_text),历史不会失真
   - 未达成阶段跟当前 `crowdfund_stages` 启用配置走;运营改阶段是低频操作,且通常是新增更高阶段,不改已有阶段
   - 如未来真需要"开播后阶段彻底冻结",再加 `live_session_stage_snapshots` 表;现在不做避免过度设计
2. **stats 初始化失败不阻断开播** — `Init` 报错只打 warn,直播照常起;CF-5 接 Tip 链路时如果发现 stats 行缺失,WorkbenchService 已经走 ErrRecordNotFound 兜底返回 0 值快照
3. **WorkbenchService 不持有 *gorm.DB** — 构造函数虽然接 db 是为了 NewStatsRepo / NewStageRepo / NewProgressRepo,但 service 内只用接口;后续单测可以直接构造 mock repo 注入
4. **`findCurrentSession` 校验顺序** — 先查 streamer 名下所有房间,只 FindActive 状态是 LIVE 的房间;避免对所有房间打 N+1 query
5. **HistorySessions 复用 `AdminSessionStatsItem` DTO** — 主播看自己的历史场次和 admin 看任意主播的历史结构 100% 一致,无需独立 DTO
6. **没在 LiveService 加 stats 单测** — 现有 `live_test.go` 用 fake repos,改动量大;接 stats 是 nil-safe 的(`s.stats != nil` 兜底),不破坏旧测;CF-5 写 Tip service 时统一补集成测

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go build ./...` | ✓ 全包编译过 |
| `go test ./internal/service/streamer/...` | ✓ 1.72s,Auth/Live/Webhook 旧测全过 |
| `make openapi` | ✓ docs/api/openapi.yaml 重生 9148 行 + swagger-cli validate 通过 |
| `make sdk` | ✓ ts-sdk schema.ts 重生含 3 个新 operationId(`streamerCurrentSessionStats / Crowdfund / HistorySessions`)|

## 风险与待办

1. **stats 数据目前全是 0** — CF-5 接 Tip / Danmaku 链路后才有实际数据。本期前端可以拿到接口结构 + 0 值;打通端到端依赖 CF-5
2. **current_online 没有实时来源** — 目前 stats.current_online 永远 0;CF-5 / CF-6 需要 WS Hub 在 viewer enter/leave 时调 `StatsRepo.SetOnline`
3. **cumulative_views / unique_visitors** — 同上,等 WS Hub 触发
4. **HistorySessions 没暴露 admin 接口** — 仅主播看自己;运营要看所有主播的历史在 CF-2 的 admin 阶段管理是空的,后续 CF-7 补 admin `/admin/streamers/{id}/sessions`
5. **没做 next_stage 算法的单测** — 逻辑简单(threshold > cumulative && 未达成),但边缘 case(全达成 → null;无启用阶段 → null)等接通端到端时再补集成测

## 交接说明

下一位 Agent 或工程师需要知道:

1. **stats 注入点**:`router/public.go:206` `streamerStatsRepo := liverepo.NewStatsRepository(c.DB)`;同一实例注入 LiveService + WebhookService 两处
2. **当前 session 判定**:`WorkbenchService.findCurrentSession` 查 `rooms.ListByStreamer` + `sessions.FindActive(room.ID)`;主播同时多房间 LIVE 不会出现(业务规则),所以拿第一条 LIVE 房间的 active session 即可
3. **下播兜底**:主播主动 StopLive 关 stats + Zego webhook publish.stop 也关 stats,两条路径都覆盖
4. **数据 0 值不是 bug**:CF-3 阶段累加链路没接,看到数据全 0 属预期,等 CF-5
5. **OpenAPI tag**:本期用了新 tag `主播端-工作台`,docs 站会出新分组;CF-4 主播端发起投票路由可以归到同 tag 下
