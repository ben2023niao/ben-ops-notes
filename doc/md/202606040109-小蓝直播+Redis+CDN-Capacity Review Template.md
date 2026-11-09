---
id: "doc-1ce45bde857f"
title: "Capacity Review Template"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Redis", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/templates/capacity-review-template.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/templates/capacity-review-template.md"
sourceSha256: "de679e6b01b8bb0194b17112b67fa4be47419a274ae9184250cd8367ef130931"
sourceSystem: "project-doc"
---

# Capacity Review Template

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BRedis%2BCDN-Capacity%20Review%20Template.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

容量评审用于回答“现在的架构还能撑多久，下一次瓶颈在哪里”。

## Current Capacity

| 资源 | 当前值 | 上限 | 风险 |
| --- | --- | --- | --- |
| API QPS |  |  |  |
| DB QPS |  |  |  |
| DB Storage |  |  |  |
| Redis Memory |  |  |  |
| Queue Lag |  |  |  |
| CDN / Bandwidth |  |  |  |

## Growth Forecast

- 当前 DAU / MAU：
- 3 个月增长预估：
- 6 个月增长预估：
- 成本上限：

## Expansion Plan

1. 水平扩容：
2. 数据扩展：
3. 缓存策略：
4. 队列策略：
5. 限流降级：
6. 回滚方案：
