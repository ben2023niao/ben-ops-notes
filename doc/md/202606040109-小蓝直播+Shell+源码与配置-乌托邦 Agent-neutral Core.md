---
id: "doc-f0f5b464d4b4"
title: "乌托邦 Agent-neutral Core"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/core/README.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/core/README.md"
sourceSha256: "ac09f6c3fd2769fb210d054c5537bc07ebc8c1ca9b831731303c42dfb7a578f2"
sourceSystem: "project-doc"
---

# 乌托邦 Agent-neutral Core

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/core/README.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本目录定义 乌托邦 的 Agent-neutral Core，也就是不绑定 Codex、Claude Code、Cursor 或任何单一 AI 工具的公共协作规则。

乌托邦 Core 只回答这些问题：

1. 事实源在哪里。
2. 需求、契约、验收、日志如何形成闭环。
3. 团队成员如何给 Agent 派活。
4. Agent 如何声明范围、实现、验证和交接。
5. 什么情况下不能说完成。
6. 框架摩擦如何沉淀为公共资产。

具体 AI 工具的入口文件、命令、hooks、子 Agent 配置放在：

```text
docs/agents/adapters/**
framework/adapters/**
```

## Core 原则

1. Core 不写任何单一工具专属假设。
2. Core 不要求所有团队使用同一个 AI 客户端。
3. Core 只规定 PRD、OpenAPI、QA、日志、Git、运维和验收底线。
4. Adapter 负责把 Core 翻译成各工具能自然执行的入口。
5. 项目可以选择一个 primary agent runtime，也可以同时启用多个 adapter。

## Core 必读文件

| 文件 | 作用 |
| --- | --- |
| `AGENTS.md` | 当前 Codex 兼容入口，同时也保留项目级规则。 |
| `docs/agents/workflow.md` | Agent 工作流。 |
| `docs/agents/rules/ai-native-framework-rules.md` | AI 原生框架硬规则。 |
| `docs/agents/rules/engineering-rules.md` | 工程实现规则。 |
| `docs/agents/core/completion-protocol.md` | Agent 完成声明协议，定义没有证据时不能说完成。 |
| `docs/quality/release-testing-gates.md` | 上线测试门禁，定义测试如何成为上线资格证明。 |
| `scripts/validate-completion-claims.py` | 完成申请权门禁，防止 Agent 自己声明 accepted 或 released。 |
| `docs/operations/team-member-operating-model.md` | 团队成员如何使用 Agent。 |
| `docs/templates/team-member-task-brief-template.md` | 团队成员给 Agent 派活的结构化模板。 |
| `docs/templates/completion-report-template.md` | 任务完成报告模板。 |

## Adapter 必须遵守

每个 adapter 至少要说明：

1. 入口文件是什么。
2. 如何读取 Core。
3. 如何发起任务。
4. 如何做 PRD/Contract/Verify/Log/Review。
5. 如何限制目录写入边界。
6. 如何运行门禁。
7. 哪些功能只是建议，不能替代 MR gate。

Adapter 不能降低 Core 底线。比如 Claude Code 可以用 slash commands 简化流程，但不能跳过需求 ID、验收证据、Agent 日志和红蓝对抗。
