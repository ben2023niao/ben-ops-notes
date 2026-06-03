---
id: "doc-e2d64efdd530"
title: "OpenAPI 兼容性基线"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-baseline.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-baseline.md"
sourceSha256: "58f8fbd654e730d509d9262bffe07f0327a3acfde0cfe22c2c44e9dbbec15056"
sourceSystem: "project-doc"
---

# OpenAPI 兼容性基线

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/api/openapi-baseline.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

为避免 break C 端 / admin 前端，OpenAPI 变更必须做兼容性 diff。
当前基线：`docs/api/openapi.yaml` HEAD。

升级 baseline 时必须：
1. 在 MR 描述里说明变更是否 breaking
2. 通过 `python3 scripts/validate-openapi.py` 检查
3. 更新本文件锚定的 commit
