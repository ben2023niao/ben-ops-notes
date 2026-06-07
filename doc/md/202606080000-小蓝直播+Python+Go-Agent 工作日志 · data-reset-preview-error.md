---
id: "doc-df9dc84896d3"
title: "Agent 工作日志 · data-reset-preview-error"
date: "2026-06-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-preview-error.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-preview-error.md"
sourceSha256: "24064a34af23f34c21bd8bd301307f442d27e92eee93a9ed920d07b24278e10c"
sourceSystem: "project-doc"
---

# Agent 工作日志 · data-reset-preview-error

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-08-data-reset-preview-error.md`

> 整理日期：2026-06-08 00:00｜日期依据：文件名日期

日期：2026-06-08
Agent：Codex
任务：修复数据初始化预览接口 500，并核对 2026 世界杯赛程 Excel

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-930
- 设计图：不涉及
- 接口/契约：`POST /api/v1/admin/system/data-reset/preview`
- AI/工具控制文件：`AGENTS.md`
- 其他：`/Users/qx/Downloads/2026世界杯赛程表&参赛国.xlsx`

## 本次目标

1. 核对用户上传的世界杯赛程 Excel 是否符合导入结构。
2. 定位 dev 环境 `data-reset/preview` 返回 500 的根因。
3. 修复后端预览统计错误并补充回归测试。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/data_reset.go` | 修复清理影响统计在 DB Count 成功时仍返回 ErrInternal 的问题 |
| `services/go-app/internal/service/admin/data_reset_test.go` | 增加 nil DB error 不应被包装成失败的回归测试 |

## 核心决策

1. 本次 500 不是 Excel 文件体问题；正确 `curl -F file=@...` 上传仍复现 500。
2. Excel 结构可读，包含 `小组赛`、`淘汰赛`、`参赛国` 三个 sheet；参赛国 48 支、小组赛 72 场。
3. Excel 内容存在业务数据预警：淘汰赛 36 场，总场次 108 场，不是常见 2026 世界杯 104 场口径。
4. 根因是 `impactRows` / `rewardPrizeDetailsImpactRows` 将 nil GORM error 包装成非 nil `ErrInternal`，导致预览遇到第一张存在的清理表就 500。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-930 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 不涉及契约变更 |
| 不涉及契约的原因 | 仅修复服务端内部错误处理；接口路径、请求体、响应字段均未变化 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 不涉及 |
| 是否影响前端字段 | 不涉及前端字段变更 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 否，修复上线前数据初始化预览的错误处理 |
| 涉及能力 | 权限安全 / 迁移 |
| 当前 MVP 边界 | 仅支持后台超级管理员预览/执行上线前数据初始化 |
| 高风险触发项 | 用户数据 / 生产发布 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重新部署 `kickoff-admin` |
| 回滚 | 回滚本次 commit 即可 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 通过 dev `journalctl -u kickoff-admin` 使用 trace_id 定位到接口 500 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/admin -run 'Test(ParseWorldcupWorkbook\|CleanupPlan\|ParseExcelDateTime\|RewardPrizeDetails\|WrapDataResetDBError)' -count=1` | 通过 |
| `go test ./...` | 通过 |
| 本地 XLSX 结构检查 | 3 个 sheet 均存在；48 支球队；72 场小组赛；36 场淘汰赛；总 108 场 |
| dev `POST /api/v1/admin/system/data-reset/preview` 正确 multipart 上传 | 通过，HTTP 200；返回 `team_count=48`、`group_match_count=72`、`knockout_match_count=36`、`total_match_count=108`，并返回总场次 108 的 warning |

## 风险与待办

1. Excel 淘汰赛场次数量与 2026 常见 104 场口径不一致，需要产品确认是否修正源文件。
2. 如果确认这份 Excel 就是最终口径，需要产品明确接受 108 场；否则应修正淘汰赛 sheet 后再执行初始化。

## 交接说明

下一位 Agent 或工程师需要知道：

1. Chrome 复制出的 `--data-raw` multipart curl 不包含本地文件内容，手工验证必须使用 `curl -F file=@...`。
2. 本次不修改 C 端、主播端或后台前端字段。
3. 预览接口文档深链：`https://admin-dev.54-151-131-132.sslip.io/docs/#/operations/adminDataResetPreview`。
