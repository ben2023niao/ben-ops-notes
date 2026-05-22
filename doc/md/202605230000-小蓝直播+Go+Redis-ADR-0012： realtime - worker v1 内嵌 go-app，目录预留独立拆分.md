---
id: "doc-a0047aa4abd2"
title: "ADR-0012： realtime / worker v1 内嵌 go-app，目录预留独立拆分"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "监控告警", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0012-realtime-worker-embedded-in-go-app.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0012-realtime-worker-embedded-in-go-app.md"
sourceSha256: "971eb8bbfa1c9754531b667e15fc565cac1992b3a370586c8dd260dcafc44300"
sourceSystem: "project-doc"
---

# ADR-0012： realtime / worker v1 内嵌 go-app，目录预留独立拆分

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0012-realtime-worker-embedded-in-go-app.md`

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

| 状态 | 已被 [ADR-0016](ADR-0016-api-ws-worker-process-split.md) 取代 |
|---|---|
| 日期 | 2026-05-23 |
| Owner | 后端 / 运维 |
| 影响范围 | `services/realtime/`、`services/worker/`、`services/go-app/internal/http/wsapi/`、`internal/pkg/wsx/`、`framework-check` |
| 相关需求 | LIVE-003~006（WS 弹幕/进场）、LIVE-007（打赏 WS 广播）、PRED-* 开奖派彩 |
| 关联 ADR | [ADR-001](ADR-001-deployment-strategy.md) 部署策略；[ADR-0011](ADR-0011-prd-v0.3-align-prototype-v4.45.md) v0.3 对齐 |

## 1. 背景

> 2026-06-07 更新：5000 在线容量目标触发第一阶段拆分，Public API、Public WS、Worker
> 已按 [ADR-0016](ADR-0016-api-ws-worker-process-split.md) 拆为独立运行时进程。
> 本 ADR 仅保留 MVP 历史背景。

`framework.config.json` + `project.config.json` 都把 `realtime` 与 `worker` 标记为 `enabled: true`：

- **realtime** purpose：WebSocket 弹幕 / 进场广播 / 比赛事件推送 / 钱包变动推送
- **worker** purpose：竞猜开奖派彩 / 对账跑批 / 异步通知 / 风控规则评估

但实际仓库里**这两个目录不存在**，导致 `scripts/validate-project-overlay.py` 报错：

```
Project overlay validation failed: enabled service path does not exist: services/realtime
```

阻塞 `make framework-check`（17 个 validator 中的 1 个）。

与此同时，**实际代码已经在 `services/go-app` 进程内实现了 WS 能力**：

- `internal/http/wsapi/handlers.go`（152 行）：3 个 WS 路由（`/ws/v1/live/:room_id`、`/ws/v1/wallet`、`/ws/v1/match/:match_id`）
- `internal/pkg/wsx/Hub`：连接管理 + 房间广播 + 用户点对点推送
- `internal/pkg/wsx/protocol.go`：消息协议定义

worker 的部分能力（如开奖派彩）目前没实现，将通过 cron 或 cmd subcommand 临时承担。

## 2. 决定

**v1 阶段不拆独立 `realtime` / `worker` Go 服务，保持 WS 与 worker 能力内嵌在 `services/go-app` 进程内**。但保留 `services/realtime/` 与 `services/worker/` 目录占位 + README 说明，等触发条件满足时再独立拆分。

### 2.1 目录占位

```
services/
├── go-app/           # 主服务（API + Admin + 内嵌 WS + 内嵌定时任务）
├── realtime/         # v1 仅 README 占位，实际 WS 由 go-app 进程承担
│   └── README.md
└── worker/           # v1 仅 README 占位，实际异步任务由 go-app cron 承担
    └── README.md
```

### 2.2 内嵌方案下的实现位置

| 能力 | v1 位置 | v2 拆分后目标位置 |
|---|---|---|
| WS Hub + 路由 | `go-app/internal/http/wsapi/` + `internal/pkg/wsx/` | `services/realtime/internal/hub/` |
| 弹幕广播 | `go-app` Service 内直调 `wsx.Hub.BroadcastRoom` | 经 Redis pub/sub 转发到 realtime |
| 开奖派彩 | `go-app` cron / cmd subcommand | `services/worker/internal/jobs/settle/` |
| 对账跑批 | 同上 | `services/worker/internal/jobs/recon/` |
| 风控评估 | 同上 | `services/worker/internal/jobs/risk/` |

## 3. 备选方案对比

| 方案 | 优点 | 缺点 | 取舍 |
|---|---|---|---|
| **A-stub（本 ADR 采纳）** | 30 分钟解锁 framework-check；不引入跨进程通信复杂度；MVP 单机够用 | framework 声明与实现有"虚拟拆分"；新成员可能误以为 realtime 目录有真代码 | ✅ |
| A-full（独立 Go 服务） | 符合框架声明；为未来扩容预留 | 1-2 天工时；引入 Redis pub/sub 跨进程通信；调试 / 部署复杂度翻倍 | ❌ v1 不必要 |
| A-defer（改 enabled: false） | 与实际代码一致 | 与 PRD 里"实时推送"需求声明不符；未来重新启用要再改回来 | ❌ 改坏声明 |

## 4. 触发独立拆分的条件

满足**任一**条件即考虑把 `realtime` 真的拆出独立服务（写新的 ADR 评审后执行）：

1. **WS 连接数 ≥ 10,000 并发**（go-app 单进程内存或 goroutine 调度成瓶颈）
2. **WS 流量影响 API 响应**（弹幕高峰挤占 HTTP handler goroutine，P99 延迟显著上升）
3. **需要独立扩容 WS 节点**（API 流量 vs WS 流量比例失衡）
4. **多 region / 多机房同步**需求出现（必须用 Redis pub/sub 或类似机制做跨节点广播）

worker 拆分的触发条件类似：

1. **批量任务跑批时间 > 30 分钟**（cron 卡住 go-app 进程）
2. **派彩任务并发处理能力不足**（高峰期开奖大量赛事并行需要专用 worker pool）

## 5. 后果

### 5.1 正面后果

- `make framework-check` 17/17 全绿
- 部署架构保持 2 台 EC2 简单切（ADR-0001），无新组件
- 单进程内调用 `wsx.Hub` 零网络开销，比跨进程低延迟
- 调试 / 日志聚合 / 配置管理 全部单一来源

### 5.2 负面后果与缓解

| 风险 | 缓解 |
|---|---|
| 新成员看 framework.config 误以为 realtime 已是独立服务 | 历史 README 占位文档曾明确写"v1 内嵌 go-app"；当前状态以 ADR-0016 为准 |
| WS 流量挤占 API goroutine | 监控 P99；触发条件 1/2 出现时按 §4 流程拆分 |
| 未来真拆分时改动面大 | 当前 `wsx.Hub` 接口已是包级抽象，拆分时主要工作是把 `BroadcastRoom` 改成发 Redis pub/sub |

## 6. 验收口径

- [x] `services/realtime/README.md` 创建，写明 v1 内嵌 + 拆分触发条件
- [x] `services/worker/README.md` 创建，写明 v1 内嵌 + 拆分触发条件
- [x] `make framework-check` 17/17 全绿
- [ ] 监控告警：WS 并发数 / WS goroutine 数 / API P99 接入 Grafana 看板（v1.1 完成）

---

**Reviewer**: `@kickoff/backend` + `@kickoff/devops`
