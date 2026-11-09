---
id: "doc-cf4636b70e5b"
title: "2026-06-02 Admin Streamer Avatar Upload"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-streamer-avatar-upload.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-admin-streamer-avatar-upload.md"
sourceSha256: "da99bcf8277559eb40c258d9a2d28a6ec41e91e23b11f2ff2d075abdd2e4c135"
sourceSystem: "project-doc"
---

# 2026-06-02 Admin Streamer Avatar Upload

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD-2026-06-02%20Admin%20Streamer%20Avatar%20Upload.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

## Task

用户反馈主播头像不应让运营手动粘贴 URL，应按上传控件交互上传。

## Changes

- 主播新建/编辑弹窗移除 `avatar_url` 文本输入。
- 新增头像上传控件，复用后台通用上传接口 `/api/v1/admin/upload`，scene=`streamer_avatar`。
- 上传成功后自动保存返回 URL，并在提交主播创建/编辑时写入 `avatar_url`。
- 补充主播 API 类型字段，支持编辑回填 `bio`、`commission_rate` 等字段。

## Verification

- `pnpm --filter @kickoff/admin typecheck`
