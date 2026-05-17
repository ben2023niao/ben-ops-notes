---
id: "doc-d15b78a42f10"
title: "Agent 自助配对 Implementation Plan"
date: "2026-05-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "安全运维", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-self-pairing.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-self-pairing.md"
sourceSha256: "1982eba7d5b9080c73295f02f7828bd0d4380bea9946f7b7214c3ffacbaa42b0"
sourceSystem: "project-doc"
---

# Agent 自助配对 Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-self-pairing.md`

> 整理日期：2026-05-18 00:00｜日期依据：文件名日期

> **历史 plan(已执行)。公开端点路径已迁移**:`GET /agent/skill.md` + `POST /agent/pair`(原 `/api/agent/v1/pair*` 已移除)。本文内 `/api/agent/v1/pair*` 引用为执行时旧值,**以 spec §4/§5 的最终路径为准**,勿照搬。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一条公开自助配对通道:固定 URL 的引导版 Skill.md 每次被读即铸一次性短 TTL 配对码,Agent 凭码 `POST` 自助换取仅 `content:published` 的 Bearer token;管理员可一键开关通道、事后提权/吊销。

**Architecture:** 复用现有 `apps/admin/lib/agent-api/*` 的 token/scope/dispatcher 与 agent-clients UI。新增 `AgentPairingCode`/`AgentPairingConfig` 表与 `AgentClient.origin` 列,在 catch-all dispatcher 顶端 pre-auth 特判两个公开端点(GET 引导 / POST 兑换),自助配对出的 client 固定安全 scope,提权复用既有编辑页。

**Tech Stack:** Next.js 15 App Router (Route Handlers + Server Actions)、Prisma 5、Postgres、vitest、Playwright。

**Spec:** [docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md](../specs/2026-05-18-agent-self-pairing-design.md)(原 API spec:[2026-05-18-admin-agent-data-api-design.md](../specs/2026-05-18-admin-agent-data-api-design.md))

---

## File Structure

**新建**
- `apps/admin/lib/agent-api/pairing.ts` — 配对码生成/前缀、TTL 常量(复用 token.ts 的 hashToken)
- `apps/admin/lib/agent-api/pairing-skill-md.ts` — 引导版 Skill.md 渲染(开/关两态)
- `apps/admin/lib/agent-pairing-db.ts` — config 读写、铸码、兑换、码列表
- `apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx` — 只读配对码日志子页
- `apps/admin/tests/pairing.test.ts`、`pairing-db.test.ts`、`pair-endpoints.test.ts` — 测试

**修改**
- `packages/db/prisma/schema.prisma` — `AgentPairingCode`/`AgentPairingConfig` model;`AgentClient` 加 `origin`、`createdByAdminId` 改可空 + 反向关系
- `packages/db/src/index.ts` — 重导出 `AgentPairingCode`/`AgentPairingConfig`
- `apps/admin/lib/agent-api/scopes.ts` — 加 `SELF_PAIR_DEFAULT_SCOPES`
- `apps/admin/app/api/agent/v1/[[...slug]]/route.ts` — pre-auth 特判两个公开端点 + 新增 `POST` 导出
- `apps/admin/app/(admin)/agent-clients/page.tsx` — 加 `来源` 列 + 公开配对通道开关面板 + 配对码日志入口
- `apps/admin/app/(admin)/agent-clients/actions.ts` — 加 `setPairingChannelAction`
- `apps/admin/e2e/agent-clients.spec.ts` — 扩 E2E:免鉴权抓码 → 兑换 → 用 token

---

## Task 1: Prisma 模型 + 迁移 + 类型重导出

**Files:**
- Modify: `packages/db/prisma/schema.prisma`
- Modify: `packages/db/src/index.ts`
- Create: `packages/db/prisma/migrations/20260518100000_agent_self_pairing/migration.sql`(diff 生成 + 手工追加 seed)

- [ ] **Step 1: 在 `packages/db/prisma/schema.prisma` 末尾追加两个 model**

```prisma
model AgentPairingCode {
  id                  String   @id @default(uuid()) @db.Uuid
  codePrefix          String   @map("code_prefix")
  codeHash            String   @unique @map("code_hash")
  expiresAt           DateTime @map("expires_at") @db.Timestamptz(6)
  usedAt              DateTime? @map("used_at") @db.Timestamptz(6)
  usedByAgentClientId String?  @map("used_by_agent_client_id") @db.Uuid
  usedByClient        AgentClient? @relation(fields: [usedByAgentClientId], references: [id])
  createdAt           DateTime @default(now()) @map("created_at") @db.Timestamptz(6)

  @@index([codeHash])
  @@index([expiresAt])
  @@map("agent_pairing_codes")
}

model AgentPairingConfig {
  id               String   @id
  enabled          Boolean  @default(false)
  updatedByAdminId String?  @map("updated_by_admin_id") @db.Uuid
  updatedAt        DateTime @updatedAt @map("updated_at") @db.Timestamptz(6)

  @@map("agent_pairing_config")
}
```

- [ ] **Step 2: 改 `model AgentClient`(在 schema.prisma 内)**

把 `createdByAdminId String   @map("created_by_admin_id") @db.Uuid` 改为可空,且关系改可选,并加 `origin` 列与反向关系。最终该 model 相关行为:

```prisma
  origin           String   @default("admin")
  createdByAdminId String?  @map("created_by_admin_id") @db.Uuid
  createdBy        AdminUser? @relation(fields: [createdByAdminId], references: [id])
```
并在 `accessLogs AgentAccessLog[]` 同区追加一行:
```prisma
  pairingCodes AgentPairingCode[]
```
(只改这三处:`origin` 新增、`createdByAdminId` 加 `?`、`createdBy` 加 `?`,加 `pairingCodes` 反向关系。不动其它字段。)

- [ ] **Step 3: 生成迁移(schema-vs-schema diff,本仓库约定:手放迁移目录 + `migrate deploy`,禁用 `migrate dev`)**

```bash
cp packages/db/prisma/schema.prisma /tmp/sp-base.prisma
# 编辑 /tmp/sp-base.prisma:删除 model AgentPairingCode{...}、model AgentPairingConfig{...},
# 并把 AgentClient 的改动还原(删 origin 行、createdByAdminId 去掉 ?、createdBy 去掉 ?、删 pairingCodes 行)
mkdir -p packages/db/prisma/migrations/20260518100000_agent_self_pairing
pnpm --filter @ghome/db exec prisma migrate diff \
  --from-schema-datamodel /tmp/sp-base.prisma \
  --to-schema-datamodel packages/db/prisma/schema.prisma \
  --script > packages/db/prisma/migrations/20260518100000_agent_self_pairing/migration.sql
```
检视 `migration.sql`,必须只含这些**非破坏性**语句:`CREATE TABLE "agent_pairing_codes"`、`CREATE TABLE "agent_pairing_config"`、其索引、`ALTER TABLE "agent_clients" ADD COLUMN "origin" TEXT NOT NULL DEFAULT 'admin'`、`ALTER TABLE "agent_clients" ALTER COLUMN "created_by_admin_id" DROP NOT NULL`、`agent_pairing_codes` → `agent_clients` 的 FK。**绝不能**出现 `DROP TABLE`、`DROP COLUMN`、`DROP CONSTRAINT`、`category_kind`、`apps`/`videos`/`contact_submissions`/`collection_items` 相关语句。出现即停止报告(base schema 没还原干净)。

- [ ] **Step 4: 手工在 `migration.sql` 末尾追加单行配置种子**

```sql

-- seed singleton pairing config (channel OFF by default)
INSERT INTO "agent_pairing_config" ("id", "enabled", "updated_at")
VALUES ('singleton', false, CURRENT_TIMESTAMP)
ON CONFLICT ("id") DO NOTHING;
```

- [ ] **Step 5: 应用迁移 + 重生成 client**

```bash
pnpm --filter @ghome/db db:migrate:deploy
pnpm --filter @ghome/db exec prisma generate
```
Expected: 输出含 `20260518100000_agent_self_pairing` applied(1 migration applied),无 drift/reset 提示。若提示破坏性 reset → 停止报告 BLOCKED,勿重置。

- [ ] **Step 6: 在 `packages/db/src/index.ts` 的 `export type { ... } from "@prisma/client";` 块内,`AgentAccessLog,` 行后追加**

```ts
  AgentPairingCode,
  AgentPairingConfig,
```

- [ ] **Step 7: typecheck + 验证表与种子**

```bash
pnpm --filter @ghome/db typecheck
psql "postgres://ghome:ghome@localhost:5432/ghome" -c "\dt agent_pairing*" -c "SELECT id,enabled FROM agent_pairing_config;" -c "SELECT origin FROM agent_clients LIMIT 1;"
```
Expected: 两张 `agent_pairing_*` 表存在;`agent_pairing_config` 有一行 `singleton,f`;`agent_clients.origin` 列存在(现有行值 `admin`);typecheck 干净。

- [ ] **Step 8: 回归既有 db/admin 测试**

```bash
pnpm --filter @ghome/db test && pnpm --filter @ghome/admin test
```
Expected: db 42 passed/1 skipped;admin 44 passed(`createdByAdminId` 改可空不影响既有 `createAgentClient` —— 它仍传该值)。

- [ ] **Step 9: Commit**

```bash
git add packages/db/prisma/schema.prisma packages/db/prisma/migrations packages/db/src/index.ts
git commit -m "feat(db): AgentPairingCode/AgentPairingConfig + AgentClient.origin + nullable createdByAdminId"
```

---

## Task 2: pairing.ts 原语 + SELF_PAIR_DEFAULT_SCOPES

**Files:**
- Create: `apps/admin/lib/agent-api/pairing.ts`
- Modify: `apps/admin/lib/agent-api/scopes.ts`
- Test: `apps/admin/tests/pairing.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/pairing.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { generatePairingCode, codePrefix, PAIRING_CODE_TTL_MS } from "@/lib/agent-api/pairing";
import { hashToken } from "@/lib/agent-api/token";
import { SELF_PAIR_DEFAULT_SCOPES } from "@/lib/agent-api/scopes";

describe("pairing primitives", () => {
  it("generatePairingCode: ghpair_ + 32 base62, unique", () => {
    const a = generatePairingCode();
    expect(a).toMatch(/^ghpair_[0-9A-Za-z]{32}$/);
    const set = new Set(Array.from({ length: 100 }, () => generatePairingCode()));
    expect(set.size).toBe(100);
  });
  it("codePrefix: ghpair_ + first 8 (15 chars)", () => {
    const c = "ghpair_ABCDEFGH" + "zzzz";
    expect(codePrefix(c)).toBe("ghpair_ABCDEFGH");
    expect(codePrefix(c)).toHaveLength(15);
  });
  it("hashToken works for codes (generic sha256, 64 hex)", () => {
    expect(hashToken("ghpair_x")).toMatch(/^[0-9a-f]{64}$/);
    expect(hashToken("ghpair_x")).toBe(hashToken("ghpair_x"));
  });
  it("TTL is 10 minutes", () => {
    expect(PAIRING_CODE_TTL_MS).toBe(10 * 60 * 1000);
  });
  it("SELF_PAIR_DEFAULT_SCOPES is exactly content:published", () => {
    expect([...SELF_PAIR_DEFAULT_SCOPES]).toEqual(["content:published"]);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test pairing`
Expected: FAIL(模块/导出不存在)

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/pairing.ts`**

```ts
import { randomBytes } from "node:crypto";

const ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"; // 62
const CODE_LEN = 32;

/** `ghpair_` + 32 字符 base62(拒绝采样,无 modulo 偏置)。单次 + 10min TTL,32 字符足够。 */
export function generatePairingCode(): string {
  let out = "";
  while (out.length < CODE_LEN) {
    const buf = randomBytes(CODE_LEN);
    for (const b of buf) {
      if (b < 248) {
        out += ALPHABET[b % 62];
        if (out.length === CODE_LEN) break;
      }
    }
  }
  return "ghpair_" + out;
}

/** `ghpair_` + 前 8 字符(共 15),admin 日志辨识用。 */
export function codePrefix(raw: string): string {
  return raw.slice(0, 15);
}

export const PAIRING_CODE_TTL_MS = 10 * 60 * 1000;
```
(哈希复用 `apps/admin/lib/agent-api/token.ts` 的 `hashToken`(通用 sha256),不重复实现。)

- [ ] **Step 4: 在 `apps/admin/lib/agent-api/scopes.ts` 末尾追加**

```ts
/** 公开自助配对出的 token 固定只拿这些 scope(安全默认,非配置)。 */
export const SELF_PAIR_DEFAULT_SCOPES = ["content:published"] as const;
```

- [ ] **Step 5: 跑测试确认通过 + typecheck**

```bash
pnpm --filter @ghome/admin test pairing
pnpm --filter @ghome/admin typecheck
```
Expected: PASS;typecheck 干净。

- [ ] **Step 6: Commit**

```bash
git add apps/admin/lib/agent-api/pairing.ts apps/admin/lib/agent-api/scopes.ts apps/admin/tests/pairing.test.ts
git commit -m "feat(admin): pairing code primitives + SELF_PAIR_DEFAULT_SCOPES"
```

---

## Task 3: agent-pairing-db.ts(config 读写 / 铸码 / 兑换 / 码列表)

**Files:**
- Create: `apps/admin/lib/agent-pairing-db.ts`
- Test: `apps/admin/tests/pairing-db.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/pairing-db.test.ts`**

```ts
import { describe, it, expect, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import {
  isPairingEnabled,
  setPairingEnabled,
  mintPairingCode,
  redeemPairingCode,
  listPairingCodes,
} from "@/lib/agent-pairing-db";
import { hashToken } from "@/lib/agent-api/token";

const createdClientIds: string[] = [];

afterAll(async () => {
  await prisma.agentPairingCode.deleteMany({ where: { usedByAgentClientId: { in: createdClientIds } } });
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: { in: createdClientIds } } });
  await prisma.agentClient.deleteMany({ where: { id: { in: createdClientIds } } });
  await prisma.agentPairingCode.deleteMany({ where: { codePrefix: { startsWith: "ghpair_" } , usedAt: null } });
  await setPairingEnabled(false, null);
});

describe("agent-pairing-db", () => {
  it("config toggle round-trips", async () => {
    await setPairingEnabled(true, null);
    expect(await isPairingEnabled()).toBe(true);
    await setPairingEnabled(false, null);
    expect(await isPairingEnabled()).toBe(false);
  });

  it("mintPairingCode persists hash, returns raw + expiry ~10min", async () => {
    const { rawCode, expiresAt } = await mintPairingCode();
    expect(rawCode).toMatch(/^ghpair_/);
    const row = await prisma.agentPairingCode.findUnique({ where: { codeHash: hashToken(rawCode) } });
    expect(row).not.toBeNull();
    expect(row!.usedAt).toBeNull();
    expect(expiresAt.getTime()).toBeGreaterThan(Date.now() + 9 * 60 * 1000);
  });

  it("redeem valid code → self-paired client, content:published only, code burned", async () => {
    const { rawCode } = await mintPairingCode();
    const res = await redeemPairingCode(rawCode, "my-agent");
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    createdClientIds.push(res.client.id);
    expect(res.client.origin).toBe("self-paired");
    expect(res.client.scopes).toEqual(["content:published"]);
    expect(res.client.createdByAdminId).toBeNull();
    expect(res.rawToken).toMatch(/^ghagt_/);
    const code = await prisma.agentPairingCode.findUnique({ where: { codeHash: hashToken(rawCode) } });
    expect(code!.usedAt).not.toBeNull();
    expect(code!.usedByAgentClientId).toBe(res.client.id);
  });

  it("redeem reused code → code_used", async () => {
    const { rawCode } = await mintPairingCode();
    const a = await redeemPairingCode(rawCode);
    expect(a.ok).toBe(true);
    if (a.ok) createdClientIds.push(a.client.id);
    const b = await redeemPairingCode(rawCode);
    expect(b).toMatchObject({ ok: false, code: "code_used" });
  });

  it("redeem unknown code → invalid_code; expired → code_expired", async () => {
    expect(await redeemPairingCode("ghpair_nope")).toMatchObject({ ok: false, code: "invalid_code" });
    const { rawCode } = await mintPairingCode();
    await prisma.agentPairingCode.update({
      where: { codeHash: hashToken(rawCode) },
      data: { expiresAt: new Date(Date.now() - 1000) },
    });
    expect(await redeemPairingCode(rawCode)).toMatchObject({ ok: false, code: "code_expired" });
  });

  it("name collision → auto self-paired-<rand>", async () => {
    const { rawCode: c1 } = await mintPairingCode();
    const r1 = await redeemPairingCode(c1, "dup-name");
    expect(r1.ok).toBe(true);
    if (r1.ok) createdClientIds.push(r1.client.id);
    const { rawCode: c2 } = await mintPairingCode();
    const r2 = await redeemPairingCode(c2, "dup-name");
    expect(r2.ok).toBe(true);
    if (r2.ok) {
      createdClientIds.push(r2.client.id);
      expect(r2.client.name).toMatch(/^self-paired-/);
    }
  });

  it("listPairingCodes returns rows desc by createdAt", async () => {
    const rows = await listPairingCodes();
    expect(Array.isArray(rows)).toBe(true);
    if (rows.length >= 2) {
      expect(rows[0]!.createdAt.getTime()).toBeGreaterThanOrEqual(rows[1]!.createdAt.getTime());
    }
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test pairing-db`
Expected: FAIL(模块不存在)

- [ ] **Step 3: 实现 `apps/admin/lib/agent-pairing-db.ts`**

```ts
import { prisma } from "@ghome/db";
import type { AgentClient, AgentPairingCode } from "@ghome/db";
import { generateToken, hashToken, tokenPrefix } from "./agent-api/token";
import { generatePairingCode, codePrefix, PAIRING_CODE_TTL_MS } from "./agent-api/pairing";
import { SELF_PAIR_DEFAULT_SCOPES } from "./agent-api/scopes";

const CONFIG_ID = "singleton";

export async function isPairingEnabled(): Promise<boolean> {
  const row = await prisma.agentPairingConfig.findUnique({ where: { id: CONFIG_ID } });
  return row?.enabled ?? false;
}

export async function setPairingEnabled(enabled: boolean, adminId: string | null): Promise<void> {
  await prisma.agentPairingConfig.upsert({
    where: { id: CONFIG_ID },
    create: { id: CONFIG_ID, enabled, updatedByAdminId: adminId },
    update: { enabled, updatedByAdminId: adminId },
  });
}

export async function mintPairingCode(): Promise<{ rawCode: string; expiresAt: Date }> {
  const rawCode = generatePairingCode();
  const expiresAt = new Date(Date.now() + PAIRING_CODE_TTL_MS);
  await prisma.agentPairingCode.create({
    data: { codePrefix: codePrefix(rawCode), codeHash: hashToken(rawCode), expiresAt },
  });
  return { rawCode, expiresAt };
}

export type RedeemResult =
  | { ok: true; [敏感内容已脱敏]; client: AgentClient }
  | { ok: false; code: "invalid_code" | "code_used" | "code_expired" };

async function resolveUniqueName(requested?: string): Promise<string> {
  const cleaned = (requested ?? "").trim();
  if (cleaned) {
    const taken = await prisma.agentClient.findUnique({ where: { name: cleaned } });
    if (!taken) return cleaned;
  }
  for (let i = 0; i < 5; i++) {
    const candidate = `self-paired-${generatePairingCode().slice(7, 15)}`;
    const taken = await prisma.agentClient.findUnique({ where: { name: candidate } });
    if (!taken) return candidate;
  }
  return `self-paired-${Date.now()}`;
}

export async function redeemPairingCode(rawCode: string, name?: string): Promise<RedeemResult> {
  const codeHash = hashToken(rawCode);
  const row = await prisma.agentPairingCode.findUnique({ where: { codeHash } });
  if (!row) return { ok: false, code: "invalid_code" };
  if (row.usedAt) return { ok: false, code: "code_used" };
  if (row.expiresAt.getTime() < Date.now()) return { ok: false, code: "code_expired" };

  // 原子焚码:仅当仍未使用时置 usedAt,防并发双花
  const burn = await prisma.agentPairingCode.updateMany({
    where: { id: row.id, usedAt: null },
    data: { usedAt: new Date() },
  });
  if (burn.count === 0) return { ok: false, code: "code_used" };

  const finalName = await resolveUniqueName(name);
  const [敏感内容已脱敏];
  const client = await prisma.agentClient.create({
    data: {
      name: finalName,
      [敏感内容已脱敏],
      [敏感内容已脱敏],
      scopes: [...SELF_PAIR_DEFAULT_SCOPES],
      origin: "self-paired",
      createdByAdminId: null,
    },
  });
  await prisma.agentPairingCode.update({
    where: { id: row.id },
    data: { usedByAgentClientId: client.id },
  });
  return { ok: true, rawToken, client };
}

export function listPairingCodes(): Promise<AgentPairingCode[]> {
  return prisma.agentPairingCode.findMany({ orderBy: { createdAt: "desc" }, take: 200 });
}
```

- [ ] **Step 4: 跑测试确认通过 + typecheck**

```bash
pnpm --filter @ghome/admin test pairing-db
pnpm --filter @ghome/admin typecheck
```
Expected: 全部 7 用例 PASS;typecheck 干净。(`createdByAdminId: null` 仅在 schema 已改可空后合法 —— Task 1 已改。)

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-pairing-db.ts apps/admin/tests/pairing-db.test.ts
git commit -m "feat(admin): pairing-db (config toggle, mint, atomic redeem, code list)"
```

---

## Task 4: dispatcher pre-auth 特判 + 引导 Skill.md + POST 兑换

**Files:**
- Create: `apps/admin/lib/agent-api/pairing-skill-md.ts`
- Modify: `apps/admin/app/api/agent/v1/[[...slug]]/route.ts`
- Test: `apps/admin/tests/pair-endpoints.test.ts`

- [ ] **Step 1: 写失败测试 `apps/admin/tests/pair-endpoints.test.ts`**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import { NextRequest } from "next/server";
import { GET, POST } from "@/app/api/agent/v1/[[...slug]]/route";
import { setPairingEnabled } from "@/lib/agent-pairing-db";

const createdClientIds: string[] = [];

function get(path: string) {
  const req = new NextRequest(`http://localhost${path}`);
  const slug = path.replace(/^\/api\/agent\/v1\/?/, "").split("/").filter(Boolean);
  return GET(req, { params: Promise.resolve({ slug }) });
}
function post(path: string, body: unknown) {
  const req = new NextRequest(`http://localhost${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const slug = path.replace(/^\/api\/agent\/v1\/?/, "").split("/").filter(Boolean);
  return POST(req, { params: Promise.resolve({ slug }) });
}
async function codeFromSkillMd(): Promise<string> {
  const r = await get("/api/agent/v1/pair/skill.md");
  const md = await r.text();
  const m = md.match(/ghpair_[0-9A-Za-z]{32}/);
  if (!m) throw new Error("no code in skill.md: " + md.slice(0, 200));
  return m[0];
}

afterAll(async () => {
  await prisma.agentPairingCode.deleteMany({ where: { usedByAgentClientId: { in: createdClientIds } } });
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: { in: createdClientIds } } });
  await prisma.agentClient.deleteMany({ where: { id: { in: createdClientIds } } });
  await setPairingEnabled(false, null);
});

describe("pair endpoints", () => {
  it("channel OFF: GET skill.md = closed notice, no code minted", async () => {
    await setPairingEnabled(false, null);
    const before = await prisma.agentPairingCode.count();
    const r = await get("/api/agent/v1/pair/skill.md");
    expect(r.status).toBe(200);
    const md = await r.text();
    expect(md).toContain("已关闭");
    expect(md).not.toMatch(/ghpair_[0-9A-Za-z]{32}/);
    expect(await prisma.agentPairingCode.count()).toBe(before);
  });

  it("channel OFF: POST /pair → 403 pairing_disabled", async () => {
    await setPairingEnabled(false, null);
    const r = await post("/api/agent/v1/pair", { code: "ghpair_x" });
    expect(r.status).toBe(403);
    expect(await r.json()).toEqual({ error: "pairing_disabled" });
  });

  it("channel ON: GET skill.md mints a code; POST redeems → 200 token, content:published", async () => {
    await setPairingEnabled(true, null);
    const code = await codeFromSkillMd();
    const r = await post("/api/agent/v1/pair", { code, name: "e2e-pair" });
    expect(r.status).toBe(200);
    const j = await r.json();
    expect(j.token).toMatch(/^ghagt_/);
    expect(j.scopes).toEqual(["content:published"]);
    const client = await prisma.agentClient.findFirst({ where: { name: j.name } });
    expect(client?.origin).toBe("self-paired");
    if (client) createdClientIds.push(client.id);
  });

  it("invalid/missing/reused/expired mapping", async () => {
    await setPairingEnabled(true, null);
    expect((await post("/api/agent/v1/pair", {})).status).toBe(400); // invalid_request
    expect(await (await post("/api/agent/v1/pair", { code: 123 })).json()).toEqual({ error: "invalid_request" });
    expect(await (await post("/api/agent/v1/pair", { code: "ghpair_unknown" })).json()).toEqual({ error: "invalid_code" });
    const code = await codeFromSkillMd();
    const ok = await post("/api/agent/v1/pair", { code });
    const okj = await ok.json();
    const c = await prisma.agentClient.findFirst({ where: { name: okj.name } });
    if (c) createdClientIds.push(c.id);
    const again = await post("/api/agent/v1/pair", { code });
    expect(again.status).toBe(410);
    expect(await again.json()).toEqual({ error: "code_used" });
  });

  it("self-paired token can GET /apps but is 403 on ops/analytics", async () => {
    await setPairingEnabled(true, null);
    const code = await codeFromSkillMd();
    const pr = await post("/api/agent/v1/pair", { code });
    const { token, name } = await pr.json();
    const c = await prisma.agentClient.findFirst({ where: { name } });
    if (c) createdClientIds.push(c.id);
    const hdr = { authorization: `Bearer ${token}` };
    const apps = await GET(new NextRequest("http://localhost/api/agent/v1/apps", { headers: hdr }), { params: Promise.resolve({ slug: ["apps"] }) });
    expect(apps.status).toBe(200);
    const ops = await GET(new NextRequest("http://localhost/api/agent/v1/contact-submissions", { headers: hdr }), { params: Promise.resolve({ slug: ["contact-submissions"] }) });
    expect(ops.status).toBe(403);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm --filter @ghome/admin test pair-endpoints`
Expected: FAIL(`POST` 未导出 / 公开端点未实现)

- [ ] **Step 3: 实现 `apps/admin/lib/agent-api/pairing-skill-md.ts`**

```ts
/** 通道开:含本次专属配对码的引导文档。 */
export function renderPairingSkillMd(rawCode: string): string {
  return [
    "---",
    "name: ghome-agent-pairing",
    "description: Self-serve pairing — exchange a one-time code for a content:published token",
    "---",
    "",
    "# Ghome Agent 自助配对",
    "",
    "这是自助配对引导。配对成功默认仅授予 `content:published`(等价于用户站公开可见内容)。",
    "更高权限(analytics / ops)需管理员事后在后台审批,公开通道无法自助获得。",
    "",
    "## 你的一次性配对码(仅本次响应可见,10 分钟内有效,单次使用)",
    "",
    "```",
    rawCode,
    "```",
    "",
    "## 兑换",
    "",
    "```",
    "POST /api/agent/v1/pair",
    "Content-Type: application/json",
    "",
    `{ "code": "${rawCode}", "name": "<可选,自报名称>" }`,
    "```",
    "",
    "成功返回 `{ token, name, scopes }`(token 仅此一次)。随后:",
    "",
    "```",
    "GET /api/agent/v1/skill.md",
    "Authorization: Bearer <token>",
    "```",
    "",
    "取个性化完整 API 文档。",
    "",
  ].join("\n");
}

/** 通道关:关闭提示(不含码)。 */
export function renderPairingClosedMd(): string {
  return [
    "---",
    "name: ghome-agent-pairing",
    "description: Pairing channel closed",
    "---",
    "",
    "# 自助配对通道已关闭",
    "",
    "管理员当前未开启公开自助配对。请联系管理员开启,或改用管理员直接签发的授权码。",
    "",
  ].join("\n");
}
```

- [ ] **Step 4: 改 `apps/admin/app/api/agent/v1/[[...slug]]/route.ts`** —— 顶部新增 import 与公开路径常量、抽出 pathname 解析、在 `resolveAgentClient` 之前 pre-auth 特判,并新增 `POST` 导出

把文件**整体替换**为(在现有逻辑上叠加,不改既有鉴权/scope/handler 流程):

```ts
import type { NextRequest } from "next/server";
import { resolveAgentClient, logAccess, touchLastUsed } from "@/lib/agent-api/auth";
import { matchEndpoint, ENDPOINTS } from "@/lib/agent-api/manifest";
import { scopeSatisfies } from "@/lib/agent-api/scopes";
import { jsonError } from "@/lib/agent-api/http";
import { renderSkillMd } from "@/lib/agent-api/skill-md";
import { isPairingEnabled, mintPairingCode, redeemPairingCode } from "@/lib/agent-pairing-db";
import { renderPairingSkillMd, renderPairingClosedMd } from "@/lib/agent-api/pairing-skill-md";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SKILL_PATH = "/api/agent/v1/skill.md";
const PAIR_SKILL_PATH = "/api/agent/v1/pair/skill.md";
const PAIR_PATH = "/api/agent/v1/pair";

function pathnameFrom(slug: string[]): string {
  const rawPath = "/api/agent/v1" + (slug.length ? "/" + slug.join("/") : "");
  const qIdx = rawPath.indexOf("?");
  return qIdx === -1 ? rawPath : rawPath.slice(0, qIdx);
}

function md(body: string): Response {
  return new Response(body, { headers: { "content-type": "text/markdown; charset=utf-8" } });
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ slug?: string[] }> },
): Promise<Response> {
  const { slug = [] } = await params;
  const pathname = pathnameFrom(slug);

  // ── 公开 pre-auth:引导版 Skill.md ──
  if (pathname === PAIR_SKILL_PATH) {
    if (!(await isPairingEnabled())) return md(renderPairingClosedMd());
    const { rawCode } = await mintPairingCode();
    return md(renderPairingSkillMd(rawCode));
  }

  const authed = await resolveAgentClient(req);
  if (!authed.ok) return jsonError(authed.status, authed.code);
  const client = authed.client;

  if (pathname === SKILL_PATH) {
    void touchLastUsed(client);
    void logAccess(client.id, pathname, "ok");
    return md(renderSkillMd(client, ENDPOINTS));
  }

  const match = matchEndpoint(pathname, "GET", ENDPOINTS);
  if (!match) return jsonError(404, "not_found");

  if (!scopeSatisfies(client.scopes, match.endpoint.scope)) {
    if (match.endpoint.scope.startsWith("ops:")) {
      void logAccess(client.id, pathname, "denied");
    }
    return jsonError(403, "forbidden");
  }

  void touchLastUsed(client);
  void logAccess(client.id, pathname, "ok");

  try {
    return await match.endpoint.handler({
      req,
      params: match.params,
      client,
      searchParams: req.nextUrl.searchParams,
    });
  } catch (e) {
    console.error("[agent-api] handler error", { pathname, agentClientId: client.id }, e);
    return jsonError(500, "internal");
  }
}

// ── 公开 pre-auth:配对兑换 ──
export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ slug?: string[] }> },
): Promise<Response> {
  const { slug = [] } = await params;
  const pathname = pathnameFrom(slug);

  if (pathname !== PAIR_PATH) return jsonError(404, "not_found");
  if (!(await isPairingEnabled())) return jsonError(403, "pairing_disabled");

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return jsonError(400, "invalid_request");
  }
  const code = (body as { code?: unknown } | null)?.code;
  const name = (body as { name?: unknown } | null)?.name;
  if (typeof code !== "string" || !code) return jsonError(400, "invalid_request");

  const res = await redeemPairingCode(code, typeof name === "string" ? name : undefined);
  if (!res.ok) {
    const status = res.code === "invalid_code" ? 400 : 410;
    return jsonError(status, res.code);
  }
  return Response.json({
    敏感凭据：[已脱敏]
    name: res.client.name,
    scopes: res.client.scopes,
    note: "更高权限请联系管理员",
  });
}
```

> 既有 `GET` 鉴权/scope/handler 流程逐行未改,仅在 `resolveAgentClient` 前插入 `PAIR_SKILL_PATH` 分支并抽出 `pathnameFrom`/`md`;新增 `POST`。`jsonError` 已支持任意 code 字符串。

- [ ] **Step 5: 跑测试确认通过 + 全量回归 + typecheck**

```bash
pnpm --filter @ghome/admin test pair-endpoints
pnpm --filter @ghome/admin test
pnpm --filter @ghome/admin typecheck
```
Expected: pair-endpoints 全绿;全量 admin 套件无回归(原 dispatch/queries 等仍绿);typecheck 干净。

- [ ] **Step 6: Commit**

```bash
git add "apps/admin/app/api/agent/v1/[[...slug]]/route.ts" apps/admin/lib/agent-api/pairing-skill-md.ts apps/admin/tests/pair-endpoints.test.ts
git commit -m "feat(admin): public pairing endpoints (bootstrap skill.md + POST /pair)"
```

---

## Task 5: 来源列 + 通道开关面板 + 配对码日志子页

**Files:**
- Modify: `apps/admin/app/(admin)/agent-clients/actions.ts`
- Modify: `apps/admin/app/(admin)/agent-clients/page.tsx`
- Create: `apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx`

> 先 `Read` 现有 `apps/admin/app/(admin)/agent-clients/page.tsx`、`actions.ts`、`apps/admin/components/ConfirmSubmitButton.tsx`、`apps/admin/lib/auth.ts` 作风格基准。沿用 `dash-section`/`dash-table`/`page-header`/`btn-primary` 等既有 class 与既有 server-action 写法。

- [ ] **Step 1: 在 `apps/admin/app/(admin)/agent-clients/actions.ts` 末尾追加通道开关 server action**

```ts
import { setPairingEnabled } from "@/lib/agent-pairing-db";

export async function setPairingChannelAction(enabled: boolean): Promise<void> {
  const me = await adminId();
  await setPairingEnabled(enabled, me);
  await logAuditAction(
    me,
    enabled ? "agentPairing.enable" : "agentPairing.disable",
    "agentPairing",
    "singleton",
    { after: { enabled } },
  );
  revalidatePath("/agent-clients");
}
```
(`adminId`/`logAuditAction`/`revalidatePath` 已在文件内 import,沿用。把 `import { setPairingEnabled }` 合并到文件顶部 import 区。)

- [ ] **Step 2: 改 `apps/admin/app/(admin)/agent-clients/page.tsx`** —— 顶部加通道面板、表格加 `来源` 列、加配对码日志链接

整体替换为:

```tsx
import Link from "next/link";
import { listAgentClients } from "@/lib/agent-clients-db";
import { isPairingEnabled } from "@/lib/agent-pairing-db";
import { setPairingChannelAction } from "./actions";

export const dynamic = "force-dynamic";

const PAIR_PATH = "/api/agent/v1/pair/skill.md";

export default async function AgentClientsPage() {
  const [clients, pairingEnabled] = await Promise.all([listAgentClients(), isPairingEnabled()]);
  const base = process.env.ADMIN_BASE_URL ?? "";
  const enableBound = setPairingChannelAction.bind(null, true);
  const disableBound = setPairingChannelAction.bind(null, false);

  return (
    <>
      <div className="page-header">
        <h1>Agent 接入</h1>
        <Link href="/agent-clients/new" className="btn-primary">+ 新建 Agent</Link>
      </div>

      <div className="dash-section" style={{ marginBottom: 16 }}>
        <h2 style={{ marginTop: 0 }}>公开自助配对通道</h2>
        <p>
          状态:<strong>{pairingEnabled ? "已开启" : "已关闭"}</strong>
          {"　"}
          <Link href="/agent-clients/pairing-codes" style={{ color: "var(--primary)" }}>配对码日志</Link>
        </p>
        <p>
          公开地址:<code style={{ userSelect: "all" }}>{base + PAIR_PATH}</code>
        </p>
        {pairingEnabled ? (
          <form action={disableBound}>
            <button type="submit" className="btn-secondary">关闭通道</button>
          </form>
        ) : (
          <form action={enableBound}>
            <button type="submit" className="btn-primary">开启通道</button>
          </form>
        )}
      </div>

      <div className="dash-section" style={{ padding: 0, overflow: "hidden" }}>
        <table className="dash-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>来源</th>
              <th>Token 前缀</th>
              <th>Scopes</th>
              <th>状态</th>
              <th>最近使用</th>
              <th>过期</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: "center", color: "var(--text-3)" }}>
                  暂无数据
                </td>
              </tr>
            ) : (
              clients.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.origin === "self-paired" ? "自助" : "管理员"}</td>
                  <td><code>{c.tokenPrefix}…</code></td>
                  <td>{c.scopes.join(", ") || "—"}</td>
                  <td>{c.disabled ? "已停用" : "启用"}</td>
                  <td>{c.lastUsedAt ? c.lastUsedAt.toISOString().slice(0, 16).replace("T", " ") : "—"}</td>
                  <td>{c.expiresAt ? c.expiresAt.toISOString().slice(0, 10) : "—"}</td>
                  <td>
                    <Link href={`/agent-clients/${c.id}/edit`} style={{ color: "var(--primary)" }}>
                      编辑
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
```

- [ ] **Step 3: 创建只读子页 `apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx`**

```tsx
import Link from "next/link";
import { listPairingCodes } from "@/lib/agent-pairing-db";

export const dynamic = "force-dynamic";

export default async function PairingCodesPage() {
  const codes = await listPairingCodes();
  const now = Date.now();
  return (
    <>
      <div className="page-header">
        <h1>配对码日志</h1>
        <Link href="/agent-clients" style={{ color: "var(--primary)" }}>← 返回</Link>
      </div>
      <div className="dash-section" style={{ padding: 0, overflow: "hidden" }}>
        <table className="dash-table">
          <thead>
            <tr><th>码前缀</th><th>创建</th><th>过期</th><th>状态</th><th>兑换出的 Client</th></tr>
          </thead>
          <tbody>
            {codes.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-3)" }}>暂无数据</td></tr>
            ) : (
              codes.map((c) => {
                const status = c.usedAt
                  ? "已用"
                  : c.expiresAt.getTime() < now
                    ? "已过期"
                    : "未用";
                return (
                  <tr key={c.id}>
                    <td><code>{c.codePrefix}…</code></td>
                    <td>{c.createdAt.toISOString().slice(0, 16).replace("T", " ")}</td>
                    <td>{c.expiresAt.toISOString().slice(0, 16).replace("T", " ")}</td>
                    <td>{status}</td>
                    <td>{c.usedByAgentClientId ?? "—"}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
```

- [ ] **Step 4: typecheck + build + 全量回归**

```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
pnpm --filter @ghome/admin test
```
Expected: typecheck 干净;build 成功且新增路由 `/agent-clients/pairing-codes` 出现;admin 套件全绿。

- [ ] **Step 5: Commit**

```bash
git add "apps/admin/app/(admin)/agent-clients/actions.ts" "apps/admin/app/(admin)/agent-clients/page.tsx" "apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx"
git commit -m "feat(admin): agent-clients UI — origin column, pairing channel toggle, codes log"
```

---

## Task 6: E2E 扩展 + 全量验证 + spec 交叉引用

**Files:**
- Modify: `apps/admin/e2e/agent-clients.spec.ts`
- Modify: `docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md`

> 先 `Read` 现有 `apps/admin/e2e/agent-clients.spec.ts`(已有签发→展示→拉取→吊销链路与 signin 帮助)与 `apps/admin/playwright.config.ts`。沿用其 signin/选择器写法。

- [ ] **Step 1: 在 `apps/admin/e2e/agent-clients.spec.ts` 追加一个测试(自助配对端到端)**

```ts
test("self-pairing: admin enables channel → public skill.md → POST /pair → token works", async ({ page, request }) => {
  // 1. 管理员登录并开启通道(沿用文件已有的 signin 流程/常量)
  await page.goto(`${BASE}/signin`);
  await page.locator('input[name="email"]').fill(ADMIN_EMAIL);
  await page.locator('input[name="password"]').fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "登录" }).click();
  await page.waitForURL(`${BASE}/`);
  await page.goto(`${BASE}/agent-clients`);
  if (await page.getByRole("button", { name: "开启通道" }).isVisible()) {
    await page.getByRole("button", { name: "开启通道" }).click();
  }
  await expect(page.getByText("状态:已开启")).toBeVisible();

  // 2. 免鉴权抓引导 Skill.md,取一次性配对码
  const skill = await request.get(`${BASE}/api/agent/v1/pair/skill.md`);
  expect(skill.status()).toBe(200);
  const md = await skill.text();
  const code = md.match(/ghpair_[0-9A-Za-z]{32}/)?.[0];
  expect(code).toBeTruthy();

  // 3. 凭码自助兑换 token
  const pair = await request.post(`${BASE}/api/agent/v1/pair`, {
    data: { code, name: `e2e-self-${Date.now()}` },
  });
  expect(pair.status()).toBe(200);
  const { token, scopes } = await pair.json();
  expect(token).toMatch(/^ghagt_/);
  expect(scopes).toEqual(["content:published"]);

  // 4. 用 token 调数据 API
  const apps = await request.get(`${BASE}/api/agent/v1/apps`, {
    headers: { authorization: `Bearer ${token}` },
  });
  expect(apps.status()).toBe(200);

  // 5. 复原:关闭通道
  await page.goto(`${BASE}/agent-clients`);
  if (await page.getByRole("button", { name: "关闭通道" }).isVisible()) {
    await page.getByRole("button", { name: "关闭通道" }).click();
  }
});
```

- [ ] **Step 2: 跑 E2E(本地需 admin dev 在跑或 webServer 自起 + 已 seed 管理员)**

Run: `pnpm --filter @ghome/admin exec playwright test`
Expected: 全部通过(原有用例 + 新自助配对用例)。

- [ ] **Step 3: 原 spec 末尾加交叉引用**

在 `docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md` §6(后续)区追加一行:
```
- 公开自助配对通道(Skill.md → 一次性配对码 → 自助换 token):见配套附录 [2026-05-18-agent-self-pairing-design.md](2026-05-18-agent-self-pairing-design.md)。
```

- [ ] **Step 4: 全量验证**

```bash
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin test
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
pnpm lint
```
Expected: 全绿(db 42/1skip;admin 套件含新 pairing/pairing-db/pair-endpoints 全绿;typecheck/lint 干净;build 成功)。

- [ ] **Step 5: Commit**

```bash
git add apps/admin/e2e/agent-clients.spec.ts docs/superpowers/specs/2026-05-18-admin-agent-data-api-design.md
git commit -m "test(admin): e2e self-pairing flow; cross-link self-pairing spec"
```

---

## Self-Review(规划者已执行)

- **Spec 覆盖**:§2 数据模型→Task1;§3 配对码/token 原语→Task2;§4.1/§4.2 公开端点(开关/铸码/兑换7步/错误码/原子焚码)→Task3(redeem 原子焚码)+Task4(端点 + 错误映射);§5 Admin UI(来源列/开关面板/审计/码日志/提权复用)→Task5(提权复用既有编辑页,无新代码);§6 安全(固定安全 scope/单次+TTL/出厂关)→Task1 种子 enabled=false + Task2 常量 + Task3/4 行为 + 测试断言;§7 测试→各 Task TDD + Task6 E2E;§8 B1–B5→Task1–6。
- **占位符扫描**:无 TBD/TODO;每步含完整代码与命令;迁移 `<timestamp>` 用固定 `20260518100000`;name 冲突重试给了确定实现。
- **类型一致**:`generatePairingCode`/`codePrefix`/`PAIRING_CODE_TTL_MS`、`SELF_PAIR_DEFAULT_SCOPES`、`isPairingEnabled`/`setPairingEnabled`/`mintPairingCode`/`redeemPairingCode`/`RedeemResult`/`listPairingCodes`、`renderPairingSkillMd`/`renderPairingClosedMd`、`setPairingChannelAction`、route `GET`/`POST` 跨 Task 签名一致;`hashToken` 复用 token.ts 通用 sha256;`createdByAdminId: null` 仅在 Task1 改可空后被 Task3 使用(顺序正确)。
- **既有约定**:迁移走 schema-vs-schema diff + `migrate deploy`(本仓库不可用 `migrate dev`,已在 Task1 写明并给禁止性语句清单);宿主 `pnpm`、Postgres 已起、无 Docker;commit 信息子代理受分类器限制可能不带 Co-Authored-By(终态合并提交补署)。
- **已知实现期核对点**:迁移生成后人工核对 `migration.sql` 仅含白名单语句;E2E 的 signin 选择器/种子管理员凭据以现有 `agent-clients.spec.ts` 既有常量为准(该文件已实现并跑通,直接复用其顶部 BASE/ADMIN_EMAIL/ADMIN_PASSWORD)。
