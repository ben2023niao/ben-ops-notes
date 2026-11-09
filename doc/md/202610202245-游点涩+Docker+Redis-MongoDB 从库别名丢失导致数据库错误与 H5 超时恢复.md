---
id: "doc-8b9adc611d6d"
title: "MongoDB 从库别名丢失导致数据库错误与 H5 超时恢复"
date: "2026-10-20T22:45:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Redis", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2245-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91MongoDB%E4%BB%8E%E5%BA%93%E5%88%AB%E5%90%8D%E4%B8%A2%E5%A4%B1%E5%AF%BC%E8%87%B4%E6%95%B0%E6%8D%AE%E5%BA%93%E9%94%99%E8%AF%AF%E4%B8%8EH5%E8%B6%85%E6%97%B6%E6%81%A2%E5%A4%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-20-2245-【问题排查】MongoDB从库别名丢失导致数据库错误与H5超时恢复.md"
sourceSha256: "5d495f8cd2493df9ae192ac9a7af7f81e83d54fd93c666e563b66bbe6cabb099"
sourceSystem: "project-doc"
---

# MongoDB 从库别名丢失导致数据库错误与 H5 超时恢复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610202245-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BRedis-MongoDB%20%E4%BB%8E%E5%BA%93%E5%88%AB%E5%90%8D%E4%B8%A2%E5%A4%B1%E5%AF%BC%E8%87%B4%E6%95%B0%E6%8D%AE%E5%BA%93%E9%94%99%E8%AF%AF%E4%B8%8E%20H5%20%E8%B6%85%E6%97%B6%E6%81%A2%E5%A4%8D.md)

> 整理日期：2026-10-20 22:45｜日期依据：文件名日期

## 现象

- `h5.18h.game`、`www.youdianse.com` 等页面出现 502、超时或 SDK `5003 执行数据错误`。
- 后端应用日志持续报：

  ```text
  No suitable servers found (`serverSelectionTryOnce` set):
  [Failed to resolve 'server.db2b.com']
  ```

- PHP-FPM 同时出现 64/64 worker 全部 busy，H5/PC SSR 请求堆积并触发 Node worker 内存重启。

## 根因

- 正式环境 `.env.prod` 中 Mongo 从库配置已改为：
  - `server.db2a.com`
  - `server.db2b.com`
- 但 web/cron 容器的 `/etc/hosts` 只有旧的 `server.db2.com`，且仅指向两台从库 IP。
- MongoDB 驱动选择次级节点时无法解析 `server.db2b.com`，每次业务查询都要失败/重试，
  最终造成 API 慢请求、FPM worker 占满和前端 SSR 堆积。
- 数据库本身、Redis、Mongo 主库端口均正常。

## 修复

在 `docker-compose.yml` 的共享 DB hosts 配置中增加：

```yaml
- "server.db2a.com:203.0.113.1"
- "server.db2b.com:203.0.113.1"
```

同时给当前 web/cron 容器热补 `/etc/hosts`：

```text
203.0.113.1  server.db2a.com
203.0.113.1 server.db2b.com
```

保留旧的 `server.db2.com` 两条映射用于兼容历史配置。

## 并发容量

故障期间后端 PHP-FPM 达到 `64/64` busy。为快速恢复并留出空闲 worker，
本次将 `php/fpm-pool.conf` 调整为：

```text
pm.max_children = 128
pm.start_servers = 32
pm.min_spare_servers = 16
pm.max_spare_servers = 64
```

只重建了 `youdianse-main-php-web`，配置已在容器内生效。

## 前端恢复

- H5 与 PC 的 PM2 运行参数由 `max_memory_restart: 500M` 调整为 `1G`，
  避免正常高并发下 worker 在 450～500MB 区间频繁重启。
- H5/PC 均执行滚动 reload，未同时中断两套页面。

## 验证

- `server.db2a.com -> 203.0.113.1`
- `server.db2b.com -> 203.0.113.1`
- Mongo 主库 `server.db1.com:27017` open
- Redis `203.0.113.1:6379` open
- PHP-FPM 配置已生效为 `pm.max_children=128`
- 公网 `https://h5.18h.game/`：HTTP 200，约 3.4 秒
- 公网 `https://h5.18h.game/?channel=yds1033`：HTTP 200，约 2.9 秒
- 公网 `https://www.youdianse.com/`：HTTP 200，约 1 秒

## 注意

- 数据库故障细节不发送群通知，仅保留在仓库文档中。
- 后续调整 Mongo 从库域名时，必须同步更新 `.env.prod` 和 compose `extra_hosts`。
