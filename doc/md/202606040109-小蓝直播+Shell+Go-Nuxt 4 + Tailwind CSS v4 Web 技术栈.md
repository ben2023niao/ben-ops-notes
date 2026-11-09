---
id: "doc-72c325533f6c"
title: "Nuxt 4 + Tailwind CSS v4 Web 技术栈"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "自动化", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/web-stack-nuxt-tailwind.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/web-stack-nuxt-tailwind.md"
sourceSha256: "5dd85d50b558da2cc2f5bfd2551eaf41d5733d738032aebebe99a72144525ad7"
sourceSystem: "project-doc"
---

# Nuxt 4 + Tailwind CSS v4 Web 技术栈

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Nuxt%204%20%2B%20Tailwind%20CSS%20v4%20Web%20%E6%8A%80%E6%9C%AF%E6%A0%88.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文件定义公共 AI 框架中 `apps/web` 的默认 Web 技术栈适配方式。官网、下载页、PC 站、H5 和公开 Web 产品都归入 `apps/web`，不再拆出单独的一级官网下载应用。

```text
Nuxt 4 + Tailwind CSS v4 + pnpm workspace
```

这是 Monorepo 内的 Web app 结构，不是独立仓库。

## 1. 适用范围

| 目录 | 用途 | 默认技术栈 |
| --- | --- | --- |
| `apps/web` | 官网、下载页、营销页、隐私政策、PC 站、H5、公开 Web 产品站 | Nuxt 4 + Tailwind CSS v4 |
| `apps/admin` | 后台管理端 | 可独立选择，复杂后台可用 Nuxt，也可用 Laravel Filament |

移动 App 项目默认需要 `apps/web`。纯 Web 项目默认启用 `apps/web`。

## 2. 推荐目录

```text
apps/web/
  package.json
  nuxt.config.ts
  app/
    app.vue
    assets/
      css/
        main.css
    components/
      base/
      layout/
      domain/
    composables/
      useApiClient.ts
      useAuthState.ts
    layouts/
      default.vue
      marketing.vue
    middleware/
      auth.ts
    pages/
      index.vue
    plugins/
    error.vue
  server/
    go-app/
    middleware/
  public/
  tests/
    unit/
    e2e/
```

官网和下载页在 `apps/web` 内按页面或 feature 拆分：

```text
apps/web/
  app/
    pages/
      index.vue
      privacy.vue
      terms.vue
    components/
      hero/
      download/
      feature/
      trust/
```

## 3. Nuxt 4 目录规则

1. 使用 Nuxt 4 默认 `app/` 作为应用源目录。
2. 页面放 `app/pages/`。
3. 组件放 `app/components/`，按 `base/layout/domain` 或页面领域拆分。
4. 状态和复用逻辑放 `app/composables/`。
5. 只允许轻量 BFF 或 Nuxt server route 放 `server/api/`；核心业务 API 仍归 `services/go-app` 或 `services/laravel-app`。
6. 不在 Nuxt app 内写长期业务规则；业务规则写入 `docs/prd`、`docs/architecture` 或 `packages/contracts`。

## 4. Tailwind CSS v4 规则

Tailwind v4 使用 CSS-first 入口。每个 Nuxt app 的主 CSS：

```css
@import "tailwindcss";
@import "../../../packages/ui/tokens/theme.css";

@source "../../../packages/ui";
```

规则：

1. Tailwind 主题 token 优先沉淀到 `packages/ui/tokens/theme.css`。
2. `apps/web`、`apps/admin` 和其他 Web surface 不各自复制一套颜色、字体、间距。
3. Monorepo 共享组件或 token 需要被 Tailwind 扫描时，在 CSS 中显式 `@source` 指向 `packages/ui`。
4. 如果项目配置了 workspace alias，可以把相对路径替换成包名导入，但必须在 package 名和 tsconfig/vite alias 中同步声明。
5. 默认不创建旧式 `tailwind.config.js`；只有插件、preset 或第三方生态确实需要时才加，并写 ADR。

## 5. Nuxt 配置规则

Nuxt app 默认使用 Tailwind 官方 Vite 插件：

```ts
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "{{DATE}}",
  css: ["~/assets/css/main.css"],
  vite: {
    plugins: [tailwindcss()],
  },
});
```

如果 Nuxt 或部署环境对 Vite 插件有兼容问题，可以退回 `@tailwindcss/postcss`，但必须写入 ADR 和 Agent 日志。

## 6. 共享 UI 与契约

```text
apps/web        -> packages/ui/web
apps/web        -> packages/ui/tokens
apps/admin   -> packages/ui/web
apps/admin   -> packages/ui/tokens
apps/*          -> packages/contracts
packages/ui/*   -/-> services/*
packages/ui/*   -/-> apps/* business API
```

规则：

1. `packages/ui/tokens` 放 Tailwind v4 CSS-first token。
2. `packages/ui/web` 放 Nuxt/Vue/Web UI 组件。
3. `packages/ui/mobile` 放 React Native UI 组件。
4. Nuxt app 的 API client 从 `packages/generated/ts` 或 OpenAPI 生成类型读取。
5. 不能在页面内写静态假数据冒充接口完成。
6. SEO异常验证、下载渠道、CMS 配置、表单提交都要有契约或明确占位原因。

## 7. 脚本约定

每个 Nuxt app 至少提供：

```json
{
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "generate": "nuxt generate",
    "preview": "nuxt preview",
    "typecheck": "nuxt typecheck",
    "lint": "eslint .",
    "test": "vitest run"
  }
}
```

根目录 CI 可按路径触发：

```text
apps/web/**  -> pnpm --filter web lint/typecheck/test/build
apps/admin/** -> pnpm --filter admin lint/typecheck/test/build
packages/ui/**   -> pnpm --filter web build + pnpm --filter admin build
```

## 8. 验收门禁

Nuxt Web 任务必须在 Agent 日志写：

1. PRD、营销目标或页面目标。
2. UI 验收模式。
3. `375x812`、`768x1024`、`1440x900` 截图或项目指定视口。
4. SEO异常验证 title、description、canonical、Open Graph 或不涉及原因。
5. 下载渠道或表单/API 状态。
6. `pnpm --filter <app> build`、`typecheck`、关键 Playwright 验收结果。

大流量阶段还必须补：

1. CDN、缓存、图片优化。
2. SSR/SSG/ISR 或静态生成策略。
3. Web 性能指标，如 LCP、CLS、TTFB。
4. 回滚和灰度发布方案。
