---
id: "doc-6e1b6ee10243"
title: "Agent 工作日志 · support-reception-mvp"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "MySQL", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-support-reception-mvp.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-support-reception-mvp.md"
sourceSha256: "906c95875f62125db98d882c0ac24da73688b825b0dcc53f3db384dbf7abc8b8"
sourceSystem: "project-doc"
---

# Agent 工作日志 · support-reception-mvp

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-support-reception-mvp.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：新增 MVP 客服接待系统

## 输入资料

- PRD：`docs/prd/product-prd.md`
- 需求 ID：SUPPORT-001
- 设计图：用户提供 C 端客服聊天截图
- 设计图文件名：IMAGE 2026-06-02 18:20:02.jpg
- 视觉要点：C 端是点对点客服对话；后台需要一个“客服接待”菜单，由运营客服人员回复用户。
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`AGENTS.md`

## 本次目标

1. 增加 C 端客服会话创建、拉消息、发消息接口。
2. 增加后台客服会话列表、消息列表、回复、关闭、重开接口。
3. 后台新增“运营管理 / 客服接待”菜单和简易接待页。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000032_create_support_chat_tables.*.sql` | 新增客服会话与消息表 |
| `services/go-app/internal/model/support.go` | 新增客服 model |
| `services/go-app/internal/dto/support.go` | 新增客服 DTO |
| `services/go-app/internal/service/support/service.go` | 新增客服会话与消息业务逻辑 |
| `services/go-app/internal/http/public/support.go` | 新增 C 端客服 handler |
| `services/go-app/internal/http/adminapi/support.go` | 新增后台客服 handler |
| `services/go-app/internal/http/router/public.go` | 注册 C 端客服路由 |
| `services/go-app/internal/http/router/admin.go` | 注册后台客服路由与 cs_admin RBAC |
| `apps/admin/src/api/modules/support.ts` | 新增后台客服 API client |
| `apps/admin/src/views/support/reception.vue` | 新增后台客服接待页面 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 同步客服接口契约 |

## 核心决策

1. MVP 阶段不引入完整工单系统，仅实现一对一客服会话与消息。
2. 客服消息暂用后台轮询，避免把客服聊天混入直播 WebSocket 频道。
3. 匿名 C 端使用 `visitor_key` 绑定会话；登录 C 端使用 JWT 用户 ID 绑定会话。
4. 后台客服接口要求 `cs_admin`，`super_admin` 按 RBAC 规则自动放行。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | SUPPORT-001 |
| 模块 PRD | `docs/prd/product-prd.md` |
| OpenAPI / Event / DTO | 已更新 `docs/api/openapi.yaml` 与 `packages/contracts/openapi/v1.yaml` |
| 不涉及契约的原因 | 不适用 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 000032 migration，含 down.sql 与索引 |
| 是否影响账本、事务、幂等或审计 | 不影响资金账本；后台回复/状态变更写 audit |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 不是；包含 C 端/后台两套鉴权边界、匿名访客会话绑定、客服消息未读计数 |
| 涉及能力 | 权限安全 / 迁移 / 审计 |
| 当前 MVP 边界 | 不做客服分配队列、在线状态、已读回执、WebSocket 实时客服 |
| 未来迁移成本 | 中等；可在现有会话/消息表上增加分配策略和 WS 推送 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行新增 migration；不新增服务和端口 |
| 回滚 | 回滚代码并执行 000032 down.sql 可删除客服表 |
| 密钥 | 不涉及 |
| 备份恢复 | 新增客服消息数据，纳入现有 MySQL 备份 |
| 观测 | 后台写操作进入既有审计日志 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 匿名客服必须携带 visitor_key，后台接口有 cs_admin RBAC |
| 红队质疑 | 轮询有延迟，不适合高并发强实时客服；MVP 可接受，上线后按量升级 WS |
| 合入判断 | 可合入 dev 验证 |

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
| `go test ./services/go-app/internal/service/support ./services/go-app/internal/http/public ./services/go-app/internal/http/adminapi ./services/go-app/internal/http/router` | 通过 |
| `go test ./services/go-app/internal/...` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm run openapi:validate` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate packages/contracts/openapi/v1.yaml` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户提供客服聊天截图 |
| 页面截图 | 未启动浏览器截图；本次以后台 typecheck 和接口闭环为准 |
| API 接口路径 | `/api/v1/admin/support/*` |
| 后台权限与审计 | `cs_admin` / `super_admin`；回复、关闭、重开写 audit |
| 根节点是否挂载 | 已在运营管理菜单挂载 `SupportReception` |
| 合入判断 | 可进入 dev 联调 |

## 风险与待办

1. 后台页面当前只支持文字回复和图片展示，图片回复按钮可后续接 `/api/v1/upload scene=support`。
2. 当前消息刷新使用 5 秒轮询；客服量上来后建议升级单独客服 WS。
3. 暂未实现客服分配、在线状态、快捷话术、已读回执。

## 交接说明

1. C 端匿名用户先调用 `POST /api/v1/support/conversations/current`，保存返回的 `id` 和本地 `visitor_key`。
2. C 端图片消息先调用 `/api/v1/upload`，`scene=support`，再把返回 URL 作为 `content` 发送。
3. 后台客服入口是“运营管理 / 客服接待”。
