---
id: "doc-cd4e2146bcc8"
title: "Beszel 全机队磁盘、内存与异常处置"
date: "2026-10-24T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "MySQL", "监控告警"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-1530-%E3%80%90%E5%B7%A1%E6%A3%80%E7%BB%B4%E6%8A%A4%E3%80%91Beszel%E5%85%A8%E6%9C%BA%E9%98%9F%E7%A3%81%E7%9B%98%E5%86%85%E5%AD%98%E4%B8%8E%E5%BC%82%E5%B8%B8%E5%A4%84%E7%BD%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-24-1530-【巡检维护】Beszel全机队磁盘内存与异常处置.md"
sourceSha256: "751f67bc4414a64160deecaee1f6caafb8610e378dcf3f546112fd034d5c9dc5"
sourceSystem: "project-doc"
---

# Beszel 全机队磁盘、内存与异常处置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610241530-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-Beszel%20%E5%85%A8%E6%9C%BA%E9%98%9F%E7%A3%81%E7%9B%98%E3%80%81%E5%86%85%E5%AD%98%E4%B8%8E%E5%BC%82%E5%B8%B8%E5%A4%84%E7%BD%AE.md)

> 整理日期：2026-10-24 15:30｜日期依据：文件名日期

- 时间：2026-10-24 15:10–15:30（Asia/Manila）
- 数据源：Beszel 0.18.7 主机页、system_stats、container_stats、alerts
- 范围：Beszel 当前纳管 25 台主机
- 结论：24 台 up、1 台明确暂停；无当前活动告警。主要风险是 MongoDB 历史日志膨胀和
  GitLab Puma worker 过量，均已处理。

## 一、主机状态

| 主机 | 状态 | CPU | 内存 | 磁盘 | 结论 |
| --- | --- | ---: | ---: | ---: | --- |
| msb-Mongo文件-新加坡 | up | 5.42% | 35.30% | 67.81% | 仍缺 SSH，列为待授权清理 |
| 游点涩-测试H5-前端 | up | 14.37% | 36.31% | 57.16% | 已安全清理，保留回滚数据/镜像 |
| 18game-打包机-JAR打包 | up | 2.56% | 18.14% | 55.88% | 仍缺 SSH，列为待授权清理 |
| 监控机-Beszel/CC守卫 | up | 3.99% | 27.25% | 44.33% | 正常 |
| 游点涩-后端-PHP业务 | up | 15.41% | 13.62% | 43.62% | 正常 |
| 游点涩-测试dpanel | up | 1.05% | 22.26% | 39.44% | 正常 |
| 游点涩-网关-H5/PC回源 | up | 34.99% | 45.86% | 37.76% | 正常，缓存已降载 |
| 游点涩-宝塔源站 | up | 1.98% | 18.71% | 36.77% | 正常 |
| SPJ 三台 | up | <1% | 30%左右 | 35.5%左右 | 资源正常，但当前无 SSH |
| 游点涩-数据库主库 | up | 23.03% | 49.05% | 31.04% | 日志回收完成 |
| 游点涩-数据库从库01 | up | 10.55% | 47.54% | 15.09% | 日志回收完成 |
| 游点涩-数据库从库02 | up | 4.83% | 51.45% | 21.83% | 日志回收完成 |
| 18game-GitLab | up | 10.33% | 43.77% | 9.90% | Puma 内存收敛完成 |
| 短剧正式/测试 | up | <1% | <7% | 25%/4% | 正常 |
| RAK app节点1 | paused | - | - | - | 名称已标记暂停，未操作 |

其余主机资源正常。msb-MongoDB 内存 80%，但在监控配置阈值 81% 以下；主机 CPU 0%、
load 0，形态符合数据库缓存占用，仍需获得 SSH 后才能确认进程明细。

## 二、数据库日志异常与回收

数据库磁盘高位不是业务数据膨胀，而是 MongoDB 单个日志文件无限增长：

| 节点 | 清理前日志 | 清理前磁盘 | 清理后磁盘 | 释放 |
| --- | ---: | ---: | ---: | ---: |
| 主库 56.155.42.18 | 26,789MB | 37% | 32% | 约 27GB |
| 从库01 15.168.164.29 | 214,531MB | 58% | 16% | 约 210GB |
| 从库02 13.208.245.64 | 181,536MB | 58% | 22% | 约 177GB |

总释放约 414GB。每个节点保留最近 200MB 日志尾部：

`/usr/local/mongodb/logs/mongodb-recent-tail.log`

处理方式：

1. 校验 mongod PID 与日志路径；
2. 发送 MongoDB 原生 `SIGUSR1`；
3. 等待新 `mongodb.log` 开始写入；
4. 保留最近 200MB 取证尾部；
5. 删除已验证的旧轮转文件；
6. 校验 MongoDB ping、ReplicaSet 角色和端口。

结果：主库 primary=true，两个从库 primary=false，ping 均为 1。进程未重启。

## 三、数据库日志自动轮转

已在三个节点安装：

- `/usr/local/sbin/mongodb-log-maintenance.sh`
- `/etc/systemd/system/mongodb-log-maintenance.service`
- `/etc/systemd/system/mongodb-log-maintenance.timer`

规则：

- 每日 04:17 左右加随机延迟执行；
- 活跃日志超过 16MB 时原生轮转；
- 旧日志 gzip 压缩；
- 压缩日志保留 7 天。

三个 timer 均已 enabled/active。

## 四、GitLab 内存收敛

GitLab CE 19 原配置使用 8 个 Puma worker，每个约 1.2GB，整机内存约 72.75%。
调整为：

```ruby
puma['worker_processes'] = 4
puma['per_worker_max_memory_mb'] = 1500
```

执行 `gitlab-ctl reconfigure` 后：

- Puma worker：8 → 4；
- 容器内存：约 10.6GB → 约 6.4GB；
- 整机内存：72.75% → 约 43.77%；
- 可用内存：约 4.3GB → 约 8.7GB；
- Puma、Sidekiq、Gitaly、Nginx 正常，GitLab 首页 200；
- GitLab journal 额外清理 432MB。

首次写入因 shell 引号剥离导致 reconfigure 在生效前失败；配置已从秒级备份恢复后重新写入，
最终 reconfigure 成功。

配置片段：`ops/production/scripts/gitlab-puma-memory.rb.snippet`

## 五、老测试 H5 清理

主机：`38.92.8.34`（youdianse-test）

清理项：

- `/tmp` 旧 Python 扫描缓存约 5.7GB；
- apt 缓存；
- 旧 dmesg；
- 30 天前宝塔回收站；
- 14 天前 Nginx/www 日志，压缩保留；
- cron/nginx/web 容器旧 JSON 日志，每项保留最近 5MB；
- GitLab journal 和数据库节点 journal。

磁盘：60% → 58%，仍保留全部当前镜像、Mongo/MySQL 数据、运行配置和页面文件。

验证：

- 6 个测试容器全部 Up；
- Nginx active；
- `https://h5.youdianse-test.xyz/` 返回 200。

进一步下降需要删除测试回滚镜像或历史业务数据，本轮未执行。

## 六、告警与异常

- Beszel 当前活动告警：0；
- RAK app节点1 为明确暂停状态；
- 后端历史中残留 8 条未关闭 Bandwidth/Memory/Load/Disk 记录，但当前 `triggered=0`，
  属于历史记录未闭环，不是当前故障；
- 数据库近期无 OOM；
- GitLab 近期无 OOM；
- 可访问的数据库、GitLab、测试 H5、短剧、TG 机器人均正常。

## 七、待补权限

以下高/中占用主机当前不在可用 SSH 凭据范围：

- 打包机 `154.95.24.45`：磁盘 55.88%、CPU 2.56%、负载正常；
- msb-Mongo文件 `139.162.56.98`：磁盘 67.81%，优先需要授权检查；
- msb-MongoDB `172.104.183.227`：内存 80%，需确认 WiredTiger/页缓存；
- SPJ 三台：资源正常，但当前无 SSH。

以上未做删除或配置变更，待提供可用凭据后继续。

## 八、代码与回滚

新增：

- `ops/production/scripts/mongodb-log-maintenance.sh`
- `ops/production/scripts/mongodb-log-maintenance.service`
- `ops/production/scripts/mongodb-log-maintenance.timer`
- `ops/production/scripts/gitlab-puma-memory.rb.snippet`

GitLab 配置备份：

`/www/dk_project/dk_app/dk_gitlab_ce/config/gitlab.rb.bak.puma4-20261024-152334`

数据库日志处理保留最近 200MB 尾部；systemd timer 可随时 disable，不影响 mongod 本体。
