---
id: "doc-5d8251b891e8"
title: "Agent 工作日志 · bug-28779-home-live-room-session-tip"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28779-home-live-room-session-tip.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28779-home-live-room-session-tip.md"
sourceSha256: "a98d8a2a3c13e20e682520e2c1aa175ef5d028e05f44fc3bd127311173c837a3"
sourceSystem: "project-doc"
---

# Agent 工作日志 · bug-28779-home-live-room-session-tip

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-bug-28779-home-live-room-session-tip.md`

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：修复禅道 Bug #28779：首页直播房间卡片打赏数量每次开播固定不变

## 输入资料

- PRD：`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-live.md`
- 需求 ID：HOME-004 / LIVE-007 / Bug #28779
- 接口/契约：`GET /api/v1/home/live-rooms`、`GET /api/v1/match/{match_id}/live-rooms`
- 验收证据：`docs/qa/acceptance-evidence.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：禅道 `https://pm.jsyyds.com/index.php?m=bug&f=view&bugID=28779`

## 数据链路

1. H5 首页 `apps/web/app/pages/index.vue` 调用 `getHomeLiveRooms(15)`。
2. 前端 API `apps/web/app/apis/home.ts` 请求 `GET /api/v1/home/live-rooms`。
3. 后端 `services/go-app/internal/http/public/home.go` 进入 `home.Service.LiveRooms`。
4. `RoomRepository.ListLive` 从 `live_rooms` 读取当前 LIVE 房间。
5. 送礼链路 `POST /api/v1/live/room/{room_id}/tip` 写入 `live_tips`，其中 `session_id` 指向当前 `live_sessions.id`。
6. 同步 / 异步统计链路同时维护：
   - `live_tips`：本场打赏流水，按 `session_id` 区分每次开播。
   - `live_sessions.total_tip_rmb`：本场 RMB 汇总。
   - `live_session_stats.tip_income_diamond`：本场钻石汇总，异步更新。
   - `live_rooms.cumulative_tip`：房间历史累计 RMB，不按开播场次清零。
7. H5 卡片 `apps/web/app/components/match/MatchCard.vue` 展示“打赏”数字，映射层在 `apps/web/app/utils/adapters.ts`。

## 根因

房间列表 DTO 原来只有 `cumulative_tip`，该字段来自 `live_rooms.cumulative_tip`，语义是房间历史累计打赏 RMB；H5 卡片展示的“打赏”属于当前开播场次热度，不应该读取历史累计或历史峰值。由于历史字段跨场次保留，每次重新开播会显示同一个或只增不清零的数字。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `AGENTS.md` | 新增 Bug 修复前必须梳理完整数据链路、业务不确定先沟通的规则 |
| `services/go-app/internal/repository/live/current_session_tip_stats.go` | 新增当前 active session 打赏聚合查询，数据源为 `live_tips` |
| `services/go-app/internal/service/livecard/home_live_room.go` | 新增房间卡片 DTO 的本场打赏字段填充 helper |
| `services/go-app/internal/dto/home.go` | `HomeLiveRoomItem` 新增当前场次打赏字段 |
| `services/go-app/internal/service/home/service.go` | 首页正在直播列表补充本场打赏字段 |
| `services/go-app/internal/service/schedule/service.go` | 赛事详情相关直播列表补充同一口径字段 |
| `packages/contracts/openapi/v1.yaml` / `docs/api/openapi.yaml` | 更新 OpenAPI 契约 |
| `apps/web/shared/types/home.ts` | H5 类型增加本场打赏字段 |
| `apps/web/app/utils/adapters.ts` | H5 房间卡片“打赏”改读 `current_session_tip_diamond` |

## 核心决策

1. 保留 `cumulative_tip` 作为历史累计字段，避免破坏既有调用方。
2. 新增 `current_session_tip_diamond` / `current_session_tip_rmb` / `current_session_tip_count` / `current_session_id`，让本场统计语义明确。
3. 本场金额聚合以 `live_tips` 为 source of truth，不依赖异步更新的 `live_session_stats`，避免列表短暂不准。
4. 首页列表和赛事详情相关直播复用同一 helper，避免两个入口口径漂移。
5. H5 房间卡片只读取 `current_session_tip_diamond`，字段缺失时显示 0，不再兜底读取历史累计 `cumulative_tip`。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不新增表，不改 DDL；复用 `live_sessions.idx_status_start` 和 `live_tips.idx_session` |
| 是否影响账本、事务、幂等或审计 | 不改资金写链路；只新增读侧聚合字段 |
| 是否涉及 H5 | 是，修改字段映射，不改变页面结构 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/livecard -count=1` | 通过 |
| `go test ./internal/service/home ./internal/service/schedule ./internal/repository/live ./internal/http/public -count=1` | 通过 |
| `pnpm install --frozen-lockfile --prefer-offline` | 通过 |
| `pnpm --filter @kickoff/web typecheck` | 通过 |
| `docs/qa/acceptance-evidence.md` | 本次只修 Bug #28779 的字段口径和 H5 映射，不声明项目级完成 |
| dev 只读 SQL 抽查 | 证明同一房间多场 `live_tips.session_id` 分开，但 `live_rooms.cumulative_tip` 为历史累计 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应页面 | H5 首页正在直播房间卡片 |
| 对应设计图 | 不涉及，本次只修 API 字段映射，不改视觉结构 |
| 设计尺寸 | 不涉及视觉稿；字段映射修复 |
| 目标视口 | H5 mobile 375x812 / 390x844，平板 768x1024，桌面 1440x900 |
| API 接口路径 | `GET /api/v1/home/live-rooms` |
| 页面截图 | `docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-375x812.png` / `docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-390x844.png` / `docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-768x1024.png` / `docs/qa/screenshots/current/h5-home-live-rooms-bug-28779-1440x900.png` |
| 真实手机视口 | 已用本地 H5 dev server + headless Chrome 截图验证 375x812、390x844 |
| 响应式验收 | 不涉及布局变更 |
| SEO异常验证 / meta scope | 不涉及 SEO异常验证、title、description、Open Graph 或页面 meta 修改 |
| 与设计图主要偏差 | 无视觉变更 |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 合入判断 | 允许合入；dev 当前没有 LIVE 房间，部署后需用真实开播场次做接口和页面复测 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 修复点收口在契约字段和 DTO 映射，旧字段保留，前后端语义更清楚 |
| 红队质疑 | 如果前端继续读旧字段或峰值在线，问题会复现；因此同步更新 H5 adapter |
| 合入判断 | 允许合入，需部署后用真实开播场次再次 curl 验证新增字段 |

## 风险与待办

1. 禅道账号当前被要求修改密码，自动写回备注会失败，需要账号状态恢复后补备注。
2. 当前 dev 没有 LIVE 房间，部署后需要开播一场并送礼，验证 `current_session_tip_diamond` 随本场变化。
3. 如果后续需要展示“打赏笔数”而非“打赏钻石”，前端应改读 `current_session_tip_count`，不要再复用历史累计字段。
