---
id: "doc-89ecfa69e73f"
title: "线上 H5 全链路 502 与 MongoDB 从库别名故障复盘"
date: "2026-10-20T23:10:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "Redis", "监控告警"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2310-%E3%80%90%E4%BA%8B%E6%95%85%E5%A4%8D%E7%9B%98%E3%80%91%E7%BA%BF%E4%B8%8AH5%E5%85%A8%E9%93%BE%E8%B7%AF502%E4%B8%8EMongoDB%E4%BB%8E%E5%BA%93%E5%88%AB%E5%90%8D%E6%95%85%E9%9A%9C.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2310-【事故复盘】线上H5全链路502与MongoDB从库别名故障.md"
sourceSha256: "5dcacdae7971496e19d12f6731c812593286876bdb4079001d7b3392ebe6d3e8"
sourceSystem: "project-doc"
---

# 线上 H5 全链路 502 与 MongoDB 从库别名故障复盘

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2310-【事故复盘】线上H5全链路502与MongoDB从库别名故障.md`

> 整理日期：2026-10-20 23:10｜日期依据：文件名日期

## 一、结论摘要

2026-10-20 晚，`h5.18h.game`、`www.youdianse.com` 及同源页面出现 502、超时和
SDK `5003 数据执行错误`。最终根因是：

1. 配置仓库中的 MongoDB 从库已拆成 `server.db2a.com` 和 `server.db2b.com`；
2. web/cron 容器 `/etc/hosts` 仍只有旧的 `server.db2.com`；
3. MongoDB 驱动无法解析 `server.db2b.com`，大量查询失败并持续重试；
4. PHP-FPM 64 个 worker 全部占满，接口排队到数秒；
5. H5/PC Nuxt SSR 因 API 慢请求堆积，PM2 worker 达到 500MB 限制后反复重启；
6. CloudFront 回源得到的上游连接不稳定，最终对用户表现为 502/超时。

数据库实例、Redis、主库端口和 CloudFront/DNS/证书本身均正常。

## 二、影响范围

- 页面：`h5.18h.game`、`www.youdianse.com` 及共用同一套 SSR/API 的域名。
- API：`/api/v1/*`、`/api/sdk/*`、页面 SSR 初始化请求。
- 用户表现：页面打不开、接口超时、SDK 返回 `5003 数据执行错误`。
- 未影响：数据库服务本身、Redis 服务本身、域名解析、TLS 证书、后端容器存活。

## 三、详细时间线

| 时间（北京时间） | 事件 |
| --- | --- |
| 22:09:05 | 运维从 CICD 发起 `main / 688f43568c2e` 发布。 |
| 22:09:28 | 发布因业务仓库存在旧 `.bak` 文件触发 dirty 保护而失败，现网未切换。 |
| 22:19:39 | 监控显示页面仍正常，随后开始出现整体性异常。 |
| 22:19:55 | 同源页面可用性快速下降，CloudFront 开始返回 502。 |
| 22:20 左右 | 网关 Nginx 日志持续出现 `upstream prematurely closed connection`；H5 SSR 容器 CPU 接近 100%。 |
| 22:25:40 | 运维重新从 CICD 发布 `688f43568c2e`。 |
| 22:26:38 | 白名单同步通过，web/nginx/cron 健康检查一度为 SUCCESS；数据库异常仍未暴露。 |
| 22:27 左右 | 前端源站 `3003` 本地可返回 200，但延迟约 10～15 秒；CloudFront 仍返回 502。 |
| 22:29 左右 | 后端 PHP-FPM 显示 64/64 busy；所有常规 API 耗时约 2～5 秒，SSR 请求继续堆积。 |
| 22:30 左右 | H5/PC SSR 先后滚动重启，PM2 worker 临时恢复。 |
| 22:31 左右 | PM2 从 4 个 worker 恢复为 8 个 worker，但仍频繁接近 500MB 重启阈值。 |
| 22:34 左右 | 宝塔本机 `Host: h5.18h.game` 返回 200，证明 Nginx、证书和前端容器可达。 |
| 22:36 左右 | 浏览器 UA 访问公网 H5 可返回 200，但耗时约 27 秒，确认是应用层慢而不是 DNS/证书。 |
| 22:38 左右 | PM2 内存重启阈值调整为 `1G`，H5/PC 滚动 reload，单 worker 内存回落到 110～165MB。 |
| 22:40 左右 | 后端错误日志明确显示 `Failed to resolve 'server.db2b.com'`。 |
| 22:41 左右 | web/cron 热补 `server.db2a.com`、`server.db2b.com` 到 `/etc/hosts`。 |
| 22:42 左右 | MongoDB/Redis 主机全部可解析，API 从超时降到约 0.73 秒。 |
| 22:43 左右 | PHP-FPM 配置由 64 调整为 128，并重建 web 容器使配置生效。 |
| 22:44 左右 | 公网 H5 约 3.4 秒返回 200；www 约 1 秒返回 200。 |
| 22:47 左右 | 稳定性复测：H5/www 均约 0.8 秒返回 200，API 约 0.002 秒。 |

## 四、根因证据

### 4.1 业务配置

正式 `.env.prod` 中：

```text
[database.mongodb.slave1]
host = server.db2a.com

[database.mongodb.slave2]
host = server.db2b.com
```

配置仓库、宿主机和容器内 `.env` SHA256 完全一致，说明配置文件同步本身没有丢失。

### 4.2 容器 hosts 缺失

容器原先仅有：

```text
203.0.113.1  server.db2.com
203.0.113.1 server.db2.com
```

没有 `server.db2a.com` 和 `server.db2b.com`。

应用错误：

```text
No suitable servers found (`serverSelectionTryOnce` set):
[Failed to resolve 'server.db2b.com']
```

### 4.3 数据库本身正常

实测：

- `server.db1.com:27017` open
- `server.db2a.com:27017` open，指向 `203.0.113.1`
- `server.db2b.com:27017` open，指向 `203.0.113.1`
- Redis `203.0.113.1:6379` open

### 4.4 容量放大因素

- PHP-FPM 故障时达到 64/64 busy。
- H5 PM2 8 worker，单 worker 约 450～500MB，旧阈值 `500M` 触发周期性 kill/restart。
- PC PM2 同样接近阈值并出现 `@popperjs/core` 缺失异常。

## 五、恢复操作

1. 给 web/cron 容器补齐正式环境数据库别名：

   ```text
   203.0.113.1  server.db2a.com
   203.0.113.1 server.db2b.com
   ```

2. 在 `docker-compose.yml` 的共享 `extra_hosts` 中持久化相同映射。
3. H5/PC PM2 `max_memory_restart` 从 `500M` 调整为 `1G`，滚动 reload。
4. PHP-FPM 调整并重建 web：

   ```text
   pm.max_children = 128
   pm.start_servers = 32
   pm.min_spare_servers = 16
   pm.max_spare_servers = 64
   ```

5. 保留旧 `server.db2.com` 两条映射，兼容历史配置。

## 六、恢复结果

- 业务版本：`main / 688f43568c2e`
- web/nginx/cron：running
- `h5.18h.game`：HTTP 200，约 0.8 秒
- `www.youdianse.com`：HTTP 200，约 0.8 秒
- API `/api/v1/system/info`：HTTP 200，约 0.002 秒
- Mongo/Redis 主机：全部可解析并可连接
- PHP-FPM：`pm.max_children=128`

## 七、已落地的兜底

### 7.1 数据库主机名/端口守卫

脚本：

```text
ops/production/scripts/youdianse-db-alias-guard.py
```

正式机 cron：

```text
*/2 * * * * /usr/bin/flock -xn /var/run/youdianse-db-alias-guard.lock \
  /usr/bin/python3 /opt/docker-youdianse-php/ops/production/scripts/youdianse-db-alias-guard.py \
  >> /var/log/youdianse-db-alias-guard.log 2>&1
```

能力：

- 从 `.env.prod` 提取全部 Mongo/Redis host/port；
- 在 web、cron 内检查域名解析；
- 已知正式数据库别名缺失时自动补 `/etc/hosts`；
- 从 web 容器内测试 Mongo/Redis TCP；
- 只写本地日志，不发群通知，不输出密码。

实测结果：`RESULT PASS`，5 个 Mongo/Redis 目标在两个容器内全部可解析，4 个端口全部 open。

### 7.2 SSR 内存阈值守卫

脚本：

```text
ops/production/scripts/youdianse-ssr-memory-guard.py
```

网关 cron：

```text
*/5 * * * * /usr/bin/flock -xn /var/run/youdianse-ssr-memory-guard.lock \
  /usr/bin/python3 /usr/local/sbin/youdianse-ssr-memory-guard.py \
  >> /var/log/youdianse-ssr-memory-guard.log 2>&1
```

能力：

- 容器重建或旧镜像恢复 500MB 阈值时自动改回 1G；
- H5/PC 分别滚动 reload；
- 不发送群通知。

## 八、如何彻底访问策略验证此类问题

### 8.1 配置发布前做契约校验

发布前必须校验：

- `.env` 中引用的每个 Mongo/Redis host；
- web、cron 容器内是否可解析；
- 对应端口是否可达；
- 配置仓库、宿主机、容器内 `.env` SHA256 是否一致。

任何一项失败，发布直接失败，不允许进入容器重建。

### 8.2 Compose hosts 与 env 同步维护

数据库从库域名调整时必须同时修改：

- config-repo 的 `.env.prod`；
- `docker-compose.yml` 的 `extra_hosts`；
- 当前 web/cron 容器 `/etc/hosts`（由重建或守卫自动完成）。

禁止只改 `.env` 后直接发布。

### 8.3 禁止容器内部手工长期维护

本次热补 `/etc/hosts` 只用于恢复；长期真值必须落在 compose 和配置仓库。

### 8.4 发布后真实业务探测

不能只做端口探测。发布后至少验证：

- Mongo 主库及两个从库域名解析和 MongoDB 握手；
- `/api/v1/system/info`；
- `/api/sdk/system/info`；
- H5 首页与一个带渠道参数页面；
- PC 首页；
- PHP-FPM busy/idle；
- SSR CPU、内存和 PM2 reload 次数。

### 8.5 容量与告警

- PHP-FPM 持续出现 `64/64 busy` 时告警；
- H5/PC PM2 worker 10 分钟内重启超过阈值时告警；
- 公网 H5 1 分钟连续 502 时告警；
- 日志中 `Failed to resolve 'server.db2'` 或 `No suitable servers found` 出现即高优先级告警；
- 告警内容只保留在运维内部，不向业务群输出数据库细节。

### 8.6 回滚原则

若发布后 5 分钟内出现：

- 全域名同时 502；
- API 错误率快速上升；
- 数据库域名解析失败；
- FPM 持续满载；

应优先回滚上一稳定版本，再继续排查，避免长时间带故障运行。

## 九、相关提交

- `cab9c3a`：修复 Debian Bullseye apt 归档源导致的正式环境镜像构建失败。
- `8ceed0f`：补齐 MongoDB `db2a/db2b` 容器 hosts 别名并扩容 PHP-FPM。
- 本次追加：数据库别名守卫、SSR 内存阈值守卫及本事故复盘。
