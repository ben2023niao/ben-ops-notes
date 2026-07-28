---
id: "doc-26d115febe9a"
title: "18game DevOps 持久化工作台落地记录"
date: "2026-07-29T20:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "自动化", "CDN", "DNS", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2020-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E4%BC%98%E5%8C%96%E3%80%9118gameDevOps%E6%8C%81%E4%B9%85%E5%8C%96%E5%B7%A5%E4%BD%9C%E5%8F%B0%E8%90%BD%E5%9C%B0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2020-【架构改造+优化】18gameDevOps持久化工作台落地记录.md"
sourceSha256: "b7b6cc0716a6d6cb3a0cfc8e96c92e40599deb61f574a7f9c3ff98b2be2bf235"
sourceSystem: "project-doc"
---

# 18game DevOps 持久化工作台落地记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2020-【架构改造+优化】18gameDevOps持久化工作台落地记录.md`

> 整理日期：2026-07-29 20:20｜日期依据：文件名日期

环境标签：通用

## 基本信息

- 时间：2026-07-29 20:20
- 分类：架构改造、优化
- 范围：当前 `18game_devops` 仓库
- 风险等级：C1
- 不涉及：服务器配置、生产发布、数据库、DNS、CDN、证书、IAM 写操作

## 背景

参考“Codex、Claude Code 与运维工作台架构”，本次将跨会话、跨工具、跨电脑的运维协作方式落到当前仓库，避免后续继续依赖聊天记录记忆服务器、域名、发布链路和当前任务状态。

## 本次落地内容

1. 新增根级 `AGENTS.md`。
   - 固定 AI 执行规则。
   - 明确线上任务每步通知 `18GAME_ 上线群（正式環境）`。
   - 明确读取顺序、风险分级、执行边界、秘密控制和提交规则。

2. 新增仓库级 `workbench/`。
   - `START_HERE.md`：新会话统一入口。
   - `ACTIVE_TASKS.md`：活跃任务和阻塞项。
   - `PROJECT_INDEX.md`：项目索引。
   - `MACHINE_ACCESS_MATRIX.md`：机器访问矩阵摘要。
   - `PROJECT_RUNTIME_CHAINS.md`：测试 H5/PC、线上 H5、后端 uploads/APK 链路。
   - `AUDIT_CONFLICTS.md`：事实冲突和待裁决项。

3. 新增项目级工作台 `workbench/projects/18game_devops/`。
   - `CURRENT_STATE.md`：当前已验证状态。
   - `CURRENT_TASK.md`：当前任务、风险等级和安全交接点。
   - `DECISIONS.md`：工作台落地决策。
   - `00-brief` 到 `99-archive`：按项目文档生命周期预留目录。

4. 新增 CC 任务交接模板。
   - `workbench/templates/cc-context.template.md`
   - `workbench/templates/cc-plan.template.md`
   - `workbench/templates/cc-manifest.template.json`
   - `workbench/templates/cc-result.template.md`
   - `workbench/handoff/to-cc/`
   - `workbench/handoff/from-cc/`

## 与现有目录关系

- `devops/ai_context/servers.yml` 继续作为机器、路径、容器和运行链路的事实源。
- `workbench/MACHINE_ACCESS_MATRIX.md` 只做摘要和跳转，不重复保存秘密或大段服务器资料。
- `devops/python/ben-bot/doc/` 继续保存 ben-bot 改造、故障和发布记录。
- `workbench/` 保存当前状态、任务、冲突、决策和 CC 交接，不替代历史文档。

## 通知验证

- 附件规则要求通知 `18GAME_ 上线群（正式環境）`。
- 本轮先检查运行中 ben-bot 已知群和线上 H5 发布默认配置，未直接解析到正式群。
- 随后通过线上后端运维仓库 Telegram 配置完成目标群标题校验，并发送 `【线上环境｜步骤 1 完成】` 通知。
- 文档不记录 chat、token 或 secrets 文件内容。

## 后续使用方式

新会话先读：

```text
AGENTS.md
workbench/START_HERE.md
workbench/ACTIVE_TASKS.md
workbench/PROJECT_INDEX.md
workbench/MACHINE_ACCESS_MATRIX.md
workbench/PROJECT_RUNTIME_CHAINS.md
workbench/projects/18game_devops/CURRENT_STATE.md
workbench/projects/18game_devops/CURRENT_TASK.md
```

高风险任务先生成：

```text
workbench/handoff/to-cc/TASK-ID-context.md
workbench/handoff/to-cc/TASK-ID-plan.md
workbench/handoff/to-cc/TASK-ID-manifest.json
```

执行完成后回填：

```text
workbench/handoff/from-cc/TASK-ID-result.md
```

## 验证

- 已确认新增结构在本地仓库可见。
- 文件内未写入密码、token、Secret Key、私钥正文或 `.env` 原文。
- 工作台引用既有 `devops/ai_context`，避免维护两份冲突机器事实。
