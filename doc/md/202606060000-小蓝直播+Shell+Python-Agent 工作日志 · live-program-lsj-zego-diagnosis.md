---
id: "doc-f13b091239f8"
title: "Agent 工作日志 · live-program-lsj-zego-diagnosis"
date: "2026-06-06T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "监控告警", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-live-program-lsj-zego-diagnosis.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-06-live-program-lsj-zego-diagnosis.md"
sourceSha256: "854dc94a14df0b8e83d73e8a0978cce1543c4af1b3cc90434454db67732ad715"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-program-lsj-zego-diagnosis

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606060000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-program-lsj-zego-diagnosis.md)

> 整理日期：2026-06-06 00:00｜日期依据：文件名日期

日期：2026-06-06
Agent：Codex
任务：补充 LSJ 源与 ZEGO 云播放器失败诊断

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-001 / LIVE-101
- 接口/契约：`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. ZEGO 云播放器失败时，能区分 LSJ 源当前是否可播。
2. HLS 探测不能把已经结束的 playlist 误判成可直播。
3. 日志和后台错误信息保留排障字段，便于给 LSJ / ZEGO 技术侧定位。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 增强 HLS playlist 探测；ZEGO 终态失败时追加 LSJ 诊断和结构化日志 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 覆盖 ENDLIST 拒绝、LSJ live 诊断、LSJ hls_error 诊断 |

## 核心决策

1. 不新增数据表，先把诊断写入当前 `error_message` 和结构化日志，降低上线风险。
2. `#EXT-X-ENDLIST` 明确视为 LSJ 源结束，不能继续交给 ZEGO 创建云播放器。
3. ZEGO `Status=6/7/8` 后主动复查 LSJ play + HLS；若 LSJ 当前可播，错误显示 `LSJ诊断=source_live`，后续重点查 ZEGO 拉源链路。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-001 / LIVE-101 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-live.md` |
| OpenAPI / Event / DTO | 未新增字段；复用 `error_message` 与现有日志事件 |
| 不涉及契约的原因 | 接口响应结构不变，只增强错误内容和后端日志 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 可观测性 / 高可用 |
| 当前 MVP 边界 | 不引入独立监控系统；先在运行时链路形成可定位诊断 |
| 未来迁移成本 | 后续可把同样诊断函数接入定时 worker 或指标系统 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 不影响部署入口和配置 |
| 密钥 | 不涉及 |
| 观测 | 新增 LSJ HLS 诊断字段：ended、segment_count、media_sequence、target_duration、http_status |
| 回滚 | 回滚本次两个 liveprogram 文件即可 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | ZEGO 失败时不再只有 `status/destroy_reason`，会同步记录 LSJ 当前可播性 |
| 红队质疑 | 单次 HLS 探测不能证明后续持续稳定；后续可接入周期 worker 和媒体序列增长监控 |
| 合入判断 | 可合入，满足当前排障诉求 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | passed |
| `cd services/go-app && go test ./internal/service/liveprogram` | passed |
| `cd services/go-app && go test ./...` | passed |

## 风险与待办

1. 当前是请求触发式诊断，不是独立定时监控。
2. 单次 HLS live snapshot 只能说明“当前后端可访问”，不能证明 ZEGO 节点同一时刻可访问。
3. 若 LSJ 源仍频繁抖动，建议新增周期 worker，记录 media sequence 连续增长情况并做告警。

## 交接说明

1. 后台看到 `LSJ诊断=source_live` 时，优先带 `player_id / stream_id / room_id` 找 ZEGO 排查。
2. 后台看到 `LSJ诊断=hls_error ... ENDLIST` 时，优先换 LSJ 线路或赛事源。
3. 当前没有改 H5 / 主播端前端接入方式。
