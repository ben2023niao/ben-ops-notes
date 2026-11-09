---
id: "doc-2a5d23fb0f3b"
title: "admin-account-password-update"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-admin-account-password-update.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-admin-account-password-update.md"
sourceSha256: "7cf5cdb4ca9fdf19243b64ab1a8dbd8b4f9728a2e198237eab056c6bac640cd9"
sourceSystem: "project-doc"
---

# admin-account-password-update

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BRedis-admin-account-password-update.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：后台管理员账号补充修改密码功能

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-003
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 在管理员账号列表为 super_admin 增加修改管理员密码入口。
2. 后端提供管理员密码修改接口，写入 bcrypt 哈希并撤销目标管理员旧 token。
3. 同步 OpenAPI / contracts，并补充测试和工作日志。

## 数据链路

入口页面：`apps/admin/src/views/admins/list.vue` 管理员账号列表
API：`PUT /api/v1/admin/admins/{id}/password`
DTO：`dto.AdminAccountPasswordUpdateRequest`
Service：`AdminAccountService.UpdatePassword`
数据表 / Redis：`admins.password_hash`、`admin:revoked_before:{id}`
返回字段：空成功响应
前端消费字段：不新增列表返回字段，仅新增请求体 `password`

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/admin_account.go` | 增加管理员密码修改逻辑，事务内更新密码并写 Redis 撤销时间 |
| `services/go-app/internal/http/adminapi/admin_account.go` | 增加 UpdatePassword handler |
| `services/go-app/internal/http/router/admin.go` | 挂载 super_admin 保护路由 |
| `services/go-app/internal/dto/admin_modules.go` | 增加请求 DTO |
| `services/go-app/internal/service/admin/admin_account_test.go` | 覆盖成功、账号不存在、Redis 缺失三条路径 |
| `apps/admin/src/api/modules/admin-account.ts` | 增加 updatePassword API client |
| `apps/admin/src/views/admins/list.vue` | 增加改密按钮和弹窗 |
| `apps/admin/src/locales/langs/*/adminAccount.json` | 增加中英文文案 |
| `docs/api/openapi.yaml` | 增加接口契约 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts |
| `docs/prd/modules/kickoff-admin.md` | ADM-003 补充超管可修改管理员密码 |
| `services/go-app/go.mod` / `go.sum` | 增加 `go-sqlmock` 测试依赖 |

## 核心决策

1. 仅 `super_admin` 可修改管理员密码，沿用管理员账号管理权限边界。
2. 改密成功后写 `admin:revoked_before:{id}`，目标管理员旧 token 立即失效。
3. DB 更新和 Redis 撤销写入放在同一 service 事务流程内；Redis 不可用时回滚 DB 更新并返回依赖错误。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-003 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / DTO | `PUT /api/v1/admin/admins/{id}/password`、`AdminAccountPasswordUpdateRequest` |
| 是否影响前端字段 | 不涉及列表返回字段变更；新增后台请求体字段 `password` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 影响权限安全；写 `admin.account.update_password` 审计 |
| 后台权限与审计 | super_admin 权限；写 admin audit |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 权限安全 |
| 高风险触发项 | 权限 |
| 能力门禁结论 | 允许合入，已补 token 撤销与测试 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 影响 Go Admin API 和 admin 静态构建产物 |
| 回滚 | 回滚本次代码即可移除入口和接口 |
| 密钥 | 不涉及 |
| 观测 | 新增审计 action：`admin.account.update_password` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin -run 'TestAdminAccount' -count=1` | 通过 |
| `go vet ./...` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `go test ./... -count=1` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| API 接口路径 | `PUT /api/v1/admin/admins/{id}/password` |
| 后台权限与审计 | super_admin 可见；后端 super_admin 路由保护；写审计 |
| mock/fallback 状态与原因 | 不涉及 |
| 合入判断 | 待 reviewer / QA 验收 |

## 风险与待办

1. 需要部署到 dev 后用真实后台账号执行一次改密 E2E。
2. 修改当前登录管理员自己的密码后，该管理员旧 token 会失效，需要重新登录。
