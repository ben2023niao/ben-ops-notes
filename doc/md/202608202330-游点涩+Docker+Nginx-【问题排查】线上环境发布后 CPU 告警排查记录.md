---
id: "doc-c48e2a5e8402"
title: "【问题排查】线上环境发布后 CPU 告警排查记录"
date: "2026-08-20T23:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "监控告警", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2330-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%8F%91%E5%B8%83%E5%90%8ECPU%E5%91%8A%E8%AD%A6%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2330-【问题排查】线上环境发布后CPU告警排查记录.md"
sourceSha256: "227a5e62bb3ca127de4ae95edffa9697b3df850488f3bfd0efb0a5203b25b786"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境发布后 CPU 告警排查记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2330-【问题排查】线上环境发布后CPU告警排查记录.md`

> 整理日期：2026-08-20 23:30｜日期依据：文件名日期

文档日期：2026-08-20 23:30
环境：游点涩线上环境（main 分支）
分类：问题排查
标签：线上环境、CPU 告警、发布后高峰、php-fpm、nginx、QPS、bigDataJob

## 背景

2026-08-20 22:57 发布 `e91c91979d9d`（合并 feature/cike20260803大数据，
仅改动 `app/Services/Common/BigDataJobService.php`，大数据上报任务增加唯一 ID 防覆盖）。
发布成功（CICD 通知显示“队列：ok”，bigDataJob 校验生效）。
23:10 监控告警：CPU 99.5%（连续 3 次），web 容器 CPU 峰值 368.54%。

## 排查过程

```text
1. top / docker stats：
   - php-fpm 多进程均摊 6%-30% CPU（30 workers），无单一异常进程；
   - web 容器 CPU 峰值 368%，cron 1.68%，logbus-v2 0.43%。
2. nginx 访问日志（docker logs）：
   - 发布后 TOP 接口：tracking/record、configDict、system/info、
     AppVersion/latestVersion、recordPageVisit、game/detail、User/info 等；
   - 最近 60 秒约 1.76 万请求（约 290 QPS）；
   - 2 分钟 34788 个 200，21 个 404、14 个 499、0 个 5xx，无错误风暴。
3. php-fpm 配置：pm=dynamic，max_children=30，start_servers=8，
   max_spare=15，max_requests=500（4 核机器）。
4. 发布内容核对：e91c91979d9d 仅 BigDataJobService.php +11/-1（唯一 ID），
   不影响 tracking/record 主流程。
5. big_data_job 积压：wait=7（瞬时写入），failed=0，队列消费正常。
6. 发布前基线不可比：nginx 容器发布时重建，旧容器日志已清空。
```

## 根因

```text
发布重启后在线客户端（App/SDK）集中重新请求版本检查、配置、心跳、埋点上报等
接口，形成约 290 QPS 的瞬时高并发；4 核机器 + php-fpm max_children=30 被推至
处理上限，触发 CPU 告警。属发布期性能压力，非代码故障（错误率 0.1%、无 5xx）。
```

## 处置与验证

```text
无需干预，持续观察：
- web CPU：368% -> 285% -> 140%（约 20 分钟内回落 62%）；
- load：6.62 -> 5.36 -> 3.90；
- QPS 维持约 280 但 php-fpm 已正常消化，无 499/5xx 堆积；
- bigDataJob 队列守护稳定，积压未上涨。
```

## 后续建议

```text
1. 发布后 30 分钟内重点盯 CPU/负载，告警阈值可临时关注；
2. 评估 php-fpm max_children 按内存余量适度上调（当前 7.5G 内存、30 workers）；
3. 高频只读接口（configDict/system/info/latestVersion）评估缓存，
   降低发布回源冲击；
4. 评估发布错峰/灰度或预先扩容，避免集中回源打满；
5. 构建缓存基础镜像已由发布侧跟进（首次发布慢、后续几十秒）。
```

## 通知记录

```text
步骤 1：CPU 告警排查定位为发布后客户端集中回源高并发
步骤 2：CPU 高占用根因确认（约 290 QPS，无故障无错误风暴）
步骤 3：观察确认 CPU 显著回落，系统稳定
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
