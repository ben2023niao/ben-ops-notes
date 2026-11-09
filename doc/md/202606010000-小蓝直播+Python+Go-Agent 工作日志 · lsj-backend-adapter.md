---
id: "doc-e93e2a8f1fba"
title: "Agent 工作日志 · lsj-backend-adapter"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-lsj-backend-adapter.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-lsj-backend-adapter.md"
sourceSha256: "30f8c315e22b57e05915dd26aeee992f09ec87f56030bdb915150fa9ce624bfb"
sourceSystem: "project-doc"
---

# Agent 工作日志 · lsj-backend-adapter

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606010000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20lsj-backend-adapter.md)

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：Codex
任务：为 Go Gin 后端新增 LSJ 体育直播源 adapter 第一层架构。

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101
- 接口/契约：LSJ YApi：`/system/domains`、`/sportsLive/search`、`/sportsLive/play`
- 团队可读文档：`AGENTS.md`、`docs/architecture/live-streaming-architecture.md`
- 架构决策：`docs/decisions/ADR-0015-lsj-sports-live-source-backend-ingestion.md`

## 本次目标

1. 后端先建立 LSJ 协议 adapter，不让三方源字段进入 C 端契约。
2. 配置从 `APP_LIVE_SOURCE_LSJ_*` 注入，密钥不写 yaml。
3. 用单测覆盖 AES-128-ECB/base64、请求加密、响应解密、播放条件和 CDN 签名。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/infra/live/lsj/*` | 新增 LSJ client、codec、类型和测试。 |
| `services/go-app/internal/config/config.go` | 新增 `LiveSource.LSJ` 配置结构。 |
| `services/go-app/internal/config/loader.go` | 绑定 `APP_LIVE_SOURCE_LSJ_*` 环境变量。 |
| `services/go-app/internal/config/loader_test.go` | 新增 LSJ 配置 env 加载测试。 |
| `services/go-app/config/*.yaml*` | 新增 LSJ 配置占位，密钥保持空。 |
| `.env.example` | 新增 LSJ env 模板和安全说明。 |
| `docs/decisions/ADR-0015-lsj-sports-live-source-backend-ingestion.md` | 明确后端/媒体 worker 接入边界。 |

## 核心决策

1. LSJ 上游源只允许 Go 后端或 media worker 调用，不直接暴露给 Web C 端/主播端。
2. C 端仍通过我方 `play-url` 拉 ZEGO 节目流，避免 public API 被三方字段污染。
3. 本次只落 adapter 和配置，不建表、不改公开 OpenAPI、不启动同步 worker。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不涉及；尚未新增我方公开接口。 |
| 不涉及契约的原因 | 本次是内部 adapter 层，后续管理端配置/同步任务 API 另行设计。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响 |
| 密钥 | `APP_LIVE_SOURCE_LSJ_APPKEY` 仅 env/secret 注入 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方 API adapter / 直播源接入 / 权限安全 |
| 当前 MVP 边界 | 只实现协议 adapter，未接入生产同步状态机 |
| 未来迁移成本 | 后续可新增其他 source provider，不影响 C 端 API |
| 高风险触发项 | 权限 / 生产发布（密钥和上游源 URL 泄露风险） |
| 能力门禁结论 | 允许作为第一层后端架构合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 新增可选 env；默认关闭，不影响现有启动 |
| 回滚 | 删除 adapter 和配置即可；默认关闭状态下无运行时影响 |
| 密钥 | 生产通过 secret 注入 `APP_LIVE_SOURCE_LSJ_APPID` / `APP_LIVE_SOURCE_LSJ_APPKEY` |
| 观测 | 后续 worker/service 集成时需补日志、指标、告警 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/config ./internal/infra/live/lsj` | 通过 |
| `python3 scripts/test_sports_live_pull_demo.py` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 风险与待办

1. 后续需要新增同步任务：30 分钟全量，直播中 30 秒刷新，短窗口容错后标记完结。
2. 后续需要新增后台源配置和导播任务状态表，按数据库规范建 migration/down.sql。
3. 正式接入 media worker 后要补充上游错误率、拉源失败、断流恢复和导播任务告警。

## 交接说明

下一位 Agent 或工程师需要知道：

1. LSJ adapter 已可注入配置后直接调用，但当前没有接到业务服务。
2. 不要在 C 端 API 或前端代码中返回/保存 LSJ `main_url` / `backup_url`。
3. 下一步应设计 `live_source_configs` / `live_production_jobs` 或等价任务模型，并同步 OpenAPI/PRD/数据模型。
