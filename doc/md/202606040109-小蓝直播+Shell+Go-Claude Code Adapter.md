---
id: "doc-411d235d5268"
title: "Claude Code Adapter"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/adapters/claude-code.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/adapters/claude-code.md"
sourceSha256: "77ff41b9a8834dd4d5d1b0402918e4bc7fbd52d82da2ad14fa27dd825751cdd2"
sourceSystem: "project-doc"
---

# Claude Code Adapter

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/adapters/claude-code.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

Claude Code Adapter 用于把 乌托邦 Core 映射到 Claude Code 用户更自然的入口：`CLAUDE.md`、`.claude/commands/**`、`.claude/agents/**` 和可选 hooks。

## 入口文件

```text
CLAUDE.md
.claude/commands/**
.claude/agents/**
```

模板位于：

```text
framework/adapters/claude-code/
```

## 设计目标

1. 让 Claude Code 用户不需要先阅读所有 乌托邦 文档，也能按正确流程开工。
2. 把 PRD、契约、目录边界、验证、日志和红蓝对抗封装成 slash commands。
3. 把 Product、Contract、Backend、Frontend、QA、Reviewer 等角色封装成子 Agent 模板。
4. 保持 Core 工具无关，Claude Code 只作为执行适配层。

## 推荐命令

| 命令模板 | 作用 |
| --- | --- |
| `.claude/commands/utopia-task-brief.md` | 根据团队成员输入补齐任务 Brief 和目录边界。 |
| `.claude/commands/utopia-prd-check.md` | 检查需求 ID、PRD 模块和验收标准。 |
| `.claude/commands/utopia-contract-check.md` | 检查 OpenAPI、事件、DTO 和 mock 来源。 |
| `.claude/commands/utopia-red-blue-review.md` | 执行蓝队自检、红队质疑和合入判断。 |
| `.claude/commands/utopia-handoff.md` | 生成交接、风险和下一步。 |
| `.claude/commands/utopia-framework-upgrade.md` | 执行框架升级 plan/report/apply 流程。 |

## 推荐子 Agent

| 子 Agent | 作用 |
| --- | --- |
| product | PRD、需求 ID、范围和验收标准。 |
| contract | OpenAPI、事件、DTO、错误码和接口文档源。 |
| backend | Go Gin、Laravel、Worker、数据一致性和权限。 |
| frontend | Web、Admin、Mobile UI、真实接口和视觉证据。 |
| qa-reviewer | 验收矩阵、测试证据、红蓝对抗和合入判断。 |

## Hooks 使用边界

Claude Code hooks 可以帮助提醒或阻断风险，但不能替代 MR gate，也不是 乌托邦 Core 的默认要求。项目暂时不想上 hook 时，应使用 `npm run check`、`npm run verify:ui-runtime` 和 CI/MR 门禁完成约束。

可选把 hooks 用于：

1. 阻断 UI 变更没有真实截图证据就停止。
2. 提醒必须运行 `npm run check`。
3. 提醒必须更新 Agent 日志。
4. 提醒改动越过 `allowedWritePaths` 时需要 review。

不建议把会修改文件、提交代码、推送远端或部署生产的动作设为自动 hooks。

如果团队决定启用 Stop hook，可以安装：

```text
.claude/settings.json
.claude/hooks/agent-stop-verify.sh
```

Stop hook 只运行：

```bash
npm run verify:ui-runtime
```

它会调用真实浏览器截图、UI visual evidence 校验和 AI completion gate。根据 Claude Code hooks 官方文档，Stop hook 可以在 Claude 结束响应前运行，并用阻断结果要求它继续修复。未启用 hook 的项目，必须在完成报告和 MR/CI 中运行同一条命令链。

## Claude Code 完成标准

无论通过命令、子 Agent 还是普通对话执行，完成标准仍然是 乌托邦 Core：

1. 需求 ID 存在。
2. PRD 或任务说明存在。
3. OpenAPI/事件/DTO 已更新或写明不涉及。
4. 目录写入边界明确。
5. 验证命令真实运行。
6. 验收证据更新。
7. Agent 日志更新。
8. 红蓝对抗有明确合入判断。
