---
id: "doc-5f2764b8d71b"
title: "bug-28273-frontend-live-state-sync"
date: "2026-06-05T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-frontend-live-state-sync.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-frontend-live-state-sync.md"
sourceSha256: "355aa3acb756accff6e8ca67fb3dca66910e951f0225a50f688a987daf352988"
sourceSystem: "project-doc"
---

# bug-28273-frontend-live-state-sync

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-05-bug-28273-frontend-live-state-sync.md`

> 整理日期：2026-06-05 00:00｜日期依据：文件名日期

日期：2026-06-05
Agent：Codex
任务：补齐 Bug 28273 前端直播状态同步

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-912
- 接口/契约：`POST /api/v1/admin/rooms/{id}/force-end`、`GET /api/v1/live/room/{id}`、`GET /api/v1/streamer/me/rooms`
- 其他：Zandao Bug 28273

## 本次目标

1. H5 已打开直播间收到后端 `room.status.ended` 后立即显示下播。
2. 主播端房间列表和开播工作台不要长期使用旧的 `LIVE` 缓存。
3. 不改变 API 契约，只消费现有字段和事件。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/web/app/components/live/ClientLiveRoom.vue` | 监听 `room.status.ended/live` WS 事件，更新本地房间状态和观看人数 |
| `apps/live-host/app/composables/useStreamerRooms.ts` | 房间列表缓存增加 5 秒 TTL，`ensureRoom` 过期后强制刷新 |
| `apps/live-host/app/pages/index.vue` | 主播端房间列表每 5 秒刷新一次房间状态 |
| `apps/live-host/app/pages/studio/[room_id].vue` | 开播工作台每 5 秒强刷房间状态，发现 ENDED 后停止本地推流/节目预览并提示 |

## 核心决策

1. 不新增后端事件和接口，前端只消费现有 `room.status.ended` 与房间列表状态。
2. H5 走 WS 实时更新，避免 SSR 缓存导致已打开页面继续显示 `LIVE`。
3. 主播端没有房间级 WS，采用 5 秒轮询作为 MVP 下的保守方案。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-912 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 契约不变；继续使用 `room.status.ended`、`GET /api/v1/streamer/me/rooms` |
| 项目验收证据 | `docs/qa/project-acceptance.md` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 只修正前端读取/缓存策略，不新增字段 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响 |
| 规范例外与原因 | H5 typecheck 受本地依赖缺失阻塞；整包 H5 lint 存在既有错误，已对本次文件定向 lint |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否 |
| 涉及能力 | 实时状态同步 / 缓存一致性 |
| 当前 MVP 边界 | 主播端用短轮询兜底，后续可迁移到主播端 WS 房间状态事件 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `pnpm --filter @kickoff/live-host typecheck` | 通过 |
| `pnpm --filter @kickoff/web exec eslint app/components/live/ClientLiveRoom.vue` | 通过 |
| `pnpm --filter @kickoff/live-host exec eslint app/composables/useStreamerRooms.ts 'app/pages/index.vue' 'app/pages/studio/[room_id].vue'` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 阻塞：本地缺 `@nuxt/fonts` / `@nuxtjs/sitemap` |
| `pnpm --filter @kickoff/web lint` | 阻塞：整包存在既有 no-undef / vue lint 错误，非本次文件 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | H5 已打开页面可通过 WS 事件切换到 ENDED；主播端通过短轮询刷新后台权威状态 |
| 红队质疑 | 主播端轮询不是最终实时架构，网络异常时最多停留到下一次成功刷新 |
| 合入判断 | MVP 可合入；后续可升级为主播端 WS 状态频道 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 不涉及，状态同步修复 |
| 目标视口 / 设计尺寸 | 375x812 手机视口、1440x900 桌面视口；未改布局尺寸 |
| 真实手机视口 | 375x812；未跑浏览器截图，逻辑修复以接口/事件同步为主 |
| 桌面/平板视口 | 1440x900；未跑浏览器截图，逻辑修复以接口/事件同步为主 |
| 响应式验收 | responsive 逻辑改动，不改布局；H5 移动和桌面共用 `ClientLiveRoom` 状态源 |
| 页面截图 | 未生成 screenshot .png；未改视觉布局 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` 未新增记录，原因：本次不改视觉布局 |
| API 接口路径 | `GET /api/v1/live/room/{id}` / `GET /api/v1/streamer/me/rooms` |
| SEO异常验证/分享/下载渠道 | 不涉及 SEO异常验证、title、description 修改 |
| console 是否无 error | 未跑浏览器，已做定向 lint 和 live-host typecheck |
| 合入判断 | 可合入逻辑修复 |

## 风险与待办

1. 主播端轮询会带来少量请求；当前房间列表规模小，5 秒间隔可接受。
2. 更长期方案是给主播端增加房间状态 WS 频道，避免轮询。

## 交接说明

下一位 Agent 或工程师需要知道：

1. API 契约没有变化，前端读到旧状态的核心原因是本地缓存和未消费 WS 事件。
2. H5 已打开页面现在依赖 `room.status.ended` 立即切换下播遮罩。
3. 主播端工作台被后台强制下播后会本地停止 publisher/program player/mixer，并显示提示。
