---
id: "doc-628c2bb658a1"
title: "dev-env-compose-payment-config"
date: "2026-05-30T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Python", "Go", "Docker", "监控告警", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-30-dev-env-compose-payment-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-30-dev-env-compose-payment-config.md"
sourceSha256: "7d9d1b4780a3c658dda8442f5839cc8caca3c2151b8795b49fba9895ff9ad0c2"
sourceSystem: "project-doc"
---

# dev-env-compose-payment-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605300000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BPython-dev-env-compose-payment-config.md)

> 整理日期：2026-05-30 00:00｜日期依据：文件名日期

日期：2026-05-30
Agent：Codex
任务：dev 支付配置改为项目 .env 注入，移除运行时对 /etc/kickoff 的依赖

## 输入资料

- PRD：`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：WALLET-002, WALLET-006, WALLET-007
- 接口/契约：`POST /api/v1/hooks/payment/shark`, `POST /api/v1/hooks/payment/shark/refund`
- 团队可读文档：`infra/deploy/README.md`, `infra/deploy/runner-bootstrap.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户要求 dev 不直接读取 `/etc/kickoff`，真实配置由运维在构建/部署时写入 `.env`

## 本次目标

1. `.env.example` 补齐 Shark 支付配置占位符，不提交真实密钥。
2. `docker-compose.yml` 将 `APP_PAY_SHARK_*` 从 `.env` 注入 Go 服务。
3. dev systemd unit 改为读取 `/opt/kickoff/.env`，不要求写 `/etc/kickoff`。
4. 部署文档同步 dev 配置落点和权限口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.env.example` | 新增 Shark 支付 env 模板 |
| `docker-compose.yml` | `x-go-env` 新增 Shark 支付环境变量 |
| `infra/deploy/systemd/kickoff-api.service` | dev API 改读 `/opt/kickoff/.env` |
| `infra/deploy/systemd/kickoff-admin.service` | dev Admin API 改读 `/opt/kickoff/.env` |
| `infra/deploy/systemd/kickoff-web.service` | dev Web SSR 改读 `/opt/kickoff/.env` |
| `infra/deploy/README.md` | 更新 dev secret 文件、目录、权限和运维说明 |
| `infra/deploy/runner-bootstrap.md` | 更新一次性 bootstrap 的 `.env` 创建步骤 |
| `infra/deploy/web-onboarding.md` | 更新 Web SSR 运行时 env 文件路径 |
| `infra/deploy/deploy.sh` | 更新部署前置条件注释 |

## 核心决策

1. dev 环境统一使用 `/opt/kickoff/.env`，因为 deploy 用户已需要访问 `/opt/kickoff`，不额外要求 `/etc` 写权限。
2. `.env.example` 只放占位符和默认关闭开关，真实商户号、密钥、网关、回调 URL 不进 git。
3. docker compose 继续依赖项目根目录 `.env` 的默认加载机制，systemd dev unit 通过 `EnvironmentFile=/opt/kickoff/.env` 复用同一份配置。

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | dev API/Admin/Web 的 systemd unit 需要 `daemon-reload` 后重启 |
| 回滚 | 可将 systemd unit 的 `EnvironmentFile` 改回旧路径，但不建议 |
| 密钥 | 影响 `.env.example` 与 dev `.env` 配置流程；真实密钥仍不入库 |
| 备份恢复 | 不涉及数据库、对象存储、账本、审计日志 |
| 观测 | 不涉及日志、指标、trace、告警 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | dev 不再要求 `/etc/kickoff` 写权限，配置路径与 compose 一致 |
| 红队质疑 | `/opt/kickoff/.env` 必须 `600` 且 owner 为 `kickoff:kickoff`，避免同机非授权用户读取 |
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
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `rg -n "/etc/kickoff|APP_PAY_SHARK_NOTIFY_URL=http://54\\.151|hooks/shark" infra/deploy README.md docker-compose.yml .env.example` | 通过；仅剩说明性注释，无实际 `/etc/kickoff` 读取 |
| `docker compose config` | 通过 |
| `python3 scripts/validate-ops-readiness.py` | 通过 |
| `npm run check:ops` | 通过 |
| `python3 scripts/validate-engineering-standards.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 风险与待办

1. 运维需要在 dev 服务器 `/opt/kickoff/.env` 写真实值并确认权限。
2. Shark 支付启用前，回调 URL 必须使用公网 HTTPS 域名，路径为 `/api/v1/hooks/payment/shark` 与 `/api/v1/hooks/payment/shark/refund`。
