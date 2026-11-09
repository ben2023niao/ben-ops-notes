---
id: "doc-8c34df20c522"
title: "【清理】死链 agent 与重复主机记录处置"
date: "2026-10-19T22:40:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "Nginx", "监控告警", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2240-%E3%80%90%E6%B8%85%E7%90%86%E3%80%91%E6%AD%BB%E9%93%BE%20agent%20%E4%B8%8E%E9%87%8D%E5%A4%8D%E4%B8%BB%E6%9C%BA%E8%AE%B0%E5%BD%95%E5%A4%84%E7%BD%AE.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2240-【清理】死链 agent 与重复主机记录处置.md"
sourceSha256: "c4805fd816b6fc9d87c9e3368548b466731befc45d5fe329e9ee1c28e5cfbcf4"
sourceSystem: "project-doc"
---

# 【清理】死链 agent 与重复主机记录处置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610192240-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E3%80%90%E6%B8%85%E7%90%86%E3%80%91%E6%AD%BB%E9%93%BE%20agent%20%E4%B8%8E%E9%87%8D%E5%A4%8D%E4%B8%BB%E6%9C%BA%E8%AE%B0%E5%BD%95%E5%A4%84%E7%BD%AE.md)

> 整理日期：2026-10-19 22:40｜日期依据：文件名日期

- 时间：2026-10-19 22:35 ~ 22:45（北京时间）

## 一、38.92.8.151 上的死链 agent（已清除）

### 核实

```
容器：beszel-agent（henrygd/beszel-agent），启动于 2026-08-12
配置：HUB_URL=http://3.35.9.127:8090，LISTEN=45876
日志：每 10 秒一次
   WARN WebSocket connection failed err="dial tcp 3.35.9.127:8090: connect: connection refused"
```

- 3.35.9.127 从公网完全不可达（22 端口与 8090 端口都超时），该 agent 已持续 2 个多月往一个不存在的 Hub 推送
- 与本次新装的 `beszel-agent-52`（HUB_URL=http://52.79.252.255:8090）互不影响

### 处置

```bash
docker rm -f beszel-agent        # 已执行
```

剩余容器：

```
beszel-agent-52   henrygd/beszel-agent   Up   ← 指向我们自己的 Hub
nginx-666         nginx:latest           Up
```

## 二、173.231.49.86 与 173.231.49.82 重复（已去重标注）

### 核实

```
173.231.49.82  hostname=173-231-49-82  machine-id=32f0a51d75e847358932a226b74ee2c8
173.231.49.86  hostname=173-231-49-82  machine-id=32f0a51d75e847358932a226b74ee2c8
```

**machine-id 完全相同**，确认是同一台机器的两个公网地址。

### 处置

1. **Beszel 监控**（保留一条）：

```
原名：短剧-正式服-业务-173.231.49.82
现名：短剧-正式服-业务-173.231.49.82/.86      ← 名称里标明双 IP，避免以后重复添加
```

2. **Spug 主机记录**（id=25，无任何定时任务引用）：

```
原名：短剧-正式服（173.231.49.86）
现名：[重复项]短剧-正式服(与173.231.49.82同机)
备注：2026-10-19 核实：与 173.231.49.82 为同一台（machine-id 相同），无任务引用，可删除
```

> 采用「标注而非删除」：`tasks` 表 50 条任务中没有任何一条引用该主机，但保留记录可避免历史操作记录失联；确认不再需要时可直接在 Spug 里删除。

## 三、验证

- `docker ps` 确认 38.92.8.151 只剩业务容器与我们新装的 agent
- Beszel 系统中 `短剧-正式服-业务-173.231.49.82/.86` 状态 up
- Spug `hosts.id=25` 名称与备注已更新，其他主机记录未改动
