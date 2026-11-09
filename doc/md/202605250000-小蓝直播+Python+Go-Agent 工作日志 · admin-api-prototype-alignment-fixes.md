---
id: "doc-3a12b86adb70"
title: "Agent 工作日志 · admin-api-prototype-alignment-fixes"
date: "2026-05-25T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "监控告警", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-api-prototype-alignment-fixes.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-25-admin-api-prototype-alignment-fixes.md"
sourceSha256: "e8aabcf92d7a3eff88ec1dbad20028e736ae5ce6efbc9280e08a569381628c42"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-api-prototype-alignment-fixes

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605250000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-api-prototype-alignment-fixes.md)

> 整理日期：2026-05-25 00:00｜日期依据：文件名日期

日期：2026-05-25
Agent：Codex
任务：后台功能、前台 API、原型字段对齐修复

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-301、ADM-302、ADM-406、ADM-907
- 设计图：用户提供 H5 原型本地文件与后台截图
- 设计图文件名：`2026.05.23迭代版.html#h5`
- 视觉要点：后台菜单、赛事/比分、主播、直播间、订单、风控/对账/审核模块字段需要和原型字段闭环
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`apps/admin/src/api/index.ts`
- 团队可读文档：`AGENTS.md`
- AI/工具控制文件：`.ai-framework/AGENTS.md`
- 项目 Overlay：Kickoff go-gin-app / mvp
- 其他：当前分支 `dev`

## 本次目标

1. 修复用户调账前端、后端 DTO、OpenAPI 契约不一致。
2. 补齐用户、主播、直播间列表字段，使后台 API 返回值能承载原型列表数据。
3. 给风控、对账、内容审核补后台入口和 API wrapper，避免契约有模块但后台无入口。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/internal/dto/admin_modules.go` | 扩展用户、房间、主播 DTO；调账请求改为 canonical 字段并兼容旧字段 |
| `services/go-app/internal/service/admin/user.go` | 调账请求归一化；用户列表补 `user_no` |
| `services/go-app/internal/service/admin/user_test.go` | 增加调账请求 canonical、旧数字、signed delta 覆盖 |
| `services/go-app/internal/service/admin/streamer.go` | 主播列表补关联房间、今日时长、等级、联系方式、GMV 字段 |
| `services/go-app/internal/service/admin/room.go` | 房间列表/详情补主播名、赛事名、管理员数、推流码状态 |
| `apps/admin/src/api/index.ts` | 前端 API 类型补齐调账、房间、主播、风控、对账、审核 |
| `apps/admin/src/views/users/UserListView.vue` | 调账弹窗改用 `rmb/diamond` 与 `add/subtract` |
| `apps/admin/src/views/streamers/StreamerListView.vue` | 表格补原型所需主播字段 |
| `apps/admin/src/views/rooms/RoomListView.vue` | 表格补原型所需直播间字段 |
| `apps/admin/src/views/risk/RiskListView.vue` | 新增风控告警入口 |
| `apps/admin/src/views/recon/ReconView.vue` | 新增对账中心入口 |
| `apps/admin/src/views/moderation/ModerationView.vue` | 新增内容审核入口 |
| `apps/admin/src/router/index.ts` | 新增风控、对账、审核路由 |
| `apps/admin/src/layouts/AdminLayout.vue` | 新增风控、对账、审核菜单 |
| `docs/api/openapi.yaml` | 更新调账、主播、房间字段契约 |
| `packages/contracts/openapi/v1.yaml` | 同步 OpenAPI contract |

## 核心决策

1. 调账接口以 `currency + direction + amount` 为新契约，同时服务端兼容旧数字枚举和旧 `delta`，降低前端灰度风险。
2. 主播、直播间字段只做读侧 enrichment，不引入新表或 migration，避免扩大数据模型影响面。
3. 风控/对账/审核前端接入现有 placeholder API；P1 表未落地前页面为空态数据，但路由、权限、契约路径已闭环。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-301、ADM-302、ADM-406、ADM-907 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/admin_modules.go` |
| 验收证据行 | 本日志验证记录 |
| 不涉及契约的原因 | 涉及契约，已更新 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 不新增表，不涉及 migration |
| 是否影响数据表 / migration / 索引 | 否 |
| 是否使用表设计模板 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 影响调账请求解析；资金写入仍走原有 ledger + audit |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 架构能力门禁 | `docs/architecture/capability-gates.md` |
| 结构化证据 | 不涉及 |
| 是否只是 CRUD | 主要为后台契约/字段闭环 |
| 涉及能力 | 权限安全 / 数据一致性 |
| 当前 MVP 边界 | 风控、对账、审核后端 P1 表未启用，保持 placeholder |
| 高风险触发项 | 资金 / 权限 / 审核 |
| 能力门禁结论 | 允许进入 review |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 运维就绪 | `docs/operations/ops-readiness.md` |
| 部署 | 影响 admin 前端构建产物和 go-app 二进制 |
| 回滚 | 回滚本次代码变更即可；无 migration |
| 密钥 | 不涉及 |
| 备份恢复 | 不涉及 |
| 观测 | 不新增指标 |
| Runbook | 不涉及 |

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
| `go test ./services/go-app/internal/service/admin -run TestUserBalanceAdjustNormalizeRequest -count=1 -v` | 通过 |
| `go test ./services/go-app/internal/service/admin -count=1` | 通过 |
| `go test ./services/go-app/...` | 通过 |
| `pnpm --filter @kickoff/admin build` | 通过，只有 Rollup pure annotation 和 chunk size warning |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| 对应设计图 | 用户提供本地 H5 原型和后台截图 |
| 页面截图 | 未生成截图，已完成生产构建验证 |
| UI 视觉证据 manifest | 未更新 |
| 真实手机视口 | 不适用，后台管理端 |
| 桌面/平板视口 | admin 构建通过 |
| 响应式验收 | 未跑浏览器截图 |
| 公共组件拆分 | 沿用现有 Element Plus / page-card / toolbar |
| API 接口路径 | `/users/:id/balance-adjust`、`/streamers`、`/rooms`、`/risk/*`、`/recon/*`、`/moderation/*` |
| mock/fallback 状态与原因 | 风控/对账/审核后端为 P1 placeholder |
| 后台权限与审计 | 菜单沿用 `isRisk` / `isFinance`；调账仍走原 audit |
| 根节点是否挂载 | 路由已挂载 |
| 静态资源是否 200 | 未启 dev server；构建产物生成成功 |
| console 是否无 error | 未跑浏览器 |
| 与设计图主要偏差 | 风控/对账/审核因后端表未启用，当前为空列表 |
| 合入判断 | 待 review |

## 风险与待办

1. 风控、对账、审核模块后端仍是 P1 placeholder，后续需要建表和 service 实现。
2. 订单列表的更多业务展示字段仍依赖后续订单 DTO 标准化。
3. 本次未做浏览器截图验收，建议后续联调环境跑 UI smoke。

## 交接说明

下一位 Agent 或工程师需要知道：

1. `AGENTS.md` 在本次开始前已是脏文件，本次未回退。
2. 本次不新增 migration。
3. 调账服务端兼容旧请求，但新前端和 OpenAPI 已使用 canonical 字段。
