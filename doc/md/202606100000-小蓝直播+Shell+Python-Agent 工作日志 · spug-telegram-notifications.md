---
id: "doc-709b2c3b2a4f"
title: "Agent 工作日志 · spug-telegram-notifications"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "监控告警", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-telegram-notifications.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-telegram-notifications.md"
sourceSha256: "49322155084020744d95756ad918f7d0f594fd48479694f45e1afe9c13f07d97"
sourceSystem: "project-doc"
---

# Agent 工作日志 · spug-telegram-notifications

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-spug-telegram-notifications.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：Spug dev 部署脚本增加 Telegram 分阶段通知

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：OPS
- 接口/契约：不涉及 OpenAPI / DTO
- 团队可读文档：`infra/deploy/README.md`、`infra/deploy/spug-dev-task-template.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 增强 `infra/deploy/spug-dev-update.sh`，覆盖完整部署过程的 Telegram 通知。
2. 支持部署机本地 `.cicd.env` 或 Spug secret 变量注入通知密钥。
3. 避免真实 Telegram token / chat id 写入 Git。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `infra/deploy/spug-dev-update.sh` | 自动加载 `.cicd.env`，增加部署开始、Git 更新、Compose 重建、健康检查、成功和失败通知 |
| `infra/deploy/spug-dev-task-template.md` | 补充 `TG_NOTIFY_STEPS`、`CICD_ENV_FILE` 和 `.cicd.env` 示例 |
| `infra/deploy/README.md` | 补充 Telegram 通知行为与密钥注入落点 |
| `docs/agents/logs/2026-06-10-spug-telegram-notifications.md` | 本次工作日志 |

## 核心决策

1. 真实 Telegram token / chat id 只允许放在 Spug secret、服务器环境或部署机本地 `.cicd.env`。
2. 脚本发送阶段通知，但不在日志或通知中输出密钥值。
3. `TG_NOTIFY_STEPS=1` 默认开启分阶段通知；如通知过多，可在任务变量中设为 `0`，保留失败/完成通知。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | Spug 手动或定时执行时可向飞机群报告关键阶段 |
| 回滚 | 不改变回滚策略；失败通知包含当前阶段和 commit |
| 密钥 | 不新增仓库内 secret；真实值由 Spug secret 或 `.cicd.env` 注入 |
| 备份恢复 | 不涉及数据库、账本或对象存储 |
| 观测 | 通知覆盖 fetch/pull、compose down/up、各服务 health OK 和 deploy done/failed |

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

## 风险与待办

1. 需要在 dev 服务器或 Spug secret 中配置 `TG_BOT_TOKEN` / `TG_CHAT_ID`，否则脚本会静默跳过 Telegram 通知。
2. Web 构建阶段仍可能出现 Sentry sourcemap 上传证书链告警；该问题不属于本次通知脚本范围。
