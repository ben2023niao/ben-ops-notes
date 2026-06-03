---
id: "doc-45a9393ad373"
title: "Laravel 在 Monorepo 中的构建方式"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Docker", "Nginx", "MySQL", "Redis", "自动化"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/laravel-monorepo-structure.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/laravel-monorepo-structure.md"
sourceSha256: "0de4d10d62c9d481ba92b3a029605cbe6caec56a4d651a4980fd26705cee1fa0"
sourceSystem: "project-doc"
---

# Laravel 在 Monorepo 中的构建方式

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/laravel-monorepo-structure.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文件说明团队在 Monorepo 中使用 Laravel 时的推荐目录。核心原则：

```text
Monorepo 管工程边界
Laravel 管 PHP 应用内部结构
```

也就是说，Monorepo 不会把 Laravel 拆散。完整 Laravel 应用应该放在一个服务目录内，例如：

```text
services/laravel-app/
```

如果项目是纯 Laravel 产品，也可以配置为：

```text
apps/laravel-app/
```

但团队默认 Go Gin + Laravel 混合栈下，Laravel 作为完整 PHP 应用服务，推荐放在 `services/laravel-app/`。

## 1. 推荐总目录

```text
repo/
  apps/
    mobile/                  # 可选：移动端/客户端
    admin/                   # 可选：React/Vue 独立后台前端；若使用 Filament 可不创建

  services/
    go-app/                     # Go Gin：核心 API、高并发、账本、实时相关
    laravel-app/               # Laravel：完整应用服务，Web/API/Filament/Console/Jobs
    realtime/                # Go：WebSocket/事件
    worker/                  # Go 或独立 worker；Laravel queue 可留在 laravel-app 内

  packages/
    contracts/               # OpenAPI、事件、错误码、DTO 约定
    generated/php/           # 从 contracts 生成的 PHP DTO/client
    php/                     # Laravel/PHP 公共 helper
    ui/

  docs/
    prd/
    architecture/
    qa/
    agents/

  infra/
    ci/
    deploy/
```

## 2. Laravel 应用内部推荐结构

以下结构保留 Laravel 原生习惯，同时按业务领域拆分。示例以视频、采集、搜索、SEO异常验证、广告、运营后台为例；新项目按 PRD 替换领域名。

```text
services/laravel-app/
  app/
    Console/
      Commands/
        Crawl/
        Video/
        Stats/

    DTO/
      Video/
      Crawl/
      Search/
      SEO异常验证/

    Enums/
      ErrorCode.php
      VideoStatus.php
      CrawlStatus.php
      SourceType.php

    Exceptions/
      BusinessException.php

    Filament/
      Resources/
        VideoResource/
        CategoryResource/
        TagResource/
        ActorResource/
        CrawlSourceResource/
        CrawlTaskResource/
        AdResource/
        PageResource/
        SettingResource/
        SearchKeywordResource/
        OperationLogResource/
      Pages/
      Widgets/
      Actions/

    Http/
      Controllers/
        Home/
        Video/
        Category/
        Search/
        User/
        Page/
        Ad/
        Auth/
        Crawl/
      Requests/
        Video/
        Category/
        Search/
        Auth/
        Crawl/
      Resources/
        Video/
        Category/
        Search/

    Jobs/
      Crawl/
        CrawlCategoryJob.php
        CrawlVideoDetailJob.php
        SyncM3u8StatusJob.php
      Video/
        RefreshVideoStatsJob.php
      Search/
        BuildSearchIndexJob.php

    Models/
      Video.php
      VideoSource.php
      VideoPlayUrl.php
      VideoStats.php
      Category.php
      Tag.php
      Actor.php
      CrawlSource.php
      CrawlTask.php
      CrawlTaskLog.php
      Ad.php
      Page.php
      SearchKeyword.php
      WatchHistory.php
      Favorite.php
      Setting.php
      OperationLog.php

    Services/
      Video/
        VideoService.php
        VideoQueryService.php
        VideoPlayService.php
        VideoStatsService.php
      Category/
        CategoryService.php
      Search/
        SearchService.php
      Crawl/
        CrawlSourceService.php
        CrawlTaskService.php
        HeimuCrawlerService.php
        M3u8ParserService.php
      SEO异常验证/
        SeoService.php
      Ad/
        AdService.php
      User/
        UserService.php
      Shared/
        CacheKeyManager.php
        ResponseBuilder.php

    Support/
      ContentStatus.php
      VideoUrlNormalizer.php
      HashHelper.php

  config/
    modules/
      video.php
      crawl.php
      SEO异常验证.php
      ads.php
      cache.php

  database/
    migrations/
    seeders/
    factories/

  routes/
    web.php
    api.php
    api/
      video.php
      category.php
      search.php
      page.php
      auth.php
      crawl.php
      ad.php

```

Laravel 应用目录中不放 Monorepo 级 Docker 和产品文档。它们属于根目录公共工程层：

```text
infra/
  deploy/
  docker/
docs/
  go-app/
  prd/
  operations/
```

`services/laravel-app/` 内可以保留服务级 README 或框架原生文档，但产品 PRD、跨端 API 文档、部署文档、Docker/Nginx/PHP-FPM/MySQL/Redis 编排不放进 Laravel 应用目录。

## 3. Laravel 内部分层规则

| 层 | 职责 | 禁止 |
| --- | --- | --- |
| `Http/Controllers` | HTTP 入口、调用 Request、Service/Action、返回 Resource | 禁止堆业务规则 |
| `Http/Requests` | 参数校验、权限前置校验 | 禁止写复杂业务流程 |
| `Http/Resources` | 输出结构，对齐 OpenAPI schema | 禁止私自新增契约外字段 |
| `Services` | 业务用例、查询、播放、采集、SEO异常验证、广告等领域服务 | 禁止直接接收未校验 request |
| `DTO` | 服务层输入输出对象 | 禁止把数组在多层之间裸传 |
| `Enums` | 状态、错误码、类型枚举 | 禁止 magic string 散落 |
| `Jobs` | 队列任务、异步处理、采集、索引构建 | 必须幂等，可重试 |
| `Filament` | 后台资源、页面、组件、操作 | 敏感操作必须写权限和审计 |
| `Models` | Eloquent 模型和关系 | 禁止承载复杂业务流程 |
| `Support` | 小型纯工具 | 禁止变成业务垃圾桶 |

## 4. 路由拆分规则

`routes/api.php` 只做聚合，不放大量路由定义：

```php
require __DIR__.'/api/video.php';
require __DIR__.'/api/category.php';
require __DIR__.'/api/search.php';
require __DIR__.'/api/page.php';
require __DIR__.'/api/auth.php';
require __DIR__.'/api/crawl.php';
require __DIR__.'/api/ad.php';
```

每个领域路由文件对应 OpenAPI path 分组：

```text
routes/api/video.php     -> packages/contracts/openapi/paths/video.yaml
routes/api/search.php    -> packages/contracts/openapi/paths/search.yaml
routes/api/crawl.php     -> packages/contracts/openapi/paths/crawl.yaml
routes/api/ad.php        -> packages/contracts/openapi/paths/ad.yaml
```

## 5. Filament 与 apps/admin 的关系

两种模式二选一，不要混乱：

| 模式 | 目录 | 适用 |
| --- | --- | --- |
| Laravel + Filament 一体后台 | `services/laravel-app/app/Filament` | 快速后台、运营 CRUD、审核配置 |
| 独立前端后台 | `apps/admin` + `services/laravel-app` 或 `services/go-app` | 复杂前端交互、统一后台 UI、多后端 API |

如果使用 Filament 一体后台：

1. `apps/admin` 可以不创建，或只保留 README 说明。
2. 后台页面验收以 Filament Resource、Policy、Action、审计日志为核心。
3. CI 重点跑 Laravel Feature test、Policy test、Filament action test。

如果使用独立 `apps/admin`：

1. `apps/admin` 只做前端。
2. `services/laravel-app` 或 `services/go-app` 承载后台 API，具体 owner 由 OpenAPI 标注。
3. 前端和后端通过 OpenAPI 协作。

## 6. Monorepo 中的契约归属

Laravel 内部可以有 DTO 和 Resource，但跨端契约仍归：

```text
packages/contracts/
```

规则：

1. Laravel Resource 必须对齐 OpenAPI schema。
2. Laravel Enum 中的错误码、状态码必须同步到 `packages/contracts/errors.md` 或 OpenAPI enum。
3. 新增 routes/api/*.php 前，先新增或更新 OpenAPI path。
4. Filament 后台敏感操作也要登记到 PRD/验收矩阵，不能因为是后台页面就绕过规则。

## 7. Laravel 与 Go Gin 的边界

团队默认：

```text
Go Gin       核心 API、强事务、高并发、实时相关
Laravel      后台运营、CRUD、采集任务、配置、审核、Filament
```

跨服务协作示例：

```text
Laravel 审核视频状态
  -> 写 operation_logs
  -> 发布 domain event 或调用 Go API
  -> Go 公开 API 读取新状态或刷新缓存
  -> ECC 验证前台状态变化
```

禁止：

1. Laravel 直接引用 Go internal 包。
2. Go 直接读 Laravel 私有 service。
3. 两边同时无约束写同一核心表。
4. 后台绕过 Go 的账本/订单服务直接改余额。

## 8. Git 协作方式

Monorepo 下 Laravel 不单独开一个长期独立仓库。按功能分支协作：

```text
feature/video-crawl
feature/admin-video-review
feature/search-index
```

不要按技术角色拆成：

```text
laravel/video
go/video
frontend/video
```

一个功能如果同时影响 Laravel、Go、OpenAPI、前端和测试，应放在同一个 MR，保证契约和实现一致。

大功能可以拆阶段：

```text
feature/video-contract
feature/video-laravel-admin
feature/video-go-public-go-app
feature/video-ecc
```

但每个阶段都必须能独立验证，不能留下半截不可用状态。

## 9. Laravel 任务验收

涉及 `services/laravel-app/**` 的任务，Agent 日志必须写：

1. PRD 来源。
2. OpenAPI path 或说明不涉及 API。
3. Controller / Request / Resource / Service / Job / Filament Resource 修改范围。
4. 是否有 migration。
5. 是否有 Policy/Gate。
6. 是否有 OperationLog。
7. Feature test / Unit test / queue test。
8. 是否影响 Go Gin 服务或跨服务 ECC。

## 10. 推荐检查命令

```bash
cd services/laravel-app
composer validate
composer install
php artisan test
php artisan route:list
php artisan migrate --pretend
```

可选增强：

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
vendor/bin/pest
```

这些命令应由项目按实际依赖接入根目录 `npm run check` 或 CI。
