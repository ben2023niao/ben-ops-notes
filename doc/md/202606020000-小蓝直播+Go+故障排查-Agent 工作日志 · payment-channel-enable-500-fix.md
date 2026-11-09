---
id: "doc-9179f5b00b19"
title: "Agent 工作日志 · payment-channel-enable-500-fix"
date: "2026-06-02T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-channel-enable-500-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-02-payment-channel-enable-500-fix.md"
sourceSha256: "cb84e7a26cdab8238606a0d20455d3356cb58fdb553880d7c6e59856dd63926a"
sourceSystem: "project-doc"
---

# Agent 工作日志 · payment-channel-enable-500-fix

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606020000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20payment-channel-enable-500-fix.md)

> 整理日期：2026-06-02 00:00｜日期依据：文件名日期

日期：2026-06-02
Agent：Codex
任务：修复后台支付通道首次启用 500

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-914
- 接口/契约：`PUT /api/v1/admin/payment-channels/{code}`
- 其他：用户在后台启用 `wechat` 时返回 HTTP 500，trace_id `212fecaa-7b24-4487-8bee-40270b9180e1`

## 本次目标

1. 复现后台支付通道启用 500。
2. 定位 `system_configs` 写入失败原因。
3. 修复首次写入配置 key 的 insert 字段。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/service/admin/payment_channels.go` | `system_configs` insert 去掉不存在的 `created_by` 字段，改写现有 `updated_by` |

## 核心决策

1. `system_configs` 表结构来自 migration `000007`，字段包含 `updated_by`，不包含 `created_by`。
2. 支付通道开关首次启用会创建 `wallet.recharge.channels.enabled` key，因此 insert 分支必须与表结构一致。
3. 不新增 migration；这是 service 写入字段错误，不是表缺字段。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-914 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | 未改契约 |
| 不涉及契约的原因 | 修复服务端持久化错误 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | `docs/architecture/database-design-standards.md` |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 后台写操作仍保留审计；修复审计前配置写入失败 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `curl -X PUT /api/v1/admin/payment-channels/wechat {"enabled":true}` | 修复前复现 HTTP 500 |
| `go test ./internal/service/admin ./internal/http/adminapi` | 通过 |

## 风险与待办

1. 部署后需复测同一 PUT 请求。
2. 成功后继续测 `GET /api/v1/wallet/channels` 是否返回 `wechat`。
