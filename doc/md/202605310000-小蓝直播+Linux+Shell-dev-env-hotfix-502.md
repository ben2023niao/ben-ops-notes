---
id: "doc-8546fc8fb2c8"
title: "dev-env-hotfix-502"
date: "2026-05-31T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Shell", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-dev-env-hotfix-502.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-dev-env-hotfix-502.md"
sourceSha256: "1d9501d916c29f42fef773c805439a17b332ef3a50aa216bf37243c0f81370a8"
sourceSystem: "project-doc"
---

# dev-env-hotfix-502

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-31-dev-env-hotfix-502.md`

> 整理日期：2026-05-31 00:00｜日期依据：文件名日期

日期：2026-05-31
Agent：Codex
任务：修复 dev API/Admin 502，兼容迁移运行时 env

## 输入资料

- 需求 ID：WALLET-002
- 接口/契约：`POST /api/v1/admin/auth/login`
- 团队可读文档：`infra/deploy/README.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 修复测试机 API/Admin 502。
2. 保持 systemd 运行时不直接读取 `/etc/kickoff/*.env`。
3. 兼容老测试机尚未手工创建 `/opt/kickoff/.env` 的状态。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/deploy.sh` | deploy 阶段如 `/opt/kickoff/.env` 缺失，则从旧 `/etc/kickoff/{common,api,admin}.env` 一次性迁移 |
| `infra/deploy/systemd/kickoff-api.service` | `EnvironmentFile=-/opt/kickoff/.env`，避免文件缺失时 systemd 直接拒启 |
| `infra/deploy/systemd/kickoff-admin.service` | 同上 |

## 核心决策

1. systemd unit 只读 `/opt/kickoff/.env`，不回退读取 `/etc/kickoff`。
2. deploy 脚本只做一次兼容迁移，迁移后运行时仍以 `/opt/kickoff/.env` 为唯一 dev secret 文件。
3. 如果新旧 env 都不存在，deploy fail-fast，并提示运维创建 `/opt/kickoff/.env`。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `curl https://admin-dev.54-151-131-132.sslip.io/api/v1/admin/auth/login` | 复现 502 |
| `curl https://api-dev.54-151-131-132.sslip.io/healthz` | 复现 502 |
| `bash -n infra/deploy/deploy.sh` | 通过 |

## 风险与待办

1. 推送后需观察 GitLab deploy-dev 是否完成，并再次 curl health/login。
2. 运维后续仍应正式维护 `/opt/kickoff/.env`，不要长期依赖兼容迁移。
