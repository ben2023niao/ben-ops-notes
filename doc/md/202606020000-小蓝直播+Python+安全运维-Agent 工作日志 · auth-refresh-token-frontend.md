---
id: "doc-1088089e49ec"
title: "Agent 工作日志 · auth-refresh-token-frontend"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-auth-refresh-token-frontend.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-auth-refresh-token-frontend.md"
sourceSha256: "726cafc29f764570a52487cae4bcefc43b21ed5ae571344d23cc747c280217ea"
sourceSystem: "project-doc"
---

# Agent 工作日志 · auth-refresh-token-frontend

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20auth-refresh-token-frontend.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：修复 admin / live-host / web 三端 refresh_token 前端续签逻辑

## 输入资料

- PRD：`docs/prd/modules/kickoff-auth.md`
- 需求 ID：AUTH-010
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. Admin 端 401 后使用 refresh_token 续签并重试请求。
2. Live-host 端统一 API client 在 401 后续签并重试请求。
3. Web 端统一 useApi 在 401 后续签并重试请求，并在 logout 时携带 refresh_token。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/preferences.ts` | 开启 Vben refresh token 模式。 |
| `apps/admin/src/api/request.ts` | 实现 `doRefreshToken`，写回 access / refresh token。 |
| `apps/live-host/app/composables/useApiClient.ts` | 401 或 envelope code=401 时 refresh + retry，失败进入过期流程。 |
| `apps/web/app/composables/useApi.ts` | client 交互请求 401 时 refresh + retry；refresh 失败清理登录态。 |
| `apps/web/app/apis/auth.ts` | logout 支持提交 refresh_token。 |
| `apps/web/app/composables/useAuth.ts` | logout 调用传入当前 refresh token。 |

## 核心决策

1. 后端不改，按用户要求只补前端接入。
2. refresh 请求不走已有拦截器，避免 refresh 自身 401 触发递归。
3. 每个失败请求最多 retry 一次，避免无限循环。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | AUTH-010 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-auth.md` |
| OpenAPI / Event / DTO | 未改契约；沿用现有 `/auth/refresh` 与 `/streamer/auth/refresh` |
| 不涉及契约的原因 | 本次只接入既有接口。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 权限安全 |
| 高风险触发项 | 权限 / 用户数据 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅前端构建产物变化 |
| 回滚 | 回滚本次前端文件变更 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 续签请求绕开业务拦截器，避免递归；失败后清理登录态。 |
| 红队质疑 | Admin 本地后端路由未在本次修改，需确认部署环境已有对应 refresh 接口。 |
| 合入判断 | 可提交评审。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/live-host typecheck` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 失败：本机缺 Python `PIL` |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及页面 UI |
| 页面截图 | 不涉及页面 UI |
| API 接口路径 | `/auth/refresh`、`/api/v1/auth/refresh`、`/api/v1/streamer/auth/refresh` |
| console 是否无 error | 未启动浏览器验证；已完成 typecheck |
| 合入判断 | 可提交评审 |

## 风险与待办

1. Admin 端需确认部署后端已提供 `/auth/refresh`。
2. 未做真实过期 token 的端到端 curl/浏览器验证。
3. 运行环境 validator 仍受本机缺 `PIL` 阻塞。

## 交接说明

1. 如需进一步验证，可用短 TTL access token 模拟 401，观察三端是否自动续签并重放原请求。
2. Web logout 现在会提交 refresh_token，后端可撤销 refresh token。
3. 如 Admin 后端实际没有 `/auth/refresh`，前端会在 refresh 失败后走重新登录。
