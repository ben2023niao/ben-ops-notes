---
id: "doc-5d6c4b79db19"
title: "Agent 工作日志 · live-crowdfund-public-api"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-live-crowdfund-public-api.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-live-crowdfund-public-api.md"
sourceSha256: "bafb3a1b88ce1c16a441fded899c347b5167a8ce4557c981f576381a543a9784"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-crowdfund-public-api

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-crowdfund-public-api.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：新增 C 端直播间众筹解锁快照 API

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-102
- 接口/契约：`GET /api/v1/live/room/{room_id}/crowdfund`
- 团队可读文档：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`docs/qa/project-acceptance.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：C 端当前只有 WS 增量事件，进房无法主动拉取当前众筹解锁快照

## 本次目标

1. 给 C 端新增未登录可见的直播间众筹解锁快照接口。
2. 响应复用既有 `CrowdfundProgressView`，返回累计钻石、阶段列表、已达成快照和下一阶段。
3. 同步 OpenAPI、contracts、PRD，并用 service 单测覆盖聚合口径。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/live/service.go` | 新增 `CurrentCrowdfund` 只读聚合方法 |
| `services/go-app/internal/http/public/live.go` | 新增 public handler |
| `services/go-app/internal/http/router/public.go` | 注册 `GET /live/room/:room_id/crowdfund` |
| `services/go-app/internal/service/live/service_test.go` | 覆盖 C 端众筹快照返回累计、阶段、已达成和 next_stage |
| `docs/api/openapi.yaml` | 新增 C 端 operation `liveRoomCrowdfund` |
| `packages/contracts/openapi/v1.yaml` | 同步契约副本 |
| `docs/prd/modules/kickoff-live.md` | 补 LIVE-102 C 端接口和联调口径 |

## 核心决策

1. 不新增 DTO 字段，复用主播端已经使用的 `CrowdfundProgressView`，降低前端接入成本。
2. 接口未登录可见，和直播间详情、礼物榜一致；只读且不暴露后台内部字段。
3. 进房初始化走 HTTP 快照，后续实时变化仍走 `live.crowdfund.progress` / `live.crowdfund.stage_unlocked` WS。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-102 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 新增 `liveRoomCrowdfund`；复用 `CrowdfundProgressView`；未改 WS event |
| 是否影响前端字段 | 新增公开接口；未删除、改名或改变既有字段 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 只读接口；不影响账本、事务、幂等、审计 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 是否只是 CRUD | 否，直播间实时统计快照读取 |
| 涉及能力 | 统计 / 数据一致性 / 权限安全 |
| 高风险触发项 | 不涉及资金写入；读取打赏累计展示口径 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需部署 go-app 新二进制后生效 |
| 回滚 | 回滚本次代码即可移除新接口 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 复用现有 HTTP trace_id / access log |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | C 端进房可直接初始化打赏解锁卡，不再等下一次打赏 WS |
| 红队质疑 | 未开播房间返回 404；前端需按无快照隐藏卡片或保留空态 |
| 合入判断 | 可以提交，需前端接入 API |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/live ./internal/http/public ./internal/http/router` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

不修改 `apps/web/**`；本次仅新增后端 API 与契约，前端需后续接入。

## 风险与待办

1. 前端需在 `/live/{room_id}` 进房后调用 `GET /api/v1/live/room/{room_id}/crowdfund`。
2. 前端继续监听 WS 增量事件，避免快照后进度不刷新。
3. 如产品希望未开播也返回空快照，可后续调整 404 口径。

## 交接说明

下一位 Agent 或工程师需要知道：

1. 接口文档深链：`https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/liveRoomCrowdfund`
2. 接口路径：`GET /api/v1/live/room/{room_id}/crowdfund`
3. 响应字段：`session_id`、`room_id`、`cumulative_diamond`、`stages`、`achieved`、`next_stage`
