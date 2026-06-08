---
id: "doc-961c0e1b9981"
title: "site-footer-config"
date: "2026-06-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-site-footer-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-site-footer-config.md"
sourceSha256: "82170cf967ee8ef446a4f82a9eeeaf648a9043f0f76fcc5a095dad7a77b422a7"
sourceSystem: "project-doc"
---

# site-footer-config

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-06-09-site-footer-config.md`

> 整理日期：2026-06-09 00:00｜日期依据：文件名日期

日期：2026-06-09
Agent：Codex
任务：后台基础配置新增 C 端页脚联系信息，并通过公开配置接口返回

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-h5.md`
- 需求 ID：ADM-006、H5-030
- 设计图：C 端页脚展示客服邮箱 / 商务合作 / 主域名；后台系统配置基础 tab
- 接口/契约：`GET /api/v1/config/system`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 后台系统配置基础 tab 增加商务合作邮箱和主域名配置；客服邮箱复用已有 `home.support_email`。
2. C 端公开配置接口新增 `site.support_email`、`site.business_email`、`site.primary_domain`。
3. 同步 OpenAPI / contracts / PRD，不修改 H5 前端代码。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/admin_modules.go` | `PublicSystemConfigResponse` 增加 `site` 节点 |
| `services/go-app/internal/service/admin/system.go` | 公开配置白名单增加页脚三项并组装返回 |
| `services/go-app/internal/service/admin/system_public_test.go` | 覆盖默认、覆盖、空值回退场景 |
| `services/go-app/migrations/000050_seed_site_footer_configs.*.sql` | 新增后台基础配置 seed / rollback |
| `docs/api/openapi.yaml` | 更新公开配置接口 schema |
| `packages/contracts/openapi/v1.yaml` | 同步契约 |
| `docs/prd/modules/kickoff-admin.md` | 新增 ADM-006 |
| `docs/prd/modules/kickoff-h5.md` | 新增 H5-030 |

## 核心决策

1. 配置键沿用 `home.*` 命名：`home.support_email`、`home.business_email`、`home.primary_domain`。
2. 公开接口用 `site` 节点承载页面级展示信息，不混入 `wallet` 或 `gift`。
3. `home.support_email` 同时服务客服入口和页脚，避免同一含义维护两份配置。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-006、H5-030 |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-h5.md` |
| OpenAPI / DTO | `PublicSystemConfig.site` |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 新增 system_configs seed migration；不改表结构 |
| 是否影响账本、事务、幂等或审计 | 不涉及资金账本；后台配置修改仍走已有审计 |
| 是否影响前端字段变更 | 是，公开接口新增 `data.site.*` 字段；未删除/改名旧字段 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行新 migration 后后台基础配置出现新项 |
| 回滚 | 执行 `000050_seed_site_footer_configs.down.sql` 删除新增配置项并恢复客服邮箱描述 |
| 密钥 | 不涉及 secret |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `python3 scripts/validate-prd.py` | 通过 |
| `go test ./internal/service/admin` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| API 接口路径 | `GET /api/v1/config/system` |
| 合入判断 | 后端/后台契约已补；H5 前端需读取 `data.site.*` 展示页脚 |

## 交接说明

1. 前端读取 `GET /api/v1/config/system` 的 `data.site.support_email`、`data.site.business_email`、`data.site.primary_domain`。
2. 后台在 `系统管理 / 系统配置 / 基础` 维护三项；客服邮箱沿用已有配置。
