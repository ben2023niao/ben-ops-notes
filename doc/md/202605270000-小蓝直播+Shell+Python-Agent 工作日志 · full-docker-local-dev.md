---
id: "doc-2da33c0cb55a"
title: "Agent 工作日志 · full-docker-local-dev"
date: "2026-05-27T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Docker", "MySQL", "Redis", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-full-docker-local-dev.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-27-full-docker-local-dev.md"
sourceSha256: "92149a9c58a190aefaa57748e346fd589853c9b93efab72b6ab776b985180ed6"
sourceSystem: "project-doc"
---

# Agent 工作日志 · full-docker-local-dev

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605270000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20full-docker-local-dev.md)

> 整理日期：2026-05-27 00:00｜日期依据：文件名日期

日期：2026-05-27
Agent：Codex
任务：容器化本地完整开发栈

## 输入资料

- PRD：不涉及业务需求变更
- 需求 ID：不涉及
- 接口/契约：`docs/api/openapi.yaml`（未改契约）
- 团队可读文档：`infra/deploy/README.md`、`docs/operations/build-vs-runtime-boundary.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：`docker-compose.yml`、`services/go-app/config/`、`apps/web/nuxt.config.ts`

## 本次目标

1. 本机不安装 Go/Node，仅用 Docker 跑完整联调栈。
2. 一条命令启动 MySQL、Redis、迁移、API、Admin API、C 端 Web、Admin Web。
3. 验证四个本地入口可访问。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docker-compose.yml` | 扩展为全 Docker 本地联调编排 |
| `Makefile` | 增加 `docker-up`、`docker-down`、`docker-reset`、`docker-logs` |
| `infra/docker/go-dev.Dockerfile` | 增加 Go 1.25 开发镜像 |
| `infra/docker/frontend-dev.Dockerfile` | 增加 Node 20 + pnpm 开发镜像 |
| `services/go-app/config/config.docker.yaml` | 增加 Docker 本地配置 |
| `scripts/docker-migrate-seed.sh` | 增加 MySQL 等待、migration、seed 一次性脚本 |
| `infra/deploy/README.md` | 增加本地全 Docker 开发说明 |
| `apps/web/nuxt.config.ts` | 支持 `NUXT_DEV_API_PROXY`，修复 Docker SSR API 访问 |
| `apps/web/app/plugins/api.ts` | SSR 使用服务端 API base，浏览器端继续同源 |
| `docs/templates/prd-module-template.md` | 修复 PRD validator 依赖的模板文件 |
| `docs/templates/prd-item-template.md` | 修复 PRD validator 依赖的模板文件 |
| `docs/quality/prd-gates.md` | 修复 PRD validator 依赖的质量文档 |

## 核心决策

1. 本地开发 Compose 使用 bind mount 源码，避免宿主机 Go/Node 依赖。
2. 前端依赖安装拆为 `frontend-deps` 一次性容器，避免 Web/Admin Web 并发写同一个 `node_modules` volume。
3. C 端 Web 的 SSR 走 `http://api:8080`，浏览器端仍走同源 `/api`，避免暴露 Docker 内网服务名。
4. 这是 local/dev 编排，不改变生产构建期与运行时边界。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 + 本地开发适配 |
| 哪些内容可复用到下一个项目 | Compose 拆分依赖容器、Docker dev config、migrate seed 模式 |
| 哪些内容只属于当前项目 | Kickoff 服务名、端口、Go config、seed/migration 路径 |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可服务多 Web surface 与 Go Gin 本地联调 |
| 是否涉及 Scale Profile | mvp |
| 是否影响项目 Overlay | 不影响 |
| 是否增加了自动校验或 CI 门禁 | 未增加 CI 门禁 |
| 是否降低了 Agent 偷懒空间 | 降低，提供可复现的一键本地验证入口 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | 不涉及业务 PRD |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | 不涉及 |
| OpenAPI / Event / DTO | 未修改 |
| 验收证据行 | 本日志验证记录 |
| 不涉及契约的原因 | 仅改本地开发编排和 Nuxt dev/SSR API 代理 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及新增表 |
| 是否影响数据表 / migration / 索引 | 不改 DDL，仅新增本地迁移执行脚本 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及业务资金逻辑 |
| 规范例外与原因 | `validate-runtime-environment.py` 在宿主机缺 Node 时失败；本任务目标是 Docker 化规避宿主机 Node/Go |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | 不涉及 |
| 是否只是 CRUD | 否 |
| 涉及能力 | 迁移 / 开发环境可复现 |
| 不适用项及原因 | 不涉及业务高可用、资金一致性、权限变更 |
| 当前 MVP 边界 | 本机 Docker 联调 |
| 未来迁移成本 | 生产镜像仍需按 build-vs-runtime-boundary 单独建设 |
| 升级触发指标 | 节点 >= 2、零停机需求、build 时长 >= 5min |
| 高风险触发项 | 不涉及 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 仅影响本地 Docker 开发入口，不替代 `infra/deploy` 快速验证部署链路 |
| 回滚 | `git revert` 本次文件变更；本地数据可 `make docker-reset` 重建 |
| 密钥 | 新增本地默认 env fallback；生产 secret 仍不进 git |
| 备份恢复 | 不影响生产备份恢复 |
| 观测 | 本地通过 `make docker-logs` 查看容器日志 |
| Runbook | README 已补本地命令 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 四个入口 HTTP 200，Web SSR API 代理已修复 |
| 红队质疑 | 本地 migrate 脚本忽略重复 migration 错误，只适合 local/dev，不适合生产 |
| 合入判断 | 可进入 review |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |
| 完成申请 | 已实现本地全 Docker 启动并提交验证证据 |
| 完成裁决 | 等 Reviewer / Owner / QA / CI |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 失败：宿主机缺 `node` |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `docker compose up -d --force-recreate frontend-deps api admin-api web admin-web` | 通过 |
| `docker compose exec -T web pnpm --filter @kickoff/web typecheck` | 通过 |
| `docker compose exec -T web pnpm --filter @kickoff/web lint` | 失败：52 errors / 49 warnings，集中在既有 Vue 自动导入 `no-undef`、`vue/html-self-closing` 等；本次修改文件未出现在报错列表 |
| `curl http://203.0.113.1:8080/healthz` | 200 |
| `curl http://203.0.113.1:8081/healthz` | 200 |
| `curl http://203.0.113.1:3000/` | 200 |
| `curl http://203.0.113.1:5174/` | 200 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及 |
| 页面截图 | 未截图，本次为 Docker 运行验证 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` 未更新 |
| 真实手机视口 | 未测 |
| 桌面/平板视口 | HTTP 入口已验证 |
| 响应式验收 | 不涉及 UI 改版 |
| 公共组件拆分 | 不涉及 |
| API 接口路径 | `/api/v1/home/today-matches` 等 SSR 请求已走 Public API |
| SEO异常验证/分享/下载渠道 | 不涉及 |
| mock/fallback 状态与原因 | 不涉及 |
| 后台权限与审计 | 不涉及 |
| 根节点是否挂载 | C 端首页返回 SSR HTML |
| 静态资源是否 200 | 未逐项检查 |
| console 是否无 error | 未做浏览器控制台验收 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 可进入 review |

## 风险与待办

1. 宿主机缺 Node 时 `validate-runtime-environment.py` 仍失败；本地 Docker 可运行，但全量 host gate 仍需安装 Node 或调整门禁策略。
2. `scripts/docker-migrate-seed.sh` 为 local/dev 幂等体验忽略重复 migration 错误，生产仍应使用正式 migrate 流程 fail-closed。
3. Web lint 当前存在既有规则问题；本次修改文件未触发 lint 报错，但全量 lint 仍需单独治理。
4. 本次未构建生产镜像，未改变 `infra/deploy` 两机快速验证方案。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 本地启动使用 `make docker-up` 或 `docker compose up --build`。
2. 访问入口：C 端 `:3000`，Admin Web `:5174`，Public API `:8080`，Admin API `:8081`。
3. 停止保留数据用 `make docker-down`，重置数据卷用 `make docker-reset`。
