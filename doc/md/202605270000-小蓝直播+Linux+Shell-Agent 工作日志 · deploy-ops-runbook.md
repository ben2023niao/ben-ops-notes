---
id: "doc-e503060413b8"
title: "Agent 工作日志 · deploy-ops-runbook"
date: "2026-05-27T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "Python", "Go", "Docker", "Nginx", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-deploy-ops-runbook.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-deploy-ops-runbook.md"
sourceSha256: "db8ac085935efa5ec93f61690bef2a56000e78666a5d0e5ff1117f2d1675f2ca"
sourceSystem: "project-doc"
---

# Agent 工作日志 · deploy-ops-runbook

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605270000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BShell-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20deploy-ops-runbook.md)

> 整理日期：2026-05-27 00:00｜日期依据：文件名日期

日期：2026-05-27
Agent：Codex
任务：补全本地一键运行与 dev 部署运维文档

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：不涉及
- 接口/契约：未修改
- 团队可读文档：`infra/deploy/README.md`、`infra/deploy/runner-bootstrap.md`、`infra/deploy/deploy.sh`、`infra/deploy/systemd/`
- AI/工具控制文件：`AGENTS.md`
- 其他：`.gitlab-ci.yml`、`docker-compose.yml`、`Makefile`

## 本次目标

1. 把项目如何本地一键 Docker 跑起来写成可交接文档。
2. 把 dev 环境 CI 自动部署、手工部署、回滚、排障写清楚。
3. 同步修正部署接入文档中过期的 Go 版本说明。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/README.md` | 重写为完整运维与部署手册 |
| `infra/deploy/runner-bootstrap.md` | 将 build runner Go 版本更新为 1.25，并说明部署机启用 Nuxt SSR 时需要 Node 20 运行时 |
| `docs/agents/logs/2026-05-27-deploy-ops-runbook.md` | 本次工作日志 |

## 核心决策

1. 继续把 `infra/deploy/README.md` 作为运维入口，避免新增分散文档。
2. 明确本地 Docker 编排只用于 local/dev，不等同生产运行时镜像。
3. 部署文档以当前 ADR-0013 双 runner 快速验证阶段为准，生产期镜像方案仅作为未来目标说明。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目运维资产 |
| 哪些内容可复用到下一个项目 | 一键 Docker、本地/CI/手工部署/回滚/排障文档结构 |
| 哪些内容只属于当前项目 | IP、域名、service 名、端口、systemd unit、GitLab runner tag |
| 是否可规模化 | 可作为多服务运维入口模板 |
| 是否涉及 Scale Profile | mvp |
| 是否影响项目 Overlay | 不影响 |
| 是否增加自动校验或 CI 门禁 | 未增加 |
| 是否降低 Agent 偷懒空间 | 是，明确部署步骤、验收和排障证据 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | 不涉及业务 PRD |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | 不涉及 |
| OpenAPI / Event / DTO | 未修改 |
| 验收证据行 | 本日志验证记录 |
| 不涉及契约的原因 | 仅文档变更 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 规范例外与原因 | 宿主机缺 Node 导致 runtime validator 失败，已记录 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 文档化本地 Docker、CI 自动部署、手工部署、systemd、nginx、回滚 |
| 回滚 | 文档化 7 天 artifact retry 与超过 7 天重跑 build |
| 密钥 | 文档化 `/etc/kickoff/*.env`，未新增 secret |
| 备份恢复 | 引用既有备份恢复文档 |
| 观测 | 文档化 journald、docker compose logs、nginx 检查 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 文档覆盖新同学本地接入、CI 发布、手工发布、回滚、排障 |
| 红队质疑 | 当前仍是 dev 快速验证，不应用作生产镜像方案 |
| 合入判断 | 可进入 review |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 失败：宿主机缺 `node` |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `python3 scripts/validate-ops-readiness.py` | 通过 |

## 风险与待办

1. `runner-bootstrap.md` 只同步修正了 Go 版本和 Node 运行时说明，后续如实际服务器 OS 版本变化需再校准命令。
2. 当前文档描述的是 dev 快速验证阶段，不覆盖生产镜像仓库和多机部署实操。
3. 宿主机缺 Node 的 runtime validator 仍未通过。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 运维入口文档是 `infra/deploy/README.md`。
2. 两机首次接入仍看 `infra/deploy/runner-bootstrap.md`。
3. C 端 Nuxt SSR 生产式接入仍看 `infra/deploy/web-onboarding.md`。
