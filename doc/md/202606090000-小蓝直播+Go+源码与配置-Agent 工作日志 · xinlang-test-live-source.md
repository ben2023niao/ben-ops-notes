---
id: "doc-1e06a51b8a05"
title: "Agent 工作日志 · xinlang-test-live-source"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-xinlang-test-live-source.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-xinlang-test-live-source.md"
sourceSha256: "f73003717539c7e2b29b99ca4de04da5fe8c9a8aaab15ec6254307d1d7e3062d"
sourceSystem: "project-doc"
---

# Agent 工作日志 · xinlang-test-live-source

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-xinlang-test-live-source.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：新增电影测试源到后台上游资源预览

## 输入资料

- 需求 ID：LIVE-101
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- AI/工具控制文件：`AGENTS.md`
- 其他：`https://www.zzzypro.com/#term-6`、`https://api.xinlangapi.com/xinlangapi.php/provide/vod/`

## 数据链路

后台入口：`/api/v1/admin/sports-live`
DTO / service：`SportsLiveSourceService.Search/Play`
第三方来源：LSJ 正式源 + Xinlang MacCMS 兼容采集接口
返回字段：沿用 `app_name`、`stream_name`、`live_list`、`quality_code`、`can_play`
前端消费：上游资源管理页和赛事绑定弹窗手动选择 `type=100` 时可预览/绑定 Xinlang 电影源；`全部` 只查 LSJ 正式体育类型 `1/18/151`

## 本次目标

1. 新增电影测试源，后台资源页可搜索和预览 m3u8。
2. 赛事绑定弹窗可手动选择电影源，开播准备和 ZEGO 云播放器链路按 `app_name` 路由到对应上游。
3. 配置默认关闭，通过 env 在 dev 环境启用。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/xinlang/client.go` | 新增 Xinlang 客户端，搜索 VOD 列表并回查详情换取 m3u8 |
| `services/go-app/internal/service/streamer/sports_live_composite.go` | 新增多源组合器，按 `app_name` 路由播放 |
| `services/go-app/internal/http/router/admin.go` | 后台资源页、赛事绑定和节目流链路合并 LSJ + Xinlang |
| `services/go-app/internal/config/*` | 新增 `live_source.xinlang` 配置与 env 绑定 |
| `apps/admin/src/views/matches/list.vue` | 赛事绑定弹窗增加电影源手动选项 |
| `apps/admin/src/views/rooms/detail.vue` | 房间节目流预览支持电影源 |
| `apps/admin/src/locales/langs/zh-CN/*` | 资源页文案从 LSJ 调整为上游资源 |
| `.env.example`、`infra/deploy/README.md`、`services/go-app/config/*.yaml` | 新增 Xinlang 配置模板 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 更新后台资源预览说明 |

## 核心决策

1. 电影源是测试源，对外类型固定为 `type=100`，供应商标识为 `xinlang`；不混入上游资源管理页和赛事绑定弹窗的 `全部` 列表，但手动选择后可以写入历史表 `match_lsj_sources` 并进入 ZEGO 开播准备链路。
2. `stream_name` 使用短标识 `vod:<id>:<episode>`，播放时后端回查详情换取 m3u8，避免 URL 泄露和长度问题。
3. 未新增 API 字段；前端契约结构不变，只调整后台页面保护逻辑。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 是否影响前端字段 | 不新增、不改名、不删除字段；仅更新接口说明 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | dev 配置默认开启；如 `/opt/kickoff/.env` 显式设置 `APP_LIVE_SOURCE_XINLANG_ENABLED=false` 会覆盖并关闭 |
| 密钥 | 不涉及新密钥 |
| 回滚 | 关闭 `APP_LIVE_SOURCE_XINLANG_ENABLED` 或回滚代码即可 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/infra/live/xinlang ./internal/service/streamer ./internal/config ./internal/http/router` | 通过 |
| `pnpm --filter @kickoff/admin run typecheck` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |
| `curl https://api.xinlangapi.com/xinlangapi.php/provide/vod/?ac=videolist&t=10&pg=1` | dev 机器可访问，返回电影 VOD 列表 |
| `curl https://api.xinlangapi.com/xinlangapi.php/provide/vod/?ac=detail&ids=<vod_id>` | dev 机器可访问，返回详情与播放地址 |

## 风险与待办

1. Xinlang 属于资源站测试源，不保证体育直播版权和稳定性，只能后台手动选择，不混入正式体育全部列表。
2. 正式体育直播源扩展为多供应商时，应单独做通用 `program_sources` 表和供应商 ADR。
3. dev 启用后需人工在后台上游资源管理页确认可预览。
