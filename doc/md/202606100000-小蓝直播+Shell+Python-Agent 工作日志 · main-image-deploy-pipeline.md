---
id: "doc-8a022e988646"
title: "Agent 工作日志 · main-image-deploy-pipeline"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Docker", "MySQL", "Redis", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-main-image-deploy-pipeline.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-main-image-deploy-pipeline.md"
sourceSha256: "3c46334fcf2c062ea6db13cc0a14d59ce6e2b11f844f0492f19f1dd832b2b662"
sourceSystem: "project-doc"
---

# Agent 工作日志 · main-image-deploy-pipeline

> 来源文件：`~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-main-image-deploy-pipeline.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：main 正式服发布链路改为 CI 构建镜像 + Spug 拉镜像发布

## 输入资料

- PRD：不涉及业务需求变更；构建产物边界参考 `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-h5.md`、`docs/prd/modules/kickoff-live.md`
- 需求 ID：OPS-DEPLOY；受影响前端产物关联 `ADM-001` / `H5-001` / `LIVE-001`
- 接口/契约：不涉及 OpenAPI / DTO 字段变更
- 团队可读文档：`infra/deploy/README.md`、`infra/deploy/main-business-code-update.md`、`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户要求“dev 合并到 main 就能发布到正式，专业主流，不能以 MVP 算”

## 本次目标

1. main pipeline 在合并后构建后端和前端生产镜像并推送 Registry。
2. Spug 正式服任务只拉 main、拉镜像、启动容器，不在正式机编译 Go / Node 源码。
3. 文档同步给运维可配置的 Spug 变量和回滚/排查口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.gitlab-ci.yml` | 增加 build/deploy 阶段，main 构建 `kickoff-backend` / `kickoff-frontend` 镜像；正式发布保留人工触发闸门 |
| `infra/docker/backend-prod.Dockerfile` | 新增后端多阶段生产镜像，runtime 仅包含二进制、配置模板、migration SQL、迁移脚本和 mysql client |
| `infra/docker/backend-prod.Dockerfile.dockerignore` | 限制后端构建上下文，避免 framework/docs/apps 等进入镜像上下文 |
| `infra/docker/frontend-prod.Dockerfile` | main 前端镜像 build 阶段显式注入正式 API 域名、Sentry release 和可选 sourcemap token |
| `infra/deploy/docker-compose.main.yml` | 新增正式服专用 compose，引用 CI 镜像并连接云 MySQL / Redis |
| `infra/deploy/spug-main-update.sh` | 支持 `DEPLOY_MODE=pull`、Registry 登录、默认用 main 短 SHA 作为 `IMAGE_TAG` |
| `infra/deploy/README.md` | 更新正式发布链路说明 |
| `infra/deploy/main-business-code-update.md` | 更新 main 业务发布 runbook |
| `infra/deploy/spug-main-task-template.md` | 更新 Spug 任务变量模板 |
| `docker-compose.yml` | 注释声明根 compose 不再作为正式服发布入口 |
| `services/go-app/internal/config/*` | 补齐 Redis username / TLS 配置读取，匹配正式 ElastiCache 配置 |
| `services/go-app/internal/infra/redis.go` | go-redis 初始化时按配置启用 TLS |
| `apps/web/.env.stg` / `apps/web/.env.prod` | 移除已提交的 `SENTRY_AUTH_TOKEN` 明文，真实 token 改由 CI protected variable 注入 |

## 核心决策

1. 正式服不现场 build，避免生产机依赖 Node/Go toolchain、framework 和源码。
2. main 专用 compose 独立于本地/dev compose，降低 dev 和 prod 发布路径互相污染的风险。
3. 镜像 tag 默认使用 main 当前短 SHA，确保 Git 提交、CI 产物和 Spug 发布可追踪。
4. 正式 ElastiCache 配置已在文档中要求 TLS，因此后端必须真实支持 `APP_REDIS_TLS_*`，否则发布后会连不上 Redis。
5. 前端生产域名属于 build-time bundle 配置，必须在 Docker build 阶段注入；Sentry auth token 是构建期私密变量，不得继续放在 `.env.*` 文件中。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | OPS-DEPLOY |
| 模块 PRD | 不涉及 |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 仅调整 CI/CD、镜像和运维脚本，不改变 API 返回字段或路径 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不新增 migration；仅把现有 migration SQL 打入后端 runtime 镜像供发布执行 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 当前迁移脚本仍沿用既有 `scripts/docker-migrate-seed.sh`，未在本次改造迁移框架，避免上线前扩大风险 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 main 发布方式：GitLab Registry 镜像 + Spug pull 模式 |
| 回滚 | 回滚 main commit 后重新触发 pipeline / Spug，或临时指定上一版 `IMAGE_TAG` |
| 密钥 | 新增 Registry Deploy Token 运行时变量；Sentry auth token 改为 GitLab protected/masked variable；真实值仅放 GitLab / Spug secret 或服务器 `.cicd.env` |
| 备份恢复 | 不涉及数据库备份策略 |
| 观测 | 保留原 health check 和 Telegram 部署通知 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 正式机不 build，运行镜像不包含 framework/docs/source，发布链路可回滚 |
| 红队质疑 | 迁移仍使用历史 SQL 脚本方式而非严格 migration version lock，建议后续单独做迁移治理 |
| 合入判断 | 允许合入 MR 验证 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented |
| Project Decision | pending-review |
| 项目级闭环 | `docs/qa/project-acceptance.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `sh -n infra/deploy/spug-main-update.sh` | 通过 |
| `ruby -e 'require "yaml"; YAML.load_file(".gitlab-ci.yml")'` | 通过 |
| `docker compose -f infra/deploy/docker-compose.main.yml config` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:ops` | 通过 |
| `npm run check:mr-gates` | 通过 |
| `rg -n "sntrys_[A-Za-z0-9+/_=-]{20,}"` | 通过：未发现真实 Sentry auth token 明文残留 |
| `docker build -f infra/docker/backend-prod.Dockerfile ...` | 未执行成功：本机 Docker daemon 未启动；需 GitLab Runner 构建验证 |

## 前端页面验收

UI 验收模式：`no-design-mvp`

目标 viewport / design dimensions：手机视口 `375x812`、`390x844`；桌面/PC 视口 `1440x900`。

页面截图：本次不改页面结构、样式、交互或文案，不新增 Playwright screenshot；引用既有页面截图证据
`docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-375x812.png`、
`docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-1440x900.png`、
`docs/qa/screenshots/current/admin-login-1440x900.png`。
结构化视觉证据引用 `docs/qa/ui-visual-evidence.json`。

响应式验证：不涉及响应式布局修改；构建变量只影响 production bundle 的 API base / Sentry release，不改变 375x812 手机视口、390x844 手机视口或 1440x900 桌面布局。

SEO异常验证/meta scope：不涉及 SEO异常验证、title、description 或 sitemap 规则变更；保留 `apps/web/.env.prod` 既有站点名和生产 API base 口径。

不涉及 H5/Web/Admin 页面交互改动；仅调整前端生产镜像构建期环境变量与密钥注入方式。

## 风险与待办

1. GitLab Runner 需要支持 Docker-in-Docker 或改为等价 Kaniko/BuildKit runner。
2. 正式发布必须人工执行 Spug 任务或 GitLab manual deploy job，正式服 `.cicd.env` 需要配置 Registry 只读 Deploy Token。
3. 后续应把 migration 升级为严格版本化工具并引入生产前备份/锁机制。

## 追加记录：Spug API 触发与 main 构建收口

时间：2026-06-10

### 变更补充

| 文件 | 说明 |
| --- | --- |
| `.gitlab-ci.yml` | main 自动构建生产镜像；`deploy-production-spug` 改为 `manual` 人工触发 job，登录 Spug API 后调用 `POST /api/schedule/{task_id}/`；支持 `SPUG_PROD_TASK_ID(S)` / `SPUG_PROD_TASK_NAME(S)` 多任务顺序发布；dev 的 UI artifact 构建限制在 `dev` 分支，main 只保留生产镜像构建路径 |
| `infra/docker/frontend-prod.Dockerfile` | Web / live-host 生产镜像构建改为直接执行 `nuxt build` / `nuxt generate`，不依赖未入库的 `.env.prod` 文件 |
| `infra/deploy/main-business-code-update.md` | 补充正式服 `.cicd.env` 必需的 JWT / 数据加密密钥，以及上线前不回显真实值的检查命令 |
| `infra/deploy/spug-main-task-template.md` | 同步补充 Spug / 服务器本地必需密钥和生成方式 |

### 口径确认

- `SPUG_BASE_URL` 是 Spug 面板地址，例如 `http://52.76.254.19`，不是 GitLab Registry 的 `https://203.0.113.1:5050` 或 `3-1-159-178.nip.io:5050`。
- GitLab Registry 只用于正式服拉镜像；正式服通过 `REGISTRY_URL` / `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` 登录后 `docker compose pull`。
- 多机发布不需要改 CI：可以一个 Spug 任务选多个执行对象，也可以在 GitLab manual job 中用 `SPUG_PROD_TASK_IDS` / `SPUG_PROD_TASK_NAMES` 配多个任务顺序触发；每台机器通过自己的 `.cicd.env` 决定 `COMPOSE_SERVICES`。
- 生产服务器 `.cicd.env` 必须补齐 `APP_JWT_ACCESS_SECRET`、`APP_JWT_REFRESH_SECRET`、`APP_DATA_ENC_KEY`、`APP_DATA_HMAC_KEY`；真实值只在服务器或 secret 系统保存，不进 Git / 聊天记录。

### 追加验证

| 命令/方式 | 结果 |
| --- | --- |
| `git diff --check` | 通过 |
| `ruby -e 'require "yaml"; YAML.load_file(".gitlab-ci.yml")'` | 通过 |
| `python3 -m py_compile /tmp/spug_trigger_ci.py` | 通过 |
| `docker compose -f infra/deploy/docker-compose.main.yml config`（注入占位必需变量） | 通过 |
| `npm run check` | 初次失败：实现变更未同步 Agent log；补充本追加记录后重跑 |
| `go test ./...`（`services/go-app`） | 通过 |
| `docker build -f infra/docker/backend-prod.Dockerfile ...` | 本机 Docker daemon 未启动，无法本地构建；需由 GitLab `kickoff-build` runner 验证 |

### 风险更新

1. 首次正式发布前必须在 `54.179.243.100` 的 `/opt/xiaolan_watches_the_game_at_night/.cicd.env` 补齐 JWT / 数据加密密钥，否则 compose 会在变量展开阶段 fail-fast。
2. 已避免 main 重复走 dev UI artifact 构建，正式发布以 Docker image job 为准，且发布动作需要人工确认。
