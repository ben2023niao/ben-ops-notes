---
id: "doc-f0ee2a398a84"
title: "Beszel 全机队巡检、磁盘清理与 PM2 内存阈值修复"
date: "2026-10-26T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-26-%E3%80%90%E7%9B%91%E6%8E%A7%E7%BB%B4%E6%8A%A4%E3%80%91Beszel%E5%85%A8%E6%9C%BA%E9%98%9F%E5%B7%A1%E6%A3%80%E7%A3%81%E7%9B%98%E6%B8%85%E7%90%86%E4%B8%8EPM2%E5%86%85%E5%AD%98%E9%98%88%E5%80%BC%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-26-【监控维护】Beszel全机队巡检磁盘清理与PM2内存阈值修复.md"
sourceSha256: "f1c07a54defad2340ecbd6a353ccdc5e760ee03593e8937e80b8ee66ffddb550"
sourceSystem: "project-doc"
---

# Beszel 全机队巡检、磁盘清理与 PM2 内存阈值修复

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-26-【监控维护】Beszel全机队巡检磁盘清理与PM2内存阈值修复.md`

> 整理日期：2026-10-26 00:00｜日期依据：文件名日期

- 时间：2026-10-26（Asia/Manila）
- 环境：游点涩/18game 线上与测试
- 监控中心：`52.79.252.255:8090`
- Beszel：`beszel-zh:v0.18.7`
- 代码提交：`18game_devops/b88d7ee`
- 结论：完成全机队趋势与异常分析；监控机、网关、后端共释放约 8GB；补齐 5 台主机 55 条告警规则；H5/PC PM2 重启阈值由 500MB 修正为 1GB，短时回归无新增重启

## 一、变更前基线

| 项目 | 状态 |
| --- | --- |
| `18game_devops/main` | `01aa89c`，与 `origin/main` 一致，工作区 clean |
| `docker-youdianse-php/main` | `e4e28ca`，与 `origin/main` 一致，工作区 clean |
| Beszel 容器 | 已运行 7 天，health 200 |
| 监控对象 | 26 台 up、1 台明确 paused |
| 触发中告警 | 0 |

浏览器会话不可用，本次通过 Beszel 所在服务器的 PocketBase SQLite 只读数据、HTTP health 和目标主机 SSH 交叉验证。未修改 Beszel 登录凭据。

## 二、当前机队快照

### 高 CPU/load

| 主机 | CPU | 内存 | 磁盘 | load1 |
| --- | ---: | ---: | ---: | ---: |
| 游点涩-预发布 | 50.97% | 51.35% | 1.88% | 20.19 |
| 游点涩-网关 | 31–36% | 44–46% | 35.6% | 2.3–3.3 |
| 游点涩-测试后端 | 29.51% | 40.66% | 16.22% | 1.16 |
| 游点涩-数据库主库 | 20.61% | 51.66% | 32.78% | 3.47 |

### 高磁盘/内存

| 主机 | 指标 | 当前值 | 阈值 | 判断 |
| --- | --- | ---: | ---: | --- |
| msb-Mongo文件 | 磁盘 | 67.81% | 72% | 近 7 天稳定，未增长 |
| 18game-打包机 | 磁盘 | 57.8% | 60% | 近 7 天缓慢增加 |
| 游点涩-测试H5 | 磁盘 | 57.31% | 64% | 近 7 天稳定 |
| msb-MongoDB | 内存 | 80.12% | 81% | 7 天由 73% 缓升到 80% 后趋稳 |
| 18game-TG机器人 | 内存 | 21% | 新增 82% | 正常 |

## 三、7 天趋势与异常分析

基于 `system_stats/480m` 计算 7 天 p95，基于 `120m` 复核阶跃：

| 主机 | p95 CPU | p95 load1 | 最大 CPU | 最大 load1 |
| --- | ---: | ---: | ---: | ---: |
| 预发布 | 46.14% | 18.42 | 50.99% | 20.38 |
| 网关 | 43.34% | 5.34 | 58.20% | 7.95 |
| 测试后端 | 33.85% | 1.78 | 33.99% | 1.78 |
| 数据库主库 | 29.33% | 4.81 | 31.57% | 5.22 |
| 后端 PHP | 14.26% | 2.24 | 14.95% | 2.35 |

### 预发布异常阶跃

`138.252.248.139` 的 CPU/load 在 10-26 发生明显阶跃：

| 时间 | CPU | load1 | 内存 |
| --- | ---: | ---: | ---: |
| 10-25 21:30 UTC | 0.89% | 0.33 | 43.49% |
| 10-25 23:30 UTC | 31.59% | 12.54 | 48.00% |
| 10-26 01:30 UTC | 50.99% | 20.39 | 50.75% |
| 10-26 13:30 UTC | 50.97% | 20.37 | 51.37% |

换算为 Asia/Manila，异常发生在 10-26 早上约 07:30–09:30，之后长时间几乎完全不变。高度疑似固定满载进程、构建/扫描任务或监控口径异常，不像自然业务波动。

当前 `root@138.252.248.139:38927` 拒绝现有密钥，Beszel 中也无可读容器统计，因此无法安全定位 PID。禁止在未确认进程前直接重启。

## 四、告警配置缺口修复

发现以下 5 台 up 主机虽然正常上报数据，但 `alerts` 规则为 0：

- `18game-TG机器人-191.40.41.155`
- `18game-定时任务机-Spug调度-16.208.32.40`
- `游点涩-测试环境-dpanel-38.92.8.151`
- `游点涩-预发布环境-PC/H5-138.252.248.139`
- `短剧-测试服-业务-45.135.237.47`

这也是预发布持续高 CPU/load 未告警的直接原因。

本次为每台补齐 11 条规则，共 55 条：

- CPU：60%
- 磁盘：60%
- 带宽：33
- 普通主机内存：70–85%
- 普通主机 load1/5/15：10
- 预发布 20 核 load1/5/15：20
- 包含在线状态、GPU、温度、电池等标准项

数据库备份：

```text
/root/codex-backup/beszel-alerts-20261026-140012/data.db
SHA256: 316b9e15f7097a108cba7a105eeb2501f5de738b08402be7db4a92cc2f7e6c91
```

修复后：

- `PRAGMA integrity_check`：ok
- 5 台均为 11 条规则
- Beszel 重启加载配置后 health 200
- 预发布 LoadAvg1/5/15 已实际触发
- 其他新增规则无即时误报

## 五、磁盘垃圾清理

只清理悬空镜像、未使用 build cache、旧 journal、包缓存和超过保留期的轮转日志；未删除运行容器、数据卷、业务持久化日志或当前镜像。

| 主机 | 清理前 | 清理后 | 主要结果 |
| --- | ---: | ---: | --- |
| 监控机 52.79.252.255 | 45% | 42% | 约释放 1.5GB；journal 473MB→236MB |
| 网关 16.208.38.88 | 36% | 28% | 约释放 4GB；journal 4.0GB→2.3GB |
| 后端 16.209.16.108 | 46% | 41% | 约释放 2.4GB；build cache 1.71GB→0 |

合计约释放 8GB。

清理后验证：

- 监控机 7 个容器全部 Up，Beszel/ben-bot 正常
- 网关 Nginx active，`nginx -t` 通过，H5/PC 8/8 worker online
- 后端 web/nginx/cron/logbus/beszel-agent 全部 Up
- 公网 www/h5/pc 全部 200
- `/api/v1/system/info` POST：200
- `server.db1/db2a/db2b` 在容器内解析正常

## 六、PM2 内存阈值修复

虽然历史文档记录 H5/PC 已调整为 1GB，实际 ecosystem 仍为：

```text
max_memory_restart: '500M'
```

日志显示：

- H5 worker 在 591–760MB 被重启
- PC worker 在 524–633MB 被重启
- PC 持续出现 `@popperjs/core` 缺失

worker 自动重启会关闭已有连接，是 keepalive 参数调整后仍出现 upstream 104 的放大器。

### 线上修正

- H5/PC `max_memory_restart`：500MB→1GB
- PM2 滚动 reload
- H5 8/8、PC 8/8 online
- 所有 worker 生效值：1,073,741,824 字节

### 2 分钟回归

| 容器 | 起始重启计数 | 结束重启计数 | 新增 |
| --- | ---: | ---: | ---: |
| H5 | 14,508 | 14,508 | 0 |
| PC | 13,186 | 13,186 | 0 |

所有 worker 持续运行超过 200 秒。网关自 13:50 后 3003/3004 upstream 104 新增为 0。

### 发布固化

已修改：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_deploy.py`
- `devops/python/ben-bot/tests/test_http_keepalive.py`
- ben-bot 版本升级为 `v1.0.9`

后续前端发布会自动把 PM2 单 worker 阈值设为 1GB。

## 七、剩余阻塞

1. 预发布机现有 SSH 密钥被拒绝，需补可用凭据或堡垒机会话，才能定位固定 CPU/load 进程。
2. 打包机、msb Mongo 文件、msb Mongo、测试 H5、SPJ 三台目前无可用 SSH，不能直接清理或检查进程内存组成。
3. msb-MongoDB 内存 7 天从约 73% 升到 80% 后趋稳，阈值 81% 暂不调整，需在获得 SSH 后确认 WiredTiger 缓存和进程构成。
4. PC 容器仍偶发 `@popperjs/core` 缺失，需前端重新构建包含依赖的镜像。
5. API 上游 `203.0.113.1:443` 仍存在偶发 prematurely closed，与本次前端 3003/3004 重启链独立。

## 八、备份与回滚

### Beszel 告警数据库

```text
/root/codex-backup/beszel-alerts-20261026-140012/data.db
```

### PM2 配置

```text
/root/codex-backup/pm2-memory-20261026-135729/
```

### ben-bot 发布模板

```text
/root/codex-backup/benbot-pm2mem-20261026-135819/benbot-app-scripts.tar.gz
SHA256: 3969b6fa4804a02671c2929b1294e5c325f44d3aa28125e3ca11146b25ccddae
```

## 九、通知记录

- 步骤 1：`124294`
- 步骤 2：`124295`
- 步骤 3：`124296`
- 步骤 4：`124297`
- 步骤 5：`124298`
- 步骤 6：`124299`
- 步骤 7：`124334`
- 步骤 8：`124336`
- 步骤 9：`124340`
- 步骤 10：`124341`

## 十、结论

- 高磁盘主机中，可访问的三台已完成安全清理。
- 5 台无告警规则的主机已补齐并实测触发。
- PM2 频繁内存重启已在运行时和未来发布模板中修正。
- 预发布高 CPU/load 已被新告警捕获，但根因定位仍受 SSH 凭据阻塞。
- 不可访问主机的分析和清理需要在补齐凭据后继续。
