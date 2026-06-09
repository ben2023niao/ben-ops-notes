---
id: "doc-cc5c0762acc9"
title: "Agent 工作日志 · spug-dev-update-script"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Docker", "MySQL", "Redis", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-dev-update-script.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-dev-update-script.md"
sourceSha256: "18f50c84dcbdd66f2ab799d16b64c10583a7aefc4d462d0d88a19546590ce606"
sourceSystem: "project-doc"
---

# Agent 工作日志 · spug-dev-update-script

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-dev-update-script.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：dev 环境 Spug 代码更新脚本

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：OPS
- 接口/契约：不涉及 OpenAPI / DTO
- 团队可读文档：`infra/deploy/README.md`、`docs/operations/ops-readiness.md`、`docs/architecture/deployment-and-monitoring.md`
- 用户附件：Spug/Docker Compose 自动部署脚本草稿

## 本次目标

1. 增加 dev 环境可由 Spug 执行的代码更新和 Docker Compose 重启脚本。
2. 增加 Spug 定时任务模板，明确变量、命令、健康检查和回滚入口。
3. 避免真实 Telegram token / chat id 写入仓库。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/spug-dev-update.sh` | 新增 Spug dev 更新部署脚本，默认拉取 `dev` 分支并重建当前 compose dev/deploy/build 服务 |
| `infra/deploy/spug-dev-task-template.md` | 新增 Spug 任务模板，含默认 dev 模式、deploy profile 模式和 build profile 模式 |
| `infra/deploy/README.md` | 增加 Spug dev 代码更新任务入口 |
| `docs/agents/logs/2026-06-10-spug-dev-update-script.md` | 本次工作日志 |

## 核心决策

1. 脚本默认使用当前仓库实际服务名：`mysql redis migrate api admin-api ws worker web live-host admin-web`。
2. 编译产物模式通过 `COMPOSE_PROFILE=build` 和 `web-built/admin-built/live-host-built` 显式开启；现有 dev 服务器部署态可通过 `COMPOSE_PROFILE=deploy` 使用 `web-prod/admin-prod/live-host-prod`。
3. Telegram 通知只读 `TG_BOT_TOKEN` / `TG_CHAT_ID` 环境变量；用户附件中的真实 token 未写入仓库。
4. Git 更新使用 `git pull --ff-only`，工作区不干净时默认失败，避免定时任务覆盖部署机本地改动。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 新增 Spug 可执行脚本，支持拉取 dev 分支后重建 Docker Compose 服务 |
| 回滚 | 模板记录 `git revert <bad-sha>` 后重跑脚本；数据库 migration 不自动回滚 |
| 密钥 | 不新增仓库内 secret；通知密钥必须由 Spug secret 变量或服务器环境注入 |
| 备份恢复 | 不涉及数据库 schema 变更；如后续发布含 migration，仍按现有 migration 策略 |
| 观测 | 脚本内置 API/Admin/WS/Worker/Web/Live Host health check，失败时输出对应 compose logs |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `git fetch origin` | 通过 |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `sh -n infra/deploy/spug-dev-update.sh` | 通过 |
| `bash -n infra/deploy/spug-dev-update.sh` | 通过 |
| secret 片段扫描 | 未命中，确认附件中的真实 Telegram token 片段未进入仓库 |
| `npm run check:ops` | 通过 |
| `python3 scripts/validate-agent-log-boundaries.py` | 通过 |
| `git diff --check` | 通过 |

## 风险与待办

1. 当前工作区已 rebase 到最新 `origin/dev` 后解决部署文档和 compose 冲突。
2. 首次在 Spug 启用前，应手动执行一次模板命令确认服务器 Docker Compose 服务名与端口一致。
3. 如部署机需要强制修复文件属主，可临时设置 `FIX_OWNERSHIP=1`；默认关闭以降低定时任务破坏面。
