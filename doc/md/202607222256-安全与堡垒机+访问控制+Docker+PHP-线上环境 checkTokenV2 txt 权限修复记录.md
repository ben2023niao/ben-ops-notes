---
id: "doc-eba87bae79c4"
title: "线上环境 checkTokenV2 txt 权限修复记录"
date: "2026-07-22T22:56:00"
categories: ["安全与堡垒机", "访问控制"]
tags: ["安全与堡垒机", "访问控制", "Docker", "PHP", "权限管理", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/03-安全配置与访问控制/游点涩-网关与白名单/2026-07-22-2256-【修复Bug】线上环境checkTokenV2-txt权限修复.md"
---

# 线上环境 checkTokenV2 txt 权限修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607222256-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%2BDocker%2BPHP-%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20checkTokenV2%20txt%20%E6%9D%83%E9%99%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 来源：本地项目文档 `game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-22-2256-【修复Bug】线上环境checkTokenV2-txt权限修复.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

文档日期：2026-07-22 22:56
环境：游点涩线上环境（main 分支）
分类：修复Bug

## 背景

测试环境排查 `/customer/other/checkTokenV2` 返回 `4002 Service Error` 时，确认根因之一是容器内 `alb_white_secret.txt` 权限为 `root:root 0600`，PHP-FPM worker 的 `www-data` 用户无法读取文件内容。

正式环境同步测试环境修复，确保 `alb_white.txt` 与 `alb_white_secret.txt` 在 web/cron 容器内对 `www-data` 可读。

## 修复

web 和 cron 容器启动时，对两份保护文件执行权限修正：

```text
chgrp www-data alb_white.txt alb_white_secret.txt
chmod 0640 alb_white.txt alb_white_secret.txt
```

这样保持文件不是公开 `0644`，同时允许 PHP-FPM / PHP CLI 所在的 `www-data` 组读取。

## 验证

发布后检查容器内权限：

```text
alb_white.txt owner=root:www-data mode=640
alb_white_secret.txt owner=root:www-data mode=640
```

使用 `www-data` 身份验证：

```text
alb_white.txt readable=yes file=ok
alb_white_secret.txt readable=yes file=ok
```

## 复测说明

服务端 txt 文件存在性和容器内可读权限恢复后，可通知测试和发行复测接口。

如果旧请求仍返回 `4002`，需要确认请求中的 `host_sign` 是否由当前正式环境对应平台私钥重新生成。旧的、过期的或使用其他环境私钥生成的 `host_sign` 仍会被业务正常拒绝。
