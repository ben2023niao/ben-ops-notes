---
id: "doc-845c5eba82a8"
title: "Monorepo 仓库结构说明"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/repo-structure.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/repo-structure.md"
sourceSha256: "ca454253805fe845683e30c68a8de0e9603d56cac0c83cee9fbc86aa98e6a5c6"
sourceSystem: "project-doc"
---

# Monorepo 仓库结构说明

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/repo-structure.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文是 乌托邦 的公共 Monorepo 结构规则。业务项目初始化后可以按 preset 启用其中一部分目录，但不能改变目录职责。

乌托邦 采用 Monorepo 的目标，是让客户端、后台、服务端、契约、测试和文档共享同一套上下文，让 AI Agent 能围绕同一份 PRD、契约和验收证据工作。

## 使用原则

1. 目录按职责启用，不按个人角色启用。不要给“前端分支”“后端分支”各建一套重复目录。
2. `apps/*` 是可运行应用；`services/*` 是服务端应用或服务；`packages/*` 是跨端共享能力；`docs/*` 是项目事实源和验收证据。
3. 官网、下载页、PC/H5、公开 Web 统一归入 `apps/web`。
4. 后台管理前端归入 `apps/admin`；后台 API 可以由 `services/go-app` 或 `services/laravel-app` 提供，必须通过 OpenAPI 标注 owner。
5. Laravel 保持完整应用边界，归入 `services/laravel-app`。
6. 未启用目录不能放假实现冒充进度，可以只保留 README 或在 `docs/project/constraints.md` 写明例外。

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `apps/mobile` | 用户端 App 或主客户端。 |
| `apps/web` | 官网、下载页、PC 站、H5、公开 Web 产品站。默认 Nuxt 4 + Tailwind CSS v4。 |
| `apps/admin` | 后台管理前端；只放后台前端，不放 Go/PHP 服务端。 |
| `services/go-app` | Go Gin 核心应用服务，承载 Public API、Admin API、领域逻辑和高并发服务。 |
| `services/laravel-app` | 完整 Laravel 应用服务。团队默认可承载 Web/API/Filament/Console/Jobs；目录内部保持 Laravel 原生结构；不用 Laravel 时可以不创建。 |
| `services/realtime` | 实时服务、消息、事件推送、在线状态。 |
| `services/worker` | 异步任务、回调、定时任务。 |
| `packages/contracts` | 平台无关契约源头：OpenAPI、事件、错误码、schema。 |
| `packages/generated` | 从契约生成的 ts/go/php 代码，不手写业务逻辑。 |
| `packages/ts` | TypeScript 生态公共包，按 `shared/web/mobile` 拆。 |
| `packages/ui` | 设计 token 和 UI 组件，按 `tokens/web/mobile` 拆。 |
| `packages/go` | Go 多服务公共包，按 `kit/httpx/observability` 拆。 |
| `packages/php` | PHP/Laravel 公共包，按 `support/filament` 拆。 |
| `infra/deploy` | 部署脚本、环境配置、发布说明。 |
| `infra/ci` | CI/CD 配置、质量门禁脚本。 |
| `docs` | PRD、架构能力门禁、API、QA、Agent 规则和项目沉淀。 |

## 依赖方向

```text
apps/* -> packages/contracts
apps/* -> packages/generated/ts
apps/mobile -> packages/ts/mobile
apps/mobile -> packages/ui/mobile
apps/web -> packages/ts/web
apps/web -> packages/ui/web
apps/admin -> packages/ts/web
apps/admin -> packages/ui/web
services/* -> packages/contracts
services/go-app -> packages/generated/go
services/go-app -> packages/go/*
services/realtime -> packages/go/*
services/worker -> packages/go/*
services/laravel-app -> packages/generated/php
services/laravel-app -> packages/php/*
services/go-app -/-> services/laravel-app
services/laravel-app -/-> services/go-app/internal
services/* -/-> apps/*
packages/* -/-> apps/*
```

服务端不得依赖客户端代码。Go Gin 和 Laravel 服务之间也不得直接引用彼此内部代码，只能通过 OpenAPI、事件、数据库 owner 规则或消息队列协作。契约包只能包含跨端稳定类型、接口和事件定义，不放业务实现。公共包边界见 `docs/architecture/package-boundaries.md`。

## Web 应用边界

```text
apps/mobile    移动 App 或主客户端
apps/web       官网、下载页、投放页、隐私条款、PC/H5/Public Web 产品站
apps/admin   后台管理前端
```

Web 项目不能被塞进 `apps/mobile` 或 `apps/admin` 里凑合。官网和下载页统一归入 `apps/web`。详细规则见 `docs/architecture/web-surface-strategy.md`。

## 规模化边界

MVP 阶段可以保持少服务、少部署，但必须保留服务 owner、数据 owner、契约 owner 和架构能力判断。真实访问量上来后，按 `docs/architecture/capability-gates.md` 与 `docs/architecture/scaling-strategy.md` 的 `growth`、`scale`、`enterprise` 轨道评审，不按“看起来经典”的目录名提前乱拆。

## 文档优先规则

1. 新模块先在本文件登记职责。
2. 新业务对象先更新 `docs/architecture/data-model.md`。
3. 新接口先更新 `packages/contracts/` 与 `docs/api/`。
4. 重大技术取舍写入 `docs/decisions/`。
