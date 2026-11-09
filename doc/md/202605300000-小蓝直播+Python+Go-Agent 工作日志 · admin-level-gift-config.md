---
id: "doc-7d8c8e89c2e0"
title: "Agent 工作日志 · admin-level-gift-config"
date: "2026-05-30T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Python", "Go", "MySQL", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-30-admin-level-gift-config.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-30-admin-level-gift-config.md"
sourceSha256: "f34d44613824fd8bd65939557da47906bcda26d7d6437b8b9912b0777402ed60"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-level-gift-config

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605300000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BPython%2BGo-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-level-gift-config.md)

> 整理日期：2026-05-30 00:00｜日期依据：文件名日期

日期：2026-05-30
Agent：Codex
任务：后台新增用户等级门槛配置与礼物列表管理，隐藏竞猜活动后台入口

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`（项目对应后台模块；框架通用检查口径：`docs/prd/modules/admin.md`）
- 需求 ID：ADM-409、ADM-410
- 设计图：不涉及
- 接口/契约：`docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`
- 团队可读文档：`docs/architecture/data-model.md`、`docs/architecture/funds-and-ledger.md`
- AI/工具控制文件：`AGENTS.md`
- 其他：用户明确“竞猜功能砍掉，后台先加用户等级配置和礼物列表管理”

## 本次目标

1. 后台新增用户等级门槛 CRUD，配置达到多少累计送出礼物钻石可升级。
2. 后台新增礼物目录 CRUD，配置 icon、钻石价格、1-5 特效枚举、启用状态和排序。
3. 不恢复任何等级特权；后台隐藏竞猜活动菜单入口。

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `services/go-app/migrations/000024_create_economy_config_tables.*.sql` | 新增 `user_level_configs`、`gift_catalog` 及默认数据 |
| `services/go-app/internal/model/economy.go` | 新增等级门槛、礼物目录模型 |
| `services/go-app/internal/repository/economy/repo.go` | 新增配置表 repository |
| `services/go-app/internal/service/admin/economy.go` | 新增 admin CRUD 服务，写操作审计 |
| `services/go-app/internal/http/adminapi/economy.go` | 新增 admin handler |
| `services/go-app/internal/http/router/admin.go` | 注册 admin API |
| `services/go-app/internal/service/admin/economy_test.go` | 覆盖创建、更新、删除、冲突、非法 code |
| `apps/admin/src/api/modules/economy.ts` | 新增后台 API client |
| `apps/admin/src/views/system/user-levels.vue` | 新增用户等级配置页面 |
| `apps/admin/src/views/system/gifts.vue` | 新增礼物管理页面 |
| `apps/admin/src/router/routes/modules/system.ts` | 新增系统菜单入口 |
| `apps/admin/src/router/routes/modules/contents.ts` | 移除竞猜活动菜单入口 |
| `apps/admin/src/locales/langs/*/economy.json` | 新增中英文文案 |
| `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml` | 新增 ADM-409/ADM-410 契约 |
| `docs/prd/modules/kickoff-admin.md` | 新增需求条目和审计要求 |
| `docs/architecture/data-model.md` | 新增数据模型说明 |
| `docs/architecture/funds-and-ledger.md` | 清理按等级押注上限旧口径 |

## 核心决策

1. 新增 `user_level_configs`，不复用历史 `level_configs` 的 privilege / limit / chat color 字段。
2. 等级只表示升级门槛，不影响 C 端权限、限额、颜色、进场、排序或投注。
3. 礼物 `effect_type` 先固定为 1-5 枚举，避免提前绑定具体动画实现。

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-409、ADM-410 |
| 需求总账 | `docs/prd/requirements.md` |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md`（后台模块；框架通用检查口径：`docs/prd/modules/admin.md`） |
| OpenAPI / Event / DTO | `docs/api/openapi.yaml`、`packages/contracts/openapi/v1.yaml`、`services/go-app/internal/dto/economy.go` |
| 验收证据行 | `docs/qa/acceptance-evidence.md` |
| 不涉及契约的原因 | 不适用，已更新契约 |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 代码规范 | `docs/quality/code-standards.md` |
| 数据表设计 | 新增 migration up/down，雪花 ID、软删除、创建/更新时间、索引齐全 |
| 是否影响数据表 / migration / 索引 | 是 |
| 是否影响账本、事务、幂等或审计 | 不直接改资金账本；admin 写操作调用 `audit.Log` |
| 规范例外与原因 | 无 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 是，运营后台配置 CRUD |
| 涉及能力 | 权限安全 / 迁移 |
| 当前 MVP 边界 | 只提供后台配置，不接 C 端送礼扣费和等级计算任务 |
| 高风险触发项 | 用户数据 / 权限 |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需要执行 migration `000024`；admin 前端需重新构建发布 |
| 回滚 | 执行 `000024_create_economy_config_tables.down.sql` 并回滚后端/admin 代码 |
| 密钥 | 不涉及 |
| 备份恢复 | 新增配置表进入 MySQL 常规备份 |
| 观测 | 写操作进入 admin audit log |

## 红蓝对抗

| 角色 | 结论 |
| --- | --- |
| 蓝队自检 | 未恢复等级特权；礼物仅配置价格和展示枚举 |
| 红队质疑 | 后续接 C 端送礼时必须走复式账本和审计，不得直接扣钱包字段 |
| 合入判断 | 通过当前后端/API/admin 构建验证后可进入 review |

项目级验收入口：`docs/qa/project-acceptance.md`。本次仅申请 ADM-409 / ADM-410 功能级 review，不宣称项目级 closure。

## 完成申请与裁决

| 项目 | 内容 |
| --- | --- |
| Agent Claim | implemented / verified |
| Project Decision | pending-review |

## 验证记录

| 命令/方式 | 结果 |
| --- | --- |
| `./devtools/framework status` | 通过 |
| `python3 scripts/validate-runtime-environment.py && python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |
| `go test ./internal/service/admin ./internal/repository/economy ./internal/http/adminapi` | 通过 |
| `go test ./...`（`services/go-app`） | 通过 |
| `npm run check:openapi` | 通过 |
| `npm run check:contract` | 通过 |
| `npm --prefix apps/admin run typecheck` | 通过 |
| `npm --prefix apps/admin run build` | 通过 |
| `python3 scripts/validate-prd.py && python3 scripts/validate-engineering-standards.py && python3 scripts/validate-capability-gates.py && python3 scripts/validate-completion-claims.py` | 通过 |

## 前端页面验收

| 项目 | 结果 |
| --- | --- |
| UI 验收模式 | no-design-mvp |
| 对应设计图 | 不涉及 |
| 目标视口 / 设计尺寸 | Admin 桌面端 1440×900；无外部设计稿尺寸 |
| 页面截图 | `output/playwright/admin-user-levels-desktop.png`、`output/playwright/admin-user-levels-mobile.png` |
| API 接口路径 | `/api/v1/admin/system/user-levels`、`/api/v1/admin/system/gifts` |
| UI 视觉证据 manifest | `docs/qa/ui-visual-evidence.json` |
| 真实手机视口 | Playwright 375×812 已打开 `/system/user-levels` 并截图 |
| 桌面/平板视口 | Playwright 1440×900 已打开 `/system/user-levels` 并截图 |
| 响应式验收 | no-design-mvp；验证构建产物在桌面/移动视口可加载，页面因未登录进入后台认证流程 |
| mock/fallback 状态与原因 | 本次新增等级/礼物页面不使用 mock；占位原因：`apps/admin/src/api/request.ts` 仍有历史 mock 错误字段兼容注释，属于既有请求适配器兼容逻辑，本次未修改 |
| SEO异常验证/meta scope | 本次未修改 `apps/web/**`；工作树中既有 `apps/web` 改动与本任务无关，SEO异常验证/meta 不在 ADM-409/ADM-410 范围内 |
| 后台权限与审计 | 需 admin JWT；写操作写 audit |
| 根节点是否挂载 | 已挂载到系统管理菜单 |
| 合入判断 | pending-review |

## 风险与待办

1. 当前仅完成后台配置；C 端送礼、扣钻、等级计算任务未接入。
2. 默认礼物 icon 使用 `/uploads/gifts/*.png` 占位路径，运营上线前需上传正式图标或替换 URL。
3. 竞猜活动仅隐藏后台菜单，未删除后端/契约历史接口；如产品确认彻底下线，应单独做删除/兼容 ADR。

## 交接说明

1. 部署前先跑 migration `000024`。
2. 后续接送礼必须使用 `internal/pkg/ledger.PostTx`，禁止直接更新钱包余额。
3. 等级配置不得用于弹幕颜色、投注限额、进场特效或排序权重。
