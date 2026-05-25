---
id: "doc-ef71eb389845"
title: "Agent 工作日志 · admin-obs-stream-params"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-obs-stream-params.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-obs-stream-params.md"
sourceSha256: "eaaab1d1e278082be4b6605e196bf5807ac9d510095aa39d49ac5c0f2ac96cb0"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-obs-stream-params

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-admin-obs-stream-params.md`

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：后台直播间补齐 OBS 推流参数展示

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-910, ADM-911, ADM-912
- 接口/契约：`packages/contracts/openapi/v1.yaml`, `docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台查看推流凭据时直接返回 OBS 可填的服务器和推流码。
2. 后台房间列表/详情页展示 `OBS 服务器`、`OBS 推流码`、`完整 RTMP` 并提供复制。
3. OpenAPI 与 Go 后端真实响应保持一致。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/config/config.go` | `SRSConfig` 增加 `rtmp_server` |
| `services/go-app/internal/config/loader.go` | 绑定 `APP_SRS_RTMP_SERVER` |
| `services/go-app/config/config.dev.yaml` | dev 默认 OBS 服务器设为 `rtmp://187.127.105.155:1935/live` |
| `services/go-app/internal/service/admin/room.go` | 推流凭据响应增加 `rtmp_server`、`obs_stream_key`、`push_url`，查看动作写审计 |
| `services/go-app/internal/service/admin/room_test.go` | 覆盖 OBS 推流码和完整 RTMP 拼接 |
| `apps/admin/src/api/index.ts` | 更新后台房间推流凭据类型 |
| `apps/admin/src/views/rooms/RoomListView.vue` | 列表页推流参数弹窗展示/复制 OBS 参数 |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | 详情页推流凭据区展示/复制 OBS 参数 |
| `packages/contracts/openapi/v1.yaml` | 更新 admin stream-key 接口响应 |
| `docs/api/openapi.yaml` | 由契约生成的发布文档 |

## 核心决策

1. 后台返回的 `obs_stream_key` 固定按当前 SRS hook 解析格式：`room_{room_no}_key{stream_key}`。
2. `rtmp_server` 来自配置 `srs.rtmp_server`，可用 `APP_SRS_RTMP_SERVER` 覆盖。
3. 继续保留原始 `stream_key`，但后台主展示和复制的是 OBS 应填的 `obs_stream_key`。

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/config ./internal/service/admin ./internal/http/adminapi ./internal/http/router` | 通过 |
| `python3 scripts/build-openapi-docs.py` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate docs/api/openapi.yaml` | 通过 |
| `npm run check:openapi && npm run check:contract` | 通过 |
| `cd apps/admin && npm run build` | 通过 |

## 风险与待办

1. dev 服务器仍需配置 `APP_DATA_ENC_KEY` / `APP_DATA_HMAC_KEY` 后才能成功创建房间并生成推流密钥。
2. 如果正式推流域名不是 `187.127.105.155:1935`，只需改 `APP_SRS_RTMP_SERVER`，不需要改代码。
