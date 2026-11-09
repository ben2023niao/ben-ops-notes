---
id: "doc-69c3d5c4d8d7"
title: "测试环境根盘健康告警与 Docker 垃圾清理记录"
date: "2026-07-29T18:03:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "Nginx", "监控告警", "自动化", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-29-1803-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E6%A0%B9%E7%9B%98%E5%81%A5%E5%BA%B7%E5%91%8A%E8%AD%A6%E4%B8%8EDocker%E5%9E%83%E5%9C%BE%E6%B8%85%E7%90%86%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-29-1803-【优化】测试环境根盘健康告警与Docker垃圾清理记录.md"
sourceSha256: "5908b75165bb836dc1139b6299842bb9d6db6590bbeb377db182b3de21008101"
sourceSystem: "project-doc"
---

# 测试环境根盘健康告警与 Docker 垃圾清理记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607291803-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E6%A0%B9%E7%9B%98%E5%81%A5%E5%BA%B7%E5%91%8A%E8%AD%A6%E4%B8%8E%20Docker%20%E5%9E%83%E5%9C%BE%E6%B8%85%E7%90%86%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 18:03｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-29
环境：游点涩测试环境（dev 分支）
分类：优化

## 背景

2026-07-29 17:55 北京时间，测试环境收到根盘磁盘告警：

```text
游点涩测试健康告警
角色 测试服务器
磁盘 根盘80.5% >= 80%

游点涩_test-H5 disk usage above threshold
Usage of root averaged 80.04% for the previous 10 minutes.
```

测试环境为单机部署，前端、后端、宝塔都在 `38.92.8.34`。本次只处理测试环境，不触碰正式环境。

## 敏感信息边界

- 测试服务器连接信息已保存到本地私有目录 `.private/test-env-server-info/`。
- `.private/` 已写入本地 `.git/info/exclude`，不提交代码仓库。
- 本文档不记录 SSH 密码、Telegram token、chat_id、发布口令、私钥或 Git 凭据。

## 清理前排查

```bash
df -hT /
du -xhd1 / | sort -h | tail -20
du -xhd1 /var | sort -h | tail -20
docker system df
docker builder du
journalctl --disk-usage
```

清理前关键结果：

| 项 | 数值 |
| --- | --- |
| 根盘 | `/dev/sda1`，29G，总已用 24G，可用 5.7G，使用率 81% |
| `/var` | 15G |
| `/var/lib` | 11G |
| `/var/log` | 3.8G |
| `/opt/docker-youdianse-php` | 370M |
| 业务运行日志 | `/opt/docker-youdianse-php/runtime/app-logs` 约 214M |
| Docker Images | 9.72G，总可回收 4.544G |
| Docker Containers | 可回收 156M |
| Docker Build Cache | 5.99G，总可回收 5.99G，其中 private 约 3.904G |
| systemd journal | 2.9G |

结论：根盘告警主因是 Docker 构建缓存、旧镜像和系统 journal；业务运行日志不是主因，本次未清理业务日志。

## 清理动作

执行命令：

```bash
docker container prune -f
docker image prune -af
docker builder prune -af
docker volume prune -f
journalctl --vacuum-size=500M
```

清理边界：

- 只清理 Docker 停止容器、未使用镜像、未使用 build cache、未使用 volume 和 systemd journal 归档。
- 不删除 `/opt/docker-youdianse-php/runtime/app-logs` 普通业务日志。
- 不删除业务仓库、运维仓库、宝塔配置、运行容器或当前镜像。

## 清理结果

| 项 | 清理前 | 清理后 |
| --- | --- | --- |
| 根盘使用率 | 81% | 47% |
| 根盘已用 | 24G | 14G |
| 根盘可用 | 5.7G | 16G |
| Docker Images | 18 个，9.72G | 5 个，1.922G |
| Docker Containers | 7 个，可回收 156M | 6 个，0 可回收 |
| Docker Build Cache | 142 项，5.99G | 0 |
| systemd journal | 2.9G | 544M |

本次约释放 10G 根盘空间，根盘告警解除。

## 运行验证

清理后容器状态：

```text
youdianse-dev-php-cron                   Up
youdianse-dev-php-nginx                  Up
youdianse-dev-php-web                    Up
youdianse_test_18game_h5_client_3003     Up
youdianse_pc_dev_18game_pc_client_3004   Up
youdianse_test-beszel-agent              Up
```

本机 HTTP 验证：

```text
CICD:  http://203.0.113.1:18090 -> 200
后台:  http://203.0.113.1:8088/admin1866/login -> 200
H5:    http://203.0.113.1:3003 -> 200
```

公网入口在清理前已确认可访问：

```text
https://cicd.youdianse-test.xyz -> 200
https://admin.youdianse-test.xyz/admin1866/login -> 200
https://h5.youdianse-test.xyz/ -> 200
```

## 后续建议

1. 测试环境根盘只有 29G，构建和发布频繁时 Docker build cache 容易快速增长。
2. 根盘超过 75% 时可先执行 `docker system df` 和 `journalctl --disk-usage` 判断是否为 Docker/journal 垃圾。
3. 常规清理优先使用本次命令；不要直接删除业务日志和仓库目录。
4. 若后续频繁触发 80% 告警，建议把 Docker 数据目录或业务日志迁移到更大的数据盘，或给根盘扩容。
