---
id: "doc-4f83173643fb"
title: "Agent 工作日志 · streamer-account-reset"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-streamer-account-reset.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-streamer-account-reset.md"
sourceSha256: "5b69859a18b2111d829f76c0ac14e242b64971812648bdd9d8590247e36bbdd5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · streamer-account-reset

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606050000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20streamer-account-reset.md)

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：主播编辑账号只读展示与重置密码

## 输入资料

- 需求 ID：`ADM-310`
- 页面：后台主播管理 `#/streamers`
- 接口：`GET/PUT /api/v1/admin/streamers/{id}`、`POST /api/v1/admin/streamers/{id}/reset-password`

## 修改内容

1. 后台主播编辑弹窗不再把登录账号作为可编辑表单项。
2. 编辑模式展示只读登录账号，并提供复制账号按钮。
3. 编辑模式提供重置密码按钮，后端生成一次性临时密码并返回给运营复制。
4. 后端主播列表/详情返回 `username`，供后台展示。
5. 新增主播重置密码接口，写审计日志，并按 `streamer` subject 撤销旧登录态。
6. 编辑主播时 `contact_phone` 支持保存并写入脱敏电话。
7. JWT 全局撤销 key 改为按 subject 隔离，避免 C 端用户和主播 ID 相同时互相误伤。
8. 同步 OpenAPI、contract 与 PRD 口径。

## 验证记录

- `go test ./internal/service/admin ./internal/http/adminapi ./internal/http/middleware`
- `pnpm --filter @kickoff/admin typecheck`
- `npm run check:openapi`
- `npm run check:contract`
- `npm run check:prd`
- `npm run check:engineering-standards`
- `npm run check:capability-gates`
- `npm run check:completion-claim`
- `git diff --check`
