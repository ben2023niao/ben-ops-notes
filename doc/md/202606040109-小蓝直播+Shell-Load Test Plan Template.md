---
id: "doc-44f14fe291e8"
title: "Load Test Plan Template"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/templates/load-test-plan-template.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/templates/load-test-plan-template.md"
sourceSha256: "e27823ad32e49765a57999406805cbb9adee1a3c4641e5bafe373dbd36ceeb3c"
sourceSystem: "project-doc"
---

# Load Test Plan Template

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell-Load%20Test%20Plan%20Template.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

压测不是上线后的补救动作。进入 `growth` 及以上规模轨道，关键接口和关键页面必须有压测计划。

## Scope

- 服务 / 页面：
- API / Route：
- 测试环境：
- 测试数据：
- 不压测范围：

## Traffic Model

| 场景 | QPS / 并发 | 持续时间 | 通过标准 |
| --- | --- | --- | --- |
| baseline |  |  |  |
| peak |  |  |  |
| spike |  |  |  |
| soak |  |  |  |

## Metrics

1. P50 / P95 / P99 latency。
2. error rate。
3. CPU / memory。
4. DB connection / slow query。
5. cache hit rate。
6. queue lag。
7. Web LCP / TTFB，如涉及 Web。

## Red Blue Review

| 角色 | 结论 |
| --- | --- |
| 蓝队压测结论 |  |
| 红队质疑 |  |
| 是否允许上线 |  |

## Executable Evidence

压测结果必须写入：

```text
docs/qa/performance-evidence.json
```

并通过：

```bash
npm run check:performance
```

该门禁会读取压测报告文件，校验 QPS、P95、P99、error rate、queue lag 等阈值。模板文档不能替代真实压测报告。
