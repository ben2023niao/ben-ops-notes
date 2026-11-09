---
id: "doc-1414fac31dca"
title: "Agent 工作日志：恢复 systemconfigs 默认值（v0.3 真实 PRD 口径）"
date: "2026-05-24T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Go", "Docker", "MySQL", "自动化", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-restore-system-configs-defaults.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-24-restore-system-configs-defaults.md"
sourceSha256: "4cb8d01755c1b56f04c8e363c7bfee615208ca437a4def948f48e55eb1034134"
sourceSystem: "project-doc"
---

# Agent 工作日志：恢复 systemconfigs 默认值（v0.3 真实 PRD 口径）

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605240000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BGo%2BDocker-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%EF%BC%9A%E6%81%A2%E5%A4%8D%20systemconfigs%20%E9%BB%98%E8%AE%A4%E5%80%BC%EF%BC%88v0.3%20%E7%9C%9F%E5%AE%9E%20PRD%20%E5%8F%A3%E5%BE%84%EF%BC%89.md)

> 整理日期：2026-05-24 00:00｜日期依据：文件名日期

日期：2026-05-24
Agent：claude-code
任务：用户反馈上一轮"删 seed 占位数据"做过头了 — system_configs 是后台运营需要管理的真配置项，不该清空；应当给 v0.3 真实默认值打底，admin 上线时再调整。

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（按 `project.config.json` exceptions[apps.admin].exceptionReason 与 `docs/prd/modules/admin.md` 同义）、`docs/prd/modules/kickoff-wallet.md`
- 需求 ID：后台-系统配置；WALLET-* 资金参数；PRED-* 押注上下限
- 后端配置事实源：`services/go-app/config/config.local.yaml` `biz.*` 节
- 接口契约：`docs/api/openapi.yaml` AdminSystemConfigItem；`docs/api/admin-api.md` 后台 API 总览；`packages/contracts/openapi/v1.yaml` 同源镜像
- 后端归属：services/go-app（apiOwnerService）；权限 super_admin only on PUT；写操作走 audit
- 用户原话："我们结合前端api ，是需要有配置的啊，你可以默认一下，但是你不能删掉"

## 本次目标

1. 在 `scripts/seed/seed.sql` 中恢复 `system_configs` 默认值，但用 v0.3 真实 PRD 口径（不是之前那种假 `@kickoff_support` / `[邮箱已脱敏]`）
2. 默认值与 `config.local.yaml biz.*` 对齐 — 即业务侧实际跑的值
3. 真实截图证明 admin /system/config 现在展示 17 行真默认

## 默认值口径来源

| Key | 默认 | 出处 |
| --- | --- | --- |
| wallet.recharge.min_amount_rmb | 10 | config.local.yaml biz.recharge.min_amount |
| wallet.recharge.max_amount_rmb | 50000 | config.local.yaml biz.recharge.max_amount |
| wallet.recharge.platform_fee_rate | 0.05 | ADR-0011 §v0.3 / commit d06e089 |
| wallet.withdraw.min_amount_rmb | 10 | config.local.yaml biz.withdraw.min_amount |
| wallet.withdraw.max_amount_rmb | 50000 | config.local.yaml biz.withdraw.max_amount |
| wallet.withdraw.daily_limit_rmb | 200000 | config.local.yaml biz.withdraw.daily_limit |
| wallet.withdraw.platform_fee_rate | 0.05 | ADR-0011 §v0.3 |
| wallet.adjust.max_rmb | 10000 | config.local.yaml biz.adjust.max_rmb |
| predict.bet.min_diamond | 100 | config.local.yaml biz.predict.min_bet_diamond |
| predict.bet.max_diamond | 50000 | config.local.yaml biz.predict.max_bet_diamond |
| live.max_concurrent_rooms | 50 | 工程经验默认（单机 v1）；ADR-0012 拆分触发条件 ≥10k 远超此值 |
| live.danmaku_cooldown_ms | 3000 | 防刷弹幕基线；可在线 admin 调整 |
| home.banner_count | 5 | 首页 banner 轮播上限（PRD home v0.3） |
| home.support_telegram | （空） | 运营上线时填写 |
| home.support_email | （空） | 运营上线时填写 |
| security.bcrypt_cost | 12（敏感） | auth service 同步；前端脱敏 *** 显示 |
| security.idempotency_ttl_seconds | 86400 | 幂等键 24h TTL（与 middleware 同步） |

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `scripts/seed/seed.sql` | 新增 17 条 system_configs INSERT IGNORE；文件头说明从"2 类种子"改回"3 类种子"（admins / level_configs / system_configs） |
| `docs/qa/screenshots/current/admin-system-config-1440x900.png` | CDP 真实登录后 /system/config 截图，17 行真默认渲染完整 |
| MySQL 运行时 | 重跑 seed.sql 把默认值同步进 docker 库 |

## 核心决策

1. **默认值 = YAML 镜像而非"留空给运营填"**：admin /system/config 是观察 + 微调入口，初始空白会让运营误以为系统没在跑；用 YAML 真实值打底，运营调整后写库覆盖
2. **support_telegram / support_email 留空**：这两项是公司联络方式，没有"业务默认"；description 明确写"admin 上线时填写"
3. **security.bcrypt_cost 标 sensitive**：is_sensitive=1，前端读取脱敏为 ***，禁止前端修改（必须运维流程 + 重启服务）
4. **未读取的配置依然保留**：业务侧（recharge/withdraw/predict service）当前仍读 YAML，未从 system_configs 动态读；本表是"未来动态化预留 + admin 可视化"，是有意识的双轨而非垃圾数据
5. **不混用 banner / streamer / 比赛业务数据回滚**：那些是运营录入的"业务数据"而非"系统配置"，保留前次决策清空状态

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | (1) curl admin Bearer 实测：17 items 全部返回，敏感字段 `***` 正确脱敏；(2) CDP 真实登录截图：表格渲染完整、列名 / 默认值 / 分类 / 说明全部到位，security.bcrypt_cost 修改按钮置灰；(3) 默认值与 config.local.yaml biz.* 字段逐项核对一致 |
| 红队质疑 | (1) 默认值与代码实际读取的 YAML 双轨，admin 改了 DB 业务侧不生效会不会混淆？→ 蓝队答：description 列明示"运行时默认"；service 层何时从 DB 读取走未来 ADR，目前是观察口径而非运行口径；(2) bcrypt_cost 标 sensitive 但其实不算密码 / token，是否过度脱敏？→ cost 值泄露会让授权安全测试者预估 hash 计算成本调整离线爆破策略，属敏感参数；(3) 默认 17 项是否有遗漏？→ 当前已覆盖 wallet / withdraw / predict / live / home / security 六大类核心；后续业务真要某项动态化时再补 |
| 合入判断 | 允许合入 |

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented + verified（CDP 真实登录截图 + curl API 双重证据） |
| Project Decision | pending-review |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | 后台-系统配置（无独立 ID）；与 WALLET-* / PRED-* / LIVE-* 资金/竞猜/直播默认值相关 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`、`docs/prd/modules/kickoff-wallet.md` |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml` AdminSystemConfigItem schema 未变 |
| 验收证据行 | `docs/qa/project-acceptance.md` kickoff-admin（自动化测试列加入 CDP 实拍截图） |
| 不涉及契约的原因 | 仅数据回填，无 schema / 接口变化 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | SQL idempotent（INSERT IGNORE） |
| 数据表设计 | 不涉及表结构 |
| 是否影响账本、事务、幂等或审计 | 否；run-time admin 改这些值时仍走 admin.system.config_update audit |
| 规范例外与原因 | 无 |
| UI 验收模式 | no-design-mvp |
| 目标视口 / 设计尺寸 | 1440x900（桌面） |

## 后端归属

| 项目 | 内容 |
| --- | --- |
| Admin API ownerService | `services/go-app` |
| 权限模型 | adminBearer JWT + role；PUT /system/config/:key 需 super_admin |
| 审计（audit） | `admin.system.config_update` 事件（修改值 before/after 入库；敏感项前后值脱敏 ***） |

## 验证记录

### API 实测

```
GET /api/v1/admin/system/config
→ items: 17 (general=5 / wallet=8 / predict=2 / live=2)
→ security.bcrypt_cost value = "***" (is_sensitive=true, 脱敏正确)
```

### 页面截图（真实手机视口 + 桌面视口）

| 视口 | 文件 | 说明 |
| --- | --- | --- |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-system-config-1440x900.png` | CDP 真实登录后渲染；17 行真默认全部展示，sensitive bcrypt_cost 显示 *** 且修改按钮置灰 |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-users-empty-1440x900.png` | 前次截图，用户管理列名正确为"用户名" |
| 1440x900（桌面） | `docs/qa/screenshots/current/admin-login-1440x900.png` | 前次截图 |
| 375x812（真实手机视口） | `docs/qa/screenshots/current/admin-login-375x812.png` | 前次截图 |

证据清单：`docs/qa/ui-visual-evidence.json` 当前 pages: []；本日志记录的页面截图作为 v0.3 admin 端核心页面 smoke 证据。

### 响应式（responsive） / SEO异常验证

admin 后台桌面优先，移动 fallback 由 Element Plus 自动 stack；不涉及 SEO异常验证（内部系统）。

### 构建与门禁

- `pnpm --filter @kickoff/admin build`：通过（vue-tsc 严格模式 — 复用上次 build，本轮仅改 SQL）
- `make framework-check`：17/17 全绿

## 后续动作

1. v1.1 把 wallet recharge / withdraw 的 min/max/fee_rate 真接到 system_configs（service 层启动时 + admin 改时 hot reload），届时 DB 成为"运行口径"，YAML 仅作 fallback
2. 真实 support_telegram / support_email 由运营在 admin 后台填入，无需再改 seed
3. 团队成员 `make seed` 重跑即可同步
