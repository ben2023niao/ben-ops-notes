---
id: "doc-232f5637e8f9"
title: "Agent 工作日志 · admin-predict-create-dialog-help"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-predict-create-dialog-help.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-predict-create-dialog-help.md"
sourceSha256: "964ae5f2047089811b024a89947916d1f7131d2d632af699678eaea3a89e97fb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-predict-create-dialog-help

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-predict-create-dialog-help.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：后台新建竞猜活动弹窗放大并补充运营说明

## 输入资料

- PRD：`docs/prd/modules/kickoff-predict.md`
- 需求 ID：PRED-001, PRED-004, PRED-009
- 后台页面：`apps/admin/src/views/predict/PredictListView.vue`

## 本次目标

1. 放大“新建竞猜活动”弹窗，避免选项配置区域拥挤。
2. 给运营说明“选项”的含义：H5 用户实际点击押注的候选结果。
3. 按不同类目给出可套用示例，降低运营填错概率。

## 修改内容

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/views/predict/PredictListView.vue` | 弹窗宽度改为 960px，表单改为左侧配置 + 右侧说明；新增胜负/比分/射手/自定义类目说明、示例选项、套用示例按钮和选项填写提示 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `cd apps/admin && npm run build` | 通过 |
| `git diff --check` | 通过 |

## 风险与待办

1. 本次只改后台管理 UI，不改 H5 前台代码。
2. 竞猜实际下注提交链路由 H5 前端接入 `POST /api/v1/predict/bet`，本次未涉及。
