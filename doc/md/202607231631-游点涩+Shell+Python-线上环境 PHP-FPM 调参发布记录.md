---
id: "doc-6a83e3a310df"
title: "线上环境 PHP-FPM 调参发布记录"
date: "2026-07-23T16:31:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Nginx", "Redis", "自动化", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-23-1631-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83PHP-FPM%E8%B0%83%E5%8F%82%E5%8F%91%E5%B8%83%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-23-1631-【优化】线上环境PHP-FPM调参发布记录.md"
sourceSha256: "8317ec3888bed95d5e691483b3ef0b0a04e53bf71f0e12ebaa245f23a15d2b65"
sourceSystem: "project-doc"
---

# 线上环境 PHP-FPM 调参发布记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607231631-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BPython-%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20PHP-FPM%20%E8%B0%83%E5%8F%82%E5%8F%91%E5%B8%83%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-23 16:31｜日期依据：文件名日期

文档日期：2026-07-23 16:31
环境：游点涩线上环境（main 分支）
分类：优化

## 背景

线上 `master-error.log` 高频出现：

```text
[pool www] server reached pm.max_children setting (5), consider raising it
```

后端确认调整目标：

```text
PHP-FPM SAPI memory_limit=128M
pm.max_children=25
```

## 修改内容

`php/dev.ini`：

```ini
memory_limit=128M
```

`php/fpm-logging.conf`：

```ini
[www]
pm.max_children = 25
```

说明：官方 `www.conf` 中默认 `pm.max_children=5` 保持不改；正式环境通过后加载的 `zz-youdianse-logging.conf` 覆盖为 `25`。

## 本地验证

```bash
bash -n cicd-web.sh
sh -n entrypoint/web-entrypoint.sh
sh -n entrypoint/cron-entrypoint.sh
python3 -m compileall cicd-web cicd-web.py cicd-web-auto-update.py
docker compose --profile cron config
git diff --check
```

临时 `php:7.4-fpm` 容器验证：

```text
memory_limit => 128M => 128M
/usr/local/etc/php-fpm.d/www.conf:pm.max_children = 5
/usr/local/etc/php-fpm.d/zz-youdianse-logging.conf:pm.max_children = 25
php-fpm -tt exit=0
```

## 线上发布

- 运维版本：`0e2e86e`
- 业务版本：`20ac0f839734`
- 镜像：`youdianse-php:main-20ac0f839734`
- 服务：`web nginx cron`

发布结果：

```text
SUCCESS
HTTP 200
Session writable
Redis OK
MongoDB OK
Hosts OK
```

容器内验证：

```text
memory_limit => 128M => 128M
/usr/local/etc/php-fpm.d/www.conf:pm.max_children = 5
/usr/local/etc/php-fpm.d/zz-youdianse-logging.conf:pm.max_children = 25
```

## 后续观察

发布后观察：

- `runtime/logs/php-fpm/master-error.log` 是否继续出现 `reached pm.max_children setting (25)`。
- web 容器内存和 CPU 是否稳定。
- 是否出现 `Allowed memory size exhausted`，如出现需定位具体接口或任务。
- 慢日志中同步 curl、Mongo count/aggregate、Excel 导出和批处理同步阻塞仍需研发继续跟进。
