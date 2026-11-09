---
id: "doc-7f6369f271a3"
title: "项目类型 Preset"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/project/presets.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/project/presets.md"
sourceSha256: "009456ad26bbc8c88a9c99e0d8bfaf154c02b83b6b0000490493eb6fd57fea97"
sourceSystem: "project-doc"
---

# 项目类型 Preset

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-%E9%A1%B9%E7%9B%AE%E7%B1%BB%E5%9E%8B%20Preset.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

项目类型 preset 用来降低新项目启动时的决策成本。公共框架提供推荐组合，项目 Overlay 决定是否采用。

Preset 不是强制所有项目一样，而是给 AI Agent 一个清晰起点，避免每次都凭感觉猜目录和技术栈。

每个 preset 都有一个结构化 profile：

```text
framework/profiles/{preset}/profile.json
```

初始化脚本优先读取 profile 文件，再写入 `project.config.json`。`framework.config.json` 中的 preset 只作为索引和兼容层，二者必须保持一致。

## 1. 可选 preset

| preset | 适用场景 | 必选模块 | 推荐模块 |
| --- | --- | --- | --- |
| `mobile-app` | 移动 App、App 下载官网、实时能力 | `apps/mobile`、`apps/web` | `services/go-app`、`services/realtime`、`services/worker` |
| `nuxt-web` | 官网、下载页、PC 站、H5、公开 Web 产品，默认 Nuxt 4 + Tailwind CSS v4 | `apps/web` | `services/go-app` |
| `go-gin-api` | Go Gin API-first 服务，可包含 Public API 和 Admin API | `services/go-app` | `apps/admin`、`apps/web` |
| `laravel-app` | Laravel Web/API/Filament/Console/Jobs 一体化项目 | `services/laravel-app` | `packages/php/support`、`packages/php/filament` |
| `fullstack-monorepo` | Nuxt Web + Go Gin API + Laravel 应用 + Worker/Realtime 的完整 Monorepo | `apps/web`、`services/go-app`、`services/laravel-app` | `apps/mobile`、`apps/admin`、`services/worker`、`services/realtime` |
| `custom` | 特殊项目 | 项目自行声明 | 项目自行声明 |

兼容别名：`web-platform` 等同 `nuxt-web`，`go-gin-app` 等同 `go-gin-api`，`go-gin-laravel` 等同 `fullstack-monorepo`。新项目优先使用表格中的正式 preset 名称。

## 2. 使用规则

1. `project.config.json.project.type` 和 `project.config.json.project.preset` 应保持一致。
2. 选择 preset 后，必选模块必须在 `project.config.json` 中启用。
3. 推荐 service 可由 profile 默认启用；推荐 app 不默认启用，避免误开后台或官网。
4. 推荐模块可以不启用，但需要在任务或 ADR 中说明原因。
5. 选择 `custom` 时，必须在 `docs/project/constraints.md` 写明自定义原因。
6. 不允许用 preset 绕过公共硬规则。
7. 修改 preset 必须同步更新 `framework/profiles/**/profile.json` 并运行 `npm run check:framework-modules`。

## 3. 示例

移动 App 项目：

```json
{
  "project": {
    "type": "mobile-app",
    "preset": "mobile-app",
    "scaleProfile": "mvp"
  },
  "apps": {
    "mobile": { "enabled": true },
    "web": { "enabled": true }
  },
  "services": {
    "go-app": { "enabled": true },
    "realtime": { "enabled": true },
    "worker": { "enabled": true }
  }
}
```

Laravel 一体化项目：

```json
{
  "project": {
    "type": "laravel-app",
    "preset": "laravel-app",
    "scaleProfile": "mvp"
  },
  "services": {
    "laravel-app": { "enabled": true }
  }
}
```
