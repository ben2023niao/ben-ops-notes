---
id: "doc-f13dbd57cb0d"
title: "Agent 工作日志 · predict-public-status-mapping"
date: "2026-05-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-predict-public-status-mapping.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-26-predict-public-status-mapping.md"
sourceSha256: "6f96a1238896d7f6fe748fd65b7d68527e1904d1daeddea1ea1d4af8583e514a"
sourceSystem: "project-doc"
---

# Agent 工作日志 · predict-public-status-mapping

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605260000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20predict-public-status-mapping.md)

> 整理日期：2026-05-26 00:00｜日期依据：文件名日期

日期：2026-05-26
Agent：Codex
任务：竞猜活动 C 端四状态映射

## 输入资料

- PRD：`docs/prd/modules/kickoff-predict.md`
- 需求 ID：PRED-009
- 接口/契约：`packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`
- 团队可读文档：`docs/operations/secrets-management.md`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 保持后台运营状态不变。
2. 给 C 端 `GET /api/v1/predict/activities` 增加 `UPCOMING` 动态映射。
3. 明确 public `status` 是单状态筛选，不要求逗号多状态。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/predict/service.go` | C 端列表按 public 状态筛选并映射 `UPCOMING` |
| `services/go-app/internal/http/public/predict.go` | public `status` 解析改为 `UPCOMING/OPEN/CLOSED/SETTLED/all` |
| `services/go-app/internal/dto/predict.go` | 增加 `PStatusUpcoming` |
| `services/go-app/internal/service/predict/service_test.go` | 覆盖 C 端状态映射 |
| `packages/contracts/openapi/v1.yaml` | 同步 public status 单值契约 |
| `docs/api/openapi.yaml` | 同步 public status 单值契约 |

## 核心决策

1. `DRAFT` 仍是后台草稿，不暴露给 H5 竞猜列表。
2. `UPCOMING` 不落库为独立后台状态；由 `status=OPEN && open_at > now` 动态映射。
3. 不做 CSV 多状态契约；C 端可以按 tab 分别请求单个 status，或不传/传 `all` 拉取全部 C 端可见状态后自行分组。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | PRED-009 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-predict.md` |
| OpenAPI / Event / DTO | `packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`、`services/go-app/internal/dto/predict.go` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 不适用 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不涉及 migration |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否，本次只改 public 列表展示状态 |
| 规范例外与原因 | 无 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要重新部署 Go 服务后生效 |
| 回滚 | 回滚 commit 即恢复旧状态口径 |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不涉及 |
| Runbook | 不涉及 |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | C 端只返回 `UPCOMING/OPEN/CLOSED/SETTLED` 这些用户可见状态，后台 `DRAFT` 不泄露。 |
| 红队质疑 | 若运营未配置 `open_at`，活动开启后会直接显示为 `OPEN`；这是当前后台表单能力边界，后续如要真正运营“未开始”需补后台开盘时间输入。 |
| 合入判断 | 允许合入；映射不改变资金结算状态机。 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented |
| Project Decision | pending-review |
| 项目级完成依据 | `docs/qa/project-acceptance.md` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/predict ./internal/http/public ./internal/dto` | 通过 |
| `go test ./...` | 通过 |
| `python3 scripts/validate-openapi.py` | 通过 |
| `docs/qa/acceptance-evidence.md` | 本次未新增验收记录 |
