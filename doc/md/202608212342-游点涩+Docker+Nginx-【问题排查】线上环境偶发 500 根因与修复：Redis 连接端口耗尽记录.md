---
id: "doc-20405ed9dfa8"
title: "【问题排查】线上环境偶发 500 根因与修复：Redis 连接端口耗尽记录"
date: "2026-08-21T23:42:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "Redis", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-2342-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%81%B6%E5%8F%91500%E6%A0%B9%E5%9B%A0%E4%B8%8E%E4%BF%AE%E5%A4%8D-Redis%E8%BF%9E%E6%8E%A5%E7%AB%AF%E5%8F%A3%E8%80%97%E5%B0%BD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-2342-【问题排查】线上环境偶发500根因与修复-Redis连接端口耗尽记录.md"
sourceSha256: "0e2e2c79b5a70d4ed35b2bea07bde07d6c7c5c8ea6b66c199e44c199a5873d11"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境偶发 500 根因与修复：Redis 连接端口耗尽记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-21-2342-【问题排查】线上环境偶发500根因与修复-Redis连接端口耗尽记录.md`

> 整理日期：2026-08-21 23:42｜日期依据：文件名日期

文档日期：2026-08-21 23:42
环境：游点涩线上环境（main 分支）
分类：问题排查 / 性能修复
标签：线上环境、500、Redis、Cannot assign requested address、端口耗尽、sysctls

## 背景

后端多版本更新发布后出现偶发 500：后台卡顿、游戏内 SDK 注册/消费订单
概率 error、刷新后 500。已排查 php-fpm、慢查询、Mongo 索引等多个方向。

## 根因

```text
业务日志 128 万+ 条 Uncaught RedisException：Cannot assign requested address。

链路：
1. 应用每个请求新建 Redis 连接（无连接复用），关闭后产生 TIME_WAIT；
2. 高 QPS（约 280）下，容器内 TIME_WAIT 在 60s 内堆积 1.6 万+，
   容器默认 ephemeral 端口范围 32768-60999（约 2.8 万）被打满；
3. 端口耗尽 -> 新 Redis 连接失败（EADDRNOTAVAIL）-> 约 50% 请求 500。

佐证：
- 容器内 /proc/net/tcp 27554 条 socket（接近 2.8 万上限）；
- Redis 服务器正常：connected_clients 19/10000、rejected=0；
- 内网直连 8 次全 200（串行无并发压力），真实并发流量 50% 500。

其他已排除/已处理项：
- pointMall/index N+1 全表扫描（gift_pack/exchange_record 缺业务索引）：
  已创建 4 个索引（user_gift_exchanged、gift_code_type_status、status_1、
  user_game_created），降低慢请求；
- Recharge/create 第三方支付 curl 最长 40s 会占 worker（应用侧优化项）。
```

## 处置

```text
docker-compose.yml web/cron 服务新增 sysctls：
  net.ipv4.ip_local_port_range=1024 65535（端口范围翻倍，约 6.4 万）
  net.ipv4.tcp_tw_reuse=1（TIME_WAIT 端口复用）

执行：线上 compose patch（原文件备份 docker-compose.yml.bak.20260821-sysctl）
-> docker compose up -d --force-recreate --no-build web nginx cron。
```

## 验证

```text
修复前：最近 60 秒 14154 个 500（50%），Uncaught RedisException 持续；
修复后：最近 60 秒 5xx = 0，Redis 异常 = 0；
容器内端口范围 1024-65535、tcp_tw_reuse=1 生效；
容器 web/nginx/cron 全部 Up，load 2.70，业务正常。
```

## 后续建议

```text
1. 根治：应用层 Redis 改用 persistent 连接（pconnect）或连接池，
   从源头减少 TIME_WAIT 产生；
2. 观察高峰时段 5xx 与 /proc/net/tcp 连接数；
3. pointMall 索引已建，后续发布避免 N+1 查询；
4. 支付 curl 超时建议由后端从 40s 调短（如 10s）并加重试。
```

## 通知记录

```text
步骤 1：线上问题初步分析（php-fpm 当前 30 未打满，后台 200）
步骤 2：日志分析（无今日新致命错误，问题已缓解）
步骤 3：扩容后 PHP 参数优化方案（16核/30G）
步骤 4：配置同步线上，重启 web 容器生效
步骤 5：PHP 优化参数生效并验证
（后续偶发 500 专项排查步骤见下）
步骤 1：偶发 500 初步定位（pointMall 慢请求）
步骤 2：偶发 500 定位（pointMall Mongo 缺索引）
步骤 3：偶发 500 根因（Redis 连接端口耗尽）
步骤 4：偶发 500 修复（sysctls + 重建容器）
步骤 5：偶发 500 修复成功，5xx 归零
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
