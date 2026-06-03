---
id: "doc-8843a2130e6f"
title: "Go Gin + Laravel 后端技术线"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Docker", "Nginx", "MySQL", "Redis", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/backend-stack-go-gin-laravel.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/backend-stack-go-gin-laravel.md"
sourceSha256: "f1054e2520580fc3d850681f3ae07407445f198d5b69843ed14998f372556a00"
sourceSystem: "project-doc"
---

# Go Gin + Laravel 后端技术线

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/backend-stack-go-gin-laravel.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文件是团队公共 AI 框架的 P0 后端技术栈适配说明。新项目如果采用团队默认后端栈，优先使用：

```text
Go + Gin       核心 API、高并发服务、网关、实时、worker
PHP + Laravel 完整 Laravel 应用服务，承载 Web/API/Filament/Console/Jobs
```

本文件是公共框架规则，不是某个项目的业务 PRD。具体业务接口仍以 `packages/contracts` 和项目 PRD 为准。

后端实现必须同时遵守：

```text
docs/quality/code-standards.md
docs/architecture/database-design-standards.md
```

## 1. 推荐目录

```text
services/
  go-app/                 # Go Gin：核心应用服务
    cmd/
      api/                # Public API 入口
      admin/              # Admin API 入口，可选；当 OpenAPI owner 指向 services/go-app 时使用
      migrate/            # 迁移或维护命令，可选
    internal/
      config/             # 配置加载
      http/
        public/           # 面向 App/Web 的 API handler
        admin/            # 面向后台管理的 API handler
        middleware/       # auth、trace、rate limit
      application/        # usecase / command / query
      domain/             # 领域模型、领域服务、领域事件
      repository/         # repository interface
      infrastructure/     # mysql、redis、queue、third-party adapter
      observability/      # log、metrics、trace
    migrations/           # 如 Go 服务持有表结构
    tests/
  laravel-app/           # Laravel：完整应用服务，Web/API/Admin API/Filament/Console/Jobs
    app/
      Console/Commands/
      DTO/
      Enums/
      Exceptions/
      Filament/
      Http/Controllers/
      Http/Requests/
      Http/Resources/
      Jobs/
      Models/
      Services/
      Support/
    config/modules/
    database/migrations/
    routes/api/
    tests/Feature/
    tests/Unit/
  realtime/            # Go：WebSocket、事件、在线状态
  worker/              # Go 或 Laravel Queue，按项目配置
packages/
  contracts/           # OpenAPI、事件、错误码、DTO
  generated/go/        # 从契约生成的 Go DTO/client
  generated/php/       # 从契约生成的 PHP DTO/client
  go/                  # Go 多服务公共包
  php/                 # PHP/Laravel 公共包
docs/
  architecture/
  api/
  qa/
  agents/logs/
```

Laravel 在 Monorepo 中不是被拆散，而是在 `services/laravel-app/` 内保持完整 Laravel 应用结构。更详细的 Laravel 领域目录、Filament、Jobs、routes/api 拆分见：

```text
docs/architecture/laravel-monorepo-structure.md
```

目录边界：

1. `services/go-app` 不依赖 Laravel 应用代码。
2. `services/laravel-app` 不依赖 Go 内部包。
3. 两者只能通过数据库、消息队列、事件或 HTTP 契约协作。
4. 跨服务字段、错误码、事件必须放在 `packages/contracts`。
5. 业务规则必须写入 `docs/prd` 或 `docs/architecture`，不能只藏在 Controller/Handler 里。

## 2. 服务分工

| 领域 | 默认归属 | 原因 |
| --- | --- | --- |
| 用户登录、核心用户态、公开 API | Go Gin | 高并发、接口稳定、方便水平扩展。 |
| 订单、钱包、账本、扣费 | Go Gin | 强事务、幂等、审计和性能优先。 |
| 实时连接、在线状态、消息事件 | Go | 长连接和资源控制优先。 |
| Filament 后台、角色权限、菜单 | Laravel | 后台生态和 CRUD 效率高。 |
| 用户管理、内容审核、举报处理 | Laravel | 运营流程复杂，Laravel 开发效率高。 |
| Web 页面、配置、活动、Banner、报表 | Laravel | Laravel/Filament/Blade/Inertia 等生态选择灵活。 |
| 定时任务/异步任务 | Go 或 Laravel Queue | 按任务归属选择，必须幂等。 |

如果某个业务同时影响 Go 和 Laravel，必须先写清服务边界：

```text
契约 owner：哪个服务暴露 API
数据 owner：哪个服务拥有写权限
事件 owner：哪个服务发布事件
审计 owner：哪个服务记录审计
```

## 3. OpenAPI 归属规则

OpenAPI 不属于 Go，也不属于 Laravel，而是跨团队契约。

`apps/admin` 也不决定后台 API 属于谁。前后端分离后台必须先在 `docs/api/admin-api.md` 和 OpenAPI 中标注 owner service，再分别派生 Go 或 Laravel 实现任务。

建议拆分：

```text
packages/contracts/openapi/
  index.yaml
  paths/
    public-auth.yaml       # owner: services/go-app
    public-users.yaml      # owner: services/go-app
    admin-users.yaml       # owner: services/laravel-app 或 services/go-app/admin
    admin-reports.yaml     # owner: services/laravel-app 或 services/go-app/admin
  schemas/
    user.yaml
    admin.yaml
    error.yaml
```

每个 path 文件必须在文件头或旁边文档标注：

```text
ownerService: services/go-app
runtime: go
framework: gin
```

或：

```text
ownerService: services/laravel-app
runtime: php
framework: laravel
```

变更规则：

1. 新接口先改 OpenAPI，再写 Gin Handler 或 Laravel Controller。
2. 前端 mock、后端实现、测试用例都围绕 OpenAPI。
3. Go 和 Laravel 返回的错误结构必须一致。
4. 破坏性字段变更必须写 ADR 或 migration plan。

## 4. Go Gin 工程规则

推荐结构：

```text
internal/http/          # Gin router、handler、response mapper
internal/application/   # use case / service
internal/domain/        # 实体、领域规则、接口
internal/infrastructure/ # MySQL、Redis、队列、第三方 SDK
internal/middleware/    # auth、trace、recover、rate limit
```

Gin 规则：

1. Handler 只做参数绑定、鉴权上下文、调用 use case、返回响应。
2. 业务规则不得堆在 Handler。
3. 请求体验证必须对应 OpenAPI schema。
4. 所有响应使用统一 error envelope。
5. 高风险写操作必须要求 idempotency key。
6. 数据库事务必须在 application 或 infra 层明确，不在 Handler 里散写。
7. 测试至少包含 handler test、use case test、高风险 repository/transaction test。

Go Gin 推荐命令：

```bash
cd services/go-app
go test ./...
go test -race ./...
go vet ./...
```

## 5. Laravel 工程规则

简化推荐结构：

```text
app/Http/Controllers/   # 只接 HTTP，不写复杂业务
app/Http/Requests/      # 请求校验
app/Actions/            # 单一业务动作
app/Services/           # 跨动作服务
app/Models/             # Eloquent model
app/Policies/           # 权限
database/migrations/    # 表结构
tests/Feature/          # API/权限/流程测试
tests/Unit/             # 服务和规则测试
```

复杂业务或内容/采集/搜索/SEO异常验证/广告项目，推荐使用领域化 Laravel 结构：

```text
app/DTO/
app/Enums/
app/Filament/Resources/
app/Http/Controllers/{Domain}/
app/Http/Requests/{Domain}/
app/Http/Resources/{Domain}/
app/Jobs/{Domain}/
app/Services/{Domain}/
routes/api/{domain}.php
config/modules/{domain}.php
```

Laravel 规则：

1. Controller 只做 request、policy、action、resource response。
2. FormRequest 必须承接请求校验。
3. Policy/Gate 必须承接后台权限。
4. 业务动作优先放入 Action，避免 Controller 肥大。
5. Resource/DTO 输出必须对齐 OpenAPI schema。
6. 后台敏感操作必须写 audit log。
7. migration 必须可重复部署，不手改线上表。
8. Queue job 必须幂等，失败可重试。

Laravel 推荐命令：

```bash
cd services/laravel-app
composer install
php artisan test
php artisan migrate --pretend
php artisan route:list
```

如果项目使用 Pint/PHPStan/Psalm，也必须加入 `npm run check` 或 CI。

## 6. 数据库与事务边界

默认原则：

1. 一个表只能有一个主要写入 owner。
2. Go 和 Laravel 不同时随意写同一核心表。
3. 如果必须共享表，必须在 `docs/architecture/data-model.md` 标出 owner 和允许写入场景。
4. 资金、订单、账本、扣费默认由 Go 服务持有写权限。
5. 后台审核、运营配置默认由 Laravel 持有写权限。
6. 跨服务同步优先使用事件或明确 API，不靠双方私下读写彼此内部状态。

## 7. 测试门禁

Go Gin 服务至少：

```text
go test ./...
handler contract tests
high-risk transaction tests
```

Laravel 服务至少：

```text
php artisan test
Feature tests for auth/permission/audit
migration check
```

跨服务 ECC 至少：

```text
前端 -> Go API -> 数据变化
后台 -> Laravel API -> 审计日志
Laravel 审核动作 -> Go 公开 API 状态变化
高风险流程 -> 账本/审计/权限闭环
```

只跑 Go 或只跑 Laravel 都不能证明项目闭环。

## 8. 部署建议

单 VPS / Docker Compose 起步：

```text
nginx
app-mobile/web static
app-admin/web static
go-app-go-gin
laravel-app
realtime-go
worker-go-or-laravel
mysql
redis
```

路由示例，具体前缀由项目在 `infra/deploy/` 的网关或 Nginx 配置中决定：

```text
/api/v1/*        -> services/go-app
/admin/*         -> services/laravel-app Filament
/laravel/api/*   -> services/laravel-app API
/realtime/*      -> services/realtime
```

部署门禁：

1. Go 和 Laravel 都必须输出健康检查。
2. `.env.example` 必须覆盖两个服务。
3. Laravel app key、queue、cache、session、DB 配置必须分环境。
4. Go 和 Laravel 日志都必须可被采集。
5. 回滚必须说明数据库 migration 的处理方式。

## 9. Agent 工作要求

当任务涉及 Go Gin：

1. 先读 OpenAPI owner。
2. 再改 Gin route/handler/use case。
3. 补 Go test。
4. 日志写明 handler、use case、事务和错误码。

当任务涉及 Laravel：

1. 先读 OpenAPI owner。
2. 再改 route/controller/request/action/resource。
3. 补 Feature test。
4. 日志写明 permission、audit、migration 和队列影响。

当任务同时涉及 Go Gin + Laravel：

1. 必须写服务边界。
2. 必须写跨服务 ECC。
3. 必须写红蓝对抗。
4. 不能只验证其中一端。
