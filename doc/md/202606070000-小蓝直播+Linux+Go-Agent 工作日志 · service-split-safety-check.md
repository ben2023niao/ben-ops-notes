---
id: "doc-f819c8ccefc4"
title: "Agent 工作日志 · service-split-safety-check"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Linux", "Go", "Nginx", "MySQL", "Redis", "监控告警", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-split-safety-check.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-service-split-safety-check.md"
sourceSha256: "142e449ba499ca856e33e2b43b392c63bbbd8fbef332dbea3da9143a9d2740ca"
sourceSystem: "project-doc"
---

# Agent 工作日志 · service-split-safety-check

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BLinux%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20service-split-safety-check.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：服务拆分完整性与业务影响检查

## 输入资料

- 需求 ID：LIVE-003、LIVE-012、ADM-908、ADM-912
- 接口/契约：`docs/api/websocket-current.md`、`docs/api/conventions.md`、`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 检查 API / WS / Worker 拆分后是否漏路由、漏部署、漏 health。
2. 确认公网 REST、Public WS、Admin Web、H5 Web 不出现 404/502。
3. 发现会影响后台业务的点直接修复。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-908、LIVE-003、LIVE-012、ADM-912 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`；兼容门禁引用：`docs/prd/modules/admin.md` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| OpenAPI / Event / DTO | `docs/api/websocket-current.md`、`docs/api/conventions.md`、`docs/api/openapi.yaml`；兼容门禁引用：`packages/contracts/openapi` |
| ownerService | `services/go-app` |
| 权限 / 审计 | 房间监控 WS 只读订阅，不新增写操作；沿用 Admin JWT + 房间权限校验，不新增 audit 写入点 |

## 发现与修复

| 项目 | 结论 |
| --- | --- |
| Public REST | `/healthz`、`/readyz`、`/api/v1/meta/feature-flags`、`/api/v1/home/live-rooms` 均返回 200 |
| Public WS | `/ws/v1/client`、`/ws/v1/live/{id}` 握手返回 101 |
| Admin Web | 首页返回 200 |
| H5 Web | 首页返回 200 |
| Admin 房间监控 WS | 原 `/ws/v1/admin/rooms/{id}/danmaku` 在公网 admin 域名返回 SPA HTML，说明 nginx 未代理 `/ws` |

为避免依赖运维手工改 nginx，本次增加 admin WS 同源推荐路径：

- 后端新增：`GET /api/v1/admin/ws/rooms/:id/danmaku`
- 前端改用：`wss://admin-dev.../api/v1/admin/ws/rooms/{id}/danmaku?敏感凭据：[已脱敏]
- 旧路径 `/ws/v1/admin/rooms/:id/danmaku` 保留兼容本地代理和历史文档。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./cmd/api ./cmd/ws ./cmd/worker ./internal/http/router ./internal/worker` | 通过 |
| `go test ./cmd/admin ./cmd/api ./cmd/ws ./cmd/worker ./internal/http/router ./internal/worker` | 通过 |
| `pnpm --filter @kickoff/admin build:stg` | 通过 |
| `curl https://api-dev.../healthz` | 200 |
| `curl https://api-dev.../readyz` | 200，MySQL / Redis ok |
| Public WS handshake `/ws/v1/client` | 101 |
| Admin legacy WS path probe | 返回 SPA HTML，已通过新 `/api` 路径规避 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 不涉及，本次只修改后台房间监控 WS 连接地址 |
| 设计图尺寸 | 不涉及；目标检查尺寸记录为 1440x900 |
| 目标视口 | 1440x900 现有后台桌面 Web 视口；无布局变更 |
| 真实手机视口 | 375x812 不涉及，后台桌面管理页面；本次不改变移动布局 |
| 桌面/平板视口 | 1440x900 现有后台桌面 Web 视口；无布局变更 |
| 响应式验收 | 375x812 手机视口、1440x900 桌面视口均不涉及布局实现变更；本次只改后台 WS URL 生成 |
| SEO异常验证 / meta | 不涉及 SEO异常验证、title、description 变更 |
| 页面截图 | 不涉及，无视觉变更；未生成 `.png` 截图，未使用 Playwright screenshot |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json`；无视觉变更，不新增 screenshot 记录 |
| API 接口路径 | `GET /api/v1/admin/ws/rooms/{id}/danmaku` |
| console 是否无 error | 未做浏览器登录态验证；已通过 `pnpm --filter @kickoff/admin build:stg` |
| 合入判断 | 允许合入，修复公网 admin 域名 `/ws` 未反代导致的监控 WS 不可用风险 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队 | 新路径复用已有 `/api` 反代，避免要求测试机 nginx 追加 `/ws` 规则，降低部署风险 |
| 红队 | 如果前端继续使用旧 `/ws/v1/admin/...`，公网 admin 域名会返回 SPA HTML；因此前端必须切到 `/api/v1/admin/ws/...` |
| 合入判断 | 允许合入 |

## 风险与待办

1. 仍建议运维后续给 admin 域名补 `/ws` 代理或统一移除旧路径依赖。
2. 我没有 SSH / GitLab API 权限，无法直接查看测试机 `systemctl status kickoff-*` 或 deploy job 日志。
