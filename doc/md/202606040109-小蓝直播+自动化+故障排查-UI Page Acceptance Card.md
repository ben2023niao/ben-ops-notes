---
id: "doc-4cfb91c30bd9"
title: "UI Page Acceptance Card"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/templates/ui-page-acceptance-card.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/templates/ui-page-acceptance-card.md"
sourceSha256: "ac5ed0c935d6fcb535bef80bb7c2ae5a237c3ce4df2cae3da0bbd219261597b7"
sourceSystem: "project-doc"
---

# UI Page Acceptance Card

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/templates/ui-page-acceptance-card.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

每个需要精细 UI 验收的页面都应填写一张卡。快速 MVP 且没有设计源的项目，可以选择 `no-design-mvp`，但必须写清楚验收模式，不能把未验收页面说成已完成。

## 页面

- App / Surface：
- Route / Screen：
- PRD 来源：
- OpenAPI / Event 来源：
- UI 验收模式：`no-design-mvp` / `wireframe` / `reference-style` / `strict-design`

## 设计源

- 设计图 / Figma / 参考页：
- 设计源缺失原因：
- 允许的视觉偏差：

## 截图基线

本页对应的结构化证据必须同步写入：

```text
docs/qa/ui-visual-evidence.json
```

| Viewport | Baseline Screenshot | Current Screenshot | Visual Diff | 结论 |
| --- | --- | --- | --- | --- |
| 375x812 |  |  |  |  |
| 390x844 |  |  |  |  |
| 768x1024 |  |  |  |  |
| 1440x900 |  |  |  |  |

## 交互验收

| 交互 | API / 状态 | 证据 | 结论 |
| --- | --- | --- | --- |
| 点击 |  |  |  |
| 输入 |  |  |  |
| 下拉刷新 / 加载更多 |  |  |  |
| 异常态 / 空态 |  |  |  |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 |  |
| 红队质疑 |  |
| 合入判断 |  |

## 自动化门禁

- `npm run check:ui-visual-validator`
- `npm run check:ui-visual`
