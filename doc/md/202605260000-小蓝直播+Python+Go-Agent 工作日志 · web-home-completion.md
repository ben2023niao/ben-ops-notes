---
id: "doc-d36acaad8eea"
title: "Agent 工作日志 · web-home-completion"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "CDN", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-home-completion.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-home-completion.md"
sourceSha256: "97e20917c52b839ebe8fad7af83ace0a225e2e65c3e17a38c7a019c3a8099fc6"
sourceSystem: "project-doc"
---

# Agent 工作日志 · web-home-completion

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-web-home-completion.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：首页 H5/Web 对齐 PRD 与后端契约

## 输入资料

- PRD：`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-h5.md`
- 需求 ID：HOME-002、HOME-003、HOME-004、HOME-005、HOME-006、HOME-010
- 原型：`/Users/qx/Downloads/2026.05.23迭代版.html#h5`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 核对首页 PRD、OpenAPI 与 Go 后端接口。
2. 补齐 H5/Web 首页缺失区块：赛事主视觉、今日赛程、我的竞猜和空状态。
3. 修正首页 CTA 硬编码与构建期类型错误。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/web/app/pages/index.vue` | 使用 `/home/today-matches` 驱动顶部赛事主视觉，接入 `/home/my-predicts`，渲染今日赛程和我的竞猜 |
| `apps/web/app/components/home/HeroCarousel.vue` | 移除 `/live/r-101` 硬编码，按比赛关联直播间生成 CTA |
| `apps/web/app/components/home/TodayMatches.vue` | 新增首页今日赛程区块 |
| `apps/web/app/components/home/MyPredicts.vue` | 新增首页我的竞猜区块 |
| `apps/web/app/components/home/HotPredict.vue` | 支持队旗图片和无可投注活动空状态 |
| `apps/web/app/components/home/LiveRooms.vue` | 增加无直播空状态 |
| `services/go-app/internal/http/public/home.go` | 对齐首页 live-rooms/hot-predicts 默认 limit |
| `services/go-app/internal/service/home/service.go` | 热门竞猜按奖池排序 |
| `docs/prd/modules/kickoff-home.md` | 更新首页接口状态为已实现 |

## 核心决策

1. 首页顶部不接 banner 接口；赛事主视觉直接由 `today-matches` 驱动。
2. 运营广告不在本次首页主链路中新增；缺广告数据时不渲染广告模块。
3. 后端首页契约已存在，本次只修默认 limit 和热门竞猜排序口径。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | HOME-002、HOME-003、HOME-004、HOME-005、HOME-006、HOME-010 |
| 模块 PRD | `docs/prd/modules/kickoff-home.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` 已有首页 today-matches / live-rooms / hot-predicts / my-predicts 契约 |
| 不涉及契约的原因 | 未新增接口；仅对齐前端使用和后端默认值 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及，首页为纯读 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，属于前台首页聚合展示与契约对齐 |
| 涉及能力 | 缓存 / CDN 友好的多接口并发读取 |
| 高风险触发项 | 不涉及 |
| 能力门禁结论 | 允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/home ./internal/http/public` | 通过 |
| `npm --prefix apps/web run typecheck` | 通过 |
| `npm --prefix apps/web run build` | 通过 |
| Playwright 访问 `http://203.0.113.1:3000/` | 通过，截图 `output/playwright/homepage.png` |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | H5 原型 `#h5` 与首页 PRD |
| 页面截图 | `output/playwright/homepage.png` |
| 桌面/平板视口 | 已用桌面视口验收 |
| API 接口路径 | `/api/v1/home/today-matches`、`/api/v1/home/live-rooms`、`/api/v1/home/hot-predicts`、`/api/v1/home/my-predicts` |
| mock/fallback 状态与原因 | 本机 8080 `banner/today-matches/live-rooms` 均为空，页面展示空状态 |
| console 是否无 error | 无 error，仅 Nuxt DevTools/Vite 信息日志 |
| 合入判断 | 待 reviewer/owner 裁决 |

## 风险与待办

1. 本机 8080 的 `/home/today-matches`、`/home/live-rooms` 返回空数组，需要后台补赛事、直播间测试数据。
2. 本机 8080 的 `/home/hot-predicts` 返回旧字段形状，缺 `options/status/match_brief`，需要确认运行实例是否未部署当前后端。
3. HOME-008 广告位仍按 PRD 标记为待实现，未纳入本次首页主链路。

## 交接说明

下一位工程师需要知道：

1. 首页顶部已按 `today-matches` 赛事主视觉处理，不要接站点广告 banner。
2. 若后台补齐赛事/直播间/竞猜选项数据，首页会自动从空状态切换到卡片展示。
3. 若线上 `/home/hot-predicts` 仍返回旧字段，需要优先部署当前 Go 后端或排查路由指向。
