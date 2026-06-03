---
id: "doc-c982c4ec66a4"
title: "乌托邦 Core 与 Handbook 分离"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "自动化", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/handbook-separation.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/handbook-separation.md"
sourceSha256: "ae88953a27e5d4dd1795c34b78c22c922c342b40b76ea6ba4ee5607a8cb2726d"
sourceSystem: "project-doc"
---

# 乌托邦 Core 与 Handbook 分离

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/handbook-separation.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

## 1. 设计目标

乌托邦 Core 是执行内核，乌托邦 Handbook 是学习层。二者必须分开维护，避免业务项目通过 `.ai-framework` 子仓库接入 Core 时，把长教程、案例、页面展示实现带入 AI 执行上下文。

核心原则：

```text
Core 给 AI 执行。
Handbook 给团队成员学习。
```

Core 必须短、硬、可验证；Handbook 可以详细、有思想、有案例、有展示站。

## 2. 为什么要拆

长手册适合团队成员理解框架，但不适合作为 Agent 默认执行材料。它会带来四类误读风险：

1. Agent 把教程案例误读成项目要求。
2. Agent 把解释性文字误读成强制规则。
3. Agent 在长文里抓错重点，忽略 `AGENTS.md`、`CLAUDE.md`、`docs/agents/core/**` 和 validator。
4. 业务项目通过 `.ai-framework` 引入大量学习资料，污染项目执行上下文。

因此，`docs/manual/**`、`docs/learning/**`、`docs/overview/**` 和 乌托邦 自身的文档站实现不进入 Core 的同步清单，也不作为业务项目默认资料。

## 3. 仓库边界

```text
utopia-core/
  AGENTS.md
  CLAUDE.md
  docs/agents/
  docs/architecture/
  docs/operations/
  docs/quality/
  docs/templates/
  scripts/
  framework/
  devtools/

utopia-handbook/
  docs/manual/
  docs/learning/
  docs/overview/
  apps/web/
```

## 4. 执行优先级

Agent 执行任务时，优先级如下：

| 层级 | 作用 |
| --- | --- |
| `AGENTS.md` / `CLAUDE.md` | 当前 Agent runtime 的硬入口。 |
| `docs/agents/core/**` | Agent-neutral 完成协议和工作边界。 |
| `docs/agents/rules/**` | 可执行工程规则。 |
| `project.config.json` / `docs/project/**` | 当前项目 Overlay。 |
| `docs/prd/**` / `packages/contracts/**` / `docs/qa/**` | 当前项目事实源。 |
| Handbook | 团队学习材料，按需阅读，不自动进入执行上下文。 |

如果 Handbook 与 Core 执行规则冲突，以 Core 和当前项目 Overlay 为准。

## 5. 同步规则

1. `framework.sync.json` 不得同步 `docs/manual/**`、`docs/learning/**`、`docs/overview/**`。
2. Core 的 `apps/web` 只保留项目 Web surface 占位，不承载 乌托邦 Handbook 文档站。
3. Handbook 发布、域名、CDN、搜索、统计属于 `utopia-handbook` 项目，不进入业务项目。
4. Handbook 可以引用 Core 规则，但不能反向改变 Core 的完成标准；需要改变标准时，必须回到 Core 提交 MR。

## 6. 新项目如何使用

新项目只接入 Core：

```bash
git submodule add <UTOPIA_CORE_REPO_URL> .ai-framework
devtools/framework plan
devtools/framework apply
```

团队成员学习框架时再打开 Handbook。项目执行时，Agent 不应默认全文读取 Handbook。
