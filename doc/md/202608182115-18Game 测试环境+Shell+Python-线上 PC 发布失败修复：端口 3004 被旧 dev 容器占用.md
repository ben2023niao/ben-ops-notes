---
id: "doc-2119f227557a"
title: "线上 PC 发布失败修复：端口 3004 被旧 dev 容器占用"
date: "2026-08-18T21:15:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_2115-%E3%80%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8APC%E5%8F%91%E5%B8%83%E5%A4%B1%E8%B4%A5-%E7%AB%AF%E5%8F%A33004%E8%A2%AB%E6%97%A7dev%E5%AE%B9%E5%99%A8%E5%8D%A0%E7%94%A8.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-18_2115-【修复记录】线上PC发布失败-端口3004被旧dev容器占用.md"
sourceSha256: "a615ea075e072efd9545528afe3f286f7ecab88a72f5eafeea86805d798f7228"
sourceSystem: "project-doc"
---

# 线上 PC 发布失败修复：端口 3004 被旧 dev 容器占用

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608182115-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E7%BA%BF%E4%B8%8A%20PC%20%E5%8F%91%E5%B8%83%E5%A4%B1%E8%B4%A5%E4%BF%AE%E5%A4%8D%EF%BC%9A%E7%AB%AF%E5%8F%A3%203004%20%E8%A2%AB%E6%97%A7%20dev%20%E5%AE%B9%E5%99%A8%E5%8D%A0%E7%94%A8.md)

> 整理日期：2026-08-18 21:15｜日期依据：文件名日期

环境标签：线上环境 / PC 前端 / 发布失败 / 16.208.38.88

时间：2026-08-18 21:15（Asia/Manila）

## 背景

线上环境-游点涩-新pc-发版发布 main 分支 a2c7676：镜像构建成功（159.6s），容器启动失败（退出码 125），发布整体失败。

## 根因

```
docker: Error response from daemon: failed to set up container networking:
Bind for 0.0.0.0:3004 failed: port is already allocated
```

- 新 main 容器名 `youdianse_prod_pc_main_18game_pc_client_3004`，旧 dev 容器名 `youdianse_prod_pc_dev_18game_pc_client_3004`（入口默认 dev 时留下的）。
- 发布引擎按“分支名”识别容器，分支 dev→main 时未识别并停止旧 dev 容器，导致新容器启动时 3004 被占用；docker run 网络编程失败后留下无端口映射的 Created 容器。

## 处理

1. 停止旧 dev 容器（保留未删）：`docker stop youdianse_prod_pc_dev_18game_pc_client_3004`。
2. 删除无端口映射的失败容器，用正确参数重建 main 容器：

   ```bash
   docker run -d --name youdianse_prod_pc_main_18game_pc_client_3004 \
     -p 3004:3004 --restart unless-stopped \
     -e NODE_ENV=production -e HOST=0.0.0.0 -e PORT=3004 \
     -e DISPLAY_NAME=游点涩pc新线上 -e BRANCH=main -e SHORT_ID=a2c7676 \
     -w /app youdianse_prod_pc_main_a2c7676_18game_pc_client_3004:latest \
     sh -lc "set -a && . ./.env && set +a && exec pm2-runtime ecosystem.config.cjs"
   ```

## 验证

- `docker ps`：容器 Up，端口 `0.0.0.0:3004->3004/tcp`。
- 公网 `https://pc.yds-pc-h5-01.cc/` → 200。
- `/version.json` → environment=main, branch=main, short_id=a2c7676, git_id=a2c76760ae...。
- `/healthz` → 200。

## 建议（发布引擎）

- 发布引擎启动容器前应按“端口/项目”停掉占用该端口的旧容器（不只看分支名），避免分支切换（dev→main）再冲突。
- 旧 dev PC 容器保留在服务器（停止状态），不要再向该端口发 dev 分支。
- H5 老容器名本身是 main 分支，发 H5 main 不会撞名。

## 通知与提交

- 每步已发 `18GAME_ 上线群（正式環境）`（步骤 1-2）。
- 本地 Git 已提交（不 Push），commit 信息见提交结果通知。
