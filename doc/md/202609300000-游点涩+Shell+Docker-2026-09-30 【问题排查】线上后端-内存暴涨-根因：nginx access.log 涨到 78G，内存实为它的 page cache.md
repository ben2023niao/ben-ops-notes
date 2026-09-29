---
id: "doc-dc6503af28d9"
title: "2026-09-30 【问题排查】线上后端\"内存暴涨\"根因：nginx access.log 涨到 78G，内存实为它的 page cache"
date: "2026-09-30T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E5%90%8E%E7%AB%AF%E5%86%85%E5%AD%98%E6%9A%B4%E6%B6%A8%E6%A0%B9%E5%9B%A0-nginx%E6%97%A5%E5%BF%9778G%E5%8D%A0page%20cache.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-【问题排查】线上后端内存暴涨根因-nginx日志78G占page cache.md"
sourceSha256: "67352796b93cc2dcae2304c3922b8d2940b138cd388853d79b21a2afbe8f48e7"
sourceSystem: "project-doc"
---

# 2026-09-30 【问题排查】线上后端"内存暴涨"根因：nginx access.log 涨到 78G，内存实为它的 page cache

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-09-30-【问题排查】线上后端内存暴涨根因-nginx日志78G占page cache.md`

> 整理日期：2026-09-30 00:00｜日期依据：文件名日期

环境标签：线上环境（正式）
时间：2026-09-30 10:00 ~ 10:20（北京时间）

## 一、现象

CPU 已回落（刷量被压制），但监控上**内存占用明显上涨**：后端容器
`youdianse-main-php-nginx` 显示 9.79 GiB（32%）。

## 二、定位过程

1. 宿主机 `free`：used 仅 2.3 GB、buff/cache 28 GB → 内存不是"被进程吃掉"
2. 容器内存构成（cgroup v2 `memory.stat`）：

```text
anon   = 35 MB      ← 真实进程内存（很小）
file   = 25.1 GB    ← page cache（几乎全部）
kernel = 128 MB
memory.current = 25.28 GB
```

3. nginx worker：16 个进程合计 RSS 仅 91 MB → 没有泄漏
4. 日志目录：`/opt/docker-youdianse-php/runtime/nginx-logs/access.log` = **78 GB**
   → 结论：容器"内存"里那 25 GB 全是这个巨型日志文件的 page cache
5. 根因：**后端 nginx 日志没有轮转**（既没有 logrotate 也没有 S3 归档），
   加上此前登录刷量写入量大，日志一路涨到 78 GB

## 三、处置

| 项 | 动作 |
| --- | --- |
| 立即 | `truncate -s 0` 截断 access.log（copytruncate 方式，nginx 无需重启）→ 容器内存 9.79 GiB → **41 MB**，/data 释放 78 G（101G → 23G） |
| 持久化 1 | 新增 `/etc/logrotate.d/youdianse-backend-nginx`：`size 200M / rotate 5 / compress / copytruncate`，cron 每 15 分钟检查 |
| 持久化 2 | 新增 ben-bot 脚本 `youdianse-backend-log-s3-archive.sh`：超过 24 小时的 .gz 上传 `s3://youdianse-prod-gateway-logs/backend/` 后删除本地，cron 每 6 小时 |
| 顺带治理 | 后端业务日志（PHP 写的 api_request/api_response/big_data_click，每天约 5G）新增 logrotate：`size 500M / rotate 3 / compress / copytruncate`，cron 每 15 分钟 |

## 四、验证

- 容器内存：nginx **41 MB**、web 205 MB、cron 46 MB、logbus 40 MB（全部正常水位）
- 宿主机：used 2.3 GB / available 28 GB
- 磁盘：/data 23G / 492G（释放 78G）
- 业务回归：www api 200、h5 页面 200、登录接口 200

## 五、结论与经验

1. **Docker/Beszel 显示的"容器内存"包含 page cache**（读写大日志产生），
   不等于进程真实占用；排查时先看 `memory.stat` 的 anon 与 file 构成
2. 线上每个写日志的组件都应有**轮转 + 远端归档**：本次事故前，网关与宝塔已有轮转，
   唯独**后端漏了**，导致 78G 日志 → 内存虚高 + 磁盘占用
3. 后续巡检建议把「日志目录大小」纳入例行检查（本仓 `youdianse-*-log-s3-archive.sh`
   已覆盖网关 / 宝塔 / 后端三处）
