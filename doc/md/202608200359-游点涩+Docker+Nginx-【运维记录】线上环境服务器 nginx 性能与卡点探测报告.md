---
id: "doc-e625f1c19834"
title: "【运维记录】线上环境服务器 nginx 性能与卡点探测报告"
date: "2026-08-20T03:59:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0359-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%9C%8D%E5%8A%A1%E5%99%A8nginx%E6%80%A7%E8%83%BD%E4%B8%8E%E5%8D%A1%E7%82%B9%E6%8E%A2%E6%B5%8B%E6%8A%A5%E5%91%8A.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0359-【运维记录】线上环境服务器nginx性能与卡点探测报告.md"
sourceSha256: "fa48b5f65c221451e4e4fa5b776f87a3eafdc02c63153825e676c2a2c7ce13a2"
sourceSystem: "project-doc"
---

# 【运维记录】线上环境服务器 nginx 性能与卡点探测报告

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0359-【运维记录】线上环境服务器nginx性能与卡点探测报告.md`

> 整理日期：2026-08-20 03:59｜日期依据：文件名日期

文档日期：2026-08-20 03:59
环境：游点涩线上环境（main 分支）
分类：运维记录
标签：线上环境、nginx、性能、PHP-FPM、卡点、服务器探测

## 探测时间

2026-08-20 03:58-03:59（北京时间）

## 各服务器现状

### 1. 新网关 16.208.38.88（ip-172-31-27-233）

```text
系统：负载 1.19；内存 3.9G/20G；根盘 69%（可用 16G，留意）；数据盘未列出
nginx：8 worker × 4096 连接、fd 16384
stub_status：Active 626 / Reading 0 / Writing 9 / Waiting 519
worker_connections 错误：469（无新增）；TIME_WAIT 16645（回落中）
H5 容器 CPU 104%（单核占满）、PC 9.75%；内存 1GB 级
```

### 2. 宝塔 16.208.5.147（ip-172-31-26-125）

```text
系统：负载 0.03；内存 2.1G/20G；根盘 30%、数据盘 4%
nginx：worker_connections 51200、fd 51200
错误：连接/上游错误均为 0；80/443 established 约 57
PHP-FPM 8.2：pm.max_children=100、start=10、spare=30（富余）
```

### 3. 后端 16.209.16.108（ip-172-31-31-108）

```text
系统：负载 0.31；内存 1.8G/7.7G；根盘 40%、数据盘 21%（日志 96G）
nginx 容器：4 worker × 4096、fd 16384；8088 连接复用正常
最近 10 分钟 499：59（约 6/分钟）
web 容器 CPU 36.6%；cron 0.01%；CICD 200
【关键卡点】PHP-FPM：pm = dynamic；pm.max_children = 5；start_servers = 2；max_spare = 3
```

### 4. 前端 13.208.101.121（ip-172-31-16-205）

```text
系统：负载 0.15；内存 2.2G/7.7G；根盘 52%
H5 Nuxt：4 node worker（pm2），容器 CPU 0.5%、内存 302MB（空闲）
```

## 卡点分析

```text
核心卡点：后端 web PHP-FPM pm.max_children=5
  全部 API（登录/选服/支付/大数据上报）最多并发 5 个 PHP 进程；
  高峰期 5 个全忙 -> 新请求排队 -> 网关/宝塔等待超时 -> 499/网络失败（“时好时坏”主因之一）；
  容器内存 7.5G，单 FPM 进程约 50MB，扩容余量充足。

次要关注：
  1) 新网关 H5 容器 CPU 单核占满（104%），观察是否需要扩核/扩容；
  2) 新网关根盘 69%，关注构建产物/日志增长；
  3) 后端数据盘 21%（日志 96G），已有阈值 100G 与清理任务。
```

## 建议（需授权后执行）

```text
1) web 容器 php-fpm 调优：max_children 5 -> 30，start_servers 2 -> 8，
   max_spare_servers 3 -> 15（按压力动态调整，观察后收敛）；
2) 网关 H5 容器观察 CPU/流量，必要时扩核或扩容；
3) 网关根盘清理/扩容评估；
4) 宝塔、前端无需调整。
```

## PHP-FPM 调优执行结果（2026-08-20 04:03 补充）

```text
web 容器新增挂载 php/fpm-pool.conf 覆盖默认 www.conf：
  pm.max_children    5  -> 30
  pm.start_servers   2  -> 8
  pm.min_spare_servers 1 -> 5
  pm.max_spare_servers 3 -> 15
  新增 pm.max_requests = 500（定期回收 worker，防内存累积）
docker-compose.yml 增加 YOUDIANSE_RUNTIME_PHP_FPM_POOL_CONF_FILE 挂载。

验证：php-fpm -tt 通过；admin 200、登录接口 200；
FPM pool worker 按需扩到 11-12 个（上限 30），容器内存 55MB 起步。
```

## 通知记录

```text
步骤 1 四台服务器性能探测完成   message_id 9982
步骤 2 卡点分析与建议           message_id 9983
步骤 1（追加）PHP-FPM 调优完成  message_id 9987
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值。
