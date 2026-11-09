---
id: "doc-0e99809080a1"
title: "测试环境 albwhite 代号w 配置被覆盖修复记录"
date: "2026-08-11T17:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "监控告警", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-11-1700-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83alb_white%E4%BB%A3%E5%8F%B7w%E9%85%8D%E7%BD%AE%E8%A2%AB%E8%A6%86%E7%9B%96%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-11-1700-【修复Bug】测试环境alb_white代号w配置被覆盖修复记录.md"
sourceSha256: "1b9f5f3cecba0c6cf7fbe9b8d8e6f459fe982566071a7fdf9a09a5f0779f714e"
sourceSystem: "project-doc"
---

# 测试环境 albwhite 代号w 配置被覆盖修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608111700-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20albwhite%20%E4%BB%A3%E5%8F%B7w%20%E9%85%8D%E7%BD%AE%E8%A2%AB%E8%A6%86%E7%9B%96%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-11 17:00｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-08-11 17:00

## 背景

番子-远程后端在群里要求测试环境新增配置：

```text
alb_white.txt 末尾新增：
# ===== 代号w =====
test.projectw.xyz

alb_white_secret.txt 末尾新增：
# ===== 代号w  线上生产服 =====  格式 平台 + 私钥
designw=<平台测试私钥，值不落文档/Git>
```

随后反馈“测试环境配置文件被覆盖了”。

## 根因

```text
alb_white.txt / alb_white_secret.txt 的持久位置是测试服务器本地源文件：
  /opt/docker-youdianse-php/cicd-web/runtime/app-local-files/

发布流程每次重建容器后，会用该源文件覆盖 web/cron 容器内同名文件
（权限 root:www-data 0640）。

反复被覆盖的原因：配置被加在了“临时位置”：
1. 直接 docker cp / docker exec 改容器内文件 → 容器重建即丢；
2. 改业务仓库 src/youdianse-php/alb_white.txt → 发布时 git 还原即丢。

测试环境 webhook 自动发布频繁（2026-08-11 当天已有 13:16 / 14:37 / 15:44 /
16:56 四次），因此加错位置的内容很快就被冲掉。

处理前核验：容器、业务仓库、本地源文件三处均无“代号w / test.projectw.xyz /
designw”新增项；源文件 mtime 仍为 07-30 / 07-28，说明此前从未有人维护持久源文件。
```

## 处理过程

```text
1. 备份：cicd-web/runtime/manual-backups/
   alb_white.txt.bak.before_daihaow_20260811_165649
   alb_white_secret.txt.bak.before_daihaow_20260811_165649
2. 追加到服务器本地源文件（持久位置）：
   alb_white.txt：追加“# ===== 代号w =====”和 test.projectw.xyz
   alb_white_secret.txt：追加“# ===== 代号w  线上生产服 =====  格式 平台 + 私钥”
   和 designw=<平台测试私钥>
3. 同步 web/cron 容器并修正权限 root:www-data 0640。
4. 16:57 webhook 自动发布并发重建容器后复查，条目仍存在。
```

## 验证结果

```text
源文件标记：代号w=1、test.projectw.xyz=1、designw=1
web 容器：代号w=1、test.projectw.xyz=1、designw=1；权限 root:www-data 0640
cron 容器：代号w=1、test.projectw.xyz=1、designw=1；权限 root:www-data 0640
业务仓库：dev 分支，HEAD 1e7f47e2，工作区干净
后台入口：http://203.0.113.1:8088/admin1866/login HTTP 200
```

## 维护规则（防复发，发群同步）

以后新增白名单/平台密钥，只维护服务器本地源文件，不要改容器、不要改业务仓库同名文件：

```bash
cd /opt/docker-youdianse-php
# alb_white.txt（域名白名单，可正常追加）
printf '\n# ===== 代号x =====\ntest.xxx.xyz\n' >> cicd-web/runtime/app-local-files/alb_white.txt
# alb_white_secret.txt（平台+私钥，追加后不把内容发群/写文档）
printf '\n# ===== 代号x =====\nplatform=secret\n' >> cicd-web/runtime/app-local-files/alb_white_secret.txt
chmod 0600 cicd-web/runtime/app-local-files/alb_white.txt cicd-web/runtime/app-local-files/alb_white_secret.txt
```

需要立即生效时同步容器（或等下一次发布自动同步）：

```bash
docker cp cicd-web/runtime/app-local-files/alb_white.txt youdianse-dev-php-web:/var/www/html/youdianse-php/alb_white.txt
docker cp cicd-web/runtime/app-local-files/alb_white_secret.txt youdianse-dev-php-web:/var/www/html/youdianse-php/alb_white_secret.txt
docker exec youdianse-dev-php-web sh -lc 'chgrp www-data /var/www/html/youdianse-php/alb_white*.txt && chmod 0640 /var/www/html/youdianse-php/alb_white*.txt'
# cron 容器同样处理
```

## 机制隐患（后续建议优化）

```text
发布流程 backup_existing_protected_app_local_files 在业务仓库文件 dirty 时，
会把“业务工作区版本”覆盖到本地源文件。若业务工作区版本比源文件旧
（源文件里存在业务仓库没有的本地条目），可能冲掉源文件独有条目。

建议后续：
1. 提供统一追加脚本（只写源文件并同步容器），替代手工 docker cp；
2. 或把“dirty 迁移”改为不覆盖源文件，仅告警提示人工合并；
3. 重要密钥追加后立即备份并核对源文件大小/行数。
```

## 提交与通知

```text
本仓库（测试环境 dev）：新增本文档并更新 workbench，提交推送；
不提交 alb_white*.txt 内容到 Git，密钥值不落文档与通知。
测试服务器 /opt 同步 docs/workbench。
```
