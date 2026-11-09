---
id: "doc-f6bd75d2dd05"
title: "Agent 工作日志 · main-multibrand-handoff-docs"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Nginx", "监控告警", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-multibrand-handoff-docs.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-multibrand-handoff-docs.md"
sourceSha256: "20d46071a3234648c1f838df45e06badeb35e405d4801a6b9855264c141ee298"
sourceSystem: "project-doc"
---

# Agent 工作日志 · main-multibrand-handoff-docs

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BNginx-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20main-multibrand-handoff-docs.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：main 多品牌域名前后端改造交接文档

## 输入资料

- PRD：不涉及业务 PRD
- 需求 ID：OPS
- 接口/契约：不涉及 OpenAPI / DTO / Event 契约
- 团队可读文档：`infra/deploy/main-business-code-update.md`、`infra/deploy/README.md`、`infra/deploy/spug-main-task-template.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：main 多品牌域名设计、宝塔反向代理现状、已提交的 `e41c2e9 fix(deploy): 兼容 main 多品牌域名 CORS [OPS]`

## 本次目标

1. 将 main 多品牌 CDN 域名兼容改造内容整理为前端团队可执行文档。
2. 将后端 CORS、Compose、Spug 和 `.cicd.env` 改造内容整理为后端团队可执行文档。
3. 明确真实密钥不进入 Git，文档只保留占位符和运行时注入方式。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/main-multibrand-frontend-prompt.md` | 新增前端改造提示词，覆盖域名矩阵、已改文件、前端 API base、同品牌 API 推导和验证清单。 |
| `infra/deploy/main-multibrand-backend-prompt.md` | 新增后端改造提示词，覆盖 CORS Origin 原则、已改文件、env 覆盖、Compose/Spug 透传和验证清单。 |
| `docs/agents/logs/2026-06-11-main-multibrand-handoff-docs.md` | 本工作日志。 |

## 核心决策

1. 前端和后端拆成两份独立文档，便于分别交给对应团队执行。
2. 文档保留 main 当前真实服务器和域名矩阵，但不写真实密码、token、证书私钥等 secret。
3. CORS 口径明确为页面 Origin，不把 API 目标域名误当成默认 Origin。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | OPS |
| 需求总账 | 不涉及业务需求总账 |
| 模块 PRD | 不涉及 |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 仅新增运维交接文档，不改变接口、DTO 或事件契约。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不直接触发部署；文档用于指导后续前端/后端继续兼容多品牌 CDN 域名。 |
| 回滚 | 删除新增文档即可，不影响运行时。 |
| 密钥 | 不写真实 secret；`.cicd.env`、JWT、DB、Telegram 等仅保留占位符。 |
| 观测 | 不涉及日志、指标或告警改造。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `git fetch origin` | 通过 |
| `git status --short` | 仅存在未跟踪本地 `apps/live-host/.env*`，本次未触碰。 |
| `git rev-list --left-right --count HEAD...@{upstream}` | `0 0` |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `python3 scripts/validate-agent-log-boundaries.py` | 通过 |
| `npm run check:ops` | 通过 |
| `git diff --check` | 通过 |
| Telegram token 形态扫描 | 未在新增文档中命中真实 token。 |

## 风险与待办

1. 这些文档是交接提示词，不代表前端应用代码已完成动态同品牌 API 推导。
2. `sssqho.cn` / `voemor.cn` 子域名仍依赖 DNS、腾讯 CDN、宝塔 `server_name` 和 SSL 配置完整。
3. 后续如新增品牌域名，需要同步更新前端推导规则、后端 `APP_SERVER_CORS_ALLOW_ORIGINS` 和运维文档。

## 交接说明

1. 前端交接文档：`infra/deploy/main-multibrand-frontend-prompt.md`。
2. 后端交接文档：`infra/deploy/main-multibrand-backend-prompt.md`。
3. main 运行时 CORS 变量：`APP_SERVER_CORS_ALLOW_ORIGINS`。
