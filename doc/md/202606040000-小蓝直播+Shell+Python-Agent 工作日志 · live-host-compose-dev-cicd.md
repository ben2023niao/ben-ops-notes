---
id: "doc-5e004d57b146"
title: "Agent 工作日志 · live-host-compose-dev-cicd"
date: "2026-06-04T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Docker", "Nginx", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-live-host-compose-dev-cicd.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-04-live-host-compose-dev-cicd.md"
sourceSha256: "657505443ac3b8dc6d35c413757226cea97e909ed6ddb8f9f8663cb03af388b3"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-host-compose-dev-cicd

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-host-compose-dev-cicd.md)

> 整理日期：2026-06-04 00:00｜日期依据：文件名日期

日期：2026-06-04
Agent：Codex
任务：将 `apps/live-host` 纳入 Docker Compose 与 `dev-cicd.sh` 容器化部署

## 输入资料

- PRD：不涉及产品需求变更
- 需求 ID：不涉及；本次为部署编排与脚本维护
- 接口/契约：不涉及 OpenAPI / DTO 变更
- 团队可读文档：`README.md`、`infra/deploy/README.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：`docker-compose.yml`、`dev-cicd.sh`、`apps/live-host/package.json`、`infra/docker/frontend-dev.Dockerfile`

## 本次目标

1. 在 Compose 本地 dev 栈中增加 `live-host`，监听 `3030`。
2. 按现有前端容器构建方式补齐部署镜像，包含 `web`、`admin`、`live-host` 三个前端产物。
3. 优化 `dev-cicd.sh`，部署时启动 `live-host-prod`，并由宝塔反向代理到 `3030`。
4. 补齐容器化前端 / 后端项目增删运维手册，并完成一次本地全量 Docker 启动验证。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docker-compose.yml` | 新增 `live-host` dev 服务与 `live-host-prod` deploy 服务；修正 `frontend-deps` 非交互安装、Admin Web 5174 端口、Web API base |
| `dev-cicd.sh` | 按分支构建 stg/prod 前端镜像，启动 deploy profile，加入 live-host URL、健康检查和 `.cicd.env` 私有配置读取 |
| `infra/docker/frontend-dev.Dockerfile` | 简化为本地 dev 基础镜像，依赖安装由 `frontend-deps` 完成 |
| `infra/docker/frontend-prod.Dockerfile` | 新增部署前端镜像构建，构建 web/admin/live-host 三端产物 |
| `infra/docker/frontend-prod.Dockerfile.dockerignore` | 新增前端部署镜像构建上下文规则，避免 framework/docs/secrets 进入镜像 |
| `infra/docker/static-server.mjs` | 新增 Node 静态文件服务，用于 admin/live-host，不引入 nginx |
| `Makefile` | `docker-logs` 纳入 `live-host` |
| `README.md` | 更新本地 Docker 服务清单、端口、部署模式命令、`dev-cicd.sh` 配置和本次验证记录 |
| `infra/deploy/README.md` | 同步本地 Docker 与 live-host 排障说明 |
| `docs/operations/containerized-service-runbook.md` | 新增前端 / 后端项目增删流程、示例和验证清单 |

## 核心决策

1. 不在前端镜像内加入 nginx；`admin-prod` 与 `live-host-prod` 使用 Node 静态服务监听容器端口，宝塔在外层做反向代理。
2. `web-prod` / `admin-prod` / `live-host-prod` 使用同一个 `kickoff-frontend:${BUILD_ENV}` 镜像，避免三端重复构建。
3. deploy 服务使用 `profiles: ["deploy"]`，避免默认 `docker compose up --build` 同时启动 dev server 和部署容器造成端口冲突。
4. `dev-cicd.sh` 不硬编码 Telegram token；真实 token / chat_id 由部署机本地 `.cicd.env` 注入，也不上传 `.env` 文件，避免密钥通过聊天工具泄露。
5. `frontend-deps` 使用 `CI=true pnpm install --frozen-lockfile --force`，避免 pnpm 在非交互容器中弹出重建 `node_modules` 提示后直接退出。
6. Admin Web dev 服务显式监听 `0.0.0.0:5174`，与 Compose 暴露端口一致。
7. C 端 Web dev 服务使用 `WEB_DEV_API_BASE` 指向 SSR 与浏览器都能访问的 API 域名；本地 `api` 容器仍通过 `8080` 独立验证。

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
| 部署 | 影响 Docker Compose 部署服务和 `dev-cicd.sh` |
| 回滚 | 回滚本次 compose、Dockerfile、脚本和文档修改 |
| 密钥 | Telegram token 改为 `.cicd.env` / 环境变量读取；`.env` 不再通过 Telegram 上传 |
| 备份恢复 | 不涉及 |
| 观测 | Telegram 报告增加 live-host 地址；健康检查增加 `http://<ip>:3030/` |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | live-host 已纳入 dev 和 deploy 两条容器路径 |
| 红队质疑 | 首次前端镜像构建会下载完整 pnpm 依赖；后续依赖 Docker cache |
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
| `sh -n dev-cicd.sh` | 通过 |
| `docker compose config --quiet` | 通过 |
| `docker compose --profile deploy config --services` | 通过，包含 `live-host-prod` |
| `docker compose build live-host` | 通过 |
| `docker compose --profile deploy build web-prod` | 通过，生成 `kickoff-frontend:stg` |
| `docker run --rm kickoff-frontend:stg node --check infra/docker/static-server.mjs` | 通过 |
| `docker run --rm kickoff-frontend:stg test -f apps/live-host/.output/public/index.html` | 通过 |
| `docker run --rm kickoff-frontend:stg test -f apps/admin/dist/index.html` | 通过 |
| `docker run --rm kickoff-frontend:stg test -f apps/web/.output/server/index.mjs` | 通过 |
| `docker compose up -d --build` | 通过，首次发现 `frontend-deps` 交互提示问题后已修复 |
| `docker compose up -d --force-recreate frontend-deps web live-host admin-web` | 通过，`frontend-deps` 完整安装 workspace 依赖约 3m45s |
| `docker compose up -d --force-recreate --no-deps admin-web` | 通过，Admin Web 监听 `5174` |
| `docker compose up -d --force-recreate --no-deps web` | 通过，Web 使用 `WEB_DEV_API_BASE` 后根路径正常 |
| `curl http://203.0.113.1:8080/healthz` | HTTP 200 |
| `curl http://203.0.113.1:8081/healthz` | HTTP 200 |
| `curl http://203.0.113.1:3000/` | HTTP 200 |
| `curl http://203.0.113.1:3030/` | HTTP 200 |
| `curl http://203.0.113.1:5174/` | HTTP 200 |

## 前端页面验收

本次未修改 `apps/web/**`、`apps/admin/**` 或 `apps/live-host/**` 页面代码，仅调整容器化部署；不需要截图验收。

## 风险与待办

1. `live-host` 构建仍存在 Zego SDK 大 chunk warning，可后续做懒加载拆包。
2. 部署机需要在 `/opt/xiaolan_watches_the_game_at_night/.cicd.env` 或 `CICD_ENV_FILE` 指向的私有文件中设置 `TG_BOT_TOKEN` / `TG_CHAT_ID`，未设置时脚本会跳过 Telegram 通知。
3. 根目录不再要求 `.env.stg` 或 `.env.prod`；部署机有 `.env` 时 compose 自动读取，没有 `.env` 时使用 compose 默认值和当前环境变量继续部署。
4. CI/CD 健康检查使用部署机本机 `203.0.113.1` 端口，并按 `HEALTH_RETRIES` / `HEALTH_INTERVAL` 重试等待；失败时自动输出对应 compose service 最近日志。

## 交接说明

1. 本地 live-host dev 入口：`http://203.0.113.1:3030`。
2. 部署容器服务名：`live-host-prod`，容器名：`kickoff-live-host-prod`。
3. 宝塔反向代理目标：`http://<部署机内网或本机 IP>:3030`。
4. 前端 / 后端项目后续增删流程见 `docs/operations/containerized-service-runbook.md`。
