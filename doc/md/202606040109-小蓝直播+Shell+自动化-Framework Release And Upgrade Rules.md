---
id: "doc-a9bf45180794"
title: "Framework Release And Upgrade Rules"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/operations/framework-release.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/operations/framework-release.md"
sourceSha256: "686fe50ebbe3895a5d4e5749e0a0ca724259c1f1525a7838b00e84e46774bb17"
sourceSystem: "project-doc"
---

# Framework Release And Upgrade Rules

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Framework%20Release%20And%20Upgrade%20Rules.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文定义公共 AI 框架的版本发布、tag、兼容和升级规则。

## 1. Version Source Of Truth

公共框架版本以根目录 `FRAMEWORK_VERSION` 为准。

以下文件必须保持一致：

```text
FRAMEWORK_VERSION
framework.config.json -> frameworkVersion
framework.lock.json -> framework.version
CHANGELOG.md
```

## 2. SemVer Policy

版本号使用 SemVer：

```text
MAJOR.MINOR.PATCH
```

规则：

1. `MAJOR`：公共目录、同步策略、命令语义或质量门禁出现不兼容变化。
2. `MINOR`：新增规则、模板、preset、校验器或受管文件，不破坏旧项目。
3. `PATCH`：修复脚本、文档、校验误报或兼容性问题。
4. `-rc.N`：候选版本，只允许在试点项目验证，不作为团队默认版本。

## 3. Tag Rules

框架发布 tag 固定使用：

```text
framework-vX.Y.Z
```

示例：

```text
framework-v0.3.0
framework-v0.3.1
framework-v1.0.0
```

不允许使用项目名作为框架 tag，例如 `project-name-v0.3.0`。

## 4. Compatibility Policy

公共框架升级默认不修改业务运行时文件。

允许自动同步：

1. 命令包装。
2. 框架同步脚本。
3. 校验器。
4. 明确带有 managed marker 的公共工具文件。

只允许提示，不能自动覆盖：

1. `AGENTS.md`。
2. `README.md`。
3. `docs/agents/rules/**`。
4. `docs/templates/**`。
5. `docs/operations/**`。
6. `docs/quality/**`。
7. `docs/architecture/**`。

禁止框架同步覆盖：

1. `apps/**`。
2. `services/**`。
3. `packages/**`。
4. `docs/prd/**`。
5. `docs/project/**`。
6. `docs/qa/**`。
7. `infra/deploy/**`。

## 5. Upgrade SOP

项目升级框架时按以下步骤执行：

```bash
git -C .ai-framework fetch --tags
git -C .ai-framework checkout framework-vX.Y.Z
devtools/framework plan
devtools/framework report
devtools/framework apply
npm run check
npm run check:init
```

如果 `plan` 出现 advisory 文件差异，只能人工 review 后决定是否迁移，不允许自动覆盖项目已本地化的规则。

`report` 必须输出升级报告，至少包含当前锁定版本、目标版本、managed/advisory 文件数量、MR 门禁、升级步骤和 changelog 摘要。框架升级 MR 必须附该报告。

## 6. Release Checklist

发布框架 tag 前必须完成：

1. 更新 `FRAMEWORK_VERSION`。
2. 更新 `framework.config.json`。
3. 更新 `framework.lock.json`。
4. 更新 `CHANGELOG.md`，包含 compatibility、upgrade notes、breaking changes。
5. 更新或确认 `framework.sync.json`。
6. 运行 `devtools/framework report`。
7. 运行 `npm run check`。
8. 运行 `npm run check:init`。
9. 运行 `SELF_CHECK_PATH_MODE=without-rg npm run check:init`。
10. 创建 tag：`framework-vX.Y.Z`。
11. 创建 tag 后运行 `npm run check:framework-release:tag`。
