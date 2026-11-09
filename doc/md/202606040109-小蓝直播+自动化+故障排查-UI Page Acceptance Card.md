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

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2B%E8%87%AA%E5%8A%A8%E5%8C%96%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-UI%20Page%20Acceptance%20Card.md)

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
