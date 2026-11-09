---
id: "doc-44ac462afd57"
title: "2026-06-02 System Config Description Wrap"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-description-wrap.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-system-config-description-wrap.md"
sourceSha256: "1b9732d149d3cfc674a84296ff733845868acbe23cb460043daf35e074b3d116"
sourceSystem: "project-doc"
---

# 2026-06-02 System Config Description Wrap

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-2026-06-02%20System%20Config%20Description%20Wrap.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈系统配置说明对运营不清晰，表格里说明被省略号截断，无法直接理解 JSON 配置在前端的表现。

## Changes

- 系统配置表 `说明` 列改为完整多行展示，不再省略。
- 充值配置说明改成运营可读口径：
  - 快捷金额数组会说明前端显示为多个充值按钮。
  - 手续费率、兑换比例、最小/最大金额给出填写示例。
  - 精确充值包说明普通场景填 `[]`，特殊套餐给出 JSON 示例。
- 新增 `000036_improve_system_config_descriptions`，更新已部署环境现有配置说明。
- 同步更新 `000031` seed，保证新环境默认说明一致。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
- `go test ./services/go-app/internal/service/admin`
