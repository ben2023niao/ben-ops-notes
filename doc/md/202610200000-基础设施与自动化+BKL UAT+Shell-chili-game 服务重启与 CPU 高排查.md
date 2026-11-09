---
id: "doc-92b757751796"
title: "chili-game 服务重启与 CPU 高排查"
date: "2026-10-20T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Shell", "Docker", "监控告警", "自动化", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8820%E6%97%A5-chili-game%E6%9C%8D%E5%8A%A1%E9%87%8D%E5%90%AF%E4%B8%8ECPU%E9%AB%98%E6%8E%92%E6%9F%A5/2026%E5%B9%B410%E6%9C%8820%E6%97%A5-chili-game%E6%9C%8D%E5%8A%A1%E9%87%8D%E5%90%AF%E4%B8%8ECPU%E9%AB%98%E6%8E%92%E6%9F%A5.md"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月20日-chili-game服务重启与CPU高排查/2026年10月20日-chili-game服务重启与CPU高排查.md"
sourceSha256: "944903a69764199229041bb4265c7cdbf7c8832b4bfff2c0fe912bd57b7224c4"
sourceSystem: "project-doc"
---

# chili-game 服务重启与 CPU 高排查

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610200000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BShell-chili-game%20%E6%9C%8D%E5%8A%A1%E9%87%8D%E5%90%AF%E4%B8%8E%20CPU%20%E9%AB%98%E6%8E%92%E6%9F%A5.md)

> 整理日期：2026-10-20 00:00｜日期依据：文件名日期

日期：2026-10-20
执行人：Ben（运维）
版本：v1

## 现象

SVD/Bruce 反馈 UAT manager/worker CPU 高，服务不断重启。

## 操作记录

- `/home/stack/deploy-chili-game-stack.sh` 修改时间：2026-10-20 20:24:55
- `/home/stack/chili-game/docker-compose.yml` 修改时间：18:05:40
- 所有 `chili-game-stack` 服务在 2026-10-20 12:27:46~53 UTC（20:27 本地）被更新
- GitLab 只有 `root/devops`，没有 app 项目/流水线
- Jenkins `game-backend` 最近构建是 15:58 本地，20:27 前后没有构建记录
- 因此这次更像是在 manager 上直接执行 deploy 脚本；`blkuat` 当前有来自 1.46.146.79 的登录会话，具体执行人需 Bruce/SVD 确认

## 证据

`chili-game-stack` 大部分服务处于 `0/2 (max 1 per node)`，任务报：

```text
task: non-zero exit (137): dockerexec: unhealthy container
task: non-zero exit (143): dockerexec: unhealthy container
```

`game-merchant-api` 报：

```text
failed to resolve reference ".../game/game-merchant-api:1.0.0-uat": not found
```

healthcheck 配置：

```text
test: ["CMD", "nc", "-z", "-w", "3", "localhost", "<port>"]
start_period: 30s
interval: 10s
retries: 5
```

应用日志显示 Spring Boot 启动需要 41~69 秒：

```text
Root WebApplicationContext initialization completed in 46696 ms
Started GateWayApplication in 69.297 seconds
```

30s start_period + 5×10s 重试，容器在应用还没完全 ready 时就被判 unhealthy，随后被 SIGKILL/重启。

## 根因

1. `start_period: 30s` 对 Spring Boot 启动太短，健康检查在启动完成前就开始累计失败。
2. healthcheck 使用 `localhost`，存在 IPv6/IPv4 解析差异风险，建议固定 `203.0.113.1`。
3. `game-merchant-api:1.0.0-uat` 没有推到 Harbor，stack deploy 直接 Rejected。
4. 多个服务同时重启，造成 CPU 抖动，叠加此前的 chili-pay 批量负载，形成报警刷屏。

## 给开发的修复建议

```yaml
healthcheck:
  test: ["CMD", "nc", "-z", "-w", "3", "203.0.113.1", "<port>"]
  interval: 10s
  timeout: 3s
  retries: 10
  start_period: 180s
```

执行顺序：

1. 先把 `game-merchant-api:1.0.0-uat` 推到 Harbor。
2. 修改 `/home/stack/chili-game/docker-compose.yml` 的 healthcheck。
3. 重新 `docker stack deploy`，观察 `docker service ps` 是否从 `0/2` 变成 `2/2`。
4. 暂不重启其他无关服务。

## 当前状态

截至 20:38 本地，`chili-game-stack` 仍多数为 `0/2`，`game-merchant-api` 仍缺镜像；未修改开发 stack 配置，等待开发确认后执行。

## 提交

- 主提交：`a4fd970`
- 文档收尾提交：见 `git log -1`
- 远端：`root/devops` main
