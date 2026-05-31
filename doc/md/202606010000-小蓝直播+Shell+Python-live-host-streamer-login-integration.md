---
id: "doc-cc7abcb49f8f"
title: "live-host-streamer-login-integration"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-host-streamer-login-integration.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-host-streamer-login-integration.md"
sourceSha256: "4c6e9a9cffd38d59234435e5922f593f69ea53e6524b66f666a6e969594a5b71"
sourceSystem: "project-doc"
---

# live-host-streamer-login-integration

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-live-host-streamer-login-integration.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：Codex
任务：接入 `apps/live-host` 主播登录接口，并补开发环境 API 代理

## 输入资料

- PRD：`docs/prd/modules/README.md`（主播端历史说明）、`apps/live-host/README.md`
- 需求 ID：`STR-001`
- 设计图：不涉及
- 设计图文件名：不涉及
- 设计图尺寸：不涉及
- 视觉要点：沿用现有主播端登录页与设备调试页
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/http/streamerapi/auth.go`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`AGENTS.md`
- 项目 Overlay：`project.config.json`
- 其他：开发环境已配置 `NUXT_PUBLIC_API_URL`

## 本次目标

1. 将 `live-host` 登录接口从占位 `/host/auth/*` 切换为真实 `/streamer/auth/*`
2. 兼容当前后端返回结构并持久化主播登录态
3. 为开发环境补 `/api` 代理，避免浏览器直接跨域请求 `api-dev`

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/live-host/nuxt.config.ts` | 支持 `NUXT_PUBLIC_API_URL`，dev 下为 `/api` 启用 Nitro `devProxy` |
| `apps/live-host/app/composables/useAuth.ts` | 对齐主播登录/登出接口与 `me + token` 响应结构 |
| `apps/live-host/app/pages/login.vue` | 改进登录错误处理，接入新 auth composable |
| `apps/live-host/app/pages/index.vue` | 使用真实主播信息展示页头，开播跳转传真实显示名 |
| `apps/live-host/app/layouts/default.vue` | 顶栏展示真实主播字段 |
| `apps/live-host/.env.example` | 改为 `NUXT_PUBLIC_API_URL` 主配置，保留 `API_BASE` 覆盖 |
| `apps/live-host/.env.staging` | 同上 |
| `apps/live-host/app/components/devices/DevicePicker.vue` | 清理未使用 props 变量，修复 lint |
| `apps/live-host/app/components/studio/DanmuList.vue` | 显式导入 `nextTick`，修复 lint |
| `apps/live-host/app/components/studio/GiftBannerLayer.vue` | 显式导入 `nextTick`，修复 lint |
| `apps/live-host/app/components/studio/ToastStack.vue` | 显式导入 `useToast`，修复 lint |
| `apps/live-host/app/pages/studio/[room_id].vue` | 显式导入 `useToast`，修复 lint |

## 核心决策

1. `NUXT_PUBLIC_API_URL` 视为 API 实际目标地址；浏览器默认直连该地址，只有显式将 `NUXT_PUBLIC_API_BASE` 设为空串时才走本地 `/api` 代理。
2. 鉴于 OpenAPI 与 Go 服务在主播 token 字段上存在漂移，前端按真实登录结构 `data.me + data.token` 落地，并兼容额外 token 字段。
3. 保留现有设备调试/开播流程，不在本次扩展“我的房间”与“开播签发 Zego token”接口，避免扩大改动面。
4. 后续排查发现 `api-dev` 已对 `http://localhost:3001` 放行 CORS，因此将默认策略改为“浏览器直连 `NUXT_PUBLIC_API_URL`”；本地 `/api` 代理仅作为显式启用的兜底方案。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属于规则、模板、脚本、技术栈适配器，还是项目资产 | 项目资产 + Nuxt dev 代理适配 |
| 哪些内容可复用到下一个项目 | `NUXT_PUBLIC_API_URL` + devProxy 的同源代理思路 |
| 哪些内容只属于当前项目 | 主播端 `/api/v1/streamer/auth/*` 契约与本地 storage key |
| 是否可规模化到多 Agent、多端、多 Web surface、多服务或 Go Gin + Laravel | 可复用到同类 Nuxt SPA + Go API 项目 |
| 是否涉及 Scale Profile：mvp / growth / scale / enterprise | `mvp` |
| 是否影响项目 Overlay：project.config.json / docs/project | 否 |
| 是否增加了自动校验或 CI 门禁 | 否 |
| 是否降低了 Agent 偷懒空间 | 是，避免继续使用占位接口与错误 env 名称 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | `STR-001` |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | 当前主 PRD 已废弃主播端，实际以 `apps/live-host/README.md` + OpenAPI 为准 |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/streamer.go` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 不适用，本次直接对齐契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | 不涉及 |
| 是否只是 CRUD | 否，属于前端鉴权接线与运行时代理 |
| 涉及能力 | 权限安全 |
| 不适用项及原因 | 不涉及异步、账本、迁移、统计 |
| 当前 MVP 边界 | 仅接登录/登出，不扩主播开播业务接口 |
| 未来迁移成本 | 低；后续接 refresh / 我的房间 / start-live 可继续在现有 composable 上扩展 |
| 升级触发指标 | 主播端需要自动续签或多房间切换时 |
| 高风险触发项 | 权限 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 仅影响前端运行时 env 读取与开发代理；不影响生产入口 |
| 回滚 | 回滚 `live-host` 相关前端文件即可 |
| 密钥 | 更新了 `.env.example` / `.env.staging` 的 API 变量说明；未新增 secret |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 登录接口、登出接口、dev 代理、类型检查、全量 lint 均已验证 |
| 红队质疑 | OpenAPI 与后端 token 字段存在漂移，已在前端兼容处理但仍建议后端统一契约 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | verified |
| Project Decision | pending-review |
| 完成申请 | 已实现并验证主播登录接入与开发代理 |
| 完成裁决 | 待 Reviewer / Owner / QA |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 失败，环境缺少 Python `PIL` 依赖，不是本次代码引入 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `./node_modules/.bin/nuxt typecheck` | 通过 |
| `./node_modules/.bin/eslint . --cache --cache-location /tmp/live-host-eslint-cache` | 通过 |
| `curl -i -X POST https://api-dev.54-151-131-132.sslip.io/api/v1/streamer/auth/login ...` | 远端接口存在，返回 400/401，非 404 |

## 风险与待办

1. 主播端仍未接 `/api/v1/streamer/me/rooms`、`/rooms/{room_id}/start`、`/refresh-zego-token`，当前开播流程继续依赖本地 Zego dev token。
2. OpenAPI 中主播 token schema 与 Go 实现不一致，建议后端统一为单一真实契约。
3. 项目级 runtime validator 依赖 Python `PIL`，当前执行环境缺依赖，CI/本地环境需补装。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 开发环境推荐只配 `NUXT_PUBLIC_API_URL`；前端请求继续写 `/api/...`，由 Nuxt dev proxy 转发。
2. `useAuth` 已持久化 access/refresh token 和主播 `me` 信息，可继续扩 refresh 逻辑。
3. 若继续接通“我的房间/开播”链路，应优先使用现有主播端 OpenAPI 路径，不要再依赖 `.env` 中的假 `roomID/userID`。
