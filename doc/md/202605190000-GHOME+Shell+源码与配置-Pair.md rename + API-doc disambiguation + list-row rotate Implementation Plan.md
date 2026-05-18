---
id: "doc-79b7be40020c"
title: "Pair.md rename + API-doc disambiguation + list-row rotate Implementation Plan"
date: "2026-05-19T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-19-pair-md-rename-and-list-rotate.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-19-pair-md-rename-and-list-rotate.md"
sourceSha256: "fe6d2a21cdfe01d5c19579fe94dd12c0b86425546f3cb6171ee8abdd9ffbce95"
sourceSystem: "project-doc"
---

# Pair.md rename + API-doc disambiguation + list-row rotate Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-19-pair-md-rename-and-list-rotate.md`

> 整理日期：2026-05-19 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Rename the public bootstrap endpoint `GET /agent/skill.md` → `GET /agent/pair.md` (old removed), add a prominent "this is the pairing bootstrap, NOT the API doc" disambiguation to both bootstrap renders, and add a one-click「轮换」(rotate token) action to each agent-clients list row.

**Architecture:** Pure rename (move the route folder, update middleware exact-allow, the admin page's displayed URL, and the test import) + a shared disambiguation block prepended in both `pairing-skill-md` renders + a list-row `<form>` reusing the existing `rotateAction` + `ConfirmSubmitButton`. No new data model, no new server action, no Prisma migration.

**Tech Stack:** Next.js 15 App Router, vitest, Playwright.

**Spec:** [docs/superpowers/specs/2026-05-18-agent-self-pairing-design.md](../specs/2026-05-18-agent-self-pairing-design.md) (revision dated 2026-05-19).

---

## File Structure

- Move `apps/admin/app/agent/skill.md/route.ts` → `apps/admin/app/agent/pair.md/route.ts` (content unchanged except the caveat comment wording)
- Modify `apps/admin/middleware.ts` — public allowlist `/agent/skill.md` → `/agent/pair.md`
- Modify `apps/admin/app/(admin)/agent-clients/page.tsx` — `PAIR_PATH` const → `/agent/pair.md`; add per-row rotate `<form>` + 2 imports
- Modify `apps/admin/lib/agent-api/pairing-skill-md.ts` — shared `DISAMBIGUATION` block prepended in both `renderPairingSkillMd` and `renderPairingClosedMd`
- Modify `apps/admin/tests/pair-endpoints.test.ts` — import path → `pair.md/route`; add disambiguation assertions
- Modify `apps/admin/e2e/agent-clients.spec.ts` — bootstrap path → `/agent/pair.md`; add list-row rotate step

---

**Files:** move `apps/admin/app/agent/skill.md/route.ts` → `apps/admin/app/agent/pair.md/route.ts`; modify `apps/admin/middleware.ts`, `apps/admin/app/(admin)/agent-clients/page.tsx`, `apps/admin/tests/pair-endpoints.test.ts`

- [ ] **Step 1: Move the route file (preserve git history)**

```bash
mkdir -p "apps/admin/app/agent/pair.md"
git mv "apps/admin/app/agent/skill.md/route.ts" "apps/admin/app/agent/pair.md/route.ts"
rmdir "apps/admin/app/agent/skill.md" 2>/dev/null || true
```

- [ ] **Step 2: Update the caveat comment in the moved file**

In `apps/admin/app/agent/pair.md/route.ts` replace the first comment line:
```
// 目录名 `skill.md` 是字面路径段 → 公开 URL `/agent/skill.md`(非文件扩展名,勿"整理"目录名)。
```
with:
```
// 目录名 `pair.md` 是字面路径段 → 公开 URL `/agent/pair.md`(非文件扩展名,勿"整理"目录名)。
```
Leave everything else in the file byte-for-byte unchanged (imports, `runtime`/`dynamic`, GET logic).

- [ ] **Step 3: Update middleware exact-allow**

In `apps/admin/middleware.ts`, change the line `    pathname === "/agent/skill.md" ||` to `    pathname === "/agent/pair.md" ||`. Change nothing else (keep `/api/agent/` prefix allow, keep `/agent-clients/*` NOT allowed so it stays session-guarded).

- [ ] **Step 4: Update the admin page's displayed public URL**

In `apps/admin/app/(admin)/agent-clients/page.tsx`, change `const PAIR_PATH = "/agent/skill.md";` to `const PAIR_PATH = "/agent/pair.md";`. Nothing else in this task.

- [ ] **Step 5: Update the test import path**

In `apps/admin/tests/pair-endpoints.test.ts`, change:
```ts
import { GET as pairSkillGet } from "@/app/agent/skill.md/route";
```
to:
```ts
import { GET as pairSkillGet } from "@/app/agent/pair.md/route";
```
Do not change any assertions in this task (Task 2 adds the disambiguation assertions).

- [ ] **Step 6: Verify**

```bash
pnpm --filter @ghome/admin exec tsc --noEmit 2>&1 | grep -E "error TS" || echo "typecheck clean"
pnpm --filter @ghome/admin test pair-endpoints
pnpm --filter @ghome/admin build 2>&1 | grep -E "/agent/(pair\.md|skill\.md)|/agent-clients"
```
Expected: typecheck clean (zero errors); `pair-endpoints` 2/2 pass; build route list shows `ƒ /agent/pair.md` and NOT `/agent/skill.md`, and still shows `/agent-clients`. Grep the whole admin app to confirm no stale ref:
```bash
grep -rn "agent/skill.md" apps/admin --include='*.ts' --include='*.tsx' | grep -v '/.next/' || echo "no stale /agent/skill.md ✓"
```
Expected: only `pair-endpoints.test.ts` must NOT appear (we fixed it); zero matches is the pass.

- [ ] **Step 7: Commit**

```bash
git add "apps/admin/app/agent" apps/admin/middleware.ts "apps/admin/app/(admin)/agent-clients/page.tsx" apps/admin/tests/pair-endpoints.test.ts
git commit -m "refactor(admin): rename public bootstrap /agent/skill.md → /agent/pair.md"
```

---

**Files:** Modify `apps/admin/lib/agent-api/pairing-skill-md.ts`, `apps/admin/tests/pair-endpoints.test.ts`

- [ ] **Step 1: Add failing assertions to `apps/admin/tests/pair-endpoints.test.ts`**

In the "channel OFF" test, after the existing `expect(md).toContain("已关闭");` line add:
```ts
    expect(md).toContain("不是 API 文档");
    expect(md).toContain("/api/agent/v1/skill.md");
```
In the "channel ON" test, after the existing `expect(md).toContain("输入配对码");` line add:
```ts
    expect(md).toContain("不是 API 文档");
```

- [ ] **Step 2: Run → FAIL**

Run: `pnpm --filter @ghome/admin test pair-endpoints`
Expected: FAIL — the closed notice does not yet contain `不是 API 文档` / `/api/agent/v1/skill.md` (and the open doc lacks the exact phrase `不是 API 文档`).

- [ ] **Step 3: Add the shared disambiguation block to `apps/admin/lib/agent-api/pairing-skill-md.ts`**

At the top of the file (before `renderPairingSkillMd`), add:
```ts
// 醒目区分:杜绝把"配对引导页"误当作鉴权后的 API 文档(本轮修订动因)。两态文档均须含。
const DISAMBIGUATION: string[] = [
  "> ⚠️ **这是配对引导页,不是 API 文档。** 本页每次访问都会换一枚新配对码。",
  "> 配对完成、owner 在 Admin 校验后你会拿到 Bearer token;真正的个性化 API 文档是另一个地址且须带 敏感凭据：[已脱敏]
  "> `GET /api/agent/v1/skill.md`(Header `Authorization: Bearer <token>`)。",
  "",
];
```
Then in `renderPairingSkillMd`, insert `...DISAMBIGUATION,` into the returned array immediately AFTER the closing frontmatter `"---",` and its following `"",` and the `# Ghome Agent 配对` title line — concretely, place it right after the title+blank so the array becomes:
```ts
    "---",
    "name: ghome-agent-pairing",
    "description: Pair this agent — hand the short code to your owner to confirm in Admin",
    "---",
    "",
    "# Ghome Agent 配对",
    "",
    ...DISAMBIGUATION,
    "配对成功默认仅授予 `content:published`(等价于用户站公开可见内容)。",
```
And in `renderPairingClosedMd`, similarly insert `...DISAMBIGUATION,` right after its title block:
```ts
    "---",
    "name: ghome-agent-pairing",
    "description: Pairing channel closed",
    "---",
    "",
    "# 自助配对通道已关闭",
    "",
    ...DISAMBIGUATION,
    "管理员当前未开启公开自助配对。请联系管理员开启,或改用管理员直接签发的授权码。",
```
(Read the current file first to match the exact existing surrounding lines; only insert the `...DISAMBIGUATION,` line — do not alter other lines. If the current array shape differs slightly, the rule is: insert the spread immediately after the `# …` title line and its trailing `"",`, before the first body sentence.)

- [ ] **Step 4: Run → PASS**

Run: `pnpm --filter @ghome/admin test pair-endpoints`
Expected: 2/2 pass (both channel ON and OFF md now contain `不是 API 文档`; closed md also contains `/api/agent/v1/skill.md`).

- [ ] **Step 5: typecheck + commit**

```bash
pnpm --filter @ghome/admin exec tsc --noEmit 2>&1 | grep -E "error TS" || echo "typecheck clean"
git add apps/admin/lib/agent-api/pairing-skill-md.ts apps/admin/tests/pair-endpoints.test.ts
git commit -m "feat(admin): prominent 'pairing bootstrap, not API doc' disambiguation in both renders"
```

---

**Files:** Modify `apps/admin/app/(admin)/agent-clients/page.tsx`

- [ ] **Step 1: Add the two imports**

In `apps/admin/app/(admin)/agent-clients/page.tsx`:
- change `import { setPairingChannelAction } from "./actions";` → `import { setPairingChannelAction, rotateAction } from "./actions";`
- add a new import line: `import { ConfirmSubmitButton } from "@/components/ConfirmSubmitButton";`

(`rotateAction(id: string): Promise<void>` already exists in `apps/admin/app/(admin)/agent-clients/actions.ts` — it does `rotateAgentToken` + audit `agentClient.rotate` + `redirect('/agent-clients/{id}/edit?敏感凭据：[已脱敏] `ConfirmSubmitButton` is the existing `"use client"` component with a `confirm` prop that gates submit via `window.confirm`.)

- [ ] **Step 2: Replace the action cell to add the rotate form**

Replace this exact block in the row map:
```tsx
                  <td>
                    <Link href={`/agent-clients/${c.id}/edit`} style={{ color: "var(--primary)" }}>
                      编辑
                    </Link>
                  </td>
```
with:
```tsx
                  <td>
                    <Link href={`/agent-clients/${c.id}/edit`} style={{ color: "var(--primary)" }}>
                      编辑
                    </Link>
                    {"　"}
                    <form action={rotateAction.bind(null, c.id)} style={{ display: "inline" }}>
                      <ConfirmSubmitButton
                        confirm={`轮换会立即作废 ${c.name} 当前 token,确定?`}
                        style={{ background: "none", border: "none", padding: 0, color: "var(--primary)", cursor: "pointer" }}
                      >
                        轮换
                      </ConfirmSubmitButton>
                    </form>
                  </td>
```
(`rotateAction.bind(null, c.id)` adapts the `(id)=>Promise<void>` action to the `<form action>` `(FormData)=>` signature — the bound `id` is fixed, the FormData arg is ignored, exactly how the existing edit page binds rotate/delete. `display:inline` keeps the form on the same line as the 编辑 link.)

- [ ] **Step 3: Verify**

```bash
pnpm --filter @ghome/admin exec tsc --noEmit 2>&1 | grep -E "error TS" || echo "typecheck clean"
pnpm --filter @ghome/admin build 2>&1 | grep -E "/agent-clients( |$)"
pnpm --filter @ghome/admin test 2>&1 | grep -E "Test Files|Tests "
```
Expected: typecheck clean; build success with `/agent-clients` route present; full admin suite green (no regression — this is a UI-only change, no test asserts the old single-link cell).

- [ ] **Step 4: Commit**

```bash
git add "apps/admin/app/(admin)/agent-clients/page.tsx"
git commit -m "feat(admin): one-click 轮换 (rotate token) action on each agent-clients list row"
```

---

**Files:** Modify `apps/admin/e2e/agent-clients.spec.ts`

> First `Read` `apps/admin/e2e/agent-clients.spec.ts` to reuse its exact top constants (`ADMIN_EMAIL`/`ADMIN_PASSWORD`/`BASE`) and signin pattern. There is one test in it (the pairing test).

- [ ] **Step 1: Update the bootstrap path and add a list-row rotate step**

In the single pairing test:
1. Change `await request.get(\`${BASE}/agent/skill.md\`)` → `await request.get(\`${BASE}/agent/pair.md\`)`. Leave the regex that extracts the 8-char code and the rest of the existing flow (login → enable channel → fetch pair.md → extract code → confirm at `/agent-clients/pair` → land on edit?敏感凭据：[已脱敏] use token on `/api/agent/v1/apps` 200 → reuse code → `?error=code_used`) intact.
2. BEFORE the final "close channel" restore step, insert a list-row rotate sub-flow:
```ts
  // list-row 轮换:回列表,对刚配出的 Agent 那行点「轮换」(接受确认弹窗)→ 新 token 仍可用
  page.on("dialog", (d) => d.accept());
  await page.goto(`${BASE}/agent-clients`);
  const row = page.locator("tr", { hasText: agentName });
  await row.getByRole("button", { name: "轮换" }).click();
  await page.waitForURL(/\/agent-clients\/[^/]+\/edit\?敏感凭据：[已脱敏]
  const rotated = decodeURIComponent(new URL(page.url()).searchParams.get("token") ?? "");
  expect(rotated).toMatch(/^ghagt_/);
  const apps2 = await request.get(`${BASE}/api/agent/v1/apps`, {
    headers: { authorization: `Bearer ${rotated}` },
  });
  expect(apps2.status()).toBe(200);
```
This requires the test to know the Agent's name it created. The existing test fills `input[name="name"]` with a timestamped value — capture it into a `const agentName = \`e2e-pair-${Date.now()}\`;` declared once and used both for the confirm-page name input and the `hasText: agentName` row locator. If the existing test currently inlines the name, refactor it to that single `agentName` const (minimal change). Keep `page.on("dialog", ...)` registered once before the click (the rotate uses `ConfirmSubmitButton` → `window.confirm`).

- [ ] **Step 2: Full verification matrix (all must be green — no exceptions)**

```bash
pnpm --filter @ghome/admin exec tsc --noEmit 2>&1 | grep -E "error TS" || echo "typecheck clean"
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin test
pnpm --filter @ghome/admin build
pnpm lint
```
Expected: typecheck zero errors; db 42 passed/1 skipped; admin suite all green; build success — route list has `/agent/pair.md` and `/agent-clients/pair`, does NOT have `/agent/skill.md` or `/agent/pair` (POST); lint clean (a pre-existing unrelated `apps/web` `<img>` warning is acceptable, not an error). If an UNTOUCHED file shows the known shared-Postgres cleanup flake, re-run once and note; the files this branch changed must be solidly green and typecheck zero-error.

Then E2E: ensure port 3100 free first (`lsof -nP -iTCP:3100 -sTCP:LISTEN` → if a `next dev` pid, `kill` it so Playwright starts a FRESH server with the new code), then `pnpm --filter @ghome/admin exec playwright test`. Expected: all green (the rewritten pairing test incl. the new list-row rotate sub-flow). Kill any dev server you started afterward (leave 3100 free).

- [ ] **Step 3: Commit**

```bash
git add apps/admin/e2e/agent-clients.spec.ts
git commit -m "test(admin): e2e uses /agent/pair.md + exercises list-row rotate"
```

---

## Self-Review (规划者已执行)

- **Spec 覆盖**:§4.1 改名(route 移位 + middleware + 引导文档)→Task1+Task2;§4.1 醒目区分(两态)→Task2;§5 列表行轮换→Task3;§7 测试导入路径改 + 区分语断言→Task1(import)+Task2(assertions);§7 E2E(pair.md + 列表行轮换)→Task4;顶部修订 note 的"无新数据模型/迁移"→全程未碰 schema/db。§8 历史切片表不动(spec note 已说明)。无遗漏。
- **占位符扫描**:无 TBD/TODO;每步含完整代码与命令;Task2 Step3 给出"读现文件、仅插入 spread 行"的确定规则,非占位。
- **类型一致**:`rotateAction(id:string)` 既有签名 ↔ Task3 `rotateAction.bind(null,c.id)` 与现编辑页 bind 模式一致;`ConfirmSubmitButton` props(`confirm`/`children`/`style`)↔ Task3 用法一致;`pairSkillGet` import 改 `@/app/agent/pair.md/route` ↔ Task1 路由移位后实际路径一致;`DISAMBIGUATION: string[]` ↔ 两处 `...DISAMBIGUATION,` spread 一致;测试断言字符串 `不是 API 文档` / `/api/agent/v1/skill.md` ↔ Task2 文案块实际包含。
- **既有约定**:无 Prisma 迁移;宿主 pnpm、Postgres 已起、无 Docker;`fileParallelism:false` 保持;子代理 commit 可能不带 Co-Authored-By(终态合并补)。
- **实现期核对点**:Task2 Step3 要先读 `pairing-skill-md.ts` 现状,按"标题行后插入 spread"规则插(已写明);Task4 E2E signin 选择器/常量复用文件现有写法(已写明先 Read)。
