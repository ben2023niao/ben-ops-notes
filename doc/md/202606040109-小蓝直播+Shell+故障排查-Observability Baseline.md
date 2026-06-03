---
id: "doc-f94bee023ebd"
title: "Observability Baseline"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/architecture/observability-baseline.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/architecture/observability-baseline.md"
sourceSha256: "a4afccc33039ee7c6d5fa6c90fc0c5c178d60c0de8af5ee6597b928797247afc"
sourceSystem: "project-doc"
---

# Observability Baseline

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/architecture/observability-baseline.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

本文定义从 MVP 到大流量项目的最小观测基线。

## 1. MVP

1. 服务启动/健康检查，即 health check。
2. 请求日志。
3. 错误日志。
4. 基础构建和部署记录。

## 2. Growth

1. RED 指标：Rate、Errors、Duration。
2. 资源指标：CPU、Memory、Disk、Network。
3. 数据库指标：连接数、慢查询、锁等待。
4. 缓存指标：命中率、内存、淘汰。
5. 队列指标：积压、延迟、重试、死信。
6. Web 指标：LCP、TTFB、CLS、下载转化。

## 3. Scale / Enterprise

1. 分布式 trace。
2. SLO 与 error budget。
3. 多服务依赖图。
4. 业务指标和技术指标关联。
5. 容量趋势 / capacity trend。
6. 成本和资源效率。

## 4. Evidence Gate

观测与 SLO 证据必须写入：

```text
docs/qa/performance-evidence.json
```

并由以下命令校验：

```bash
npm run check:performance
```

完成状态必须包含真实 dataSource、dashboard、alerts、runbook 和 red-blue review。没有这些证据时，只能标记为 `in-progress` 或 `blocked`。
