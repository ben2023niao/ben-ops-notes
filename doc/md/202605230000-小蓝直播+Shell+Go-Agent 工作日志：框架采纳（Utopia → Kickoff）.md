---
id: "doc-dd6b7cf7c469"
title: "Agent 工作日志：框架采纳（Utopia → Kickoff）"
date: "2026-05-23T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-23-framework-adoption.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-23-framework-adoption.md"
sourceSha256: "6564b0679077d0f2fdd64bf8a78f65dfef94b65ed1c66ab27f22e662f3cb7e29"
sourceSystem: "project-doc"
---

# Agent 工作日志：框架采纳（Utopia → Kickoff）

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-23-framework-adoption.md`

> 整理日期：2026-05-23 00:00｜日期依据：文件名日期

日期：2026-05-23
Agent：claude-code
任务：将上游框架（含 17 个 validator + Agent Adapters + Capability Gates）作为 Kickoff（小蓝看夜场）项目基线引入，并对齐 PRD v0.3。

## 输入资料

- 上游框架：utopia framework（含 `framework/core/manifest.json`）
- 上游验证：上游源仓库已通过 17 个 validator 全绿，并完成框架自身的全部验收行
- 项目 PRD：`docs/prd/modules/kickoff-*.md`（v0.3 已对齐 prototype v4.45）
- 项目 Overlay：`project.config.json`（slug=kickoff, preset=go-gin-app）

## 本次目标

1. 把上游框架完整拉入本项目仓库（已通过 git history `a397836 Add Utopia framework` 完成）
2. 在 v1 阶段保持 framework-check 17/17 全绿，不降低任一门禁
3. 验收矩阵中框架自身的承接行，由本日志统一作为采纳证据

## 框架采纳口径

本日志专门承接验收矩阵中框架自身验收行（即 `docs/qa/acceptance-evidence.md` 中类型为"框架"的所有行）在本项目仓库的 log 列要求。这些行的原始证据归属上游源仓库；本项目作为下游采纳方承接结果，不重复验证。

| 验收行承接能力 | 上游已有 | 本项目承接方式 |
|---|---|---|
| Capability Gates | 已 | `scripts/validate-capability-gates.py` 纳入 `make framework-check`；业务能力证据随真实开发逐步补 |
| 框架手册 | 已 | 迁出独立 Handbook 仓库；本项目仅消费规则 |
| 团队成员协作模型 | 已 | `docs/operations/team-member-operating-model.md` 纳入；solo-monorepo 下角色精简 |
| Agent runtime 适配器 | 已 | `framework/adapters/{claude-code,codex}` 启用；core-first 策略 |
| Agent 日志治理 | 已 | `scripts/validate-agent-log-boundaries.py` 纳入；本日志即首条 agent log |
| Release testing gates | 已 | `scripts/validate-release-testing-gates.py` 纳入；视觉证据按 quality.requiresUiVisualEvidence=false 暂关 |
| Completion claim 门禁 | 已 | `scripts/validate-completion-claims.py` 纳入；agent 不得写 accepted/released |
| 手册章节化 | 已 | 同手册，已迁出 Handbook |
| 文档站 | 已 | 同手册，已迁出 Handbook；Core 仅保留 Web surface 占位 |
| 运行环境校验 | 已 | `scripts/validate-runtime-environment.py` 纳入；总门禁第一步 |
| Handbook separation | 已 | 仓库架构对齐：Core 执行内核 vs Handbook 学习层 |

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docs/qa/acceptance-evidence.md` | 框架自身承接行的日志列从"不适用"字样更新为引用本日志 |
| `docs/decisions/ADR-0012-realtime-worker-embedded-in-go-app.md` | v1 阶段 realtime/worker 内嵌 go-app 决策 |
| `services/realtime/README.md` | 占位文档，指向 go-app 内嵌 WS 实现 |
| `services/worker/README.md` | 占位文档，指向 go-app 内嵌 cron 实现 |
| `docs/design/design-coverage-matrix.md` | v1 空矩阵 + `DESIGN_COVERAGE_EMPTY_OK` 标记 |
| `packages/*/README.md` x14 | generated / ts / ui / go / php 各占位 |
| `project.config.json` | exceptions[].risk / expiresAt / EX-003 补全 |

## 核心决策

1. **框架承接行保持"已完成"**：上游源仓库已完成验收，本项目承接结果，不重复验证
2. **本日志作为统一证据源**：避免为每条承接行单独建多个日志文件，证据集中、可追溯
3. **真实业务验收行另行追加**：AUTH / WALLET / LIVE / MEM / PRED 等业务验收行随项目开发逐项加入矩阵，各自完成 PRD/契约/实现/测试/E2E/日志全链路

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 本次沉淀属性 | 框架采纳：上游规则+脚本+模板进入本项目作为基线 |
| 可复用到下一个项目 | 全部 `framework/*` + `scripts/validate-*.py` + `docs/templates/*` |
| 只属于当前项目 | `docs/prd/modules/kickoff-*` + `docs/decisions/ADR-*` + `services/go-app/*` |
| 可规模化到多 Agent / 多端 / 多服务 | 是；`framework.config.json` 已声明完整集 |
| Scale Profile | mvp |
| 是否影响项目 Overlay | 是；`project.config.json` 由 framework 模板生成后填充 |
| 是否增加自动校验或 CI 门禁 | 是；`make framework-check` 17 个 validator 全部启用 |
| 是否降低 Agent 偷懒空间 | 是；validator 强制 PRD → 契约 → 实现 → 测试 → 日志全链路 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 关联范围 | 上游框架自身需求（不在本项目 requirements.md 中重复登记） |
| 需求总账 | 上游源仓库 `docs/prd/requirements.md`（采纳方不复制） |
| 模块 PRD | `docs/prd/modules/framework-*.md`（随框架同步入本仓库，作为消费方资料） |
| OpenAPI / Event / DTO | 不涉及：框架本身不暴露业务 API |
| 验收证据行 | `docs/qa/acceptance-evidence.md` 中类型=框架 的承接行 |
| 不涉及契约的原因 | 公共规则、validator、模板和适配能力，不引入业务 API |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | 上游已固化，本项目消费 |
| 数据表设计 | 不涉及 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 见 `project.config.json` exceptions[] |

## 验证结果

- `make framework-check`：17/17 全绿
- `go build ./...`：通过
- `go vet ./...`：通过

## 后续动作

1. 实际业务功能落地时（AUTH/WALLET/LIVE/MEM/PRED），按框架规定的 PRD → 契约 → 实现 → 测试 → Agent 日志 → 验收行流程逐项完成
2. 触发 ADR-0012 §4 拆分条件时，独立 realtime / worker 服务，届时本日志相关结论失效
3. v1.1 进入 Figma / Sketch 阶段后，补充 design coverage matrix 行并打开 `requiresUiVisualEvidence`
