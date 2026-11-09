---
id: "doc-93a1c43eaf4d"
title: "ADR-0016： Public API / WebSocket / Worker 进程拆分"
date: "2026-06-07T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Go", "Docker", "Kubernetes", "Nginx", "Redis"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0016-api-ws-worker-process-split.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/decisions/ADR-0016-api-ws-worker-process-split.md"
sourceSha256: "b0609f4883cfb7d8f9826d8ac2409e04de8e427122b1c1e7deb6ee23f3c0e4e5"
sourceSystem: "project-doc"
---

# ADR-0016： Public API / WebSocket / Worker 进程拆分

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BShell-ADR-0016%EF%BC%9A%20Public%20API%20-%20WebSocket%20-%20Worker%20%E8%BF%9B%E7%A8%8B%E6%8B%86%E5%88%86.md)

> 整理日期：2026-06-07 00:00｜日期依据：正文日期

| 状态 | 已采纳 |
|---|---|
| 日期 | 2026-06-07 |
| Owner | 后端 / 运维 |
| 影响范围 | `services/go-app/cmd/api`、`cmd/ws`、`cmd/worker`、`internal/http/router/public.go`、`infra/deploy`、`docker-compose.yml` |
| 相关需求 | LIVE-003、LIVE-004、LIVE-006、LIVE-012、MATCH-007、ADM-101、ADM-912 |
| 关联 ADR | [ADR-001](ADR-001-deployment-strategy.md)、[ADR-0012](ADR-0012-realtime-worker-embedded-in-go-app.md) |

## 1. 背景

ADR-0012 允许 MVP 阶段把 Public REST、WebSocket 和后台 worker 内嵌在同一个 `cmd/api` 进程里。随着目标容量提升到 5000 人同时在线，这个形态会带来三个问题：

1. WS 长连接会占用 API 进程文件描述符、goroutine 和内存，容易影响普通 HTTP P99。
2. 定时任务和延迟任务跟 API 共生命周期，发布或崩溃时会一起中断，排障边界不清楚。
3. 直播下播兜底、订单超时、竞猜过期等 worker 逻辑需要独立观测和独立重启。

本次拆分先保持一个 Go codebase，不拆数据库，不改前端 URL，不改变 OpenAPI 业务契约；只把运行时进程边界切出来。

## 2. 决定

引入四个 Go 运行时进程：

| 进程 | 命令 | 端口 | 职责 |
|---|---|---|---|
| `kickoff-api` | `services/go-app/cmd/api` | `8080` | C 端 Public REST API、支付/SRS hook |
| `kickoff-admin` | `services/go-app/cmd/admin` | `8081` | 运营后台 Admin API、后台 WS |
| `kickoff-ws` | `services/go-app/cmd/ws` | `8082` | C 端 / 主播端 `/ws/v1/*` 长连接 |
| `kickoff-worker` | `services/go-app/cmd/worker` | `8083` | 充值超时、支付对账、竞猜过期、直播心跳兜底等后台任务；仅暴露 health/metrics |

Public API router 新增三种装配模式：

- `BuildPublicAPI`：只注册 REST / hook，不注册 `/ws/v1/*`，不启动内嵌 worker。
- `BuildPublicWS`：只注册 `/ws/v1/*`，不注册 REST，不启动内嵌 worker。
- `BuildPublic`：legacy 兼容入口，保留 REST + WS + 内嵌 worker；新部署不再使用。

外部入口保持不变：

- REST：`https://api-dev.54-151-131-132.sslip.io/api/v1/...`
- WS：`wss://api-dev.54-151-131-132.sslip.io/ws/v1/...`

nginx 按路径拆分：`/ws/` 转发到 `203.0.113.1:8082`，其他 public REST 转发到 `203.0.113.1:8080`。

## 3. 取舍

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 继续单进程 | 改动最少 | 5000 在线时 WS/worker/API 互相影响，排障困难 | 否 |
| 本次采用：模块化单体多进程 | 不改业务契约，部署成本低，能独立扩容 WS 和 worker | 代码仍在同一 module；API 进程仍会初始化部分广播依赖 | 是 |
| 直接拆独立 repo / K8s 多 worker | 扩展性最好 | 当前工期过大，队列、服务发现、压测和运维配套都要同步补齐 | 后续阶段 |

## 4. 运维约束

1. `kickoff-worker` 当前按单副本运行，避免定时类任务重复执行；多副本前必须加 Redis leader lock 或把任务拆成队列消费者。
2. `kickoff-ws` 可独立提高 `LimitNOFILE` 和内存上限；5000 WS 连接单机需要内核 `ulimit`、nginx、Redis 连接数一起调。
3. API 域名 nginx 必须先匹配 `/ws/`，否则 WS 会打到 `kickoff-api` 并返回 404。
4. Worker 仅暴露本机 `8083` health/metrics，不走公网。
5. 本阶段不改变直播视频承载：视频流仍依赖 Zego/LSJ/CDN；本拆分只覆盖业务 REST、WS 和后台任务。

## 5. 后果

正面：

- API 发布和 WS 长连接隔离，后续可单独重启 / 扩容。
- Worker 不再跟 Public API 共生命周期。
- 前端 WebSocket URL 不变，前端不需要改接入地址。
- dev systemd 与本地 Docker Compose 都能跑拆分后的真实形态。

风险与后续：

- 多个 worker 副本会重复扫描任务，后续要加 leader lock 或迁移到 Redis Streams / 专用队列。
- `wsx.Hub` 目前同时承担本地连接和 Redis pub/sub 广播，API/worker 进程后续可收敛为 publisher-only，减少订阅开销。
- 需要补压测：单 `kickoff-ws` 5000 连接、100 msg/s 弹幕扇出、API P99 对比。
- 需要补观测：WS 连接数、订阅数、广播延迟、worker job 成功/失败/耗时。

## 6. 验收口径

- `make build` 产出 `api`、`admin`、`ws`、`worker` 四个二进制。
- `cmd/api` 使用 `BuildPublicAPI`，不再启动 worker。
- `cmd/ws` 使用 `BuildPublicWS`。
- `cmd/worker` 独立启动当前后台任务并暴露 `/healthz`。
- dev 部署脚本安装四个二进制、同步四个 systemd unit、重启并 health check 四个 Go 进程。
- 文档明确 nginx `/ws/` 转发规则。

---

**Reviewer**: `@kickoff/backend` + `@kickoff/devops`
