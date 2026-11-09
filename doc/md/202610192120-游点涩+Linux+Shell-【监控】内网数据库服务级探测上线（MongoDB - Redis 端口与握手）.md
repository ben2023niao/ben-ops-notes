---
id: "doc-535d5b89d5ba"
title: "【监控】内网数据库服务级探测上线（MongoDB / Redis 端口与握手）"
date: "2026-10-19T21:20:00+08:00"
dateSource: "正文日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Redis", "监控告警", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2130-%E3%80%90%E7%9B%91%E6%8E%A7%E3%80%91%E5%86%85%E7%BD%91%E6%95%B0%E6%8D%AE%E5%BA%93%E6%9C%8D%E5%8A%A1%E7%BA%A7%E6%8E%A2%E6%B5%8B%E4%B8%8A%E7%BA%BF%EF%BC%88Mongo/Redis%20%E7%AB%AF%E5%8F%A3%E4%B8%8E%E6%8F%A1%E6%89%8B%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2130-【监控】内网数据库服务级探测上线（Mongo/Redis 端口与握手）.md"
sourceSha256: "0bfd06197ed1c14e9c1a41f858fbfd7181e579e69ced755f4df45070e7b8af1d"
sourceSystem: "project-doc"
---

# 【监控】内网数据库服务级探测上线（MongoDB / Redis 端口与握手）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610192120-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E3%80%90%E7%9B%91%E6%8E%A7%E3%80%91%E5%86%85%E7%BD%91%E6%95%B0%E6%8D%AE%E5%BA%93%E6%9C%8D%E5%8A%A1%E7%BA%A7%E6%8E%A2%E6%B5%8B%E4%B8%8A%E7%BA%BF%EF%BC%88MongoDB%20-%20Redis%20%E7%AB%AF%E5%8F%A3%E4%B8%8E%E6%8F%A1%E6%89%8B%EF%BC%89.md)

> 整理日期：2026-10-19 21:20｜日期依据：正文日期

- 时间：2026-10-19 21:20 ~ 21:35（北京时间）
- 背景：游点涩线上数据库三台只有内网地址（172.31.x），外部监控系统无法直接探活
- 方案：**在内网侧（后端 16.209.16.108）部署一个轻量探测脚本**，主动探测内网端口并直接告警——不需要隧道、不需要开放任何入向端口、不改安全组

## 一、探测项

| 名称 | 地址 | 协议 | 判定 |
| --- | --- | --- | --- |
| 主库 | 203.0.113.1:27017 | MongoDB | OP_MSG `hello` 握手（返回 291 字节） |
| 从库01 | 203.0.113.1:27017 | MongoDB | OP_MSG `hello` 握手 |
| 从库01-Redis | 203.0.113.1:6379 | Redis | `PING` → `+PONG` |
| 从库02 | 203.0.113.1:27017 | MongoDB | OP_MSG `hello` 握手 |

只做连接与协议握手，**不读不写任何业务数据**。

## 二、部署方式

```
脚本：   /usr/local/sbin/yds-db-probe.py
配置：   /etc/youdianse/db-probe.env（bot token，600 root）
日志：   /var/log/yds-db-probe.log（每次一行 JSON）
状态：   /var/run/yds-db-probe-state.json（连续失败计数）
定时：   crontab  */2 * * * *  每 2 分钟执行一次
```

告警策略：

- 连续失败 ≥ 2 次才判定为 down（避免网络抖动误报）
- 状态变化（正常→异常 / 异常→正常）才发 Telegram，正文带 `@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2 @fyb99`
- 同时发「18GAME_ 上线群」与「18game运维」
- 记录在 `alerts` 之外的独立日志里，便于回溯

## 三、首次执行结果（21:30）

| 目标 | 结果 | 耗时 |
| --- | --- | ---: |
| 主库 203.0.113.1:27017 | ✅ mongo hello 291 bytes | 349 ms |
| 从库01 203.0.113.1:27017 | ✅ mongo hello 291 bytes | 327 ms |
| 从库01-Redis 203.0.113.1:6379 | ✅ +PONG | 1.3 ms |
| 从库02 203.0.113.1:27017 | ✅ mongo hello 291 bytes | 325 ms |

> 观察：三台 Mongo 的 `hello` 握手都在 **325~350 ms**，而 Redis 只有 1.3 ms。正常空闲的 Mongo 握手应在几毫秒级，这个延迟与当前主库读放大（每秒扫百万索引键）一致，属于负载偏高的信号，建议结合前面的 profiling 一起看。

## 四、与「放 blackbox + 隧道」方案的对比

| | 本方案（内网探测脚本） | blackbox + SSH 隧道 |
| --- | --- | --- |
| 需要开入向端口 | 不需要 | 不需要（但需要隧道进程） |
| 需要改安全组 | 不需要 | 不需要 |
| 额外容器 | 0 | 2 个（blackbox + 隧道） |
| 密钥/隧道维护 | 无 | 需要维护隧道密钥与端口转发 |
| 覆盖 | Mongo/Redis 端口与协议握手 + 告警 | 任意 HTTP/TCP 探测 |

如后续 Davie 的 Prometheus 需要集中采数，可让探测脚本额外输出 Prometheus textfile 格式（或由内网机暴露一个只读端口给 Prometheus），这个可以再对接。

## 五、维护

- 追加/修改探测目标：改脚本里的 `TARGETS` 列表后重新 install 即可
- 手动执行：`sudo python3 /usr/local/sbin/yds-db-probe.py --dry-run`
- 查看最近结果：`sudo tail -5 /var/log/yds-db-probe.log`
- 停用：`sudo crontab -l | grep -v yds-db-probe | sudo crontab -`
