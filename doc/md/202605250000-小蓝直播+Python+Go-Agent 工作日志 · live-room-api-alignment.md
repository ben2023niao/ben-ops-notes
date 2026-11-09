---
id: "doc-67927c767b05"
title: "Agent 工作日志 · live-room-api-alignment"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-live-room-api-alignment.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-live-room-api-alignment.md"
sourceSha256: "43408fc245b7aed427d7361c41b8642372bf9cf8a50a915998a697447ac002ba"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-room-api-alignment

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605250000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-room-api-alignment.md)

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：Codex
任务：直播间卡片、比赛直播间列表、弹幕接口契约与 Go 后端实现对齐

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：HOME-004, LIVE-004, LIVE-005, ADM-904
- 设计图：`file:///Users/qx/Downloads/2026.05.23迭代版.html#h5`
- 接口/契约：`packages/contracts/openapi/v1.yaml`, `docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 对齐 H5 首页“正在直播”卡片所需字段与 Go 后端真实返回。
2. 对齐比赛详情“直播间列表”与首页直播间卡片同一套字段契约。
3. 修正直播间弹幕历史/发送接口 OpenAPI 与后端真实响应结构。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/home.go` | 扩展 `HomeLiveRoomItem`，新增主播、状态、缩略图、峰值观看、累计打赏、比赛快照字段 |
| `services/go-app/internal/service/home/service.go` | 首页直播间列表补充主播与比赛数据聚合 |
| `services/go-app/internal/service/home/service_test.go` | 覆盖首页直播间卡片字段与比赛快照 |
| `services/go-app/internal/service/schedule/service.go` | 比赛直播间列表补齐与首页一致的直播间卡片字段 |
| `services/go-app/internal/service/schedule/service_test.go` | 覆盖比赛直播间列表使用 `HomeLiveRoom` 契约 |
| `services/go-app/internal/http/router/public.go` | 给 home/schedule service 注入 DB，用于主播信息聚合 |
| `services/go-app/internal/dto/admin_modules.go` | 后台房间标题限制从 128 对齐原型 40 字符 |
| `packages/contracts/openapi/v1.yaml` | 更新 `HomeLiveRoom`、`LiveDanmaku`、`AdminLiveRoom` 等 schema 与接口响应 |
| `docs/api/openapi.yaml` | 由契约生成的发布文档 |
| `AGENTS.md` | 增加 Agent 后端/后台职责边界 |

## 核心决策

1. `LIVE` 不再依赖前端假状态，后端从 `live_rooms.status = 2` 返回 `status: LIVE`。
2. 首页 `/api/v1/home/live-rooms` 与比赛详情 `/api/v1/match/{id}/live-rooms` 统一使用 `HomeLiveRoom`。
3. 房间详情聊天室不塞进详情接口，继续使用已有弹幕 HTTP + WS 通道；本次修正 OpenAPI 与真实响应。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金写入；仅读接口与标题校验 |
| 是否修改 H5/Web 前端 | 否 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/home ./internal/service/schedule ./internal/http/public ./internal/http/router ./internal/service/live ./internal/service/admin` | 通过 |
| `python3 scripts/build-openapi-docs.py` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate docs/api/openapi.yaml` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |

## 风险与待办

1. 前台 H5/Web 需要改为消费 `HomeLiveRoom` 中的 `status`、`streamer_name`、`viewer_count`、`cumulative_tip`、`match` 字段；本次按职责边界不修改前台代码。
2. 后台房间详情若要做实时聊天室监控，需要在 `apps/admin/**` 增加页面接入已有 admin WS / 删除弹幕能力。
