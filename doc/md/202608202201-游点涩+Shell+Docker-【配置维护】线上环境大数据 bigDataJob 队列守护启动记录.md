---
id: "doc-80a52f50dc14"
title: "【配置维护】线上环境大数据 bigDataJob 队列守护启动记录"
date: "2026-08-20T22:01:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2201-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%A4%A7%E6%95%B0%E6%8D%AEbigDataJob%E9%98%9F%E5%88%97%E5%AE%88%E6%8A%A4%E5%90%AF%E5%8A%A8%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2201-【配置维护】线上环境大数据bigDataJob队列守护启动记录.md"
sourceSha256: "aadbb17666018d2f62f2090eb052ffba7a926b681d2913fa43d05a8298eb351c"
sourceSystem: "project-doc"
---

# 【配置维护】线上环境大数据 bigDataJob 队列守护启动记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2201-【配置维护】线上环境大数据bigDataJob队列守护启动记录.md`

> 整理日期：2026-08-20 22:01｜日期依据：文件名日期

文档日期：2026-08-20 22:01
环境：游点涩线上环境（main 分支）
分类：配置维护 / 问题修复
标签：线上环境、大数据上报、bigDataJob、队列守护、QUEUE_WORKERS、MongoDB

## 背景

开发新增大数据上报实时队列（`bigDataJob queue`），生产必须常驻消费。由于线上 cron 容器
由 `entrypoint/queue-watchdog.sh` + 环境变量 `QUEUE_WORKERS` 统一守护队列进程，而
`docker-compose.yml` 中该变量未包含 `bigDataJob:queue`，导致新队列一直没有启动，
`big_data_job` 集合积压约 12.1 万条等待任务。

业务提交：`7d3c9f9c`（含 `app/Tasks/BigDataJobTask.php`，消费命令：
`php bin/shell.php bigDataJob queue [queueName] [drive] [serverName]`）。

## 调整内容

```text
docker-compose.yml（cron 服务）：
  QUEUE_WORKERS: "crontab:queue job:queue"
              -> "crontab:queue job:queue bigDataJob:queue"

守护方式：watchdog 将 bigDataJob:queue 映射为
  php /var/www/html/youdianse-php/bin/shell.php bigDataJob queue
  每轮运行 297 秒，退出后 5 秒自动重启，日志写入 runtime/logs/queue/bigDataJob-queue.log
```

线上同步：`/opt/docker-youdianse-php/docker-compose.yml` 已同步修改，
原文件备份为 `docker-compose.yml.bak.20260820-bigdata`；
已执行 `docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build cron`
重启 cron 容器（业务代码已在线上仓库，无需重新构建镜像）。

## 验证

```text
1. 进程：cron 容器内出现 shell.php bigDataJob queue（与 crontab queue、job queue 并存）；
2. watchdog 日志：starting workers: crontab:queue job:queue bigDataJob:queue；
3. 消费日志：bigDataJob-queue.log 持续输出 RegisterReportJob / AppLogReportJob /
   DownloadReportJob / GameRegisterReportJob =>success；
4. Mongo big_data_job 积压（status=0）：
   21:56 启动时  121088
   21:58 首查    104074（约 90 秒消费 1.7 万）
   22:01 复查     75172（持续下降，failed=0）
5. TE 日志：runtime/logs/te.log.2026-08-20-22_0 已生成，22 点档数据正常落盘，
   由 logbus2 继续推送 TE 平台。
```

说明：消费成功的任务由 `BigDataJobService::executeQueue` 执行后
`BigDataJobModel::deleteById($_id)` 删除（不入成功态），失败才置 status=-1，
因此以 wait 数量下降作为消费验证指标，成功日志以 bigDataJob-queue.log 为准。

## 后续

```text
1. 观察 big_data_job 积压直至清空，确认 failed 数量持续为 0；
2. 若出现失败任务：php bin/shell.php bigDataJob retryFailed 重置后由守护进程重试；
3. 后续新增队列需同步维护 docker-compose.yml 的 QUEUE_WORKERS；
4. 开发侧 compose.dev.json / 后续代码发布时，需保证容器仍包含本配置（compose 由运维仓库维护）。
```

## 通知记录

```text
步骤 1：确认发布问题与当前状态
步骤 2：本地配置修改 QUEUE_WORKERS 增加 bigDataJob:queue
步骤 3：线上同步配置并重启 cron 容器，bigDataJob queue 已开始消费
汇总：见群内最终总结
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
