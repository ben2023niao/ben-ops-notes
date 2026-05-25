---
id: "doc-fde9091a031b"
title: "Agent 工作日志 · auth-response-user-contract"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-auth-response-user-contract.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-auth-response-user-contract.md"
sourceSha256: "cf5f540d88e5c0bbf04996f830691357a27920e4e2f0fc995883ce4cb033a3a6"
sourceSystem: "project-doc"
---

# Agent 工作日志 · auth-response-user-contract

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-auth-response-user-contract.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：修复注册成功后未返回 user 字段

## 输入资料

- PRD：`docs/prd/modules/kickoff-auth.md`
- 需求 ID：AUTH-002, AUTH-004, AUTH-010
- 接口/契约：`packages/contracts/openapi/v1.yaml`, `docs/api/openapi.yaml`
- 前端只读核对：`apps/web/shared/types/user.ts`, `apps/web/app/composables/useAuth.ts`
- 验收引用：`docs/qa/project-acceptance.md`

## 本次目标

1. `POST /api/v1/auth/register` 成功响应按 OpenAPI 返回 `data.user`。
2. 登录与 refresh 共用同一响应结构，避免三处 auth 接口契约不一致。
3. 增加回归测试，直接防止旧结构 `user_id/account/level/token` 再次返回。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/auth.go` | `AuthResponse` 改为 OpenAPI 的 `AuthTokenPair` 结构：顶层 token 字段 + `user` 对象 |
| `services/go-app/internal/service/auth/auth.go` | 组装 `AuthUser`，补齐 `id/account/username/avatar_url/level/level_name/status/created_at/created_ts` |
| `services/go-app/internal/service/auth/auth_test.go` | 增加公共 auth 响应契约回归测试，并断言 JSON 不再包含旧字段 |

## 核心决策

1. 以现有 OpenAPI 与 H5 类型为准，不新增兼容旧入口。
2. `username` 为空时回退为 `account`，符合注册默认用户名规则。
3. 用户状态输出对齐契约枚举：`ACTIVE/FROZEN/BANNED/DELETED`。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/auth` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 风险与待办

1. 本次只修后端公共 auth 响应，不修改 H5/Web 前端代码。
2. OpenAPI 原本已声明 `AuthTokenPair.user`，本次是让 Go 实现追上契约，因此未改 OpenAPI 内容。
