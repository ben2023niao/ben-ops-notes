---
id: "doc-5f54d06752bc"
title: "线上环境 PHP 错误日志持久化、小时轮转与 20G 告警改造"
date: "2026-07-18T14:57:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-18-1457-%E3%80%90%E4%BC%98%E5%8C%96%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83PHP%E5%85%A8%E9%87%8F%E6%97%A5%E5%BF%97%E6%8C%81%E4%B9%85%E5%8C%96%E4%B8%8E20G%E5%91%8A%E8%AD%A6%E6%94%B9%E9%80%A0.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-18-1457-【优化+架构改造】线上环境PHP全量日志持久化与20G告警改造.md"
sourceSha256: "362d84b0eda4c2a81318ae6bce84df1c0e789218b0509519f6d0d965e2d51384"
sourceSystem: "project-doc"
---

# 线上环境 PHP 错误日志持久化、小时轮转与 20G 告警改造

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-18-1457-【优化+架构改造】线上环境PHP全量日志持久化与20G告警改造.md`

> 整理日期：2026-07-18 14:57｜日期依据：文件名日期

文档日期：2026-07-18 14:57
环境：游点涩线上环境（main 分支）
分类：优化+架构改造

通知群：18GAME_ 上线群（正式環境）

## 改造目标

1. 参考 `dev` 分支已验证的 PHP 日志改造，在线上保留 PHP CLI、OPcache、PHP-FPM master、worker 和 slowlog 错误类日志。
2. 日志统一落到宿主机 `runtime/app-logs`，容器重建后仍保留。
3. 关闭全量 PHP-FPM access 日志，将 FPM `log_level` 从 `debug` 降到 `warning`。
4. 将业务日志目录告警边界从 `2G` 调整为 `20G`，只告警，不自动删除日志。
5. 增加小时轮转：普通日志 gzip 本地归档，access 日志截断丢弃，大错误日志分片发 Telegram 成功后删除本地归档。
6. 每完成一步立即通知正式群，消息标识为“线上环境”，通知名单增加 `@Daviea2`。

## 配置和持久化路径

| 日志类型 | 容器内路径 | 说明 |
| --- | --- | --- |
| PHP CLI/定时任务错误 | `runtime/logs/php/php-error.log` | `E_ALL`、启动和运行错误 |
| OPcache 错误 | `runtime/logs/php/php-opcache-error.log` | 与业务/CLI 错误分开 |
| FPM master | `runtime/logs/php-fpm/master-error.log` | `warning` 级别 |
| FPM worker | `runtime/logs/php-fpm/worker-error.log` | 捕获 worker 错误和 stdout/stderr |
| FPM access | `runtime/logs/php-fpm/access.log` | 不再保留全量 access；小时任务发现后直接截断 |
| FPM slowlog | `runtime/logs/php-fpm/slow.log` | 超过 3 秒记录，堆栈深度 50，不终止请求 |
| 队列守护 | `runtime/logs/queue/` | 保留现有 watchdog 和 worker 日志 |
| 外部定时任务 | `runtime/logs/cron/` | 保留现有单任务日志 |

容器内 `runtime/logs` 由 Compose bind mount 到线上后端宿主机：

```text
/opt/docker-youdianse-php/runtime/app-logs
```

## 实现要点

- `php/dev.ini`：关闭页面错误显示，开启 `log_errors`、`E_ALL`、内存泄漏报告，分别设置 PHP 和 OPcache 错误日志。
- `php/fpm-logging.conf`：FPM `log_level=warning`、worker 输出捕获、3 秒 slowlog；不配置全量 access 日志。
- `docker-compose.yml`：把 FPM 日志配置挂载到 `/usr/local/etc/php-fpm.d/zz-youdianse-logging.conf`。
- `docker-compose.yml`：仅为 web 容器增加 `SYS_PTRACE`，使 FPM master 能对超时 worker 生成 slowlog 堆栈；不开启 privileged，不关闭整套 seccomp。
- `entrypoint/web-entrypoint.sh` 和 `entrypoint/cron-entrypoint.sh`：启动前创建日志目录和文件，校正为 `www-data`。
- `cicd-web/core.py`：把 FPM 配置加入发布元数据、运行配置差异检查和 no-build 配置同步。
- `cicd-web/config/settings.json`：`defaults.app_log_alert_gb` 设为 `20`。
- `ops/production/scripts/youdianse-app-log-hourly-rotate.py`：小时轮转 `runtime/app-logs`，错误日志超过阈值时分片发 Telegram，发送成功后删除本地归档。

## PHP 主配置基线

`php/dev.ini` 是当前线上 web 和 cron 容器共用的 PHP 主配置：

```ini
; 游点涩线上环境 PHP 配置。
; PHP CLI 错误写入 php/php-error.log；PHP-FPM worker 会由
; php/fpm-logging.conf 覆盖到 php-fpm/worker-error.log。
memory_limit=512M
upload_max_filesize=50M
post_max_size=50M
display_errors=Off
display_startup_errors=Off
error_reporting=E_ALL
log_errors=On
error_log=/var/www/html/youdianse-php/runtime/logs/php/php-error.log
ignore_repeated_errors=Off
ignore_repeated_source=Off
report_memleaks=On
html_errors=Off
date.timezone=Asia/Shanghai

; 单独保留 OPcache 错误，方便和业务/CLI 错误区分。
opcache.error_log=/var/www/html/youdianse-php/runtime/logs/php/php-opcache-error.log
```

这份配置已整理并发送到“18GAME_ 上线群（正式環境）”。

## 2026-07-22 降噪与小时轮转补充

2026-07-22 已完成线上降噪和轮转：

```text
FPM log_level：warning
FPM access.log：不再配置，历史 access.log 首轮轮转已直接截断
PHP display_errors/display_startup_errors：Off
小时轮转脚本：ops/production/scripts/youdianse-app-log-hourly-rotate.py
root crontab：每小时第 12 分钟执行，flock 防重入
错误日志发送阈值：32M
Telegram 分片上限：45M
```

首轮真实执行结果：

```text
runtime/app-logs：约 27G -> 2.4G
根盘：约 81% -> 30%
轮转文件：53
发送并清理：1 个大错误日志归档（php-fpm/master-error.log.gz）
直接丢弃：1 个 access 归档
失败：0
```

## 本地验证记录

2026-07-18 已完成：

- Python 语法、Shell 语法、JSON 和 `git diff --check` 通过。
- `docker compose config` 成功，已识别 FPM 日志配置挂载和 `runtime/app-logs` 持久化挂载。
- CICD 配置解析确认默认告警阈值为 `20G`，`main` 已选中 `php/fpm-logging.conf`。
- 使用官方 `php:7.4-fpm` 镜像解析全部配置成功。
- 真实启动 FPM master 和 2 个 `www-data` worker 成功，master debug 日志已落盘。
- 主动触发 PHP CLI warning，标记成功写入 `php/php-error.log`。

## 线上发布后验证

```bash
cd /opt/docker-youdianse-php

sudo docker compose --env-file .ops-build.env --profile cron config >/tmp/youdianse-compose-main-check.yml
sudo docker exec youdianse-main-php-web php-fpm -tt
sudo docker exec youdianse-main-php-web php -i | grep -E 'display_errors|display_startup_errors|error_reporting|log_errors|error_log|opcache.error_log'
sudo docker exec youdianse-main-php-web sh -lc 'find /var/www/html/youdianse-php/runtime/logs/php /var/www/html/youdianse-php/runtime/logs/php-fpm -maxdepth 1 -type f -ls'
sudo docker top youdianse-main-php-web -eo pid,ppid,user,comm,args
sudo docker top youdianse-main-php-cron -eo pid,ppid,user,comm,args
du -sh runtime/app-logs
curl -I http://203.0.113.1:8088/admin1866/login
```

线上按以下项目主动验证：

1. Web 请求后 `php-fpm/access.log` 不再增长。
2. 超过 3 秒的 PHP 请求会把堆栈写入 `slow.log`。
3. worker 错误会写入 `worker-error.log`。
4. 强制重建 `web/nginx/cron` 后，重建前的验证标记仍存在。
5. CICD 运行日志输出当前大小与 `20G` 阈值。
6. root crontab 小时轮转任务存在，并能用 `flock` 防重入。

## 线上实测结果

2026-07-18 已全部完成：

```text
运维版本：9325420
业务版本：66d701bf852a
镜像：youdianse-php:main-66d701bf852a
容器：youdianse-main-php-web / nginx / cron
日志大小：11G
告警阈值：20G
```

- 线上发布和二次强制重建均成功，HTTP 200、Session writable、Redis/MongoDB/hosts 正常。
- PHP CLI warning 已写入 `php/php-error.log`。
- FPM worker error 已写入 `php-fpm/worker-error.log`，worker stderr 已被 master 捕获。
- 2026-07-18 曾启用全量 `access.log`；2026-07-22 已关闭全量 access，仅保留慢请求与错误类日志。
- 首次实测发现 Docker 默认安全策略拒绝 FPM master `ptrace` worker，因此只能识别慢请求，不能写堆栈。为 web 容器最小化增加 `SYS_PTRACE` 后，`slow.log` 从 0 增长到 159 字节并包含调用栈，已无 `Operation not permitted`。
- 强制重建 web/nginx/cron 后三个容器 ID 全部变化，重建前的 CLI、worker error、worker stderr 和 slowlog 标记仍存在，持久化验证通过。
- web 实际运行 FPM master 和动态 worker；cron 实际运行 `crontab queue` 和 `job queue` 两条 PHP 队列进程。
- CICD 发布、配置同步和通知名单均已增加 `@Daviea2`。
- 宝塔、后端、前端三台线上服务器的 `/etc/youdianse-health-alert.json` 与 `/usr/local/sbin/youdianse-server-health-alert.py` 已同步 `@Daviea2`；后端小时汇总脚本也已同步。三台均通过 Python 编译、JSON 解析和 `--json` 无通知实测，原配置备份保留。

## 风险与维护

- 普通业务日志仍会写入 `runtime/app-logs`，小时任务默认不再压缩或截断 `api_request`、`api_response`、当天业务日志、队列日志等普通业务日志；若目录总量接近 20G，原有 Telegram 告警仍会提醒。
- 小时任务默认只处理 `runtime/app-logs/php` 与 `runtime/app-logs/php-fpm`：`php-fpm/access.log` 直接截断丢弃，达到阈值的 `error`/`slow` 日志切割发送 Telegram，发送成功后删除服务器本地归档。
- 20G 告警不会自动清理；删除或清空日志前必须先确认排障价值。
- FPM 配置错误会阻止 web 容器启动，发布前和发布后都必须执行 `php-fpm -tt`。
- `SYS_PTRACE` 仅用于 FPM slowlog 读取同容器 worker 堆栈；若移除该 capability，FPM 仍会识别慢请求，但会因 `Operation not permitted` 无法写入调用栈。
- 回滚时使用 CICD 选择上一个已验证的运维版本和业务 git id 重新发布，不删除宿主机 `runtime/app-logs`。

## 通知规则

根目录 `AGENTS.md` 已固定：后续每完成一步必须立即通知“18GAME_ 上线群（正式環境）”，标题使用 `【线上环境｜步骤 N 完成】`，失败不得静默跳过。统一通知：

```text
@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2
```
