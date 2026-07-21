---
id: "doc-594f72ca4f4a"
title: "测试环境 PHP 错误日志持久化、小时轮转与 5G 告警改造"
date: "2026-07-22T09:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "监控告警", "自动化", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0900-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83PHP%E9%94%99%E8%AF%AF%E6%97%A5%E5%BF%97%E6%8C%81%E4%B9%85%E5%8C%96%E5%B0%8F%E6%97%B6%E8%BD%AE%E8%BD%AC%E4%B8%8E5G%E5%91%8A%E8%AD%A6%E6%94%B9%E9%80%A0.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0900-【优化】测试环境PHP错误日志持久化小时轮转与5G告警改造.md"
sourceSha256: "3e242d3aff3d609aaf2ab7cba51cd8838e041624558ead3095b821be85e05604"
sourceSystem: "project-doc"
---

# 测试环境 PHP 错误日志持久化、小时轮转与 5G 告警改造

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0900-【优化】测试环境PHP错误日志持久化小时轮转与5G告警改造.md`

> 整理日期：2026-07-22 09:00｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-22
环境：游点涩测试环境（dev 分支）
分类：优化

参照：`/Users/ben/Documents/ben/docker/main/docker-youdianse-php/docs/20260718-线上环境PHP全量日志持久化与20G告警改造.md` 的最新 main 工作副本。

## 改造目标

1. 复用测试环境 2026-07-18 已验证的日志持久化基础。
2. 按 main 最新口径降低日志噪声：关闭页面错误显示，FPM `log_level` 从 `debug` 降到 `warning`。
3. 不再保留全量 `php-fpm/access.log`，只保留 PHP CLI、OPcache、FPM master、worker、slowlog 等错误类日志。
4. 将业务日志目录告警阈值从 `20G` 调整为 `5G`，适配测试服务器约 29G 系统盘；只告警，不自动删除普通业务日志。
5. 增加小时轮转任务：只处理 `runtime/app-logs/php` 与 `runtime/app-logs/php-fpm`；`access.log` 直接截断，达到阈值的 `error`/`slow` 日志切割发送 Telegram，发送成功后删除本地归档。

## 改造文件

- `php/dev.ini`：`display_errors` 和 `display_startup_errors` 改为 `Off`，继续将 PHP/OPcache 错误写入持久化目录。
- `php/fpm-logging.conf`：FPM `log_level=warning`，移除全量 access 配置，保留 3 秒 slowlog 与 worker 错误日志。
- `docker-compose.yml`：web 容器增加 `SYS_PTRACE`，保证 FPM slowlog 可以写 PHP 调用栈。
- `cicd-web/config.py`、`cicd-web/config/settings.json`：默认日志告警阈值改为 `5G`。
- `ops/test/scripts/youdianse-app-log-hourly-rotate.py`：测试环境小时轮转脚本。
- `ops/test/install-app-log-hourly-rotate.sh`：安装 `/usr/local/sbin/youdianse-app-log-hourly-rotate.py` 并维护 root crontab 管理块。
- `README.md`：同步测试环境排查和维护说明。

## 服务器安装

```bash
cd /opt/docker-youdianse-php
git pull
sh ops/test/install-app-log-hourly-rotate.sh
/usr/bin/flock -xn /var/run/youdianse-app-log-hourly-rotate.lock /usr/bin/python3 /usr/local/sbin/youdianse-app-log-hourly-rotate.py --dry-run --no-notify
```

root crontab 管理块：

```text
# BEGIN YOUDIANSE_APP_LOG_ROTATE
12 * * * * /usr/bin/flock -xn /var/run/youdianse-app-log-hourly-rotate.lock /usr/bin/python3 /usr/local/sbin/youdianse-app-log-hourly-rotate.py >> /var/log/youdianse-app-log-hourly-rotate.log 2>&1
# END YOUDIANSE_APP_LOG_ROTATE
```

## 验证命令

```bash
python3 -m py_compile ops/test/scripts/youdianse-app-log-hourly-rotate.py
bash -n ops/test/install-app-log-hourly-rotate.sh entrypoint/web-entrypoint.sh entrypoint/cron-entrypoint.sh cicd-web.sh
docker compose config >/tmp/youdianse-dev-compose-check.yml
git diff --check
```

发布后验证：

```bash
docker exec youdianse-dev-php-web php-fpm -tt
docker exec youdianse-dev-php-web php -i | grep -E 'display_errors|display_startup_errors|error_reporting|log_errors|error_log|opcache.error_log'
docker exec youdianse-dev-php-web sh -lc 'find /var/www/html/youdianse-php/runtime/logs/php /var/www/html/youdianse-php/runtime/logs/php-fpm -maxdepth 1 -type f -ls'
crontab -l | grep -A2 YOUDIANSE_APP_LOG_ROTATE
tail -80 /var/log/youdianse-app-log-hourly-rotate.log
```

期望结果：

- `display_errors` 和 `display_startup_errors` 为 `Off`。
- `php-fpm -tt` 解析到 `log_level = warning`，不再配置全量 `access.log`。
- 慢请求仍写入 `php-fpm/slow.log`，`SYS_PTRACE` 允许输出调用栈。
- CICD 日志目录告警阈值显示 `5G`。
- 小时轮转 dry-run 显示只处理 `php`、`php-fpm` 范围内达到阈值的日志，小普通日志和业务日志会跳过。

## 通知记录

按 `AGENTS.md` 要求，本任务每个步骤都应发送 `【测试环境｜步骤 N 完成】` 普通文本通知。当前本地没有 Telegram 密钥，且测试服务器 SSH 认证失败时，不允许静默视为成功；需记录失败原因并在服务器连接恢复后补发或由运维手工发送。
