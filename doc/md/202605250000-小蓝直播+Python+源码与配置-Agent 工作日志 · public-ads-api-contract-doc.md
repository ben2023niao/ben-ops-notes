---
id: "doc-083d9d759e67"
title: "Agent 工作日志 · public-ads-api-contract-doc"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-public-ads-api-contract-doc.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-public-ads-api-contract-doc.md"
sourceSha256: "80bb67c32c00fa52442de9f85001e1b69824e92c028091c83f9aac68ec748f9e"
sourceSystem: "project-doc"
---

# Agent 工作日志 · public-ads-api-contract-doc

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605250000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20public-ads-api-contract-doc.md)

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：Codex
任务：先行明确 public 广告 API 文档契约

## 输入资料

- PRD：`docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-h5.md`、`docs/prd/modules/kickoff-admin.md`
- 需求 ID：HOME-008、H5-019、H5-020、H5-021、H5-021b、ADM-913
- 设计图：用户提供 H5 原型 `2026.05.23迭代版.html#h5`
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`AGENTS.md`
- ADR：`docs/decisions/ADR-0014-ads-slot-creative-split.md`

## 本次目标

1. 先文档化 public 广告读取 API，不写实现代码。
2. 明确 H5 / Web 首页广告数据从后台「广告管理」到前台展示的流向。
3. 固定 `slot_code`、响应字段、空态、时间窗和兼容策略。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `docs/decisions/ADR-0014-ads-slot-creative-split.md` | 增加 public 广告接口、返回规则、slot_code 标准表 |
| `docs/prd/modules/kickoff-home.md` | 首页广告位改为 `ad_slots/ad_creatives`，补 `home_middle` public API |
| `docs/prd/modules/kickoff-h5.md` | H5 广告位数据源改为按 `slot_code` 拉 public 广告接口 |
| `docs/prd/modules/kickoff-admin.md` | ADM-913 改为 H5/Web 多广告位统一管理 |
| `docs/api/openapi.yaml` | 新增 public ads 两个接口和响应 schema |
| `packages/contracts/openapi/v1.yaml` | 同步 OpenAPI contract |

## 核心决策

1. 新增通用 public 读取接口：`GET /api/v1/ads/slots`、`GET /api/v1/ads/slots/{slot_code}/creatives`。
2. 旧 `GET /api/v1/home/banner`、`GET /api/v1/config/h5-ads` 保留兼容，不作为新页面首选接口。
3. slot 不存在、关闭或无生效内容时返回 200 + 空列表，前端按不渲染处理。
4. public 响应只暴露展示必要字段，不暴露后台审计和内部字段。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | HOME-008、H5-019、H5-020、H5-021、H5-021b、ADM-913 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-home.md`、`docs/prd/modules/kickoff-h5.md`、`docs/prd/modules/kickoff-admin.md` |
| OpenAPI / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` |
| 不涉及代码原因 | 用户要求先写文档再写代码，本次只落文档和契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 数据表设计 | 沿用 ADR-0014 的 `ad_slots/ad_creatives`，本次不新增表 |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否影响账本、事务、幂等或审计 | 否，public 读接口不涉及资金写入 |
| 规范例外与原因 | 无 |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 风险与待办

1. 下一步需要按契约实现 public handler/service/repository 读取逻辑。
2. 需要补 seed 或迁移，确保 `h5_home_hero`、`h5_home_live_feed` 等标准 slot 存在。
3. H5 首页要接入 `h5_home_hero`，广告为空时回退赛事 Hero。
