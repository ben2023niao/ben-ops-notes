---
id: "doc-e91b7bc2f539"
title: "Agent 工作日志 · danmaku-ratelimit-ci-flake"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "Redis", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-danmaku-ratelimit-ci-flake.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-danmaku-ratelimit-ci-flake.md"
sourceSha256: "302a0be282b57946a60008093ca8aa9d7331278c60c35e31f589a2b7c6da6bc8"
sourceSystem: "project-doc"
---

# Agent 工作日志 · danmaku-ratelimit-ci-flake

> 来源文件：`~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-danmaku-ratelimit-ci-flake.md`

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

日期：2026-06-11
Agent：Codex
任务：修复 main Pipeline #538 弹幕限流测试偶发失败

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`
- 需求 ID：LIVE-005
- CI 证据：GitLab Pipeline #538，`go test -race -count=1 -timeout 5m ./...`
- 失败测试：`kickoff/go-app/internal/service/live.TestSendDanmaku_RateLimit_PerUserPerRoom`

## 本次目标

1. 定位 main 分支 CI 失败根因。
2. 修复弹幕限流测试的时间边界不确定性。
3. 使用与 CI 相同的 race 测试命令验证。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/live/service.go` | 为弹幕限流秒级窗口增加可测试时钟，线上默认 `time.Now` |
| `services/go-app/internal/service/live/danmaku_ratelimit_test.go` | 固定测试时钟，并明确同用户同房间、同用户不同房间、不同用户同房间的断言 |

## 核心决策

1. 根因是测试依赖 `time.Now().Unix()` 的真实秒边界；CI 执行跨秒时 Redis key 改变，导致第 4 次发送未命中同一窗口。
2. 保留线上固定窗口限流行为，仅给 service 增加包内测试可注入的 clock。
3. 不改接口、不改数据表、不改前端字段。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响接口契约 | 否 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 是否涉及前端字段变更 | 否 |
| 是否影响密钥或运行时配置 | 否 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `cd services/go-app && go test -race -count=1 -timeout 5m ./...` | 通过 |

## 风险与待办

1. 本次只修复 CI 偶发失败，不调整弹幕限流产品口径。
2. 若后续要从固定窗口升级滑动窗口，应单独评估 Redis key、TTL 和压测指标。
