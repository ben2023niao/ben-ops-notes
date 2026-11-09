---
id: "doc-517385c4337b"
title: "Agent 工作日志 · admin-protocol-management"
date: "2026-05-29T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Python", "Go", "Docker", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-29-admin-protocol-management.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/docs/agents/logs/2026-05-29-admin-protocol-management.md"
sourceSha256: "32176c4dd0d7398510f860d075207b111dbbc10f90d524e789427f138afef5f1"
sourceSystem: "project-doc"
---

# Agent 工作日志 · admin-protocol-management

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605290000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BShell%2BPython-Agent%20%E5%B7%A5%E4%BD%9C%E6%97%A5%E5%BF%97%20%C2%B7%20admin-protocol-management.md)

> 整理日期：2026-05-29 00:00｜日期依据：文件名日期

日期：2026-05-29
Agent：Claude（后端 + vben 前端）
任务：后台新增「协议管理」模块（标题 + 富文本内容，admin 端 tiptap 编辑）

## 输入资料

- PRD：`docs/prd/modules/kickoff-admin.md`
- 需求 ID：ADM-919（本次新增登记）
- 设计图：无（用户口头需求）
- 接口/契约：`packages/contracts/openapi/v1.yaml` → `docs/api/openapi.yaml`（生成）
- AI/工具控制文件：`CLAUDE.md` / `AGENTS.md` / `apps/admin/CLAUDE.md`
- 其他：参考现有 ADR-0014 ads 模块（最接近的 admin CRUD 链路）

## 本次目标

1. 设计协议存储表（DB 此前无此字段）
2. 后端 CRUD：契约 + migration + model + repo + service + handler + router + 单测
3. 前端 vben admin 协议管理页面，正文接入 tiptap 富文本编辑器

## 修改文件

| 文件 | 说明 |
| --- | --- |
| `packages/contracts/openapi/v1.yaml` | 新增 protocols CRUD paths + 3 个 schema + `后台-协议管理` tag（唯一源） |
| `docs/api/openapi.yaml` | `make openapi` 生成产物（+112 行） |
| `services/go-app/migrations/000022_create_protocol_tables.{up,down}.sql` | `protocols` 表（雪花 ID / 软删 / code 唯一 / content MEDIUMTEXT） |
| `services/go-app/internal/model/protocol.go` | Protocol GORM model |
| `services/go-app/internal/dto/protocol.go` | Item / Create / Update DTO |
| `services/go-app/internal/repository/protocol/repo.go` | Repository 接口 + 实现 |
| `services/go-app/internal/service/admin/protocol.go` | ProtocolService（snowflake + audit + code 校验/唯一） |
| `services/go-app/internal/service/admin/protocol_test.go` | fake repo 单测，覆盖 happy/error（race 通过） |
| `services/go-app/internal/http/adminapi/protocol.go` | HTTP handler |
| `services/go-app/internal/http/router/admin.go` | 注册 service/handler + 4 条路由（requireAdmin） |
| `apps/admin/src/api/modules/protocol.ts` + `api/index.ts` | 前端 API 模块 + 导出 |
| `apps/admin/src/views/protocols/list.vue` | 列表 + 增删改弹窗，content 用 VbenTiptap |
| `apps/admin/src/router/routes/modules/contents.ts` | 内容管理下新增协议管理菜单 |
| `apps/admin/src/locales/langs/{zh-CN,en-US}/{page,protocol}.json` | 中英文案 |

## 核心决策

1. **形态：列表式自由 CRUD + 单条覆盖**（用户拍板）。不建版本表，改动追溯靠 `admin_audit_logs`。
2. **content 用 MEDIUMTEXT**：富文本 HTML（tiptap 产出）可能上万字带标签，TEXT(64KB) 不一定够。
3. **code 业务唯一 key**：`uk_code_deleted (code, deleted_at)` 软删后可同名重建；格式 `^[a-z0-9_]+$` 在 service 层 + OpenAPI pattern 双重约束。
4. **照搬 ADR-0014 ads 链路**，复用 `package admin` 已有的 `boolToTiny` helper、`parseIDParam`、`ApiEnvelope`/`EmptyOK`/`SnowflakeId` 契约组件。
5. **前端 tiptap 不进 useVbenForm schema**：content 用独立 `ref` + `VbenTiptap` v-model（HTML 字符串）管理，编辑态回填靠 tiptap 自带的 modelValue watch。

## 框架价值判断

| 问题 | 结论 |
| --- | --- |
| 沉淀属于规则/模板/脚本/适配器还是项目资产 | 项目资产（一个具体业务模块） |
| 哪些可复用到下一个项目 | 「标题+富文本 CMS」CRUD 的后端+vben+tiptap 套路可复用 |
| 哪些只属于当前项目 | protocols 表与 code 约定 |
| 是否可规模化 | 是，标准 admin CRUD 模式 |
| Scale Profile | mvp |
| 是否影响 Overlay | 否 |
| 是否增加自动校验/CI 门禁 | 否（沿用 openapi validate + go test） |
| 是否降低 Agent 偷懒空间 | 否 |

## 需求追踪

| 项目 | 内容 |
| --- | --- |
| 需求 ID | ADM-919 |
| 需求总账 | `docs/prd/requirements.md`（未登记，建议后续补） |
| 模块 PRD | `docs/prd/modules/kickoff-admin.md` §ADM-919 |
| OpenAPI / DTO | `packages/contracts/openapi/v1.yaml`（AdminProtocol*） |
| 验收证据 | 见下「验证」 |
| 不涉及契约的原因 | — |

## 工程规范

| 项目 | 内容 |
| --- | --- |
| 是否影响数据表 / migration / 索引 | 是，新增 `protocols` 表 + 索引 + down.sql |
| 是否影响账本/事务/幂等/审计 | 仅审计（写操作 `admin.protocol.*`）；非资金 |
| 规范例外 | dev 环境无 `schema_migrations`，migration 经 `scripts/docker-migrate-seed.sh` 同款方式直接应用 |

## 架构能力门禁

| 项目 | 内容 |
| --- | --- |
| 是否只是 CRUD | 是 |
| 涉及能力 | 权限安全（requireAdmin + 审计） / 迁移 |
| 高风险触发项 | 不涉及（非资金/订单/扣费） |
| 能力门禁结论 | 允许合入 |

## 运维影响

| 项目 | 内容 |
| --- | --- |
| 部署 | 需在目标环境执行 000022 migration |
| 回滚 | `000022_*.down.sql`（DROP TABLE protocols） |
| 密钥 | 不涉及 |
| 备份恢复 | 新增表纳入 DB 备份 |
| 观测 | 写操作进 admin_audit_logs |

## 验证

- **后端**：容器内 `go build ./...` + `go test -race ./internal/service/admin/`（含 protocol 8 例）全绿；`go test ./internal/http/adminapi/` 无回归。
- **契约**：`python3 scripts/build-openapi-docs.py` 重生 + `swagger-cli validate docs/api/openapi.yaml` 通过；`gen:sdk` 重生 ts-sdk。
- **E2E**（admin-api :8081，air 热重载）：登录拿 token → CREATE(雪花id) / 重复 code→20003 / 非法 code→20001 / PATCH(字段生效) / DELETE(软删后列表空) 全部符合预期；`admin_audit_logs` 三条 `admin.protocol.{create,update,delete}` result=ok。
- **前端**：`pnpm --filter @kickoff/admin typecheck` 通过（vue-tsc exit 0）。
- **遗留**：浏览器实测受阻——dev server(:5174) 因预先存在的 `sass-embedded` 缺失（最近 env/依赖 commit 引入）持续 restart failed，非本任务改动导致。tiptap 页面交互未在浏览器实测。
