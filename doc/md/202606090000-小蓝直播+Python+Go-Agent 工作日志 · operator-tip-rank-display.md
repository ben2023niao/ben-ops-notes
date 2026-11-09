---
id: "doc-a5e6ab16c900"
title: "Agent 工作日志 · operator-tip-rank-display"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-rank-display.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-operator-tip-rank-display.md"
sourceSha256: "1f769febf7c63275e01091d9554cc220f40d2beb978b7942397bf2d761916678"
sourceSystem: "project-doc"
---

# Agent 工作日志 · operator-tip-rank-display

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606090000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20operator-tip-rank-display.md)

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：运营账号送礼进入 C 端/主播端实时礼物榜展示口径

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-007、LIVE-102、ADM-402
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/funds-and-ledger.md`、`docs/decisions/ADR-0017-operator-account-finance-boundary.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 修正 `/api/v1/streamer/me/sessions/current/tip-rank` 运营账号送礼后榜单不变的问题。
2. C 端 `/api/v1/live/room/{room_id}/tip-rank` 与主播端榜单统一为“互动展示口径”，包含运营账号礼物。
3. 保持结算、GMV、众筹、奖励等真实经营口径继续排除运营账号礼物。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/repository/live/tip.go` | `RankBySession` 不再过滤 `is_operator_tip` |
| `services/go-app/internal/repository/live/tip_test.go` | 增加 SQL 回归测试，防止展示榜单再次过滤运营账号 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 更新 C 端/主播端 `tip-rank` 文档口径 |
| `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md` | 更新运营账号礼物展示与结算分离口径 |
| `docs/architecture/funds-and-ledger.md`、`docs/decisions/ADR-0017-operator-account-finance-boundary.md` | 更新资金边界说明 |

## 核心决策

1. 实时礼物榜属于互动展示，不是主播结算口径。
2. 运营账号礼物应进入 C 端/主播端实时礼物榜，让运营账号在前台看起来和真实用户一致。
3. 结算仍使用 `settlement_*` 字段或 `is_operator_tip=false` 过滤。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | LIVE-007、LIVE-102、ADM-402 |
| 模块 PRD | `docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 更新 `liveTipRank`、`streamerCurrentTipRank` 文档说明；无字段改名 |
| 前端字段影响 | 不改字段，不要求 C 端/主播端改展示逻辑；榜单数据会自然包含运营账号礼物 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否，沿用 000051 的结算字段拆分 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 只需发布后端服务和文档；无新增 migration |
| 回滚 | 回滚本提交后榜单重新排除运营账号 |
| 密钥 | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 修正后展示榜单包含运营账号；结算统计查询未变 |
| 红队质疑 | 如果运营误把展示榜单当结算榜，会混淆；文档和后台场次对账字段已明确结算看 `settlement_*` |
| 合入判断 | 待测试通过后允许合入 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/repository/live ./internal/service/live ./internal/service/streamer` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `git diff --check` | 通过 |
