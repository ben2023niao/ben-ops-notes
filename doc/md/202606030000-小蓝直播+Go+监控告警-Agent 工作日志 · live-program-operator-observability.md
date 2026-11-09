---
id: "doc-74462074d900"
title: "Agent 工作日志 · live-program-operator-observability"
date: "2026-06-03T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "监控告警", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-live-program-operator-observability.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-03-live-program-operator-observability.md"
sourceSha256: "65b987fa6f7356a7930745e040b0ab1c90a21b5c69f46a26a611fde8eca6e729"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-program-operator-observability

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606030000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-program-operator-observability.md)

> 整理日期：2026-06-03 00:00｜日期依据：文件名日期

日期：2026-06-03
Agent：Codex
任务：直播节目流开播准备补充明确日志与运营提示

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-101
- 接口/契约：不变更接口结构，仅优化错误提示与后端日志
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. LSJ play / m3u8 探测失败时，后台错误提示明确告诉运营下一步操作。
2. ZEGO 云播放器未进入 Playing 时，提示携带可用于技术支持排查的 player 状态信息。
3. 后端写结构化日志，便于按 room/match/source/player 定位问题，并避免输出完整签名 URL。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/liveprogram/service.go` | 开播准备流程增加 LSJ/ZEGO 结构化日志与操作提示 |
| `services/go-app/internal/service/liveprogram/service_test.go` | 增加 URL host 脱敏单测 |
| `services/go-app/internal/pkg/logger/fields.go` | 登记直播节目流 event_type |
| `docs/agents/logs/2026-06-03-live-program-operator-observability.md` | 本次工作记录 |

## 核心决策

1. 日志记录房间、ZEGO 房间、赛事、LSJ 源、线路和 URL host，不记录完整 m3u8 签名地址。
2. LSJ play 失败、HLS 探测失败、ZEGO 创建失败、ZEGO 未 Playing 分别记录 warn，成功选中 HLS 线路记录 info。
3. 后台错误文案直接提示运营使用「直播源预览」确认线路，再执行「强制重建」。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-101 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 接口结构未变；新增日志 event_type |
| 不涉及契约的原因 | 响应字段不变，仅错误 message 更明确 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金；原有开播准备审计保持 |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 涉及能力 | 可观测性 / 第三方依赖诊断 |
| 当前 MVP 边界 | 只做日志与人类可执行提示，不新增告警规则 |
| 高风险触发项 | 生产发布 / 第三方直播源 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需随 go-app 发布生效 |
| 密钥 | 不涉及新增 secret；日志避免输出完整签名 URL |
| 观测 | 新增 `live.program.lsj_probe_failed` / `live.program.zego_player_failed` |
| 回滚 | 回滚本次代码即可恢复旧提示与日志行为 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 失败提示能指导运营换源/重建，日志可按房间和源定位 |
| 红队质疑 | 不能把完整 signed m3u8 打进日志，否则可能泄露临时播放凭据 |
| 合入判断 | 可合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/liveprogram` | 通过 |
