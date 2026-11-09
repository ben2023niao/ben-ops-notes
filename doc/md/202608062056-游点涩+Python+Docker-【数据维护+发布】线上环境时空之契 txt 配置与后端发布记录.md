---
id: "doc-75c9192c8544"
title: "【数据维护+发布】线上环境时空之契 txt 配置与后端发布记录"
date: "2026-08-06T20:56:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Python", "Docker", "Nginx", "Redis", "自动化", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-06-2056-%E3%80%90%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%2B%E5%8F%91%E5%B8%83%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%97%B6%E7%A9%BA%E4%B9%8B%E5%A5%91txt%E9%85%8D%E7%BD%AE%E4%B8%8E%E5%90%8E%E7%AB%AF%E5%8F%91%E5%B8%83%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-06-2056-【数据维护+发布】线上环境时空之契txt配置与后端发布记录.md"
sourceSha256: "34bbcffebdcbf2165ad43202a17089f8cb1596bd27e4ed13626e92ac7558f1bb"
sourceSystem: "project-doc"
---

# 【数据维护+发布】线上环境时空之契 txt 配置与后端发布记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608062056-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BPython%2BDocker-%E3%80%90%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%2B%E5%8F%91%E5%B8%83%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%97%B6%E7%A9%BA%E4%B9%8B%E5%A5%91%20txt%20%E9%85%8D%E7%BD%AE%E4%B8%8E%E5%90%8E%E7%AB%AF%E5%8F%91%E5%B8%83%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-06 20:56｜日期依据：文件名日期

时间：2026-08-06 20:56 PST

## 基本信息

```text
平台：youdianse
环境：正式环境
范围：后端 web / nginx / php-cron，alb_white.txt，alb_white_secret.txt
业务 git id：3c6537634f418378257ef224eb15bd9c95d34fc1
短 git id：3c6537634f41
镜像：youdianse-php:main-3c6537634f41
开发：@willooku
产品/测试：@willooku
运维：@Kermit0824 @jett_yunwei @Ben_Bird @melo_sre @Daviea2
```

## 升级内容

```text
维护时空之契正式环境后端 txt 配置：
- alb_white.txt：确认已存在时空之契域名配置。
- alb_white_secret.txt：补齐时空之契线上生产服说明段，确认 skzq 平台配置存在且只有 1 条。
```

说明：本文档不记录 `alb_white_secret.txt` 的私钥明文。

## 执行步骤

```text
1. 读取 workbench，确认本仓库 main 对应游点涩线上正式环境，后端服务器为 16.209.16.108。
2. 使用线上后端服务器 Telegram 配置核对目标群为 18GAME_ 上线群（正式環境）。
3. 只读核对发布锁、线上版本、远端 main、磁盘、容器和两个需求 txt 文件。
4. 核对历史维护文档，确认本次按业务保护文件手动维护、保护备份、同步容器、权限验证方式处理。
5. 备份并维护 txt 配置：
   备份目录：cicd-web/runtime/app-local-file-backups/manual-skzq-20260806-205358
6. 同步最新 txt 到发布保护备份、web 容器和 cron 容器。
7. 执行发布前检查：
   sudo cicd-web/runtime/venv/bin/python cicd-web.py check --json
8. 执行正式后端发布：
   sudo cicd-web/runtime/venv/bin/python cicd-web.py deploy --git-id 3c6537634f418378257ef224eb15bd9c95d34fc1 --with-cron --json
9. 发布后执行独立验证。
```

## 配置结果

```text
alb_white.txt：
- 时空之契说明段：存在
- game.matchrpg-test.com：存在
- 本次未重复追加

alb_white_secret.txt：
- 时空之契线上生产服说明段：已补齐
- skzq 平台配置：存在
- skzq 平台配置数量：1
```

## 发布结果

```text
发布状态：SUCCESS
业务 HEAD：3c6537634f418378257ef224eb15bd9c95d34fc1
web 容器：youdianse-main-php-web，youdianse-php:main-3c6537634f41，running
nginx 容器：youdianse-main-php-nginx，nginx:stable，running
cron 容器：youdianse-main-php-cron，youdianse-php:main-3c6537634f41，running
dirty：false
```

## 验证结果

```text
CICD 发布内置健康检查：
HTTP：200
Session：writable
Redis：203.0.113.1:6379 open
MongoDB：server.db1.com:27017 open
Hosts：ok

独立入口验证：
本地后台：http://203.0.113.1:8088/admin1866/login -> 200
本地 CICD：http://203.0.113.1:18090 -> 200
公网后台：https://admin.youdianse-main.xyz/admin1866/login -> 200
公网 CICD：https://cicd.youdianse-main.xyz -> 200
H5 主域：https://h5.youdianse-main.xyz -> 200

txt 验证：
源文件：域名、说明段、skzq 平台配置均存在，skzq 数量 1
发布保护备份：域名、说明段、skzq 平台配置均存在，skzq 数量 1
web 容器：域名、说明段、skzq 平台配置均存在；权限 root:www-data 640；www-data 可读
cron 容器：域名、说明段、skzq 平台配置均存在；权限 root:www-data 640；www-data 可读

仓库与磁盘：
线上运维仓库状态：干净
线上业务仓库状态：干净
后端根盘：49G，已用 33G，使用率 68%
业务日志目录：约 19G
```

## Telegram 通知

已按 `AGENTS.md` 每步发送普通文本通知：

```text
【线上环境｜步骤 1 完成】正式环境与 workbench 任务核对
【线上环境｜步骤 2 完成】线上发布前预检与需求 txt 核对
【线上环境｜步骤 3 完成】需求 txt 维护方式核对
【线上环境｜步骤 4 完成】维护时空之契 txt 配置
【线上环境｜步骤 5 完成】CICD 发布前检查
【线上环境｜步骤 6 完成】正式后端发布与独立验证
【线上环境｜步骤 7 完成】文档与 workbench 总结
```

## 当前版本

```text
线上后端当前版本：3c6537634f418378257ef224eb15bd9c95d34fc1
线上后端当前镜像：youdianse-php:main-3c6537634f41
影响容器：web / nginx / cron
```
