---
id: "doc-0e5f7e4d9c95"
title: "Agent 工作日志 · high-value-gift-config"
date: "2026-06-07T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-high-value-gift-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-07-high-value-gift-config.md"
sourceSha256: "0bc9562207745165ed25c16433309ec113f2847f0cf5e2311dbb36d936b2bb92"
sourceSystem: "project-doc"
---

# Agent 工作日志 · high-value-gift-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606070000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20high-value-gift-config.md)

> 整理日期：2026-06-07 00:00｜日期依据：文件名日期

日期：2026-06-07
Agent：Codex
任务：新增高价值礼物阈值系统配置

## 输入资料

- PRD：`docs/prd/modules/kickoff-live.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：LIVE-007、ADM-410
- 接口/契约：`GET /api/v1/config/system`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台系统配置新增“高价值礼物阈值”，运营可在基础配置里修改。
2. C 端公开系统配置接口返回该阈值，前端用礼物 `diamond_price > threshold` 判断是否高价值礼物。
3. 不修改 H5/Web 前端实现。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000047_seed_high_value_gift_config.up.sql` | seed `gift.high_value_threshold`，默认 25，分类 `general` |
| `services/go-app/migrations/000047_seed_high_value_gift_config.down.sql` | 回滚删除该配置 |
| `services/go-app/internal/service/admin/system.go` | 公开配置白名单与默认值新增礼物阈值 |
| `services/go-app/internal/dto/admin_modules.go` | `PublicSystemConfigResponse` 新增 `gift.high_value_threshold` |
| `services/go-app/internal/service/admin/system_public_test.go` | 覆盖默认值、覆盖值、空值回退 |
| `docs/api/openapi.yaml` | 更新公开系统配置契约 |
| `packages/contracts/openapi/v1.yaml` | 同步 contracts OpenAPI |

## 核心决策

1. 配置 key 使用 `gift.high_value_threshold`，避免“大礼物”口径，统一称为“高价值礼物”。
2. 配置分类使用 `general`，后台系统配置页显示在“基础”tab。
3. 公开接口返回结构为 `data.gift.high_value_threshold`，单位为钻石。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 仅新增 seed migration，不改表结构 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金写入 |
| 是否影响前端 | 不修改 `apps/web` / `apps/mobile` |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `go test ./internal/service/admin` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
