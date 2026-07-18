---
id: "doc-e265530a2b74"
title: "测试环境 PHP 全量日志持久化改造"
date: "2026-07-18T14:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-18-1400-%E3%80%90%E4%BC%98%E5%8C%96%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83PHP%E5%85%A8%E9%87%8F%E6%97%A5%E5%BF%97%E6%8C%81%E4%B9%85%E5%8C%96%E6%94%B9%E9%80%A0.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-18-1400-【优化+架构改造】测试环境PHP全量日志持久化改造.md"
sourceSha256: "60093413569fdc478d12850376c787b294b7cd605859a145bf12616b9ab767e1"
sourceSystem: "project-doc"
---

# 测试环境 PHP 全量日志持久化改造

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-18-1400-【优化+架构改造】测试环境PHP全量日志持久化改造.md`

> 整理日期：2026-07-18 14:00｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-18
环境：游点涩测试环境（dev 分支）
分类：优化+架构改造

## 目标

在保留原有 PHP 限制与时区配置的基础上，打开 PHP CLI、PHP-FPM、OPcache、队列和外部定时任务的可用日志，并统一写入宿主机持久化目录。容器发布重建后，历史日志仍然保留。

保留配置：

```ini
memory_limit=512M
upload_max_filesize=50M
post_max_size=50M
display_errors=On
error_reporting=E_ALL
date.timezone=Asia/Shanghai
```

新增能力：

- 开启 `display_startup_errors`、`log_errors`、内存泄漏报告，不忽略重复错误。
- PHP CLI、队列和外部定时任务错误写入 `php/php-error.log`。
- OPcache 错误单独写入 `php/php-opcache-error.log`。
- PHP-FPM master 使用 debug 日志级别，写入 `php-fpm/master-error.log`。
- PHP-FPM worker 的 PHP 错误单独写入 `php-fpm/worker-error.log`。
- 捕获 FPM worker stdout/stderr，避免只留在容器临时标准输出。
- 每个 FastCGI 请求写入 `php-fpm/access.log`，包含状态、耗时、内存、CPU、PID 和脚本路径。
- 请求执行超过 3 秒时，把最多 50 层 PHP 调用栈写入 `php-fpm/slow.log`；只记录，不终止请求。
- CICD 运行配置同步增加 `php/fpm-logging.conf` 宿主机/容器一致性检查。

## 日志路径

宿主机持久化根目录：

```text
/opt/docker-youdianse-php/runtime/app-logs
```

容器内根目录：

```text
/var/www/html/youdianse-php/runtime/logs
```

日志映射：

| 类型 | 宿主机相对路径 | 说明 |
| --- | --- | --- |
| PHP CLI/定时/队列错误 | `runtime/app-logs/php/php-error.log` | `php/dev.ini` 的统一 PHP 错误日志 |
| OPcache 错误 | `runtime/app-logs/php/php-opcache-error.log` | OPcache 单独日志 |
| FPM master | `runtime/app-logs/php-fpm/master-error.log` | master 与进程管理 debug 日志 |
| FPM worker | `runtime/app-logs/php-fpm/worker-error.log` | Web PHP 错误、警告、异常 |
| FPM 请求 | `runtime/app-logs/php-fpm/access.log` | 每个 FastCGI 请求一条 |
| FPM 慢请求 | `runtime/app-logs/php-fpm/slow.log` | 超过 3 秒的 PHP 调用栈 |
| 队列 | `runtime/app-logs/queue/*.log` | watchdog 和各 worker 输出 |
| 外部定时任务 | `runtime/app-logs/cron/*.log` | 每个任务独立输出 |

web 与 cron 容器共享同一个持久化挂载，因此 PHP CLI 日志路径相同；FPM 专属日志只由 web 容器写入。

## 改造文件

- `php/dev.ini`：PHP 全局错误与 OPcache 日志。
- `php/fpm-logging.conf`：FPM master、worker、access、slowlog 配置。
- `docker-compose.yml`：只读挂载 FPM 日志配置，日志目录继续复用持久化挂载。
- `php-web.Dockerfile`：把 FPM 日志配置打入镜像作为默认值。
- `entrypoint/web-entrypoint.sh`：创建 FPM/PHP 日志目录与文件并设置权限。
- `entrypoint/cron-entrypoint.sh`：创建 PHP CLI/OPcache 日志文件并设置权限。
- `cicd-web/core.py`：把 FPM 日志配置纳入配置选择、构建元数据和配置同步校验。
- `README.md`：补充测试环境运维排查命令与日志说明。

## 验证命令

仓库静态检查：

```bash
PYTHONPYCACHEPREFIX=/tmp/youdianse-pycache python3 -m py_compile \
  cicd-web.py cicd-web/core.py cicd-web/config.py cicd-web/telegram.py cicd-web/command.py
bash -n entrypoint/web-entrypoint.sh entrypoint/cron-entrypoint.sh \
  entrypoint/cron-task-runner.sh entrypoint/queue-watchdog.sh cicd-web.sh
docker compose config >/tmp/youdianse-php-log-compose.yml
git diff --check
```

容器内配置与落盘检查：

```bash
docker exec youdianse-dev-php-web php-fpm -tt
docker exec youdianse-dev-php-web php -i | grep -E \
  'display_errors|display_startup_errors|error_reporting|log_errors|error_log|opcache.error_log'
docker exec youdianse-dev-php-web sh -lc \
  'find /var/www/html/youdianse-php/runtime/logs/php /var/www/html/youdianse-php/runtime/logs/php-fpm -maxdepth 1 -type f -ls'
docker exec youdianse-dev-php-cron sh -lc \
  'find /var/www/html/youdianse-php/runtime/logs/php /var/www/html/youdianse-php/runtime/logs/queue /var/www/html/youdianse-php/runtime/logs/cron -maxdepth 1 -type f -ls'
```

主动写入 PHP CLI 测试错误后，确认宿主机可见：

```bash
docker exec youdianse-dev-php-cron php -r \
  'trigger_error("php-log-persist-verify", E_USER_WARNING);'
grep -F 'php-log-persist-verify' runtime/app-logs/php/php-error.log
```

访问后台后，确认 FPM access 日志新增：

```bash
before=$(wc -l < runtime/app-logs/php-fpm/access.log)
curl -sS -o /dev/null https://admin.youdianse-test.xyz/admin1866/login
after=$(wc -l < runtime/app-logs/php-fpm/access.log)
test "$after" -gt "$before"
```

## 日志容量与清理边界

本次不增加自动删除。所有新增日志都位于 `runtime/app-logs`，沿用现有 2G 阈值检查：目录达到阈值时向 Telegram 飞机群提醒，由运维确认后手工归档、截断或删除。

```bash
cd /opt/docker-youdianse-php
du -sh runtime/app-logs
find runtime/app-logs -type f -printf '%s %TY-%Tm-%Td %p\n' | sort -nr | head -30
```

FPM debug 与全请求 access 日志增长较快，测试期间应重点观察 `php-fpm/master-error.log` 和 `php-fpm/access.log`。

## 本次验证结果

- Python 语法检查：通过。
- Shell 语法检查：通过。
- Docker Compose 展开检查：通过，FPM 配置和日志持久化挂载存在。
- `git diff --check`：通过。
- 使用官方 `php:7.4-fpm` 执行 `php-fpm -tt`：通过。
- 使用官方 `php:7.4-fpm` 主动触发 PHP CLI warning：已写入目标 PHP 错误日志。

测试服务器实测：

- PHP 日志改造运维提交：`51e1ad5`。
- 增加 `@Daviea2` 通知提交：`2a144eb`。
- 业务代码 git id：`312d94ce1de2814ca977fb46594b0a3a6c30f6d2`。
- 测试镜像：`youdianse-php:dev-312d94ce1de2`。
- 真实发布结果：`SUCCESS`；HTTP 200、Session writable、Redis/MongoDB 连通。
- `php -i`：512M、50M、50M、E_ALL、启动错误显示、错误日志、OPcache 日志和 Asia/Shanghai 均生效。
- `php-fpm -tt`：master debug、access、3 秒 slowlog、50 层调用栈、worker 输出捕获和 worker error_log 均生效。
- 日志权限：PHP/FPM 日志文件属主为 `www-data:www-data`，FPM worker 可写。
- 进程：1 个 FPM master、2 个 FPM worker、queue watchdog、`crontab queue` 和 `job queue` 均正常。
- 主动写入：CLI warning `php-cli-persist-verify-20260718` 已写入宿主机 `runtime/app-logs/php/php-error.log`。
- FPM access：真实请求后日志行数从 1 增至 2；二次容器重建后继续从 6 增至 7。
- 挂载：web 与 cron 均将 `/opt/docker-youdianse-php/runtime/app-logs` 映射到容器 `runtime/logs`。
- 跨重建：强制重建 web/nginx/cron 后，CLI warning 标记仍存在，HTTP 仍为 200，FPM/队列进程正常。
- 日志目录最终大小：143M，低于 2G 告警阈值；未执行任何自动清理。
- 服务器原有 `env/.env.dev` 本地修改在更新、发布和重建过程中均保留，未覆盖。
- CICD Web 与健康监控配置均已刷新，实际 Telegram 验证消息包含 `@Daviea2`。

## 飞机群通知

本次每一步均以 `【测试环境｜步骤 N 完成】` 为标题发送 Telegram 普通文本通知。消息只描述步骤和结果，不包含 bot token、chat_id、SSH 密码、发布密码或仓库凭据。

该要求已固化到仓库根目录 `AGENTS.md`，作为整个仓库的持续执行规则。后续任务必须逐步通知；本地缺少 Telegram 密钥时改用测试服务器本地密钥，不允许静默跳过。

测试环境统一运维通知名单为：`@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2`。发布开始/完成/失败、配置同步、自动更新和健康监控通知均应包含新运维 `@Daviea2`。
