---
id: "doc-4ae1179e2280"
title: "Agent Log Governance"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/agent-log-governance.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/agent-log-governance.md"
sourceSha256: "20ed1dde779a46b310208d54dfd4ae157a4e36e8f1fb98e800540533dcdb252a"
sourceSystem: "project-doc"
---

# Agent Log Governance

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/agent-log-governance.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

## 1. 设计目标

乌托邦 要求每个项目保留 Agent 日志，但日志边界必须清楚：

```text
项目日志是项目事实源。
框架日志是框架事实源。
汇总平台是观察层。
```

新项目不能继承 乌托邦 框架仓库的历史日志。每个项目的 `docs/agents/logs/` 只记录该项目自己的任务、验证、红蓝对抗、风险和交接。

## 2. 三类日志

| 类型 | 存放位置 | 作用 | 是否复制到新项目 |
| --- | --- | --- | --- |
| 框架日志 | 乌托邦 仓库 `docs/agents/logs/` | 记录 乌托邦 自身规则、模板、脚本、门禁如何演进 | 否 |
| 项目日志 | 业务项目 `docs/agents/logs/` | 记录该项目自己的需求、实现、验证、风险和交接 | 项目内产生 |
| 汇总日志索引 | 乌托邦 Log Hub | 跨项目只读采集、搜索、统计、风险分析和框架反哺 | 只读采集 |

## 3. 初始化规则

新项目初始化时必须执行日志净化：

1. 删除复制进来的 `docs/agents/logs/*.md`。
2. 删除 `docs/agents/logs/_template/`。
3. 保留或创建 `docs/agents/logs/.gitkeep`。
4. 只生成当前项目的 bootstrap 日志。
5. 不允许出现 `FRAMEWORK-xxx` 或 `FRAMEWORK-QA-xxx` 这类 乌托邦 框架需求 ID。

`framework.sync.json` 不得同步 `docs/agents/logs/**`。公共框架只能同步日志规则和日志模板，例如：

```text
docs/agents/rules/logging-rules.md
docs/templates/agent-log-template.md
docs/architecture/agent-log-governance.md
```

## 4. 项目日志规则

项目日志必须回答：

1. 本次任务来自哪个项目需求 ID。
2. 读取了哪些项目资料。
3. 修改了哪些项目文件。
4. 验证命令是否真实执行。
5. 红蓝对抗结论是什么。
6. 哪些问题要反哺 乌托邦。

项目可以在日志中提到 乌托邦，但不能把 乌托邦 框架仓库的历史日志复制为项目日志。

## 5. 乌托邦 Log Hub

跨项目汇总不应该靠复制日志文件，而应该建设独立工程：

```text
乌托邦 Log Hub
  GitLab API / CI Artifact / scheduled crawler
  Markdown parser
  PostgreSQL
  Search index
  Web dashboard
```

Log Hub 通过只读采集读取各项目的 `docs/agents/logs/*.md`，不反向修改业务项目。

## 6. 推荐采集流程

```text
Project A docs/agents/logs/*.md
Project B docs/agents/logs/*.md
Project C docs/agents/logs/*.md
        ↓
GitLab API / CI artifact
        ↓
Log parser
        ↓
PostgreSQL + Search index
        ↓
风险报表 / Agent 表现 / 框架摩擦 / 复用候选
```

## 7. 推荐数据模型

| 表 | 作用 |
| --- | --- |
| `projects` | 项目基础信息、仓库地址、owner、状态。 |
| `repositories` | GitLab/GitHub 仓库信息和默认分支。 |
| `agent_logs` | 单条 Agent 日志索引、需求 ID、Agent、日期、结论。 |
| `validation_runs` | 日志提到的验证命令和结果。 |
| `risks` | 风险、阻塞、未完成事项和 owner。 |
| `framework_feedback` | 从项目日志抽取出的 乌托邦 框架优化建议。 |

## 8. 反哺机制

项目日志中出现框架摩擦时：

1. 项目内先记录风险和临时处理。
2. Log Hub 汇总相似问题。
3. 同类问题多次出现后，创建 乌托邦 框架 MR。
4. 框架 MR 更新规则、模板、validator 或文档。
5. 各项目通过 `.ai-framework` 升级获取改进。

## 9. 最低验收

1. `scripts/init-project.sh` 初始化后，新项目只包含当前项目 bootstrap 日志。
2. `scripts/template-self-check.sh` 检查新项目没有继承 乌托邦 历史日志。
3. `scripts/validate-agent-log-boundaries.py` 检查 `framework.sync.json` 不同步 `docs/agents/logs/**`。
4. 项目日志中如出现 乌托邦 框架需求 ID，必须失败。
