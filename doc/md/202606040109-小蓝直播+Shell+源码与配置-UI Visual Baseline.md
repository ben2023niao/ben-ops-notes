---
id: "doc-fa390f50f9da"
title: "UI Visual Baseline"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/qa/ui-visual-baseline.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/qa/ui-visual-baseline.md"
sourceSha256: "044aa24fba37946c55f72b15217a5141484f7325785e2b5c057cf5e183e8173b"
sourceSystem: "project-doc"
---

# UI Visual Baseline

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/qa/ui-visual-baseline.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文定义 UI 验收的项目级证据要求。不同项目可以通过 `project.config.json` 选择不同 `designMode`，但不能把没有截图、没有交互证据、没有 API 状态的页面标记为完成。

## 1. Design Modes

| Mode | 是否需要设计源 | 是否需要截图 | 是否需要视觉 diff | 说明 |
| --- | --- | --- | --- | --- |
| `no-design-mvp` | 否 | 至少关键视口截图 | 否 | 快速 MVP，无设计源时使用。 |
| `wireframe` | 线框或草图 | 是 | 可选 | 用于内部工具或低视觉风险页面。 |
| `reference-style` | 参考页或设计图 | 是 | 建议 | 用于官网、Web、营销页、常规 App 页面。 |
| `strict-design` | 是 | 是 | 必须 | 用于明确设计图还原或 App Store 上架级页面。 |

## 2. Viewport Matrix

默认视口矩阵：

```text
375x812
390x844
768x1024
1440x900
```

移动 App Web preview 至少覆盖 `375x812` 和 `390x844`。

官网、PC Web、后台至少覆盖 `1440x900` 和 `768x1024`。

## 3. Completion Gate

页面完成必须有：

1. PRD 或任务来源。
2. OpenAPI / Event / mock 原因。
3. 页面截图路径。
4. 视口尺寸。
5. 红蓝对抗结论。
6. 未完成事项。

`strict-design` 页面还必须补视觉 diff / visual diff 或逐项设计矩阵结论。

## 4. Executable Evidence

视觉证据必须登记到：

```text
docs/qa/ui-visual-evidence.json
```

并通过：

```bash
npm run check:ui-visual
```

该门禁会读取 baseline/current 截图，校验视口矩阵，计算像素级 visual diff，并在差异超过 `maxDiffRatio` 时失败。

如果需要生成 diff 图片，先运行：

```bash
UI_VISUAL_WRITE_DIFFS=1 npm run check:ui-visual
```

不允许只在 Agent 日志里写“已对齐设计图”而没有截图和 manifest 证据。
