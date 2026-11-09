---
id: "doc-b1e718661d01"
title: "Agent 工作日志 · main-multibrand-cors"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-multibrand-cors.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-multibrand-cors.md"
sourceSha256: "2703affb88e9b2f088ee619b8743cca91dca4540d22859e6420df1ca2d4c0826"
sourceSystem: "project-doc"
---

# Agent 工作日志 · main-multibrand-cors

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20main-multibrand-cors.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：main 多品牌域名兼容与 `pshxti.cn` CORS 修复

## 输入资料

- PRD：不涉及业务 PRD
- 需求 ID：OPS
- 接口/契约：不涉及 OpenAPI / DTO / Event 契约
- 团队可读文档：`infra/deploy/main-business-code-update.md`、`infra/deploy/spug-main-task-template.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：宝塔服务器 `13.229.218.208` Nginx vhost 抽查、`pshxti.cn` / `sssqho.cn` / `voemor.cn` DNS 抽查、CORS 预检复现结果

## 本次目标

1. 解决 `pshxti.cn` 页面调用 API 时的 CORS 403。
2. 让 main 运行时可以通过 `APP_SERVER_CORS_ALLOW_ORIGINS` 兼容多品牌页面域名。
3. 将生产前端默认 API base 从旧 `shijiebeixl.com` 切到 `pshxti.cn` 主链路。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `.gitlab-ci.yml` | 前端生产镜像默认 build args 改为 `api.pshxti.cn` / `admin-api.pshxti.cn`。 |
| `infra/docker/frontend-prod.Dockerfile` | 前端生产 Dockerfile 默认 API 域名改为 `pshxti.cn` 主链路。 |
| `docker-compose.yml` | 根 compose deploy build args 与运行时 env 补齐 `pshxti.cn` API base 和 CORS env 透传。 |
| `infra/deploy/docker-compose.main.yml` | main 正式 compose 透传 `APP_SERVER_CORS_ALLOW_ORIGINS`，storage 默认公网前缀使用 `admin-api.pshxti.cn`。 |
| `infra/deploy/spug-main-update.sh` | `sudo docker compose` 时显式透传 `APP_SERVER_CORS_ALLOW_ORIGINS`。 |
| `services/go-app/internal/config/loader.go` | 支持 `APP_SERVER_CORS_ALLOW_ORIGINS` 逗号分隔 env 覆盖 YAML CORS 列表。 |
| `services/go-app/config/config.docker.yaml` | Docker 配置默认 CORS 白名单加入三品牌页面域名，并保留旧 `shijiebeixl.com` 页面域名。 |
| `services/go-app/config/config.prod.yaml.example` | 生产配置样例同步多品牌 CORS 白名单。 |
| `infra/deploy/README.md` | main 变量模板补充 `pshxti.cn` API base 和 CORS env。 |
| `infra/deploy/spug-main-task-template.md` | Spug main 模板补充 `pshxti.cn` API base 和 CORS env。 |
| `infra/deploy/main-business-code-update.md` | 更新三品牌域名设计、宝塔当前状态、外网检查和 CORS 排障说明。 |
| `docs/agents/logs/2026-06-11-main-multibrand-cors.md` | 本工作日志。 |

## 核心决策

1. CORS 只放浏览器页面 Origin：`h5.*`、`www.*`、apex、`live-host.*`、`admin.*`，不把 API 目标域名作为默认 Origin。
2. C 端和主播端默认 API base 使用 `https://api.pshxti.cn`，后台默认使用 `https://admin-api.pshxti.cn/api/v1/admin`。
3. `APP_SERVER_CORS_ALLOW_ORIGINS` 作为运行时覆盖口，后续新增品牌域名无需改 Go 代码。
4. 旧 `shijiebeixl.com` 页面域名暂时保留在 CORS 白名单中，降低切换风险。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | OPS |
| 需求总账 | 不涉及业务需求总账 |
| 模块 PRD | 不涉及 |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 仅部署配置、运行时配置和运维文档变更。 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | main 需要重新构建/发布 backend/frontend 镜像，使 CORS env 支持和前端 API base 生效。 |
| 宝塔 | 已确认 `api/admin/admin-api` 的 `sssqho.cn` / `voemor.cn` 别名在对应 vhost 中；C 端、主播端别名还需补 DNS/CDN/宝塔 `server_name`。 |
| 密钥 | 未写入真实密码、token 或证书私钥。 |
| 回滚 | 可回滚提交；如只是临时 CORS 调整，可优先改服务器 `.cicd.env` 中 `APP_SERVER_CORS_ALLOW_ORIGINS`。 |

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
| 宝塔 vhost grep | 已确认 `pshxti.cn` 相关 vhost 与部分 `sssqho.cn` / `voemor.cn` API/admin aliases。 |
| DNS 抽查 | `sssqho.cn` / `voemor.cn` apex 已解析；多个子域名仍 no answer。 |
| CORS 预检复现 | `Origin: https://h5.pshxti.cn` 对 API 预检当前返回 403，符合修复目标。 |
| `docker compose run --rm --no-deps api go test ./internal/config` | 通过 |
| `docker compose config` | 通过 |
| `docker compose -f infra/deploy/docker-compose.main.yml config` | 通过，确认 `APP_SERVER_CORS_ALLOW_ORIGINS` 和 `pshxti.cn` 默认域名展开。 |
| `npm run check:ops` | 通过 |
| `sh -n infra/deploy/spug-main-update.sh` | 通过 |
| `python3 scripts/validate-agent-log-boundaries.py` | 通过 |
| `git diff --check` | 通过 |
| secret 扫描（数据库密码 / Telegram token 格式） | 未命中 |

## 风险与待办

1. 未配置 DNS/CDN 的 `sssqho.cn` / `voemor.cn` 子域名即使 CORS 已兼容，也无法访问。
2. 静态前端镜像的 API base 需要通过 main pipeline 重新构建后才会从旧域名切换到 `pshxti.cn`。
3. 若未来希望每个品牌页面调用同品牌 API 域名，需要前端按 `location.hostname` 动态选择 API base，或按品牌分别构建前端镜像。

## 交接说明

1. main CORS 运行时变量：`APP_SERVER_CORS_ALLOW_ORIGINS`。
2. main 推荐前端 API base：`WEB_PUBLIC_API_BASE=https://api.pshxti.cn`、`LIVE_HOST_PUBLIC_API_BASE=https://api.pshxti.cn`、`ADMIN_API_BASE=https://admin-api.pshxti.cn/api/v1/admin`。
3. 宝塔服务器：`13.229.218.208`；main 业务服务器：`54.179.243.100`。
