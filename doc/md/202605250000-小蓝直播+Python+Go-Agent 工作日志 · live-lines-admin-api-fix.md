---
id: "doc-bf696d754b3e"
title: "Agent 工作日志 · live-lines-admin-api-fix"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-live-lines-admin-api-fix.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-live-lines-admin-api-fix.md"
sourceSha256: "1fa25d7c2c9fd3bff8e63f04da0012ddd6c8506f56f53e2f45dc51f67995bfb5"
sourceSystem: "project-doc"
---

# Agent 工作日志 · live-lines-admin-api-fix

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605250000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20live-lines-admin-api-fix.md)

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：siggod
任务：H5 原型直播间线路选择、后台管理与 OpenAPI 对齐

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：`ADM-912`、`ADM-913`、`ADM-914`、`LIVE-016`
- 设计图：`/Users/qx/Downloads/2026.05.23迭代版.html#h5`
- 接口/契约：`packages/contracts/openapi/v1.yaml`、`docs/api/openapi.yaml`
- AI/工具控制文件：`AGENTS.md`

## 本次目标

1. 补齐直播间“线路选择”的后台管理入口。
2. 补齐后台已有但 OpenAPI 缺失的直播线路、支付通道、上传、提现出款流水接口。
3. 生成发布用 `docs/api/openapi.yaml` 并验证。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/api/index.ts` | 增加 `liveLineApi` 与线路 DTO |
| `apps/admin/src/router/index.ts` | 增加 `/live-lines` 后台路由 |
| `apps/admin/src/layouts/AdminLayout.vue` | 增加「直播线路」菜单 |
| `apps/admin/src/views/live-lines/LiveLineListView.vue` | 新增直播线路 CRUD 页面 |
| `apps/web/app/apis/live.ts` | 播放 token 续期改为 POST |
| `services/go-app/internal/http/public/ads.go` | 新增统一公开广告读取 handler |
| `services/go-app/internal/http/router/public.go` | 注册统一广告读取接口 |
| `packages/contracts/openapi/v1.yaml` | 补齐本轮后台/前台接口契约 |
| `docs/api/openapi.yaml` | 由 `scripts/build-openapi-docs.py` 生成的发布契约 |
| `docs/api/h5-admin-public-api-mapping.md` | H5 页面、后台管理、前台 API 映射清单 |

## 核心决策

1. 前台不新增 `h5-*` 接口，统一使用 `/api/v1/...`。
2. 直播线路先把后台管理和 API 数据源做好，H5 播放切流可继续假数据过渡。
3. 旧 H5 广告专用入口暂不继续扩展，后续按统一广告位模型清理。

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 涉及提现出款契约补齐；未改资金逻辑 |
| OpenAPI | 已更新源文件并生成发布文件 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py` | 通过 |
| `python3 scripts/validate-prd.py` | 通过 |
| `python3 scripts/validate-engineering-standards.py` | 通过 |
| `python3 scripts/validate-capability-gates.py` | 通过 |
| `python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/http/public ./internal/http/router ./internal/repository/ads ./internal/service/admin` | 通过 |
| `npm run check:openapi` | 通过 |
| `python3 scripts/build-openapi-docs.py` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate packages/contracts/openapi/v1.yaml` | 通过 |
| `npx -y @apidevtools/swagger-cli@latest validate docs/api/openapi.yaml` | 通过 |
| `pnpm --filter @kickoff/admin build` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | H5 直播间线路选择 |
| API 接口路径 | `/api/v1/admin/live-lines`、`/api/v1/live/lines`、`/api/v1/live/lines/select` |
| mock/fallback 状态与原因 | H5 播放切流可先假数据；后台管理和公开读取接口已具备 |
| 后台权限与审计 | 复用现有 `requireAdmin` 和 service 审计 |
| 根节点是否挂载 | `/live-lines` 已挂到 admin router 和侧边栏 |
| 合入判断 | 待 reviewer / CI 裁决 |

## 风险与待办

1. 支付通道后台接口和契约已对齐，但 admin 菜单页仍待补。
2. 旧 H5 广告专用接口应在确认无调用后删除。
3. 继续按 H5 原型逐页核对钱包明细、个人中心、等级权益、直播互动。
