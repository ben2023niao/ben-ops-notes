---
id: "doc-90345e3c5478"
title: "Agent 工作日志 · service-process-split"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Go", "Docker", "Kubernetes", "Nginx", "Redis"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-process-split.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-process-split.md"
sourceSha256: "41c3d19f1e431840433c279f0db88c3c47381977f0931ddd9aca8407e557cdbf"
sourceSystem: "project-doc"
---

# Agent 工作日志 · service-process-split

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BShell-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20service-process-split.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：5000 在线容量目标下，先拆分 Public API / Public WS / Worker 运行时进程

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-match-detail.md`
- 需求 ID：LIVE-003、LIVE-004、LIVE-006、LIVE-012、MATCH-007、ADM-101、ADM-912
- 接口/契约：`docs/api/openapi.yaml`、`docs/api/conventions.md`、`docs/api/websocket-current.md`
- 团队可读文档：`docs/architecture/capacity-and-performance.md`、`docs/architecture/deployment-and-monitoring.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. Public API 不再承载 `/ws/v1/*` 长连接，不再启动后台 worker。
2. 新增独立 `cmd/ws` 承载 C 端 / 主播端 WebSocket。
3. 新增独立 `cmd/worker` 承载充值超时、对账、竞猜过期、直播心跳兜底等后台任务。
4. dev systemd、Docker Compose、部署脚本、API 文档和运维文档同步新的进程边界。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/cmd/api/main.go` | Public API 改为 `BuildPublicAPI`，移除内嵌 worker 启动 |
| `services/go-app/cmd/ws/main.go` | 新增 Public WS 独立入口，默认 `:8082` |
| `services/go-app/cmd/worker/main.go` | 新增 Worker 独立入口，默认 `:8083`，暴露 health/metrics |
| `services/go-app/internal/http/router/public.go` | Public router 增加 API/WS/legacy 三种装配模式 |
| `services/go-app/internal/http/router/public_options_test.go` | 覆盖拆分选项和 WS 路由表 |
| `services/go-app/internal/config/*`、`services/go-app/config/*` | 增加 `server.ws` / `server.worker` 配置和 env override |
| `services/go-app/Makefile`、`docker-compose.yml` | 构建和本地联调纳入 `ws` / `worker` |
| `infra/deploy/*` | 部署脚本、systemd unit、runner bootstrap 和 README 纳入四进程 |
| `docs/decisions/ADR-0016-api-ws-worker-process-split.md` | 新增架构决策 |
| `services/realtime/README.md`、`services/worker/README.md` | 从“占位内嵌”更新为当前运行方式 |
| `docs/api/*` | 明确 WS URL 不变，但 nginx `/ws/` 转发到 `kickoff-ws:8082` |

## 核心决策

1. 采用模块化单体多进程，不直接拆独立 repo / K8s 多服务，避免一次性引入过多运维复杂度。
2. 外部 REST 和 WS URL 不变；nginx 负责 `/ws/` 路由拆分，前端无需改接入地址。
3. Worker 当前按单副本运行；多副本前必须补 leader lock 或迁移到 Redis Streams / 专用队列。

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 高并发、异步、可观测性、部署、回滚 |
| 当前 MVP 边界 | 单机 systemd 四进程；Worker 单副本 |
| 未来迁移成本 | 需要 publisher-only WS broadcaster、worker leader lock、压测和 K8s HPA |
| 高风险触发项 | 生产发布、直播可用性 |
| 能力门禁结论 | 允许作为第一阶段合入，不能声明完成完整 5000 在线生产容量 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | `make build` 产出 `api/admin/ws/worker`；deploy 安装四个二进制和四个 unit |
| 回滚 | 回滚 commit 后 deploy 会恢复旧 `api/admin` 二进制；nginx `/ws/` 转发需同步回退或保留 legacy `BuildPublic` 部署 |
| 密钥 | 不新增 secret |
| 备份恢复 | 不涉及数据库结构 |
| 观测 | Worker 暴露 `/internal/metrics`；WS 仍复用现有 Prometheus middleware |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/http/router` | 通过 |
| `go test ./cmd/api ./cmd/ws ./cmd/worker ./internal/http/router` | 通过 |
| `make build` | 通过，产出 `api/admin/ws/worker` |
| `git diff --check` | 通过 |
| `go test ./...` | 通过 |
| `./devtools/framework check` | 通过 |

## 风险与待办

1. `kickoff-worker` 多副本会重复扫描任务；扩容前必须补 Redis leader lock 或队列化。
2. API/worker 当前仍会初始化 `wsx.Hub` 用于广播，后续应抽 `Broadcaster` publisher-only 以减少不必要订阅。
3. 需要真实压测：单 `kickoff-ws` 5000 连接、100 msg/s 弹幕扇出、API P99 对比。

## 交接说明

1. dev nginx 必须把 `/ws/` 转发到 `203.0.113.1:8082`，REST 仍转发到 `203.0.113.1:8080`。
2. 前端 WebSocket 地址不变：`wss://api-dev.54-151-131-132.sslip.io/ws/v1/...`。
3. 这次是第一阶段进程拆分，不是完整的生产容量建设终点。
