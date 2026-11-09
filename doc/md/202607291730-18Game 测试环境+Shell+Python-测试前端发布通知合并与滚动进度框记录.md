---
id: "doc-0c3d3c5fafdf"
title: "测试前端发布通知合并与滚动进度框记录"
date: "2026-07-29T17:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "CDN", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1730-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E5%89%8D%E7%AB%AF%E5%8F%91%E5%B8%83%E9%80%9A%E7%9F%A5%E5%90%88%E5%B9%B6%E4%B8%8E%E6%BB%9A%E5%8A%A8%E8%BF%9B%E5%BA%A6%E6%A1%86%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1730-【优化】测试前端发布通知合并与滚动进度框记录.md"
sourceSha256: "f82b60b62cf2bcb9323bc51bb833e02a3dab723db60671d65ba69557bbe95fdc"
sourceSystem: "project-doc"
---

# 测试前端发布通知合并与滚动进度框记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607291730-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%E5%89%8D%E7%AB%AF%E5%8F%91%E5%B8%83%E9%80%9A%E7%9F%A5%E5%90%88%E5%B9%B6%E4%B8%8E%E6%BB%9A%E5%8A%A8%E8%BF%9B%E5%BA%A6%E6%A1%86%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 17:30｜日期依据：文件名日期

环境标签：测试环境

## 1. 文档信息

- 日期：2026-07-29
- 分类：优化、发布保障、机器人体验
- 范围：测试环境游点涩 H5/PC 按钮发布、GitLab webhook 自动发布、Telegram 飞机群发布进度通知
- 原则：减少刷屏，发布过程集中在一个持续刷新的进度消息中展示；日志和 env 附件仍保留。

## 2. 背景

测试环境 H5/PC 发版接入 AWS S3、腾讯新加坡 COS 和腾讯 CDN/EdgeOne 刷新后，远程脚本会对关键步骤逐条发送 Telegram 消息。

实际群内体验问题：

- 每个步骤都发一条新消息，群里重复内容太多。
- H5/PC 一次发布可能产生多条“发布步骤通知”。
- 按钮发布本身已有 ben-bot 外层进度框，远程步骤消息再次刷屏属于重复通知。
- webhook 自动发布没有按钮上下文，也需要保留可见进度，但应聚合到同一条消息。

## 3. 优化策略

### 3.1 按钮发布

按钮发布由 ben-bot 外层 `LiveOutputMessage` 承载进度：

- 首次点击按钮后，机器人编辑当前消息为发布进度框。
- 后续命令输出和 `[progress]` 标记持续编辑同一条消息。
- 远程脚本内部的“步骤通知”在检测到 `BEN_BOT_LIVE_OUTPUT=1` 时默认静默，不再额外发多条 Telegram 消息。
- 最终成功/失败仍更新同一条外层进度框。
- 详细发布日志附件和 env.txt 附件继续发送，便于排查。

### 3.2 webhook 自动发布

webhook 自动发布可能没有 Telegram 按钮消息可编辑，因此远程脚本内部保留一个聚合进度消息：

- 第一次步骤通知使用 `sendMessage` 创建一条“发布进度”消息。
- 后续步骤使用 `editMessageText` 编辑同一条消息。
- 消息体保留最近步骤列表，形成滚动更新效果。
- 默认每 3 秒最多编辑一次，避免 Telegram flood limit。
- 发布成功或失败时强制刷新最终状态。

## 4. 代码调整

修改文件：

| 文件 | 内容 |
| --- | --- |
| `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py` | 新增内部步骤消息聚合、`sendMessage`/`editMessageText` 复用、按钮发布时静默内部步骤消息 |

PC 发布说明：

- `测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py` 复用 H5 发布引擎。
- 因此本次优化自动覆盖 PC 按钮发布和 PC webhook 自动发布。

## 5. 行为变化

优化前：

```text
AWS 身份校验: 成功       -> 新消息
S3 静态资源同步: 开始    -> 新消息
S3 静态资源同步: 成功    -> 新消息
COS 静态资源同步: 成功   -> 新消息
Docker 构建: 成功        -> 新消息
腾讯 CDN 缓存刷新: 开始  -> 新消息
腾讯 CDN 缓存刷新: 成功  -> 新消息
```

优化后：

```text
测试环境-游点涩-h5-发版 发布进度
状态: 执行中
更新时间: 2026-07-29 HH:MM:SS
耗时: 123s
访问地址: https://h5.youdianse-test.xyz

最近步骤（滚动更新）:
01. HH:MM:SS AWS 身份校验: 成功
02. HH:MM:SS S3 静态资源同步: 开始
03. HH:MM:SS S3 静态资源同步: 成功
04. HH:MM:SS COS 静态资源同步: 成功
05. HH:MM:SS Docker 构建: 成功
06. HH:MM:SS 腾讯 CDN 缓存刷新: 成功
```

## 6. 配置说明

| 配置 | 默认值 | 说明 |
| --- | --- | --- |
| `BEN_BOT_LIVE_OUTPUT` | 按钮发布为 `1` | 外层 ben-bot 进度框开关 |
| `YOUDIANSE_H5_TEST_STEP_TG_NOTIFY` | `1` | webhook 场景保留内部步骤进度消息 |
| `BEN_BOT_INNER_STEP_TG_WHEN_LIVE` | `0` | 外层 live progress 存在时，默认不再发送内部步骤消息 |
| `BEN_BOT_STEP_TG_TAIL_LINES` | `18` | 内部步骤进度消息保留的最近步骤数 |
| `BEN_BOT_STEP_TG_EDIT_INTERVAL` | `3.0` | 内部步骤进度消息最小编辑间隔，单位秒 |

## 7. 验证记录

本地验证：

```bash
python3 -m py_compile \
  devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py \
  devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py \
  devops/python/ben-bot/app/benbot/executor.py
```

结果：

- 语法检查通过。
- H5 按钮发布和 webhook 使用同一个 H5 发布脚本。
- PC 发布复用 H5 发布引擎，因此同步生效。

## 8. 后续维护

- 发布步骤新增时继续使用 `send_deploy_step_to_telegram(summary)`，不要直接调用 `send_telegram_text` 发步骤消息。
- 按钮发布优先依赖外层 live progress，不新增内部步骤消息。
- webhook 发布依赖内部 edit 消息，确保有 `TG_BOT_TOKEN` 和目标 `TG_CHAT_ID`。
- env.txt 和部署日志附件属于结果材料，不算步骤刷屏，可继续保留。
