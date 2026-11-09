---
id: "doc-08d1d949f965"
title: "测试环境 env 新增 APK CDN 配置并发布容器记录"
date: "2026-08-05T16:18:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-05-1618-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83env%E6%96%B0%E5%A2%9EAPK-CDN%E9%85%8D%E7%BD%AE%E5%B9%B6%E5%8F%91%E5%B8%83%E5%AE%B9%E5%99%A8%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-05-1618-【运维记录】测试环境env新增APK-CDN配置并发布容器记录.md"
sourceSha256: "fc50fc1be726110cf9836798b0aa6b7a42011df4dad9266b443f377fe3e7756c"
sourceSystem: "project-doc"
---

# 测试环境 env 新增 APK CDN 配置并发布容器记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608051618-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20env%20%E6%96%B0%E5%A2%9E%20APK%20CDN%20%E9%85%8D%E7%BD%AE%E5%B9%B6%E5%8F%91%E5%B8%83%E5%AE%B9%E5%99%A8%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-05 16:18｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-08-05 16:18
环境：游点涩测试环境（dev 分支）
分类：运维记录

## 背景

根据本次需求，测试环境需要在 `env/.env.dev` 新增 3 个 APK CDN 配置段，并发布到测试服务器后端容器运行态。

本次只处理测试环境，不处理正式环境。用户明确要求 `env/.env.dev` 必须提交；本文档、workbench、Telegram 通知和最终回复均不展开 key 明文。

## 配置文件

本地文件：

```text
env/.env.dev
```

测试服务器文件：

```text
/opt/docker-youdianse-php/env/.env.dev
```

## 新增配置段

新增段名和域名：

```text
[cdn.tencent.eep1.prod-apk.zkifae.cn]
domain=eep1.prod-apk.zkifae.cn
key=已配置

[cdn.jixing.res2.eepgames.com]
domain=res2.eepgames.com
key=已配置

[cdn.aliyun.a-apk.rkqzgk.cn]
domain=a-apk.rkqzgk.cn
key=已配置
```

## 操作记录

1. 确认操作边界

```text
仓库：/Users/ben/Documents/ben/docker/dev/docker-youdianse-php
环境：测试环境
初始状态：本地 git 工作区干净
正式环境：未触碰
```

2. workbench 记录

```text
文件：workbench/CURRENT_TASK.md
内容：记录任务范围、目标配置段、敏感信息边界、步骤通知结果和容器发布验证结果。
```

3. 本地 env 修改

```text
备份目录：.private/env-backups/
修改文件：env/.env.dev
结果：3 个新增配置段已写入；domain 与 key 字段均通过脱敏核验。
```

4. 测试服务器 env 修改

```text
备份文件：/opt/docker-youdianse-php/cicd-web/runtime/env-backups/.env.dev.before_apk_cdn_20260805_20260805_161603.bak
修改文件：/opt/docker-youdianse-php/env/.env.dev
结果：3 个新增配置段已写入；domain 与 key 字段均通过脱敏核验。
```

5. CICD Web 读取检查

```text
命令：cicd-web.py sync-config
结果：运行配置一致，同步开关关闭。
说明：CICD Web 可读取当前运行配置，并确认容器内 .env 已可看到宿主机新配置内容。
```

6. 容器运行态发布

```bash
cd /opt/docker-youdianse-php
docker compose --env-file .ops-build.env --profile cron config
docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build web nginx cron
```

发布结果：

```text
youdianse-dev-php-web：已重新创建并启动
youdianse-dev-php-nginx：已重新创建并启动
youdianse-dev-php-cron：已重新创建并启动
```

## 验证结果

配置校验：

```text
docker compose config：OK
宿主机 env/.env.dev：3 个新增段存在，domain 正确，key 已配置
web 容器 .env：sha256 与宿主机一致，3 个新增段解析 OK
cron 容器 .env：sha256 与宿主机一致，3 个新增段解析 OK
```

运行检查：

```text
后台入口：https://admin.youdianse-test.xyz/admin1866/login
HTTP 状态：200
容器状态：web/nginx/cron 均 Up
```

## 提交策略

本次按用户明确要求提交：

```text
env/.env.dev
docs/2026-08-05-1618-【运维记录】测试环境env新增APK-CDN配置并发布容器记录.md
workbench/CURRENT_TASK.md
```

注意：

```text
文档、workbench、Telegram 通知和最终回复不展开 key 明文。
```

提交结果：

```text
提交：9ebed94 config: add test apk cdn env sections
分支：dev
推送：origin/dev 成功
```

## 测试服务器仓库同步

同步目标：

```text
/opt/docker-youdianse-php -> 9ebed94
```

同步过程：

```text
首次使用 git pull --ff-only --autostash 处理服务器 env 本地改动。
autostash 回放时 env/.env.dev 出现 UU 冲突。
因为提交 9ebed94 已包含本次目标配置，最终选择提交版本解决冲突。
```

同步后复核：

```text
服务器 HEAD：9ebed94
服务器 git status：clean
web/nginx/cron：已再次 force-recreate
web 容器 .env：sha256 与宿主机一致，3 个新增段解析 OK
cron 容器 .env：sha256 与宿主机一致，3 个新增段解析 OK
后台入口 HTTP：200
```

## 飞机群通知

本次按 `AGENTS.md` 执行逐步 Telegram 通知。

通知结果：

```text
步骤 1 环境边界确认：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 2 workbench 任务记录：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 3 本地 env 配置：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 4 测试服务器 env 同步：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 5 CICD Web 读取检查：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 6 容器运行态发布：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 7 运维文档落地：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 8 提交前验证：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 9 提交推送：2 个运维群成功，1 个旧/异常目标 HTTP 400
步骤 10 测试服务器同步收口：2 个运维群成功，1 个旧/异常目标 HTTP 400
```

说明：当前测试服务器通知配置中存在一个旧/异常目标返回 HTTP 400；两个运维群发送成功。

## 回滚

如需回滚服务器配置：

```bash
cd /opt/docker-youdianse-php
cp -p cicd-web/runtime/env-backups/.env.dev.before_apk_cdn_20260805_20260805_161603.bak env/.env.dev
docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build web nginx cron
```

回滚后复测：

```text
web 容器 .env sha256 与宿主机一致
cron 容器 .env sha256 与宿主机一致
后台入口 HTTP 200
```
