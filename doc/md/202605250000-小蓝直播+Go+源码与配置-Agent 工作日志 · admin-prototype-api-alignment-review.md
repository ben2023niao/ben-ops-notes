---
id: "doc-8f5d067b0cbf"
title: "Agent 工作日志 · admin-prototype-api-alignment-review"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-prototype-api-alignment-review.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-prototype-api-alignment-review.md"
sourceSha256: "9d8c4f0dbb10da777552eb096366392bb9944f6f62338fa0ebae30c40403aeb8"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-prototype-api-alignment-review

> 来源文件：`~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-prototype-api-alignment-review.md`

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：Codex
任务：核对后台功能与 OpenAPI、原型数据字段的一致性

## 输入资料

- 原型：`/Users/qx/Downloads/2026.05.23迭代版.html`
- 截图：用户提供的后台「赛事 & 比分」页面
- 后台前端：`apps/admin/src/views/**`、`apps/admin/src/api/index.ts`
- API 契约：`docs/api/openapi.yaml`
- 后端路由 / DTO：`services/go-app/internal/http/router/admin.go`、`services/go-app/internal/dto/admin_modules.go`
- PRD：`docs/prd/modules/kickoff-admin.md`

## 结论

当前后台与 API、原型不能完全一一对上。赛事、球队、竞猜、直播间、订单、审计等主流程已有页面和后端接口；但仍存在字段契约错位、OpenAPI 与实现不一致、原型 P0 模块缺前端入口或后端仍为 placeholder 的问题。

## 主要发现

| 严重度 | 模块 | 问题 |
| --- | --- | --- |
| Critical | 用户调账 | 前端发送 `direction: 1/2`、`currency: 1/2`，后端 DTO 要求 `direction: add/subtract`、`currency: rmb/diamond`；OpenAPI 又写 `delta`，三者不一致 |
| Critical | 风控 / 对账 / 内容审核 | 原型和 OpenAPI 声明完整页面与接口，但当前前端没有入口，后端多数接口是 placeholder / empty list |
| High | 主播管理 | 原型列包含真实姓名、等级、关联房间、累计 GMV、联系方式、推流凭据/授权码；当前前端/API 只覆盖编号、昵称、状态、场次、累计打赏、创建时间 |
| High | 直播间管理 | PRD/OpenAPI 要列分配管理员、推流码状态、关联主播/比赛名称；当前列表 DTO 只有 `streamer_id`、`match_id`、状态、在线、创建时间 |
| High | 用户管理 | 前端类型/表格依赖 `user_no`，后端 DTO 没有该字段；原型要累计消费、最后登录、风控中/封禁，当前 API 更接近累计充值、ACTIVE/FROZEN |
| Medium | 竞猜活动 | 前端仍用旧字段 `title/category/close_at_ms/odds/winner_option_id`；后端兼容，但 OpenAPI 主契约是 `name/market_type/open_at/close_at/rate/result_option_key` |
| Medium | 订单中心 | 原型是一个订单中心三 tab；当前拆成三页可接受，但提现列表缺收款账号/风控评分，押注列表缺赛事/市场/潜在收益展示 |
| Medium | OpenAPI admin schemas | `AdminUser` schema 描述的是后台账号，不是前台用户管理项；多个 admin 列表响应没有专门 schema，容易继续漂移 |

## 已验证

- 已按 AGENTS 要求执行框架状态与 validator。
- 本次是审计核对，未修改业务代码。
