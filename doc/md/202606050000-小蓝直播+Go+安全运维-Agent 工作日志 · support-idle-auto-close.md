---
id: "doc-6e9f8437e3d8"
title: "Agent 工作日志 · support-idle-auto-close"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-support-idle-auto-close.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-support-idle-auto-close.md"
sourceSha256: "d847470d8bfb23ff3a461bff5af28d0ea1b43690116cd7021f8f9d9b861b7e0c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · support-idle-auto-close

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-support-idle-auto-close.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：客服接待会话 5 分钟无新消息自动关闭

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`SUPPORT-001`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户要求“客服系统优化一下，如果接入超过 5 分钟没有发信息则自动关闭”

## 本次目标

1. 后端客服会话超过 5 分钟无新消息自动关闭。
2. 后台客服接待页展示自动关闭规则提示。
3. 同步 OpenAPI / contracts / PRD，并补验证记录。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/support/service.go` | 新增客服会话空闲自动关闭兜底；重开会话重置空闲计时 |
| `services/go-app/internal/service/support/service_test.go` | 校验空闲关闭过滤条件使用 `last_message_at`，不依赖 `updated_at` |
| `apps/admin/src/views/support/reception.vue` | 客服接待页新增 5 分钟自动关闭提示 |
| `apps/admin/src/locales/langs/zh-CN/support.json` | 中文提示文案 |
| `apps/admin/src/locales/langs/en-US/support.json` | 英文提示文案 |
| `docs/api/openapi.yaml` | 同步客服接口自动关闭说明；修复 home banner 排序描述 YAML 写法 |
| `packages/contracts/openapi/v1.yaml` | 同步接口契约 |
| `docs/prd/modules/kickoff-admin.md` | 新增 `SUPPORT-001` 客服接待验收口径 |

## 核心决策

1. 空闲判断只看 `last_message_at`：后台列表轮询、客服查看消息等读操作不会续期。
2. 自动关闭会追加一条系统消息，方便后台客服和用户知道会话为何关闭。
3. 用户或客服后续继续发消息时，复用原会话并重新打开，减少前端对接分支。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及；复用 `support_conversations.last_message_at/status` |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；客服自动关闭为系统兜底，不是后台人工写操作 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，新增客服会话生命周期规则 |
| 涉及能力 | 数据一致性 / 用户数据 / 权限安全 |
| 当前 MVP 边界 | 通过客服相关 API 调用触发兜底；后台页面每 5 秒轮询，能覆盖运营接待场景 |
| 未来迁移成本 | 如需无请求也准时关闭，可迁移为 worker 定时任务，复用当前过滤条件 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不新增服务、不改端口、不改环境变量 |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 观测 | 自动关闭写入系统消息；无新增日志指标 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 5 分钟规则由后端统一执行，避免前端各自实现导致状态不一致 |
| 红队质疑 | 如果后台页面不打开且没有任何 API 请求，自动关闭不会准点触发；当前 MVP 接待页轮询可覆盖运营场景 |
| 合入判断 | 可合入；后续若要求严格定时关闭，再加 worker |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/support` | 通过 |
| `go test ./internal/service/support ./internal/http/public ./internal/http/adminapi` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run check:prd` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm run openapi:validate` | 通过 |
| `git diff --check` | 通过 |

## 风险与待办

1. 当前为 API 触发型兜底，不是独立定时任务；如产品要求“无人访问也严格 5 分钟关闭”，需要增加 worker。
2. 自动关闭没有写 admin 审计，因为它不是后台用户操作；系统消息已保留会话内可见证据。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 空闲关闭判断必须继续基于 `last_message_at`，不要改成 `updated_at`。
2. 后台客服页轮询 `GET /api/v1/admin/support/conversations` 会触发空闲关闭兜底。
3. `SUPPORT-001` 的接口文档已更新到 Stoplight 对应 operation。
