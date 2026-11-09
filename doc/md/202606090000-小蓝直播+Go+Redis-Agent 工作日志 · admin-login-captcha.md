---
id: "doc-a1e2ccb0aa87"
title: "Agent 工作日志 · admin-login-captcha"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Redis", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-login-captcha.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-admin-login-captcha.md"
sourceSha256: "637e3761df27a4a8e8932afd216a89d8eaed2c8327483d3083376aa924e69413"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-login-captcha

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606090000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BRedis-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-login-captcha.md)

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：后台登录页移除上线前开发账号提示，并新增图形验证码

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-003
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`

## 本次目标

1. 后台登录页不再展示超级管理员、财务管理员、客服管理员、房间管理员等开发快捷填充入口。
2. 后台登录增加图形验证码，降低登录刷接口风险。
3. 同步 Go DTO、OpenAPI、contract、后台登录页和中英文文案。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/captcha.go` | Redis 一次性图形验证码生成与校验；后端绘制 PNG 图片 |
| `services/go-app/internal/service/admin/captcha_test.go` | 验证码生成、消费、错误输入、Redis 不可用单测 |
| `services/go-app/internal/service/admin/auth.go` | 后台登录先校验验证码再查账号密码 |
| `services/go-app/internal/http/adminapi/auth.go` | 新增后台验证码 handler |
| `services/go-app/internal/http/router/admin.go` | 新增 `GET /api/v1/admin/auth/captcha` 并加 IP 限流 |
| `services/go-app/internal/dto/admin.go` | 登录请求新增 `captcha_id`、`captcha_code` |
| `apps/admin/src/views/_core/authentication/login.vue` | 删除开发账号快捷填充，新增验证码输入和刷新 |
| `apps/admin/src/api/core/auth.ts` | 新增后台验证码 API client |
| `apps/admin/src/locales/langs/*/mp.json` | 新增验证码文案，删除开发填充文案 |
| `docs/api/openapi.yaml` | 更新后台登录契约 |
| `packages/contracts/openapi/v1.yaml` | 更新 contracts 契约 |
| `docs/prd/modules/kickoff-admin.md` | 记录上线安全口径 |

## 核心决策

1. 验证码使用 Redis 存储，TTL 2 分钟，登录校验后一次性消费，输错也失效；图片由后端绘制为 PNG data URL，不返回 SVG 文本字符。
2. 验证码接口按 IP 限流 30 次/分钟；登录接口保留原 IP 与账号维度限流。
3. 登录页沿用 `AuthenticationLogin` 和 Vben Form schema，通过 suffix 渲染验证码图片，不重写整套登录 UI。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-003 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `GET /api/v1/admin/auth/captcha`；`POST /api/v1/admin/auth/login` 新增 `captcha_id`、`captcha_code` |
| 是否影响前端字段 | 影响后台登录页字段；不影响 C 端、主播端字段 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金账本；登录成功/失败原审计保持 |
| 规范例外与原因 | 直接执行 `eslint` 未命中 monorepo 配置，改用项目 `typecheck` 与 build 校验 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要同时部署 Admin API 与后台前端，否则新版登录页无法拿到验证码 |
| 回滚 | 回滚本次 commit 即可恢复旧登录契约 |
| 密钥 | 不涉及 |
| 观测 | 复用现有登录审计与错误响应 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin ./internal/http/adminapi ./internal/http/router` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:stg` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 涉及页面 | 后台登录页 `/auth/login` |
| API 接口路径 | `GET /api/v1/admin/auth/captcha`、`POST /api/v1/admin/auth/login` |
| 后台权限与审计 | 登录成功/失败审计保持；验证码接口无需登录 |
| 与设计图主要偏差 | 删除开发快捷填充；新增图形验证码 |
| 合入判断 | 允许提交，等待 CI/QA 验证线上页面 |

## 风险与待办

1. 需要后端和后台前端同步发布；只发前端会导致登录缺验证码接口。
2. 验证码是基础图形验证码，可抵挡简单刷接口；如上线后遇到授权安全测试可再接行为验证码或 WAF。
