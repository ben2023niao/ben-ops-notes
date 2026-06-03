---
id: "doc-31a312934443"
title: "Git 工作流规则"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/operations/git-workflow.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/operations/git-workflow.md"
sourceSha256: "a0824aebf814415f5be59ba05ef51870496b57e20d080adaf31b3da0d980ccd2"
sourceSystem: "project-doc"
---

# Git 工作流规则

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/operations/git-workflow.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文档定义 {{PROJECT_NAME}} 团队和 AI Agent 的 Git 使用规则。目标是减少多人协作冲突、避免误操作、保证 PRD、OpenAPI、代码、测试和部署状态一致。

## 1. 为什么 Monorepo 更适合 AI 工程团队

{{PROJECT_NAME}} 使用 Monorepo，不是因为项目一开始就很大，而是因为 AI 工程团队需要统一上下文：

1. AI Agent 可以同时读取 PRD、OpenAPI、前端、后端、测试、ADR 和日志。
2. 前端、后端、测试围绕同一个 `packages/contracts` 协作。
3. 业务规则集中沉淀在 `docs/`，不会散落在多个仓库。
4. 复杂任务可以用一次 MR 同时修改契约、实现、测试和文档，保证版本一致。
5. Agent 工作日志留在仓库内，形成项目记忆。

Monorepo 的价值来自规则，不来自目录本身。没有 Git 规则、CI 规则和 Review 规则，Monorepo 会变成混乱大仓库。

## 2. 分支模型

```text
main                 生产稳定分支
develop              日常集成分支
feature/xxx          功能分支
fix/xxx              普通修复分支
release/x.y.z        预发布分支
hotfix/xxx           生产紧急修复分支
```

推荐流转：

```text
feature/* -> Merge Request -> develop
fix/*     -> Merge Request -> develop
develop   -> release/*     -> staging
release/* -> main          -> production
hotfix/*  -> main + develop
```

分支按功能或任务命名，不按前端/后端角色命名。

推荐：

```text
feature/auth-login
feature/call-billing
feature/gift-send
feature/admin-host-review
```

不推荐：

```text
frontend/login
backend/login
```

原因是一个功能通常会同时影响 PRD、OpenAPI、前端、后端和测试。按角色拆分支容易让契约不一致，按功能拆分支更利于端到端交付。

## 3. 禁止事项

1. 禁止直接 push 到 `main`。
2. 禁止未创建任务就开始大范围改动。
3. 禁止接口变更不更新 OpenAPI。
4. 禁止业务规则变更不更新 PRD 或 `docs/agents/rules/business-rules.md`。
5. 禁止数据模型变更不更新 `docs/architecture/data-model.md`。
6. 禁止复杂 Agent 任务不写 `docs/agents/logs/`。
7. 禁止高风险逻辑无测试合并，包括支付、订单、扣费、权限、审核、删除数据。
8. 禁止在一个 MR 混合无关改动，例如同时做登录、重构 UI、修改部署脚本。

## 4. 每日开发流程

开始任务前：

```bash
git checkout develop
git pull
git checkout -b feature/short-task-name
```

开发过程中保持小步提交：

```bash
git status
git add <files>
git commit -m "feat: add login go-app contract"
```

提交 MR 前同步 develop：

```bash
git checkout develop
git pull
git checkout feature/short-task-name
git rebase develop
```

如果团队 Git 经验不统一，可以先用 `merge develop` 替代 rebase，但全团队必须统一一种方式。

## 5. Commit 规范

```text
feat: 新功能
fix: 修复问题
docs: 文档变更
test: 测试变更
refactor: 重构，不改变行为
chore: 工程配置、依赖、脚手架
ci: CI/CD 变更
build: 构建系统变更
revert: 回滚
```

示例：

```text
docs: add git workflow rules
feat: add call session contract
fix: handle insufficient coin error
test: add gift order idempotency cases
ci: add path based pipeline plan
```

## 6. 任务必须声明修改范围

每个任务开始前写清楚 owner 和文件范围：

```text
任务：实现登录接口
Owner：后端 A
主要修改：
- services/go-app/**
- packages/contracts/openapi/**
- docs/api/**

不得修改：
- apps/mobile/**
- apps/admin/**
```

AI Agent 接到任务时，也必须遵守这个范围。范围不清楚时先补任务说明，不要直接改。

## 7. Merge Request 规则

每个 MR 必须包含：

```text
改了什么
为什么改
影响哪些模块
是否修改 OpenAPI
是否修改数据模型
是否需要数据库迁移
是否影响部署
测试怎么跑
Agent 日志在哪里
```

MR 合并前必须：

1. CI 通过。
2. 至少一个 owner review。
3. 高风险变更需要对应 owner review。
4. 文档、契约、测试和代码保持一致。

## 8. OpenAPI 修改规则

`packages/contracts` 是前端、后端、测试和 Agent 的工程事实来源。

接口变更必须：

1. 先更新 OpenAPI。
2. 更新错误码、事件或 DTO，如有需要。
3. 在 MR 中说明是否破坏兼容。
4. 通知前端、后端、测试 owner review。
5. 同步更新测试用例。

建议后续将 OpenAPI 拆分：

```text
packages/contracts/openapi/
  index.yaml
  paths/
    auth.yaml
    users.yaml
    calls.yaml
    messages.yaml
    orders.yaml
  schemas/
    user.yaml
    call.yaml
    order.yaml
    error.yaml
```

大功能推荐先创建 contract 任务：

```text
feature/auth-login-contract
```

contract 合并后，前端、后端、测试再并行：

```text
feature/auth-login-go-app
feature/auth-login-mobile
feature/auth-login-tests
```

小功能可以直接使用一个功能分支：

```text
feature/auth-login
```

但仍然必须先更新 OpenAPI，再写实现。

## 8.1 Go Gin + Laravel 协作规则

团队默认后端技术线为 Go Gin + Laravel 时，仍然按功能分支协作，不按技术栈长期拆分支。

推荐：

```text
feature/video-crawl
feature/admin-video-review
feature/search-index
feature/order-audit
```

不推荐：

```text
laravel/video
go/video
frontend/video
```

原因是 Monorepo 的核心价值是契约、实现、测试和文档一致。一个功能如果同时影响 Laravel、Go、OpenAPI、前端和测试，应优先放在同一个 MR 中完成端到端闭环。

大功能可以拆成阶段性功能分支：

```text
feature/video-contract
feature/video-laravel-admin
feature/video-go-public-go-app
feature/video-ecc
```

拆分条件：

1. 每个分支都能独立通过 CI。
2. 每个分支都有验收证据和 Agent 日志。
3. 不允许留下“契约已改但两端都不可用”的长期状态。
4. `packages/contracts/**` 修改必须让 Go owner、Laravel owner、前端 owner、QA owner review。

Laravel 专项修改范围示例：

```text
任务：实现视频采集后台
主要修改：
- services/laravel-app/app/Http/Controllers/Crawl/**
- services/laravel-app/app/Services/Crawl/**
- services/laravel-app/app/Jobs/Crawl/**
- services/laravel-app/routes/api/crawl.php
- packages/contracts/openapi/paths/crawl.yaml
- docs/qa/acceptance-evidence.md

不得修改：
- services/go-app/internal/**
- apps/mobile/**
```

Go + Laravel 联动修改范围示例：

```text
任务：后台审核视频后前台可见
主要修改：
- packages/contracts/openapi/paths/admin-video.yaml
- packages/contracts/openapi/paths/video.yaml
- services/laravel-app/app/Filament/Resources/VideoResource/**
- services/laravel-app/app/Services/Video/**
- services/go-app/internal/http/video/**
- tests/ecc/video-review-flow.*
- docs/qa/project-acceptance.md
```

## 9. 冲突处理规则

遇到冲突时：

1. 先确认冲突文件 owner。
2. 不确定业务含义时不要自行选择一边。
3. `openapi`、`data-model`、`business-rules` 冲突必须找对应 owner 确认。
4. 解决冲突后必须重新跑相关测试。
5. 冲突涉及业务规则时，写入 Agent 日志或 ADR。

## 10. Agent 提交规则

AI Agent 完成复杂任务必须：

1. 写 `docs/agents/logs/YYYY-MM-DD-short-task.md`。
2. 说明输入资料、修改文件、核心决策、验证结果、风险和交接。
3. 不隐藏未完成事项。
4. 不跨任务范围改无关文件。

## 11. Hotfix 流程

生产紧急修复：

```text
main -> hotfix/xxx -> MR -> main -> production
                    -> merge/cherry-pick -> develop
```

hotfix 必须补：

1. 问题原因。
2. 修复说明。
3. 回归用例。
4. 发布记录。
