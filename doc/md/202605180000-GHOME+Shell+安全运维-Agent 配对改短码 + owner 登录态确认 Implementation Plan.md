---
id: "doc-4fd4aadd25f3"
title: "Agent 配对改短码 + owner 登录态确认 Implementation Plan"
date: "2026-05-18T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-pairing-owner-confirm.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-pairing-owner-confirm.md"
sourceSha256: "72e99714230d5da578e199ed1dc8422c70d813568afb1544b2e8bb96051317f6"
sourceSystem: "project-doc"
---

# Agent 配对改短码 + owner 登录态确认 Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-18-agent-pairing-owner-confirm.md`

> 整理日期：2026-05-18 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 把 Agent 配对从"长码公开自助 POST 兑换"改为"8 位短码 + owner 登录 Admin 输入短码、后台校验通过 → Admin 一次性显示 token"。

**Architecture:** 复用现有 token 一次性回显机制(编辑页 `?敏感凭据：[已脱敏] + `TokenRevealBanner`)。公开 `GET /agent/skill.md` 仍铸码(改 8 位短码),公开 `POST /agent/pair` 删除;新增登录态 `/agent-clients/pair` 页 + `confirmPairingAction` 调 `confirmPairingCode(code,adminId,name?)`(原子焚码、`createdByAdminId=确认管理员`、固定 `content:published`)。

**Tech Stack:** Next.js 15 App Router、Prisma、vitest、Playwright。无 Prisma 迁移。

**Spec:** [docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md](../specs/2026-05-18-agent-self-pairing-design.md)

---

## File Structure

- Modify `apps/admin/lib/agent-api/pairing.ts` — 8 位短码生成器 + `randomTicket()`;删旧 `codePrefix`;TTL 30min
- Modify `apps/admin/lib/agent-pairing-db.ts` — `mintPairingCode` 用 ticket;`redeemPairingCode`→`confirmPairingCode(code,adminId,name?)`(+`pairing_disabled`、`createdByAdminId=adminId`);`resolveUniqueName` 后缀修正;`listPairingCodes` 带确认管理员
- Modify `apps/admin/lib/agent-api/pairing-skill-md.ts` — 引导文案改"交给 owner 登录 Admin 输入",TTL 30min,删 `POST /agent/pair`
- Delete `apps/admin/app/agent/pair/route.ts`(+ 空目录);Modify `apps/admin/middleware.ts` 去 `/agent/pair`
- Modify `apps/admin/app/(admin)/agent-clients/actions.ts` — 加 `confirmPairingAction`
- Create `apps/admin/app/(admin)/agent-clients/pair/page.tsx` — 确认表单 + `?error=` 提示
- Modify `apps/admin/app/(admin)/agent-clients/page.tsx` — header 加「输入配对码」入口
- Modify `apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx` — 不显码,列改 创建/过期/状态/确认管理员/Client
- Modify `apps/admin/tests/pair-endpoints.test.ts` — 删公开 POST 用例,加 `confirmPairingCode` 用例
- Modify `apps/admin/e2e/agent-clients.spec.ts` — 改写为短码 + 登录态确认流

---

## Task 1: pairing.ts 短码生成器

**Files:** Modify `apps/admin/lib/agent-api/pairing.ts`; Test `apps/admin/tests/pairing.test.ts`

- [ ] **Step 1: 改写测试 `apps/admin/tests/pairing.test.ts`** 为(整体替换文件内容):

```ts
import { describe, it, expect } from "vitest";
import { generatePairingCode, randomTicket, PAIRING_CODE_TTL_MS } from "@/lib/agent-api/pairing";
import { hashToken } from "@/lib/agent-api/token";
import { SELF_PAIR_DEFAULT_SCOPES } from "@/lib/agent-api/scopes";

const CHARSET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789#$%@*+=-";

describe("pairing primitives", () => {
  it("generatePairingCode: 8 chars, only from the safe charset, no ambiguous O0I1L", () => {
    for (let i = 0; i < 200; i++) {
      const c = generatePairingCode();
      expect(c).toHaveLength(8);
      for (const ch of c) expect(CHARSET).toContain(ch);
      expect(c).not.toMatch(/[O0I1L]/);
    }
  });
  it("generatePairingCode: unique across calls", () => {
    const set = new Set(Array.from({ length: 200 }, () => generatePairingCode()));
    expect(set.size).toBe(200);
  });
  it("randomTicket: short non-secret tag, distinct from a code", () => {
    const t = randomTicket();
    expect(t).toMatch(/^pair-[0-9A-Za-z]{6}$/);
    expect(randomTicket()).not.toBe(randomTicket());
  });
  it("hashToken works for short codes (sha256 hex 64)", () => {
    expect(hashToken("ABCD2#%@")).toMatch(/^[0-9a-f]{64}$/);
    expect(hashToken("ABCD2#%@")).toBe(hashToken("ABCD2#%@"));
  });
  it("TTL is 30 minutes", () => {
    expect(PAIRING_CODE_TTL_MS).toBe(30 * 60 * 1000);
  });
  it("SELF_PAIR_DEFAULT_SCOPES unchanged = content:published", () => {
    expect([...SELF_PAIR_DEFAULT_SCOPES]).toEqual(["content:published"]);
  });
});
```

- [ ] **Step 2: Run → FAIL.** `pnpm --filter @ghome/admin test pairing` — expect fail (`randomTicket` missing / length 8 mismatch).

- [ ] **Step 3: Replace `apps/admin/lib/agent-api/pairing.ts` entirely with:**

```ts
import { randomBytes } from "node:crypto";

// 去易混字符(无 O 0 I 1 L)的大写字母+数字 + 安全特殊符;不含引号/反斜杠/空格/斜杠。
const CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789#$%@*+=-"; // 39
const CODE_LEN = 8;
const TICKET_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"; // 62
const TICKET_LEN = 6;

function sample(alphabet: string, len: number): string {
  const n = alphabet.length;
  const limit = Math.floor(256 / n) * n; // 拒绝 >=limit 去 modulo 偏置
  let out = "";
  while (out.length < len) {
    const buf = randomBytes(len);
    for (const b of buf) {
      if (b < limit) {
        out += alphabet[b % n];
        if (out.length === len) break;
      }
    }
  }
  return out;
}

/** 8 位短配对码(去易混字符,拒绝采样无偏置)。单次 + 30min TTL。原始码永不入库/日志。 */
export function generatePairingCode(): string {
  return sample(CODE_ALPHABET, CODE_LEN);
}

/** 与密文无关的随机工单号,写入 AgentPairingCode.codePrefix 列纯做日志关联(不可反推短码)。 */
export function randomTicket(): string {
  return "pair-" + sample(TICKET_ALPHABET, TICKET_LEN);
}

export const PAIRING_CODE_TTL_MS = 30 * 60 * 1000;
```

- [ ] **Step 4: Run → PASS.** `pnpm --filter @ghome/admin test pairing` (6 cases). Then `pnpm --filter @ghome/admin typecheck` — note: this WILL fail to fully typecheck until Task 2 (callers of removed `codePrefix`); that is expected — only assert `test pairing` is green here; do NOT fix other files in this task.

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-api/pairing.ts apps/admin/tests/pairing.test.ts
git commit -m "feat(admin): 8-char short pairing code + randomTicket; 30min TTL"
```

---

## Task 2: agent-pairing-db.ts

**Files:** Modify `apps/admin/lib/agent-pairing-db.ts`; Test `apps/admin/tests/pairing-db.test.ts`

- [ ] **Step 1: Replace `apps/admin/tests/pairing-db.test.ts` entirely with:**

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import {
  isPairingEnabled,
  setPairingEnabled,
  mintPairingCode,
  confirmPairingCode,
  listPairingCodes,
} from "@/lib/agent-pairing-db";

let adminId: string;
const createdClientIds: string[] = [];

beforeAll(async () => {
  const a = await prisma.adminUser.create({
    data: { email: `pairdb-${Date.now()}@x.io`, [敏感内容已脱敏] },
  });
  adminId = a.id;
});
afterAll(async () => {
  await prisma.agentPairingCode.deleteMany({ where: { usedByAgentClientId: { in: createdClientIds } } });
  await prisma.agentAccessLog.deleteMany({ where: { agentClientId: { in: createdClientIds } } });
  await prisma.agentClient.deleteMany({ where: { id: { in: createdClientIds } } });
  await prisma.agentPairingCode.deleteMany({ where: { codeHash: { not: "" }, usedAt: null } });
  await setPairingEnabled(false, null);
  await prisma.adminUser.delete({ where: { id: adminId } });
});

describe("confirmPairingCode", () => {
  it("valid → client with createdByAdminId set, content:published, code burned", async () => {
    await setPairingEnabled(true, null);
    const { rawCode } = await mintPairingCode();
    const res = await confirmPairingCode(rawCode, adminId, "owner-named");
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    createdClientIds.push(res.client.id);
    expect(res.client.origin).toBe("self-paired");
    expect(res.client.scopes).toEqual(["content:published"]);
    expect(res.client.createdByAdminId).toBe(adminId);
    expect(res.client.name).toBe("owner-named");
    expect(res.rawToken).toMatch(/^ghagt_/);
    const code = await prisma.agentPairingCode.findFirst({ where: { usedByAgentClientId: res.client.id } });
    expect(code?.usedAt).not.toBeNull();
  });

  it("reused → code_used; unknown → invalid_code; expired → code_expired", async () => {
    await setPairingEnabled(true, null);
    const { rawCode } = await mintPairingCode();
    const a = await confirmPairingCode(rawCode, adminId);
    if (a.ok) createdClientIds.push(a.client.id);
    expect((await confirmPairingCode(rawCode, adminId))).toMatchObject({ ok: false, code: "code_used" });
    expect((await confirmPairingCode("NOPE2#$@", adminId))).toMatchObject({ ok: false, code: "invalid_code" });
    const { rawCode: c2 } = await mintPairingCode();
    await prisma.agentPairingCode.update({
      where: { codeHash: (await import("@/lib/agent-api/token")).hashToken(c2) },
      data: { expiresAt: new Date(Date.now() - 1000) },
    });
    expect((await confirmPairingCode(c2, adminId))).toMatchObject({ ok: false, code: "code_expired" });
  });

  it("channel disabled → pairing_disabled (even with a valid fresh code)", async () => {
    await setPairingEnabled(true, null);
    const { rawCode } = await mintPairingCode();
    await setPairingEnabled(false, null);
    expect((await confirmPairingCode(rawCode, adminId))).toMatchObject({ ok: false, code: "pairing_disabled" });
  });

  it("concurrent confirm of same code → exactly one ok", async () => {
    await setPairingEnabled(true, null);
    const { rawCode } = await mintPairingCode();
    const [r1, r2] = await Promise.all([
      confirmPairingCode(rawCode, adminId),
      confirmPairingCode(rawCode, adminId),
    ]);
    const oks = [r1, r2].filter((r) => r.ok);
    const used = [r1, r2].filter((r) => !r.ok);
    expect(oks.length).toBe(1);
    expect(used.length).toBe(1);
    for (const r of oks) if (r.ok) createdClientIds.push(r.client.id);
  });

  it("mintPairingCode stores a random ticket in codePrefix, never the code", async () => {
    await setPairingEnabled(true, null);
    const { rawCode } = await mintPairingCode();
    const { hashToken } = await import("@/lib/agent-api/token");
    const row = await prisma.agentPairingCode.findUnique({ where: { codeHash: hashToken(rawCode) } });
    expect(row?.codePrefix).toMatch(/^pair-[0-9A-Za-z]{6}$/);
    expect(row?.codePrefix).not.toContain(rawCode);
  });

  it("listPairingCodes returns rows desc with usedByClient relation", async () => {
    const rows = await listPairingCodes();
    expect(Array.isArray(rows)).toBe(true);
    // 关系字段存在(可能为 null,但类型上应有 usedByClient)
    if (rows[0]) expect("usedByClient" in rows[0]).toBe(true);
  });
});
```

- [ ] **Step 2: Run → FAIL.** `pnpm --filter @ghome/admin test pairing-db` (no `confirmPairingCode` export).

- [ ] **Step 3: Edit `apps/admin/lib/agent-pairing-db.ts`:**

(a) imports line: change `import { generatePairingCode, codePrefix, PAIRING_CODE_TTL_MS } from "./agent-api/pairing";` → `import { generatePairingCode, randomTicket, PAIRING_CODE_TTL_MS } from "./agent-api/pairing";`

(b) `mintPairingCode`: change `data: { codePrefix: codePrefix(rawCode), codeHash: hashToken(rawCode), expiresAt }` → `data: { codePrefix: randomTicket(), codeHash: hashToken(rawCode), expiresAt }`

(c) `resolveUniqueName`: the candidate line `const candidate = \`self-paired-${generatePairingCode().slice(7, 15)}\`;` → `const candidate = \`self-paired-${generatePairingCode()}\`;` (short code is now 8 chars, no `ghpair_` prefix to slice; comment may be simplified to "随机后缀复用短码生成器(8 位)").

(d) Replace the `RedeemResult` type + `redeemPairingCode` function with:

```ts
export type ConfirmResult =
  | { ok: true; [敏感内容已脱敏]; client: AgentClient }
  | { ok: false; code: "invalid_code" | "code_used" | "code_expired" | "pairing_disabled" };

export async function confirmPairingCode(
  rawCode: string,
  adminId: string,
  name?: string,
): Promise<ConfirmResult> {
  if (!(await isPairingEnabled())) return { ok: false, code: "pairing_disabled" };

  const codeHash = hashToken(rawCode);
  const row = await prisma.agentPairingCode.findUnique({ where: { codeHash } });
  if (!row) return { ok: false, code: "invalid_code" };
  if (row.usedAt) return { ok: false, code: "code_used" };
  if (row.expiresAt.getTime() < Date.now()) return { ok: false, code: "code_expired" };

  // 焚码→建客户端→回填,一个事务内防并发双花;任一失败整体回滚(码保持未使用)。
  const result = await prisma.$transaction(async (tx) => {
    const burn = await tx.agentPairingCode.updateMany({
      where: { id: row.id, usedAt: null },
      data: { usedAt: new Date() },
    });
    if (burn.count === 0) return { ok: false, code: "code_used" } as const;

    const finalName = await resolveUniqueName(tx, name);
    const [敏感内容已脱敏];
    const client = await tx.agentClient.create({
      data: {
        name: finalName,
        [敏感内容已脱敏],
        [敏感内容已脱敏],
        scopes: [...SELF_PAIR_DEFAULT_SCOPES],
        origin: "self-paired",
        createdByAdminId: adminId,
      },
    });
    await tx.agentPairingCode.update({
      where: { id: row.id },
      data: { usedByAgentClientId: client.id },
    });
    return { ok: true, rawToken, client } as const;
  });
  return result;
}
```

(e) `listPairingCodes`: change to include the related client:
```ts
export function listPairingCodes() {
  return prisma.agentPairingCode.findMany({
    orderBy: { createdAt: "desc" },
    take: 200,
    include: { usedByClient: { select: { name: true, createdByAdminId: true } } },
  });
}
```
(Confirm the relation field name on `AgentPairingCode` by reading `packages/db/prisma/schema.prisma` model `AgentPairingCode` — it is `usedByClient` per the existing schema; if the actual relation name differs, use the real one and adjust the test's `"usedByClient" in rows[0]` accordingly. Drop the explicit `: Promise<AgentPairingCode[]>` return annotation since the include widens the type; let it infer. Remove the now-unused `AgentPairingCode` type import if nothing else uses it — verify before removing.)

- [ ] **Step 4: Run → PASS + typecheck.** `pnpm --filter @ghome/admin test pairing-db` (6 cases). `pnpm --filter @ghome/admin typecheck` — will still fail in `app/agent/pair/route.ts` (imports removed `redeemPairingCode`) and `pair-endpoints.test.ts`; that is expected and fixed in Task 3/5. Only require `test pairing-db` green here.

- [ ] **Step 5: Commit**

```bash
git add apps/admin/lib/agent-pairing-db.ts apps/admin/tests/pairing-db.test.ts
git commit -m "feat(admin): confirmPairingCode(code,adminId,name) — channel-gated, createdByAdminId set"
```

---

## Task 3: 删 /agent/pair + middleware + 引导文案

**Files:** Delete `apps/admin/app/agent/pair/route.ts`; Modify `apps/admin/middleware.ts`, `apps/admin/lib/agent-api/pairing-skill-md.ts`

- [ ] **Step 1:** `git rm apps/admin/app/agent/pair/route.ts` and remove the now-empty `apps/admin/app/agent/pair/` directory.

- [ ] **Step 2:** In `apps/admin/middleware.ts` public-path `if`, delete the line `    pathname === "/agent/pair" ||` (KEEP `pathname === "/agent/skill.md" ||`).

- [ ] **Step 3:** Replace `renderPairingSkillMd` in `apps/admin/lib/agent-api/pairing-skill-md.ts` with (keep `renderPairingClosedMd` unchanged):

```ts
/** 通道开:含本次专属短配对码的引导文档(owner 登录 Admin 输入完成配对)。 */
export function renderPairingSkillMd(rawCode: string): string {
  return [
    "---",
    "name: ghome-agent-pairing",
    "description: Pair this agent — hand the short code to your owner to confirm in Admin",
    "---",
    "",
    "# Ghome Agent 配对",
    "",
    "配对成功默认仅授予 `content:published`(等价于用户站公开可见内容)。",
    "更高权限(analytics / ops)由管理员事后在后台「编辑」页提权。",
    "",
    "## 你的一次性配对码(仅本次响应可见,30 分钟内有效,单次使用)",
    "",
    "```",
    rawCode,
    "```",
    "",
    "## 如何完成配对",
    "",
    "把上面这串配对码交给你的 **owner**(拥有 Admin 账号的人)。owner 操作:",
    "",
    "1. 用自己的账号登录 Admin 后台",
    "2. 顶部导航进入「Agent 接入」→ 点「输入配对码」",
    "3. 填入这串配对码(可选填一个 Agent 名称)并提交",
    "4. 校验通过后,Admin 页面会**一次性**显示本 Agent 的 Bearer token",
    "5. owner 把该 token 配置进本 Agent",
    "",
    "拿到 token 后,用它调用个性化完整 API 文档:",
    "",
    "```",
    "GET /api/agent/v1/skill.md",
    "Authorization: Bearer <token>",
    "```",
    "",
  ].join("\n");
}
```

- [ ] **Step 4: Verify.** `pnpm --filter @ghome/admin typecheck` — now clean EXCEPT `apps/admin/tests/pair-endpoints.test.ts` still imports the deleted `@/app/agent/pair/route` (fixed in Task 5). Confirm no OTHER file references `@/app/agent/pair` or `redeemPairingCode`: `grep -rn "agent/pair/route\|redeemPairingCode" apps/admin --include='*.ts' --include='*.tsx' | grep -v '/.next/'` → only `pair-endpoints.test.ts` may remain. `pnpm --filter @ghome/admin build` — succeeds and route list NO LONGER contains `/agent/pair` (still has `/agent/skill.md`).

- [ ] **Step 5: Commit**

```bash
git add apps/admin/app/agent apps/admin/middleware.ts apps/admin/lib/agent-api/pairing-skill-md.ts
git commit -m "refactor(admin): remove public POST /agent/pair; skill.md instructs owner Admin-confirm"
```

---

## Task 4: confirmPairingAction + /agent-clients/pair 页 + 入口 + 日志页改列

**Files:** Modify `apps/admin/app/(admin)/agent-clients/actions.ts`, `page.tsx`, `pairing-codes/page.tsx`; Create `apps/admin/app/(admin)/agent-clients/pair/page.tsx`

- [ ] **Step 1:** In `apps/admin/app/(admin)/agent-clients/actions.ts`:
(a) change the import `import { setPairingEnabled } from "@/lib/agent-pairing-db";` → `import { setPairingEnabled, confirmPairingCode } from "@/lib/agent-pairing-db";`
(b) append:

```ts
export async function confirmPairingAction(form: FormData): Promise<void> {
  const me = await adminId();
  const code = String(form.get("code") ?? "").trim();
  const name = String(form.get("name") ?? "").trim() || undefined;
  if (!code) redirect("/agent-clients/pair?error=invalid_request");
  const res = await confirmPairingCode(code, me, name);
  if (!res.ok) redirect(`/agent-clients/pair?error=${res.code}`);
  await logAuditAction(me, "agentClient.pair", "agentClient", res.client.id, {
    after: { name: res.client.name, scopes: res.client.scopes, via: "pairing-code" },
  });
  revalidatePath("/agent-clients");
  // 一次性明文 token 经同源、仅管理员的重定向 URL 单次展示(库内仅哈希),勿外推到其他路由。
  redirect(`/agent-clients/${res.client.id}/edit?敏感凭据：[已脱敏]
}
```
(`adminId`/`logAuditAction`/`revalidatePath`/`redirect` already imported & file already has top `"use server"`. Note: `redirect()` throws, so the `if (!res.ok) redirect(...)` correctly does not fall through — mirrors existing actions.)

- [ ] **Step 2:** Create `apps/admin/app/(admin)/agent-clients/pair/page.tsx`:

```tsx
import Link from "next/link";
import { EditForm, FormRow } from "@/components/EditForm";
import { confirmPairingAction } from "../actions";

export const dynamic = "force-dynamic";

const ERRORS: Record<string, string> = {
  invalid_request: "请填写配对码。",
  invalid_code: "配对码无效(不存在)。请向 Agent 重新获取。",
  code_used: "该配对码已被使用。请让 Agent 重新读取获取新码。",
  code_expired: "该配对码已过期(30 分钟有效)。请让 Agent 重新读取获取新码。",
  pairing_disabled: "公开配对通道当前已关闭,无法完成配对。",
};

export default async function PairConfirmPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;
  const msg = error ? (ERRORS[error] ?? "配对失败,请重试。") : null;
  return (
    <>
      <div className="page-header">
        <h1>输入配对码</h1>
        <Link href="/agent-clients" style={{ color: "var(--primary)" }}>← 返回</Link>
      </div>
      {msg && (
        <div className="dash-section" style={{ borderColor: "var(--danger, #c0392b)", color: "var(--danger, #c0392b)", marginBottom: 16 }}>
          {msg}
        </div>
      )}
      <p style={{ color: "var(--text-3)", marginBottom: 16 }}>
        Agent 读取公开 Skill.md 后会拿到一串 8 位配对码,把它填到这里完成配对;校验通过后本页会一次性显示该 Agent 的 token。
      </p>
      <EditForm action={confirmPairingAction} submitLabel="校验并完成配对">
        <FormRow label="配对码">
          <input name="code" required autoComplete="off" className="form-input" placeholder="8 位配对码" />
        </FormRow>
        <FormRow label="Agent 名称(可选)" hint="留空则自动命名 self-paired-xxxxxxxx">
          <input name="name" className="form-input" placeholder="自报名称" />
        </FormRow>
      </EditForm>
    </>
  );
}
```
(Read another admin form page e.g. `redirects/new` to confirm the `className="form-input"`/`EditForm`/`FormRow` conventions match; adjust class names to whatever the codebase actually uses for inputs if `form-input` is not it.)

- [ ] **Step 3:** In `apps/admin/app/(admin)/agent-clients/page.tsx`, the header is currently `<div className="page-header"><h1>Agent 接入</h1></div>`. Add the confirm-entry link:

```tsx
      <div className="page-header">
        <h1>Agent 接入</h1>
        <Link href="/agent-clients/pair" className="btn-primary">输入配对码</Link>
      </div>
```
(`Link` already imported.)

- [ ] **Step 4:** Rewrite `apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx` to drop the code/prefix column and show confirming admin:

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
            <tr><th>创建</th><th>过期</th><th>状态</th><th>确认管理员</th><th>兑换出的 Client</th></tr>
          </thead>
          <tbody>
            {codes.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-3)" }}>暂无数据</td></tr>
            ) : (
              codes.map((c) => {
                const status = c.usedAt ? "已用" : c.expiresAt.getTime() < now ? "已过期" : "待确认";
                return (
                  <tr key={c.id}>
                    <td>{c.createdAt.toISOString().slice(0, 16).replace("T", " ")}</td>
                    <td>{c.expiresAt.toISOString().slice(0, 16).replace("T", " ")}</td>
                    <td>{status}</td>
                    <td>{c.usedByClient?.createdByAdminId ?? "—"}</td>
                    <td>{c.usedByClient?.name ?? "—"}</td>
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

- [ ] **Step 5: Verify.** `pnpm --filter @ghome/admin typecheck` — clean except `pair-endpoints.test.ts` (Task 5). `pnpm --filter @ghome/admin build` — success; route list contains `/agent-clients/pair` and `/agent-clients/pairing-codes`, NOT `/agent/pair`.

- [ ] **Step 6: Commit**

```bash
git add "apps/admin/app/(admin)/agent-clients/actions.ts" "apps/admin/app/(admin)/agent-clients/pair/page.tsx" "apps/admin/app/(admin)/agent-clients/page.tsx" "apps/admin/app/(admin)/agent-clients/pairing-codes/page.tsx"
git commit -m "feat(admin): authenticated pairing-code confirm page + action; codes log shows confirming admin"
```

---

## Task 5: 重写 pair-endpoints 测试 + E2E + 全量回归

**Files:** Modify `apps/admin/tests/pair-endpoints.test.ts`, `apps/admin/e2e/agent-clients.spec.ts`

- [ ] **Step 1:** Replace `apps/admin/tests/pair-endpoints.test.ts` entirely with (public POST gone; only GET skill.md behavior remains here — confirm logic is covered by `pairing-db.test.ts` from Task 2):

```ts
import { describe, it, expect, afterAll } from "vitest";
import { prisma } from "@ghome/db";
import { GET as pairSkillGet } from "@/app/agent/skill.md/route";
import { setPairingEnabled } from "@/lib/agent-pairing-db";

afterAll(async () => {
  await prisma.agentPairingCode.deleteMany({ where: { usedAt: null } });
  await setPairingEnabled(false, null);
});

const CODE_RE = /[ABCDEFGHJKMNPQRSTUVWXYZ23456789#$%@*+=-]{8}/;

describe("GET /agent/skill.md", () => {
  it("channel OFF: closed notice, no code minted", async () => {
    await setPairingEnabled(false, null);
    const before = await prisma.agentPairingCode.count();
    const r = await pairSkillGet();
    expect(r.status).toBe(200);
    const md = await r.text();
    expect(md).toContain("已关闭");
    expect(md).not.toMatch(CODE_RE);
    expect(await prisma.agentPairingCode.count()).toBe(before);
  });

  it("channel ON: mints a short code; doc instructs owner Admin-confirm, not POST", async () => {
    await setPairingEnabled(true, null);
    const before = await prisma.agentPairingCode.count();
    const r = await pairSkillGet();
    expect(r.status).toBe(200);
    const md = await r.text();
    // 含 8 位短码块
    expect(md).toMatch(/```\n[ABCDEFGHJKMNPQRSTUVWXYZ23456789#$%@*+=-]{8}\n```/);
    // 新指引:登录 Admin 输入配对码;不再出现公开 POST /agent/pair
    expect(md).toContain("输入配对码");
    expect(md).not.toContain("POST /agent/pair");
    expect(await prisma.agentPairingCode.count()).toBe(before + 1);
  });
});
```

- [ ] **Step 2: Run → PASS.** `pnpm --filter @ghome/admin test pair-endpoints` (2 cases).

- [ ] **Step 3:** Rewrite the self-pairing test in `apps/admin/e2e/agent-clients.spec.ts`. Keep the file's top constants (`ADMIN_EMAIL`/`ADMIN_PASSWORD`/`BASE`) and the signin pattern used by the existing test. Replace the single `test("self-pairing: ...")` block with:

```ts
test("pairing: enable channel → skill.md short code → owner confirms in Admin → token works", async ({
  page,
  request,
}) => {
  // 1. admin login
  await page.goto(`${BASE}/signin`);
  await page.locator('input[name="email"]').fill(ADMIN_EMAIL);
  await page.locator('input[name="password"]').fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "登录" }).click();
  await page.waitForURL(`${BASE}/`);

  // 2. enable channel
  await page.goto(`${BASE}/agent-clients`);
  if (await page.getByRole("button", { name: "开启通道" }).isVisible()) {
    await page.getByRole("button", { name: "开启通道" }).click();
  }

  // 3. Agent reads public skill.md (unauthenticated request), extract 8-char code
  const skill = await request.get(`${BASE}/agent/skill.md`);
  expect(skill.status()).toBe(200);
  const md = await skill.text();
  const m = md.match(/```\n([ABCDEFGHJKMNPQRSTUVWXYZ23456789#$%@*+=-]{8})\n```/);
  expect(m).toBeTruthy();
  const code = m![1];

  // 4. owner confirms in Admin (logged-in)
  await page.goto(`${BASE}/agent-clients/pair`);
  await page.locator('input[name="code"]').fill(code);
  await page.locator('input[name="name"]').fill(`e2e-pair-${Date.now()}`);
  await page.getByRole("button", { name: "校验并完成配对" }).click();

  // 5. lands on edit page with one-time token revealed
  await page.waitForURL(/\/agent-clients\/[^/]+\/edit\?敏感凭据：[已脱敏]
  const url = new URL(page.url());
  const 敏感凭据：[已脱敏] ?? "");
  expect(token).toMatch(/^ghagt_/);

  // 6. token works on the data API
  const apps = await request.get(`${BASE}/api/agent/v1/apps`, {
    headers: { authorization: `Bearer ${token}` },
  });
  expect(apps.status()).toBe(200);

  // 7. reusing the same code now fails (friendly error on the confirm page)
  await page.goto(`${BASE}/agent-clients/pair`);
  await page.locator('input[name="code"]').fill(code);
  await page.getByRole("button", { name: "校验并完成配对" }).click();
  await page.waitForURL(/\/agent-clients\/pair\?error=code_used/);

  // 8. restore: close channel
  await page.goto(`${BASE}/agent-clients`);
  if (await page.getByRole("button", { name: "关闭通道" }).isVisible()) {
    await page.getByRole("button", { name: "关闭通道" }).click();
  }
});
```
(If the existing test referenced helper consts only it used, leave shared ones. Keep any other tests in the file unchanged. The token is read from the post-confirm redirect URL `?敏感凭据：[已脱敏] rather than scraping the banner — robust and matches the action's redirect.)

- [ ] **Step 4: Verify full matrix.**
```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin test
pnpm --filter @ghome/admin build
pnpm lint
```
All green: typecheck clean; db 42/1-skip; admin suite green (pairing/pairing-db/pair-endpoints rewritten); build success (`/agent-clients/pair` emitted, `/agent/pair` absent); lint clean. Then E2E: ensure port 3100 free (`lsof -nP -iTCP:3100 -sTCP:LISTEN` → kill any `next dev`), `pnpm --filter @ghome/admin exec playwright test` → all green (Playwright auto-starts a fresh server). Kill any server you started.

- [ ] **Step 5: Commit**

```bash
git add apps/admin/tests/pair-endpoints.test.ts apps/admin/e2e/agent-clients.spec.ts
git commit -m "test(admin): rewrite pairing tests + e2e for short-code owner-confirm flow"
```

---

## Self-Review(规划者已执行)

- **Spec 覆盖**:§3 短码→Task1;§2/§4.4 confirmPairingCode/codePrefix=ticket/createdByAdminId→Task2;§4.1/§4.2 删公开 POST + skill.md 文案 + middleware→Task3;§4.3/§5 confirm 页+action+入口+日志页改列→Task4;§7 测试/E2E→Task2(confirm 单测)+Task5(skill.md 集成 + E2E);§6 安全(通道关时 confirm 亦拒、固定 content:published、createdByAdminId、短码不入库/日志)→Task2/3/4 + spec 已述;§8 C1–C5↔Task1–5;§9 未来项不实现。无遗漏。
- **占位符扫描**:无 TBD/TODO;每步含完整代码与命令;Task1/2/3/4 明确写出"此任务 typecheck 仅部分通过、余下任务修复"的顺序约定,非占位。
- **类型一致**:`generatePairingCode`/`randomTicket`/`PAIRING_CODE_TTL_MS`(Task1)↔ 被 Task2 引用一致;`confirmPairingCode(rawCode,adminId,name?)`/`ConfirmResult`(Task2)↔ Task4 `confirmPairingAction` 调用一致;`listPairingCodes` 加 `include:{usedByClient}` ↔ Task4 日志页 `c.usedByClient?.name/createdByAdminId` 一致;删除的 `redeemPairingCode`/`codePrefix`/`/agent/pair` 在 Task3/5 同步清除引用,Task1/2 已标注遗留到后续任务修复的顺序。
- **既有约定**:无 Prisma 迁移(codeHash 不变、codePrefix 值变、createdByAdminId 复用既有可空列);宿主 pnpm、Postgres 已起、无 Docker;`fileParallelism:false` 保持;子代理 commit 可能不带 Co-Authored-By(终态合并补)。
- **实现期核对点**:`AgentPairingCode.usedByClient` 关系名以 `schema.prisma` 实际为准(Task2 Step3e 已标注核对);admin 表单输入框 class(`form-input`)以现有表单页实际为准(Task4 Step2 已标注核对);E2E signin 选择器复用文件现有 test 写法。
