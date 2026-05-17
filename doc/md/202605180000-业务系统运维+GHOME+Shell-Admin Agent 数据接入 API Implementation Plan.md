---
id: "doc-85dcf312c72e"
title: "Admin Agent 数据接入 API Implementation Plan"
date: "2026-05-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-admin-agent-data-api.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-admin-agent-data-api.md"
sourceSha256: "dc26cf19bfdbb48ff637e0f91bd6f61486a70102ac9ea18f153187aa7eed9725"
sourceSystem: "project-doc"
---

# Admin Agent 数据接入 API Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-admin-agent-data-api.md`

> 整理日期：2026-05-18 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `apps/admin` 内增加一套 manifest 驱动、按 Agent scope 分级的只读数据 API + 个性化 Skill.md + Agent 授权码管理 UI。

**Architecture:** 一个 `[[...slug]]` catch-all dispatcher 用 Bearer token 解析 `AgentClient`、按 manifest 命中端点并校验 scope、写 `AgentAccessLog`,再调 manifest handler 复用 prisma 查询返回 JSON。Skill.md 端点遍历同一 manifest 按 scope 过滤生成 Markdown。Admin UI 签发/吊销/轮换授权码。

**Tech Stack:** Next.js 15 App Router (Route Handlers + Server Actions)、Prisma 5、Postgres、vitest、Playwright。

**Spec:** [docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md](../specs/2026-05-18-admin-agent-data-api-design.md)

---

## File Structure

**新建**
- `apps/admin/lib/agent-api/scopes.ts` — scope 联合常量 + 校验
- `apps/admin/lib/agent-api/token.ts` — token 生成 / sha256 / prefix(纯函数)
- `apps/admin/lib/agent-api/manifest.ts` — `AgentEndpoint`/`AgentCtx` 类型 + `ENDPOINTS` 数组 + `matchEndpoint`
- `apps/admin/lib/agent-api/auth.ts` — `resolveAgentClient` / `logAccess` / `touchLastUsed`
- `apps/admin/lib/agent-api/http.ts` — `jsonError` / `pageArgs` / `envelope` / `statusFilter`
- `apps/admin/lib/agent-api/queries.ts` — 各资源 handler(复用 prisma)
- `apps/admin/lib/agent-api/skill-md.ts` — `renderSkillMd`
- `apps/admin/app/api/agent/v1/[[...slug]]/route.ts` — dispatcher
- `apps/admin/lib/agent-clients-db.ts` — AgentClient 增删改查 + 轮换
- `apps/admin/app/(admin)/agent-clients/page.tsx` — 列表
- `apps/admin/app/(admin)/agent-clients/new/page.tsx` — 新建
- `apps/admin/app/(admin)/agent-clients/[id]/edit/page.tsx` — 编辑
- `apps/admin/app/(admin)/agent-clients/actions.ts` — server actions
- `apps/admin/components/TokenRevealBanner.tsx` — token 一次性展示(client component)
- `apps/admin/vitest.config.ts` — admin 测试配置
- `apps/admin/tests/*.test.ts` — 测试
- `apps/admin/e2e/agent-clients.spec.ts` — E2E

**修改**
- `packages/db/prisma/schema.prisma` — 新增 `AgentClient` / `AgentAccessLog` model + 反向关系
- `packages/db/src/index.ts` — 重导出 `AgentClient` / `AgentAccessLog` 类型
- `apps/admin/package.json` — 加 `vitest` devDep + `test` 脚本
- `apps/admin/middleware.ts` — 公开路径白名单加 `/api/agent/`
- `apps/admin/app/(admin)/layout.tsx` — 侧边栏加「Agent 接入」入口
- `.github/workflows/ci.yml` — 加 admin test 步骤
- `apps/admin/playwright.config.ts`(若无则新建,镜像 web 配置)

---

## Task 1: Prisma 模型 + 迁移

**Files:**
- Modify: `packages/db/prisma/schema.prisma`
- Modify: `packages/db/src/index.ts`
- Create: `packages/db/prisma/migrations/<timestamp>_agent_clients/migration.sql`(由 prisma 生成)

- [ ] **Step 1: 在 schema.prisma 末尾(`ContactSubmission` model 之后)追加两个 model**

```prisma
model AgentClient {
  id               String   @id @default(uuid()) @db.Uuid
  name             String   @unique
  tokenPrefix      String   @map("token_prefix")
  tokenHash        String   @unique @map("token_hash")
  scopes           String[]
  disabled         Boolean  @default(false)
  expiresAt        DateTime? @map("expires_at") @db.Timestamptz(6)
  lastUsedAt       DateTime? @map("last_used_at") @db.Timestamptz(6)
  note             String?
  createdByAdminId String   @map("created_by_admin_id") @db.Uuid
  createdBy        AdminUser @relation(fields: [createdByAdminId], references: [id])
  createdAt        DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt        DateTime @updatedAt @map("updated_at") @db.Timestamptz(6)

  accessLogs AgentAccessLog[]

  @@index([tokenPrefix])
  @@map("agent_clients")
}

model AgentAccessLog {
  id            String   @id @default(uuid()) @db.Uuid
  agentClientId String   @map("agent_client_id") @db.Uuid
  client        AgentClient @relation(fields: [agentClientId], references: [id])
  endpoint      String
  status        String
  ts            DateTime @default(now()) @db.Timestamptz(6)

  @@index([agentClientId, ts(sort: Desc)])
  @@map("agent_access_log")
}
```

- [ ] **Step 2: 给 `AdminUser` model 加反向关系**

在 `model AdminUser` 内 `repliedSubmissions ContactSubmission[]` 行下新增一行:

```prisma
  agentClients       AgentClient[]
```

- [ ] **Step 3: 生成迁移**

⚠️ 本仓库**不能用 `prisma migrate dev`**:既有迁移含 schema.prisma 无法表达的裸 SQL(`category_kind` 生成列、复合 FK、deferrable unique),`migrate dev` 每次都误判为破坏性 drift。仓库实际约定是**手放迁移目录 + `prisma migrate deploy`**(全部既有迁移 + CI + docker `migrate` 服务皆用 deploy)。用 **schema-vs-schema diff** 生成纯增量 SQL,绕开 live-DB drift:

```bash
# 1) 复制当前 schema 为 base,从 base 里删掉本任务新增的两个 model + AdminUser 那行 agentClients 反向关系
cp packages/db/prisma/schema.prisma /tmp/schema-base.prisma
#   编辑 /tmp/schema-base.prisma:删除 model AgentClient {...}、model AgentAccessLog {...}、
#   以及 AdminUser 内新增的 "agentClients AgentClient[]" 一行(恢复为本任务前的 schema)
# 2) schema→schema diff 仅产出这两张新表的 CREATE TABLE(Prisma 原生格式,正确默认值)
mkdir -p packages/db/prisma/migrations/20260518000000_agent_clients
pnpm --filter @ghome/db exec prisma migrate diff \
  --from-schema-datamodel /tmp/schema-base.prisma \
  --to-schema-datamodel packages/db/prisma/schema.prisma \
  --script > packages/db/prisma/migrations/20260518000000_agent_clients/migration.sql
# 3) 检视 migration.sql:必须只含 agent_clients / agent_access_log 的 CREATE TABLE/INDEX/FK,
#    绝不能出现任何 DROP COLUMN / DROP INDEX / ALTER ... category_kind / contact_submissions。
#    若出现,停止并报告(说明 base schema 没删干净)。
# 4) 应用(deploy 按迁移文件原样执行,既有迁移已 applied → 幂等,不会带入 drift)
pnpm --filter @ghome/db db:migrate:deploy
```
Expected: `packages/db/prisma/migrations/20260518000000_agent_clients/migration.sql` 仅含两张新表的 `CREATE TABLE "agent_clients"` / `CREATE TABLE "agent_access_log"` + 索引 + FK;`migrate deploy` 输出 `1 migration applied`。

- [ ] **Step 4: 在 `packages/db/src/index.ts` 的 `export type { ... } from "@prisma/client";` 块内追加两个类型**

在 `RedirectOwnerKind,` 行后、`} from "@prisma/client";` 前加:
```ts
  AgentClient,
  AgentAccessLog,
```

- [ ] **Step 5: 重新生成 client 并 typecheck**

Run:
```bash
docker compose run --rm migrate pnpm --filter @ghome/db exec prisma generate
pnpm --filter @ghome/db typecheck
```
Expected: 均无错误;`import type { AgentClient } from "@ghome/db"` 可用。

- [ ] **Step 6: Commit**

```bash
git add packages/db/prisma/schema.prisma packages/db/prisma/migrations packages/db/src/index.ts
git commit -m "feat(db): AgentClient + AgentAccessLog models for agent data API"
```

---

## Task 2: admin vitest 基建 + CI 步骤

**Files:**
- Create: `apps/admin/vitest.config.ts`
- Modify: `apps/admin/package.json`
- Modify: `.github/workflows/ci.yml`
- Create: `apps/admin/tests/smoke.test.ts`

- [ ] **Step 1: 创建 `apps/admin/vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    globals: false,
    testTimeout: 10000,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
      "@prisma/client": path.resolve(__dirname, "../../packages/db/node_modules/.prisma/client"),
    },
  },
});
```

- [ ] **Step 2: 在 `apps/admin/package.json` 的 `scripts` 块加两行**

`"clean"` 行后追加:
```json
    "test": "vitest run",
    "test:watch": "vitest",
```
并在 `devDependencies` 加 `"vitest": "^2.1.0"`。

- [ ] **Step 3: 写最小冒烟测试 `apps/admin/tests/smoke.test.ts`**

```ts
import { describe, it, expect } from "vitest";

describe("admin vitest wiring", () => {
  it("runs", () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] **Step 4: 安装依赖并跑测试验证基建可用**

Run:
```bash
pnpm install
pnpm --filter @ghome/admin test
```
Expected: PASS,1 passed。

- [ ] **Step 5: 在 `.github/workflows/ci.yml` 加 admin 测试步骤**

在 `- name: Test (web — click-tracking helpers)` 那一步(`run: pnpm --filter @ghome/web test`)之后插入:
```yaml
      - name: Test (admin — agent API)
        run: pnpm --filter @ghome/admin test
```

- [ ] **Step 6: Commit**

```bash
git add apps/admin/vitest.config.ts apps/admin/package.json apps/admin/tests/smoke.test.ts pnpm-lock.yaml .github/workflows/ci.yml
git commit -m "chore(admin): vitest setup + CI test step"
```

---

## Task 3: scopes.ts

**Files:**
- Create: `apps/admin/lib/agent-api/scopes.ts`
- Test: `apps/admin/tests/scopes.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/scopes.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { ALL_SCOPES, isValidScope } from "@/lib/agent-api/scopes";

describe("scopes", () => {
  it("contains exactly the 7 spec scopes", () => {
    expect([...ALL_SCOPES].sort()).toEqual(
      [
        "analytics:read",
        "content:all",
        "content:published",
        "ops:admins",
        "ops:audit",
        "ops:contacts",
        "ops:redirects",
      ].sort(),
    );
  });

  it("isValidScope accepts known, rejects unknown", () => {
    expect(isValidScope("content:published")).toBe(true);
    expect(isValidScope("ops:admins")).toBe(true);
    expect(isValidScope("ops:secret")).toBe(false);
    expect(isValidScope("")).toBe(false);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test scopes`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/scopes.ts`**

```ts
export const ALL_SCOPES = [
  "content:published",
  "content:all",
  "analytics:read",
  "ops:redirects",
  "ops:audit",
  "ops:contacts",
  "ops:admins",
] as const;

export type AgentScope = (typeof ALL_SCOPES)[number];

export function isValidScope(s: string): s is AgentScope {
  return (ALL_SCOPES as readonly string[]).includes(s);
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test scopes`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/scopes.ts apps/admin/tests/scopes.test.ts
git commit -m "feat(admin): agent-api scope enum"
```

---

## Task 4: token.ts

**Files:**
- Create: `apps/admin/lib/agent-api/token.ts`
- Test: `apps/admin/tests/token.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/token.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { generateToken, hashToken, tokenPrefix } from "@/lib/agent-api/token";

describe("token", () => {
  it("generateToken has ghagt_ prefix and 32 base62 chars", () => {
    const t = generateToken();
    expect(t).toMatch(/^ghagt_[0-9A-Za-z]{32}$/);
  });

  it("generateToken is unique across calls", () => {
    const set = new Set(Array.from({ length: 100 }, () => generateToken()));
    expect(set.size).toBe(100);
  });

  it("hashToken is deterministic sha256 hex (64 chars)", () => {
    expect(hashToken("ghagt_abc")).toBe(hashToken("ghagt_abc"));
    expect(hashToken("ghagt_abc")).toMatch(/^[0-9a-f]{64}$/);
    expect(hashToken("ghagt_abc")).not.toBe(hashToken("ghagt_abd"));
  });

  it("tokenPrefix returns ghagt_ + first 8 random chars (14 total)", () => {
    const t = "ghagt_ABCDEFGH" + "rest";
    expect(tokenPrefix(t)).toBe("ghagt_ABCDEFGH");
    expect(tokenPrefix(t)).toHaveLength(14);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test token`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/token.ts`**

```ts
import { randomBytes, createHash } from "node:crypto";

const ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/** 生成 `ghagt_` + 32 字符 base62（约 190 bit 熵）的原始 token。 */
export function generateToken(): string {
  const buf = randomBytes(32);
  let out = "";
  for (const b of buf) out += ALPHABET[b % 62];
  return "ghagt_" + out.slice(0, 32);
}

/** sha256 十六进制；入库与查找均用它，原始 token 不落库。 */
export function hashToken(raw: string): string {
  return createHash("sha256").update(raw).digest("hex");
}

/** `ghagt_` + 前 8 个随机字符,用于 UI/日志辨识。 */
export function tokenPrefix(raw: string): string {
  return raw.slice(0, 14);
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test token`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/token.ts apps/admin/tests/token.test.ts
git commit -m "feat(admin): agent token generate/hash/prefix"
```

---

## Task 5: manifest 类型 + matchEndpoint

**Files:**
- Create: `apps/admin/lib/agent-api/manifest.ts`
- Test: `apps/admin/tests/manifest.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/manifest.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { matchEndpoint, type AgentEndpoint } from "@/lib/agent-api/manifest";

const eps: AgentEndpoint[] = [
  { path: "/api/agent/v1/apps", method: "GET", scope: "content:published", summary: "", exampleResponse: {}, handler: async () => new Response() },
  { path: "/api/agent/v1/apps/:slug", method: "GET", scope: "content:published", summary: "", exampleResponse: {}, handler: async () => new Response() },
];

describe("matchEndpoint", () => {
  it("matches static path", () => {
    const m = matchEndpoint("/api/agent/v1/apps", "GET", eps);
    expect(m?.endpoint.path).toBe("/api/agent/v1/apps");
    expect(m?.params).toEqual({});
  });

  it("matches param path and extracts param", () => {
    const m = matchEndpoint("/api/agent/v1/apps/foo-bar", "GET", eps);
    expect(m?.endpoint.path).toBe("/api/agent/v1/apps/:slug");
    expect(m?.params).toEqual({ slug: "foo-bar" });
  });

  it("returns null for unknown path or wrong method", () => {
    expect(matchEndpoint("/api/agent/v1/nope", "GET", eps)).toBeNull();
    expect(matchEndpoint("/api/agent/v1/apps", "POST" as "GET", eps)).toBeNull();
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test manifest`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/manifest.ts`**（先只放类型 + matchEndpoint，`ENDPOINTS` 留空数组,Task 8/11 填充）

```ts
import type { NextRequest } from "next/server";
import type { AgentClient } from "@ghome/db";
import type { AgentScope } from "./scopes";

export interface AgentCtx {
  req: NextRequest;
  params: Record<string, string>;
  client: AgentClient;
  searchParams: URLSearchParams;
}

export interface AgentEndpoint {
  path: string; // 如 "/api/agent/v1/apps" 或 "/api/agent/v1/apps/:slug"
  method: "GET";
  scope: AgentScope;
  summary: string;
  query?: { name: string; type: string; desc: string }[];
  exampleResponse: unknown;
  handler: (ctx: AgentCtx) => Promise<Response>;
}

export interface EndpointMatch {
  endpoint: AgentEndpoint;
  params: Record<string, string>;
}

export function matchEndpoint(
  pathname: string,
  method: "GET",
  endpoints: AgentEndpoint[],
): EndpointMatch | null {
  const segs = pathname.split("/").filter(Boolean);
  for (const ep of endpoints) {
    if (ep.method !== method) continue;
    const epSegs = ep.path.split("/").filter(Boolean);
    if (epSegs.length !== segs.length) continue;
    const params: Record<string, string> = {};
    let ok = true;
    for (let i = 0; i < epSegs.length; i++) {
      const e = epSegs[i];
      if (e.startsWith(":")) params[e.slice(1)] = decodeURIComponent(segs[i]);
      else if (e !== segs[i]) {
        ok = false;
        break;
      }
    }
    if (ok) return { endpoint: ep, params };
  }
  return null;
}

// Task 8 / Task 11 填充
export const ENDPOINTS: AgentEndpoint[] = [];
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test manifest`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/manifest.ts apps/admin/tests/manifest.test.ts
git commit -m "feat(admin): agent-api manifest types + path matcher"
```

---

## Task 6: 鉴权解析 + 访问日志

**Files:**
- Create: `apps/admin/lib/agent-api/auth.ts`
- Test: `apps/admin/tests/auth.test.ts`（命中真实 Postgres，CI 已起 service）

- [ ] **Step 1: 写失败测试 `apps/admin/tests/auth.test.ts`**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import { NextRequest } from "next/server";
import { resolveAgentClient, logAccess } from "@/lib/agent-api/auth";
import { generateToken, hashToken, tokenPrefix } from "@/lib/agent-api/token";

const RAW = generateToken();
let adminId: string;
let clientId: string;

beforeAll(async () => {
  const admin = await prisma.adminUser.create({
    data: { email: `auth-test-${Date.now()}@x.io`, [敏感内容已脱敏] },
  });
  adminId = admin.id;
  const c = await prisma.agentClient.create({
    data: {
      name: `auth-test-${Date.now()}`,
      [敏感内容已脱敏],
      [敏感内容已脱敏],
      scopes: ["content:published"],
      createdByAdminId: adminId,
    },
  });
  clientId = c.id;
});

afterAll(async () => {
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: clientId } });
  await prisma.agentClient.delete({ where: { id: clientId } });
  await prisma.adminUser.delete({ where: { id: adminId } });
});

function reqWith(auth?: string) {
  const h = new Headers();
  if (auth) h.set("authorization", auth);
  return new NextRequest("http://localhost/api/agent/v1/apps", { headers: h });
}

describe("resolveAgentClient", () => {
  it("401 when header missing or malformed", async () => {
    expect((await resolveAgentClient(reqWith())).ok).toBe(false);
    expect((await resolveAgentClient(reqWith("Bearer nope"))).ok).toBe(false);
  });

  it("401 when token unknown", async () => {
    const r = await resolveAgentClient(reqWith(`Bearer ${generateToken()}`));
    expect(r).toMatchObject({ ok: false, status: 401, code: "unauthorized" });
  });

  it("ok for valid token", async () => {
    const r = await resolveAgentClient(reqWith(`Bearer ${RAW}`));
    expect(r.ok).toBe(true);
  });

  it("401 token_revoked when disabled", async () => {
    await prisma.agentClient.update({ where: { id: clientId }, data: { disabled: true } });
    const r = await resolveAgentClient(reqWith(`Bearer ${RAW}`));
    expect(r).toMatchObject({ ok: false, code: "token_revoked" });
    await prisma.agentClient.update({ where: { id: clientId }, data: { disabled: false } });
  });

  it("401 token_expired when past expiresAt", async () => {
    await prisma.agentClient.update({
      where: { id: clientId },
      data: { expiresAt: new Date(Date.now() - 1000) },
    });
    const r = await resolveAgentClient(reqWith(`Bearer ${RAW}`));
    expect(r).toMatchObject({ ok: false, code: "token_expired" });
    await prisma.agentClient.update({ where: { id: clientId }, data: { expiresAt: null } });
  });

  it("logAccess writes a row", async () => {
    await logAccess(clientId, "/api/agent/v1/apps", "ok");
    const n = await prisma.agentAccessLog.count({
      where: { agentClientId: clientId, status: "ok" },
    });
    expect(n).toBeGreaterThanOrEqual(1);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test auth`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/auth.ts`**

```ts
import type { NextRequest } from "next/server";
import type { AgentClient } from "@ghome/db";
import { prisma } from "@ghome/db";
import { hashToken } from "./token";

export type AuthResult =
  | { ok: true; client: AgentClient }
  | { ok: false; status: 401; code: "unauthorized" | "token_revoked" | "token_expired" };

const BEARER_RE = /^Bearer\s+(ghagt_[0-9A-Za-z]{32})$/;

export async function resolveAgentClient(req: NextRequest): Promise<AuthResult> {
  const m = BEARER_RE.exec(req.headers.get("authorization") ?? "");
  if (!m) return { ok: false, status: 401, code: "unauthorized" };

  const client = await prisma.agentClient.findUnique({
    where: { [敏感内容已脱敏] },
  });
  if (!client) return { ok: false, status: 401, code: "unauthorized" };
  if (client.disabled) return { ok: false, status: 401, code: "token_revoked" };
  if (client.expiresAt && client.expiresAt.getTime() < Date.now()) {
    return { ok: false, status: 401, code: "token_expired" };
  }
  return { ok: true, client };
}

/** fire-and-forget;调用方用 `void logAccess(...)`,不阻塞响应。 */
export async function logAccess(
  agentClientId: string,
  endpoint: string,
  status: "ok" | "denied",
): Promise<void> {
  try {
    await prisma.agentAccessLog.create({ data: { agentClientId, endpoint, status } });
  } catch (e) {
    console.error("[agent-api] logAccess failed:", e);
  }
}

/** lastUsedAt 节流:距上次 >60s 才写。fire-and-forget。 */
export async function touchLastUsed(client: AgentClient): Promise<void> {
  const now = Date.now();
  if (client.lastUsedAt && now - client.lastUsedAt.getTime() < 60_000) return;
  try {
    await prisma.agentClient.update({
      where: { id: client.id },
      data: { lastUsedAt: new Date() },
    });
  } catch (e) {
    console.error("[agent-api] touchLastUsed failed:", e);
  }
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test auth`
Expected: PASS（需 DATABASE_URL 指向已迁移的库;本地 `docker compose up -d` 后跑,或在 CI 中自动满足）

- [ ] **Step 5: middleware 放行 `/api/agent/`**

在 `apps/admin/middleware.ts` 的公开路径 `if (...)` 条件里,`pathname.startsWith("/api/cron/") ||` 那行之后加一行:
```ts
    pathname.startsWith("/api/agent/") ||
```

- [ ] **Step 6: Commit**

```bash
git add apps/admin/lib/agent-api/auth.ts apps/admin/tests/auth.test.ts apps/admin/middleware.ts
git commit -m "feat(admin): agent token resolution + access log + middleware passthrough"
```

---

## Task 7: HTTP 辅助(分页 / 信封 / 状态门控 / 错误)

**Files:**
- Create: `apps/admin/lib/agent-api/http.ts`
- Test: `apps/admin/tests/http.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/http.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { pageArgs, statusFilter, jsonError } from "@/lib/agent-api/http";

describe("pageArgs", () => {
  it("defaults to page 1 size 20", () => {
    expect(pageArgs(new URLSearchParams())).toEqual({ page: 1, pageSize: 20, skip: 0, take: 20 });
  });
  it("caps pageSize at 100 and floors page at 1", () => {
    const sp = new URLSearchParams("page=0&pageSize=999");
    expect(pageArgs(sp)).toEqual({ page: 1, pageSize: 100, skip: 0, take: 100 });
  });
  it("computes skip", () => {
    const sp = new URLSearchParams("page=3&pageSize=10");
    expect(pageArgs(sp)).toEqual({ page: 3, pageSize: 10, skip: 20, take: 10 });
  });
});

describe("statusFilter", () => {
  it("forces published when no content:all", () => {
    expect(statusFilter(["content:published"], new URLSearchParams("status=draft"))).toEqual({
      status: "published",
      deletedAt: null,
    });
  });
  it("honors ?status= when content:all present", () => {
    const s = ["content:all"];
    expect(statusFilter(s, new URLSearchParams("status=draft"))).toEqual({
      status: "draft",
      deletedAt: null,
    });
    expect(statusFilter(s, new URLSearchParams("status=all"))).toEqual({});
    expect(statusFilter(s, new URLSearchParams())).toEqual({
      status: "published",
      deletedAt: null,
    });
  });
});

describe("jsonError", () => {
  it("returns status + {error}", async () => {
    const r = jsonError(403, "forbidden");
    expect(r.status).toBe(403);
    expect(await r.json()).toEqual({ error: "forbidden" });
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test http`
Expected: FAIL

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/http.ts`**

```ts
export interface PageArgs {
  page: number;
  pageSize: number;
  skip: number;
  take: number;
}

export function pageArgs(sp: URLSearchParams): PageArgs {
  const page = Math.max(1, Math.floor(Number(sp.get("page")) || 1));
  const pageSize = Math.min(100, Math.max(1, Math.floor(Number(sp.get("pageSize")) || 20)));
  return { page, pageSize, skip: (page - 1) * pageSize, take: pageSize };
}

/** 内容类查询的 status/deletedAt where 片段。无 content:all 时锁死 published。 */
export function statusFilter(
  scopes: string[],
  sp: URLSearchParams,
): { status?: string; deletedAt?: null } {
  if (!scopes.includes("content:all")) return { status: "published", deletedAt: null };
  const s = sp.get("status");
  if (s === "draft" || s === "archived" || s === "published") return { status: s, deletedAt: null };
  if (s === "all") return {};
  return { status: "published", deletedAt: null };
}

export function envelope(data: unknown[], total: number, page: number, pageSize: number): Response {
  return Response.json({ data, page, pageSize, total });
}

export function jsonError(status: number, error: string): Response {
  return Response.json({ error }, { status });
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test http`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/http.ts apps/admin/tests/http.test.ts
git commit -m "feat(admin): agent-api http helpers (paging/status/envelope/error)"
```

---

## Task 8: 内容资源 handler + manifest 条目

**Files:**
- Create: `apps/admin/lib/agent-api/queries.ts`
- Modify: `apps/admin/lib/agent-api/manifest.ts`(填充 `ENDPOINTS` 内容部分)
- Test: `apps/admin/tests/queries-content.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/queries-content.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { ENDPOINTS } from "@/lib/agent-api/manifest";

describe("content endpoints registered", () => {
  it("registers the expected content paths with content:published scope", () => {
    const paths = ENDPOINTS.map((e) => e.path);
    for (const p of [
      "/api/agent/v1/apps",
      "/api/agent/v1/apps/:slug",
      "/api/agent/v1/videos",
      "/api/agent/v1/videos/:slug",
      "/api/agent/v1/guides",
      "/api/agent/v1/guides/:slug",
      "/api/agent/v1/topics",
      "/api/agent/v1/topics/:slug",
      "/api/agent/v1/albums",
      "/api/agent/v1/albums/:slug",
      "/api/agent/v1/rankings",
      "/api/agent/v1/categories",
      "/api/agent/v1/tags",
    ]) {
      expect(paths).toContain(p);
    }
    expect(ENDPOINTS.find((e) => e.path === "/api/agent/v1/apps")?.scope).toBe(
      "content:published",
    );
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test queries-content`
Expected: FAIL（内容端点未注册,paths 不含这些）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/queries.ts`**

```ts
import { prisma } from "@ghome/db";
import type { AgentCtx } from "./manifest";
import { pageArgs, statusFilter, envelope, jsonError } from "./http";

/* ---------- 内容:列表 + 详情 ---------- */

export async function listApps(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const where = statusFilter(ctx.client.scopes, ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.app.findMany({
      where,
      skip,
      take,
      orderBy: { updatedAt: "desc" },
      select: { id: true, slug: true, name: true, shortDesc: true, status: true, categoryId: true, updatedAt: true },
    }),
    prisma.app.count({ where }),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function getApp(ctx: AgentCtx): Promise<Response> {
  const where = { slug: ctx.params.slug, ...statusFilter(ctx.client.scopes, ctx.searchParams) };
  const app = await prisma.app.findFirst({
    where,
    include: { category: true, tags: { include: { tag: true } } },
  });
  return app ? Response.json(app) : jsonError(404, "not_found");
}

export async function listVideos(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const where = statusFilter(ctx.client.scopes, ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.video.findMany({
      where,
      skip,
      take,
      orderBy: { updatedAt: "desc" },
      select: { id: true, slug: true, title: true, shortDesc: true, status: true, categoryId: true, updatedAt: true },
    }),
    prisma.video.count({ where }),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function getVideo(ctx: AgentCtx): Promise<Response> {
  const where = { slug: ctx.params.slug, ...statusFilter(ctx.client.scopes, ctx.searchParams) };
  const v = await prisma.video.findFirst({
    where,
    include: { category: true, tags: { include: { tag: true } } },
  });
  return v ? Response.json(v) : jsonError(404, "not_found");
}

export async function listGuides(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const where = statusFilter(ctx.client.scopes, ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.guide.findMany({
      where,
      skip,
      take,
      orderBy: { updatedAt: "desc" },
      select: { id: true, slug: true, title: true, summary: true, status: true, updatedAt: true },
    }),
    prisma.guide.count({ where }),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function getGuide(ctx: AgentCtx): Promise<Response> {
  const where = { slug: ctx.params.slug, ...statusFilter(ctx.client.scopes, ctx.searchParams) };
  const g = await prisma.guide.findFirst({ where });
  return g ? Response.json(g) : jsonError(404, "not_found");
}

/* ---------- collections:topic / album / ranking ---------- */

function collectionList(kind: "topic" | "album" | "ranking") {
  return async (ctx: AgentCtx): Promise<Response> => {
    const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
    const sf = statusFilter(ctx.client.scopes, ctx.searchParams);
    const where = { kind, ...sf };
    const [data, total] = await Promise.all([
      prisma.collection.findMany({
        where,
        skip,
        take,
        orderBy: { updatedAt: "desc" },
        select: { id: true, slug: true, title: true, status: true, kind: true, updatedAt: true },
      }),
      prisma.collection.count({ where }),
    ]);
    return envelope(data, total, page, pageSize);
  };
}

function collectionDetail(kind: "topic" | "album" | "ranking") {
  return async (ctx: AgentCtx): Promise<Response> => {
    const where = { kind, slug: ctx.params.slug, ...statusFilter(ctx.client.scopes, ctx.searchParams) };
    const c = await prisma.collection.findFirst({
      where,
      include: { items: { orderBy: { position: "asc" } } },
    });
    return c ? Response.json(c) : jsonError(404, "not_found");
  };
}

export const listTopics = collectionList("topic");
export const getTopic = collectionDetail("topic");
export const listAlbums = collectionList("album");
export const getAlbum = collectionDetail("album");
export const listRankings = collectionList("ranking");

export async function listCategories(): Promise<Response> {
  const data = await prisma.category.findMany({ orderBy: { slug: "asc" } });
  return Response.json({ data });
}

export async function listTags(): Promise<Response> {
  const data = await prisma.tag.findMany({ orderBy: { slug: "asc" } });
  return Response.json({ data });
}
```

> 注:`select` 字段以 `packages/db/prisma/schema.prisma` 现有列为准;若某字段名不符,以 schema 实际列名替换(如 `shortDesc`/`summary`/`title` 等),不要新增列。

- [ ] **Step 4: 在 `apps/admin/lib/agent-api/manifest.ts` 填充 `ENDPOINTS` 内容部分**

把文件末尾 `export const ENDPOINTS: AgentEndpoint[] = [];` 替换为:

```ts
import * as q from "./queries";

export const ENDPOINTS: AgentEndpoint[] = [
  { path: "/api/agent/v1/apps", method: "GET", scope: "content:published", summary: "App 列表(分页)", query: [{ name: "page", type: "int", desc: "页码,默认1" }, { name: "pageSize", type: "int", desc: "每页,默认20,上限100" }, { name: "status", type: "string", desc: "仅 content:all 生效:draft|archived|published|all" }], exampleResponse: { data: [{ id: "uuid", slug: "demo", name: "Demo", status: "published" }], page: 1, pageSize: 20, total: 1 }, handler: q.listApps },
  { path: "/api/agent/v1/apps/:slug", method: "GET", scope: "content:published", summary: "App 详情(含分类/标签)", exampleResponse: { id: "uuid", slug: "demo", name: "Demo" }, handler: q.getApp },
  { path: "/api/agent/v1/videos", method: "GET", scope: "content:published", summary: "视频列表(分页)", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listVideos },
  { path: "/api/agent/v1/videos/:slug", method: "GET", scope: "content:published", summary: "视频详情", exampleResponse: { id: "uuid", slug: "demo" }, handler: q.getVideo },
  { path: "/api/agent/v1/guides", method: "GET", scope: "content:published", summary: "指南列表(分页)", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listGuides },
  { path: "/api/agent/v1/guides/:slug", method: "GET", scope: "content:published", summary: "指南详情", exampleResponse: { id: "uuid", slug: "demo" }, handler: q.getGuide },
  { path: "/api/agent/v1/topics", method: "GET", scope: "content:published", summary: "专题列表", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listTopics },
  { path: "/api/agent/v1/topics/:slug", method: "GET", scope: "content:published", summary: "专题详情(含成员)", exampleResponse: { id: "uuid", slug: "demo" }, handler: q.getTopic },
  { path: "/api/agent/v1/albums", method: "GET", scope: "content:published", summary: "专辑列表", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listAlbums },
  { path: "/api/agent/v1/albums/:slug", method: "GET", scope: "content:published", summary: "专辑详情(含成员)", exampleResponse: { id: "uuid", slug: "demo" }, handler: q.getAlbum },
  { path: "/api/agent/v1/rankings", method: "GET", scope: "content:published", summary: "榜单列表", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listRankings },
  { path: "/api/agent/v1/categories", method: "GET", scope: "content:published", summary: "分类全集", exampleResponse: { data: [] }, handler: q.listCategories },
  { path: "/api/agent/v1/tags", method: "GET", scope: "content:published", summary: "标签全集", exampleResponse: { data: [] }, handler: q.listTags },
];
```

(把 `import * as q from "./queries";` 提到文件顶部 import 区。)

- [ ] **Step 5: 跑测试确认通过 + typecheck**

Run:
```bash
pnpm --filter @ghome/admin test queries-content
pnpm --filter @ghome/admin typecheck
```
Expected: 测试 PASS;typecheck 无错(若报某 `select` 字段不存在,按 schema 真实列名修正后再跑)

- [ ] **Step 6: Commit**

```bash
git add apps/admin/lib/agent-api/queries.ts apps/admin/lib/agent-api/manifest.ts apps/admin/tests/queries-content.test.ts
git commit -m "feat(admin): content resource handlers + manifest entries"
```

---

## Task 9: dispatcher route + 集成测试

> **Task 6 review carry-over:** `logAccess` 是 best-effort,写失败只打 `[agent-api][AUDIT-WRITE-FAILED]` 日志(已在 auth.ts 实现,生产侧应对该 tag 配告警)。本任务的集成测试必须实际断言:成功拉取写入一条 `status="ok"` 的 `AgentAccessLog`、`ops:*` 被拒写入 `status="denied"`(Task 11 覆盖 denied 路径)。dispatcher 调 `logAccess(client.id, pathname, ...)` 时传的是 `pathname`(已归一,非原始 URL),与 auth.ts 的 200 字符 clamp 双重兜底。

**Files:**
- Create: `apps/admin/app/api/agent/v1/[[...slug]]/route.ts`
- Test: `apps/admin/tests/dispatch.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/dispatch.test.ts`**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import { NextRequest } from "next/server";
import { GET } from "@/app/api/agent/v1/[[...slug]]/route";
import { generateToken, hashToken, tokenPrefix } from "@/lib/agent-api/token";

const PUB = generateToken();
const ALL = generateToken();
let adminId: string;
const ids: string[] = [];

beforeAll(async () => {
  const a = await prisma.adminUser.create({
    data: { email: `disp-${Date.now()}@x.io`, [敏感内容已脱敏] },
  });
  adminId = a.id;
  for (const [raw, scopes] of [
    [PUB, ["content:published"]],
    [ALL, ["content:all"]],
  ] as const) {
    const c = await prisma.agentClient.create({
      data: {
        name: `disp-${raw.slice(6, 14)}`,
        [敏感内容已脱敏],
        [敏感内容已脱敏],
        scopes: [...scopes],
        createdByAdminId: adminId,
      },
    });
    ids.push(c.id);
  }
});

afterAll(async () => {
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: { in: ids } } });
  await prisma.agentClient.deleteMany({ where: { id: { in: ids } } });
  await prisma.adminUser.delete({ where: { id: adminId } });
});

function call(path: string, token?: string) {
  const h = new Headers();
  if (token) h.set("authorization", `Bearer ${token}`);
  const req = new NextRequest(`http://localhost${path}`, { headers: h });
  const slug = path.replace(/^\/api\/agent\/v1\/?/, "").split("/").filter(Boolean);
  return GET(req, { params: Promise.resolve({ slug }) });
}

describe("dispatcher", () => {
  it("401 without token", async () => {
    expect((await call("/api/agent/v1/apps")).status).toBe(401);
  });
  it("404 unknown endpoint with valid token", async () => {
    expect((await call("/api/agent/v1/nope", PUB)).status).toBe(404);
  });
  it("403 when scope missing (content token hitting nothing it lacks)", async () => {
    // apps requires content:published which PUB has -> 200; verify ALL also works
    expect((await call("/api/agent/v1/apps", ALL)).status).toBe(200);
  });
  it("200 list shape for apps", async () => {
    const r = await call("/api/agent/v1/apps", PUB);
    expect(r.status).toBe(200);
    const j = await r.json();
    expect(j).toHaveProperty("data");
    expect(j).toHaveProperty("total");
  });
  it("published-only token cannot see drafts via ?status=draft (silently ignored)", async () => {
    const r = await call("/api/agent/v1/apps?status=draft", PUB);
    const j = await r.json();
    // 所有返回项必须是 published(若库中有 draft 数据,亦不应出现)
    for (const row of j.data) expect(row.status).toBe("published");
  });
  it("writes an ok access-log row", async () => {
    await call("/api/agent/v1/apps", PUB);
    const n = await prisma.agentAccessLog.count({
      where: { agentClientId: ids[0], status: "ok" },
    });
    expect(n).toBeGreaterThanOrEqual(1);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test dispatch`
Expected: FAIL（route 模块不存在）

- [ ] **Step 3: 实现 `apps/admin/app/api/agent/v1/[[...slug]]/route.ts`**

```ts
import type { NextRequest } from "next/server";
import { resolveAgentClient, logAccess, touchLastUsed } from "@/lib/agent-api/auth";
import { matchEndpoint, ENDPOINTS } from "@/lib/agent-api/manifest";
import { jsonError } from "@/lib/agent-api/http";
import { renderSkillMd } from "@/lib/agent-api/skill-md";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SKILL_PATH = "/api/agent/v1/skill.md";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ slug?: string[] }> },
): Promise<Response> {
  const { slug = [] } = await params;
  const pathname = "/api/agent/v1" + (slug.length ? "/" + slug.join("/") : "");

  const authed = await resolveAgentClient(req);
  if (!authed.ok) return jsonError(authed.status, authed.code);
  const client = authed.client;

  // Skill.md:任一有效 token 即可,按 scope 个性化
  if (pathname === SKILL_PATH) {
    void touchLastUsed(client);
    void logAccess(client.id, pathname, "ok");
    return new Response(renderSkillMd(client, ENDPOINTS), {
      headers: { "content-type": "text/markdown; charset=utf-8" },
    });
  }

  const match = matchEndpoint(pathname, "GET", ENDPOINTS);
  if (!match) return jsonError(404, "not_found");

  if (!client.scopes.includes(match.endpoint.scope)) {
    if (match.endpoint.scope.startsWith("ops:")) {
      void logAccess(client.id, pathname, "denied");
    }
    return jsonError(403, "forbidden");
  }

  void touchLastUsed(client);
  void logAccess(client.id, pathname, "ok");

  return match.endpoint.handler({
    req,
    params: match.params,
    client,
    searchParams: req.nextUrl.searchParams,
  });
}
```

> 依赖 `renderSkillMd`(Task 10)。先建占位 `apps/admin/lib/agent-api/skill-md.ts`:
> ```ts
> import type { AgentClient } from "@ghome/db";
> import type { AgentEndpoint } from "./manifest";
> export function renderSkillMd(_c: AgentClient, _e: AgentEndpoint[]): string {
>   return "# placeholder";
> }
> ```
> Task 10 用 TDD 实现真正内容。

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test dispatch`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/app/api/agent apps/admin/lib/agent-api/skill-md.ts apps/admin/tests/dispatch.test.ts
git commit -m "feat(admin): agent API catch-all dispatcher"
```

---

## Task 10: Skill.md 生成器

**Files:**
- Modify: `apps/admin/lib/agent-api/skill-md.ts`
- Test: `apps/admin/tests/skill-md.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/skill-md.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { renderSkillMd } from "@/lib/agent-api/skill-md";
import type { AgentEndpoint } from "@/lib/agent-api/manifest";
import type { AgentClient } from "@ghome/db";

const eps: AgentEndpoint[] = [
  { path: "/api/agent/v1/apps", method: "GET", scope: "content:published", summary: "App 列表", exampleResponse: { data: [] }, handler: async () => new Response() },
  { path: "/api/agent/v1/contact-submissions", method: "GET", scope: "ops:contacts", summary: "联系表单", exampleResponse: { data: [] }, handler: async () => new Response() },
];

function client(scopes: string[]): AgentClient {
  return { id: "c1", name: "x", scopes } as unknown as AgentClient;
}

describe("renderSkillMd", () => {
  it("includes only in-scope endpoints", () => {
    const md = renderSkillMd(client(["content:published"]), eps);
    expect(md).toContain("/api/agent/v1/apps");
    expect(md).not.toContain("/api/agent/v1/contact-submissions");
  });
  it("includes ops endpoint when scoped", () => {
    const md = renderSkillMd(client(["content:published", "ops:contacts"]), eps);
    expect(md).toContain("/api/agent/v1/contact-submissions");
  });
  it("has SKILL.md frontmatter and auth section", () => {
    const md = renderSkillMd(client(["content:published"]), eps);
    expect(md).toMatch(/^---\nname: ghome-admin-data/);
    expect(md).toContain("Authorization: Bearer");
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test skill-md`
Expected: FAIL（占位实现返回 "# placeholder"）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/skill-md.ts`**

```ts
import type { AgentClient } from "@ghome/db";
import type { AgentEndpoint } from "./manifest";

export function renderSkillMd(client: AgentClient, endpoints: AgentEndpoint[]): string {
  const visible = endpoints.filter((e) => client.scopes.includes(e.scope));

  const lines: string[] = [];
  lines.push("---");
  lines.push("name: ghome-admin-data");
  lines.push(
    "description: Pull Ghome admin data (content / analytics / ops) over a scoped read-only API",
  );
  lines.push("---");
  lines.push("");
  lines.push("# Ghome Admin Data API");
  lines.push("");
  lines.push(`Authorized as **${client.name}**. Granted scopes: ${client.scopes.join(", ")}.`);
  lines.push("");
  lines.push("## 鉴权");
  lines.push("");
  lines.push("每个请求带 header:");
  lines.push("");
  lines.push("```");
  lines.push("Authorization: Bearer <你的授权码>");
  lines.push("```");
  lines.push("");
  lines.push("## 约定");
  lines.push("");
  lines.push("- 全部 GET、只读、JSON。");
  lines.push("- 列表信封:`{ data, page, pageSize, total }`;`?page=&pageSize=`(pageSize≤100)。");
  lines.push("- 错误:`{ error }`,401 未授权 / 403 缺 scope / 404 未知端点 / 400 参数非法。");
  lines.push("");
  lines.push("## 可用端点");
  lines.push("");

  for (const e of visible) {
    lines.push(`### \`GET ${e.path}\``);
    lines.push("");
    lines.push(`${e.summary} (scope: \`${e.scope}\`)`);
    lines.push("");
    if (e.query?.length) {
      lines.push("查询参数:");
      for (const qp of e.query) lines.push(`- \`${qp.name}\` (${qp.type}) — ${qp.desc}`);
      lines.push("");
    }
    lines.push("示例响应:");
    lines.push("");
    lines.push("```json");
    lines.push(JSON.stringify(e.exampleResponse, null, 2));
    lines.push("```");
    lines.push("");
  }

  return lines.join("\n");
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test skill-md`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/skill-md.ts apps/admin/tests/skill-md.test.ts
git commit -m "feat(admin): scope-personalized Skill.md generator"
```

---

## Task 11: 分析/运营 handler + manifest 条目

> **Task 9 review carry-over (do these in this task's test work):**
> 1. `apps/admin/tests/dispatch.test.ts` 里那条名为 `"403 when scope missing"` 但实际断言 200 的用例名不副实 —— Task 11 引入 `ops:*` 端点后,**改/补一条真正的跨 scope 403 用例**:一个仅持 `content:published` 的 token 访问某 `ops:*` 端点 → 断言 403,且 `AgentAccessLog` 写入一条 `status="denied"` 行(验证 spec §5/§10 的 ops:* denied 记录策略)。可在 `queries-ops.test.ts` 里实现(已规划)。
> 2. dispatcher 的 `?status=draft` 用例在库无 draft 数据时是空断言 —— 在 ops/denied 测试的 `beforeAll` 里**额外 seed 一条 draft App**,断言 `content:published` token 看不到它、`content:all` token 能看到,给"草稿不泄露"边界以实证(测完在 afterAll 清理)。
> 3. 已确认的设计决策(无需改动):denied 仅对 `ops:*` 记日志是 spec §5/§10 的刻意选择(只审计敏感面尝试,避免良性 content scope 不匹配刷屏),保持不变。

**Files:**
- Modify: `apps/admin/lib/agent-api/queries.ts`(追加)
- Modify: `apps/admin/lib/agent-api/manifest.ts`(追加条目)
- Test: `apps/admin/tests/queries-ops.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/queries-ops.test.ts`**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import { NextRequest } from "next/server";
import { GET } from "@/app/api/agent/v1/[[...slug]]/route";
import { generateToken, hashToken, tokenPrefix } from "@/lib/agent-api/token";

const ADMINS = generateToken();
const NOSCOPE = generateToken();
let adminId: string;
const ids: string[] = [];

beforeAll(async () => {
  const a = await prisma.adminUser.create({
    data: { email: `ops-${Date.now()}@x.io`, [敏感内容已脱敏] },
  });
  adminId = a.id;
  for (const [raw, scopes] of [
    [ADMINS, ["ops:admins"]],
    [NOSCOPE, ["content:published"]],
  ] as const) {
    const c = await prisma.agentClient.create({
      data: {
        name: `ops-${raw.slice(6, 14)}`,
        [敏感内容已脱敏],
        [敏感内容已脱敏],
        scopes: [...scopes],
        createdByAdminId: adminId,
      },
    });
    ids.push(c.id);
  }
});

afterAll(async () => {
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: { in: ids } } });
  await prisma.agentClient.deleteMany({ where: { id: { in: ids } } });
  await prisma.adminUser.delete({ where: { id: adminId } });
});

function call(path: string, 敏感凭据：[已脱敏] {
  const h = new Headers({ authorization: `Bearer ${token}` });
  const req = new NextRequest(`http://localhost${path}`, { headers: h });
  const slug = path.replace(/^\/api\/agent\/v1\/?/, "").split("/").filter(Boolean);
  return GET(req, { params: Promise.resolve({ slug }) });
}

describe("ops endpoints", () => {
  it("/admins returns rows WITHOUT passwordHash", async () => {
    const r = await call("/api/agent/v1/admins", ADMINS);
    expect(r.status).toBe(200);
    const j = await r.json();
    const all = JSON.stringify(j);
    expect(all).not.toContain("passwordHash");
    expect(all).not.toContain("secret-hash");
  });

  it("missing ops scope -> 403 and writes denied access-log", async () => {
    const r = await call("/api/agent/v1/admins", NOSCOPE);
    expect(r.status).toBe(403);
    const n = await prisma.agentAccessLog.count({
      where: { agentClientId: ids[1], status: "denied" },
    });
    expect(n).toBeGreaterThanOrEqual(1);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test queries-ops`
Expected: FAIL（/admins 未注册 → 404,断言失败）

- [ ] **Step 3: 在 `apps/admin/lib/agent-api/queries.ts` 末尾追加**

```ts
/* ---------- 分析 ---------- */

export async function analyticsClicksDaily(ctx: AgentCtx): Promise<Response> {
  const days = Math.min(90, Math.max(1, Math.floor(Number(ctx.searchParams.get("days")) || 7)));
  const since = new Date();
  since.setUTCDate(since.getUTCDate() - (days - 1));
  since.setUTCHours(0, 0, 0, 0);
  const rows = await prisma.$queryRaw<Array<{ day: Date; count: bigint }>>`
    SELECT date_trunc('day', ts AT TIME ZONE 'UTC')::date AS day, count(*) AS count
    FROM click_events
    WHERE ts >= ${since}
    GROUP BY 1
    ORDER BY 1 ASC
  `;
  return Response.json({
    data: rows.map((r) => ({ day: r.day.toISOString().slice(0, 10), count: Number(r.count) })),
  });
}

export async function analyticsTopRedirects(ctx: AgentCtx): Promise<Response> {
  const limit = Math.min(100, Math.max(1, Math.floor(Number(ctx.searchParams.get("limit")) || 20)));
  const rows = await prisma.$queryRaw<
    Array<{ redirect_id: string; owner_kind: string; owner_id: string | null; target_url: string; disabled: boolean; clicks: bigint }>
  >`
    SELECT r.id AS redirect_id, r.owner_kind, r.owner_id, r.target_url, r.disabled, count(c.id) AS clicks
    FROM redirects r
    LEFT JOIN click_events c ON c.redirect_id = r.id
    GROUP BY r.id
    ORDER BY clicks DESC
    LIMIT ${limit}
  `;
  return Response.json({
    data: rows.map((r) => ({
      redirectId: r.redirect_id,
      ownerKind: r.owner_kind,
      ownerId: r.owner_id,
      targetUrl: r.target_url,
      disabled: r.disabled,
      clicks: Number(r.clicks),
    })),
  });
}

/* ---------- 运营 ---------- */

export async function listRedirectsApi(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.redirect.findMany({
      skip,
      take,
      orderBy: { createdAt: "desc" },
      select: { id: true, ownerKind: true, ownerId: true, targetUrl: true, disabled: true, createdAt: true },
    }),
    prisma.redirect.count(),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function listAuditLog(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.auditLogEntry.findMany({
      skip,
      take,
      orderBy: { ts: "desc" },
      select: { id: true, adminUserId: true, action: true, targetType: true, targetId: true, ts: true },
    }),
    prisma.auditLogEntry.count(),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function listContactSubmissions(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.contactSubmission.findMany({
      skip,
      take,
      orderBy: { createdAt: "desc" },
      select: { id: true, email: true, name: true, subject: true, body: true, status: true, createdAt: true, repliedAt: true },
    }),
    prisma.contactSubmission.count(),
  ]);
  return envelope(data, total, page, pageSize);
}

export async function listAdmins(ctx: AgentCtx): Promise<Response> {
  const { page, pageSize, skip, take } = pageArgs(ctx.searchParams);
  const [data, total] = await Promise.all([
    prisma.adminUser.findMany({
      skip,
      take,
      orderBy: { createdAt: "desc" },
      // 字段白名单:绝不含 passwordHash
      select: { id: true, email: true, name: true, lastLoginAt: true },
    }),
    prisma.adminUser.count(),
  ]);
  return envelope(data, total, page, pageSize);
}
```

- [ ] **Step 4: 在 `apps/admin/lib/agent-api/manifest.ts` 的 `ENDPOINTS` 数组(内容条目之后、`]` 之前)追加**

```ts
  { path: "/api/agent/v1/analytics/clicks/daily", method: "GET", scope: "analytics:read", summary: "每日点击趋势", query: [{ name: "days", type: "int", desc: "回溯天数,默认7,上限90" }], exampleResponse: { data: [{ day: "2026-05-18", count: 12 }] }, handler: q.analyticsClicksDaily },
  { path: "/api/agent/v1/analytics/redirects/top", method: "GET", scope: "analytics:read", summary: "热门 redirect", query: [{ name: "limit", type: "int", desc: "默认20,上限100" }], exampleResponse: { data: [] }, handler: q.analyticsTopRedirects },
  { path: "/api/agent/v1/redirects", method: "GET", scope: "ops:redirects", summary: "redirect 列表(含 target)", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listRedirectsApi },
  { path: "/api/agent/v1/audit-log", method: "GET", scope: "ops:audit", summary: "管理操作审计日志", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listAuditLog },
  { path: "/api/agent/v1/contact-submissions", method: "GET", scope: "ops:contacts", summary: "联系表单提交(含 PII)", exampleResponse: { data: [], page: 1, pageSize: 20, total: 0 }, handler: q.listContactSubmissions },
  { path: "/api/agent/v1/admins", method: "GET", scope: "ops:admins", summary: "管理员账号(无 passwordHash)", exampleResponse: { data: [{ id: "uuid", email: "[邮箱已脱敏]", name: null, lastLoginAt: null }], page: 1, pageSize: 20, total: 1 }, handler: q.listAdmins },
```

- [ ] **Step 5: 跑测试确认通过 + typecheck**

Run:
```bash
pnpm --filter @ghome/admin test queries-ops
pnpm --filter @ghome/admin typecheck
```
Expected: PASS;typecheck 无错(`select` 字段若与 schema 不符,以真实列名修正)

- [ ] **Step 6: Commit**

```bash
git add apps/admin/lib/agent-api/queries.ts apps/admin/lib/agent-api/manifest.ts apps/admin/tests/queries-ops.test.ts
git commit -m "feat(admin): analytics + ops endpoints (admins whitelist, denied logging)"
```

---

## Task 12: AgentClient DB 辅助

**Files:**
- Create: `apps/admin/lib/agent-clients-db.ts`
- Test: `apps/admin/tests/agent-clients-db.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/agent-clients-db.test.ts`**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import {
  createAgentClient,
  listAgentClients,
  rotateAgentToken,
  updateAgentClient,
  deleteAgentClient,
} from "@/lib/agent-clients-db";

let adminId: string;

beforeAll(async () => {
  const a = await prisma.adminUser.create({
    data: { email: `acdb-${Date.now()}@x.io`, [敏感内容已脱敏] },
  });
  adminId = a.id;
});
afterAll(async () => {
  await prisma.agentClient.deleteMany({ where: { createdByAdminId: adminId } });
  await prisma.adminUser.delete({ where: { id: adminId } });
});

describe("agent-clients-db", () => {
  it("create returns raw token once and stores only hash", async () => {
    const { rawToken, client } = await createAgentClient({
      name: `acdb-${Date.now()}`,
      scopes: ["content:published"],
      createdByAdminId: adminId,
    });
    expect(rawToken).toMatch(/^ghagt_/);
    const row = await prisma.agentClient.findUnique({ where: { id: client.id } });
    expect(row?.tokenHash).not.toContain(rawToken);
    expect(row?.scopes).toEqual(["content:published"]);
  });

  it("rejects invalid scope", async () => {
    await expect(
      createAgentClient({ name: `bad-${Date.now()}`, scopes: ["ops:secret"], createdByAdminId: adminId }),
    ).rejects.toThrow();
  });

  it("rotate changes tokenHash, invalidates old", async () => {
    const { client } = await createAgentClient({
      name: `rot-${Date.now()}`,
      scopes: ["content:published"],
      createdByAdminId: adminId,
    });
    const before = (await prisma.agentClient.findUnique({ where: { id: client.id } }))!.tokenHash;
    const { rawToken } = await rotateAgentToken(client.id);
    const after = (await prisma.agentClient.findUnique({ where: { id: client.id } }))!.tokenHash;
    expect(after).not.toBe(before);
    expect(rawToken).toMatch(/^ghagt_/);
  });

  it("update toggles disabled / scopes; list returns it; delete removes", async () => {
    const { client } = await createAgentClient({
      name: `upd-${Date.now()}`,
      scopes: ["content:published"],
      createdByAdminId: adminId,
    });
    await updateAgentClient(client.id, { disabled: true, scopes: ["content:all"] });
    const got = (await listAgentClients()).find((c) => c.id === client.id);
    expect(got?.disabled).toBe(true);
    expect(got?.scopes).toEqual(["content:all"]);
    await deleteAgentClient(client.id);
    expect(await prisma.agentClient.findUnique({ where: { id: client.id } })).toBeNull();
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test agent-clients-db`
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `apps/admin/lib/agent-clients-db.ts`**

```ts
import { prisma } from "@ghome/db";
import type { AgentClient } from "@ghome/db";
import { generateToken, hashToken, tokenPrefix } from "./agent-api/token";
import { isValidScope } from "./agent-api/scopes";

function assertScopes(scopes: string[]) {
  for (const s of scopes) {
    if (!isValidScope(s)) throw new Error(`invalid scope: ${s}`);
  }
}

export async function createAgentClient(input: {
  name: string;
  scopes: string[];
  createdByAdminId: string;
  expiresAt?: Date | null;
  note?: string | null;
}): Promise<{ [敏感内容已脱敏]; client: AgentClient }> {
  assertScopes(input.scopes);
  const [敏感内容已脱敏];
  const client = await prisma.agentClient.create({
    data: {
      name: input.name,
      [敏感内容已脱敏],
      [敏感内容已脱敏],
      scopes: input.scopes,
      createdByAdminId: input.createdByAdminId,
      expiresAt: input.expiresAt ?? null,
      note: input.note ?? null,
    },
  });
  return { rawToken, client };
}

export function listAgentClients(): Promise<AgentClient[]> {
  return prisma.agentClient.findMany({ orderBy: { createdAt: "desc" } });
}

export function getAgentClient(id: string): Promise<AgentClient | null> {
  return prisma.agentClient.findUnique({ where: { id } });
}

export async function rotateAgentToken(
  id: string,
): Promise<{ [敏感内容已脱敏]; client: AgentClient }> {
  const [敏感内容已脱敏];
  const client = await prisma.agentClient.update({
    where: { id },
    data: { [敏感内容已脱敏], [敏感内容已脱敏] },
  });
  return { rawToken, client };
}

export async function updateAgentClient(
  id: string,
  patch: { disabled?: boolean; scopes?: string[]; expiresAt?: Date | null; note?: string | null },
): Promise<AgentClient> {
  if (patch.scopes) assertScopes(patch.scopes);
  return prisma.agentClient.update({ where: { id }, data: patch });
}

export async function deleteAgentClient(id: string): Promise<void> {
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: id } });
  await prisma.agentClient.delete({ where: { id } });
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm --filter @ghome/admin test agent-clients-db`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-clients-db.ts apps/admin/tests/agent-clients-db.test.ts
git commit -m "feat(admin): AgentClient db helpers (create/list/rotate/update/delete)"
```

---

## Task 13: Admin UI 页面 + server actions + 导航

**Files:**
- Create: `apps/admin/app/(admin)/agent-clients/actions.ts`
- Create: `apps/admin/app/(admin)/agent-clients/page.tsx`
- Create: `apps/admin/app/(admin)/agent-clients/new/page.tsx`
- Create: `apps/admin/app/(admin)/agent-clients/[id]/edit/page.tsx`
- Create: `apps/admin/components/TokenRevealBanner.tsx`
- Modify: `apps/admin/app/(admin)/layout.tsx`(侧边栏入口)

> 实现前先 `Read` 一个现有同类页面作风格基准:`apps/admin/app/(admin)/redirects/page.tsx`、`apps/admin/app/(admin)/redirects/new/page.tsx`、`apps/admin/components/ListTable.tsx`、`apps/admin/lib/audit.ts`、`apps/admin/lib/auth.ts`(取 `session.user.adminUserId` 的方式)。匹配既有 server action + 表单写法,不引入新模式。

- [ ] **Step 1: 创建 `apps/admin/app/(admin)/agent-clients/actions.ts`**

```ts
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { logAuditAction } from "@/lib/audit";
import {
  createAgentClient,
  rotateAgentToken,
  updateAgentClient,
  deleteAgentClient,
} from "@/lib/agent-clients-db";
import { ALL_SCOPES } from "@/lib/agent-api/scopes";

async function adminId(): Promise<string> {
  const session = await auth();
  const id = session?.user?.adminUserId;
  if (!id) throw new Error("unauthorized");
  return id;
}

function pickScopes(form: FormData): string[] {
  return ALL_SCOPES.filter((s) => form.get(`scope:${s}`) === "on");
}

export async function createAction(form: FormData): Promise<void> {
  const me = await adminId();
  const name = String(form.get("name") ?? "").trim();
  const note = String(form.get("note") ?? "").trim() || null;
  const expRaw = String(form.get("expiresAt") ?? "").trim();
  if (!name) throw new Error("name required");
  const { rawToken, client } = await createAgentClient({
    name,
    scopes: pickScopes(form),
    createdByAdminId: me,
    expiresAt: expRaw ? new Date(expRaw) : null,
    note,
  });
  await logAuditAction(me, "agentClient.create", "agentClient", client.id, {
    after: { name: client.name, scopes: client.scopes },
  });
  revalidatePath("/agent-clients");
  redirect(`/agent-clients/${client.id}/edit?敏感凭据：[已脱敏]
}

export async function rotateAction(id: string): Promise<void> {
  const me = await adminId();
  const { rawToken } = await rotateAgentToken(id);
  await logAuditAction(me, "agentClient.rotate", "agentClient", id, { after: { rotated: true } });
  revalidatePath(`/agent-clients/${id}/edit`);
  redirect(`/agent-clients/${id}/edit?敏感凭据：[已脱敏]
}

export async function updateAction(id: string, form: FormData): Promise<void> {
  const me = await adminId();
  const disabled = form.get("disabled") === "on";
  const expRaw = String(form.get("expiresAt") ?? "").trim();
  const client = await updateAgentClient(id, {
    disabled,
    scopes: pickScopes(form),
    expiresAt: expRaw ? new Date(expRaw) : null,
    note: String(form.get("note") ?? "").trim() || null,
  });
  await logAuditAction(me, "agentClient.update", "agentClient", id, {
    after: { disabled: client.disabled, scopes: client.scopes },
  });
  revalidatePath("/agent-clients");
  redirect("/agent-clients");
}

export async function deleteAction(id: string): Promise<void> {
  const me = await adminId();
  await deleteAgentClient(id);
  await logAuditAction(me, "agentClient.revoke", "agentClient", id, { after: { deleted: true } });
  revalidatePath("/agent-clients");
  redirect("/agent-clients");
}
```

- [ ] **Step 2: 创建 `apps/admin/components/TokenRevealBanner.tsx`**

```tsx
"use client";

import { useState } from "react";

export function TokenRevealBanner({ token }: { 敏感凭据：[已脱敏] }) {
  const [copied, setCopied] = useState(false);
  return (
    <div
      style={{
        border: "1px solid #c8860d",
        background: "#fff8e6",
        padding: "12px 16px",
        borderRadius: 8,
        margin: "16px 0",
      }}
    >
      <strong>授权码(仅此一次显示,关闭后不可再查看)</strong>
      <pre style={{ userSelect: "all", margin: "8px 0", overflowX: "auto" }}>{token}</pre>
      <button
        type="button"
        onClick={() => {
          navigator.clipboard.writeText(token).then(() => setCopied(true));
        }}
      >
        {copied ? "已复制" : "复制"}
      </button>
    </div>
  );
}
```

- [ ] **Step 3: 创建列表页 `apps/admin/app/(admin)/agent-clients/page.tsx`**

```tsx
import Link from "next/link";
import { listAgentClients } from "@/lib/agent-clients-db";

export const dynamic = "force-dynamic";

export default async function AgentClientsPage() {
  const clients = await listAgentClients();
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Agent 接入</h1>
        <Link href="/agent-clients/new">+ 新建</Link>
      </div>
      <table style={{ width: "100%", marginTop: 16 }}>
        <thead>
          <tr>
            <th>名称</th><th>Token 前缀</th><th>Scopes</th><th>状态</th><th>最近使用</th><th>过期</th><th></th>
          </tr>
        </thead>
        <tbody>
          {clients.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td><code>{c.tokenPrefix}…</code></td>
              <td>{c.scopes.join(", ")}</td>
              <td>{c.disabled ? "已停用" : "启用"}</td>
              <td>{c.lastUsedAt ? c.lastUsedAt.toISOString().slice(0, 16) : "—"}</td>
              <td>{c.expiresAt ? c.expiresAt.toISOString().slice(0, 10) : "—"}</td>
              <td><Link href={`/agent-clients/${c.id}/edit`}>编辑</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 4: 创建新建页 `apps/admin/app/(admin)/agent-clients/new/page.tsx`**

```tsx
import { ALL_SCOPES } from "@/lib/agent-api/scopes";
import { createAction } from "../actions";

export default function NewAgentClientPage() {
  return (
    <div>
      <h1>新建 Agent</h1>
      <form action={createAction}>
        <p><label>名称 <input name="name" required /></label></p>
        <p><label>过期(可选) <input name="expiresAt" type="date" /></label></p>
        <p><label>备注 <input name="note" /></label></p>
        <fieldset>
          <legend>授权范围</legend>
          {ALL_SCOPES.map((s) => (
            <label key={s} style={{ display: "block" }}>
              <input type="checkbox" name={`scope:${s}`} /> {s}
            </label>
          ))}
        </fieldset>
        <button type="submit">创建并生成授权码</button>
      </form>
    </div>
  );
}
```

- [ ] **Step 5: 创建编辑页 `apps/admin/app/(admin)/agent-clients/[id]/edit/page.tsx`**

```tsx
import { notFound } from "next/navigation";
import { ALL_SCOPES } from "@/lib/agent-api/scopes";
import { getAgentClient } from "@/lib/agent-clients-db";
import { TokenRevealBanner } from "@/components/TokenRevealBanner";
import { updateAction, rotateAction, deleteAction } from "../../actions";

export const dynamic = "force-dynamic";

export default async function EditAgentClientPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ token?: string }>;
}) {
  const { id } = await params;
  const { token } = await searchParams;
  const c = await getAgentClient(id);
  if (!c) notFound();

  const updateBound = updateAction.bind(null, id);
  const rotateBound = rotateAction.bind(null, id);
  const deleteBound = deleteAction.bind(null, id);

  return (
    <div>
      <h1>编辑 Agent — {c.name}</h1>
      {token ? <TokenRevealBanner 敏感凭据：[已脱敏] /> : null}

      <form action={updateBound}>
        <p>
          <label>
            <input type="checkbox" name="disabled" defaultChecked={c.disabled} /> 停用
          </label>
        </p>
        <p>
          <label>过期 <input name="expiresAt" type="date" defaultValue={c.expiresAt ? c.expiresAt.toISOString().slice(0, 10) : ""} /></label>
        </p>
        <p><label>备注 <input name="note" defaultValue={c.note ?? ""} /></label></p>
        <fieldset>
          <legend>授权范围</legend>
          {ALL_SCOPES.map((s) => (
            <label key={s} style={{ display: "block" }}>
              <input type="checkbox" name={`scope:${s}`} defaultChecked={c.scopes.includes(s)} /> {s}
            </label>
          ))}
        </fieldset>
        <button type="submit">保存</button>
      </form>

      <form action={rotateBound} style={{ marginTop: 16 }}>
        <button type="submit">轮换授权码(旧码立即失效)</button>
      </form>

      <form action={deleteBound} style={{ marginTop: 16 }}>
        <button type="submit" style={{ color: "crimson" }}>删除该 Agent</button>
      </form>
    </div>
  );
}
```

- [ ] **Step 6: 在 `apps/admin/app/(admin)/layout.tsx` 侧边栏加入口**

`Read` 该文件,找到现有导航链接列表(如指向 `/redirects` / `/audit-log` 的 `<Link>` 组),仿照同一写法新增一条:
```tsx
<Link href="/agent-clients">Agent 接入</Link>
```
（位置:放在 `审计日志 / audit-log` 链接之后,保持与既有项相同的标签/className。）

- [ ] **Step 7: typecheck + 构建验证**

Run:
```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
```
Expected: 均无错误

- [ ] **Step 8: Commit**

```bash
git add apps/admin/app/\(admin\)/agent-clients apps/admin/components/TokenRevealBanner.tsx apps/admin/app/\(admin\)/layout.tsx
git commit -m "feat(admin): agent-clients management UI (issue/rotate/revoke + one-time token reveal)"
```

---

## Task 14: E2E — 签发→展示→拉取→吊销

**Files:**
- Create: `apps/admin/playwright.config.ts`(若不存在;镜像 `apps/web/playwright.config.ts`,`PORT=3100`)
- Create: `apps/admin/e2e/agent-clients.spec.ts`
- Modify: `apps/admin/package.json`(加 `"e2e": "playwright test"` 脚本 + `@playwright/test` devDep,若缺)
- Modify: `.github/workflows/ci.yml`(可选:加 admin e2e 步骤,与 web e2e 同段)

> 先 `Read` `apps/web/playwright.config.ts` 作模板;admin 端口 3100;`webServer` 命令用 `pnpm --filter @ghome/admin dev`。登录态:E2E 里先走 `/signin` 用种子管理员账号(见 `packages/db/seed/data/admin-users.ts` 的 email/明文口令)登入,再操作。

- [ ] **Step 1: 写 E2E `apps/admin/e2e/agent-clients.spec.ts`**

```ts
import { test, expect } from "@playwright/test";

// 种子管理员凭据(见 packages/db/seed/data/admin-users.ts)
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL ?? "[邮箱已脱敏]";
const [敏感内容已脱敏] ?? "admin12345";
const BASE = process.env.ADMIN_BASE_URL ?? "http://localhost:3100";

test("issue → reveal once → pull data → revoke → 401", async ({ page, request }) => {
  await page.goto(`${BASE}/signin`);
  await page.getByLabel(/邮箱|email/i).fill(ADMIN_EMAIL);
  await page.getByLabel(/密码|password/i).fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: /登录|sign in/i }).click();

  await page.goto(`${BASE}/agent-clients/new`);
  const name = `e2e-${Date.now()}`;
  await page.getByLabel("名称").fill(name);
  await page.getByText("content:published").click();
  await page.getByRole("button", { name: /创建并生成授权码/ }).click();

  const [敏感内容已脱敏] page.locator("pre").first().innerText();
  expect(tokenText).toMatch(/^ghagt_/);

  // 用授权码拉数据 → 200
  const ok = await request.get(`${BASE}/api/agent/v1/apps`, {
    headers: { authorization: `Bearer ${tokenText}` },
  });
  expect(ok.status()).toBe(200);

  // 删除该 Agent → 同一 token 立即 401
  await page.getByRole("button", { name: /删除该 Agent/ }).click();
  const dead = await request.get(`${BASE}/api/agent/v1/apps`, {
    headers: { authorization: `Bearer ${tokenText}` },
  });
  expect(dead.status()).toBe(401);
});
```

> 种子管理员的真实 email/口令以 `packages/db/seed/data/admin-users.ts` 为准;`Read` 该文件后把上面默认值替换为真实值(或通过 `E2E_ADMIN_EMAIL`/`E2E_ADMIN_PASSWORD` env 注入)。`getByLabel` 的文案以 `apps/admin/app/(auth)/signin/page.tsx` 实际标签为准。

- [ ] **Step 2: 跑 E2E(本地需先 `docker compose up -d` 并已 seed)**

Run: `pnpm --filter @ghome/admin exec playwright test`
Expected: 1 passed

- [ ] **Step 3: Commit**

```bash
git add apps/admin/e2e apps/admin/playwright.config.ts apps/admin/package.json pnpm-lock.yaml .github/workflows/ci.yml
git commit -m "test(admin): e2e — issue/reveal/pull/revoke agent token"
```

---

## Final: 全量验证

- [ ] **Step 1: 全套测试 + 构建**

Run:
```bash
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin test
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
pnpm lint
```
Expected: 全绿

- [ ] **Step 2: 手工冒烟(本地 `docker compose up -d` 后)**

```bash
# 在 admin UI 新建一个带 content:published + ops:contacts 的 Agent,复制 token
敏感凭据：[已脱敏]
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:3100/api/agent/v1/skill.md | head -40
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:3100/api/agent/v1/apps?pageSize=2" | jq .
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" http://localhost:3100/api/agent/v1/audit-log   # 期望 403(无 ops:audit)
```
Expected: skill.md 含 apps 与 contact-submissions、不含 audit-log;apps 返回信封;audit-log 返回 403。

---

## Self-Review(规划者已执行)

- **Spec 覆盖**:§2 数据模型→Task1;§3 scopes→Task3;§4 manifest→Task5/8/11;§5 鉴权→Task6+Task9;§6 端点清单→Task8(内容)+Task11(分析/运营);§7 响应约定→Task7;§8 Skill.md→Task10;§9 Admin UI→Task13;§10 安全→Task6/11(白名单、denied 日志);§11 测试→各 Task TDD + Task14 E2E;§12 分阶段→A1/A2/A3/A5 对应。**A4(Skill.md)并入 A2 的 Task10**(dispatcher 需要它),已在阶段标题注明。
- **占位符扫描**:无 TODO/TBD;每步含完整代码与命令;`select` 字段处给出"以 schema 真实列名为准"的明确兜底,非占位。
- **类型一致性**:`AgentScope`/`ALL_SCOPES`/`isValidScope`、`generateToken`/`hashToken`/`tokenPrefix`、`AgentCtx`/`AgentEndpoint`/`ENDPOINTS`/`matchEndpoint`、`resolveAgentClient`/`AuthResult`/`logAccess`/`touchLastUsed`、`pageArgs`/`statusFilter`/`envelope`/`jsonError`、`renderSkillMd`、`createAgentClient`/`listAgentClients`/`getAgentClient`/`rotateAgentToken`/`updateAgentClient`/`deleteAgentClient` 跨任务签名一致。
- **已知留待实现期确认**:各 `prisma.*.findMany({ select })` 的字段名需对照 `schema.prisma` 真实列(App/Video/Guide/Collection/Redirect/ContactSubmission);种子管理员凭据与 signin 表单标签文案以源码为准。这些在对应 Step 已显式标注校正动作。
