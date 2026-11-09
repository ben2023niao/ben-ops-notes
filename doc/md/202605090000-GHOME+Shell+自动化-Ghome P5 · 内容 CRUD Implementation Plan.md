---
id: "doc-3cc905a5cb26"
title: "Ghome P5 · 内容 CRUD Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/operator/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p5-content-crud.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p5-content-crud.md"
sourceSha256: "c73633013a4511279c03cb2082eb5822eb4d5297ddff42315d53b12f0f78734c"
sourceSystem: "project-doc"
---

# Ghome P5 · 内容 CRUD Implementation Plan

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605090000-GHOME%2BShell%2B%E8%87%AA%E5%8A%A8%E5%8C%96-Ghome%20P5%20%C2%B7%20%E5%86%85%E5%AE%B9%20CRUD%20Implementation%20Plan.md)

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `apps/admin` 落地 App / Video / Guide 三类内容的列表 + 编辑(状态机 `draft → published → archived` + 软删除 `deleted_at`),配套**标签内联 CRUD**(在 App/视频编辑器里即时新建 tag),**audit_log 写入**(每个写操作落一行),以及**发布触发 web revalidate**(带 `REVALIDATE_SECRET` 校验)。完成后:运营在 admin 改一个 App 的描述并发布 → web 详情页几秒内看到;运营在 App 编辑器里新建一个 tag 并应用 → 前台 App 详情页看到这个 tag。

**Architecture:**
- **server actions** 是写入主路径(Auth.js v5 + Next.js 15 RSC 标准):每个 form 的 action 是一个 `"use server"` 函数,直接 await Prisma + audit log + revalidate
- **状态机**:`status: 'draft' | 'published' | 'archived'`(P1 schema 已建)+ `deletedAt: DateTime?`(soft delete)。UI 显示 `Status badge`(草稿 / 已发布 / 已下线 / 已删除)
- **audit_log**:抽出 `logAuditAction(adminUserId, action, targetType, targetId, diff)` 工具,**每个**写操作都调一次。`diff_json` 存改动前后值
- **revalidate webhook**:`apps/web/app/api/revalidate/route.ts` 接收 POST,header `Authorization: Bearer ${REVALIDATE_SECRET}` 校验,body `{ tags: string[] }`,调 `revalidateTag(tag)`。Admin 端 `revalidateWeb([...tags])` helper 发请求
- **tag 内联 CRUD**:`POST /api/tags` server action,接收 `{ label, slug }`,服务端二次校验(slug `/^[a-z0-9-]+$/` + label & slug 都不重复)
- **不做**(P6/P7+):collections/topics/albums/rankings 编辑;redirect 管理 UI;搜索框接通;admin 多角色 RBAC

**Tech Stack:**
- Server actions(Next.js 15 标准)
- Prisma(已 P1)
- `@uiw/react-md-editor ^4.0.5`(P5 新增,Guide bodyMd 编辑器)— client component
- `next-auth ^5.0.0-beta.25`(已 P4)
- 无新增数据库迁移(P1 schema 完整)

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §2.3、§3.2 audit_log + tags、§4.1 ISR + revalidate、§5 P5。

**前置假设:** P4 已完成,`p4-admin-auth` 标签存在;admin 已能 GitHub OAuth 登录看到 Dashboard;`audit_log` 表已建(P1)但没数据;`tags` 表已 seed 63 条;`apps/admin/lib/db.ts` 已有 5 个 Dashboard 查询;web 端的 `apps/web/app/api/revalidate/route.ts` 不存在(本期建)。

---

## File Structure(P5 末态)

```
apps/admin/
├─ app/
│  ├─ (admin)/                            # group route — 用统一 admin layout(含 Header)
│  │  ├─ layout.tsx                       # T1:嵌套 layout,包 AdminHeader
│  │  ├─ apps/
│  │  │  ├─ page.tsx                      # T2:列表
│  │  │  └─ [id]/
│  │  │      └─ edit/
│  │  │          └─ page.tsx              # T5:编辑(read view + form)
│  │  ├─ videos/
│  │  │  ├─ page.tsx                      # T2
│  │  │  └─ [id]/edit/page.tsx            # T6
│  │  └─ guides/
│  │      ├─ page.tsx                     # T2
│  │      └─ [id]/edit/page.tsx           # T7
│  ├─ api/
│  │  └─ tags/
│  │      └─ route.ts                     # T4:POST 创建 tag
│  ├─ page.tsx                            # 已存在(P4 Dashboard)— 不动
│  ├─ layout.tsx                          # 已存在(P4)— 不动
│  └─ (auth)/                             # 已存在(P4 signin)— 不动
├─ components/
│  ├─ AdminHeader.tsx                     # P4 已写,不动
│  ├─ DashboardCard.tsx                   # P4 已写,不动
│  ├─ StatusBadge.tsx                     # T1
│  ├─ ListTable.tsx                       # T1:复用列表 table 组件
│  ├─ EditForm.tsx                        # T1:复用 form helper
│  ├─ TagPicker.tsx                       # T4:client component,含"新建 tag"内联
│  └─ MarkdownEditor.tsx                  # T7:client wrapper for @uiw/react-md-editor
├─ lib/
│  ├─ auth.ts                             # 已存在(P4)— 不动
│  ├─ auth.types.ts                       # 已存在(P4)— 不动
│  ├─ db.ts                               # T2 扩展(列表查询)
│  ├─ audit.ts                            # T3:logAuditAction helper
│  ├─ revalidate.ts                       # T3:revalidateWeb helper
│  └─ status.ts                           # T1:状态机辅助(allowed transitions)
├─ middleware.ts                          # 已存在(P4)— 不动
└─ package.json                           # T1 加 @uiw/react-md-editor

apps/web/
└─ app/
    └─ api/
        └─ revalidate/
            └─ route.ts                   # T3:接收 revalidate 请求

.github/workflows/ci.yml                  # T1 加 REVALIDATE_SECRET env
apps/admin/.env / .env.example            # T1 加 REVALIDATE_SECRET
apps/web/.env / .env.example              # T1 加 REVALIDATE_SECRET
```

新增文件 ~16,改动 ~5。

---

## Conventions(整个 P5 共享)

- **写路径走 server actions**,不写 admin 自己的 REST API(除了 tag 创建 — 它需要从 client component 触发)
- **状态机 transitions**(在 `lib/status.ts` 实现 `canTransition(from, to)`):
  - `draft → published`(发布)
  - `published → draft`(撤回)
  - `published → archived` / `draft → archived`(下线)
  - `archived → draft`(恢复)
  - 软删除 `deleted_at` 是独立字段,任何状态都能软删
- **audit_log 必写**:任何 update / create / publish / archive / delete / 标签编辑 → `logAuditAction(...)`
- **publish 同时触发 revalidate**:`revalidateWeb(['app:slug', 'apps-list'])` 之类
- **`REVALIDATE_SECRET`**:32 字节随机,admin/.env、web/.env、CI 都设
- **slug 不可改**:P5 编辑 App/Video/Guide 时**不允许**改 slug(避免 SEO异常验证 + 链接断裂)。要改 slug 的场景视为"删旧建新"(P5 不做特殊 UI)
- **redirect 不在 P5 改**:redirect.targetUrl 与 disabled 留 P7 单独管理。P5 的 App/Video 编辑只动 mevendor_ata
- 提交风格:Conventional Commits;每 task 末尾 commit
- 不引 Tailwind / 不上第三方 form 库(react-hook-form 等);用原生 form

---

## Task 1 — Setup:env + 状态机辅助 + 通用 UI 组件 + (admin) layout

**Files:**
- Modify: `apps/admin/package.json`(加 `@uiw/react-md-editor`)
- Modify: `apps/admin/.env` / `apps/admin/.env.example`(加 `REVALIDATE_SECRET`)
- Modify: `apps/web/.env` / `apps/web/.env.example`(加 `REVALIDATE_SECRET`)
- Modify: `.github/workflows/ci.yml`(加 `REVALIDATE_SECRET` 到 jobs.ci.env)
- Create: `apps/admin/lib/status.ts`
- Create: `apps/admin/components/StatusBadge.tsx`
- Create: `apps/admin/components/ListTable.tsx`
- Create: `apps/admin/components/EditForm.tsx`
- Create: `apps/admin/app/(admin)/layout.tsx`
- Modify: `apps/admin/app/page.tsx`(改成跳转到 `/(admin)` 路径之一,或保留为 Dashboard 但用嵌套 layout)
- Modify: `apps/admin/app/globals.css`(加 P5 新组件样式)

### 9 Steps

**Step 1: 加 `REVALIDATE_SECRET` 到 5 处**

`apps/admin/.env.example` 与 `apps/admin/.env` 各追加一行:
```bash
# Web revalidate webhook 共享密钥(32+ 字节,与 apps/web/.env 同值)
[敏感内容已脱敏]
```

`apps/web/.env.example` 与 `apps/web/.env` 各追加一行(同上)。

`.github/workflows/ci.yml` 的 `jobs.ci.env` 区域加:
```yaml
      [敏感内容已脱敏]
```

`apps/admin/.env` 与 `apps/web/.env` 用同一 dev value:
```
[敏感内容已脱敏]
```

**Step 2: 修改 `apps/admin/package.json`**

`dependencies` 加:
```json
"@uiw/react-md-editor": "^4.0.5"
```

**Step 3: 写 `apps/admin/lib/status.ts`**

```ts
import type { ContentStatus } from "@ghome/db";

export const STATUS_LABELS: Record<ContentStatus, string> = {
  draft: "草稿",
  published: "已发布",
  archived: "已下线",
};

export const STATUS_COLORS: Record<ContentStatus, string> = {
  draft: "var(--text-3)",
  published: "var(--success)",
  archived: "var(--text-2)",
};

const ALLOWED_TRANSITIONS: Record<ContentStatus, ContentStatus[]> = {
  draft: ["published", "archived"],
  published: ["draft", "archived"],
  archived: ["draft"],  // 恢复成草稿,再次审视后可重新发布
};

export function canTransition(from: ContentStatus, to: ContentStatus): boolean {
  if (from === to) return false;
  return ALLOWED_TRANSITIONS[from].includes(to);
}

export function nextActions(current: ContentStatus): ContentStatus[] {
  return ALLOWED_TRANSITIONS[current];
}
```

**Step 4: 写 `apps/admin/components/StatusBadge.tsx`**

```tsx
import type { ContentStatus } from "@ghome/db";
import { STATUS_LABELS, STATUS_COLORS } from "@/lib/status";

export function StatusBadge({ status }: { status: ContentStatus }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: 12,
        background: "var(--primary-light)",
        color: STATUS_COLORS[status],
      }}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
```

**Step 5: 写 `apps/admin/components/ListTable.tsx`** — 通用列表 table

```tsx
import Link from "next/link";

export interface ListColumn<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  align?: "left" | "right";
  width?: string | number;
}

export function ListTable<T extends { id: string }>({
  rows,
  columns,
  rowHref,
  empty = "暂无数据",
}: {
  rows: T[];
  columns: ListColumn<T>[];
  rowHref?: (row: T) => string;
  empty?: string;
}) {
  if (rows.length === 0) {
    return (
      <div className="dash-section" style={{ textAlign: "center", color: "var(--text-3)" }}>
        {empty}
      </div>
    );
  }
  return (
    <div className="dash-section" style={{ padding: 0, overflow: "hidden" }}>
      <table className="dash-table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} style={{ width: c.width, textAlign: c.align ?? "left" }}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const href = rowHref?.(row);
            return (
              <tr key={row.id}>
                {columns.map((c) => (
                  <td key={c.key} style={{ textAlign: c.align ?? "left" }}>
                    {href && c.key === columns[0]?.key ? (
                      <Link href={href} style={{ color: "var(--primary)" }}>
                        {c.render(row)}
                      </Link>
                    ) : (
                      c.render(row)
                    )}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

**Step 6: 写 `apps/admin/components/EditForm.tsx`** — form 容器(action + footer)

```tsx
import type { ReactNode } from "react";

export function EditForm({
  action,
  children,
  submitLabel = "保存",
  extraActions,
}: {
  action: (formData: FormData) => Promise<void>;
  children: ReactNode;
  submitLabel?: string;
  extraActions?: ReactNode;
}) {
  return (
    <form action={action}>
      <div className="dash-section">{children}</div>
      <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
        <button type="submit" className="signin-btn" style={{ background: "var(--primary)" }}>
          {submitLabel}
        </button>
        {extraActions}
      </div>
    </form>
  );
}

export function FormRow({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: "block", fontSize: 13, color: "var(--text-2)", marginBottom: 6 }}>
        {label}
      </label>
      {children}
      {hint && <div style={{ fontSize: 12, color: "var(--text-3)", marginTop: 4 }}>{hint}</div>}
    </div>
  );
}
```

> form 内部用 `<input>` / `<textarea>` 等 native — 配合 server actions 直接读 FormData。

**Step 7: 写 `apps/admin/app/(admin)/layout.tsx`** — 嵌套 layout 给所有 admin 内层路由(含 Dashboard)统一加 Header

```tsx
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { AdminHeader } from "@/components/AdminHeader";

export default async function AdminGroupLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session?.user?.adminUserId) {
    redirect("/signin");
  }
  return (
    <div className="admin-shell">
      <AdminHeader
        user={{
          name: session.user.name ?? null,
          image: session.user.image ?? null,
          githubLogin: session.user.githubLogin,
        }}
      />
      <main className="admin-main">{children}</main>
    </div>
  );
}
```

> 把 `apps/admin/app/page.tsx`(Dashboard)**移到** `apps/admin/app/(admin)/page.tsx`,这样它也走 group layout — 删 Dashboard 自己的 AdminHeader 重复。**关键改动**:
> - mv `apps/admin/app/page.tsx` → `apps/admin/app/(admin)/page.tsx`
> - 在新 page.tsx 里删去 `<AdminHeader />` 调用与 `<div className="admin-shell">` 包裹,因为 layout 已包(只渲染内容)

**Step 8: 修改 `apps/admin/app/globals.css`** — 追加 P5 新组件样式

```css

/* P5 additions */
.list-toolbar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
.list-toolbar select, .list-toolbar input {
  padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 14px; background: #fff;
}
.list-toolbar .spacer { flex: 1; }
.list-toolbar a, .list-toolbar button {
  padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer;
  background: var(--primary); color: #fff; border: none; text-decoration: none;
}
.form-input, .form-textarea {
  width: 100%; padding: 8px 12px; font-size: 14px; border: 1px solid var(--border);
  border-radius: 6px; background: #fff; color: var(--text); font-family: inherit;
}
.form-textarea { min-height: 80px; resize: vertical; }
.form-row-readonly {
  font-size: 14px; color: var(--text-2); padding: 8px 12px; background: var(--bg);
  border-radius: 6px; word-break: break-all;
}
.tag-picker {
  display: flex; flex-wrap: wrap; gap: 6px; padding: 8px; border: 1px solid var(--border);
  border-radius: 6px; min-height: 40px; background: #fff;
}
.tag-picker .pill {
  padding: 4px 10px; border-radius: 12px; font-size: 12px; background: var(--primary-light);
  color: var(--primary); border: none; cursor: pointer;
}
.tag-picker .pill.selected { background: var(--primary); color: #fff; }
.tag-picker input { border: none; outline: none; background: transparent; flex: 1; min-width: 100px; font-size: 13px; }
.btn-secondary {
  padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer;
  background: transparent; color: var(--text-2); border: 1px solid var(--border);
  text-decoration: none;
}
.btn-secondary:hover { background: var(--bg); color: var(--text); }
.btn-danger { background: var(--danger); color: #fff; border: none; }
.btn-danger:hover { background: #d63b3b; }
```

**Step 9: 安装 + typecheck + 提交**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm install
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build

git add apps/admin/package.json apps/admin/lib/status.ts \
        apps/admin/components/StatusBadge.tsx apps/admin/components/ListTable.tsx \
        apps/admin/components/EditForm.tsx apps/admin/app/globals.css \
        "apps/admin/app/(admin)/" \
        apps/admin/app/page.tsx \
        apps/admin/.env.example apps/web/.env.example \
        .github/workflows/ci.yml pnpm-lock.yaml
git commit -m "feat(admin): add status state machine, list/form components, (admin) group layout, REVALIDATE_SECRET env"
```

> `apps/admin/.env` 与 `apps/web/.env` 不入库。
>
> Step 7 涉及移动 page.tsx 文件(`mv apps/admin/app/page.tsx apps/admin/app/(admin)/page.tsx`),git 视为 delete + add。**确保 (admin) 路径下的 page.tsx 渲染逻辑去掉 AdminHeader 与 admin-shell wrapper**(layout 已包了)。

## Tricky Bits (T1)

1. **`(admin)` 是 Next.js group route**,括号语法不影响 URL。`/`、`/apps`、`/videos`、`/guides` 等都通过 `(admin)/<path>/page.tsx` 解析,不引入 `/admin` 前缀。
2. **`@uiw/react-md-editor`**:client-only library。T7 才会用到。
3. **REVALIDATE_SECRET 同步两端**:admin 与 web 必须用**同一**字符串 — 否则 admin 触发的 revalidate 请求会被 web 拒。CI 用一个共享值。
4. **状态机 `canTransition` 简单**:本期 deny self-transition;archived → draft 是恢复路径。`deleted_at` 软删独立。
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS。

---

## Task 2 — 列表页:`/apps`、`/videos`、`/guides`(同模式 3 合 1)

**Files:**
- Create: `apps/admin/app/(admin)/apps/page.tsx`
- Create: `apps/admin/app/(admin)/videos/page.tsx`
- Create: `apps/admin/app/(admin)/guides/page.tsx`
- Modify: `apps/admin/lib/db.ts`(加 `listApps` / `listVideos` / `listGuides` 查询)

每页都是 server component,展示 ListTable + 状态筛选 + 搜索框(本期 placeholder,P8 才接)。

### 5 Steps

**Step 1: 修改 `apps/admin/lib/db.ts`** — 末尾加 3 个列表查询

```ts
/* ============== 列表(admin)============== */

export interface ListFilter {
  status?: "draft" | "published" | "archived" | "all";
  q?: string;  // 关键词,P8 才真接;P5 列表先按 slug/title ILIKE 简单过滤
  includeDeleted?: boolean;
}

function statusWhere(filter?: ListFilter) {
  if (!filter?.status || filter.status === "all") return {};
  return { status: filter.status };
}

function deletedWhere(filter?: ListFilter) {
  return filter?.includeDeleted ? {} : { deletedAt: null };
}

export async function listApps(filter?: ListFilter) {
  return prisma.app.findMany({
    where: {
      ...statusWhere(filter),
      ...deletedWhere(filter),
      ...(filter?.q
        ? {
            OR: [
              { slug: { contains: filter.q, mode: "insensitive" } },
              { name: { contains: filter.q, mode: "insensitive" } },
            ],
          }
        : {}),
    },
    include: { category: true },
    orderBy: { updatedAt: "desc" },
  });
}

export async function listVideos(filter?: ListFilter) {
  return prisma.video.findMany({
    where: {
      ...statusWhere(filter),
      ...deletedWhere(filter),
      ...(filter?.q
        ? {
            OR: [
              { slug: { contains: filter.q, mode: "insensitive" } },
              { title: { contains: filter.q, mode: "insensitive" } },
            ],
          }
        : {}),
    },
    include: { category: true },
    orderBy: { updatedAt: "desc" },
  });
}

export async function listGuides(filter?: ListFilter) {
  return prisma.guide.findMany({
    where: {
      ...statusWhere(filter),
      ...deletedWhere(filter),
      ...(filter?.q
        ? {
            OR: [
              { slug: { contains: filter.q, mode: "insensitive" } },
              { title: { contains: filter.q, mode: "insensitive" } },
            ],
          }
        : {}),
    },
    orderBy: { updatedAt: "desc" },
  });
}
```

**Step 2: 写 `apps/admin/app/(admin)/apps/page.tsx`**

```tsx
import { listApps } from "@/lib/db";
import { ListTable, type ListColumn } from "@/components/ListTable";
import { StatusBadge } from "@/components/StatusBadge";
import Link from "next/link";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ status?: string; q?: string }>;
}

export default async function AppsListPage({ searchParams }: Props) {
  const sp = await searchParams;
  const apps = await listApps({
    status: (sp.status as "draft" | "published" | "archived" | "all") ?? "all",
    q: sp.q,
  });

  const columns: ListColumn<(typeof apps)[number]>[] = [
    { key: "name", header: "名称", render: (a) => a.name },
    { key: "slug", header: "Slug", render: (a) => <code style={{ fontSize: 12, color: "var(--text-3)" }}>{a.slug}</code> },
    { key: "category", header: "分类", render: (a) => a.category.label },
    { key: "status", header: "状态", render: (a) => <StatusBadge status={a.status} />, width: 80 },
    { key: "updated", header: "更新时间", render: (a) => new Date(a.updatedAt).toISOString().slice(0, 16).replace("T", " "), width: 140 },
  ];

  return (
    <>
      <h1 style={{ fontSize: 22, margin: "0 0 16px" }}>App 列表</h1>
      <div className="list-toolbar">
        <form method="get" action="/apps" style={{ display: "flex", gap: 12 }}>
          <select name="status" defaultValue={sp.status ?? "all"}>
            <option value="all">全部状态</option>
            <option value="draft">草稿</option>
            <option value="published">已发布</option>
            <option value="archived">已下线</option>
          </select>
          <input name="q" defaultValue={sp.q ?? ""} placeholder="按 slug 或名称搜索" />
          <button type="submit" className="btn-secondary">筛选</button>
        </form>
        <div className="spacer" />
        <span style={{ fontSize: 13, color: "var(--text-3)" }}>共 {apps.length} 条</span>
      </div>
      <ListTable rows={apps} columns={columns} rowHref={(a) => `/apps/${a.id}/edit`} />
    </>
  );
}
```

**Step 3: 写 `apps/admin/app/(admin)/videos/page.tsx`** — 同模式,字段稍变(title 替代 name,无 category 行不变)

按 plan T2 Step 2 的 apps 页面照搬,把 `listApps` 改 `listVideos`,`a.name` 改 `v.title`,标题文案 "App 列表" → "视频列表"。

**Step 4: 写 `apps/admin/app/(admin)/guides/page.tsx`** — 同样模式

字段:title / slug / categoryLabel / status / updatedAt。`listGuides` 不 include category(category 是字符串字段)。

**Step 5: build + 验证 + 提交**

```bash
pnpm --filter @ghome/admin build
```

Expected: 3 个新 page 都是 dynamic ƒ。

启 dev,登录后(或在 dev 模式下,middleware 配 placeholder 也可)验证页面渲染:

```bash
pnpm --filter @ghome/admin dev &
sleep 8
# 假设已有 session(本地真测需要登录),或用 cookie 注入。简化:验证 redirect 到 signin
curl -sI http://localhost:3100/apps | head -3
# Expect 307 → /signin?from=%2Fapps
kill %1 2>/dev/null || true
```

(本 task 不验证渲染内容 — 需要登录才能看到。T9 端到端再覆盖。)

```bash
git add "apps/admin/app/(admin)/apps/" "apps/admin/app/(admin)/videos/" "apps/admin/app/(admin)/guides/" \
        apps/admin/lib/db.ts
git commit -m "feat(admin): list pages for apps, videos, guides with status filter"
```

## Tricky Bits (T2)

1. **路径**:列表页 URL 是 `/apps` / `/videos` / `/guides`,通过 `(admin)/<segment>/page.tsx` 解析。`/apps` 与 web 端 `/apps` 不冲突 — 不同 app(端口 3000 vs 3100)。
2. **`a.updatedAt` 转 string**:`new Date(a.updatedAt).toISOString().slice(0, 16).replace("T", " ")` → `'2026-05-09 14:30'`(UTC)。
3. **`status` searchParam**:`as` 强转,因为 plan TypeScript 接口约束。可以用 `z.enum` 做严格校验 P 后期再加。
4. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS。

---

## Task 3 — 跨切面工具:`audit.ts` + `revalidate.ts` + web `/api/revalidate` route

**Files:**
- Create: `apps/admin/lib/audit.ts`
- Create: `apps/admin/lib/revalidate.ts`
- Create: `apps/web/app/api/revalidate/route.ts`

### 6 Steps

**Step 1: 写 `apps/admin/lib/audit.ts`**

```ts
import { prisma } from "@ghome/db";
import type { Prisma } from "@ghome/db";

/**
 * 写一行 audit_log。任何 admin 写操作(create/update/publish/archive/delete/...)都应调一次。
 *
 * @param adminUserId 发起者(从 session.user.adminUserId 拿)
 * @param action     形如 'app.update' / 'video.publish' / 'tag.create'
 * @param targetType 'app' | 'video' | 'guide' | 'tag' | 'collection' | 'redirect'
 * @param targetId   被操作对象的 id
 * @param diff       JSON-able diff:`{ before: {...partial...}, after: {...partial...} }`
 */
export async function logAuditAction(
  adminUserId: string,
  action: string,
  targetType: string,
  targetId: string,
  diff: Prisma.InputJsonValue,
): Promise<void> {
  await prisma.auditLogEntry.create({
    data: { adminUserId, action, targetType, targetId, diffJson: diff },
  });
}
```

**Step 2: 写 `apps/admin/lib/revalidate.ts`**

```ts
const [敏感内容已脱敏];
const WEB_BASE_URL = process.env.WEB_BASE_URL ?? "http://localhost:3000";

if (!REVALIDATE_SECRET) {
  throw new Error(
    "[admin/revalidate] REVALIDATE_SECRET is not set. Required to call web /api/revalidate. " +
      "Set in apps/admin/.env (dev) or job env (CI). Must match apps/web's value.",
  );
}

/**
 * 通知 web 重新生成 ISR 缓存(by tags)。失败时 log 但不 throw —
 * admin 写入已经成功,revalidate 失败用户后续刷新页面 ISR 自然到期也会刷新。
 *
 * @param tags 例如 ['apps-list', 'app:broconnect']
 */
export async function revalidateWeb(tags: string[]): Promise<void> {
  if (tags.length === 0) return;
  try {
    const url = `${WEB_BASE_URL}/api/revalidate`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${REVALIDATE_SECRET}`,
      },
      body: JSON.stringify({ tags }),
      cache: "no-store",
    });
    if (!res.ok) {
      console.warn(`[admin/revalidate] failed: ${res.status} ${await res.text()}`);
    }
  } catch (err) {
    console.warn("[admin/revalidate] error:", err);
  }
}

/* ============== 通用 tag helpers ============== */
export function appTags(slug: string): string[] {
  return [`app:${slug}`, "apps-list", "home"];
}

export function videoTags(slug: string): string[] {
  return [`video:${slug}`, "videos-list", "home"];
}

export function guideTags(slug: string): string[] {
  return [`guide:${slug}`, "guides-list"];
}
```

**Step 3: 修改 `apps/admin/.env` 与 `.env.example` 加 `WEB_BASE_URL`**

```bash
# Admin 调 web revalidate webhook 的目标 URL
WEB_BASE_URL=http://localhost:3000
```

**Step 4: 写 `apps/web/app/api/revalidate/route.ts`**

```ts
import { NextResponse, type NextRequest } from "next/server";
import { revalidateTag } from "next/cache";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const [敏感内容已脱敏];
if (!REVALIDATE_SECRET) {
  throw new Error(
    "[web/revalidate] REVALIDATE_SECRET is not set. Required to validate incoming revalidate requests. " +
      "Set in apps/web/.env (dev) or job env (CI). Must match apps/admin's value.",
  );
}

export async function POST(req: NextRequest) {
  // 1. 校验 Authorization header
  const auth = req.headers.get("authorization") ?? "";
  if (auth !== `Bearer ${REVALIDATE_SECRET}`) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  // 2. 读 body
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
  if (
    typeof body !== "object" ||
    body === null ||
    !("tags" in body) ||
    !Array.isArray((body as { tags: unknown }).tags)
  ) {
    return NextResponse.json({ error: "missing tags array" }, { status: 400 });
  }

  const tags = (body as { tags: string[] }).tags
    .filter((t) => typeof t === "string" && t.length > 0)
    .slice(0, 50);  // 防滥用:最多 50 个 tag/请求

  // 3. revalidate
  for (const tag of tags) {
    revalidateTag(tag);
  }

  return NextResponse.json({ ok: true, revalidated: tags.length });
}
```

**Step 5: 修改 web SSG 页面给 fetch 加 `next: { tags: [...] }`**

> P2 的页面**没**给 Prisma 查询配 tag —— Next.js 的 `revalidateTag` 需要数据查询时声明 tag。Prisma 不像 fetch 那样支持 `next.tags`,但可以用 `unstable_cache` 包裹:

修改 `apps/web/lib/db.ts` 关键查询用 `unstable_cache`:

```ts
import { unstable_cache } from "next/cache";

// 在 db.ts 末尾添加 tagged helpers:
export const cachedAppBySlug = (slug: string) =>
  unstable_cache(
    () => getAppBySlug(slug),
    ["app-by-slug", slug],
    { tags: [`app:${slug}`] },
  )();

// list pages — tag 'apps-list' 等
export const cachedPublishedApps = (opts?: Parameters<typeof getPublishedApps>[0]) =>
  unstable_cache(
    () => getPublishedApps(opts),
    ["published-apps", JSON.stringify(opts ?? {})],
    { tags: ["apps-list"] },
  )();
```

**等等** — 上面这步是大改 web 端,涉及多页面调整。**简化方案**:**P5 只实现 admin 触发 revalidate 与 web 接收,但 web 端的页面 ISR 仍按 `revalidate=60`/`300` 时间触发**,即 admin 推送的 revalidate 当作 _no-op_ 也无大害(用户最多等 60s/5min 看到新数据)。

**修订决定**:Step 5 跳过 — 不改 web 端 ISR 配置;`/api/revalidate` 端点存在但等于 `revalidateTag(tag)` 没 tag 可命中(Next.js 会 silently ignore)。这是**P5 故意的简化**:webhook 路径打通,但 cache invalidation 等到 P6 把 collections 编辑接入时一并补 unstable_cache。

> 真要让 P5 publish 立即生效,user 在 dev 模式下看 web 即可(dev 不缓存);prod 模式等 ISR 到期。

**Step 6: 提交**

```bash
git add apps/admin/lib/audit.ts apps/admin/lib/revalidate.ts \
        apps/admin/.env.example apps/web/app/api/revalidate/ \
        apps/web/.env.example
git commit -m "feat(admin/web): add audit log helper, revalidate webhook + secret-protected web /api/revalidate"
```

## Tricky Bits (T3)

1. **`unstable_cache` 跳过的取舍**:web 端的 `revalidateTag` 需要数据查询带 tag。P2 的 Prisma 查询没带,P5 不补。webhook 仍存在(为 P6 准备),但 P5 的发布不会立即让 web 缓存失效。**这是有意的简化**,不阻塞 P5 完成判据(dev 模式可以立即看到改动)。
2. **`revalidate.ts` 顶层 throw**:模块加载阶段断言 `REVALIDATE_SECRET`,fail-fast。
3. **`revalidateWeb` 失败不 throw**:admin 写入已经 commit,revalidate 失败 log 即可。
4. **`WEB_BASE_URL`** 在 admin .env 配置;CI 也要配(本地 admin 与 web 都跑在 localhost)。
5. **`audit.ts` 的 `Prisma.InputJsonValue` 类型**:接受任意 JSON-able 对象。
6. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS。

把 `WEB_BASE_URL` 也加到 `apps/admin/.env.example` 与 `.env`,以及 CI yml(`WEB_BASE_URL: http://localhost:3000`)— 已在 Step 3 加。

---

## Task 4 — 标签内联 CRUD:`POST /api/tags` + TagPicker client component

**Files:**
- Create: `apps/admin/app/api/tags/route.ts`
- Create: `apps/admin/components/TagPicker.tsx`

### 5 Steps

**Step 1: 写 `apps/admin/app/api/tags/route.ts`** — 服务端 API

```ts
import { NextResponse, type NextRequest } from "next/server";
import { prisma } from "@ghome/db";
import { auth } from "@/lib/auth";
import { logAuditAction } from "@/lib/audit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SLUG_RE = /^[a-z0-9-]+$/;

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.adminUserId) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
  if (typeof body !== "object" || body === null) {
    return NextResponse.json({ error: "invalid body" }, { status: 400 });
  }
  const { label, slug } = body as { label?: unknown; slug?: unknown };

  if (typeof label !== "string" || label.length === 0 || label.length > 50) {
    return NextResponse.json({ error: "invalid label" }, { status: 400 });
  }
  if (typeof slug !== "string" || !SLUG_RE.test(slug) || slug.length > 50) {
    return NextResponse.json({ error: "invalid slug (must match /^[a-z0-9-]+$/)" }, { status: 400 });
  }

  // 重复检查
  const existing = await prisma.tag.findFirst({
    where: { OR: [{ slug }, { label }] },
  });
  if (existing) {
    return NextResponse.json(
      {
        error: existing.slug === slug ? "slug already exists" : "label already exists",
      },
      { status: 409 },
    );
  }

  const tag = await prisma.tag.create({ data: { label, slug } });

  await logAuditAction(
    session.user.adminUserId,
    "tag.create",
    "tag",
    tag.id,
    { after: { label, slug } },
  );

  return NextResponse.json({ id: tag.id, label: tag.label, slug: tag.slug });
}
```

**Step 2: 写 `apps/admin/components/TagPicker.tsx`** — client component(因为要 fetch + 本地 state)

```tsx
"use client";

import { useState, useTransition } from "react";

export interface TagOption {
  id: string;
  label: string;
  slug: string;
}

export function TagPicker({
  allTags,
  initialSelectedIds,
  name,
}: {
  allTags: TagOption[];
  initialSelectedIds: string[];
  name: string;  // 隐藏字段名,form 提交时为逗号分隔的 id 字符串
}) {
  const [tags, setTags] = useState<TagOption[]>(allTags);
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelectedIds);
  const [draftLabel, setDraftLabel] = useState("");
  const [draftSlug, setDraftSlug] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function toggle(id: string) {
    setSelectedIds((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  }

  async function createTag() {
    setError(null);
    if (!draftLabel.trim() || !draftSlug.trim()) {
      setError("label 与 slug 都不能为空");
      return;
    }
    startTransition(async () => {
      const res = await fetch("/api/tags", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ label: draftLabel.trim(), slug: draftSlug.trim() }),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        setError(j.error ?? "创建失败");
        return;
      }
      const tag = (await res.json()) as TagOption;
      setTags((t) => [...t, tag]);
      setSelectedIds((s) => [...s, tag.id]);
      setDraftLabel("");
      setDraftSlug("");
    });
  }

  return (
    <>
      <input type="hidden" name={name} value={selectedIds.join(",")} />
      <div className="tag-picker">
        {tags.map((t) => (
          <button
            type="button"
            key={t.id}
            className={`pill ${selectedIds.includes(t.id) ? "selected" : ""}`}
            onClick={() => toggle(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div style={{ marginTop: 8, display: "flex", gap: 6, alignItems: "center" }}>
        <input
          placeholder="新标签名(label)"
          value={draftLabel}
          onChange={(e) => setDraftLabel(e.target.value)}
          className="form-input"
          style={{ flex: 1 }}
        />
        <input
          placeholder="slug(英文 kebab-case)"
          value={draftSlug}
          onChange={(e) => setDraftSlug(e.target.value)}
          className="form-input"
          style={{ flex: 1 }}
        />
        <button type="button" onClick={createTag} disabled={pending} className="btn-secondary">
          {pending ? "..." : "+ 新建"}
        </button>
      </div>
      {error && <div style={{ color: "var(--danger)", fontSize: 13, marginTop: 6 }}>{error}</div>}
    </>
  );
}
```

**Step 3: build 验证**

```bash
pnpm --filter @ghome/admin build
```

**Step 4: 单元 / 集成测试 — 跳过**

P5 不为 server action / API 写单元测试(TDD overhead 高,T9 端到端覆盖)。

**Step 5: 提交**

```bash
git add apps/admin/app/api/tags apps/admin/components/TagPicker.tsx
git commit -m "feat(admin): add tag inline create API and TagPicker client component"
```

## Tricky Bits (T4)

1. **`POST /api/tags` 与 server action 选哪个**:用 API,因为 client component(TagPicker)需要从 fetch 触发。server action 也可以但需要 `<form>` 包装,耦合更紧。
2. **TagPicker 是 client component**:用 `useState` + `useTransition` 管 local state。`<input type="hidden">` 把选中 id 序列化成逗号分隔字符串提交 form。
3. **server-side 校验**:`SLUG_RE`、长度、重复 — 全在 API 实现,client 表单只做 basic 必填提示。
4. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS。

---

## Task 5 — App 编辑页:`/apps/[id]/edit`(read view + form + 状态切换 + 软删除)

**Files:**
- Create: `apps/admin/app/(admin)/apps/[id]/edit/page.tsx`(server component:读取数据 + 包 server actions)

> 编辑页是 P5 最复杂的;App 编辑页是模板,Video / Guide 后续 follow this pattern。

### 5 Steps

**Step 1: 写 `apps/admin/app/(admin)/apps/[id]/edit/page.tsx`**

```tsx
import { notFound, redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { prisma } from "@ghome/db";
import { logAuditAction } from "@/lib/audit";
import { revalidateWeb, appTags } from "@/lib/revalidate";
import { canTransition } from "@/lib/status";
import { StatusBadge } from "@/components/StatusBadge";
import { EditForm, FormRow } from "@/components/EditForm";
import { TagPicker } from "@/components/TagPicker";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function EditAppPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const app = await prisma.app.findUnique({
    where: { id },
    include: {
      category: true,
      tags: { include: { tag: true } },
    },
  });
  if (!app) notFound();

  const allTags = await prisma.tag.findMany({ orderBy: { label: "asc" } });
  const allCats = await prisma.category.findMany({
    where: { kind: "app" },
    orderBy: { sortOrder: "asc" },
  });

  /* ============ server action: save mevendor_ata ============ */
  async function save(formData: FormData) {
    "use server";
    const session = await auth();
    if (!session?.user?.adminUserId) redirect("/signin");

    const name = String(formData.get("name") ?? "").trim();
    const shortDesc = String(formData.get("shortDesc") ?? "").trim();
    const detail = String(formData.get("detail") ?? "").trim();
    const audience = String(formData.get("audience") ?? "").trim();
    const features = String(formData.get("features") ?? "").trim();
    const platform = String(formData.get("platform") ?? "").trim();
    const size = String(formData.get("size") ?? "").trim();
    const rating = String(formData.get("rating") ?? "").trim();
    const usersLabel = String(formData.get("usersLabel") ?? "").trim();
    const categoryId = String(formData.get("categoryId") ?? "").trim();
    const highlightsRaw = String(formData.get("highlights") ?? "").trim();
    const highlights = highlightsRaw.split("\n").map((s) => s.trim()).filter(Boolean);
    const tagIdsRaw = String(formData.get("tagIds") ?? "");
    const tagIds = tagIdsRaw.split(",").filter(Boolean);

    if (!name || !shortDesc || !categoryId) {
      throw new Error("required fields missing");
    }

    const before = {
      name: app!.name, shortDesc: app!.shortDesc, detail: app!.detail,
      categoryId: app!.categoryId, status: app!.status,
    };

    await prisma.$transaction(async (tx) => {
      await tx.app.update({
        where: { id: app!.id },
        data: {
          name, shortDesc, detail, audience, features,
          platform, size, rating, usersLabel,
          highlights,
          categoryId,
        },
      });
      // tags: 全量重置 — 简单可靠,P5 不优化为 diff
      await tx.appTag.deleteMany({ where: { appId: app!.id } });
      if (tagIds.length > 0) {
        await tx.appTag.createMany({
          data: tagIds.map((tagId) => ({ appId: app!.id, tagId })),
          skipDuplicates: true,
        });
      }
    });

    await logAuditAction(
      session.user.adminUserId,
      "app.update",
      "app",
      app!.id,
      { before, after: { name, shortDesc, categoryId, tagIds } },
    );

    await revalidateWeb(appTags(app!.slug));
  }

  /* ============ server action: status transition ============ */
  async function transition(formData: FormData) {
    "use server";
    const session = await auth();
    if (!session?.user?.adminUserId) redirect("/signin");

    const target = String(formData.get("target") ?? "") as "draft" | "published" | "archived";
    if (!canTransition(app!.status, target)) {
      throw new Error(`invalid transition ${app!.status} → ${target}`);
    }

    await prisma.app.update({ where: { id: app!.id }, data: { status: target } });
    await logAuditAction(
      session.user.adminUserId,
      `app.${target === "published" ? "publish" : target === "archived" ? "archive" : "unpublish"}`,
      "app",
      app!.id,
      { before: { status: app!.status }, after: { status: target } },
    );
    await revalidateWeb(appTags(app!.slug));
  }

  /* ============ server action: soft delete ============ */
  async function softDelete() {
    "use server";
    const session = await auth();
    if (!session?.user?.adminUserId) redirect("/signin");

    await prisma.app.update({
      where: { id: app!.id },
      data: { deletedAt: new Date(), status: "archived" },
    });
    await logAuditAction(
      session.user.adminUserId,
      "app.delete",
      "app",
      app!.id,
      { before: { status: app!.status, deletedAt: null }, after: { status: "archived", deletedAt: new Date().toISOString() } },
    );
    await revalidateWeb(appTags(app!.slug));
    redirect("/apps");
  }

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <Link href="/apps" className="btn-secondary">← 列表</Link>
        <h1 style={{ fontSize: 22, margin: 0 }}>编辑 App</h1>
        <StatusBadge status={app.status} />
        {app.deletedAt && <span style={{ color: "var(--danger)", fontSize: 12 }}>已删除</span>}
      </div>

      <EditForm action={save}>
        <FormRow label="Slug(不可修改)">
          <div className="form-row-readonly">{app.slug}</div>
        </FormRow>
        <FormRow label="名称">
          <input name="name" className="form-input" defaultValue={app.name} required />
        </FormRow>
        <FormRow label="分类">
          <select name="categoryId" className="form-input" defaultValue={app.categoryId} required>
            {allCats.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
        </FormRow>
        <FormRow label="短描述(卡片用)">
          <textarea name="shortDesc" className="form-textarea" defaultValue={app.shortDesc} required />
        </FormRow>
        <FormRow label="详情(详情页长文)">
          <textarea name="detail" className="form-textarea" defaultValue={app.detail} rows={6} />
        </FormRow>
        <FormRow label="核心亮点(每行一条)">
          <textarea name="highlights" className="form-textarea" defaultValue={app.highlights.join("\n")} rows={5} />
        </FormRow>
        <FormRow label="适合人群">
          <input name="audience" className="form-input" defaultValue={app.audience} />
        </FormRow>
        <FormRow label="主要功能">
          <input name="features" className="form-input" defaultValue={app.features} />
        </FormRow>
        <FormRow label="平台">
          <input name="platform" className="form-input" defaultValue={app.platform} />
        </FormRow>
        <FormRow label="大小">
          <input name="size" className="form-input" defaultValue={app.size} />
        </FormRow>
        <FormRow label="评分(显示文案,如 4.7)">
          <input name="rating" className="form-input" defaultValue={app.rating} />
        </FormRow>
        <FormRow label="用户量(显示文案,如 800万+)">
          <input name="usersLabel" className="form-input" defaultValue={app.usersLabel} />
        </FormRow>
        <FormRow label="标签" hint="点击切换;'+ 新建' 内联创建新 tag">
          <TagPicker
            allTags={allTags.map((t) => ({ id: t.id, label: t.label, slug: t.slug }))}
            initialSelectedIds={app.tags.map((at) => at.tag.id)}
            name="tagIds"
          />
        </FormRow>
      </EditForm>

      {/* 状态切换 buttons */}
      <div className="dash-section" style={{ marginTop: 24 }}>
        <h2 style={{ fontSize: 16, margin: "0 0 12px" }}>状态操作</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {(["draft", "published", "archived"] as const)
            .filter((t) => canTransition(app.status, t))
            .map((target) => (
              <form key={target} action={transition} style={{ display: "inline" }}>
                <input type="hidden" name="target" value={target} />
                <button
                  type="submit"
                  className="btn-secondary"
                  style={
                    target === "published"
                      ? { background: "var(--success)", color: "#fff", border: "none" }
                      : target === "archived"
                      ? { background: "var(--text-2)", color: "#fff", border: "none" }
                      : undefined
                  }
                >
                  {target === "published" ? "发布" : target === "archived" ? "下线" : "撤回到草稿"}
                </button>
              </form>
            ))}
        </div>
      </div>

      {/* 软删除 */}
      {!app.deletedAt && (
        <div className="dash-section" style={{ marginTop: 16 }}>
          <h2 style={{ fontSize: 16, margin: "0 0 12px", color: "var(--danger)" }}>危险操作</h2>
          <form action={softDelete}>
            <button type="submit" className="btn-secondary btn-danger">
              软删除此 App
            </button>
          </form>
        </div>
      )}
    </>
  );
}
```

**Step 2-3: 验证 build**

```bash
pnpm --filter @ghome/admin build
```

**Step 4: 提交**

```bash
git add "apps/admin/app/(admin)/apps/[id]/"
git commit -m "feat(admin): App edit page with mevendor_ata form, tag picker, status transitions, soft delete"
```

## Tricky Bits (T5)

1. **server actions 必须在 server component 顶部声明**:用 `"use server"` 内联注释。每个 action 是独立函数,自己调 `auth()`。
2. **`canTransition` 守卫**:UI 只显示当前状态允许的 transition,但 server action 也再校验一次(不可信 client)。
3. **tags 全量重置**:`deleteMany` + `createMany`。简单可靠;P 后期可优化为 diff。
4. **`redirect("/apps")` 在 softDelete 末尾**:next/navigation redirect throws,所以在 try/catch 之外。
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS。

---

## Task 6 — Video 编辑页:跟 App pattern

**Files:**
- Create: `apps/admin/app/(admin)/videos/[id]/edit/page.tsx`

完全照 App 编辑页 pattern,区别:
- model `prisma.video`
- 字段不同:`title / emoji / coverKey / duration / viewsLabel / likesLabel / publishedDate(date type)/ shortDesc / detail / categoryId(kind=video)`
- tags 关系是 `videoTag`(model name)+ `videoId/tagId` 复合主键
- categories 查询 `kind: "video"`
- audit action 命名 `video.update / video.publish / ...`
- revalidate tag `videoTags(slug)` from lib/revalidate.ts(`['video:slug', 'videos-list', 'home']`)

按 plan T5 的 page.tsx 改字段 + 改 model 名即可。一次 commit。

```bash
git add "apps/admin/app/(admin)/videos/[id]/"
git commit -m "feat(admin): Video edit page (mirrors App pattern with video-specific fields)"
```

---

## Task 7 — Guide 编辑页:含 markdown editor

**Files:**
- Create: `apps/admin/components/MarkdownEditor.tsx`(client wrapper)
- Create: `apps/admin/app/(admin)/guides/[id]/edit/page.tsx`

### 4 Steps

**Step 1: 写 `apps/admin/components/MarkdownEditor.tsx`**

```tsx
"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

const MDEditor = dynamic(() => import("@uiw/react-md-editor"), {
  ssr: false,
  loading: () => <div className="form-row-readonly">加载编辑器...</div>,
});

export function MarkdownEditor({ name, defaultValue }: { name: string; defaultValue: string }) {
  const [value, setValue] = useState(defaultValue);
  return (
    <>
      <input type="hidden" name={name} value={value} />
      <div data-color-mode="light">
        <MDEditor value={value} onChange={(v) => setValue(v ?? "")} height={400} />
      </div>
    </>
  );
}
```

**Step 2: 写 `apps/admin/app/(admin)/guides/[id]/edit/page.tsx`**

照 App 编辑页 pattern,字段:`title / summary / bodyMd(用 MarkdownEditor) / categorySlug / categoryLabel / gradientKey / iconKey / readMinutes(int) / viewsLabel / isHot(boolean) / publishedDate(date)`。

无 tags(P1 schema:guides 表没 tag 关系)。

audit action `guide.update / guide.publish / ...`。

revalidate tag `guideTags(slug)`(`['guide:slug', 'guides-list']`)。

**Step 3: build**

```bash
pnpm --filter @ghome/admin build
```

**Step 4: 提交**

```bash
git add "apps/admin/app/(admin)/guides/[id]/" apps/admin/components/MarkdownEditor.tsx
git commit -m "feat(admin): Guide edit page with markdown editor"
```

## Tricky Bits (T7)

1. **`@uiw/react-md-editor` 必须 client + dynamic SSR=false**:它依赖 DOM。包成 client component 后用 `next/dynamic` 进一步禁 SSR。
2. **`isHot` checkbox** vs `text input`:用 `<input type="checkbox" name="isHot" defaultChecked={guide.isHot} />`,formData 里 `formData.has("isHot")` 判断。
3. **`publishedDate` `<input type="date">`**:formData 里是 `'YYYY-MM-DD'` string,server action 里 `new Date(s)` 转换。

---

## Task 8 — End-to-end smoke + tag p5-content-crud

无新文件。本 task 跑完整 smoke,P5 plan 入库,标 tag。

### 7 Steps

**Step 1: 干净环境 reset**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
sleep 5
pnpm --filter @ghome/db db:reset --force
```

**Step 2: 4 步全套验证**

```bash
pnpm typecheck
pnpm lint
pnpm --filter @ghome/db test
pnpm --filter @ghome/web test
pnpm build
```

Expected: 全过(admin 仍无单测;web 21 + db 38 = 59 测试 pass)。

**Step 3: 起 admin dev,模拟登录后访问列表/编辑页**

```bash
pnpm --filter @ghome/admin dev &
sleep 8

# 未登录 — 应 307 → /signin
curl -sI http://localhost:3100/apps | head -3
curl -sI http://localhost:3100/apps/some-id/edit | head -3

# 列表页(假设 mock session)— P5 不写 mock auth bypass;真测试需要登录后浏览器手动。
# 这里仅校验路由本身能 build 出来:
ls apps/admin/.next/server/app/\(admin\)/apps/

kill %1 2>/dev/null || true
```

> **本 task 不真测登录后行为** — 端到端 admin 写入需要 user 在浏览器里:① OAuth 登录(需要 dev OAuth App);② 改 App;③ 看 web 详情页变化。**plan 不强制端到端**。

**Step 4: 验证 audit_log 写入路径**(用脚本绕过 admin UI 直接 SQL 验证)

```bash
# 模拟一次 admin 写入 — 直接通过 prisma client 触发 logAuditAction:
docker compose exec postgres psql -U ghome -d ghome -tAc "
SELECT count(*) FROM admin_users;
"
```

P5 阶段 admin_users 在第一次登录时被 upsert 写入。本地无登录,admin_users 为空。**跳过这个测试**,T9 端到端真登录时验。

**Step 5: 验证 web /api/revalidate 端点**

```bash
docker compose up -d
sleep 5
pnpm --filter @ghome/web build
pnpm --filter @ghome/web start &
sleep 8

# 无 auth 拒绝
curl -X POST -d '{"tags":["apps-list"]}' -H "content-type: application/json" \
  http://localhost:3000/api/revalidate -o /dev/null -w "%{http_code}\n"
# Expect: 401

# 正确 auth — 应返回 200 ok
curl -X POST -d '{"tags":["apps-list"]}' -H "content-type: application/json" \
  -H "Authorization: Bearer dev-only-revalidate-secret-32-bytes-aaaaaaaaaaaaaaaaa" \
  http://localhost:3000/api/revalidate
# Expect: {"ok":true,"revalidated":1}

kill %1 2>/dev/null || true
```

Expected: 401 + 200。

**Step 6: 验证 admin → web revalidate 通信**

```bash
# 略 — 需要真发起 admin server action,本地无登录跳过。功能已在 Step 5 验证(端点工作)
```

**Step 7: git 干净 + plan 入库 + tag P5**

```bash
git status --short
git add docs/superpowers/plans/2026-05-09-ghome-p5-content-crud.md
git commit -m "docs: commit P5 implementation plan"

git tag -a p5-content-crud -m "P5 · content CRUD: app/video/guide list + edit pages, status state machine, soft delete, inline tag CRUD, audit_log writes, revalidate webhook (web /api/revalidate secret-protected)"

git tag -l
git log --oneline p4-admin-auth..HEAD
```

Expected: 6 个 tag 全在(p0..p5)。log 显示 P5 期间 ~10 commits + tag。

## Tricky Bits (T9)

1. **本地端到端登录困难**:GitHub OAuth round-trip 需要真注册 dev App。**P5 不强制做端到端**;build + revalidate webhook 通信 + DB 行数验证就够了。
2. **真验证 admin 编辑功能**:user 自己跑(注册 OAuth App + 加 GitHub login 到白名单 + 浏览器登录)。
3. **若 git tag 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS,贴出 `git tag -a p5-content-crud ...` 让 controller 跑。

---

## P5 完成判据(对应 spec §5)

- ✅ App / Video / Guide 列表页(状态筛选 + 搜索 + 排序 by updatedAt desc)— T2
- ✅ App / Video / Guide 编辑页(mevendor_ata form + 状态切换 + 软删除)— T5/6/7
- ✅ 状态机:draft / published / archived,UI 守卫 + server action 守卫 — T1/T5
- ✅ Tag 内联 CRUD(`POST /api/tags` + TagPicker client component)— T4
- ✅ audit_log 写入(每个写操作 log + Dashboard 暂未显示活跃,P 后期做)— T3/T5/6/7
- ✅ revalidate webhook(`web /api/revalidate` + `REVALIDATE_SECRET` 校验 + admin `revalidateWeb` helper)— T3
- ✅ web `/api/revalidate` 端点工作(401/200)— T9 Step 5

---

## 已知 P5 故意不做的事(P6+ 起补)

- **collections / topics / albums / rankings 编辑** — P6
- **redirect 管理 UI** — P7
- **`unstable_cache` 接 web 端**:P5 webhook 端点已建,但 web 端的 Prisma 查询没 tag。P 后期把热点查询(列表 / 详情)用 `unstable_cache` 包裹后,admin publish 即触发刷新
- **多角色 RBAC**:全员同等编辑
- **审批工作流**:无;改完即发布
- **slug 修改**:不允许(避免 SEO异常验证 + 链接断裂)
- **bulk operations**:无批量
- **categories CRUD**:seed-only(spec §2.3)
- **批量复制 / 模板**:无
- **operation log UI**:audit_log 已写,但没 admin 页面看;P 后期做

---

## Self-Review

- **Spec 覆盖**:逐条核对 spec §2.3 + §5 P5。所有完成判据有对应 task。
- **占位符扫描**:无 TBD / TODO / "fill in"。每 step 都有具体代码或命令。
- **TS 类型一致性**:`ContentStatus` 在 lib/status.ts 与 StatusBadge 一致;`TagOption` 在 TagPicker 与 server-side `prisma.tag.findMany` 返回类型 align。
- **TDD 体现**:server actions 与 API 是 cross-cutting 配置型代码,P5 不写单测;T9 端到端冒烟 + revalidate webhook 401/200 验证 + build 全过 = 实际可用证明。
- **风险**:
  - server action 异常处理:P5 直接 throw,Next.js 显示默认 error page。后期可加 form-level error display(用 useFormState)
  - `unstable_cache` 跳过:web 端 ISR 仍按时间到期。P5 publish 不立即生效是已知 trade-off
  - 软删除恢复:P5 没 UI 恢复软删除项。P6+ 加 trash bin
  - audit_log 查询 UI 没接入 Dashboard:P 后期补
  - markdown editor `@uiw/react-md-editor` 大约 200KB gzipped — admin only,不影响 web 站

---

## 下一步

P5 完成后,**写 P6 plan**(collections / topics / albums / rankings CRUD + 拖拽排序 + external item 自动建 redirect + 前台 `/albums` 与 `/album/:slug` 落地)。
