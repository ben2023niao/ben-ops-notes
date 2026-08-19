---
id: "doc-8f5f8d7bb3ac"
title: "【运维记录】线上环境 nginx 与 PHP 容器错误日志汇总"
date: "2026-08-20T04:26:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0426-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83nginx%E4%B8%8EPHP%E5%AE%B9%E5%99%A8%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E6%B1%87%E6%80%BB.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0426-【运维记录】线上环境nginx与PHP容器错误日志汇总.md"
sourceSha256: "9a2c266052d5f9431b869868fc66bc0ab4f7a3984725018ecde12d386dce4156"
sourceSystem: "project-doc"
---

# 【运维记录】线上环境 nginx 与 PHP 容器错误日志汇总

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0426-【运维记录】线上环境nginx与PHP容器错误日志汇总.md`

> 整理日期：2026-08-20 04:26｜日期依据：文件名日期

文档日期：2026-08-20 04:26
环境：游点涩线上环境（main 分支）
分类：运维记录
标签：线上环境、nginx 错误日志、PHP-FPM、php-error、错误汇总

## nginx 错误日志

### 新网关 16.208.38.88（/var/log/nginx/error.log，1382 行）

```text
[alert] 469：worker_connections 打满（全部修复前，最后 08-20 01:00:06）
[error] 约 906：
  修复前：上游连接失败 connect/recv 111/104（连宝塔/本地超时）
  修复后：/nginx_status 外部探测被拒（访问控制，正常）、acme 校验 404
[crit] 5：SSL bad key share（客户端 TLS 参数问题，非服务端）
最近真实错误：无；仅扫描探测被拒（最近 04:20）
```

### 宝塔 16.208.5.147（/www/server/nginx/logs/error.log，235,724 行）

```text
[warn] 235,410：h5.youdianse.com 重复 server_name（历史已知，每分钟噪音）
[emerg] 2（06-16 历史重复 location，已修复）、[error] 1（06-16 nginx.pid 历史）
近期无真实错误
```

### 后端 nginx 容器

```text
无 error 级日志；仅请求体/响应缓冲临时文件警告 + 少量 499
```

## PHP 容器/框架错误日志（runtime/app-logs）

### php-error.log（401KB，近24h 12 条）

```text
全部为每小时 1 条：TrackingService::syncPageVisitToDatabase error（消息为空）
另有 08-13 大数据 getTdAnalytics env 配置 fatal（已修复）
```

### php-fpm/master-error.log（1.5MB，近24h 1267 条 WARNING）

```text
FPM 子进程脚本执行超时/异常，多为 /admin1866/user/excel 等管理端导出请求
（约 53 条/小时，占用 worker 资源）
```

### php-fpm/worker-error.log（10.8KB，35 条 PHP Fatal）

```text
Allowed memory size 128M exhausted，集中在 MongoDbConnection
（08-19 18:09 / 20:22 两个时间点）
注意：php/dev.ini 配置 memory_limit=512M，部分请求仍按 128M 执行，需核对生效范围
```

### php-fpm/slow.log（5.5MB，5342 条慢请求 >3s）

```text
以管理端导出/复杂查询为主
```

### 业务大数据日志（big_data_*）

```text
近24h error 标记：0
```

## 结论与建议

```text
1. nginx：当前无真实错误，历史告警已在 02:57 修复后归零。
2. PHP 侧为性能/稳定性隐患（与登录故障无关）：
   a) 管理端导出（/admin1866/user/excel）引发 FPM 超时 WARNING 与慢日志；
   b) MongoDbConnection 128M OOM（核对 memory_limit 生效范围）；
   c) TrackingService::syncPageVisitToDatabase 小时级任务报错（消息为空，需排查）。
建议排期处理以上三项。
```

## 通知记录

```text
nginx 错误日志汇总   message_id 9991
PHP 错误日志汇总     message_id 9992
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值；日志样例已脱敏。
