---
id: "doc-46045f84260b"
title: "aicontext Prompt 说明"
date: "2026-08-25T15:23:52+08:00"
dateSource: "文件创建/修改时间"
categories: ["基础设施与自动化", "项目文档"]
tags: ["项目文档", "Linux", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/ops/aiwork/2026_devops/devops/ai_context/doc/prompt.md"
sourcePath: "~/Projects/work/ops/aiwork/2026_devops/devops/ai_context/doc/prompt.md"
sourceSha256: "bd422360cf12845fc753cfd9d3a30a7814584d32b44cc8c38e376e09bc93b2cb"
sourceSystem: "project-doc"
---

# aicontext Prompt 说明

> 来源文件：`~/Projects/work/ops/aiwork/2026_devops/devops/ai_context/doc/prompt.md`

> 整理日期：2026-08-25 15:23｜日期依据：文件创建/修改时间

## 用途

本目录是 2026 项目的机器与通知事实源。任何涉及服务器、容器、SSH、发布、通知的操作前，先读 `servers.yml` 与 `workbench/MACHINE_ACCESS_MATRIX.md`。

## 关键规则

- 机器事实以 `servers.yml` 为准，不凭聊天记录或文件名猜测。
- 登录前核对 hostname / whoami / pwd。
- 秘密（密码、token、私钥正文）不写入本目录、工作台、群消息或提交。
- 通知统一走 `scripts/notify_2026_ops.py`，发送前校验群标题。
