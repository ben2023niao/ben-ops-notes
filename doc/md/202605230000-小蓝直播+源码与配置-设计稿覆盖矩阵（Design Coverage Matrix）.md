---
id: "doc-246b86f32be1"
title: "设计稿覆盖矩阵（Design Coverage Matrix）"
date: "2026-05-23T00:00:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/design/design-coverage-matrix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/design/design-coverage-matrix.md"
sourceSha256: "b4da841f29c82b42a0b98115e0c8abd091c43a15ff4f08ebf2074eb2b4b7928e"
sourceSystem: "project-doc"
---

# 设计稿覆盖矩阵（Design Coverage Matrix）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605230000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-%E8%AE%BE%E8%AE%A1%E7%A8%BF%E8%A6%86%E7%9B%96%E7%9F%A9%E9%98%B5%EF%BC%88Design%20Coverage%20Matrix%EF%BC%89.md)

> 整理日期：2026-05-23 00:00｜日期依据：正文日期

<!-- DESIGN_COVERAGE_EMPTY_OK：v1 不要求矩阵有行；validator 见到本标记后允许空表 -->

> **v1 状态**：`project.config.json` 中 `quality.requiresDesignMatrix = false`，本矩阵当前**仅作占位**保证 `scripts/validate-design-coverage.py` 不阻塞 framework-check。
>
> 设计稿落入 `docs/design/` 之后再按下列表格格式补充行。

## 字段定义

| 列 | 说明 |
|---|---|
| 设计稿 | 相对路径，反引号包裹（例：`docs/design/home-banner.png`） |
| 尺寸 | `WIDTHxHEIGHT`（例：`1920x1080`） |
| Surface | web / h5 / admin / streamer |
| 责任人 | `@kickoff/xxx` |
| 状态 | 已对齐 / 部分对齐 / 偏离 / 未实现 / 资源 / 待确认 |
| 实现路由 | 对应代码路由或页面（例：`#page-home` / `apps/admin/.../HomeView.vue`） |
| 红蓝评审 | yes / no / pending |

## 矩阵

| 设计稿 | 尺寸 | Surface | 责任人 | 状态 | 实现路由 | 红蓝评审 |
|---|---|---|---|---|---|---|

> v1 没有正式设计稿入库（原型由 HTML 直接评审，见 `2026.05.23迭代版.html`），表格暂空。
> 待 v1.1 进入 Figma / Sketch 阶段后逐行补充。
