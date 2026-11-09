---
id: "doc-cd0e403538d8"
title: "Agent 接入引导卡重做 Implementation Plan"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-06-10-agent-onboarding-card-redesign.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-06-10-agent-onboarding-card-redesign.md"
sourceSha256: "73061c2a1c74194d04ffd957613264c5b103c9280291e355ab27d53c158aa702"
sourceSystem: "project-doc"
---

# Agent 接入引导卡重做 Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606100000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Agent%20%E6%8E%A5%E5%85%A5%E5%BC%95%E5%AF%BC%E5%8D%A1%E9%87%8D%E5%81%9A%20Implementation%20Plan.md)

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把运营后台 `/agent-clients` 简陋的"配对通道"卡片重做成「可复制话术 + 三步引导 + 内联输码」的接入引导卡,不改配对的信任模型与后端逻辑。

**Architecture:** 纯前端/文案改动。`page.tsx` 服务端组件计算数据并渲染三状态引导卡;新增两个小客户端组件(复制按钮、可折叠容器);把独立的 `/agent-clients/pair` 输码页内联进卡片并删除;`confirmPairingAction` 失败分支改为回跳列表页透出错误;同步 `pair.md` 的 Agent 侧步骤文案。后端、Prisma、scopes、token、`confirmPairingCode` 均不动。

**Tech Stack:** Next.js 15(App Router,Server Components + Server Actions)、React 19、TypeScript、Playwright(e2e)。

设计文档:`docs/superpowers/specs/2026-06-10-agent-onboarding-card-redesign-design.md`

---

## 文件结构

| 文件 | 责任 | 改动 |
|---|---|---|
| `apps/admin/components/CopyButton.tsx` | 复制任意文本 + "已复制"反馈的客户端按钮 | 新建 |
| `apps/admin/components/CollapsibleCard.tsx` | 默认展开、可手动收起的客户端容器 | 新建 |
| `apps/admin/app/(admin)/agent-clients/actions.ts` | `confirmPairingAction` 失败回跳改为 `/agent-clients?pairError=…` | 改 |
| `apps/admin/app/(admin)/agent-clients/page.tsx` | 三状态引导卡:话术+复制、②提示、③内联输码、错误条、通道开关收编、折叠;表格不变 | 重写 |
| `apps/admin/app/(admin)/agent-clients/pair/page.tsx` | 输码内联后冗余 | 删除 |
| `apps/admin/lib/agent-api/pairing-skill-md.ts` | `renderPairingSkillMd` 步骤文案对齐内联后 UI | 改 |
| `apps/admin/e2e/agent-clients.spec.ts` | 配对流程走列表页内联输码 + 复制按钮断言 | 改 |

**验证说明:** 每个任务用 `pnpm --filter @ghome/admin typecheck` 做快速门禁(宿主机需 Node 20 + pnpm 9;或用 `docker compose run --rm admin pnpm typecheck`)。e2e 需起全栈(`docker compose up -d`),集中在最后一个任务跑。本特性是 UI/文案改动,集成正确性由 e2e 保证,无需新增后端单测。

---

### Task 1: CopyButton 客户端组件

**Files:**
- Create: `apps/admin/components/CopyButton.tsx`

- [ ] **Step 1: 创建组件**

参照同目录 `TokenRevealBanner.tsx` 的 `navigator.clipboard` 用法。

```tsx
"use client";

import { useState } from "react";

export function CopyButton({
  text,
  label = "复制",
  copiedLabel = "已复制",
}: {
  text: string;
  label?: string;
  copiedLabel?: string;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className="btn-secondary"
      style={{ whiteSpace: "nowrap" }}
      onClick={() => {
        navigator.clipboard.writeText(text).then(() => setCopied(true));
      }}
    >
      {copied ? copiedLabel : label}
    </button>
  );
}
```

- [ ] **Step 2: 类型检查**

Run: `pnpm --filter @ghome/admin typecheck`
Expected: PASS(无类型错误)

- [ ] **Step 3: 提交**

```bash
git add apps/admin/components/CopyButton.tsx
git commit -m "feat(admin): 新增 CopyButton 复制按钮组件"
```

---

### Task 2: CollapsibleCard 客户端组件

**Files:**
- Create: `apps/admin/components/CollapsibleCard.tsx`

- [ ] **Step 1: 创建组件**

默认展开;收起后只剩一个切换按钮(显示 `closedLabel`)。折叠态不持久化。

```tsx
"use client";

import { useState, type ReactNode } from "react";

export function CollapsibleCard({
  children,
  defaultOpen = true,
  openLabel = "收起",
  closedLabel = "展开",
}: {
  children: ReactNode;
  defaultOpen?: boolean;
  openLabel?: string;
  closedLabel?: string;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div>
      <button
        type="button"
        className="btn-secondary"
        style={{ marginBottom: open ? 16 : 0 }}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? openLabel : closedLabel}
      </button>
      {open && children}
    </div>
  );
}
```

- [ ] **Step 2: 类型检查**

Run: `pnpm --filter @ghome/admin typecheck`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add apps/admin/components/CollapsibleCard.tsx
git commit -m "feat(admin): 新增 CollapsibleCard 可折叠容器组件"
```

---

### Task 3: confirmPairingAction 失败回跳改到列表页

**Files:**
- Modify: `apps/admin/app/(admin)/agent-clients/actions.ts`

输码内联进列表卡片后,错误要回到 `/agent-clients`(用 `pairError` 参数),不再回到即将删除的 `/pair` 页。成功分支(跳 `edit?token`)不变。

- [ ] **Step 1: 改两处失败 redirect**

找到 `confirmPairingAction` 函数体,把:

```ts
  if (!code) redirect("/agent-clients/pair?error=invalid_request");
  const res = await confirmPairingCode(code, me, name);
  if (!res.ok) redirect(`/agent-clients/pair?error=${res.code}`);
```

改为:

```ts
  if (!code) redirect("/agent-clients?pairError=invalid_request");
  const res = await confirmPairingCode(code, me, name);
  if (!res.ok) redirect(`/agent-clients?pairError=${res.code}`);
```

该函数其余部分(成功后 `logAuditAction` 与 `redirect(\`/agent-clients/${res.client.id}/edit?敏感凭据：[已脱敏]

- [ ] **Step 2: 类型检查**

Run: `pnpm --filter @ghome/admin typecheck`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add apps/admin/app/\(admin\)/agent-clients/actions.ts
git commit -m "refactor(admin): 配对失败回跳列表页(为内联输码做准备)"
```

---

### Task 4: 重写引导卡 page.tsx

**Files:**
- Modify(整文件重写): `apps/admin/app/(admin)/agent-clients/page.tsx`

三状态:通道关 → 开启 CTA;通道开+无 Agent → 引导卡展开;通道开+有 Agent → 引导卡裹进 `CollapsibleCard`。话术内嵌 `pairUrl`;③ 输码表单 `action={confirmPairingAction}`;错误条读 `searchParams.pairError`。下方客户端表格保持现状。

- [ ] **Step 1: 用以下完整内容替换整个文件**

```tsx
import { headers } from "next/headers";
import Link from "next/link";
import { listAgentClients } from "@/lib/agent-clients-db";
import { isPairingEnabled } from "@/lib/agent-pairing-db";
import { setPairingChannelAction, confirmPairingAction, rotateAction } from "./actions";
import { ConfirmSubmitButton } from "@/components/ConfirmSubmitButton";
import { CopyButton } from "@/components/CopyButton";
import { CollapsibleCard } from "@/components/CollapsibleCard";

export const dynamic = "force-dynamic";

const PAIR_PATH = "/agent/pair.md";

const PAIR_ERRORS: Record<string, string> = {
  invalid_request: "请填写配对码。",
  invalid_code: "配对码无效(不存在)。请让 Agent 重新读取获取新码。",
  code_used: "该配对码已被使用。请让 Agent 重新读取获取新码。",
  code_expired: "该配对码已过期(30 分钟有效)。请让 Agent 重新读取获取新码。",
  pairing_disabled: "公开配对通道当前已关闭,无法完成配对。",
};

function buildSnippet(pairUrl: string): string {
  return `这是我想让你接入的内容站。阅读 ${pairUrl} 并按页面说明完成配对,然后把拿到的 8 位配对码发给我。如果遇到安全风险,请与我逐一确认。`;
}

export default async function AgentClientsPage({
  searchParams,
}: {
  searchParams: Promise<{ pairError?: string }>;
}) {
  const [{ pairError }, clients, pairingEnabled, h] = await Promise.all([
    searchParams,
    listAgentClients(),
    isPairingEnabled(),
    headers(),
  ]);
  // 部署可用 ADMIN_BASE_URL 覆盖;否则按当前访问的 host 实时拼出完整可达 URL。
  const host = h.get("x-forwarded-host") ?? h.get("host");
  const proto = h.get("x-forwarded-proto") ?? "http";
  const base = process.env.ADMIN_BASE_URL ?? (host ? `${proto}://${host}` : "");
  const pairUrl = base + PAIR_PATH;
  const snippet = buildSnippet(pairUrl);
  const enableBound = setPairingChannelAction.bind(null, true);
  const disableBound = setPairingChannelAction.bind(null, false);
  const errorMsg = pairError ? (PAIR_ERRORS[pairError] ?? "配对失败,请重试。") : null;

  const guideBody = (
    <>
      {errorMsg && (
        <div
          className="dash-section"
          style={{ borderColor: "var(--danger, #c0392b)", color: "var(--danger, #c0392b)", marginBottom: 16 }}
        >
          {errorMsg}
        </div>
      )}

      <div style={{ marginBottom: 18 }}>
        <div style={{ fontSize: 12, color: "var(--text-3)", letterSpacing: "0.04em", marginBottom: 8 }}>
          ① 把这段发给你的 Agent
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
          <div
            style={{
              flex: 1,
              border: "1px solid var(--border, #e2e2e2)",
              borderRadius: 8,
              padding: "12px 14px",
              fontSize: 13,
              lineHeight: 1.7,
              background: "var(--bg-2, #fafafa)",
            }}
          >
            {snippet}
          </div>
          <CopyButton text={snippet} />
        </div>
      </div>

      <div style={{ fontSize: 13, color: "var(--text-2)", marginBottom: 18 }}>
        ② Agent 读取后会返回一串 <strong>8 位配对码</strong>。
      </div>

      <div>
        <div style={{ fontSize: 12, color: "var(--text-3)", letterSpacing: "0.04em", marginBottom: 8 }}>
          ③ 把配对码填到这里完成接入
        </div>
        <form action={confirmPairingAction} style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <input
            name="code"
            required
            autoComplete="off"
            className="form-input"
            placeholder="8 位配对码"
            style={{ width: 160, letterSpacing: "0.15em" }}
          />
          <input name="name" className="form-input" placeholder="Agent 名称(可选)" style={{ width: 200 }} />
          <button type="submit" className="btn-primary">校验并接入</button>
        </form>
        <div style={{ fontSize: 12, color: "var(--text-3)", marginTop: 8 }}>
          校验通过后,本页会一次性显示该 Agent 的 token。
        </div>
      </div>
    </>
  );

  return (
    <>
      <div className="page-header">
        <h1>Agent 接入</h1>
      </div>

      <div className="dash-section" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
          <h2 style={{ marginTop: 0 }}>接入一个 AI Agent</h2>
          <span style={{ fontSize: 13 }}>
            {pairingEnabled ? (
              <span style={{ color: "#16a34a" }}>● 公开通道已开启</span>
            ) : (
              <span style={{ color: "var(--text-3)" }}>○ 公开通道未开启</span>
            )}
            {"　"}
            <Link href="/agent-clients/pairing-codes" style={{ color: "var(--primary)" }}>
              配对码日志
            </Link>
          </span>
        </div>

        {pairingEnabled ? (
          <>
            <p style={{ color: "var(--text-2)", marginTop: 4 }}>
              Agent 自助读取配对页,你在第 ③ 步输码确认即可接入。
            </p>
            <form action={disableBound} style={{ marginBottom: 16 }}>
              <button type="submit" className="btn-secondary">关闭通道</button>
            </form>
            {clients.length === 0 ? (
              guideBody
            ) : (
              <CollapsibleCard defaultOpen openLabel="收起" closedLabel="+ 接入新 Agent">
                {guideBody}
              </CollapsibleCard>
            )}
          </>
        ) : (
          <>
            <p style={{ color: "var(--text-2)", marginTop: 4 }}>
              公开自助配对通道未开启,开启后即可把配对话术发给 Agent。
            </p>
            <form action={enableBound}>
              <button type="submit" className="btn-primary">开启通道</button>
            </form>
          </>
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

- [ ] **Step 2: 类型检查 + 构建**

Run: `pnpm --filter @ghome/admin typecheck && pnpm --filter @ghome/admin build`
Expected: typecheck PASS;build 成功(无 "use client"/server action 边界报错)

- [ ] **Step 3: 提交**

```bash
git add apps/admin/app/\(admin\)/agent-clients/page.tsx
git commit -m "feat(admin): 重做 Agent 接入引导卡(话术+三步+内联输码)"
```

---

### Task 5: 删除冗余的独立输码页

**Files:**
- Delete: `apps/admin/app/(admin)/agent-clients/pair/page.tsx`

输码已内联进列表卡,`/agent-clients/pair` 路由不再被任何处链接(Task 4 已移除入口),且 `confirmPairingAction` 不再回跳它(Task 3)。

- [ ] **Step 1: 删除文件**

```bash
git rm apps/admin/app/\(admin\)/agent-clients/pair/page.tsx
```

- [ ] **Step 2: 确认无悬挂引用 + 构建**

Run: `grep -rn "agent-clients/pair" apps/admin/app apps/admin/lib apps/admin/components`
Expected: 无任何结果(注意:`pairing-codes` 是另一个路由,不受影响;`pair.md` 文案在 Task 6 处理)

Run: `pnpm --filter @ghome/admin build`
Expected: 构建成功

- [ ] **Step 3: 提交**

```bash
git add -A apps/admin/app/\(admin\)/agent-clients
git commit -m "refactor(admin): 删除内联后冗余的独立配对输码页"
```

---

### Task 6: 同步 pair.md 的 Agent 侧步骤文案

**Files:**
- Modify: `apps/admin/lib/agent-api/pairing-skill-md.ts`

内联后已无独立「输入配对码」按钮,Agent 文档里给 owner 的步骤要对齐新 UI。

- [ ] **Step 1: 改 `renderPairingSkillMd` 的步骤 2、3**

把:

```ts
    "2. 顶部导航进入「Agent 接入」→ 点「输入配对码」",
    "3. 填入这串配对码(可选填一个 Agent 名称)并提交",
```

改为:

```ts
    "2. 顶部导航进入「Agent 接入」",
    "3. 在「接入一个 AI Agent」卡片第 ③ 步填入这串配对码(可选填一个 Agent 名称)并提交",
```

其余行(1、4、5 及前后文)保持不变。

- [ ] **Step 2: 类型检查**

Run: `pnpm --filter @ghome/admin typecheck`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add apps/admin/lib/agent-api/pairing-skill-md.ts
git commit -m "docs(admin): pair.md 步骤文案对齐内联输码 UI"
```

---

### Task 7: 更新 e2e 走内联输码流程

**Files:**
- Modify: `apps/admin/e2e/agent-clients.spec.ts`

现有用例跳 `/agent-clients/pair` 并点「校验并完成配对」、失败回 `/pair?error=`。改为在 `/agent-clients` 列表页内联输码、按钮「校验并接入」、失败回 `/agent-clients?pairError=`,并加一条"复制话术按钮存在"的断言。

- [ ] **Step 1: 改 owner 确认段(原 36–40 行)**

把:

```ts
  // 4. owner confirms in Admin (logged-in)
  await page.goto(`${BASE}/agent-clients/pair`);
  await page.locator('input[name="code"]').fill(code);
  await page.locator('input[name="name"]').fill(agentName);
  await page.getByRole("button", { name: "校验并完成配对" }).click();
```

改为:

```ts
  // 4. owner confirms in Admin — 列表页内联输码卡
  await page.goto(`${BASE}/agent-clients`);
  await expect(page.getByRole("button", { name: "复制" })).toBeVisible();
  await page.locator('input[name="code"]').fill(code);
  await page.locator('input[name="name"]').fill(agentName);
  await page.getByRole("button", { name: "校验并接入" }).click();
```

- [ ] **Step 2: 改"重用旧码失败"段(原 53–57 行)**

把:

```ts
  // 7. reusing the same code now fails (friendly error on the confirm page)
  await page.goto(`${BASE}/agent-clients/pair`);
  await page.locator('input[name="code"]').fill(code);
  await page.getByRole("button", { name: "校验并完成配对" }).click();
  await page.waitForURL(/\/agent-clients\/pair\?error=code_used/);
```

改为:

```ts
  // 7. reusing the same code now fails (friendly error on the list card)
  await page.goto(`${BASE}/agent-clients`);
  await page.locator('input[name="code"]').fill(code);
  await page.getByRole("button", { name: "校验并接入" }).click();
  await page.waitForURL(/\/agent-clients\?pairError=code_used/);
  await expect(page.getByText("该配对码已被使用。请让 Agent 重新读取获取新码。")).toBeVisible();
```

其余段(登录、开/关通道、读 pair.md 取码、token 调 API、列表行轮换)保持不变。

- [ ] **Step 3: 起全栈并跑该 e2e**

Run:
```bash
docker compose up -d
pnpm --filter @ghome/admin e2e -- agent-clients.spec.ts
```
Expected: 该 spec 全绿(配对→token 可用→重用旧码报错并透出中文→轮换→关闭通道)

- [ ] **Step 4: 提交**

```bash
git add apps/admin/e2e/agent-clients.spec.ts
git commit -m "test(admin): e2e 配对流程改走列表页内联输码"
```

---

## 完成判定

- `/agent-clients` 顶部为引导卡,含可一键复制、内嵌正确 `pairUrl` 的话术。
- 输码在卡内就地完成;`/agent-clients/pair` 路由已删除且无悬挂引用。
- 通道开/关、配对码日志入口在卡片内,行为与现状等价。
- 三状态(通道关 / 通道开无 Agent / 通道开有 Agent)渲染正确。
- `pair.md` 的 owner 步骤文案与新 UI 一致。
- e2e `agent-clients.spec.ts` 全绿,既有配对/发 token 行为不变。
