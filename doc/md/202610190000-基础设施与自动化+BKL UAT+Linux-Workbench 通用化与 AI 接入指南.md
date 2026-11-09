---
id: "doc-4842d91c94fb"
title: "Workbench 通用化与 AI 接入指南"
date: "2026-10-19T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Linux", "Shell", "Python", "Docker", "自动化", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8819%E6%97%A5-Workbench%E9%80%9A%E7%94%A8%E5%8C%96%E4%B8%8EAI%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/2026%E5%B9%B410%E6%9C%8819%E6%97%A5-Workbench%E9%80%9A%E7%94%A8%E5%8C%96%E4%B8%8EAI%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月19日-Workbench通用化与AI接入指南/2026年10月19日-Workbench通用化与AI接入指南.md"
sourceSha256: "d7635d5bec61f3f5ee6f13a933fff092d84b3c78cbbb5c4acaa6d682697dc977"
sourceSystem: "project-doc"
---

# Workbench 通用化与 AI 接入指南

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610190000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BLinux-Workbench%20%E9%80%9A%E7%94%A8%E5%8C%96%E4%B8%8E%20AI%20%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97.md)

> 整理日期：2026-10-19 00:00｜日期依据：文件名日期

日期：2026-10-19
执行人：Ben（运维）
版本：v1

## 需求

1. 把本项目的核心 Workbench 设计抽离出来，做成任何项目都能导入的套件。
2. 写详细设计思路、解决的问题。
3. 写详细 VSCode 插件、Token 接入、项目内使用 AI 的文档。
4. 发给群里开发参考，方便各项目改造。
5. 按固定流程通知、验证、文档、提交、发群。

## 交付物

目录：`workbench-kit-通用AI工作台/`

```text
workbench-kit-通用AI工作台/
├── README.md
├── VERSION
├── config/ai.env.example
├── docs/
│   ├── 01-设计思路.md
│   ├── 02-解决什么问题.md
│   ├── 03-快速导入.md
│   ├── 04-任务流程与提示词.md
│   ├── 05-VSCode插件与配置.md
│   ├── 06-Token与AI接入.md
│   ├── 07-团队落地与改造.md
│   └── 08-群公告模板.md
├── scripts/
│   ├── install.py
│   ├── check.py
│   ├── context_pack.py
│   ├── notify.py
│   └── package_kit.py
├── templates/
│   ├── AGENTS.md
│   ├── workbench/...
│   └── vscode/...
└── tests/test_install.py
```

## 核心能力

### 1. 一键导入

```bash
python3 scripts/install.py /path/to/project \
  --name "项目名" --slug project-name --with-vscode
```

- 生成 `AGENTS.md` 和 `workbench/`
- 已有 `AGENTS.md` 不覆盖，模板放 `workbench/AGENTS.template.md`
- 可选合并 `.vscode` 配置

### 2. 完整性检查

```bash
python3 workbench/scripts/check.py .
```

检查必需文件、项目目录、占位符、通知配置风险。

### 3. AI 上下文打包

```bash
python3 workbench/scripts/context_pack.py --project . --task TASK-001
```

- 汇总 AGENTS、任务、机器矩阵、链路、当前状态
- 自动脱敏 token、密码、私钥
- 支持字符上限和输出文件

### 4. 通用通知

```bash
python3 workbench/scripts/notify.py --title "【项目】步骤 1" --text "内容"
python3 workbench/scripts/notify.py --verify-chat
```

只从环境变量或 `workbench/notify.env` 读 token。

### 5. 发布包

```bash
python3 scripts/package_kit.py
```

生成 `dist/workbench-kit-v1.0.0-日期.zip`。

## 文档重点

- `01-设计思路`：状态外置、单一入口、事实分级、任务契约、风险分级、验证优先、通知即事件。
- `02-解决什么问题`：上下文丢失、重复劳动、改错服务器、秘密泄露、无验证等。
- `05-VSCode插件与配置`：GitLens、Git Graph、Markdown、YAML、Docker、Remote SSH、Python、Copilot、Continue、Cline、Codex。
- `06-Token与AI接入`：AI API Key、Telegram Bot Token、GitLab PAT、环境变量、CI、轮换、排错。
- `07-团队落地与改造`：角色、三周落地、开发/运维改造清单、指标、失败模式。
- `08-群公告模板`：可直接发群的短版/长版说明。

## 验证

- `python3 tests/test_install.py`：安装 / 检查 / 上下文 / 幂等 / 已有 AGENTS 保护全部通过。
- `python3 -m py_compile scripts/*.py`：通过。
- 安装到临时项目后 `check.py` 通过，生成文件无未替换占位符。
- `context_pack.py` 输出包含项目名、任务信息和脱敏提示。
- `make check` 已将安装器自测纳入。
- `make kit-package` 生成 49KB 发布包；从 zip 解压后重新安装并检查，通过。
- 包内中文文件名 UTF-8 正常，无真实 token / 密码。

## 发群方式

1. `make kit-package`
2. 发 zip 到 BKLUAT ALARM
3. 配 `08-群公告模板.md` 的短版说明
4. 让开发先跑安装、检查、上下文三步

## 提交

- 主提交：`1168a46`
- 文档收尾提交：见 `git log -1`
- 远端：`root/devops` main
