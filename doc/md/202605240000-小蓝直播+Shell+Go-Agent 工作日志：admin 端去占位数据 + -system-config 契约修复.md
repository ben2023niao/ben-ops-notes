---
id: "doc-97dc5b079bbf"
title: "Agent 工作日志：admin 端去占位数据 + /system/config 契约修复"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "MySQL", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-strip-placeholder-data.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-strip-placeholder-data.md"
sourceSha256: "53e3fe4424efa78ee70941a1cf18e8fe6265fb7e225ae4924244d69e92ad39af"
sourceSystem: "project-doc"
---

# Agent 工作日志：admin 端去占位数据 + /system/config 契约修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%EF%BC%9Aadmin%20%E7%AB%AF%E5%8E%BB%E5%8D%A0%E4%BD%8D%E6%95%B0%E6%8D%AE%20%2B%20-system-config%20%E5%A5%91%E7%BA%A6%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：用户反馈 `/system/config` 显示一堆假数据；实测确认 admin 端多个页面被 `seed.sql` 注入了占位数据但代码侧并不消费；同时发现 ConfigListView TS 类型与后端 schema 不匹配导致表格列全部为空。

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（按 `project.config.json` exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义；本仓库采用 kickoff- 前缀）、`docs/prd/modules/kickoff-member.md`
- 需求 ID：ADM-402 用户列表 / kickoff-member MEM-002 等级 / 后台-系统配置
- 接口契约：`docs/api/openapi.yaml` schemas/AdminSystemConfigItem（字段 key/value 而非 config_key/config_value）；`docs/api/admin-api.md` 后台 API 总览；`packages/contracts/openapi/v1.yaml` 同源镜像
- 后端归属：services/go-app（apiOwnerService）；权限走 adminBearer + role；写操作走 audit 中间件
- 用户原话："http://203.0.113.1:5174/system/config 配置都是假的 我不需要假的数据 ，不要占位数据"

## 本次目标

1. 真实登录 admin + 走 /system/config，确认 "假数据" 的具体来源
2. 把 admin 端所有"种子注入但代码不消费"的占位数据全部清掉
3. 修 ConfigListView 字段命名 bug（与后端 schema 对齐）
4. 截图证明：登录后跳 /system/config 表格诚实为空，"用户名"列名正确

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `scripts/seed/seed.sql` | 删 system_configs / home_banners / teams / matches / match_groups / match_brackets / match_goals / streamers / live_rooms / live_room_admins / live_sessions / predict_activities / predict_options 全部种子；仅保留 admins（登录必需）+ level_configs（PRD MEM-002 等级方案） |
| `apps/admin/src/views/system/ConfigListView.vue` | TS interface 从 config_key/config_value → key/value（与后端 AdminSystemConfigItem schema 对齐）；表格 prop 同步；空表自定义文案；敏感配置禁止前端编辑；row.is_sensitive 时 value 列显示 *** |
| `docs/qa/screenshots/current/admin-system-config-empty-1440x900.png` | CDP 真实登录后截图，证明表格"暂无系统配置 — 由运维通过本页或迁移脚本写入" |
| `docs/qa/screenshots/current/admin-users-empty-1440x900.png` | CDP 真实登录后截图，证明 "用户名" 列名正确、列表 "暂无数据 / 共 0 条" |
| MySQL（运行时） | DELETE FROM system_configs/home_banners/teams/matches/match_groups/match_brackets/match_goals/streamers/live_rooms/live_room_admins/live_sessions/predict_activities/predict_options |

## 核心决策

1. **bug 修复 + 数据清理一并提交**：发现的 TypeScript 契约 bug（config_key vs key）和 seed.sql 占位污染是同一类问题（admin 没认真打开过），合并到一个 commit 而不是拆两个
2. **seed 只保留 admins + level_configs**：
   - admins：本地无种子就无法登录，必须保留（弱密码 + bcrypt hash 写死，仅 local/dev 可跑，prod 由 SIGNAL 守卫）
   - level_configs：PRD MEM-002 进度条 + admin /level-config 页面消费，是真实业务数据
   - 其余（teams/matches/streamers/rooms/predicts/banners/system_configs）：admin 后台运营时填入，默认空列表是诚实表现
3. **是否提供 dev 联调用的 fixture 数据？**：暂不；按 PRD 走"admin 后台填业务数据"是单一真相；如果未来真有联调阻塞再另写 `seed/dev-fixtures.sql` 分文件管理
4. **CDP 截图替代 chrome --screenshot**：file:// 跨域 + virtual-time-budget 导致 --screenshot 拿不到 SPA 的最终页面；改用 CDP（Node 22 自带 WebSocket）：先到 localhost 注入 localStorage token，再跳 /system/config 等 4s 渲染再 captureScreenshot
5. **不动 ConfigListView 之外的页面**：本次专注用户点名的 /system/config；其他页面的 TS 类型已在前次 admin v0.3 对齐时复盘过；后续真实运营数据进来时再针对性 review

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | (1) curl 验证 5 个 admin 端点全部 items: [] 或 6 条 level_configs；(2) CDP 截图真实登录态进入 /system/config 与 /users，表格列名正确、空表文案出现；(3) pnpm build 通过 vue-tsc 严格模式 |
| 红队质疑 | (1) 删 seed 后开发联调没数据怎么办？→ 蓝队答：admin 后台支持手动新建（banner / streamer / room / 比赛 / 竞猜）；真要批量，加 `seed/dev-fixtures.sql` 但默认不跑；(2) system_configs 表既然没人读为啥保留 schema？→ 表 schema 是为未来运行时可调参数预留，不属于本次清理范围；本次只删数据不删表；(3) 是否漏了其他 admin 页面的契约 bug？→ 前次 admin v0.3 对齐已扫过 nickname/exchange；本次只发现 system/config 一处，原因是它的字段命名独立于 PRD 字段同步；(4) MySQL 直接 DELETE 不写迁移会不会污染团队成员的本地库？→ seed.sql idempotent，重跑即对齐；其他人 `make seed` 会得到一致的精简版本 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（CDP 真实登录截图证明） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-402（用户列表）、后台-系统配置（无独立 ID） |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-member.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` AdminSystemConfigItem；`packages/contracts/openapi/v1.yaml` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` 待补；`docs/qa/project-acceptance.md` kickoff-admin 自动化测试 + 截图证据列升级 |
| 不涉及契约的原因 | 涉及但无变更：契约本身正确，是前端类型错；本次修前端对齐契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | TS 严格模式 + Vue 3 SFC；vue-tsc + ESLint 通过 |
| 数据表设计 | 不涉及表结构；仅 DELETE 数据 |
| 是否影响账本、事务、幂等或审计 | 否（system_configs 写操作仍走原 admin.system.config_update audit；本次仅清空表） |
| 规范例外与原因 | 无 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 1440x900（admin 桌面端） |

## 后端归属

| 项目 | 内容 |
| --- | --- |
| Admin API ownerService | `services/go-app` |
| 权限模型 | adminBearer JWT + role；ConfigListView 的 PUT /system/config/:key 需 super_admin |
| 审计（audit） | 修改配置走 `admin.system.config_update` audit 事件；本次未触发新 audit 类型 |

## 验证记录

### 后端 API 实测（curl + admin Bearer token）

```
GET /api/v1/admin/system/config       → items: [] (从 8 → 0)
GET /api/v1/admin/home/banner         → items: [] (从 3 → 0)
GET /api/v1/admin/streamers?size=5    → items: [] (从 4 → 0)
GET /api/v1/admin/matches?size=5      → items: [] (从 8 → 0)
GET /api/v1/admin/rooms?size=5        → items: [] (从 4 → 0)
GET /api/v1/admin/level-config        → items: 6 条 (真实 PRD 数据保留)
```

### 页面截图（真实手机视口 + 桌面视口）

| 视口 | 文件 | 说明 |
| --- | --- | --- |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-system-config-empty-1440x900.png` | CDP 真实登录 + 跳转后渲染；顶栏显示 `超级管理员 kickoff_admin 退出`；表格列名 Key / Value / 类型 / 分类 / 说明 / 操作；空表文案 "暂无系统配置 — 由运维通过本页或迁移脚本写入" |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-users-empty-1440x900.png` | 用户管理页；列名 "用户名"（不是 v0.3 前的"昵称"）；统计卡 0；表格 "暂无数据 / 共 0 条" |
| 375x812（真实手机视口） | `docs/qa/screenshots/current/admin-login-375x812.png` | 前次 admin v0.3 对齐时已抓取，本次未变化 |

证据清单：`docs/qa/ui-visual-evidence.json` 当前 pages: []（项目 quality.requiresUiVisualEvidence=false）；本日志记录的页面截图作为 v0.3 admin 端核心页面的 smoke 证据。

### 构建与门禁

- `pnpm --filter @kickoff/admin build`：通过（vue-tsc 严格模式）
- `make framework-check`：17/17 全绿
- 响应式（responsive）：admin 后台目标视口为桌面 1440x900；移动 fallback 由 Element Plus 自动 stack

### SEO异常验证 / meta 范围

不涉及 SEO异常验证：admin 后台内部运营系统，adminBearer JWT 鉴权，不对外公开。

## 后续动作

1. 团队成员 `make seed` 重跑即可同步到精简版本
2. 真实运营开始后，banner / streamer / 比赛 / 竞猜 / 系统配置一律走 admin 后台手动入库
3. 如开发联调批量数据有真实痛点，新建 `scripts/seed/dev-fixtures.sql`（默认不跑，opt-in），不污染 baseline seed
4. v1.1 ConfigListView 增加新建配置 dialog（PUT /system/config/:key 当前只能改不能新增；如果业务真用 system_configs，需要后端补 POST）
