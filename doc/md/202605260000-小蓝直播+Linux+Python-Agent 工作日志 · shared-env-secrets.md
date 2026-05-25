---
id: "doc-2742c7546cec"
title: "Agent 工作日志 · shared-env-secrets"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Python", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shared-env-secrets.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shared-env-secrets.md"
sourceSha256: "515997fa60fecca0ca9f2aa136a997fe02ba8a10ebe81803ab1f76e2a5464e7f"
sourceSystem: "project-doc"
---

# Agent 工作日志 · shared-env-secrets

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-shared-env-secrets.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：梳理部署重启行为与数据加密/HMAC 共用密钥配置

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：N/A（运维配置说明）
- 团队可读文档：`infra/deploy/README.md`、`infra/deploy/runner-bootstrap.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 确认 CI/CD deploy 是否每次重启服务。
2. 确认 `.env.example` 是否说明 `APP_DATA_ENC_KEY` / `APP_DATA_HMAC_KEY`。
3. 将 API / admin 共用 secret 提取到公共 env 文件。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.env.example` | 补充数据加密与 HMAC key 的用途说明 |
| `infra/deploy/systemd/kickoff-api.service` | 新增可选 `/etc/kickoff/common.env` |
| `infra/deploy/systemd/kickoff-admin.service` | 新增可选 `/etc/kickoff/common.env` |
| `infra/deploy/deploy.sh` | 标注 deploy 成功后会重启服务，migration 失败不重启 |
| `infra/deploy/README.md` | 更新 secret 分层与 deploy 重启行为说明 |
| `infra/deploy/runner-bootstrap.md` | 引导文档改为 common/api/admin 三文件，并修正旧变量名 |

## 核心决策

1. `common.env` 放 API / admin 共用 secret，`api.env` / `admin.env` 保留服务专属配置。
2. systemd 使用 `EnvironmentFile=-/etc/kickoff/common.env`，保持向后兼容；服务器尚未创建该文件时不会启动失败。
3. 服务专属 env 放在 common env 后面，同名变量可覆盖公共值。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅更新部署文档与 systemd unit 模板；实际服务器需安装新版 unit 并 `daemon-reload` 后生效 |
| 回滚 | 删除 unit 中 `EnvironmentFile=-/etc/kickoff/common.env` 或继续保留原 `/etc/kickoff/{api,admin}.env` 即可 |
| 密钥 | 明确 `APP_DATA_ENC_KEY` / `APP_DATA_HMAC_KEY` 应放 secret 文件，不进 git |
| 观测 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | common env 使用可选 `EnvironmentFile=-`，不破坏现有服务器；服务专属 env 仍可覆盖共用值。 |
| 红队质疑 | 若服务器只创建 common env 但忘记保留空的 api/admin env，systemd 仍会因必需的服务 env 缺失失败；bootstrap 文档已保留创建空 admin.env 和 api.env。 |
| 合入判断 | 允许合入；变更范围限于部署模板和文档，不包含真实 secret。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented |
| Project Decision | pending-review |
| 项目级完成依据 | `docs/qa/project-acceptance.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
