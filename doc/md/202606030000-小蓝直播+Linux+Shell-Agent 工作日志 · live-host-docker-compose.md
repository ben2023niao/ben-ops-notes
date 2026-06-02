---
id: "doc-eb963a05a476"
title: "Agent 工作日志 · live-host-docker-compose"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-live-host-docker-compose.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-live-host-docker-compose.md"
sourceSha256: "b00c57027a9e21602c726728146ef4a3ecb100c85c64283fe8040f85271fd194"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-host-docker-compose

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-live-host-docker-compose.md`

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：优化本地 `docker-compose.yml`，纳入 `apps/live-host` 主播端并支持 dev 环境 3030 编译运行

## 输入资料

- PRD：不涉及产品需求变更
- 需求 ID：不涉及；本次为本地 Docker 编排与运维文档维护
- 接口/契约：不涉及 OpenAPI / DTO 变更
- 团队可读文档：`README.md`、`infra/deploy/README.md`、`infra/deploy/live-host-onboarding.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：`apps/live-host/package.json`、`apps/live-host/nuxt.config.ts`

## 本次目标

1. 将新增 `apps/live-host` 纳入本地 Docker dev 栈，入口端口为 `3030`。
2. 补齐前端编译产物 Dockerfile，让 `live-host-built` 可构建并以静态站运行。
3. 更新本地联调文档与日志命令。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docker-compose.yml` | 新增 `live-host` / `live-host-built`，抽取前端 dev 公共配置，编译产物服务挂 `build` profile |
| `infra/docker/frontend-dev.Dockerfile` | 简化为 Node 20 + pnpm dev 基础镜像 |
| `infra/docker/frontend-build.Dockerfile` | 新增前端多阶段构建，支持 web/admin/live-host 三个 runtime target |
| `infra/docker/frontend-build.Dockerfile.dockerignore` | 新增前端构建上下文忽略规则，排除 docs、scripts、env 等非运行时内容 |
| `infra/docker/nginx-public-spa.conf` | 新增 live-host SPA 静态托管与 `/api` / `/ws` 代理 |
| `infra/docker/nginx-admin.conf` | 新增 admin SPA 静态托管与 admin API 代理 |
| `Makefile` | `docker-logs` 加入 `live-host` |
| `README.md` | 更新本地 Docker 服务清单、端口、常见问题 |
| `infra/deploy/README.md` | 同步本地 Docker 说明与 build profile 编译验证命令 |

## 核心决策

1. `live-host` dev 使用 `3030:3030`，命令显式覆盖 package 脚本里的默认 `3001`，避免与 C 端 Web SSR 运维端口冲突。
2. `live-host-built` 使用 nginx 托管 `.output/public`，符合 `ssr:false` SPA 的部署形态。
3. 编译产物服务使用 `profiles: ["build"]`，避免默认 `docker compose up --build` 同时启动 dev server 与编译产物服务造成端口冲突。
4. nginx upstream 使用 Docker DNS resolver + 变量式 `proxy_pass`，避免容器启动期因 `api` / `admin-api` 尚未解析而失败。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | 不涉及业务代码 |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响本地 Docker 编排与前端编译镜像；dev 分支现有 systemd/nginx 部署链路未改 |
| 回滚 | 回滚本次 compose、Dockerfile、nginx conf、README 修改即可 |
| 密钥 | 不新增 secret；ZEGO dev token 仅通过环境变量透传，不写入镜像文件 |
| 备份恢复 | 不涉及 |
| 观测 | `make docker-logs` 已纳入 `live-host` |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | `live-host` 已有 dev server 与 dev 编译产物入口，端口与代理路径明确 |
| 红队质疑 | 首次 build 依赖下载慢；后续走 Docker cache 可显著缩短 |
| 合入判断 | 可提交 review |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `git fetch origin` | 通过 |
| `git rev-list --left-right --count HEAD...@{upstream}` | `0 0` |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `docker compose config --quiet` | 通过 |
| `docker compose build live-host` | 通过 |
| `docker compose --profile build build live-host-built` | 通过，Nuxt build 成功；存在大 chunk warning |
| `docker run --rm xiaolan_watches_the_game_at_night-live-host-built nginx -t` | 通过 |

## 前端页面验收

本次未修改 `apps/web/**`、`apps/admin/**` 或 `apps/live-host/**` 页面代码，仅调整本地编排与镜像构建；不需要截图验收。

## 风险与待办

1. `live-host` 仍有 Zego SDK 相关大 chunk warning，可后续按页面懒加载拆包优化。
2. 首次 Docker build 会下载完整 pnpm 依赖，网络慢时耗时较长。
3. 本次只实测 `live-host-built` 目标；`web-built` / `admin-built` 使用同一 Dockerfile 目标，后续涉及发布前建议分别构建验证。

## 交接说明

1. 本地 dev 入口：`http://203.0.113.1:3030`。
2. 编译产物验证命令：`docker compose --profile build up --build live-host-built`。
3. 本地 `live-host` API 请求走同源 `/api`，容器内代理到 `http://api:8080`。
