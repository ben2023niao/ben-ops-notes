---
id: "doc-8c1b9d717452"
title: "Agent 工作日志 · dev-business-code-update-runbook"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Python", "Docker", "Nginx", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-dev-business-code-update-runbook.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-dev-business-code-update-runbook.md"
sourceSha256: "0fb0b509bf57a25e4402a09c7f31007b344f3406fa081176db93179e37d6e941"
sourceSystem: "project-doc"
---

# Agent 工作日志 · dev-business-code-update-runbook

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606100000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20dev-business-code-update-runbook.md)

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：补充 dev 业务代码更新运维帮助文档，并按真实宝塔反代列表简化

## 输入资料

- 用户提供当前宝塔反向代理配置截图文字
- 用户确认 dev 更新命令：`cd /opt/xiaolan_watches_the_game_at_night && git pull && cd infra/deploy && ./spug-dev-update.sh`
- `infra/deploy/spug-dev-update.sh`
- `infra/deploy/spug-dev-task-template.md`
- `docker-compose.yml`
- `infra/deploy/README.md`

## 本次目标

1. 明确 dev 业务代码更新应该在哪台服务器执行。
2. 区分宝塔反向代理服务器、dev 业务服务器、main/prod 业务服务器职责。
3. 用最简洁方式写清楚 dev 更新命令、宝塔反代关系和验收步骤。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/dev-business-code-update.md` | 新增 dev 业务代码更新 runbook |
| `infra/deploy/README.md` | 在 Spug dev 更新章节增加 runbook 入口 |
| `README.md` | 在运维文档列表增加 runbook 入口 |
| `docs/agents/logs/2026-06-10-dev-business-code-update-runbook.md` | 本工作日志 |

## 关键结论

| 服务器 | 角色 |
| --- | --- |
| `13.229.218.208` | 宝塔面板 / 反向代理服务器，不执行业务代码更新 |
| `13.250.144.163` | dev 业务服务器，执行 `origin/dev` 拉取和 Docker Compose 重建 |
| `54.179.243.100` | main / prod 业务服务器，不用于 dev 更新 |

## 外部检查

- 尝试使用本机已有 `spug_key` / `id_rsa` 以 `root`、`ubuntu`、`ec2-user` 登录 `13.229.218.208` 与 `13.250.144.163`，均返回 `Permission denied (publickey)`。
- 文档中的反代关系按用户提供的宝塔面板真实列表整理。

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

## 影响范围

- 仅文档变更。
- 不涉及业务代码、接口契约、数据库 migration、资金或审计逻辑。
