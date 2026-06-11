---
id: "doc-32302238b8ab"
title: "线上环境 CICD Web 自动更新与定时任务边界说明"
date: "2026-06-12T14:59:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-06-12-1459-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83CICD-Web%E8%87%AA%E5%8A%A8%E6%9B%B4%E6%96%B0dev%E5%88%86%E6%94%AF%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-06-12-1459-【运维记录】线上环境CICD-Web自动更新dev分支提示词.md"
sourceSha256: "558c4a744979856ee1a0cfba0f95a0bdaad2059132389dc3021062f8902d5f5e"
sourceSystem: "project-doc"
---

# 线上环境 CICD Web 自动更新与定时任务边界说明

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-06-12-1459-【运维记录】线上环境CICD-Web自动更新dev分支提示词.md`

> 整理日期：2026-06-12 14:59｜日期依据：文件名日期

文档日期：2026-06-12 14:59
环境：游点涩线上环境（main 分支）
分类：运维记录

这份文档替代旧版“root crontab 改造提示词”。旧方案已经废弃，不要再让 AI 按旧文档恢复 `cron/` 清单、安装 `/etc/cron.d`、或用仓库内容改写 root crontab。

## 当前原则

```text
1. 业务定时任务由外部可视化系统管理，不在 docker-youdianse-php 仓库维护调度清单。
2. 仓库不再保留 cron/youdianse-cron。
3. 仓库不再保留 cron/cicd-web-auto-update。
4. 不要把业务定时任务写回 root crontab。
5. 不要把业务定时任务写回 /etc/cron.d。
6. php-cron 容器只提供 PHP 执行环境、队列守护和 cron-task-runner.sh，不负责保存调度时间。
```

## 外部系统入口

```text
线上定时任务：https://cron.youdianse-main.xyz
测试定时任务：https://cron.youdianse-test.xyz
```

## 后端发布入口

```text
线上后端发布：https://cicd.youdianse-main.xyz
测试后端发布：https://cicd.youdianse-test.xyz
```

## 配置修改流程

```text
配置仓库：https://18game.18git.com/root/docker-youdianse-php
线上：选择 main 分支，修改 nginx / php / env，等待 2 分钟后到线上 CICD 发布更新配置。
测试：选择 dev 分支，修改 nginx / php / env，等待 2 分钟后到测试 CICD 发布更新配置。
```

## php-cron 的正确定位

`php-cron` 不是调度系统，它只是外部可视化定时系统调用业务任务时使用的执行容器。

```text
测试容器：youdianse-dev-php-cron
线上容器：youdianse-main-php-cron
执行入口：/usr/local/bin/cron-task-runner.sh <Class> <method>
队列守护：/usr/local/bin/queue-watchdog.sh
队列默认：crontab:queue job:queue
```

需要手动验证任务时，可以进入对应服务器执行：

```bash
docker exec youdianse-dev-php-cron /usr/local/bin/cron-task-runner.sh UserFeedbackStatus updateUserFeedbackStatus
```

线上环境把容器名前缀换成 `youdianse-main-php-cron`。

## 自动更新脚本

`cicd-web-auto-update.py` 仍是仓库里的工具脚本，但调度入口不放在 Git 仓库中。

```text
1. 可以由服务器本地已配置的任务或外部可视化系统触发。
2. 不要新增 cron/cicd-web-auto-update 模板。
3. 不要在 README 或 docs 里写 root crontab 安装教程。
4. 不要在仓库里恢复 cicd-web-auto-update.sh。
```

## 给 AI 的禁止项

如果后续让 AI 修改本仓库，必须明确告诉它：

```text
禁止创建 cron/ 目录。
禁止创建 cron/youdianse-cron。
禁止创建 cron/cicd-web-auto-update。
禁止用仓库内容改写 root crontab managed block。
禁止把业务任务安装到 /etc/cron.d。
禁止把自动更新调度入口放回 Git 仓库。
业务定时任务只能去 https://cron.youdianse-main.xyz 或 https://cron.youdianse-test.xyz 管理。
```
