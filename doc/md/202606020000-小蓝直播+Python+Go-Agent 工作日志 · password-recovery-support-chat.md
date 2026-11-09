---
id: "doc-fbcae9130f18"
title: "Agent 工作日志 · password-recovery-support-chat"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-password-recovery-support-chat.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-password-recovery-support-chat.md"
sourceSha256: "2e3889c6a2defc47c341e494156aca14c30b845c2678c023d6884098e1bfc65c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · password-recovery-support-chat

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20password-recovery-support-chat.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：打通找回密码匿名客服沟通链路

## 输入资料

- 需求 ID：SUPPORT-002
- 用户说明：找回密码客服页 100% 匿名；用户发送账号/UID 与凭证图片，后台客服接待核验后重置密码。
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. C 端客服页从本地自动回复改为真实匿名客服会话。
2. 找回密码客服会话标记 `scene=password_recovery`，后台客服可区分。
3. 匿名文字和图片消息写入后端，后台“客服接待”可看到并回复。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000033_add_support_conversation_scene.*.sql` | 给客服会话新增 `scene` 字段与索引 |
| `services/go-app/internal/model/support.go` | 新增客服场景枚举与 model 字段 |
| `services/go-app/internal/dto/support.go` | C 端 current 请求/会话响应补 `scene` |
| `services/go-app/internal/service/support/service.go` | 按 scene 创建/查找客服会话，找回密码欢迎语 |
| `services/go-app/internal/http/public/support.go` | current 接口接收 scene |
| `apps/web/app/apis/support.ts` | 新增匿名客服 API 与匿名凭证图片上传 |
| `apps/web/app/components/im/SupportChat.vue` | H5 客服页接真实接口，轮询后台回复 |
| `apps/admin/src/api/modules/support.ts` | 后台会话类型补 scene |
| `apps/admin/src/views/support/reception.vue` | 后台客服接待显示普通客服/找回密码场景 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 同步 scene 字段与说明 |

## 核心决策

1. 找回密码客服页不使用 C 端 JWT；H5 直接走匿名 support API，避免残留 token 把会话绑定到用户。
2. 当前继续使用 REST 轮询，WS 后续作为实时增强，不阻塞找回密码沟通上线。
3. 图片凭证使用匿名 `/api/v1/upload scene=support`，随后作为 `content_type=image` 消息发送。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | SUPPORT-002 |
| OpenAPI / DTO | 已更新 |
| 不涉及契约的原因 | 不适用 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 000033 migration |
| 是否影响账本、事务、幂等或审计 | 不影响资金；后台回复/关闭沿用客服审计 |
| 规范例外与原因 | H5 本次由项目负责人要求打通客服沟通链路，因此修改 `apps/web/**` |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 不是，涉及匿名会话、后台接待、图片消息和场景隔离 |
| 涉及能力 | 权限安全 / 迁移 / 用户数据 |
| 当前 MVP 边界 | 轮询消息，不做 WS 实时；不实现重置密码新能力 |
| 未来迁移成本 | 可在现有会话表上加 support token 与 WS 事件 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./services/go-app/internal/service/support ./services/go-app/internal/http/public ./services/go-app/internal/http/router` | 通过 |
| `go test ./services/go-app/internal/...` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run openapi:validate` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate packages/contracts/openapi/v1.yaml` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 交接说明

1. H5 `/im` 页面现在会创建 `scene=password_recovery` 的匿名客服会话。
2. 后台“运营管理 / 客服接待”列表会显示“找回密码”标签。
3. 用户发送的凭证图片会以客服图片消息进入后台会话。
