---
id: "doc-81d3424e6b12"
title: "线上环境 PHP-FPM 参数与服务器性能分析"
date: "2026-07-23T16:13:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-23-1613-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83PHP-FPM%E5%8F%82%E6%95%B0%E4%B8%8E%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-23-1613-【优化】线上环境PHP-FPM参数与服务器性能分析.md"
sourceSha256: "df6d53a4c23b04ae47deb0fb66c8bfbb6fb312fb87a6d976c950354f24aebdd5"
sourceSystem: "project-doc"
---

# 线上环境 PHP-FPM 参数与服务器性能分析

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-23-1613-【优化】线上环境PHP-FPM参数与服务器性能分析.md`

> 整理日期：2026-07-23 16:13｜日期依据：文件名日期

文档日期：2026-07-23 16:13
环境：游点涩线上环境（main 分支）
分类：优化

## 任务范围

本次只读研究线上 PHP 参数和服务器真实性能参数，不修改线上配置。

参考材料：`/Users/ben/Downloads/Write PHP-FPM慢请求分析与优化报告.txt`

## 线上版本

- 运维仓库：`25ab566`
- 业务镜像：`youdianse-php:main-20ac0f839734`
- 容器：`youdianse-main-php-web`、`youdianse-main-php-nginx`、`youdianse-main-php-cron`

## 服务器真实性能参数

- CPU：4 vCPU，Intel Xeon Platinum 8275CL @ 3.00GHz
- 拓扑：1 socket、2 cores/socket、2 threads/core
- 内存：7.5GiB
- 当前可用内存：约 5.7GiB
- Swap：0
- Docker 限制：web/cron/nginx 均未设置单独 CPU/内存限制，共享宿主机资源
- 采集时负载：0.83 / 0.66 / 0.61

采集时容器瞬时占用：

| 容器 | CPU | 内存 | PIDs |
| --- | ---: | ---: | ---: |
| web | 41.32% | 45.89MiB | 4 |
| cron | 0.02% | 25.23MiB | 6 |
| nginx | 2.74% | 6.83MiB | 5 |

## PHP 与 FPM 当前参数

FPM SAPI 参数：

| 参数 | 当前值 |
| --- | ---: |
| `memory_limit` | `512M` |
| `max_execution_time` | `30` |
| `max_input_time` | `-1` |
| `post_max_size` | `50M` |
| `upload_max_filesize` | `50M` |
| `opcache.enable` | `On` |
| `opcache.memory_consumption` | `128` |

FPM pool 当前使用官方镜像默认配置：

```ini
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
;pm.max_requests = 500
```

当前已配置：

```ini
request_slowlog_timeout = 3s
slowlog = /var/www/html/youdianse-php/runtime/logs/php-fpm/slow.log
```

当前未配置：

```ini
request_terminate_timeout
```

## FPM 进程真实内存

采集时 3 个 worker：

| Worker | RSS | PSS | Private Dirty |
| --- | ---: | ---: | ---: |
| worker 1 | 34.1MiB | 10.6MiB | 2.9MiB |
| worker 2 | 38.2MiB | 12.6MiB | 3.8MiB |
| worker 3 | 33.8MiB | 10.5MiB | 2.9MiB |

说明：

- `memory_limit=512M` 是单请求脚本可用内存上限，不代表每个 worker 常驻都会占用 512M。
- 当前空闲/轻载 worker RSS 约 34-39MiB，PSS 约 10.5-12.6MiB。
- 容量估算要同时看保守上限和实际业务峰值。当前没有压测下 worker 峰值内存样本，因此不能直接按 30-40MiB 放大到很高。

## 触顶证据

`master-error.log` 中：

- `reached pm.max_children` 总计：203 条
- 2026-07-22：75 条
- 2026-07-23：128 条

按小时高峰：

| 小时 | 次数 |
| --- | ---: |
| 2026-07-23 00 | 70 |
| 2026-07-22 23 | 28 |
| 2026-07-23 01 | 17 |
| 2026-07-22 16 | 15 |
| 2026-07-23 15 | 13 |
| 2026-07-22 22 | 11 |

结论：`pm.max_children=5` 明显过小，不只是高峰触顶，凌晨低峰也会触顶。

## pm.max_children 粗算

按后端提出的参考公式：

```text
总内存 / 单个 PHP 最大内存
```

当前：

```text
7.5GiB / 512MiB ≈ 15
```

但不能把整机内存都给 PHP worker，需要给系统、Docker、nginx、cron、OPcache 共享段、文件缓存、日志、发布构建和突发留余量。

按预留内存估算：

| 预留 | 可用于 PHP worker | 按 512M 粗算 |
| ---: | ---: | ---: |
| 2GiB | 约 5.5GiB | 约 11 |
| 3GiB | 约 4.5GiB | 约 9 |

按这个保守公式，`pm.max_children` 的安全参考区间是 `9-11`。

## 运维建议

建议不要直接按理论最大值 15 配满。结合当前 4 vCPU、无 Swap、已有同步阻塞慢请求、以及 worker 实际 RSS 远低于 512M，建议分阶段：

第一阶段止血：

```ini
pm = dynamic
pm.max_children = 10
pm.start_servers = 3
pm.min_spare_servers = 2
pm.max_spare_servers = 5
pm.max_requests = 500
request_terminate_timeout = 60s
```

理由：

- 从 5 提到 10，可把短期并发 worker 容量翻倍，直接缓解排队放大效应。
- 10 落在按 `memory_limit=512M` 且预留 2-3GiB 后的保守范围内。
- 4 vCPU 环境下，不宜先上过高 worker 数，否则 CPU 密集型导出/聚合会加重上下文切换。
- `pm.max_requests=500` 可降低长期运行内存泄漏风险。
- `request_terminate_timeout=60s` 用于防止极端请求长期占用 worker；具体值需确认是否存在合法超过 60 秒的导出/批处理 HTTP 请求。

第二阶段观察 24 小时：

- `master-error.log` 中 `reached pm.max_children` 是否显著下降。
- `slow.log` 慢请求数量和堆栈类型是否变化。
- `docker stats` 中 web 容器内存是否稳定。
- `dmesg` / Docker 是否出现 OOM 迹象。
- 后台导出、批处理等长请求是否被 `request_terminate_timeout` 影响。

如果仍频繁触顶且内存稳定，可再评估 `pm.max_children=12`。如果 CPU 长期打满，应优先处理同步 curl、Mongo 索引、Excel 导出和批处理同步阻塞，而不是继续增加 worker。

## 研发侧同步建议

报告里列出的 P1/P2 问题仍应继续处理：

- `CommonUtil::initCurl` 增加连接超时，收紧总超时。
- MongoDB 补索引：`user.is_disabled`、`account_detail.created_at + type`。
- 后台首页统计改预聚合/缓存。
- Excel 导出、`resetData` 批处理移出 HTTP 请求线程。

运维调大 FPM worker 只能缓解排队，不会消除慢请求根因。
