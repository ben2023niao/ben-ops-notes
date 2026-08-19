---
id: "doc-13361d59be86"
title: "【运维记录】线上环境 nginx 与 PHP 错误日志打包发送记录"
date: "2026-08-20T04:29:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0429-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83nginx%E4%B8%8EPHP%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E6%89%93%E5%8C%85%E5%8F%91%E9%80%81%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0429-【运维记录】线上环境nginx与PHP错误日志打包发送记录.md"
sourceSha256: "78d49c3025803975323bdd226b5060d0c3bc249b85685aeb2f59d6a41add1af3"
sourceSystem: "project-doc"
---

# 【运维记录】线上环境 nginx 与 PHP 错误日志打包发送记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0429-【运维记录】线上环境nginx与PHP错误日志打包发送记录.md`

> 整理日期：2026-08-20 04:29｜日期依据：文件名日期

文档日期：2026-08-20 04:29
环境：游点涩线上环境（main 分支）
分类：运维记录
标签：线上环境、错误日志、打包、Telegram 附件

## 背景

用户要求把 nginx 与 PHP 容器/框架错误日志打包发到群里。

## 打包内容

```text
nginx/
  gateway-16.208.38.88-error.log   （网关 error.log，1382 行）
  baota-16.208.5.147-error.log     （宝塔 error.log，235,736 行，多为历史重复警告）
php/
  php-error.log                     （框架 PHP 错误，401KB）
  master-error.log                  （FPM master 警告，1.5MB）
  worker-error.log                  （worker 错误/OOM，10.8KB）
  slow.log                          （慢请求堆栈，5.5MB）
```

## 处理

```text
1. 日志统一做敏感字段脱敏（token/password/secret/access_key/api_key 与 URL 凭据 -> ***已脱敏***）；
2. 打包为 youdianse-nginx-php-err-20260820-0430.tar.gz（1.15MB，gzip）；
3. 发送至 18GAME_ 上线群（正式環境）。
```

## 发送结果

```text
message_id：9993
```

## 内容摘要

```text
nginx：网关 469 条 worker_connections（修复前）+ 上游连接错误 + /nginx_status 探测被拒；
      宝塔 99.9% 为 h5.youdianse.com 重复 server_name 历史警告。
PHP：php-error 每小时 TrackingService 同步报错；FPM master 1267 条超时警告；
     worker 35 条 128M OOM；slow.log 5342 条慢请求。
详见 docs/2026-08-20-0426-【运维记录】线上环境nginx与PHP容器错误日志汇总.md。
```

## 安全与敏感内容

附件已脱敏；本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值。
