---
id: "doc-4d1d484363e6"
title: "线上环境 queue-watchdog.sh 队列守护说明"
date: "2026-06-11T23:54:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-06-11-2354-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83queue-watchdog%E9%98%9F%E5%88%97%E5%AE%88%E6%8A%A4%E8%AF%B4%E6%98%8E.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-06-11-2354-【运维记录】线上环境queue-watchdog队列守护说明.md"
sourceSha256: "f00679b5026799b20ff1382feafa95f191c4831a422c833df73d63ba4d5ea617"
sourceSystem: "project-doc"
---

# 线上环境 queue-watchdog.sh 队列守护说明

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606112354-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20queue-watchdog.sh%20%E9%98%9F%E5%88%97%E5%AE%88%E6%8A%A4%E8%AF%B4%E6%98%8E.md)

> 整理日期：2026-06-11 23:54｜日期依据：文件名日期

文档日期：2026-06-11 23:54
环境：游点涩线上环境（main 分支）
分类：运维记录

这份文档给运维同事看，用来快速理解 `php-cron` 容器里的队列守护是怎么工作的、怎么检查、出问题看哪里。

## 1. 一句话说明

`queue-watchdog.sh` 是 `php-cron` 容器的前台主进程，用来守护业务队列。

它不再每分钟执行一次 `bin/start.sh`，而是直接启动并守护两条 PHP 队列命令：

```bash
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php crontab queue
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php job queue
```

如果队列进程退出，watchdog 会记录日志，等待 5 秒，然后自动拉起。

## 2. 为什么不用旧 start.sh

旧版 18game 的做法是 cron 每分钟执行：

```bash
/bin/sh /var/www/html/18game/18game_php/bin/start.sh
```

旧 `start.sh` 的逻辑是：

```bash
ps -ef | grep shell.php
没找到进程 -> /usr/bin/php .../shell.php xxx queue >/dev/null &
```

这个方式在传统服务器上能用，但放在 Docker 容器里不够清晰：

```text
1. 依赖 ps / grep 判断进程，容器里未必安装 ps。
2. 用 & 后台启动，容器前台主进程看不出真正守护了什么。
3. 队列异常退出后，最多等到下一分钟 cron 才会再次检查。
4. 日志被 >/dev/null 丢掉，不方便排查。
```

现在业务代码路径已经从旧版：

```text
/var/www/html/18game/18game_php
```

变成当前容器路径：

```text
/var/www/html/youdianse-php
```

所以容器里统一使用 `queue-watchdog.sh` 直接守护当前路径下的队列命令。

## 3. 它在哪里运行

`docker-compose.yml` 的 `cron` 服务这样启动：

```yaml
entrypoint: ["/usr/local/bin/cron-entrypoint.sh"]
command: ["/usr/local/bin/queue-watchdog.sh"]
```

启动顺序：

```text
php-cron 容器启动
  -> /usr/local/bin/cron-entrypoint.sh
     -> 准备 PHP、.env、runtime 目录、/usr/bin/php 兼容软链
     -> exec /usr/local/bin/queue-watchdog.sh
        -> 守护 crontab queue
        -> 守护 job queue
```

`cron-entrypoint.sh` 会创建兼容软链：

```text
/usr/bin/php -> /usr/local/bin/php
```

watchdog 自己默认使用 `/usr/local/bin/php`。

## 4. 守护哪些队列

由 `docker-compose.yml` 的环境变量控制：

```yaml
QUEUE_WORKERS: "crontab:queue job:queue"
QUEUE_RESTART_DELAY: "5"
```

`QUEUE_WORKERS` 的格式是：

```text
类名:方法名 类名:方法名
```

当前会展开成：

```text
crontab:queue -> php /var/www/html/youdianse-php/bin/shell.php crontab queue
job:queue     -> php /var/www/html/youdianse-php/bin/shell.php job queue
```

如果以后要增加队列，例如 `foo bar`，可以加：

```yaml
QUEUE_WORKERS: "crontab:queue job:queue foo:bar"
```

然后它会执行：

```bash
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php foo bar
```

## 5. 核心实现逻辑

脚本文件：

```text
entrypoint/queue-watchdog.sh
```

主要分成 4 步。

第一步，读取配置：

```bash
APP_DIR=/var/www/html/youdianse-php
PHP_BIN=/usr/local/bin/php
QUEUE_WORKERS="crontab:queue job:queue"
QUEUE_RESTART_DELAY=5
QUEUE_LOG_DIR=/var/www/html/youdianse-php/runtime/logs/queue
```

第二步，启动前检查：

```text
检查 PHP_BIN 是否可执行。
检查 APP_DIR/bin/shell.php 是否存在。
创建 runtime/logs/queue 日志目录。
创建 watchdog.log。
```

第三步，为每个 worker 开一个守护循环：

```text
worker_loop crontab queue
worker_loop job queue
```

每个 `worker_loop` 做的事情：

```text
1. 记录 "xxx queue starting"。
2. 启动 PHP 队列进程。
3. wait 等待这个 PHP 进程退出。
4. 记录退出状态。
5. sleep 5 秒。
6. 回到第 1 步重新启动。
```

简单理解就是：

```text
while true:
  start php shell.php job queue
  wait until it exits
  sleep 5 seconds
  start it again
```

第四步，主进程每 10 秒检查 worker supervisor 是否还活着：

```text
如果某个 worker supervisor 异常退出：
  记录日志
  停掉所有 worker
  让容器退出
```

容器设置了：

```yaml
restart: always
```

所以如果 watchdog 主进程真的异常退出，Docker 会重启整个 `php-cron` 容器。

## 6. 进程结构

正常情况下 `docker top` 应该看到类似：

```text
/bin/sh /usr/local/bin/queue-watchdog.sh
/bin/sh /usr/local/bin/queue-watchdog.sh
/bin/sh /usr/local/bin/queue-watchdog.sh
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php crontab queue
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php job queue
sleep 10
```

为什么会有多个 `/bin/sh /usr/local/bin/queue-watchdog.sh`：

```text
第一个是 watchdog 主进程。
后面两个是 crontab queue 和 job queue 各自的 worker supervisor。
真正干活的是两个 php shell.php ... queue 进程。
sleep 10 是主进程定时检查 worker supervisor 的等待进程。
```

## 7. 日志在哪里

日志目录：

```text
/var/www/html/youdianse-php/runtime/logs/queue
```

主要文件：

```text
watchdog.log       watchdog 自己的启动、退出、重启日志
crontab-queue.log  crontab queue 的业务输出
job-queue.log      job queue 的业务输出
```

示例：

```text
[QUEUE][watchdog] 2026-06-10T22:02:59+0800 starting workers: crontab:queue job:queue
[QUEUE][watchdog] 2026-06-10T22:02:59+0800 crontab queue starting
[QUEUE][watchdog] 2026-06-10T22:02:59+0800 job queue starting
[QUEUE][watchdog] 2026-06-10T22:07:57+0800 job queue exited status=0; restart in 5s
[QUEUE][watchdog] 2026-06-10T22:08:02+0800 job queue starting
```

`job queue exited status=0; restart in 5s` 通常不是异常，表示业务队列命令正常退出，watchdog 5 秒后重新拉起。

## 8. 常用检查命令

登录后端服务器：

```bash
ssh -i id_rsa ubuntu@16.209.16.108
cd /opt/docker-youdianse-php
```

看容器是否运行：

```bash
sudo docker ps --filter name=youdianse-main-php-cron
```

看容器启动命令：

```bash
sudo docker inspect youdianse-main-php-cron --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
```

期望：

```text
Entrypoint=["/usr/local/bin/cron-entrypoint.sh"] Cmd=["/usr/local/bin/queue-watchdog.sh"]
```

看环境变量和路径：

```bash
sudo docker exec youdianse-main-php-cron sh -lc 'echo "$APP_DIR"; echo "$QUEUE_WORKERS"; ls -l /usr/bin/php /usr/local/bin/php; test -f /var/www/html/youdianse-php/bin/shell.php && echo shell.php-ok'
```

看实际进程：

```bash
sudo docker top youdianse-main-php-cron -eo pid,ppid,comm,args
```

看 watchdog 日志：

```bash
sudo docker logs --tail 100 youdianse-main-php-cron
sudo docker exec youdianse-main-php-cron sh -lc 'tail -n 100 /var/www/html/youdianse-php/runtime/logs/queue/watchdog.log'
```

看队列业务日志：

```bash
sudo docker exec youdianse-main-php-cron sh -lc 'tail -n 100 /var/www/html/youdianse-php/runtime/logs/queue/job-queue.log'
sudo docker exec youdianse-main-php-cron sh -lc 'tail -n 100 /var/www/html/youdianse-php/runtime/logs/queue/crontab-queue.log'
```

## 9. 正常状态长什么样

容器：

```text
youdianse-main-php-cron Up
```

环境：

```text
APP_DIR=/var/www/html/youdianse-php
QUEUE_WORKERS=crontab:queue job:queue
/usr/bin/php -> /usr/local/bin/php
shell.php-ok
```

进程：

```text
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php crontab queue
/usr/local/bin/php /var/www/html/youdianse-php/bin/shell.php job queue
```

日志：

```text
[QUEUE][watchdog] ... starting workers: crontab:queue job:queue
[QUEUE][watchdog] ... crontab queue starting
[QUEUE][watchdog] ... job queue starting
```

## 10. 常见问题

### 10.1 看不到队列进程

先看容器是否启动：

```bash
sudo docker ps --filter name=youdianse-main-php-cron
sudo docker logs --tail 100 youdianse-main-php-cron
```

重点看这些错误：

```text
php cli not executable
shell entry not found
invalid worker spec
worker supervisor exited unexpectedly
```

### 10.2 shell.php 找不到

说明业务代码路径不对，或者镜像里没有业务代码：

```bash
sudo docker exec youdianse-main-php-cron ls -l /var/www/html/youdianse-php/bin/shell.php
```

当前正确路径必须是：

```text
/var/www/html/youdianse-php/bin/shell.php
```

不要再使用旧路径：

```text
/var/www/html/18game/18game_php/bin/shell.php
```

### 10.3 crontab-queue.log 是 0 字节

先看进程是否在：

```bash
sudo docker top youdianse-main-php-cron -eo pid,ppid,comm,args
```

如果 `crontab queue` 进程存在，只是日志 0 字节，一般表示当前没有输出，不一定是异常。

### 10.4 job queue 一直退出又重启

看退出状态和业务日志：

```bash
sudo docker exec youdianse-main-php-cron sh -lc 'tail -n 200 /var/www/html/youdianse-php/runtime/logs/queue/watchdog.log'
sudo docker exec youdianse-main-php-cron sh -lc 'tail -n 200 /var/www/html/youdianse-php/runtime/logs/queue/job-queue.log'
```

如果是：

```text
job queue exited status=0; restart in 5s
```

通常是业务命令正常退出，watchdog 自动重启。
如果是非 0 状态，再看 `job-queue.log` 里的 PHP 报错。

### 10.5 修改队列列表后没有生效

`QUEUE_WORKERS` 是容器启动时读取的环境变量。改 `docker-compose.yml` 后需要重新创建 `php-cron` 容器。

检查当前容器实际值：

```bash
sudo docker exec youdianse-main-php-cron sh -lc 'echo "$QUEUE_WORKERS"'
```

## 11. 变更队列时怎么做

修改：

```text
docker-compose.yml
```

调整：

```yaml
QUEUE_WORKERS: "crontab:queue job:queue"
QUEUE_RESTART_DELAY: "5"
```

提交代码后，通过 CICD 重新发布并勾选或指定携带 `php-cron` 执行容器部署。

发布后验证：

```bash
sudo docker inspect youdianse-main-php-cron --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
sudo docker top youdianse-main-php-cron -eo pid,ppid,comm,args
sudo docker logs --tail 100 youdianse-main-php-cron
```

## 12. 运维记忆点

```text
1. php-cron 容器必须常驻。
2. queue-watchdog.sh 是 php-cron 的前台主进程。
3. 它守护 crontab queue 和 job queue。
4. 当前业务路径是 /var/www/html/youdianse-php。
5. 旧路径 /var/www/html/18game/18game_php 只作为历史说明，不再用于容器。
6. 不再用 cron 每分钟执行 bin/start.sh。
7. 队列退出会自动重启，默认间隔 5 秒。
8. 日志看 runtime/logs/queue。
```
