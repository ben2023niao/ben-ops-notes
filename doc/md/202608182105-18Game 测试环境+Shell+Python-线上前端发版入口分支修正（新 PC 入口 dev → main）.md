---
id: "doc-ecc038712a69"
title: "线上前端发版入口分支修正（新 PC 入口 dev → main）"
date: "2026-08-18T21:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_2105-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%AB%AF%E5%8F%91%E7%89%88%E5%85%A5%E5%8F%A3%E5%88%86%E6%94%AF%E4%BF%AE%E6%AD%A3-%E6%96%B0pc%E6%94%B9main.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_2105-【运维记录】线上前端发版入口分支修正-新pc改main.md"
sourceSha256: "3012c70b30c5203fa9284326b119ea743c8d93f04ef929af0501e7d731c92e00"
sourceSystem: "project-doc"
---

# 线上前端发版入口分支修正（新 PC 入口 dev → main）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_2105-【运维记录】线上前端发版入口分支修正-新pc改main.md`

> 整理日期：2026-08-18 21:05｜日期依据：文件名日期

环境标签：线上环境 / 前端发版 / ben-bot / 分支

时间：2026-08-18 21:05（Asia/Manila）

## 背景

用户反馈 `线上环境-游点涩-h5-发版`、`线上环境-游点涩-新h5-发版`、`线上环境-游点涩-新pc-发版` 三个入口需要发布 main 分支前端代码，但机器人显示的 git id 不是 main 分支。

## 定位

| 入口 | 分支默认值 | 结果 |
| --- | --- | --- |
| 线上环境-游点涩-h5-发版 | `H5_GIT_BRANCH` / `YOUDIANSE_H5_PROD_GIT_BRANCH` 默认 main | ✅ 本来就是 main |
| 线上环境-游点涩-新h5-发版 | `YOUDIANSE_H5_TEST_GIT_BRANCH` 默认 main | ✅ 本来就是 main |
| 线上环境-游点涩-新pc-发版 | `YOUDIANSE_PC_TEST_GIT_BRANCH` 默认 **dev** | ❌ 机器人显示 dev 提交的原因 |

## 处理

1. 修改 `devops/python/ben-bot/data/scripts/线上环境-游点涩-新pc-发版/youdianse_prod_18game_pc_client.py`：`YOUDIANSE_PC_TEST_GIT_BRANCH` `dev` → `main`。
2. 同步机器人运行机 `/opt/telegram/18game_devops/devops/python/ben-bot/data/scripts/...` 同文件。
3. `build_and_run_ben_bot.sh` 重建 ben-bot 容器（构建成功、容器启动正常）。

## 验证

- 机器人容器内该文件已为 `main`（`docker exec ben-bot grep GIT_BRANCH`）。
- GitLab main 分支确认存在：
  - H5 main 最新：`ece252d1`（Merge dev-qixi，含累充活动说明纯文本换行等）；
  - PC main 最新：`a2c76760`（Merge dev-qixi，与方林提供 git id 一致）。
- 三个入口点击后将列出 main 分支提交，可发布 main 代码。

## 通知与提交

- 每步已发 `18GAME_ 上线群（正式環境）`（步骤 1-2）。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
