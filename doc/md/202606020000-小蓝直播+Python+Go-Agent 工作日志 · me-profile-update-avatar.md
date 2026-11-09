---
id: "doc-49db0ba25133"
title: "Agent 工作日志 · me-profile-update-avatar"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-me-profile-update-avatar.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-me-profile-update-avatar.md"
sourceSha256: "e06f05e090a7c8286cf4dc4885c09edcdfd78e9030bd4447de85c45c601ed016"
sourceSystem: "project-doc"
---

# Agent 工作日志 · me-profile-update-avatar

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20me-profile-update-avatar.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：扩展个人中心资料更新接口，支持头像与用户名保存

## 输入资料

- 需求 ID：MEMBER-002
- 接口文档：`https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/meUsernameUpdate`
- 关联接口：`https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/userUpload`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 保留通用上传接口只返回 URL，不自动写业务字段。
2. 扩展 `PATCH /api/v1/me/username`，支持保存 `username` 和 `avatar_url`。
3. 同步 OpenAPI 与 contracts 文档。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/member.go` | 扩展个人资料更新请求与响应 DTO |
| `services/go-app/internal/http/public/member.go` | 资料更新 handler 改为调用 service 统一更新 |
| `services/go-app/internal/service/member/service.go` | 新增 `UpdateProfile`，要求至少传一个字段 |
| `services/go-app/internal/service/member/username_test.go` | 补充资料更新测试 |
| `docs/api/openapi.yaml` | 更新 `meUsernameUpdate` 文档 |
| `packages/contracts/openapi/v1.yaml` | 同步 contract 文档 |

## 核心决策

1. 不恢复上传接口自动写用户资料，避免通用上传和业务保存职责混在一起。
2. 保留历史路径与 `operationId=meUsernameUpdate`，向后兼容只改用户名的旧调用。
3. 头像保存需要先调用 `/api/v1/upload scene=avatar`，再把返回 URL 传给资料更新接口。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | MEMBER-002 |
| OpenAPI / DTO | 已更新 `docs/api/openapi.yaml` 与 `packages/contracts/openapi/v1.yaml` |
| 不涉及契约的原因 | 不适用 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 不影响资金；用户名和头像沿用已有用户审计 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 是，个人资料字段更新 |
| 涉及能力 | 权限安全 / 审计 |
| 当前 MVP 边界 | 只支持用户名与头像 URL；找回密码凭证资料另走独立需求 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./services/go-app/internal/service/member ./services/go-app/internal/http/public` | 通过 |
| `go test ./services/go-app/internal/...` | 通过 |
| `npm run openapi:validate` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate packages/contracts/openapi/v1.yaml` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 交接说明

1. 上传头像：先调用 `POST /api/v1/upload`，`scene=avatar`。
2. 保存资料：调用 `PATCH /api/v1/me/username`，body 可传 `{ "avatar_url": "<upload url>" }`、`{ "username": "小蓝" }` 或两个字段一起传。
3. 至少传 `username` 或 `avatar_url` 一个字段，否则返回参数错误。
