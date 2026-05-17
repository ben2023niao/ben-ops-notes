---
id: "doc-44264fdaa88b"
title: "Admin Agent 数据接入 API 设计"
date: "2026-05-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md"
sourceSha256: "9a5ce420d9475869891df6277ec1fafa044118bcec88bddd56ed122ef95e3227"
sourceSystem: "project-doc"
---

# Admin Agent 数据接入 API 设计

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md`

> 整理日期：2026-05-18 00:00｜日期依据：文件名日期

> 状态:待评审 · 日期:2026-05-18 · 范围:`apps/admin`
> 关联:[产品形态与架构](2026-05-08-ghome-product-shape-design.md)、[CLAUDE.md](../../../CLAUDE.md)

## 0. 背景与目标

Admin 后台需要对 **OpenClaw Hermes 以及其它自研 Agent** 开放数据访问。Agent 通过一个授权码(token)鉴权,在线拉取一份按其授权范围个性化的 `Skill.md`(类 superpowers SKILL.md,教 Agent 如何鉴权与调用),再以该 token 调用只读 JSON API 拉取数据。

**确认的核心约束**

- **只读**:Agent 仅能 `GET`,不可改动任何数据。
- **落在 admin app 内**:复用 `apps/admin` 既有 prisma / audit / middleware / `lib/db.ts`,不新起服务。
- **每 Agent 独立授权码 + 范围 + 可吊销**:新增 `AgentClient` 表 + admin 管理 UI。
- **manifest 驱动**:端点路由、scope 校验、Skill.md 生成共用同一份 manifest,杜绝文档与实现漂移。
- **数据范围全开但按 scope 分级**:已发布内容 / 全状态内容 / 点击分析 / 运营敏感(redirect / 审计 / 联系表单 PII / 管理员账号)均可经显式 scope 开放。

**默认决策(评审时可推翻)**

- **MVP 不做硬限流**:对象是可信自研 Agent;仅靠 `pageSize ≤ 100` 兜底,限流列入"未来"。评审时若要求敏感数据必须带限流,升为 MVP 项。

## 1. 整体架构

```
Agent (OpenClaw Hermes / 自研)
  │  Authorization: Bearer ghagt_xxx
  ▼
apps/admin/app/api/agent/v1/[[...slug]]/route.ts   单一 catch-all dispatcher
  │  ① withAgentAuth(token): 查 AgentClient → 校验 disabled / expiresAt
  │  ② 按 pathname+method 命中 manifest 条目 → 校验 entry.scope ∈ client.scopes
  │  ③ 写审计 (agent.pull / agent.denied)
  ▼
manifest[entry].handler → 复用 lib/db.ts 查询 → JSON 信封
另一条:GET /api/agent/v1/skill.md → 遍历 manifest 按 client.scopes 过滤 → 个性化 Markdown
```

新增文件集中在 `apps/admin/lib/agent-api/` 与 `apps/admin/app/api/agent/v1/`,加一支 Prisma 迁移与一组 admin UI 页面。

## 2. 数据模型

新增 Prisma model（Postgres）：

```prisma
model AgentClient {
  id               String   @id @default(uuid()) @db.Uuid
  name             String   @unique
  tokenPrefix      String   @map("token_prefix")
  tokenHash        String   @unique @map("token_hash")
  scopes           String[] // 见 §3 scope 枚举
  disabled         Boolean  @default(false)
  expiresAt        DateTime? @map("expires_at") @db.Timestamptz(6)
  lastUsedAt       DateTime? @map("last_used_at") @db.Timestamptz(6)
  note             String?
  createdByAdminId String   @map("created_by_admin_id") @db.Uuid
  createdBy        AdminUser @relation(fields: [createdByAdminId], references: [id])
  createdAt        DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt        DateTime @updatedAt @map("updated_at") @db.Timestamptz(6)

  @@index([tokenPrefix])
  @@map("agent_clients")
}
```

Agent 访问日志单独建表(现有 `audit_log.admin_user_id` 非空、专记有管理员身份的操作;Agent 拉取无管理员身份,量级与性质不同,分表):

```prisma
model AgentAccessLog {
  id            String   @id @default(uuid()) @db.Uuid
  agentClientId String   @map("agent_client_id") @db.Uuid
  client        AgentClient @relation(fields: [agentClientId], references: [id])
  endpoint      String   // 命中的 manifest path,如 "/api/agent/v1/contact-submissions"
  status        String   // "ok" | "denied"
  ts            DateTime @default(now()) @db.Timestamptz(6)

  @@index([agentClientId, ts(sort: Desc)])
  @@map("agent_access_log")
}
```

- `AgentClient` 反向加 `accessLogs AgentAccessLog[]`;`AdminUser` 反向加 `agentClients AgentClient[]`。
- 原始 token 永不入库:仅存 `tokenPrefix`(前 8 位,用于 UI/日志辨识)与 `[敏感内容已脱敏] 十六进制。
- 迁移名:`<timestamp>_agent_clients`(随 P10a 之后顺延),一支迁移同时建两张表。

## 3. Scope 枚举

TS 联合常量（`apps/admin/lib/agent-api/scopes.ts`），非 DB enum，便于演进；manifest 与签发校验均引用：

| scope | 解锁数据 |
|---|---|
| `content:published` | 已发布 App/视频/指南/专题/榜单/专辑/分类/标签 |
| `content:all` | 同上但含 draft/archived 全状态（解锁 `?status=`） |
| `analytics:read` | 每日点击趋势 / 热门 redirect 聚合（无原始 IP/UA/referrer） |
| `ops:redirects` | redirect 列表与 target |
| `ops:audit` | 审计日志 |
| `ops:contacts` | 联系表单提交（**含用户 PII**，最敏感） |
| `ops:admins` | 管理员账号列表（字段白名单：id/email/name/lastLoginAt，**绝不含 passwordHash**） |

签发时校验所选 scopes 全部 ∈ 该枚举，否则 400。

## 4. Manifest

`apps/admin/lib/agent-api/manifest.ts` 导出一个数组，每端点一条：

```ts
interface AgentEndpoint {
  path: string;                 // "/api/agent/v1/apps" 或 "/api/agent/v1/apps/:slug"
  method: "GET";
  scope: AgentScope;            // 该端点要求的 scope
  summary: string;              // Skill.md 用
  query?: { name: string; type: string; desc: string }[];
  exampleResponse: unknown;     // Skill.md 里展示的小样本
  handler: (ctx: AgentCtx) => Promise<Response>;
}
```

`AgentCtx` = `{ req, params, client }`。dispatcher、scope 校验、Skill.md 生成全部读这一份数组——这是方案 B 的核心:端点 ↔ 文档 ↔ scope 校验三者同源。

## 5. 鉴权流程

**Token 形态与签发**

- 格式 `ghagt_` + 32 字节随机（base62），≥256 bit 熵。
- 签发：服务端生成原始 token → 存 `tokenPrefix` + `[敏感内容已脱敏] → 页面**仅此一次**明文回显（复制按钮 + “关闭后不再显示”警告）。

**`withAgentAuth(requiredScope)`**（`apps/admin/lib/agent-api/auth.ts`），按序：

1. 取 `Authorization: Bearer ghagt_...`；缺失 → `401 unauthorized`
2. `sha256` → 按 `tokenHash` 唯一索引查 `AgentClient`；未命中 → `401 unauthorized`
3. `disabled=true` → `401 token_revoked`；`expiresAt` 已过 → `401 token_expired`
4. `requiredScope ∉ client.scopes` → `403 forbidden`
5. 放行；`lastUsedAt` 节流更新（距上次 >60s 才写）
6. 写访问日志到 `AgentAccessLog`:成功 `status="ok"`;被拒且端点 scope 属 `ops:*` 写 `status="denied"`。记 `agentClientId` + `endpoint`(fire-and-forget,不阻塞响应)。**不复用 `logAuditAction`**(那张表 actor 必须是管理员)

**middleware 改动**:[apps/admin/middleware.ts](../../../apps/admin/middleware.ts) 公开路径白名单增加 `pathname.startsWith("/api/agent/")`,与既有 `/api/cron/` 同样绕过 session 重定向（鉴权在 handler 内完成）。

## 6. API 端点清单

全部 `GET`，前缀 `/api/agent/v1`：

| 端点 | scope | 说明 |
|---|---|---|
| `/skill.md` | 任一有效 token | 个性化技能文档（§8） |
| `/apps` `/apps/:slug` | `content:published`（持 `content:all` 解锁 `?status=`） | App 列表/详情 |
| `/videos` `/videos/:slug` | 同上 | 视频 |
| `/guides` `/guides/:slug` | 同上 | 指南 |
| `/topics` `/topics/:slug` `/albums` `/albums/:slug` `/rankings` | 同上 | collections 三类 |
| `/categories` `/tags` | `content:published` | 分类/标签全集 |
| `/analytics/clicks/daily?days=7` | `analytics:read` | 每日点击趋势（days ≤ 90） |
| `/analytics/redirects/top?limit=20` | `analytics:read` | 热门 redirect（limit ≤ 100） |
| `/redirects` | `ops:redirects` | redirect 列表+target（复用已修的 `listRedirects`） |
| `/audit-log` | `ops:audit` | 审计日志 |
| `/contact-submissions` | `ops:contacts` | 联系表单（含 PII） |
| `/admins` | `ops:admins` | 管理员列表,字段白名单 id/email/name/lastLoginAt |

## 7. 响应约定

- JSON，字段 camelCase；复用 [apps/admin/lib/db.ts](../../../apps/admin/lib/db.ts) / [apps/web/lib/db.ts](../../../apps/web/lib/db.ts) 既有 mapper，不另写查询逻辑。
- 列表统一信封:`{ data: [...], page, pageSize, total }`。**offset 分页**:`?page=1&pageSize=20`，`pageSize` 上限 100，越界归一到 100。
- 状态过滤:端点默认 `status=published AND deletedAt IS NULL`;仅当 token 持 `content:all` 时 `?status=draft|archived|all` 生效，否则**静默忽略**该参数（不报错，防越权探测）。
- 错误体统一 `{ error: <code> }`:`401`（token 缺失/无效/吊销/过期）、`403`（有 token 缺 scope）、`404`（未知端点）、`400`（非法 query）。
- 不开 CORS（纯服务端到服务端）。

## 8. Skill.md 生成器

`apps/admin/lib/agent-api/skill-md.ts`；`GET /api/agent/v1/skill.md` 走同一 `withAgentAuth`（无需特定 scope，任一有效 token 即可），返回 `text/markdown`：

- 遍历 manifest，**仅渲染 `entry.scope ∈ client.scopes` 的端点**。
- 产出标准 superpowers 风格 SKILL.md：frontmatter（`name: ghome-admin-data` / `description`）、鉴权说明（如何带 Bearer）、base URL、按 scope 分组的端点表（path / 用途 / query / `exampleResponse`）、分页与错误码约定。
- 个性化:无 `ops:contacts` 的 Agent 看不到该端点存在,开箱即用且不泄露未授权面。

## 9. Admin 管理 UI

侧边栏新增「Agent 接入」，路由 `apps/admin/app/(admin)/agent-clients/`：

- **列表页**:name / tokenPrefix / scopes / 状态 / lastUsedAt / expiresAt（复用 `ListTable`）。
- **新建页**:name + scope 多选勾选 + 可选过期 + 备注 → 提交后**一次性**明文展示 token（复用一次性展示 UI 模式）。*(已废弃:手工新建入口已移除,Agent 仅经自助配对进入——见自助配对附录)*
- **编辑页**:停用/启用、增删 scope、**轮换 token**（生成新、旧立废）、改过期、删除。
- 全部写操作走 `logAuditAction`，action 形如 `agentClient.create/rotate/revoke/update`。

## 10. 安全

- token 仅以 sha256 入库，按 hash 唯一索引查（无明文比较）。
- `ops:admins` 字段白名单硬编码,`passwordHash` 不进序列化路径;`ops:contacts` 仅在显式 scope 下可达。
- 成功拉取 + `ops:*` 被拒尝试均落 `AgentAccessLog`（含 agentClientId / endpoint / status），便于事后追溯。
- admin UI 的签发/吊销/轮换等写操作仍走 `logAuditAction`（有管理员身份）。
- `expiresAt` / `disabled` 即时生效;轮换即旧 token 立废。
- 限流:MVP 不做（见 §0 默认决策）;`pageSize ≤ 100` 兜底。

## 11. 测试策略

vitest 为主，沿用各包现有配置：

- **单元**:token 生成/校验、scope 判定、manifest→Skill.md 渲染、`content:all` 状态门控。
- **集成**:每端点 无 token→401 / 错 scope→403 / disabled·expired→401 / published-only vs content:all 行为差异 / `/admins` 响应不含 `passwordHash`（显式断言)。
- **访问日志**:断言拉取写 `AgentAccessLog` status=ok 行、`ops:*` 被拒写 status=denied 行。
- **E2E**（Playwright，admin）:签发 → token 一次性展示 → 用该 token 拉一个端点 → 吊销 → 该 token 立即 401。

## 12. 分阶段切片

| 阶段 | 内容 | 完成判据 |
|---|---|---|
| **A1 · 数据模型 + 鉴权内核** | `AgentClient` + `AgentAccessLog` 迁移 + scopes 常量 + `withAgentAuth` + middleware 放行 | 单元测试:token 生成/校验/scope 判定通过;手工 curl 带/不带 token 命中 401/403 |
| **A2 · Manifest + dispatcher + 内容端点** | manifest 抽象 + catch-all dispatcher + content/categories/tags 端点 | 持 `content:published` token 能拉 apps/videos/...;`content:all` 解锁 `?status=` |
| **A3 · 分析 + 运营端点** | analytics / redirects / audit-log / contact-submissions / admins 端点 | 各端点 scope 门控正确;`/admins` 无 passwordHash;`ops:*` 被拒写 `AgentAccessLog` status=denied |
| **A4 · Skill.md 生成器** | manifest→个性化 Markdown | 不同 scope token 拉到的 skill.md 端点集不同;无 scope 的端点不出现 |
| **A5 · Admin 管理 UI** | agent-clients 列表/新建/编辑/轮换/吊销 + 审计 | 签发→一次性展示→拉数据→吊销→立即 401 的 E2E 通过 |

## 13. 不在本 spec 范围

- 写接口（Agent 回写数据）
- 硬限流 / 配额(评审推翻则升 MVP)
- OAuth / OIDC 等标准协议鉴权(MVP 用自管 bearer token)
- Agent 侧 SDK / 客户端封装
- Webhook / 推送(本设计仅 pull)
- AgentAccessLog 留存/清理:每次拉取写一行,MVP 不做自动清理/归档(与限流同属有意识的运维延后项);后续可加 /api/cron/ 定时 prune,按 ts 滚动保留窗口。
- 公开自助配对通道(Skill.md → 一次性配对码 → 自助换 token):见配套附录 [2026-05-18-agent-self-pairing-design.md](2026-05-18-agent-self-pairing-design.md)。
