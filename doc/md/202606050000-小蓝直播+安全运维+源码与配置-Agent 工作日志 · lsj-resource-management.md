---
id: "doc-aca8c462758d"
title: "Agent 工作日志 · lsj-resource-management"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-lsj-resource-management.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-lsj-resource-management.md"
sourceSha256: "d9fd01fb1f05d7953839697130fccc1fff1424500605b797c1ddf6b43ff74012"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-resource-management

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-lsj-resource-management.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：新增后台 LSJ 资源管理页

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-920
- 设计图：不涉及
- 接口/契约：`docs/api/openapi.yaml` 现有 `GET /api/v1/admin/sports-live`、`POST /api/v1/admin/sports-live/play`
- AI/工具控制文件：`AGENTS.md`、`apps/admin/CLAUDE.md`

## 本次目标

1. 在后台「直播管理」下新增「LSJ资源管理」菜单。
2. 复用现有 LSJ admin 接口查询赛事、线路。
3. 支持 m3u8 只读预览，不在该页面绑定赛事。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/router/routes/modules/live.ts` | 新增 LSJ 资源管理路由和菜单 |
| `apps/admin/src/views/live/lsj-resources.vue` | 新增只读资源页，展示 LSJ 赛事/线路并预览 m3u8 |
| `apps/admin/src/locales/langs/zh-CN/page.json` | 新增中文菜单文案 |
| `apps/admin/src/locales/langs/en-US/page.json` | 新增英文菜单文案 |
| `apps/admin/src/locales/langs/zh-CN/lsjResource.json` | 新增页面中文文案 |
| `apps/admin/src/locales/langs/en-US/lsjResource.json` | 新增页面英文文案 |
| `docs/prd/modules/kickoff-admin.md` | 新增 ADM-920 需求行与接口说明 |

## 核心决策

1. 不新增后端接口，直接复用已存在的 LSJ 查询和 play 接口。
2. 页面按「每条线路一行」展示，方便运营直接筛选和预览。
3. 页面保持只读，不提供赛事绑定按钮，避免和赛事管理流程混淆。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-920 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 未新增契约；复用 `adminSportsLiveSearch`、`adminSportsLivePlay` |
| 不涉及契约的原因 | 现有接口已经满足查询 LSJ 赛事/线路和获取 m3u8 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响；只读页面 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否；这是第三方直播源只读资源检索和预览入口 |
| 涉及能力 | 权限安全、第三方资源可观测性 |
| 当前 MVP 边界 | 只做查询和预览，不做绑定和批量检测 |
| 高风险触发项 | 权限；仅 super_admin 可见 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 仅影响 admin 静态前端构建 |
| 密钥 | 不新增配置，不暴露 LSJ appid/appkey |
| 观测 | 不新增日志指标 |
| 回滚 | 回滚本次 admin 路由和页面即可 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `npm run check:prd` | 通过 |
| `npm run check:completion-claim` | 通过 |
| `npm run check:engineering-standards` | 通过 |
| `npm run check:capability-gates` | 通过 |
| `git diff --check` | 通过 |
| `pnpm --filter @kickoff/admin build:stg` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 不涉及 |
| 页面截图 | 未采集；本次通过 typecheck 和 stg build 验证 |
| API 接口路径 | `GET /api/v1/admin/sports-live`、`POST /api/v1/admin/sports-live/play` |
| 后台权限与审计 | 路由仅 `super_admin` 可见；页面无写操作 |
| 与设计图主要偏差 | 不涉及 |
| 合入判断 | 待 reviewer/owner 确认 |

## 风险与待办

1. m3u8 能否播放取决于 LSJ 返回地址、浏览器 HLS 能力和跨域策略。
2. 如果后续需要在资源页直接绑定赛事，应另开需求，避免和现有赛事管理流程混淆。

## 交接说明

1. 菜单路径为 `/lsj-resources`，显示在「直播管理」下。
2. 页面使用 hls.js 预览 m3u8；无法播放时仍可复制主/备线路 URL。
3. 该页面不会保存任何 LSJ 绑定信息。
