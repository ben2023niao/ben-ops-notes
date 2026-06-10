---
id: "doc-8295035f7243"
title: "Agent 工作日志 · main-image-only-deploy"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Docker", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-image-only-deploy.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-image-only-deploy.md"
sourceSha256: "d26320b8977831bdd3b9bc915aa9ce6d3dc31b833c2970bf8840b1f22bd07376"
sourceSystem: "project-doc"
---

# Agent 工作日志 · main-image-only-deploy

> 来源文件：`~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-image-only-deploy.md`

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：main 生产发布改为 image-only，避免生产机 git pull 全仓库

## 输入资料

- PRD：不涉及业务需求
- 需求 ID：OPS-DEPLOY
- 团队可读文档：`AGENTS.md`、`infra/deploy/main-business-code-update.md`、`infra/deploy/spug-main-task-template.md`、`docs/qa/project-acceptance.md`
- 其他：GitLab main pipeline、Spug schedule task、生产 Docker Compose 发布流程

## 本次目标

1. 保持 dev 发布链路不变。
2. main 发布继续由 GitLab 构建 backend/frontend 镜像。
3. Spug 生产任务不再依赖生产机 `git pull` 全仓库，改为按 `IMAGE_TAG` 拉取 CI 镜像。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.gitlab-ci.yml` | `deploy-production-spug` 在执行任务前写入 image-only Spug 命令，传递 `CI_COMMIT_SHORT_SHA` |
| `infra/deploy/spug-main-update.sh` | 新增 `DEPLOY_SOURCE=image` 模式，跳过 Git 工作区检查、fetch、pull |
| `infra/deploy/main-business-code-update.md` | 更新 main 发布 runbook |
| `infra/deploy/spug-main-task-template.md` | 更新 Spug 任务模板 |
| `infra/deploy/README.md` | 更新 main 发布描述和变量说明 |

## 核心决策

1. 生产镜像构建继续在 GitLab `build-backend-image` / `build-frontend-image` 中完成。
2. `deploy-production-spug` 默认更新 Spug 任务命令，并将本次 `CI_COMMIT_SHORT_SHA` 作为 `IMAGE_TAG`。
3. `DEPLOY_SOURCE=git` 保留兼容，正式发布默认使用 `DEPLOY_SOURCE=image`。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | OPS-DEPLOY |
| 不涉及契约的原因 | 仅调整 CI/CD 与生产发布脚本，不改变 API、DTO、OpenAPI 或前端消费字段 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | main 生产发布改为按镜像 tag 拉取 CI 产物；dev 发布不变 |
| 回滚 | 使用旧 `IMAGE_TAG` 重新执行 image-only 发布 |
| 密钥 | 不新增密钥；继续使用 `SPUG_*` 与 `.cicd.env` |
| 观测 | 保留原 health check 与 Telegram 通知逻辑 |
| Runbook | 已更新 `infra/deploy/main-business-code-update.md` |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 生产机不再需要 checkout 开发文档、源码和 Agent 日志，降低运行时污染 |
| 红队质疑 | 首次迁移期间如果生产机仍依赖旧脚本，GitLab job 会从 `origin/main` 抽取部署脚本到 `/tmp`，不 checkout 工作区 |
| 合入判断 | 可合入 dev 验证；main 发布需人工点击 manual job |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `sh -n infra/deploy/spug-main-update.sh` | 通过 |
| `.gitlab-ci.yml` YAML 解析 | 通过 |
| `deploy-production-spug` 嵌入 Python compile | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `npm run check:ops` | 通过 |
| `npm run check` | 通过 |

## 前端页面验收

不涉及 `apps/admin/**`、`apps/web/**`、`apps/mobile/**` 页面实现变更。

## 风险与待办

1. 生产机后续应迁移到干净 runtime 目录，只保留 compose、部署脚本和 `.cicd.env`。
2. dev 发布链路仍是 artifact/systemd，后续可单独改造。
3. 局部发布服务清单可通过 `SPUG_PROD_COMPOSE_SERVICES` 控制，默认仍可由各机器 `.cicd.env` 决定。

## 交接说明

1. 该改动在 `dev` 分支完成，不直接修改 `main`。
2. 合并到 main 后，GitLab `deploy-production-spug` 会更新 Spug task command 再执行。
3. Spug 发布账号需要 `schedule.schedule.view` 与 `schedule.schedule.edit`。
