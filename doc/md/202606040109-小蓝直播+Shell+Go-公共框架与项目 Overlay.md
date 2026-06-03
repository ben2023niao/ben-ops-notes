---
id: "doc-b604816d45bf"
title: "公共框架与项目 Overlay"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/project-overlay.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/project-overlay.md"
sourceSha256: "a4441ab2709dc51e0cf507e1d6f321dfd40f9cc6eb6d87f23f36c9d45314a496"
sourceSystem: "project-doc"
---

# 公共框架与项目 Overlay

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/project-overlay.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本框架采用两层约束模型：

```text
公共 AI 框架层
  framework.config.json
  AGENTS.md
  docs/agents/rules/**
  docs/templates/**
  scripts/validate-*.py

项目 Overlay 层
  project.config.json
  docs/project/**
  docs/prd/**
  packages/contracts/**
  docs/qa/**
```

公共框架层定义团队怎样工作，项目 Overlay 层定义当前项目具体怎么用这套工作方式。

## 1. 为什么需要 Overlay

同一个团队可能做：

1. 移动 App + 官网。
2. PC/H5 Web 项目。
3. Go Gin 前后端分离项目。
4. Laravel + Filament 一体化后台项目。
5. Go Gin + Laravel 混合项目。

这些项目共享 Agent 工作流、Git 规则、契约优先、日志、红蓝对抗和质量门禁，但业务 PRD、启用模块、第三方服务、设计验收强度、规模等级不一样。

所以公共框架不应该把某个项目的选择写死；项目差异必须进入 `project.config.json` 和 `docs/project/**`。

项目类型选择由结构化 profile 承载：

```text
framework/profiles/{preset}/profile.json
```

`project.config.json.project.preset` 负责选择 profile；profile 负责声明默认启用模块和推荐质量门禁。公共框架不应该靠聊天记忆决定项目该启用 mobile、Laravel 还是 Web。

## 2. 不可覆盖规则

项目 Overlay 可以选择：

1. 启用哪些 apps 和 services。
2. 使用哪个项目类型 preset，或声明为 custom。
3. 使用 Go Gin、Laravel 或组合。
4. 是否启用严格设计图验收。
5. 当前 Scale Profile。
6. 哪些第三方服务暂未配置。

项目 Overlay 不能关闭：

1. Agent 日志。
2. 红蓝对抗。
3. Contract First。
4. 项目级验收。
5. mock 不能冒充完成。
6. 高风险链路测试、权限、审计、幂等要求。

## 3. Git 维护方式

公共框架改动和项目业务改动要在 Git 上分清楚。

推荐项目仓库以 Monorepo 方式组织业务代码，同时把公共 AI 框架作为子仓库引用：

```text
project-repo/
  .ai-framework/
  devtools/framework
  framework.lock.json
  project.config.json
  apps/
  services/
  packages/
  docs/
```

`.ai-framework` 更新只代表团队规则、模板、脚本和 preset 更新，不应该直接改业务运行时代码。需要把框架受管文件同步到项目根目录时，必须先执行 `devtools/framework plan`，确认差异后再执行 `devtools/framework apply`。

| 改动类型 | 分支建议 | 说明 |
| --- | --- | --- |
| 公共框架规则、模板、脚本 | `feature/framework-*` | 可回灌模板，影响后续所有项目 |
| 项目 Overlay 配置 | `feature/project-overlay-*` | 只影响当前项目选择 |
| 业务 PRD/OpenAPI | `feature/contract-*` | 项目业务资产 |
| 业务实现 | `feature/<module>-*` | 应引用 PRD/OpenAPI 和 Overlay |
| 生产修复 | `hotfix/*` | 修复后同步 main 和 develop |

MR 描述必须说明本次改动属于：

1. 公共框架资产。
2. 项目 Overlay。
3. 项目业务资产。

不能把项目业务例外偷偷改成公共规则。

## 4. 校验入口

```bash
npm run check:project-overlay
npm run check
```

`check:project-overlay` 会验证：

1. `project.config.json` 存在且结构完整。
2. 启用模块存在于公共 `framework.config.json`。
3. 项目 preset 合法，且必选模块已启用。
4. 设计模式在允许范围内。
5. Scale Profile 合法。
6. 必填项目文档存在。
7. 不可覆盖质量规则没有被关闭。
8. mock 不能被配置为完成。
