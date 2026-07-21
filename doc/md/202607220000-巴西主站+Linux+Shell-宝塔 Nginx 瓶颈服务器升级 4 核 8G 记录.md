---
id: "doc-61753dabc3a7"
title: "宝塔 Nginx 瓶颈服务器升级 4 核 8G 记录"
date: "2026-07-22T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-07-22-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%AE%9D%E5%A1%94Nginx%E7%93%B6%E9%A2%88%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%8D%87%E7%BA%A74%E6%A0%B88G%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-07-22-【优化】宝塔Nginx瓶颈服务器升级4核8G记录.md"
sourceSha256: "3df54dafcec14b6cca0ff9b52c82b9eb339325bdfc081b8337135834d29e0737"
sourceSystem: "project-doc"
---

# 宝塔 Nginx 瓶颈服务器升级 4 核 8G 记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-07-22-【优化】宝塔Nginx瓶颈服务器升级4核8G记录.md`

> 整理日期：2026-07-22 00:00｜日期依据：文件名日期

日期：2026-07-22
范围：宝塔 / Nginx 入口服务器 `35.247.205.6`
实例：`dbqp-saopaulo-game-results-data-bt`
Zone：`southamerica-east1-a`

## 背景

压力测试后确认瓶颈集中在宝塔 Nginx 入口服务器。升级目标：

- 先备份宝塔关键配置。
- 再创建 GCP 磁盘快照。
- 将实例从 2 核 4G 升级到 4 核 8G。
- 每个关键步骤完成验证后通知飞机群。

## 升级前状态

| 项目 | 值 |
| --- | --- |
| 公网 IP | `35.247.205.6` |
| 内网 IP | `203.0.113.1` |
| hostname | `dbqp-saopaulo-game-results-data-bt` |
| GCP 实例名 | `dbqp-saopaulo-game-results-data-bt` |
| Zone | `southamerica-east1-a` |
| 原规格 | `e2-medium` |
| CPU | `2` |
| 内存 | `3.8Gi` |
| 系统盘 | `500GB` |
| 根分区使用 | `257G / 485G`，约 `53%` |
| Nginx | `active` |
| BT 面板 | `active` |
| ben-bot | `Up` |

升级前端口监听：

```text
80    nginx
443   nginx
30264 BT-Panel
```

## 宝塔配置备份

备份文件：

```text
/root/baota-config-backup-20260722_180516.tar.gz
/root/baota-config-backup-20260722_180516.tar.gz.sha256
```

备份结果：

| 项目 | 值 |
| --- | --- |
| 大小 | `46,523,478 bytes`，约 `45MB` |
| SHA256 | `d0651d989e2b4345e0e419acc16c8fa81ded4c0596b7ed720fafd5424ea4fecc` |
| 校验 | `tar -tzf` 通过 |

备份范围：

```text
/www/server/panel/data
/www/server/panel/config
/www/server/panel/vhost
/www/server/nginx/conf
/etc/nginx
```

同时保存的检查清单：

```text
hostname
date
uname
free
df
ss -lntp
systemctl is-active nginx
systemctl is-active bt
nginx -T
docker ps
gcloud compute instances describe
```

说明：

- `/www/wwwroot` 约 `153G`，`/www/backup` 约 `20G`，未重复打包进配置备份。
- 上述大目录由后续整盘快照覆盖。

## GCP 磁盘快照

快照名称：

```text
baota-nginx-pre-upgrade-20260722-1805
```

快照验证：

| 项目 | 值 |
| --- | --- |
| 状态 | `READY` |
| Disk size | `500GB` |
| storageBytes | `7,631,743,360` |
| creationTimestamp | `2026-07-22T03:06:21.059-07:00` |

快照源盘：

```text
dbqp-saopaulo-game-results-data-bt
```

## 升级操作

由于升级 GCP machine type 必须停止实例，操作通过 GCP Compute API 从本地控制，避免在宝塔服务器停机后 SSH 断开导致无法继续启动。

执行顺序：

1. 从宝塔服务器获取短期 GCP access token。
2. 从 ben-bot 容器读取 Telegram bot token 和目标 chat id，用于停机期间继续通知。
3. 调用 GCP API 停止实例。
4. 等待实例状态变为 `TERMINATED`。
5. 调用 `setMachineType` 设置规格为 `e2-custom-4-8192`。
6. 调用 GCP API 启动实例。
7. 等待实例状态变为 `RUNNING`。
8. SSH 回连验证 CPU、内存、Nginx、BT 面板和 ben-bot。

规格变更：

```text
e2-medium -> e2-custom-4-8192
```

## 升级后状态

GCP 复核：

```text
NAME                                MACHINE_TYPE      STATUS   NETWORK_IP  NAT_IP
dbqp-saopaulo-game-results-data-bt  e2-custom-4-8192  RUNNING  203.0.113.1  35.247.205.6
```

系统复核：

```text
hostname: dbqp-saopaulo-game-results-data-bt
cpu=4
Mem: 7.8Gi total, 6.8Gi available
/dev/root 485G total, 257G used, 229G available, 53%
```

服务复核：

```text
nginx: active
bt: active
dbqp-ben-bot: Up
```

端口复核：

```text
80    nginx LISTEN
443   nginx LISTEN
30264 BT-Panel LISTEN
```

外部连通性：

```text
http://35.247.205.6/ -> HTTP/1.1 403 Forbidden
35.247.205.6:30264 -> TCP succeeded
```

说明：

- HTTP 80 返回 `403 Forbidden` 属于 Nginx 已响应，说明入口服务已恢复。
- 30264 为宝塔面板端口，TCP 连通成功。

## 飞机群通知

本次按步骤通知飞机群：

1. 收到压力测试结论，说明计划和会有短暂停机。
2. 只读探测完成，确认实例、规格、服务和端口。
3. 宝塔配置备份完成，报告备份文件、大小和 SHA256。
4. GCP 磁盘快照完成，确认 snapshot `READY`。
5. 开始停机升级，说明当前规格和目标规格。
6. 实例停止并验证 `TERMINATED`。
7. 机器规格修改完成。
8. 实例启动并验证 `RUNNING`。
9. 升级后服务验证完成。
10. 最终完成汇总。

## 回滚点

如果升级后出现严重异常，可使用：

```text
baota-nginx-pre-upgrade-20260722-1805
```

作为整盘恢复快照。

如果只需要恢复宝塔/Nginx 配置，可使用：

```text
/root/baota-config-backup-20260722_180516.tar.gz
```

## 最终结论

宝塔 Nginx 入口服务器已完成扩容：

```text
2 核 / 4G -> 4 核 / 8G
```

最终验证通过：

- GCP 状态 `RUNNING`
- 机器规格 `e2-custom-4-8192`
- 系统 CPU `4`
- 系统内存 `7.8Gi`
- Nginx `active`
- BT 面板 `active`
- `80/443/30264` 正常监听
- 宝塔面板端口 TCP 可达
- ben-bot 已恢复运行
