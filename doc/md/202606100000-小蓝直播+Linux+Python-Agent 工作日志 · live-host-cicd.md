---
id: "doc-342ca3df40d0"
title: "Agent 工作日志 · live-host-cicd"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Python", "Nginx", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-live-host-cicd.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-live-host-cicd.md"
sourceSha256: "a00ee730da702030426760b9eb2ad0fefb387b24d6b1db7c68f12717c649044c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-host-cicd

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606100000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-host-cicd.md)

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：live-host CI/CD 发布链路补齐

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：OPS
- 接口/契约：不涉及 OpenAPI / DTO
- 团队可读文档：`infra/deploy/README.md`、`infra/deploy/runner-bootstrap.md`、`infra/deploy/live-host-onboarding.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 参考 dev 分支运维发布链路，确认 `apps/live-host` 能通过 GitLab CI 构建 artifact。
2. 确认 deploy job 能消费 live-host 静态产物并同步到部署机 webroot。
3. 补齐 runner 初始化、运维手册、验收和回滚说明。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.gitignore` | 增加 `*.pem`，避免部署私钥误提交 |
| `.gitlab-ci.yml` | `live-host-ui-build` 触发条件增加 `packages/live/**`，避免共享包改动漏构建 |
| `infra/deploy/deploy.sh` | CI 默认使用 `sudo -n`，权限缺口 fail-fast |
| `infra/deploy/runner-bootstrap.md` | 补充 live-host webroot 初始化与 deploy runner sudoers 白名单 |
| `infra/deploy/README.md` | 补充 Live Host 服务清单、域名、artifact、deploy 步骤、验收与回滚 |
| `docs/agents/logs/2026-06-10-live-host-cicd.md` | 本次工作日志 |

## 核心决策

1. Live Host 是 Nuxt `ssr:false` 静态 SPA，沿用 Admin Web 的 nginx 静态托管模型，不新增 systemd 服务。
2. CI artifact 使用 `apps/live-host/.output/public/`，部署落点为 `/var/www/kickoff-live-host/`。
3. `packages/live/**` 是 live-host 的 workspace 依赖，纳入 CI changes 规则，减少漏发布风险。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | `live-host-ui-build` 产物由 `deploy.sh` 第 `[5/8]` 步同步 |
| 回滚 | 7 天内可 retry 老 pipeline 的 deploy job；超过 7 天重跑老 commit build job |
| 密钥 | 不新增 secret；真实第三方 key 仍走部署机 `/opt/kickoff/.env` 或前端环境模板 |
| 备份恢复 | 不涉及数据库、账本或对象存储 |
| 观测 | 静态站通过 nginx access/error log 排障 |

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

1. 当前实际工作区分支为 `dev`，不是用户描述的 `main`；合入 main 前需按分支策略 cherry-pick 或 MR。
2. 部署机必须先执行 `infra/deploy/live-host-onboarding.md`，创建 `/var/www/kickoff-live-host` 与 nginx vhost。
3. 本次不修改 `apps/web/**` / `apps/mobile/**` 前台实现。
