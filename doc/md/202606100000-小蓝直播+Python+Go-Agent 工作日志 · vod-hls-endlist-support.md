---
id: "doc-d92d2ac8fb5d"
title: "Agent 工作日志 · vod-hls-endlist-support"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-vod-hls-endlist-support.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-vod-hls-endlist-support.md"
sourceSha256: "c385bb2c58789ea4bc3e5bc09f9ce01fbbc82cc2e5f605c7a95feeaf1e866a09"
sourceSystem: "project-doc"
---

# Agent 工作日志 · vod-hls-endlist-support

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-10-vod-hls-endlist-support.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

日期：2026-06-10
Agent：Codex
任务：支持扩展电影源在直播间节目流准备时通过 VOD HLS 校验

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：不涉及公开字段变更
- AI/工具控制文件：`AGENTS.md`
- 其他：后台房间详情页报错 `LSJ m3u8 不可访问 ... HLS playlist ended (#EXT-X-ENDLIST)`

## 本次目标

1. 保持体育直播源的 m3u8 直播校验不变。
2. 允许 LSJ 电影源 / 新浪电影源这类 VOD HLS 播放列表携带 `#EXT-X-ENDLIST`。
3. 防止 ZEGO 失败诊断把可播放电影 VOD 源误判成 LSJ 源失败。

## 数据链路

入口页面 / API：后台房间详情页「开播准备 / 强制重建」 → admin room program API
DTO / service：`liveprogram.Service.PrepareLive`
repository / 数据表：直播间绑定赛事 → `match_lsj_sources` 当前启用线路
第三方来源：`source.Play(app_name, stream_name)` 获取 main / backup m3u8
后端校验：`pickPlayableHLSURLForSource` 预探测 HLS playlist
下游：校验通过后创建 ZEGO Cloud Player，返回 `match_stream_id` 给后台和主播端流程
前端消费字段：不涉及字段新增、删除、改名或类型变化

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | HLS 探测增加按上游源类型区分的策略；电影/VOD 源允许 ended playlist |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加电影 VOD ended playlist 回归测试，并保留体育源 ended playlist 拒绝测试 |

## 核心决策

1. 不在前端绕过错误，后端按源类型做正确的 HLS 可播判断。
2. `LSJ` 体育直播继续把 `#EXT-X-ENDLIST` 视为不可播，避免已结束体育源误开播。
3. `MOVIE` / `LSJ_MOVIE` 允许 ended playlist，但仍要求 playlist 有媒体分片或是 master playlist。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及 |
| 不涉及契约的原因 | 仅修正后端内部 HLS 校验策略，不改变请求和响应结构 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重新部署 Go 后端服务 |
| 回滚 | 回滚本次提交即可恢复旧校验策略 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 复用现有 liveprogram HLS probe 日志字段 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/liveprogram -run 'TestSyncProgramZegoHealthIncludesLSJDiagnosis/ended_movie_vod_playlist_remains_playable' -count=1` | 修复前失败，复现 VOD ended playlist 被误判 |
| `go test ./internal/service/liveprogram -count=1` | 通过 |
| `go test ./internal/service/liveprogram ./internal/infra/live/lsj ./internal/infra/live/xinlang -count=1` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `git diff --check` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |

## 风险与待办

1. ZEGO 对具体电影 m3u8 的兼容性仍取决于上游 m3u8 可被 ZEGO 访问，本次只修正后端误拦。
2. 如果后续支持更多 VOD 源，应继续复用源类型策略，不要把体育直播校验全局放宽。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 房间节目流准备链路的 m3u8 预检已经按 `sourceProgramType` 区分直播/VOD。
2. `LSJ_MOVIE` 识别来自 `lsj.IsMovieUpstreamID(row.UpstreamMatchID)`；新浪电影源识别来自 `app_name=xinlang`。
3. 本次没有前端字段变化，前端不需要改接口契约。
