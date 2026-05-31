---
id: "doc-78c4f8a5a61b"
title: "Agent 工作日志 · sports-live-pull-demo"
date: "2026-06-01T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-sports-live-pull-demo.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-sports-live-pull-demo.md"
sourceSha256: "4477bc85f983e3e4b526c0d05878bde58fc9a34092f5a82ff467415c337c2008"
sourceSystem: "project-doc"
---

# Agent 工作日志 · sports-live-pull-demo

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-01-sports-live-pull-demo.md`

> 整理日期：2026-06-01 00:00｜日期依据：文件名日期

日期：2026-06-01
Agent：Codex
任务：根据第三方体育直播拉流 YApi 文档，梳理基础接口与体育直播接入方式，并新增 LSJ 协议 smoke demo。

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-101（直播拉流接入链路相关）
- 设计图：用户提供 YApi 文档内容
- 接口/契约：`POST /lsjapi/system/domains`、`POST /lsjapi/sportsLive/search`、`POST /lsjapi/sportsLive/play`
- 团队可读文档：`AGENTS.md`、`docs/architecture/live-streaming-architecture.md`
- 其他：ZEGO Web 超低延迟直播文档中心

## 本次目标

1. 判断基础接口与体育直播拉流的接入顺序。
2. 按 YApi PHP 示例实现 `appid` header + `appkey` AES-128-ECB/base64 请求协议。
3. 验证 demo 的加解密、响应解包、体育直播 search/play 调用和 CDN 签名辅助逻辑。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `scripts/sports_live_pull_demo.py` | 新增 LSJ 体育直播拉流 API smoke demo，支持 `system/domains`、`sportsLive/search`、`sportsLive/play` 三步请求。 |
| `scripts/test_sports_live_pull_demo.py` | 新增 demo 单元测试，覆盖 AES 加解密、真实协议请求构造、响应解包和 CDN URL 签名。 |
| `docs/agents/logs/2026-06-01-sports-live-pull-demo.md` | 本次工作日志。 |

## 核心决策

1. 以 PHP 请求示例为准：虽然接口表写 `application/x-www-form-urlencoded`，实际请求体是 JSON 字符串经 AES-128-ECB 加密并 base64 后作为 raw body POST。
2. `appid` 只放 header；`appkey` 只用于请求/响应体加解密与 CDN 签名，不输出明文。
3. demo 不进入生产链路，不修改 Go 后端、OpenAPI、数据库或前端页面。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 不涉及；本次只新增第三方 API smoke demo。 |
| 不涉及契约的原因 | 第三方接口尚未决定正式生产集成边界，暂不固化为我方业务契约。 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不影响 |
| 是否影响账本、事务、幂等或审计 | 不影响 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 第三方直播源接入验证 / 不进入生产链路 |
| 高风险触发项 | 不涉及资金、权限、审核、处罚、生产发布 |
| 能力门禁结论 | 允许作为调试脚本保留 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不影响部署，不进入 runtime 镜像白名单 |
| 密钥 | demo 通过环境变量或命令行传入 `appid` / `appkey`；dry-run 输出会遮蔽 `appid`，请求体只显示加密片段。 |
| 观测 | 不涉及 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/test_sports_live_pull_demo.py` | 通过 |
| `python3 scripts/sports_live_pull_demo.py --dry-run --appid dept001 --appkey 1234567890abcdef --action all --app-name hd --stream-name demo_stream` | 通过，展示三步真实 endpoint 请求且遮蔽 appid |

## 风险与待办

1. 需要拿真实 `appid` / `appkey` 才能跑外部 API 实测。
2. `sportsLive/play` 只有 `status=1` 且 live_list 当前项 `is_played=1` 时返回链接才可播放，调度侧必须按这个状态过滤。
3. 确认世界杯直播源版权、DRM、转推授权和可用协议后，才能进入正式后端集成。
4. 若接入生产，需要新增 ADR、正式 OpenAPI、后台源配置和 media worker 任务编排。

## 交接说明

下一位 Agent 或工程师需要知道：

1. demo 只用于第三方文档联调，不是业务 API 契约。
2. 真实请求示例：`LSJ_API_APPID=... LSJ_API_APPKEY=... python3 scripts/sports_live_pull_demo.py --action search --live-type 1 --show-body`。
3. 生产集成时应把第三方响应字段校验和错误码处理补成正式 adapter 测试。
