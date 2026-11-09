---
id: "doc-f8be726f9159"
title: "项目 Overlay"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/project/README.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/project/README.md"
sourceSha256: "c1ded4621a2088e5141ccace119b5a1464e535d108a3210dc17f1058bc48271c"
sourceSystem: "project-doc"
---

# 项目 Overlay

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-%E9%A1%B9%E7%9B%AE%20Overlay.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

`project.config.json` 是项目级约束入口，用来描述当前项目在公共 AI 框架上的选择和例外。

公共框架负责回答：

1. Monorepo 目录怎样分层。
2. Agent 必须怎样记录、验证和交接。
3. PRD、OpenAPI、测试、红蓝对抗和 Git 如何协作。
4. Go Gin、Laravel、Nuxt 4、Tailwind CSS v4、packages 边界如何复用。

项目 Overlay 负责回答：

1. 当前项目启用哪些 app、service 和 package。
2. 当前项目选择哪个项目 preset，或是否声明为 custom。
3. 当前项目选 Go Gin、Laravel，还是两者组合。
4. 当前项目是否需要移动 App、官网、PC/H5、后台。
5. 当前项目的设计验收强度是 MVP、参考风格还是严格设计图。
6. 当前项目有哪些第三方服务、环境、上线约束和例外。

公共框架的硬规则不能被项目 Overlay 关闭。比如 Agent 日志、红蓝对抗、契约优先、项目级验收和“mock 不能冒充完成”都是不可覆盖规则。

## 新项目启动顺序

正式项目通过 `.ai-framework` 子仓库启动：

```bash
git submodule add <AI_FRAMEWORK_REPO_URL> .ai-framework

# 执行前需要设置 OWNER_PROJECT、OWNER_TECH_LEAD 等 CODEOWNERS 环境变量。
bash .ai-framework/scripts/init-project.sh --target "$PWD" --type mobile-app "Project Name" project-slug
```

1. 挂载 `.ai-framework` 并运行初始化脚本，初始化项目名、owner 和项目类型。
2. 选择 `docs/project/presets.md` 中的项目类型 preset，或声明为 `custom`。
3. 填写 `project.config.json` 的项目类型、启用模块、技术栈和第三方服务。
4. 填写本目录下的项目约束文档。
5. 填写 `docs/prd/product-prd.md` 和 `packages/contracts/openapi/index.yaml`。
6. 运行 `npm run check:project-overlay`。
7. 通过后再进入业务开发。

## 典型选择

移动 App 项目通常启用：

```text
apps/mobile
apps/web
services/go-app
services/realtime
services/worker
```

Web/PC 项目通常启用：

```text
apps/web
services/go-app 或 services/laravel-app
```

Laravel 后台一体化项目通常启用：

```text
services/laravel-app
packages/php/support
packages/php/filament
```

前后端分离后台项目通常启用：

```text
apps/admin
services/go-app 或 services/laravel-app
packages/generated/ts
packages/generated/go 或 packages/generated/php
```
