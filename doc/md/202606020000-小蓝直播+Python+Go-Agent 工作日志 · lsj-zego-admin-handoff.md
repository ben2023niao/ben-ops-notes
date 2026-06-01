---
id: "doc-deef9a046e6d"
title: "Agent 工作日志 · lsj-zego-admin-handoff"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-admin-handoff.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-admin-handoff.md"
sourceSha256: "f09fce2b9cfc03172633b10e6a9db0f999af57a47fb573bb073e3b0d222a5373"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-zego-admin-handoff

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-lsj-zego-admin-handoff.md`

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：LIVE-101 LSJ + ZEGO 节目流后台入口与前端对接契约收口。

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`；AI gate legacy alias：`docs/prd/modules/admin.md` 对应当前 `kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`docs/api/admin-api.md`
- 团队可读文档：`docs/api/streamer-lsj-zego-cloud-player.md`
- 验收证据：`docs/qa/acceptance-evidence.md`、`docs/qa/project-acceptance.md`
- UI 视觉证据 manifest：`docs/qa/ui-visual-evidence.json`

## 本次目标

1. 检查后端“后台绑定赛事 LSJ 源 -> 房间开播准备 -> 返回 match_stream_id -> 主播回写 mixed_stream_id”是否已有契约和实现。
2. 补齐后台管理入口，让运营能在页面完成赛事源绑定和节目流准备。
3. 更新主播端/C 端前端对接说明，明确每个端只消费自己需要的流 ID。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/api/modules/match.ts` | 新增 LSJ 源绑定/查询 API client 类型。 |
| `services/go-app/internal/http/adminapi/sports_live_source.go` | 新增后台 LSJ 上游直播查询 handler。 |
| `services/go-app/internal/http/router/admin.go` | 挂载 `GET /api/v1/admin/sports-live` 后台查询接口。 |
| `apps/admin/src/api/modules/room.ts` | 新增房间节目流查询和 prepare-live API client 类型。 |
| `apps/admin/src/views/matches/list.vue` | 新建赛事时可选绑定 LSJ 上游直播源；赛事列表使用「编辑赛事」统一编辑赛事基础信息和 LSJ 源。 |
| `apps/admin/src/views/rooms/list.vue` | 新建房间的关联赛事改为下拉选择已绑定 LSJ 源的赛事，并提示新建房间不会创建云播放器。 |
| `apps/admin/src/views/rooms/detail.vue` | 房间详情新增「节目流」区域，可刷新、开播准备、强制重建，并展示 `match_stream_id`、`player_id`、`mixed_stream_id`。 |
| `apps/admin/src/router/routes/modules/matches.ts` | 新增顶级「赛事管理」菜单，承载赛事列表、比分和 LSJ 源绑定。 |
| `apps/admin/src/router/routes/modules/contents.ts` | 从「内容管理」移除赛事入口，避免赛事运营能力被归类为内容配置。 |
| `apps/admin/src/locales/langs/zh-CN/*.json` | 新增中文后台文案。 |
| `apps/admin/src/locales/langs/en-US/*.json` | 新增英文后台文案。 |
| `docs/api/streamer-lsj-zego-cloud-player.md` | 补充后台页面入口、Stoplight 深链和主播端/C 端交付清单。 |

## 核心结论

1. 后端契约和服务实现已存在，当前缺口是后台 UI 没有运营入口；本次已补上。
2. `match_stream_id` 由后端 prepare-live 创建 ZEGO 云播放器后返回，主播端用它拉赛事源预览。
3. 主播端只推自己的 `host_stream_id`，并用 ZEGO Web SDK 混流 `match_stream_id + host_stream_id`。
4. 主播端混流成功后回写 `mixed_stream_id`；C 端只拉最终 `mixed_stream_id`。
5. LSJ 是当前唯一赛事源；后台不开放手填 m3u8。
6. 新建房间只保存业务房间、主播、赛事和推流密钥，不调用 LSJ，也不创建 ZEGO 云播放器；创建后必须进入房间详情「节目流」点击开播准备。
7. 后台菜单调整为顶级「赛事管理 / 赛事列表」，不再放在「内容管理 / 赛事比分」。
8. 新建赛事可选绑定 LSJ 源；赛事列表行操作改为「编辑赛事」，用于编辑赛事基础信息并补充或更换 LSJ 上游直播源。
9. 「编辑赛事」和「新建赛事」保持同一组运营字段：赛事编号、阶段、轮次、主队、客队、场地、开赛时间；后端 `adminMatchUpdate` 已同步扩展这些字段。
10. 运营不再手填 `app_name` / `stream_name`；后台通过 `adminSportsLiveSearch` 展示 LSJ 上游赛事和线路，选择后系统自动保存源标识。
11. LSJ 上游状态展示为运营文案：`0=未开始`、`1=直播中`、`2=已结束`；线路只有 `is_played=1` 且带 `app_name/stream_name` 时才允许选择，避免提前绑定未进流线路。
12. 后台赛事列表返回 `has_lsj_source`；直播间新建弹窗不再逐个请求 `lsj-source` 探测，避免未绑定赛事刷屏报错，并且每次打开都会刷新赛事绑定状态。
13. 本次前端验收证据继续归档到 `docs/qa/acceptance-evidence.md` 和 `docs/qa/ui-visual-evidence.json`，页面按 no-design-mvp 模式检查。

## 接口文档深链

| 分组 | 方法与路径 | Stoplight |
| --- | --- | --- |
| 后台-赛事管理 | `PUT /api/v1/admin/matches/{id}/lsj-source` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminMatchBindLSJSource` |
| 后台-赛事管理 | `GET /api/v1/admin/sports-live` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminSportsLiveSearch` |
| 后台-赛事管理 | `GET /api/v1/admin/matches/{id}/lsj-source` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminMatchLSJSource` |
| 后台-直播间管理 | `POST /api/v1/admin/rooms/{id}/prepare-live` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminRoomPrepareLive` |
| 后台-直播间管理 | `GET /api/v1/admin/rooms/{id}/program` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminRoomProgram` |
| 主播端-推流 | `GET /api/v1/streamer/rooms/{room_id}/program` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/streamerRoomProgram` |
| 主播端-推流 | `POST /api/v1/streamer/rooms/{room_id}/mixed-stream` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/streamerRoomMixedStreamReport` |
| C 端播放 | `GET /api/v1/live/room/{room_id}/play-url` | `https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/livePlayUrl` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 本次未改表；节目流表已由 LIVE-101 后端实现提供。 |
| 账本、事务、幂等 | 不涉及资金账本；后台写操作仍走既有后端审计 `admin.match.lsj_source.bind`，主播回写走 `streamer.room.mixed_stream.report`。 |
| 权限与审计 | 后台页面调用 admin API，权限由既有 admin auth/RBAC 控制；敏感写操作审计在后端服务层完成。 |
| ownerService | `services/go-app` |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 无设计图，UI 验收模式：no-design-mvp，沿用现有 Element Plus/Vben 后台表格、弹窗、详情卡片样式。 |
| 页面截图 | `output/playwright/2026-06-02-admin-room-program-desktop.png`、`output/playwright/2026-06-02-admin-matches-mobile.png` |
| 真实手机视口 | 375x812，路由进入后台后因本地预览未接真实登录态重定向登录页；无 console error。 |
| 桌面/平板视口 | 1440x900，路由进入后台后因本地预览未接真实登录态重定向登录页；无 console error。 |
| 响应式验收 | admin build 产物可加载；新增页面代码通过 `vue-tsc` 和生产构建。 |
| 公共组件拆分 | 未新增公共组件；按现有页面局部表单/卡片模式实现。 |
| API 接口路径 | 见上方 Stoplight 深链；契约在 `docs/api/openapi.yaml` 与 `packages/contracts/openapi/v1.yaml`。 |
| SEO异常验证/分享/下载渠道 | 后台管理页面不涉及。 |
| mock/fallback 状态与原因 | 未增加前端 mock；本地截图只验证构建产物和路由壳层，真实业务接口已在 dev 服务器验证过 prepare-live。 |
| 后台权限与审计 | 调用 admin API，审计由后端写入；页面不绕过权限。 |
| 根节点是否挂载 | 通过本地 Vite preview 验证。 |
| 静态资源是否 200 | 通过本地 Vite preview 验证。 |
| console 是否无 error | Playwright 报告 0 errors，1 warning。 |
| 与设计图主要偏差 | 无设计图；按现有后台页面密度和样式实现。 |
| 合入判断 | 蓝队自检允许合入；红队主要风险是线上文档站需部署后才能看到新文档内容。 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
| `pnpm --filter @kickoff/admin build:prod` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| Playwright local preview screenshots | 通过，截图见上方路径。 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 后台页面补齐了运营闭环；前端对接文档明确了三条 ZEGO 流的职责边界。 |
| 红队质疑 | 本次未新增云播放器停止/清理入口；强制重建只结束业务 session，ZEGO 云播放器清理仍需后续 worker 或显式 stop 接口。 |
| 合入判断 | 允许合入。本次是后台入口和契约交付，不改变已跑通的后端节目流创建逻辑。 |

## 风险与待办

1. 线上文档站需要部署后，Stoplight 深链才能看到本次更新后的说明页；OpenAPI operation 已存在。
2. ZEGO 云播放器强制重建后的旧 player 清理还需要补后台 stop/worker，避免联调频繁时占用额度。
3. 主播端需确认 ZEGO Web SDK 混流输出 ID 命名规则，并在成功后调用 `streamerRoomMixedStreamReport`。

## 交接说明

1. 后台运营入口：赛事列表「编辑赛事」绑定或更换上游线路；房间详情「节目流」点击开播准备。
2. 主播端只依赖 `GET /api/v1/streamer/rooms/{room_id}/program` 和 `POST /api/v1/streamer/rooms/{room_id}/mixed-stream`。
3. C 端只依赖现有 `livePlayUrl`，赛事直播最终只播放后端返回的 `mixed_stream_id` 对应流。
