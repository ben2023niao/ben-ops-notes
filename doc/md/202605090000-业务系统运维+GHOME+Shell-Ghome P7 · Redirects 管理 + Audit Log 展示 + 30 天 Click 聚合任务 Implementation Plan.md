---
id: "doc-9eded9024e58"
title: "Ghome P7 · Redirects 管理 + Audit Log 展示 + 30 天 Click 聚合任务 Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Kubernetes", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p7-redirects-audit-aggregate.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p7-redirects-audit-aggregate.md"
sourceSha256: "370a1f84d70c7b8b4526ff35e611c1c6128a40a548872da37bc90eba0af8e175"
sourceSystem: "project-doc"
---

# Ghome P7 · Redirects 管理 + Audit Log 展示 + 30 天 Click 聚合任务 Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605090000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20P7%20%C2%B7%20Redirects%20%E7%AE%A1%E7%90%86%20%2B%20Audit%20Log%20%E5%B1%95%E7%A4%BA%20%2B%2030%20%E5%A4%A9%20Click%20%E8%81%9A%E5%90%88%E4%BB%BB%E5%8A%A1%20Implementation%20Plan.md)

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收尾 admin 的运营闭环。三件事:
1. **Redirects 管理 UI**:`/redirects` 列表(过滤 ownerKind / disabled / 关键词)+ `/redirects/[id]/edit`(改 `targetUrl` 走 `validateForWrite` 异步 DNS、切 `disabled`、写 audit_log、不改 ownerKind / ownerId 这两个由内容侧维护的字段)
2. **Audit Log 展示**:`/audit-log` 列表(过滤 targetType / action 前缀 / adminUser / 时间段 + 分页)+ `/audit-log/[id]` 详情(渲染 `diffJson` 的 before/after)
3. **30 天 click_events 聚合定时任务**:在 `packages/db/src/lib/click-aggregate.ts` 实现 spec §3.2 的 SQL(单事务 + `pg_advisory_xact_lock(8131421)` + INSERT ON CONFLICT 累加 + 同事务 DELETE > 30d)。出口两个:
   - `apps/admin/app/api/cron/aggregate-clicks/route.ts`(Bearer 鉴权 + 调用聚合函数 + 写 audit_log)— 用于云端 cron 触发(Vercel cron / GitHub Actions / k8s CronJob 都能用,接口稳定)
   - `pnpm db:aggregate-clicks`(CLI,本地手跑 / 应急 / 集成测试)

**完成判据(spec §6):** 改一个 redirect 的 target → web `/r/:id` 跳到新地址;`/audit-log` 能查到这次修改。再跑 `pnpm db:aggregate-clicks` 一次 → `click_daily_stats` 行数随之上涨,`click_events` 中 > 30 天的行被清掉,**重复跑不会双倍累加**(advisory lock + 单事务保证)。

**Architecture:**
- **Redirect edit 写路径**:server action 接收 `{ targetUrl, disabled }` → `validateForWrite(targetUrl)` 异步校验(P3 url-policy)→ 通过则 `prisma.redirect.update` + `logAuditAction("redirect.update", ...)` + `revalidateWeb(...)`(redirect 没有 web 端 cache tag — 详见 Tricky Bits T2.4,**保持空数组 / 只 revalidate `home`**)。失败则 throw,form 显示错误。
- **Audit log 视图**:纯 read,无写操作。SSR 拉数据,`URLSearchParams` 驱动过滤。`diffJson` 用一个简单 `<pre>` 块加颜色区分 before/after(可选用 `DiffViewer.tsx` 客户端组件做 key-by-key diff,但 MVP 只用 `JSON.stringify(_, null, 2)` 即可)。
- **聚合任务**:核心函数 `aggregateClickEvents(prisma)` 在 `packages/db` 内,纯函数 — 接收 `PrismaClient` 用 `$transaction` 跑两条 raw SQL。两个出口都只是 thin wrapper。
  - **HTTP route `/api/cron/aggregate-clicks`**:**不**用 Auth.js session(cron 走 Bearer 不是 cookie),用 `process.env.CRON_SECRET` 校验 `Authorization: Bearer <secret>`。返回 `{ aggregatedRows, deletedRows, ms }`。一次失败应被外部调度器重试,advisory lock 保证不双跑。
  - **CLI 脚本**:打开 PrismaClient 跑函数,console.log 结果,断开连接 exit。

**Tech Stack:** 全部已有依赖,**无新增包**。
- `@ghome/db` 增 `aggregateClickEvents`(`prisma.$transaction` + raw SQL)
- `validateForWrite`(P3 url-policy,异步 2s DNS)
- `logAuditAction`(P4 admin/lib/audit.ts)
- `revalidateWeb`(P4 admin/lib/revalidate.ts)— redirect 不挂 web cache tag,见 T2 Tricky Bits

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §3.2 redirects + click_events + click_daily_stats(含聚合 SQL)+ audit_log、§6 P7 行。

**前置假设:** P6 已完成,`p6-collections-crud` 标签存在;`redirects` 表有 ≥29 条 `disabled=true` 行(P1 seed)+ 若干 P6 创建的 external item redirect(`disabled=false`);`click_events` 在 P3 上线后开始积累(本地若没有手跑 `/r/:id` 数据可能为 0,Tests 里要塞构造数据);`audit_log` 表自 P4 起每个 admin 写操作都已有行;Auth.js + middleware 一切就绪;web 已通过 `unstable_after`/cache tag 装备完成(P3/P6)。

---

## File Structure(P7 末态)

```
apps/admin/
├─ app/
│  ├─ (admin)/
│  │  ├─ redirects/
│  │  │  ├─ page.tsx                                  # T2:列表 + 过滤
│  │  │  └─ [id]/edit/page.tsx                        # T2:编辑(targetUrl + disabled)
│  │  └─ audit-log/
│  │     ├─ page.tsx                                  # T3:列表 + 过滤 + 分页
│  │     └─ [id]/page.tsx                             # T3:详情 + diff 渲染
│  └─ api/
│     └─ cron/
│        └─ aggregate-clicks/
│           └─ route.ts                               # T4:HTTP cron 入口(Bearer 鉴权)
├─ components/
│  ├─ AdminHeader.tsx                                 # T1 改:加 /redirects 与 /audit-log 入口
│  └─ DiffViewer.tsx                                  # T3:渲染 before/after diff
├─ lib/
│  └─ db.ts                                           # T1/T2/T3 扩展:redirect / audit-log 查询

packages/db/
├─ src/
│  └─ lib/
│     └─ click-aggregate.ts                           # T4:核心聚合函数(纯)
├─ scripts/
│  └─ aggregate-click-events.ts                       # T4:CLI 入口(pnpm db:aggregate-clicks)
├─ tests/
│  └─ click-aggregate.test.ts                         # T4:集成测试(打 30+ 天 events,跑两次,断言幂等)
└─ package.json                                       # T4:加 scripts.db:aggregate-clicks
```

新文件 ~9,改动 ~3。

---

## Conventions(整个 P7 共享)

- **Redirect edit 写校验**:**必走** `validateForWrite`(异步 DNS),否则可能落入"字面值合法但 DNS 解到内网"残余风险;表单失败时 throw 字符串错误,顶层让 EditForm 显示 toast(P5 P6 都用过这个 pattern)
- **Audit log 是只读视图**:不允许编辑 / 删除 audit_log 行(法律/合规意义上的"记录")
- **Cron route 鉴权**:`Authorization: Bearer <CRON_SECRET>`,`CRON_SECRET` 在 `apps/admin/.env`(dev)/ 部署 env(prod)。**不要复用 `REVALIDATE_SECRET`** — 不同语义不同泄露面。`process.env.CRON_SECRET` 必须在 module load 时断言存在(参考 `lib/click-tracking.ts` 的 `IP_HASH_SECRET` pattern)
- **Cron route 不写 audit_log 的 admin_user_id**:cron 没有 adminUser。若一定要记录,加一个保留 admin_user (`system-cron`) 或者单独写一行 `system_event_log`。**MVP 先不写 audit_log**,只 `console.log` 结果 — audit_log 表 schema 强制要求 `admin_user_id`,加进去会破坏不变量
- **Pagination**:audit-log 列表用 cursor 或 offset 都可,**MVP 用 offset + limit=50**,简单够用。`?page=2` 即 offset=50
- **Time format**:UI 全用 `toISOString().slice(0, 16).replace("T", " ")`(YYYY-MM-DD HH:MM)与现有列表一致
- **每次 redirect 写操作都 audit_log + revalidate**:revalidate 仅 `home` tag(因为前台没有 redirect 详情页 cache,只是 ItemCards 嵌入了 `/r/:id` 链接 — link href 不变,改 targetUrl 不影响 RSC 输出)
- **不做(P7 范围外)**:批量勾选 + 批量 toggle disabled、ownerKind / ownerId 编辑、redirect 创建 UI(创建只在 P3 enable-redirect 脚本与 P6 external item action 路径)、定时器内置(只暴露 HTTP/CLI,调度交外部)、audit_log 行级回滚、按 redirect 翻 click_events 明细、redirect 软删除(redirect 删了引用方就断链,`onDelete: SetNull` 之外不引入)、CSV 导出
- 提交风格:Conventional Commits;每 task 末尾 commit

---

## Task 1 — Setup:lib/db.ts 扩展 + AdminHeader 加导航

**Files:**
- Modify: `apps/admin/lib/db.ts`(末尾追加 redirect / audit-log 查询)
- Modify: `apps/admin/components/AdminHeader.tsx`(加 `/redirects` 与 `/audit-log` 入口)

### 5 Steps

**Step 1: 扩展 `apps/admin/lib/db.ts`** —— 末尾追加:

```ts
import type { RedirectOwnerKind } from "@ghome/db";

/* ============== Redirects(admin)============== */

export interface RedirectListFilter {
  ownerKind?: RedirectOwnerKind | "all";
  disabled?: "all" | "yes" | "no";
  q?: string; // 模糊匹配 targetUrl / ownerId
}

export interface RedirectListRow {
  id: string;
  ownerKind: string;
  ownerId: string | null;
  targetUrl: string;
  disabled: boolean;
  createdAt: Date;
  clicks: number; // LEFT JOIN click_events
}

export async function listRedirects(filter?: RedirectListFilter): Promise<RedirectListRow[]> {
  const ownerKindCond =
    filter?.ownerKind && filter.ownerKind !== "all"
      ? Prisma.sql`AND r.owner_kind = ${filter.ownerKind}::text::"RedirectOwnerKind"`
      : Prisma.empty;
  const disabledCond =
    filter?.disabled === "yes"
      ? Prisma.sql`AND r.disabled = true`
      : filter?.disabled === "no"
        ? Prisma.sql`AND r.disabled = false`
        : Prisma.empty;
  const qCond = filter?.q
    ? Prisma.sql`AND (r.target_url ILIKE ${`%${filter.q}%`} OR r.owner_id ILIKE ${`%${filter.q}%`})`
    : Prisma.empty;

  const rows = await prisma.$queryRaw<
    Array<{
      id: string;
      owner_kind: string;
      owner_id: string | null;
      target_url: string;
      disabled: boolean;
      created_at: Date;
      clicks: bigint;
    }>
  >`
    SELECT r.id, r.owner_kind, r.owner_id, r.target_url, r.disabled, r.created_at,
           count(c.id) AS clicks
    FROM redirects r
    LEFT JOIN click_events c ON c.redirect_id = r.id
    WHERE 1=1 ${ownerKindCond} ${disabledCond} ${qCond}
    GROUP BY r.id
    ORDER BY r.created_at DESC
    LIMIT 200
  `;
  return rows.map((r) => ({
    id: r.id,
    ownerKind: r.owner_kind,
    ownerId: r.owner_id,
    targetUrl: r.target_url,
    disabled: r.disabled,
    createdAt: r.created_at,
    clicks: Number(r.clicks),
  }));
}

export async function getRedirectById(id: string) {
  return prisma.redirect.findUnique({
    where: { id },
    include: {
      app: { select: { id: true, slug: true, name: true } },
      video: { select: { id: true, slug: true, title: true } },
      collectionItems: {
        select: {
          id: true,
          collectionId: true,
          collection: { select: { id: true, slug: true, kind: true, title: true } },
        },
      },
    },
  });
}

/** 7 日内每天点击数(用于 redirect 详情页趋势小图) */
export async function getRedirectClicksByDayLast7Days(
  redirectId: string,
): Promise<Array<{ day: string; count: number }>> {
  const since = new Date();
  since.setUTCDate(since.getUTCDate() - 6);
  since.setUTCHours(0, 0, 0, 0);
  const rows = await prisma.$queryRaw<Array<{ day: Date; count: bigint }>>`
    SELECT date_trunc('day', ts AT TIME ZONE 'UTC')::date AS day, count(*) AS count
    FROM click_events
    WHERE redirect_id = ${redirectId}::uuid AND ts >= ${since}
    GROUP BY 1
    ORDER BY 1 ASC
  `;
  return rows.map((r) => ({ day: r.day.toISOString().slice(0, 10), count: Number(r.count) }));
}

/* ============== Audit Log(admin)============== */

export interface AuditLogListFilter {
  targetType?: string; // app | video | guide | tag | collection | redirect | "all"
  actionPrefix?: string; // 前缀匹配,如 "app." / "redirect."
  adminLogin?: string; // 按 admin github_login 过滤
  since?: Date;
  until?: Date;
  page?: number; // 1-indexed
}

const AUDIT_PAGE_SIZE = 50;

export async function listAuditLog(filter?: AuditLogListFilter) {
  const page = Math.max(1, filter?.page ?? 1);
  const where: Prisma.AuditLogEntryWhereInput = {
    ...(filter?.targetType && filter.targetType !== "all"
      ? { targetType: filter.targetType }
      : {}),
    ...(filter?.actionPrefix ? { action: { startsWith: filter.actionPrefix } } : {}),
    ...(filter?.adminLogin
      ? { adminUser: { githubLogin: { contains: filter.adminLogin, mode: "insensitive" } } }
      : {}),
    ...(filter?.since || filter?.until
      ? {
          ts: {
            ...(filter.since ? { gte: filter.since } : {}),
            ...(filter.until ? { lt: filter.until } : {}),
          },
        }
      : {}),
  };
  const [total, rows] = await Promise.all([
    prisma.auditLogEntry.count({ where }),
    prisma.auditLogEntry.findMany({
      where,
      orderBy: { ts: "desc" },
      take: AUDIT_PAGE_SIZE,
      skip: (page - 1) * AUDIT_PAGE_SIZE,
      include: {
        adminUser: { select: { githubLogin: true, name: true } },
      },
    }),
  ]);
  return { rows, total, page, pageSize: AUDIT_PAGE_SIZE };
}

export async function getAuditLogEntry(id: string) {
  return prisma.auditLogEntry.findUnique({
    where: { id },
    include: { adminUser: { select: { githubLogin: true, name: true, githubEmail: true } } },
  });
}
```

> **import 顺序提示**:文件顶部已有 `import { prisma } from "@ghome/db"` 与 `import type { CollectionKind } from "@ghome/db"`。新增的 `import type { RedirectOwnerKind }` 与 `import { Prisma } from "@ghome/db"`(注意 `Prisma` 是 namespace,需要 named import,**不是** default;若 `@ghome/db` 没 re-export,从 `@prisma/client` 取:`import { Prisma } from "@prisma/client"`)。先 `grep -n "from \"@ghome/db\"" packages/db/src/index.ts` 确认是否 re-export `Prisma` namespace,无则加一行 `export { Prisma } from "@prisma/client";`。

**Step 2: 改 `apps/admin/components/AdminHeader.tsx`** — 加导航 link。改后:

```tsx
"use client";

import { signOut } from "next-auth/react";
import Link from "next/link";

interface AdminHeaderProps {
  user: { name?: string | null; image?: string | null; githubLogin: string };
}

const NAV = [
  { href: "/", label: "仪表盘" },
  { href: "/apps", label: "App" },
  { href: "/videos", label: "视频" },
  { href: "/guides", label: "指南" },
  { href: "/topics", label: "专题" },
  { href: "/albums", label: "专辑" },
  { href: "/rankings", label: "榜单" },
  { href: "/redirects", label: "Redirects" },
  { href: "/audit-log", label: "操作日志" },
];

export function AdminHeader({ user }: AdminHeaderProps) {
  return (
    <header className="admin-header">
      <div className="brand">Ghome · Admin</div>
      <nav className="admin-nav">
        {NAV.map((n) => (
          <Link key={n.href} href={n.href}>
            {n.label}
          </Link>
        ))}
      </nav>
      <div className="spacer" />
      <div className="user">
        {user.image && <img src={user.image} alt="" />}
        <span>@{user.githubLogin}</span>
      </div>
      <button className="signout" onClick={() => signOut({ callbackUrl: "/signin" })}>
        退出
      </button>
    </header>
  );
}
```

> **CSS 提示**:`apps/admin/app/globals.css` 此前已有 `.admin-header` 规则(P4 写过)。`.admin-nav` 可能没有 — 若 build 后样式难看,在 globals.css 加一段 `.admin-nav { display: flex; gap: 12px } .admin-nav a { color: var(--text-2) } .admin-nav a:hover { color: var(--text) }`(精简,与已有风格一致)。

**Step 3: typecheck**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/admin typecheck
```

Expected: pass。如果 `Prisma` namespace 未 re-export,会报 "no exported member 'Prisma'" — 按 Step 1 注释加 re-export。

**Step 4: build**

```bash
pnpm --filter @ghome/admin build
```

Expected: pass。

**Step 5: 提交**

```bash
git add apps/admin/lib/db.ts apps/admin/components/AdminHeader.tsx \
        packages/db/src/index.ts apps/admin/app/globals.css
git commit -m "feat(admin): add redirect & audit-log queries + nav links"
```

## Tricky Bits (T1)

1. **`Prisma.sql` 与 raw SQL `WHERE 1=1`**:动态 WHERE 拼接的常见 pattern;`Prisma.empty` 是空 `Prisma.sql`。**禁止**用字符串拼接 SQL — Prisma 注入安全靠 `${}` 自动参数化
2. **`r.owner_kind = ${...}::text::"RedirectOwnerKind"` 强转**:owner_kind 是 PG enum,直接用字符串比较会报类型错。`::text::"RedirectOwnerKind"` 先转 text 再强转 enum;**或**改成 Prisma `findMany`(更安全但要拼 `_count`,代码膨胀;raw 更紧凑)
3. **`createdAt: Date`**:Prisma `@db.Timestamptz(6)` 出参就是 `Date`,前端展示要 `toISOString().slice(0, 16).replace("T", " ")`
4. **`Prisma` namespace re-export**:如果 `packages/db/src/index.ts` 已 `export { Prisma }`,跳过此步;否则加 `export { Prisma } from "@prisma/client";`(放近 PrismaClient 那行旁边)
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 2 — Redirects 列表 + 编辑页

**Files:**
- Create: `apps/admin/app/(admin)/redirects/page.tsx`
- Create: `apps/admin/app/(admin)/redirects/[id]/edit/page.tsx`

### 5 Steps

**Step 1: 写 `apps/admin/app/(admin)/redirects/page.tsx`** —— 列表 + 三轴过滤(ownerKind / disabled / q)。完整代码:

```tsx
import { listRedirects } from "@/lib/db";
import { ListTable, type ListColumn } from "@/components/ListTable";
import Link from "next/link";

export const dynamic = "force-dynamic";

const OWNER_KINDS = ["all", "app", "video", "external", "collection_item"] as const;

export default async function RedirectsListPage({
  searchParams,
}: {
  searchParams: Promise<{ ownerKind?: string; disabled?: string; q?: string }>;
}) {
  const sp = await searchParams;
  const rows = await listRedirects({
    ownerKind: (sp.ownerKind as typeof OWNER_KINDS[number]) ?? "all",
    disabled: (sp.disabled as "all" | "yes" | "no") ?? "all",
    q: sp.q,
  });

  const columns: ListColumn<(typeof rows)[number]>[] = [
    {
      key: "ownerKind",
      header: "类型",
      render: (r) => r.ownerKind,
      width: 100,
    },
    {
      key: "ownerId",
      header: "归属 ID / Slug",
      render: (r) => (
        <code style={{ fontSize: 12, color: "var(--text-3)" }}>{r.ownerId ?? "—"}</code>
      ),
    },
    {
      key: "targetUrl",
      header: "目标 URL",
      render: (r) => (
        <span style={{ display: "inline-block", maxWidth: 360, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {r.targetUrl}
        </span>
      ),
    },
    {
      key: "disabled",
      header: "状态",
      render: (r) => (
        <span style={{ color: r.disabled ? "var(--text-3)" : "var(--success)" }}>
          {r.disabled ? "未启用" : "已启用"}
        </span>
      ),
      width: 80,
    },
    {
      key: "clicks",
      header: "点击",
      render: (r) => r.clicks.toLocaleString(),
      align: "right",
      width: 80,
    },
    {
      key: "createdAt",
      header: "创建",
      render: (r) => new Date(r.createdAt).toISOString().slice(0, 16).replace("T", " "),
      width: 140,
    },
  ];

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1 style={{ fontSize: 22, margin: 0 }}>Redirects</h1>
        <span style={{ fontSize: 13, color: "var(--text-3)" }}>
          外链中转表 · 共 {rows.length} 条(上限 200)
        </span>
      </div>
      <div className="list-toolbar">
        <form method="get" style={{ display: "flex", gap: 12 }}>
          <select name="ownerKind" defaultValue={sp.ownerKind ?? "all"}>
            {OWNER_KINDS.map((k) => (
              <option key={k} value={k}>
                {k === "all" ? "全部归属" : k}
              </option>
            ))}
          </select>
          <select name="disabled" defaultValue={sp.disabled ?? "all"}>
            <option value="all">全部状态</option>
            <option value="no">已启用</option>
            <option value="yes">未启用</option>
          </select>
          <input name="q" defaultValue={sp.q ?? ""} placeholder="按 URL / 归属 ID 搜索" />
          <button type="submit" className="btn-secondary">筛选</button>
        </form>
      </div>
      <ListTable rows={rows} columns={columns} rowHref={(r) => `/redirects/${r.id}/edit`} />
    </>
  );
}
```

**Step 2: 写 `apps/admin/app/(admin)/redirects/[id]/edit/page.tsx`**

```tsx
import { auth } from "@/lib/auth";
import { prisma, validateForWrite } from "@ghome/db";
import { notFound, redirect } from "next/navigation";
import { logAuditAction } from "@/lib/audit";
import { revalidateWeb } from "@/lib/revalidate";
import { getRedirectById, getRedirectClicksByDayLast7Days } from "@/lib/db";
import { EditForm, FormRow } from "@/components/EditForm";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function EditRedirectPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [r, clicksByDay] = await Promise.all([
    getRedirectById(id),
    getRedirectClicksByDayLast7Days(id),
  ]);
  if (!r) notFound();

  async function save(formData: FormData) {
    "use server";
    const session = await auth();
    if (!session?.user?.adminUserId) redirect("/signin");

    // fresh-fetch 防 stale closure(P5 final-fix pattern)
    const fresh = await prisma.redirect.findUniqueOrThrow({ where: { id } });

    const targetUrl = String(formData.get("targetUrl") ?? "").trim();
    const disabledStr = String(formData.get("disabled") ?? "");
    const disabled = disabledStr === "on" || disabledStr === "true";

    if (!targetUrl) throw new Error("targetUrl 必填");
    const v = await validateForWrite(targetUrl);
    if (!v.ok) throw new Error(`URL 校验失败:${v.reason}`);

    if (fresh.targetUrl === targetUrl && fresh.disabled === disabled) {
      // no-op
      redirect(`/redirects/${id}/edit`);
    }

    await prisma.redirect.update({
      where: { id },
      data: { targetUrl, disabled },
    });

    await logAuditAction(
      session.user.adminUserId,
      "redirect.update",
      "redirect",
      id,
      {
        before: { targetUrl: fresh.targetUrl, disabled: fresh.disabled },
        after: { targetUrl, disabled },
      },
    );
    // redirect 没有详情 cache tag;但若挂在 published 内容上,改后 home 卡片显示的"是否可点"会变,revalidate home + 引用方
    const tags = ["home"];
    if (r.app) tags.push(`app:${r.app.slug}`, "apps-list");
    if (r.video) tags.push(`video:${r.video.slug}`, "videos-list");
    for (const ci of r.collectionItems) {
      const k = ci.collection.kind;
      if (k === "topic") tags.push(`topic:${ci.collection.slug}`, "topics-list");
      else if (k === "album") tags.push(`album:${ci.collection.slug}`, "albums-list");
      else if (k === "ranking") tags.push(`ranking:${ci.collection.slug}`, "rankings");
    }
    await revalidateWeb([...new Set(tags)]);

    redirect(`/redirects/${id}/edit`);
  }

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <Link href="/redirects" className="btn-secondary">← 列表</Link>
        <h1 style={{ fontSize: 22, margin: 0 }}>编辑 Redirect</h1>
        <code style={{ fontSize: 12, color: "var(--text-3)" }}>{id}</code>
      </div>

      <section className="dash-section" style={{ marginBottom: 16 }}>
        <h2>归属信息</h2>
        <table className="dash-table">
          <tbody>
            <tr><td>类型</td><td>{r.ownerKind}</td></tr>
            <tr><td>Owner ID</td><td><code>{r.ownerId ?? "—"}</code></td></tr>
            {r.app && (
              <tr><td>App</td><td><Link href={`/apps/${r.app.id}/edit`}>{r.app.name}</Link></td></tr>
            )}
            {r.video && (
              <tr><td>视频</td><td><Link href={`/videos/${r.video.id}/edit`}>{r.video.title}</Link></td></tr>
            )}
            {r.collectionItems.length > 0 && (
              <tr>
                <td>引用</td>
                <td>
                  {r.collectionItems.map((ci) => (
                    <div key={ci.id}>
                      <Link
                        href={`/${ci.collection.kind === "topic" ? "topics" : ci.collection.kind === "album" ? "albums" : "rankings"}/${ci.collection.id}/edit`}
                      >
                        {ci.collection.title}
                      </Link>
                    </div>
                  ))}
                </td>
              </tr>
            )}
            <tr><td>创建时间</td><td>{new Date(r.createdAt).toISOString().slice(0, 19).replace("T", " ")}</td></tr>
          </tbody>
        </table>
      </section>

      <EditForm action={save} submitLabel="保存">
        <FormRow label="目标 URL" hint="必须 http/https,会经 url-policy 异步 DNS 校验(2s timeout)">
          <input name="targetUrl" className="form-input" defaultValue={r.targetUrl} required />
        </FormRow>
        <FormRow label="禁用" hint="勾上后 /r/:id 会跳到 /404,不打点">
          <label style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
            <input type="checkbox" name="disabled" defaultChecked={r.disabled} />
            <span>disabled</span>
          </label>
        </FormRow>
      </EditForm>

      <section className="dash-section" style={{ marginTop: 24 }}>
        <h2>最近 7 天点击</h2>
        <table className="dash-table">
          <thead>
            <tr><th>日期(UTC)</th><th style={{ textAlign: "right" }}>点击</th></tr>
          </thead>
          <tbody>
            {clicksByDay.length === 0 ? (
              <tr><td colSpan={2} style={{ color: "var(--text-3)", textAlign: "center" }}>暂无</td></tr>
            ) : (
              clicksByDay.map((row) => (
                <tr key={row.day}><td>{row.day}</td><td style={{ textAlign: "right" }}>{row.count.toLocaleString()}</td></tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </>
  );
}
```

**Step 3: typecheck + build**

```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
```

**Step 4: 手动冒烟 (本地)**

```bash
docker compose up -d  # 确认 Postgres 起来
pnpm --filter @ghome/admin dev
```

打开 `http://localhost:3100/redirects` → 列表显示 ≥29 行。点 row 进 edit → 改 targetUrl 到 `https://example.com`,提交 → 校验通过、保存成功;再开 `/audit-log`(T3 后)能看见 `redirect.update` 行。

**Step 5: 提交**

```bash
git add "apps/admin/app/(admin)/redirects/page.tsx" "apps/admin/app/(admin)/redirects/[id]/edit/page.tsx"
git commit -m "feat(admin): redirects list with filters + edit page (validateForWrite + audit + revalidate)"
```

## Tricky Bits (T2)

1. **`validateForWrite` 是异步**:server action 必须 `await`,timeout 2s。**别**忘了 throw,否则下面 `prisma.redirect.update` 会用未校验 URL
2. **No-op 短路**:`fresh.targetUrl === targetUrl && fresh.disabled === disabled` 时不写 audit_log + 不 revalidate(避免 audit log 噪声)— 与 P5 edit pattern 一致
3. **fresh-fetch 防 stale closure**:`findUniqueOrThrow` 在 server action 起始拉最新行(运营在两个 tab 各开一份,都点保存的多 tab 安全)
4. **Revalidate 范围**:redirect 改后 `home + 所有引用方的 cache tag`。**注意去重** `[...new Set(tags)]`,否则一个 home 多次 revalidate 浪费 RPC
5. **`disabled` 复选框 form 解析**:HTML 复选框未勾选时不发送 name,所以 `formData.get("disabled")` 是 `null`/`""`/或 `"on"`(勾上)。代码用 `=== "on" || === "true"` 双兜底
6. **不允许编辑 `ownerKind` / `ownerId`**:这两个字段由内容侧 CRUD(P5/P6)维护,redirect 编辑只看不改(详情页只展示),否则破坏 schema 的反查不变量
7. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 3 — Audit Log 列表 + 详情

**Files:**
- Create: `apps/admin/app/(admin)/audit-log/page.tsx`
- Create: `apps/admin/app/(admin)/audit-log/[id]/page.tsx`
- Create: `apps/admin/components/DiffViewer.tsx`(server component,无 client state)

### 5 Steps

**Step 1: 写 `DiffViewer.tsx`**

```tsx
interface DiffViewerProps {
  diff: unknown; // Prisma Json 类型
}

export function DiffViewer({ diff }: DiffViewerProps) {
  if (!diff || typeof diff !== "object") {
    return <pre className="diff-pre">{JSON.stringify(diff, null, 2)}</pre>;
  }
  const d = diff as { before?: unknown; after?: unknown };
  if (!("before" in d) && !("after" in d)) {
    return <pre className="diff-pre">{JSON.stringify(diff, null, 2)}</pre>;
  }
  return (
    <div className="diff-grid">
      <div>
        <h3 style={{ fontSize: 14, color: "var(--text-3)", margin: "0 0 8px" }}>Before</h3>
        <pre className="diff-pre diff-before">
          {d.before ? JSON.stringify(d.before, null, 2) : "—"}
        </pre>
      </div>
      <div>
        <h3 style={{ fontSize: 14, color: "var(--text-3)", margin: "0 0 8px" }}>After</h3>
        <pre className="diff-pre diff-after">
          {d.after ? JSON.stringify(d.after, null, 2) : "—"}
        </pre>
      </div>
    </div>
  );
}
```

CSS(加到 `apps/admin/app/globals.css`):

```css
.diff-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.diff-pre {
  background: var(--bg-2);
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 480px;
  white-space: pre;
}
.diff-before { border-left: 3px solid var(--text-3); }
.diff-after  { border-left: 3px solid var(--success); }
```

**Step 2: 写 `audit-log/page.tsx`** —— 列表 + 过滤 + 分页

```tsx
import { listAuditLog } from "@/lib/db";
import { ListTable, type ListColumn } from "@/components/ListTable";
import Link from "next/link";

export const dynamic = "force-dynamic";

const TARGET_TYPES = ["all", "app", "video", "guide", "tag", "collection", "redirect"] as const;

export default async function AuditLogListPage({
  searchParams,
}: {
  searchParams: Promise<{ targetType?: string; actionPrefix?: string; adminLogin?: string; since?: string; until?: string; page?: string }>;
}) {
  const sp = await searchParams;
  const page = sp.page ? Math.max(1, parseInt(sp.page, 10) || 1) : 1;
  const since = sp.since ? new Date(sp.since) : undefined;
  const until = sp.until ? new Date(sp.until) : undefined;
  const { rows, total, pageSize } = await listAuditLog({
    targetType: sp.targetType ?? "all",
    actionPrefix: sp.actionPrefix?.trim() || undefined,
    adminLogin: sp.adminLogin?.trim() || undefined,
    since: Number.isNaN(since?.getTime()) ? undefined : since,
    until: Number.isNaN(until?.getTime()) ? undefined : until,
    page,
  });

  type Row = (typeof rows)[number];
  const columns: ListColumn<Row>[] = [
    {
      key: "ts",
      header: "时间",
      render: (e) => new Date(e.ts).toISOString().slice(0, 19).replace("T", " "),
      width: 160,
    },
    {
      key: "user",
      header: "操作者",
      render: (e) => `@${e.adminUser.githubLogin}`,
      width: 140,
    },
    {
      key: "action",
      header: "动作",
      render: (e) => <code style={{ fontSize: 12 }}>{e.action}</code>,
      width: 160,
    },
    { key: "targetType", header: "对象类型", render: (e) => e.targetType, width: 100 },
    {
      key: "targetId",
      header: "对象 ID",
      render: (e) => <code style={{ fontSize: 12, color: "var(--text-3)" }}>{e.targetId.slice(0, 8)}…</code>,
    },
  ];

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  function pageHref(p: number) {
    const next = new URLSearchParams();
    if (sp.targetType && sp.targetType !== "all") next.set("targetType", sp.targetType);
    if (sp.actionPrefix) next.set("actionPrefix", sp.actionPrefix);
    if (sp.adminLogin) next.set("adminLogin", sp.adminLogin);
    if (sp.since) next.set("since", sp.since);
    if (sp.until) next.set("until", sp.until);
    next.set("page", String(p));
    return `/audit-log?${next.toString()}`;
  }

  return (
    <>
      <h1 style={{ fontSize: 22, margin: "0 0 16px" }}>操作日志(audit log)</h1>
      <div className="list-toolbar">
        <form method="get" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <select name="targetType" defaultValue={sp.targetType ?? "all"}>
            {TARGET_TYPES.map((t) => (
              <option key={t} value={t}>{t === "all" ? "全部对象类型" : t}</option>
            ))}
          </select>
          <input name="actionPrefix" defaultValue={sp.actionPrefix ?? ""} placeholder="action 前缀,如 app." />
          <input name="adminLogin" defaultValue={sp.adminLogin ?? ""} placeholder="GitHub login 子串" />
          <input name="since" type="datetime-local" defaultValue={sp.since ?? ""} />
          <input name="until" type="datetime-local" defaultValue={sp.until ?? ""} />
          <button type="submit" className="btn-secondary">筛选</button>
        </form>
      </div>
      <div style={{ marginBottom: 8, fontSize: 13, color: "var(--text-3)" }}>
        共 {total} 条 · 第 {page} / {totalPages} 页
      </div>
      <ListTable rows={rows} columns={columns} rowHref={(e) => `/audit-log/${e.id}`} />
      <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 16 }}>
        {page > 1 && <Link href={pageHref(page - 1)} className="btn-secondary">← 上一页</Link>}
        {page < totalPages && <Link href={pageHref(page + 1)} className="btn-secondary">下一页 →</Link>}
      </div>
    </>
  );
}
```

**Step 3: 写 `audit-log/[id]/page.tsx`**

```tsx
import { getAuditLogEntry } from "@/lib/db";
import { DiffViewer } from "@/components/DiffViewer";
import { notFound } from "next/navigation";
import Link from "next/link";

export const dynamic = "force-dynamic";

const TARGET_HREF: Record<string, (id: string) => string> = {
  app: (id) => `/apps/${id}/edit`,
  video: (id) => `/videos/${id}/edit`,
  guide: (id) => `/guides/${id}/edit`,
  redirect: (id) => `/redirects/${id}/edit`,
  // collection 路由要看 kind,不直接深链;tag 没有详情页(内联在 TagPicker 创建)
};

export default async function AuditLogDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const e = await getAuditLogEntry(id);
  if (!e) notFound();

  const targetLink = TARGET_HREF[e.targetType]?.(e.targetId);

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <Link href="/audit-log" className="btn-secondary">← 列表</Link>
        <h1 style={{ fontSize: 22, margin: 0 }}>操作详情</h1>
      </div>

      <section className="dash-section" style={{ marginBottom: 24 }}>
        <table className="dash-table">
          <tbody>
            <tr><td>时间</td><td>{new Date(e.ts).toISOString().slice(0, 19).replace("T", " ")} UTC</td></tr>
            <tr>
              <td>操作者</td>
              <td>
                @{e.adminUser.githubLogin}
                {e.adminUser.name ? ` · ${e.adminUser.name}` : ""}
                {e.adminUser.githubEmail ? ` · ${e.adminUser.githubEmail}` : ""}
              </td>
            </tr>
            <tr><td>动作</td><td><code>{e.action}</code></td></tr>
            <tr><td>对象类型</td><td>{e.targetType}</td></tr>
            <tr>
              <td>对象 ID</td>
              <td>
                <code>{e.targetId}</code>
                {targetLink && (
                  <>
                    {" "}
                    <Link href={targetLink} style={{ marginLeft: 8 }}>→ 跳到对象</Link>
                  </>
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <h2 style={{ fontSize: 16, margin: "0 0 12px" }}>变更</h2>
      <DiffViewer diff={e.diffJson} />
    </>
  );
}
```

**Step 4: typecheck + build + 冒烟**

```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
```

打开 `http://localhost:3100/audit-log` → 看到 P4-P6 累积的所有 audit 行(应已 ≥ 几十行,如果你跑过 admin)。点一行 → 详情页能看 diff JSON。

**Step 5: 提交**

```bash
git add "apps/admin/app/(admin)/audit-log/page.tsx" "apps/admin/app/(admin)/audit-log/[id]/page.tsx" \
        apps/admin/components/DiffViewer.tsx apps/admin/app/globals.css
git commit -m "feat(admin): audit log list + detail with before/after diff viewer"
```

## Tricky Bits (T3)

1. **`diffJson` 是 `unknown`**:类型签名 `Prisma.JsonValue`,DiffViewer 要 narrow + fallback。**别**直接 `.before` 否则 ts 报错
2. **`datetime-local` 输入**:`<input type="datetime-local">` 提交字符串 `2026-05-09T14:30`,`new Date(...)` 按本地时区解释。**MVP 接受这个误差**(运营按本地时区填,DB 存 UTC,显示 UTC)— 不引入时区库
3. **`Number.isNaN(since?.getTime())` 防无效日期**:用户改地址栏可能塞乱 `since=foo`
4. **`TARGET_HREF` 缺 `collection` 与 `tag`**:detail 页对这两类不显示跳链(collection 要 kind,tag 没详情页)
5. **CSS `.diff-grid` 在小屏可能挤**:加一条 media query `@media (max-width: 720px) { .diff-grid { grid-template-columns: 1fr; } }`
6. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 4 — Click Events 30 天聚合任务(核心函数 + cron route + CLI + 测试)

**Files:**
- Create: `packages/db/src/lib/click-aggregate.ts`
- Modify: `packages/db/src/index.ts`(导出 `aggregateClickEvents`)
- Create: `packages/db/scripts/aggregate-click-events.ts`
- Modify: `packages/db/package.json`(加 scripts.db:aggregate-clicks)
- Create: `apps/admin/app/api/cron/aggregate-clicks/route.ts`
- Create: `packages/db/tests/click-aggregate.test.ts`

### 7 Steps

**Step 1: 写核心函数 `packages/db/src/lib/click-aggregate.ts`**

```ts
import type { PrismaClient } from "@prisma/client";

export interface AggregateResult {
  aggregatedRows: number; // INSERT/UPSERT 影响行数(approximation)
  deletedRows: number;
  durationMs: number;
}

/**
 * 聚合 click_events 中 ts < now() - 30d 的行到 click_daily_stats,然后删除原行。
 *
 * 严格按 spec §3.2 click_daily_stats 节定义:
 * - 单事务
 * - pg_advisory_xact_lock(8131421) 防并发双跑
 * - INSERT ON CONFLICT DO UPDATE count = old + new(累加)
 * - DELETE 同事务,失败一起回滚 → 重跑不会双倍
 */
export async function aggregateClickEvents(prisma: PrismaClient): Promise<AggregateResult> {
  const start = Date.now();
  return prisma.$transaction(async (tx) => {
    await tx.$executeRawUnsafe("SELECT pg_advisory_xact_lock(8131421)");

    const inserted = await tx.$executeRawUnsafe(`
      INSERT INTO click_daily_stats (redirect_id, day, ua_family, country, count)
      SELECT
        redirect_id,
        (ts AT TIME ZONE 'UTC')::date AS day,
        COALESCE(ua_family, 'unknown'),
        COALESCE(country, 'unknown'),
        count(*)
      FROM click_events
      WHERE ts < now() - interval '30 days'
      GROUP BY 1, 2, 3, 4
      ON CONFLICT (redirect_id, day, ua_family, country)
      DO UPDATE SET count = click_daily_stats.count + EXCLUDED.count
    `);

    const deleted = await tx.$executeRawUnsafe(
      `DELETE FROM click_events WHERE ts < now() - interval '30 days'`,
    );

    return {
      aggregatedRows: Number(inserted),
      deletedRows: Number(deleted),
      durationMs: Date.now() - start,
    };
  });
}
```

> **关键:`prisma.$transaction(async tx => ...)`** 内必须用 `tx.$executeRawUnsafe`(而不是 `prisma.$executeRawUnsafe`),否则 advisory lock 与后续 SQL 不在同一连接、同一事务,**lock 失效**。

**Step 2: 改 `packages/db/src/index.ts`** 末尾加:

```ts
export { aggregateClickEvents } from "./lib/click-aggregate";
export type { AggregateResult } from "./lib/click-aggregate";
```

**Step 3: 写 CLI `packages/db/scripts/aggregate-click-events.ts`**

```ts
import { PrismaClient } from "@prisma/client";
import { aggregateClickEvents } from "../src/lib/click-aggregate";

async function main() {
  const prisma = new PrismaClient();
  try {
    const result = await aggregateClickEvents(prisma);
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await prisma.$disconnect();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
```

并改 `packages/db/package.json` 的 `scripts`:

```json
"db:aggregate-clicks": "tsx scripts/aggregate-click-events.ts"
```

**Step 4: 写 cron HTTP route `apps/admin/app/api/cron/aggregate-clicks/route.ts`**

```ts
import { NextResponse, type NextRequest } from "next/server";
import { prisma, aggregateClickEvents } from "@ghome/db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const [敏感内容已脱敏];
if (!CRON_SECRET) {
  throw new Error(
    "[admin/cron] CRON_SECRET is not set. Required for /api/cron/aggregate-clicks. " +
      "Set in apps/admin/.env (dev) or job env (prod). Choose a strong random string >= 32 bytes.",
  );
}

export async function POST(req: NextRequest) {
  const auth = req.headers.get("authorization") ?? "";
  const expected = `Bearer ${CRON_SECRET}`;
  if (auth !== expected) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  try {
    const result = await aggregateClickEvents(prisma);
    return NextResponse.json(result);
  } catch (e) {
    console.error("[admin/cron] aggregate-clicks failed:", e);
    return NextResponse.json({ error: "internal" }, { status: 500 });
  }
}
```

**Step 5: 写集成测试 `packages/db/tests/click-aggregate.test.ts`**

```ts
import { afterAll, beforeAll, beforeEach, describe, expect, it } from "vitest";
import { PrismaClient } from "@prisma/client";
import { aggregateClickEvents } from "../src/lib/click-aggregate";

/**
 * 集成测试:需要本地 Postgres + 已 migrate。
 * pnpm --filter @ghome/db test 时,vitest 用 DATABASE_URL 连本地 DB。
 */
describe("aggregateClickEvents", () => {
  const prisma = new PrismaClient();

  beforeAll(async () => {
    // 用一个真实 redirect 作为 FK 目标(从 P1 seed 中取一条 disabled=true 的)
    const r = await prisma.redirect.findFirst();
    if (!r) throw new Error("no redirect found in DB; run prisma db seed first");
  });

  beforeEach(async () => {
    // 清理本测试可能造成的副作用 — 仅清测试自身写入的旧行
    await prisma.clickEvent.deleteMany({});
    await prisma.clickDailyStat.deleteMany({});
  });

  afterAll(async () => {
    await prisma.clickEvent.deleteMany({});
    await prisma.clickDailyStat.deleteMany({});
    await prisma.$disconnect();
  });

  it("聚合 > 30d 行 + 删除原行 + 重复跑幂等", async () => {
    const r = await prisma.redirect.findFirstOrThrow();

    // 塞 5 行 35 天前的 click_events(同一天、同 ua_family、同 country)
    const oldTs = new Date();
    oldTs.setUTCDate(oldTs.getUTCDate() - 35);
    oldTs.setUTCHours(12, 0, 0, 0);

    for (let i = 0; i < 5; i++) {
      await prisma.clickEvent.create({
        data: {
          redirectId: r.id,
          ts: oldTs,
          uaFamily: "Chrome",
          uaOs: "macOS",
          country: "JP",
          referrerOrigin: "unknown",
          ipHash: "test-hash-" + i,
        },
      });
    }

    // 再塞 2 行最近的(应保留)
    for (let i = 0; i < 2; i++) {
      await prisma.clickEvent.create({
        data: {
          redirectId: r.id,
          ts: new Date(),
          uaFamily: "Chrome",
          uaOs: "macOS",
          country: "JP",
          referrerOrigin: "unknown",
          ipHash: "fresh-" + i,
        },
      });
    }

    // 第一次聚合
    const r1 = await aggregateClickEvents(prisma);
    expect(r1.deletedRows).toBe(5);
    expect(r1.aggregatedRows).toBeGreaterThanOrEqual(1); // 1 个 (redirect, day, ua, country) bucket

    // 检查 click_daily_stats
    const stat = await prisma.clickDailyStat.findUnique({
      where: {
        redirectId_day_uaFamily_country: {
          redirectId: r.id,
          day: oldTs,
          uaFamily: "Chrome",
          country: "JP",
        },
      },
    });
    expect(stat?.count).toBe(BigInt(5));

    // click_events 还剩 2 行最近的
    expect(await prisma.clickEvent.count()).toBe(2);

    // 第二次聚合(无新过期数据)→ 应该 0 删 0 增
    const r2 = await aggregateClickEvents(prisma);
    expect(r2.deletedRows).toBe(0);

    // click_daily_stats count 仍是 5(没双倍累加)
    const stat2 = await prisma.clickDailyStat.findUnique({
      where: {
        redirectId_day_uaFamily_country: {
          redirectId: r.id,
          day: oldTs,
          uaFamily: "Chrome",
          country: "JP",
        },
      },
    });
    expect(stat2?.count).toBe(BigInt(5));
  });
});
```

**Step 6: 跑 typecheck + 测试 + build**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d  # Postgres
pnpm --filter @ghome/db typecheck
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin build
```

Expected:
- 测试:1 passed(可能要数秒,内含 5+2 INSERT + 聚合)
- admin build:CRON_SECRET 必须在 build 期定义,否则 module-load 时 throw。**先把 `[敏感内容已脱敏] 加到 `apps/admin/.env`**,再 build

CLI 冒烟:

```bash
pnpm --filter @ghome/db db:aggregate-clicks
# 输出 { aggregatedRows: 0, deletedRows: 0, durationMs: ~10 }(测试已清理过)
```

HTTP 冒烟(开 dev server 后):

```bash
curl -X POST http://localhost:3100/api/cron/aggregate-clicks \
     -H "Authorization: Bearer local-dev-secret-change-me-32+chars"
# {"aggregatedRows":0,"deletedRows":0,"durationMs":...}
curl -X POST http://localhost:3100/api/cron/aggregate-clicks
# {"error":"unauthorized"}  (401)
```

**Step 7: 提交**

```bash
git add packages/db/src/lib/click-aggregate.ts packages/db/src/index.ts \
        packages/db/scripts/aggregate-click-events.ts packages/db/package.json \
        packages/db/tests/click-aggregate.test.ts \
        apps/admin/app/api/cron/aggregate-clicks/route.ts \
        apps/admin/.env.example
git commit -m "feat(db,admin): click_events 30d aggregation (fn + cron route + CLI + tests)"
```

(`.env.example` 加一行 `[敏感内容已脱敏] 占位 + 注释要求 ≥32 字符)

## Tricky Bits (T4)

1. **`prisma.$transaction(async tx => ...)` 与 `tx.$executeRawUnsafe`**:advisory_xact_lock 必须与后续 SQL 同一事务、同一连接,所以**用 `tx`**,不要在事务内误用 `prisma`。`pg_advisory_xact_lock` 在事务结束时自动释放
2. **`$executeRawUnsafe` vs `$executeRaw`**:这里 SQL 没有用户输入,用 Unsafe 简化(零参数),仍安全。如果未来加可调参数(e.g. 自定义 retention 天数),改成 `$executeRaw\`...\${paramVar}...\`` + `Prisma.sql`
3. **测试隔离**:`beforeEach` 清 `clickEvent` + `clickDailyStat`。**不要清 redirects**(P1 seed 行其他测试也用)
4. **测试要本地 DB**:`pnpm --filter @ghome/db test` 在 CI 已经有 Postgres service(P1 升级过),本地需要 docker compose 起来。如果 CI 出问题,看 `.github/workflows/ci.yml` 的 `DATABASE_URL` 是否传给了 vitest
5. **CRON_SECRET 长度**:32+ 字符,不能用 `dev` 之类弱值。`.env.example` 里塞一段 `# generate with: openssl rand -hex 32`
6. **CRON_SECRET 模块顶层 throw**:与 P3 `IP_HASH_SECRET` 一致 — 启动期失败比运行时静默用空字符串安全得多
7. **失败重跑幂等**:advisory lock 在事务结束自动释放;事务回滚 → INSERT 与 DELETE 都没生效 → 下次跑等价于第一次。**前提是聚合 SQL 与 DELETE 同一事务**,这是核心不变量,不要拆
8. **POST 不 GET**:cron route 只接 POST。GET 不实现(避免被搜索引擎或浏览器误触)
9. **不写 audit_log**:cron 没有 admin_user_id,audit_log schema 强制 NOT NULL。MVP 仅 console.log,不写专用 system_event_log 表(P8 收尾或更后再考虑)
10. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 5 — End-to-end 冒烟 + tag p7-redirects-audit-aggregate

**Files:** 无新文件;此 task 仅冒烟 + 打 tag。

### 5 Steps

**Step 1: 跑全套 CI 等价命令本地一次**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
pnpm install
pnpm --filter @ghome/db db:migrate:deploy   # 无新迁移,no-op
pnpm --filter @ghome/db db:seed              # 不动旧数据(seed 是 idempotent 的 upsert)
pnpm --filter @ghome/db typecheck
pnpm --filter @ghome/db test                 # url-policy + db-constraints + click-aggregate
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin lint
pnpm --filter @ghome/admin build
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web lint
pnpm --filter @ghome/web build
```

全部 pass 才算过关。**注意 admin build 需要 `apps/admin/.env` 含 `CRON_SECRET`**,否则模块顶层 throw。

**Step 2: 端到端 UI 冒烟脚本**

依次执行(打开 admin 与 web):

1. 启 admin dev:`pnpm --filter @ghome/admin dev`(3100)
2. 启 web dev:`pnpm --filter @ghome/web dev`(3000)
3. 登入 admin,**改一条 disabled=true 的 redirect** 的 targetUrl 到 `https://example.com`(确认 url-policy 校验通过)+ 取消 disabled
4. 在 admin `/audit-log` 列表筛 `targetType=redirect actionPrefix=redirect.update` → 看到刚才那行
5. 点详情 → 看到 before/after JSON
6. 找出该 redirect 的 owner(若是 app),打开 web `/app/{slug}`,点击 CTA → 浏览器跳到 example.com
7. 在 admin 跑 cron CLI:`pnpm --filter @ghome/db db:aggregate-clicks` → console 输出 `aggregatedRows>=0`
8. 重复一次 → `deletedRows=0`(幂等)

**Step 3: 把 5 步冒烟结果记到本 task 的 commit message 里(可选)**

或者写一行 summary。

**Step 4: 给 P7 打 tag**

```bash
git tag p7-redirects-audit-aggregate
```

**Step 5: 最终提交(若有改动)+ 推 tag(用户决定)**

```bash
git status     # 应 clean
# git push origin p7-redirects-audit-aggregate   # 用户授权后再推
```

## Tricky Bits (T5)

1. **冒烟需要本地 Postgres + 真有 click_events 数据**:若你从未点过任何 `/r/:id`,`click_events` 表是空的 — 聚合不会出错,但端到端验证看不到数字变化。可以在 step 2 第 3 步里手动 `curl http://localhost:3000/r/{redirectId}` 几次造数据
2. **`p7-redirects-audit-aggregate` tag**:与 P0-P6 风格一致(P{n}-{summary})
3. **若 git tag 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Final 验收清单(P7 整体)

- [ ] `apps/admin/(admin)/redirects/page.tsx` 存在,本地能列出 ≥29 行(P1 seed) + 任何 P6 创建的 external item redirect
- [ ] `/redirects/[id]/edit` 改 targetUrl 走 `validateForWrite`,失败时表单显示错误 toast
- [ ] 改一条 redirect → web 端 `/r/:id` 跳到新地址(浏览器实测)
- [ ] `/audit-log` 列表分页(50/页) + 5 维过滤(targetType / actionPrefix / adminLogin / since / until)
- [ ] `/audit-log/[id]` 详情显示 before/after diff
- [ ] `aggregateClickEvents` 函数:单事务 + advisory lock + INSERT ON CONFLICT + DELETE 同事务
- [ ] CLI `pnpm db:aggregate-clicks` 跑成功
- [ ] HTTP `POST /api/cron/aggregate-clicks` 401 / 200 双路径正确
- [ ] 集成测试:塞 5 行 35d 前数据 → 聚合 → `click_daily_stats.count = 5` + `click_events 剩 2 行新的`;再跑一次 → 聚合无变化(幂等)
- [ ] AdminHeader 加 `/redirects` `/audit-log` 入口
- [ ] CRON_SECRET 在 module-load 期断言存在(类似 IP_HASH_SECRET)
- [ ] CI 通过(包括新测试)

## 不做(P7 范围外,留给 P8 或后续)

- redirect 批量勾选 + 批量 toggle disabled / delete
- redirect 创建 UI(创建只在 P3 enable-redirect 脚本与 P6 external item action)
- redirect 删除(`onDelete: SetNull` 已挂,但 admin 不暴露删除按钮 — 引用方先解绑)
- redirect 软删除
- audit_log 行级回滚 / 一键 revert
- audit_log CSV 导出 / 全文搜索
- 按 redirect 翻 click_events 明细(只暴露聚合的"7 日趋势")
- 内置 cron 调度器(只暴露 HTTP/CLI,真到生产用 Vercel cron / GitHub Actions / k8s CronJob)
- 聚合维度自定义(retention 天数固定 30d)
- 多租户 / 多管理员的权限分隔(P7 仍是"白名单管理员都能看全量")

---

**下一步:** P7 完成后,**写 P8 plan**(ILIKE + pg_trgm 搜索接口、首页搜索框接通、404 / 性能 / SEO异常验证 收尾)。
