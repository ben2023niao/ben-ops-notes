---
id: "doc-13eca90b36a8"
title: "测试环境新增大数据上报 SDK 与 tesdk 配置"
date: "2026-08-06T17:48:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-06-1748-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E6%96%B0%E5%A2%9E%E5%A4%A7%E6%95%B0%E6%8D%AE%E4%B8%8A%E6%8A%A5SDK%E4%B8%8Ete-sdk%E9%85%8D%E7%BD%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-06-1748-【运维记录】测试环境新增大数据上报SDK与te-sdk配置.md"
sourceSha256: "8480615a83a0b3f86d9a848794a483d7c66ac472ba30f1fdfa056cd4aeeaedfc"
sourceSystem: "project-doc"
---

# 测试环境新增大数据上报 SDK 与 tesdk 配置

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-06-1748-【运维记录】测试环境新增大数据上报SDK与te-sdk配置.md`

> 整理日期：2026-08-06 17:48｜日期依据：文件名日期

环境标签：测试环境

时间：2026-08-06 17:48

## 背景

后端要求在游点涩测试环境新增大数据上报 SDK 包，并补充测试环境 env 配置：

```text
composer package：thinkinggame/ta-php-sdk:v3.1.1
env section：[te_sdk]
server_url：已按需求配置为数数科技接收地址
app_id：已按需求配置
```

## 操作范围

```text
环境：游点涩测试环境 / dev
运维仓库：/opt/docker-youdianse-php
业务仓库：/opt/docker-youdianse-php/src/youdianse-php
业务提交：b3706f8c chore: add thinking analytics sdk
镜像：youdianse-php:dev-b3706f8c
容器：youdianse-dev-php-web、youdianse-dev-php-nginx、youdianse-dev-php-cron
```

本次不触碰正式环境。

## 变更内容

业务仓库 `dev` 分支：

```text
composer.dev.json：新增 thinkinggame/ta-php-sdk = v3.1.1
composer.prod.json：新增 thinkinggame/ta-php-sdk = v3.1.1
```

测试服务器运行配置：

```text
/opt/docker-youdianse-php/env/.env.dev：新增 [te_sdk]
server_url：已设置
app_id：已设置
```

## 发布过程

1. 只读核验本地和测试服务器均为测试环境 `dev` 分支，测试镜像构建入口使用 `composer.dev.json`。
2. 本地业务仓库 fast-forward 到服务器当前业务提交后，新增 SDK 依赖。
3. 提交并推送业务仓库：

```text
b3706f8c chore: add thinking analytics sdk
```

4. 测试服务器拉取业务仓库 `dev`，备份 `/opt/docker-youdianse-php/env/.env.dev`，写入 `[te_sdk]`。
5. 生成 `.ops-build.env`，构建 `youdianse-php:dev-b3706f8c`，重建 `web/nginx/cron`。

## 验证结果

```text
业务仓库 HEAD：b3706f8c
容器镜像：youdianse-php:dev-b3706f8c
web/nginx/cron：Up
容器内 SDK：thinkinggame/ta-php-sdk v3.1.1
容器内 .env：[te_sdk] present，server_url/app_id set
后台入口：http://203.0.113.1:8088/admin1866/login HTTP 200
```

## 飞机群通知

按 `AGENTS.md` 逐步发送 Telegram 普通文本通知。当前测试服务器通知配置中 2 个群发送成功，1 个旧/异常目标返回 HTTP 400，与历史状态一致。

## 回滚方式

如需回滚 SDK：

```text
1. 业务仓库回退或反向提交移除 composer.dev.json / composer.prod.json 中 thinkinggame/ta-php-sdk。
2. 测试服务器拉取回滚后的业务提交。
3. 从 cicd-web/runtime/env-backups/ 选择本次变更前的 .env.dev 备份恢复，或移除 [te_sdk] 段。
4. 重新构建 youdianse-php 镜像并重建 web/nginx/cron。
5. 验证后台 HTTP 200 和容器状态。
```
