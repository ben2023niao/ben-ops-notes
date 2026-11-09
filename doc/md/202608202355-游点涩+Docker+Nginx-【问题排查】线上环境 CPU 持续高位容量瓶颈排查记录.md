---
id: "doc-076e6c85ee5d"
title: "【问题排查】线上环境 CPU 持续高位容量瓶颈排查记录"
date: "2026-08-20T23:55:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "Redis", "监控告警", "自动化", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2355-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83CPU%E6%8C%81%E7%BB%AD%E9%AB%98%E4%BD%8D%E5%AE%B9%E9%87%8F%E7%93%B6%E9%A2%88%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2355-【问题排查】线上环境CPU持续高位容量瓶颈排查记录.md"
sourceSha256: "d16159921a122500b5bf5f34440eb53b858be626f4b83cef530ca81cf8218f17"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境 CPU 持续高位容量瓶颈排查记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608202355-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20CPU%20%E6%8C%81%E7%BB%AD%E9%AB%98%E4%BD%8D%E5%AE%B9%E9%87%8F%E7%93%B6%E9%A2%88%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-20 23:55｜日期依据：文件名日期

文档日期：2026-08-20 23:55
环境：游点涩线上环境（main 分支）
分类：问题排查 / 容量评估
标签：线上环境、CPU 告警、容量瓶颈、QPS、php-fpm、接口缓存、升级

## 背景

2026-08-20 23:10、23:40 连续两次 CPU 告警（99%+，阈值 80%），web 容器
峰值 320%。与 23:10 前一次告警不同，本次发布已过 40+ 分钟，CPU 仍持续
高位（idle 1.5%），判断非发布瞬时回源，而是容量问题。

## 排查数据

```text
1. 请求量（业务日志 api_request 按分钟统计）：
   - 发布前 22:45-22:55：约 14421-16557/min（约 250 QPS）；
   - 发布后 23:00-23:49：约 14837-18377/min（约 283 QPS），上升约 13%，
     属晚间流量常态，非瞬时回源。
2. 接口构成（60 秒窗口，共约 1.74 万请求）：
   tracking/record 2993、configDict/getConfigDict 1787、system/info 1583、
   AppVersion/latestVersion 1526、Tracking/recordPageVisit 1330 —— 前 5 占约 53%；
   system/info 返回超大数据（含 menus/social/用户信息/密码等，数 KB）。
3. 来源分布：网关 16.208.38.88 为代理主源（3 分钟 1144 次），其余用户 IP
   分散，无异常轮询/授权安全测试特征。
4. 错误率：60 秒 17370 个 200，43 个 499、20 个 404、0 个 5xx。
5. 配置：OPcache 已开启（10000 files/128MB）；php-fpm pm=dynamic、
   max_children=30、max_requests=500；nginx worker_connections 4096。
6. 容器：web CPU 峰值 320%，当前约 128%；cron 1%、logbus2 1%，非队列/日志侧问题。
```

## 根因

```text
常态 QPS 约 280（晚间），PHP 单请求 CPU 成本约 14ms，4 核机器已满负荷
（load 5-6，idle 1.5%）。20:38 发布 7d3c9f9c 后 tracking/record 改为写
Mongo 入队（big_data_job），叠加晚间流量上升，CPU 推至告警线并持续。
属容量瓶颈，非故障（错误率 0.1%、无 5xx）。
```

## 解决方案（待决策执行）

```text
1. 业务侧接口缓存（收益最大，预计降 30-50% 请求成本）：
   - system/info、configDict/getConfigDict、AppVersion/latestVersion 等
     只读低频变化接口加 Redis 缓存（60-300s）；
   - tracking/record、recordPageVisit 埋点批量/合并写入，减少 Mongo 单条 insert。
2. 升级配置：4 核 -> 8 核（CPU 翻倍，最直接）；
3. php-fpm 微调（低峰期执行，避免 CPU 100% 时重启 web 引发回源高峰）：
   - max_requests 500 -> 2000（减少 worker 重建开销）；
   - 评估 pm.max_children 30 -> 24 是否降低调度开销；
4. 监控：保持 CPU 80% 告警；发布后 1 小时重点观察。
```

## 处置说明

```text
CPU 100% 期间不建议重启 web 容器（会再次触发客户端集中回源），
php-fpm 参数调整安排在低峰期；接口缓存需开发配合改代码。
已确认无异常流量/代码故障，系统稳定运行中。
```

## 通知记录

```text
步骤 1：CPU 告警排查：确认 QPS 为常态 250-300，非瞬时回源
步骤 2：CPU 高根因确认：常态 QPS 280 打满 4 核，属容量问题非故障
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
