---
id: "doc-17a7c1a580ca"
title: "Agent 工作日志 · lsj-movie-source"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "CDN", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-movie-source.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-movie-source.md"
sourceSha256: "264b4ef4b0c7ec24ae4e3dc9be915dcd9dd1aa66c92de2a6962abc4cda0a7cfb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-movie-source

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-lsj-movie-source.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：修复 LSJ 电影源空列表

## 输入资料

- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 线上现象：后台「上游资源管理」选择 `LSJ电影源` 时赛事数和可预览线路均为 0

## 数据链路

后台入口：`/api/v1/admin/sports-live?type=lsj_movie`
DTO / service：`SportsLiveSourceService.Search/Play`
第三方来源：LSJ 电影真实接口 `/movie/search`、`/movie/detail`，不是体育接口 `/sportsLive/search?type=100`
数据保存：赛事绑定仍写 `match_lsj_sources.app_name / stream_name / upstream_match_id`；LSJ 电影的 `upstream_match_id` 使用 `lsj_movie:` 前缀标记来源类型
返回字段：沿用 `app_name`、`stream_name`、`live_list`、`quality_code`、`can_play`；LSJ 电影默认线路返回 `app_name=lsj_movie`、`stream_name=movie:<movie_id>`，预览/开播时实时调用 `/movie/detail` 换 m3u8 并使用 movie CDN 加签
前端消费：上游资源管理、赛事绑定弹窗、房间源预览新增「LSJ电影源」；「全部」仍只查足球、篮球、电竞

## 根因

前一版把 `lsj_movie` 映射成 LSJ 体育接口的 `type=100`。dev 服务器使用真实 LSJ 密钥验证：

- `/sportsLive/search type=1`：返回足球资源
- `/sportsLive/search type=18`：返回篮球资源
- `/sportsLive/search type=151`：返回电竞资源
- `/sportsLive/search type=100`：`count=0/items=0`
- `/movie/search`：返回电影数组，`/movie/detail` 返回 `links[].m3u8_url`

因此页面空不是前端缓存或部署问题，而是后端接错 LSJ 电影接口。

## 修改范围

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/lsj/*` | 新增 LSJ movie search/detail adapter；`lsj_movie` 不再走 `sportsLive type=100` |
| `services/go-app/internal/service/liveprogram/service_test.go` | 更新 LSJ movie 绑定探测测试，使用固定 `app_name=lsj_movie` |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 更新查询类型、`source_type` 枚举和 LSJ movie 短标识说明 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 是否影响前端字段 | 不删除、不改名旧字段；`LSJ_MOVIE` 仍使用同一返回结构 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/infra/live/lsj ./internal/infra/live/xinlang ./internal/service/streamer ./internal/service/liveprogram ./internal/http/router ./internal/config` | 通过 |
| `pnpm --filter @kickoff/admin run typecheck` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| dev 服务器真实 LSJ 探测 | `/movie/search` 可返回电影；`/sportsLive/search type=100` 为空 |

## 风险与待办

1. 电影搜索只返回影片列表，不返回分页总数；当前 `count` 使用本页映射后的条数。
2. 当前搜索列表只暴露默认线路；预览/开播时取 `/movie/detail` 的第一个可用 m3u8。
3. LSJ 电影源不混入「全部」，避免误绑到正式体育赛事。

---

## 追加记录：Xinlang 林正英电影源搜索扩展

日期：2026-06-10
需求 ID：LIVE-101

### 背景

`https://admin-dev.54-151-131-132.sslip.io/#/lsj-resources` 当前 Xinlang 电影测试源只按配置 `type_id=10` 拉剧情片分页，页面关键词只过滤当前页。上游存在林正英相关电影，但多分布在喜剧片、动作片等分类；例如「僵尸先生（国语版）」「一眉道人」「灵幻先生」「驱魔警察」「音乐僵尸」。

### 本次调整

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/xinlang/client.go` | 支持 `SearchLiveParams.Keyword`；有关键词时使用上游 `wd` 跨分类搜索，不强制 `type_id=10`；对「林正英 / 英叔」追加经典片名别名查询 |
| `services/go-app/internal/infra/live/lsj/types.go` | `SearchLiveParams` 增加 `Keyword`，`LiveItem` 增加 `Actors` |
| `services/go-app/internal/service/streamer/sports_live_source.go` | 后端搜索入口透传 keyword，并返回 actors |
| `services/go-app/internal/http/adminapi/sports_live_source.go`、`streamerapi/sports_live_source.go` | 接收 `keyword` query |
| `apps/admin/src/views/live/lsj-resources.vue` | 搜索时下推 keyword，并展示演员字段 |
| `apps/admin/src/api/modules/match.ts` | 增加 `keyword` 请求参数和 `actors` 响应字段 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 契约同步新增 `keyword` 和 `actors` |

### 现网探测

| 验证项 | 结果 |
| --- | --- |
| Xinlang 上游 `wd=僵尸先生` | 返回「僵尸先生（国语版）」等，演员含林正英 |
| dev Admin 播放接口 `app_name=xinlang, stream_name=vod:72953:0` | 返回 m3u8，playlist 校验包含 `#EXTM3U` |
| 当前 dev Admin `type=lsj_movie` | 返回 0 条，LSJ 电影源暂未提供数据；本次可用源为 Xinlang 电影测试源 |

### 测试

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/streamer ./internal/infra/live/xinlang -run 'TestSportsLiveSourceServiceSearchMapsPlayableStreams\|TestSearchLiveKeywordOmitsConfiguredTypeAndMapsActors\|TestSearchLiveExpandsLinZhengyingKeywordAliases' -count=1` | 通过 |
| `go test ./internal/infra/live/xinlang ./internal/infra/live/lsj ./internal/service/streamer ./internal/service/liveprogram ./internal/http/adminapi ./internal/http/streamerapi -count=1` | 通过 |
| `pnpm --filter @kickoff/admin typecheck` | 通过 |
