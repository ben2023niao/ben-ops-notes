---
id: "doc-85595f6e00f2"
title: "Agent 工作日志 · web-bet-panel-wireup"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-bet-panel-wireup.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-bet-panel-wireup.md"
sourceSha256: "40096b2c867c96136bde38c56b4fe0927549468c16e64e91cb0230e1b03173d5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · web-bet-panel-wireup

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20web-bet-panel-wireup.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：claude (web)
任务：投注弹窗（BetPanel）未触发投注接口 —— 三处全接 placeBet

## 输入资料

- PRD：prd 稿 https://xiaolankanyeqiu.netlify.app/
- 需求 ID：竞猜投注（placeBet / POST /api/v1/predict/bet）
- 接口/契约：`packages/contracts` 已有 `POST /api/v1/predict/bet`（PlaceBetRequest）、`GET /api/v1/live/room/{id}/activities`（RoomActivities），本次未改契约
- 其他：dev 后端经 Nuxt 代理（NUXT_PUBLIC_API_BASE → api-dev），有真实 OPEN 活动 `21086780010790913`

## 本次目标

1. 定位「投注弹窗不触发接口」根因
2. 竞猜页 / 首页热门竞猜 / 直播间三处全部接通 placeBet
3. 单测 + 浏览器验证 POST 实际发出且 body 正确

## 修改文件

| 文件 | 说明 |
| --- | --- |
| shared/types/activity.ts | ActivityOption 加 optionKey；新增 BetContext（activityId+optionKey） |
| shared/types/room.ts | LivePredictOption 加 optionKey；PredictCard 加 activityId |
| app/utils/adapters.ts | toActivityVM 透传 option_key；新增 toLivePredictCard（含空卡降级） |
| app/utils/adapters.test.ts | 补 option_key 透传 + toLivePredictCard 用例（共 9 测全过） |
| app/components/live/BetPanel.vue | 加 submitting prop（请求中禁用/改文案）；submit 不再自动 close，交父级成功后关闭 |
| app/pages/predict.vue | onPick 带 activity.id+option.optionKey；绑 @submit→登录校验→placeBet→成功 toast+关闭 |
| app/pages/index.vue | 同上；onPick 直接收 BetContext |
| app/components/home/HotPredict.vue | pick 事件带 item.id+opt.pick（原来丢了 ID） |
| app/components/live/ClientLiveRoom.vue | 客户端拉 getRoomActivities，toLivePredictCard 填 predictSeed.ing |
| app/components/live/desktop/LiveRoomDesktop.vue | 绑 @submit→placeBet；BetContext 统一类型 |
| app/components/live/mobile/LiveRoomMobile.vue | 同上 |
| app/components/live/mobile/shared/MobilePredictionCard.vue | open-bet 带 activityId+optionKey；空卡禁用投注按钮 |
| LivePlayerPC.vue / MobileTheaterShell.vue / MobileImmersiveShell.vue | open-bet 事件类型改为 BetContext |

## 核心决策

1. 根因分三层：① 4 个挂载处只绑 @close 从不绑 @submit（直接原因）；② betContext 一路丢 activity_id/option_key；③ 直播间竞猜卡原为 mock 种子（predictSeed=EMPTY），无契约来源。
2. 直播间走「三处全接」：ClientLiveRoom 客户端拉 `/live/room/{id}/activities`，映射真实活动；无活动/拉取失败 → 空卡 → 投注按钮禁用（优雅降级，不写转换器适配）。
3. BetPanel 保持纯展示：只 emit submit + amount，activity_id/option_key 由父级 betContext 持有；关闭与 toast 由父级在 placeBet 成功后控制，失败保留面板便于重试。
4. 未碰后端：placeBet 契约已存在，纯前端事件链 + 数据透传问题。

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 三处浏览器实测均发出 POST /api/v1/predict/bet，body 含正确 activity_id/option_key/amount_diamond，带 Idempotency-Key 头；成功后面板关闭 |
| 红队质疑 | dev 后端无真实直播间（live-rooms 空、r-101 非法 room_id），直播间端到端用 page.route mock getLiveRoom+getRoomActivities 验证；真实房间未覆盖 |
| 合入判断 | 允许合入（前端事件链已通，契约未动） |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| node --test app/**/*.test.ts | 9 pass / 0 fail |
| nuxt typecheck | 无新增错误（adapters.ts:53-60 与 nuxt.config.ts:58 为既有，非本次改动） |
| 浏览器 /predict | POST bet body `{activity_id:21086780010790913,option_key:opt_1,amount_diamond:500}` 200 |
| 浏览器首页热门竞猜 | POST bet body `{...,opt_1,500}` 200 |
| 浏览器 /live/r-101（mock 房间+活动） | POST bet body `{...,opt_1,1000}` 200，Idempotency-Key 存在，成功后面板关闭 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| API 接口路径 | POST /api/v1/predict/bet；GET /api/v1/live/room/{id}/activities |
| mock/fallback 状态与原因 | 直播间无主推活动 → 空卡，投注按钮禁用（canBet=false） |
| console 是否无 error | 投注流程无新增 error |
| 合入判断 | 允许合入 |

## 风险与待办

1. 直播间端到端未在真实房间上验证（dev 无直播间数据）；上真房间后回归一次。
2. 打赏面板（TipPanel）同样是 mock——只 emit send 不调 `tip()` 接口；本次未动，按需另开任务。
3. 成功后未刷新「我的竞猜」列表（仅 toast+关闭），如需即时反映需在 predict.vue 重拉 getMyBets。

## 交接说明

1. BetContext（shared/types/activity.ts）是三处统一的投注上下文类型，新增投注入口复用它。
2. 直播间竞猜数据来自 ClientLiveRoom 拉取的 RoomActivities.main，经 toLivePredictCard 映射；空卡 activityId='' 即禁用投注。
3. placeBet 失败由 useApi 自动弹错误 toast，父级 catch 仅保留面板。
