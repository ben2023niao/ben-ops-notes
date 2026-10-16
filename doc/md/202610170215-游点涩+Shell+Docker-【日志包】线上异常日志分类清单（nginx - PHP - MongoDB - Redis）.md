---
id: "doc-5b5d3fb54977"
title: "【日志包】线上异常日志分类清单（nginx / PHP / MongoDB / Redis）"
date: "2026-10-17T02:15:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "Redis", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0215-%E3%80%90%E6%97%A5%E5%BF%97%E5%8C%85%E3%80%91%E5%BC%82%E5%B8%B8%E6%97%A5%E5%BF%97%E5%88%86%E7%B1%BB%E6%B8%85%E5%8D%95%EF%BC%88nginx-PHP-MongoDB-Redis%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0215-【日志包】异常日志分类清单（nginx-PHP-MongoDB-Redis）.md"
sourceSha256: "1ef7cb069edba4574ebbb2df6b860ba1dd8be21b6ec03720921fae10a7ef367d"
sourceSystem: "project-doc"
---

# 【日志包】线上异常日志分类清单（nginx / PHP / MongoDB / Redis）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-17-0215-【日志包】异常日志分类清单（nginx-PHP-MongoDB-Redis）.md`

> 整理日期：2026-10-17 02:15｜日期依据：文件名日期

- 采集时间：2026-10-17 02:10 ~ 02:15（北京时间）
- 采集方式：服务器本地只读取证（未改动任何配置与数据）
- 背景：开发再次更新代码后，后端与数据库流量仍高（后端 ens5 入 ~65 MB/s、从库01 出 ~63 MB/s、主库仅 2~3 MB/s）
- 处理原则：**只保留异常行，剔除正常噪音**；每类日志一个独立压缩包

## 一、已发群的 6 个分类包

| 序号 | 包名 | 内容 | 条数 | 大小 |
| --- | --- | --- | ---: | ---: |
| 1 | `1-nginx后端.zip` | `01-后端nginx-error-异常.log`（仅 `[error]` 7,612 + `[emerg]` 2，已剔除 `[warn]` 53,571 行与 `[notice]` 829 行）、`02-后端nginx-异常请求.log`（状态码 ≥400 原始行） | 7,620 / 1,591 | 2.2 MB / 315 KB |
| 2 | `2-网关nginx.zip` | `07-网关nginx-error-异常.log`（`[error]` 级；其中 `limiting connections by zone "perip_ssr"` 约 6.3 万次）、`08-网关-异常请求.log` | 63,537 / 7,031 | 15.7 MB / 1.5 MB |
| 3 | `3-PHP应用.zip` | `03-PHP应用-异常日志.log`：10-16 1,865 行 + 10-17 342 行，全部 `level=ERROR` | 2,224 | 706 KB |
| 4 | `4-PHP-FPM.zip` | `04-php-fpm-异常.log`（scoreboard 1,021 / seems busy 2,307 / max_children 486 / 其它 498）、`05-php-fpm-缓慢请求.log`（27,250 条 executing too slow，含接口聚合 TOP25）、`06-php-fpm-慢调用栈-按栈去重.log`（原始栈去重，每栈留最近 5 条） | 4,318 / 27,255 / 20,490 | 582 KB / 5.7 MB / 1.5 MB |
| 5 | `5-MongoDB.zip` | `09-MongoDB-异常.log`（复制集/读放大/网络/热点集合/写失败）、`10-当前流量快照.txt` | — | 88 KB |
| 6 | `6-Redis.zip` | `11-Redis-异常.log`（SLOWLOG 128 条原始 + 指标异常 + 30 秒 MONITOR 危险命令） | 154 | 17 KB |

## 二、本次抽出来的关键异常（给开发直接对应代码）

### 2.1 MongoDB

```
逐节点读放大（15 秒窗口，directConnection 直连）
  主库   203.0.113.1：网络出 2.5 MB/s | query 327.6/s getmore 356.6/s 写 85.5/s
                       scanned 1,059,259/s → returned 1,012/s = 放大 1,047 倍  ← 异常
  从库01 203.0.113.1：网络出 63.2 MB/s | 放大 3.3 倍
  从库02 203.0.113.1：网络出 0 MB/s   | 放大 7.7 倍（基本空闲，query 2.9/s）

热点集合累计 queries：game_category 14.41 亿、game 2.72 亿、user 2.24 亿、adv 2.19 亿、
                     user_task_list 1.42 亿、app_version 1.39 亿、user_sign_config 1.33 亿

写失败（新增，17 条）：insert job / user_game_follow 报错，
  error 指向 app/Core/Mongodb/MongoModel.php line 238 且异常信息为空
```

### 2.2 PHP

```
slow_api（10-16 1,792 条 / 10-17 304 条）：recharge/create 占绝大多数，其次 spend/create2
check_host_sign_failed（10-17 21 条）：step = hosts_list_empty / decrypt_host_sign_empty
php-fpm：executing too slow 27,250 条；failed to acquire scoreboard 1,021 条
```

### 2.3 Redis

```
SLOWLOG 128 条：KEYS 126 条，单次 0.3~0.67 秒，平均 129 秒一次
  token_user（登录踢下线）102 次、tracking 12、tracking_guest_dl 9、product_click 5
连接风暴：20 秒新建 5,984 个连接（≈299/秒），连接不复用
内存 1.02 GB、maxmemory 未设置、淘汰 0、命中率 92.29%
```

### 2.4 nginx

```
后端 error.log：[error] 7,612（含 connect() failed 长尾）、[emerg] 2
后端 access：状态码 ≥400 1,591 行（404 为主）
网关 error.log：limiting connections by zone "perip_ssr" ≈6.3 万次 + upstream prematurely closed 59 + recv() failed 36
```

## 三、同时刻流量快照（2026-10-17 02:10~02:15）

| 节点 | 入/出 | CPU |
| --- | --- | --- |
| 后端 16.209.16.108 | 入 69.35 MB/s / 出 4.58 MB/s（php-web 容器入 75.09 MB/s） | 12% |
| 从库01 203.0.113.1 | 出 59.7~68.0 MB/s / 入 1.0~1.2 MB/s | 7~11% |
| 主库 203.0.113.1 | 出 1.6~3.0 MB/s / 入 0.6 MB/s | 16~27% |
| 从库02 203.0.113.1 | 出 0.2 MB/s | 4~8% |
| 网关 16.208.38.88 | 入 7.2~8.0 MB/s / 出 15.8~18.0 MB/s | 49~58% |

结论：代码更新后流量结构没变——后端仍在从 Mongo 读约 65 MB/s，且**主库读放大涨到 1,047 倍**（主库自己只输出 2~3 MB/s，却每秒扫描 106 万索引键）；从库02 依旧没有承接读流量。

## 四、待开发处理优先级

1. `MongoModel.php:238` 的写失败（异常信息为空，建议补上下文日志并复现）
2. 主库那 ~327 query/s 的重查询定位（开 profiling 采样，确认哪些只读查询没走 `on('slave')`）
3. `game_category` / `user_sign_config` / `app_version` / `user_task_list` 等配置集合进缓存（Redis 已有能力）
4. 读流量均分到从库02
5. Redis：`KEYS` 改 `SCAN`/Set 索引（登录踢下线 102/126 次）、开启连接复用
