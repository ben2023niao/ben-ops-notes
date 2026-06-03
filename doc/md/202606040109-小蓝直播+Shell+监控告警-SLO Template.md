---
id: "doc-90df96837c0e"
title: "SLO Template"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "监控告警", "自动化", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/templates/slo-template.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/templates/slo-template.md"
sourceSha256: "603f60b523e77ddfeaf587c03462622ba2625885c8fd1a87314813ba9e2cdb1a"
sourceSystem: "project-doc"
---

# SLO Template

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/templates/slo-template.md`

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

适用范围：`growth`、`scale`、`enterprise` 项目，或任何用户量、交易、通话、实时链路已经成为业务核心的系统。

## Service

- 服务名：
- Owner：
- 用户影响：
- Scale Profile：

## SLO

| 指标 | 目标 | 统计窗口 | 数据源 |
| --- | --- | --- | --- |
| Availability |  | 7d / 30d |  |
| P95 Latency |  | 7d / 30d |  |
| P99 Latency |  | 7d / 30d |  |
| Error Rate |  | 7d / 30d |  |
| Saturation |  | 7d / 30d |  |

## Error Budget

- 月度错误预算：
- 消耗阈值：
- 冻结发布条件：
- 恢复条件：

## Alerting

| 告警 | 阈值 | 接收人 | Runbook |
| --- | --- | --- | --- |
|  |  |  |  |

## Executable Evidence

SLO 结果必须沉淀到：

```text
docs/qa/performance-evidence.json
```

并通过：

```bash
npm run check:performance
```

`growth`、`scale`、`enterprise` 项目不能只写 SLO 目标，必须提供数据源、统计窗口、实际值和红蓝对抗结论。
