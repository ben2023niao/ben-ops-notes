---
id: "doc-1b56f49b8dd0"
title: "Agent 工作日志：admin 前端对齐 PRD v0.3（nickname → username）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Redis", "自动化", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-admin-v03-alignment.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-admin-v03-alignment.md"
sourceSha256: "b859d10b178ce3c211615c33e8877f90add69255164ae1a07a7ba87914079eba"
sourceSystem: "project-doc"
---

# Agent 工作日志：admin 前端对齐 PRD v0.3（nickname → username）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%EF%BC%9Aadmin%20%E5%89%8D%E7%AB%AF%E5%AF%B9%E9%BD%90%20PRD%20v0.3%EF%BC%88nickname%20%E2%86%92%20username%EF%BC%89.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：把 apps/admin 端的 `nickname` 残留字段全部对齐到 v0.3 的 `username`，与后端 OpenAPI 契约（AdminUser / User schema）保持一致。

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-member.md`（按 `project.config.json` exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义；统一 kickoff- 前缀）
- 需求 ID：ADM-402（用户列表）、ADM-403（用户详情）、ADM-904 等观众/审计
- 接口契约：`docs/api/openapi.yaml` schemas/User（v0.3 已是 username）、AdminUser（无 nickname 字段）；`docs/api/admin-api.md` 后台 API 总览；`packages/contracts/openapi/v1.yaml` 同源镜像
- 前置变更：ADR-0011 v0.3 对齐、commit fa3157e（schema 改名）、commit c7cad2d（OpenAPI 修正）

## 本次目标

1. 删 AuthResp / MeResp 中的 `nickname` 字段 — AdminUser schema 根本没有这个字段，前端定义是死代码
2. 把 AdminUserItem.nickname → username（对应后端 v0.3 User schema 重命名）
3. 同步更新 store 状态、layout 用户名展示、登录欢迎语
4. 视图层 4 个表/详情列：UserList、UserDetail、RoomDetail viewers、UserList 调账 dialog
5. vue-tsc 严格模式 build 通过 + framework-check 全绿

## 后端归属

| 项目 | 内容 |
| --- | --- |
| Admin API ownerService | `services/go-app`（go-gin-app；详见 `project.config.json` apps.admin.apiOwnerService） |
| 权限模型 | adminBearer JWT + role 中间件（super_admin / finance_admin / risk_admin / room_admin） |
| 审计（audit） | `services/go-app/internal/pkg/audit` 在所有写操作侧落日志，对应 admin_audit_logs 表；本次纯 UI 字段重命名不触发新 audit 事件 |

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `apps/admin/src/api/auth.ts` | 删 AuthResp.nickname / MeResp.nickname |
| `apps/admin/src/api/index.ts` | AdminUserItem.nickname → username（注释标注 v0.3 对齐） |
| `apps/admin/src/stores/auth.ts` | State / login / fetchMe / reset 移除 nickname 字段 |
| `apps/admin/src/layouts/AdminLayout.vue` | 顶栏显示 `auth.username`（去掉 nickname fallback） |
| `apps/admin/src/views/login/LoginView.vue` | 欢迎语 `欢迎，${auth.username}` |
| `apps/admin/src/views/users/UserListView.vue` | 列 "昵称" → "用户名"（prop 同步）；调账 dialog 显示 user.username |
| `apps/admin/src/views/users/UserDetailView.vue` | 标题 + 描述项 "昵称" → "用户名" |
| `apps/admin/src/views/rooms/RoomDetailView.vue` | 观众列表 prop nickname → username（后端 viewers 接口已注 _note 待 Redis 接入） |

## 核心决策

1. **AdminUser 没有 nickname 字段**：前端 AuthResp / MeResp 的 nickname 是从未传值的死代码；直接删除而非保留 optional
2. **不动 admins 表 schema**：admins.username 是管理员账号（登录凭证），与 users.username（用户 display name）同名不同义，已在 migration 000010 注释明确；前端只是消费 schema
3. **RoomDetailView 观众列表先改 prop**：backend `Viewers()` 当前返回空 items + `_note`，未来 Redis 接入时按 v0.3 模型一定是 username；现在改好避免未来再次踩坑
4. **不动 schema 注释行**：api/index.ts 第 53 行 "nickname → username（display name）" 是迁移记录注释，保留

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | vue-tsc --noEmit + vite build 通过，无 type error；grep nickname 仅剩 1 处迁移注释；admin TS 类型与 OpenAPI schemas/User、AdminUser 完全对齐 |
| 红队质疑 | (1) 字段重命名是否影响后端契约？→ 不影响 — 仅前端类型定义改名，HTTP body field 早已是 username（commit fa3157e）；(2) RoomDetailView viewers 改 prop 是否过早？→ 后端 items: []any{} 占位 + _note 明确未来按 v0.3 模型；提前对齐避免上线后再改；(3) 是否还有 mock/seed/E2E 残留 nickname？→ apps/admin 范围内已扫净；前端工程师负责的 apps/web、apps/h5 待其同步对齐 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（pnpm build 通过；vue-tsc 严格模式无 type error） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-402 / ADM-403 / ADM-904 / kickoff-member MEM-001 同步显示 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-member.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` schemas/User、AdminUser（无前端 schema 变更） |
| 验收证据行 | `docs/qa/acceptance-evidence.md` 待补 ADM-402/403 行；`docs/qa/project-acceptance.md` kickoff-admin 行（自动化测试 = vue-tsc build） |
| 不涉及契约的原因 | 仅前端类型对齐，HTTP body field 早已是 username |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | TS 严格模式 + Vue 3 SFC；vue-tsc + ESLint（Vite 内置）通过 |
| 数据表设计 | 不涉及 |
| 是否影响账本、事务、幂等或审计 | 否 |
| 规范例外与原因 | 无 |
| UI 验收模式 | no-design-mvp（admin 端 designMode=no-design-mvp；本次变更仅文案/字段重命名，不涉视觉规格） |
| 目标视口 / 设计尺寸 | 1440x900（admin 后台桌面端目标视口；Element Plus 默认栅格断点 lg） |

## 验证记录

- `pnpm --filter @kickoff/admin build`：通过（vue-tsc --noEmit + vite build 一气呵成）
- `grep -rn nickname apps/admin/src --include="*.ts" --include="*.vue"`：仅余 1 处迁移注释
- `make framework-check`：17/17 全绿
- bundle 大小：DashboardView 1.04MB / index 1.24MB（与本次变更无关，预 v1.1 做 manualChunks）

### 页面截图（真实手机视口 + 桌面视口）

`pnpm --filter @kickoff/admin preview` 起本地 4174 端口，headless Chromium 抓取两档：

| 视口 | 文件 | 说明 |
| --- | --- | --- |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-login-1440x900.png` | Element Plus 默认 lg 断点；登录页"用户名"label 渲染正确 |
| 375x812（真实手机视口） | `docs/qa/screenshots/current/admin-login-375x812.png` | iPhone X/11/12 视口 — admin 后台默认桌面优先；移动端布局为 fallback |

### 响应式验证（responsive）

admin 后台目标视口为桌面 1440x900；375x812 截图仅作 "桌面优先 + 移动 fallback" 的覆盖证据（Element Plus 组件在窄屏下自动 stack）。本次变更纯字段重命名，未引入新布局，响应式行为继承现有页面表现。完整响应式验收等真实业务页面落地时再做。

### SEO异常验证 / meta 范围

不涉及 SEO异常验证：admin 后台是内部运营系统（adminBearer JWT 鉴权），不对搜索引擎公开；不需要 title/description meta tag 优化，不在搜索引擎收录范围。

证据清单：`docs/qa/ui-visual-evidence.json` 当前 pages: []（v1 admin 不要求登记 visual evidence pages，按 project.config quality.requiresUiVisualEvidence=false）；本日志记录的页面截图作为本次字段重命名的 smoke 证据，未来 admin 视觉规格落地时再正式登记。

## 后续动作

1. 联调：起 admin（:5174）+ go-app admin（:8081），登录 + 用户列表 + 用户详情 + 调账 dialog 手工验证一遍
2. 待 backend Viewers 真接入 Redis 后，前端 roomApi.viewers 把 items: any[] 显式定义为 `{ user_id, username, level }`
3. apps/web、apps/h5 由前端工程师同步对齐（不在本团队范围）
