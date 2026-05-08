---
id: "doc-6efa7274232b"
title: "Ghome P8 · ILIKE + pgtrgm 搜索 + SEO异常验证异常验证/404/性能 收尾 Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p8-search-wrapup.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p8-search-wrapup.md"
sourceSha256: "029f7d41d0c004bc92e0d41cc50f85fdeabfdbf412524f72fa1b43a586e80754"
sourceSystem: "project-doc"
---

# Ghome P8 · ILIKE + pgtrgm 搜索 + SEO异常验证异常验证/404/性能 收尾 Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p8-search-wrapup.md`

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ghome MVP 收尾。三件事:
1. **搜索接口**:`apps/web/lib/db.ts` 实现 `searchAll(q)`,并行查 apps / videos / guides 三类(各 ≤10),走 P1 已建好的 `pg_trgm GIN` 索引(对 `coalesce(...) || ' ' || coalesce(...)` 表达式),tag 命中走子查询反查;按"name/title 命中 > tag 命中 > desc 命中"简单权重排序。出口两个:
   - `apps/web/app/api/search/route.ts`(JSON API,Edge 不友好用 `runtime='nodejs'`,**给前端即时联想框预留**;P8 内不实现联想 UI,只有结果页与 API)
   - `apps/web/app/search/page.tsx`(SSR 结果页,从 `?q=` 拿关键词,渲染三栏混合结果)
2. **首页搜索框接通**:`apps/web/app/page.tsx` 当前是 `disabled` 的占位输入,改成 GET `<form action="/search">` + 真实 `<input>` + 提交按钮;`Header.tsx` 顶部也加一个轻量搜索入口
3. **SEO异常验证 + 404 收尾**:
   - 每个详情页加 `generateMetadata`(App / Video / Guide / Topic / Album / Ranking / Tag / Category)— 当前仅 `layout.tsx` 有 root metadata
   - `app/sitemap.ts` 输出全部 published 内容的 URL(每日 ISR 生成)
   - `app/robots.ts` 输出 `User-agent: * Allow: /` + sitemap 链接
   - `not-found.tsx` 加快捷链(回首页 / 看 App / 看视频 / 看指南)+ 加 `metadata.title = '404'`
   - 搜索结果页空态、阻断词(过短 q < 2 char)兜底 UX

**完成判据(spec §6 P8):** 在首页搜索框输入"健身"提交 → `/search?q=%E5%81%A5%E8%BA%AB` 渲染:命中 App(若 detail 含"健身")+ 命中视频(`weekly-fitness-vlog` 等)+ 命中指南(若有)三栏混合结果。Sitemap 在 `https://localhost:3000/sitemap.xml` 列出所有 published 内容路径;robots.txt 允许全爬。

**Architecture:**
- **三表并行查询**:`prisma.$transaction([apps, videos, guides])` 三条 `$queryRaw`,各自带 ORDER BY 简单权重;再用 LIMIT 10 截断。GIN trgm 索引让 ILIKE `'%q%'` 在 9-20 行的小数据集毫秒级返回(P1 索引表达式与查询表达式必须一致才命中,见 Tricky Bits)
- **q 校验**:trim,长度 < 2 char → 直接返回空结果(防全表扫 + 防爆 noise);长度 > 100 char 截断;`%`/`_` LIKE 元字符转义(防 ILIKE 注入扰动 — 不影响安全,只影响匹配语义)
- **/search 页面 SSR**:`export const dynamic = "force-dynamic"`(每次都查),不做 ISR;搜索是低频路径,直查 DB 比维护 cache 更简单
- **/api/search**:同样 `dynamic = 'force-dynamic'` + `runtime = 'nodejs'`(Prisma 直连),返回 `{ apps: [], videos: [], guides: [], q, took: ms }`。**未鉴权**(公开搜索)。**rate limit P8 不做** — 外部部署形态确定后再加;本地 dev 不需要
- **per-detail 页 generateMetadata**:只覆盖 title + description + (可选)opengraph。不引入 og:image 生成器、不引入 canonical 自动检测 — 部署形态定下来再补
- **sitemap.ts**:用 `MetadataRoute.Sitemap` 规范返回,SSG 时构建期跑 `prisma.findMany`;ISR 每天重建一次(`export const revalidate = 86400`)
- **robots.ts**:静态返回(无 DB);引用 `WEB_BASE_URL` 拼 sitemap URL

**Tech Stack:** 全部已有依赖,**无新增包**。
- pg_trgm 扩展 + GIN 索引在 P1 migration 已建好(`apps_search_idx` `videos_search_idx` `guides_search_idx`,见 `packages/db/prisma/migrations/20260509015050_constraints/migration.sql:50-55`)
- Prisma `$queryRaw` + `Prisma.sql` 模板
- Next.js 15 `MetadataRoute.Sitemap` / `MetadataRoute.Robots` 内置

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §4.4 搜索(MVP)、§6 P8。

**前置假设:** P7 已完成,`p7-redirects-audit-aggregate` 标签存在;`apps/web/lib/db.ts` 已有 `getPublishedApps` `getPublishedVideos` `getPublishedGuides`;首页 `search-box` 当前是 `disabled` 占位;14 表 schema 全 seed,`coalesce(...) || ' ' || coalesce(...)` GIN 表达式索引存在。

---

## File Structure(P8 末态)

```
apps/web/
├─ app/
│  ├─ api/
│  │  └─ search/
│  │     └─ route.ts                      # T2:JSON API
│  ├─ search/
│  │  └─ page.tsx                         # T2:SSR 结果页
│  ├─ page.tsx                            # T3 改:search-box 接通 GET form
│  ├─ layout.tsx                          # T4 可能改:扩展 metadata 默认值(description 等)
│  ├─ not-found.tsx                       # T4 改:加快捷链
│  ├─ sitemap.ts                          # T4 新建
│  ├─ robots.ts                           # T4 新建
│  ├─ app/[slug]/page.tsx                 # T4 改:加 generateMetadata
│  ├─ video/[slug]/page.tsx               # T4 改:加 generateMetadata
│  ├─ guide/[slug]/page.tsx               # T4 改:加 generateMetadata
│  ├─ topic/[slug]/page.tsx               # T4 改:加 generateMetadata
│  ├─ album/[slug]/page.tsx               # T4 改:加 generateMetadata
│  ├─ category/[slug]/page.tsx            # T4 改:加 generateMetadata
│  └─ tag/[slug]/page.tsx                 # T4 改:加 generateMetadata
├─ components/
│  └─ Header.tsx                          # T3 改:加搜索快捷入口(可选,顶部小图标)
└─ lib/
   ├─ db.ts                               # T1 扩展:searchAll + 类型
   └─ search.ts                           # T1 新建:q 标准化 / 元字符转义 / 权重打分

apps/web/tests/
└─ search.test.ts                         # T5:DB 集成测试(打 seed,搜"健身"断言三栏均命中)
```

新文件 ~6 + ~9 改动 detail 页。

---

## Conventions(整个 P8 共享)

- **q 标准化**:始终走 `normalizeQuery(raw)` → `{ q, escaped, valid }`;`valid=false` 直接返回空结果。组件传入 raw URL,API/page **同一**入口校验 — 不做两遍
- **三表并行**:用 `await Promise.all([searchApps(q), searchVideos(q), searchGuides(q)])`,各自独立 raw SQL。**不**用单条 UNION SQL — 三类 schema 不同、字段不同,UNION 化会迫使写 cast,反而难读
- **ORDER BY 权重**:`CASE WHEN name ILIKE :q THEN 0 WHEN tag_match THEN 1 ELSE 2 END` 三档权重;同档内 ORDER BY `updated_at DESC`。LIMIT 10
- **响应字段精简**:API 仅返回 `id / slug / name(title) / shortDesc(summary) / iconKey/coverKey / categorySlug` — **不**返回 detail/body_md / **不**返回 `redirect.targetUrl`(防 RSC payload 泄漏)
- **ISR / cache**:`/search` 不缓存(`force-dynamic`);`/api/search` 同;**只有** `sitemap.ts` 用 ISR(`revalidate = 86400`)。robots.ts 是纯静态的(返回常量)
- **metadata.description 长度 ≤ 160 char**:Google 建议
- **不做(P8 范围外)**:
  - 即时联想(typeahead / autocomplete)— 留 P9
  - 搜索分页 — 各类 LIMIT 10 即够 MVP
  - 搜索结果高亮(`<mark>` 包裹关键词)
  - tag 二级筛选 / 排序选项 / "仅 published 30 天内"
  - rate limit / IP 节流
  - sitemap 的 ChangeFreq / Priority 调优(用默认)
  - og:image 生成 / canonical 自动检测 / Twitter Cards / JSON-LD
  - i18n / hreflang
  - 搜索点击打点(/r/:id 已有点击,搜索不打点)
- 提交风格:Conventional Commits;每 task 末尾 commit

---

## Task 1 — 搜索 DB 函数 + q 标准化 helper

**Files:**
- Create: `apps/web/lib/search.ts`
- Modify: `apps/web/lib/db.ts`(末尾追加 `searchAll`)

### 5 Steps

**Step 1: 写 `apps/web/lib/search.ts`** — q 校验 + 元字符转义 + 类型

```ts
export interface NormalizedQuery {
  raw: string;       // 用户原始输入
  q: string;         // trim 后供展示用
  pattern: string;   // ILIKE 用,已转义 + 加 % 包裹
  valid: boolean;    // 长度足够、非空白才有效
}

const MIN_LEN = 2;
const MAX_LEN = 100;

/**
 * 把用户输入转成 ILIKE 安全的模式串。
 * - trim
 * - 长度 [2, 100] 校验,否则 valid=false 提早返回
 * - 转义 ILIKE 元字符 % _ \,避免用户输 'jeff%' 之类引发字面外的匹配
 * - 用 % 包裹两端
 */
export function normalizeQuery(raw: unknown): NormalizedQuery {
  const s = typeof raw === "string" ? raw.trim() : "";
  if (s.length < MIN_LEN) return { raw: String(raw ?? ""), q: s, pattern: "", valid: false };
  const truncated = s.slice(0, MAX_LEN);
  // 顺序:先转 \ 再转 % _,否则先转 % 后转 \ 会把刚加的 \% 又转成 \\%
  const escaped = truncated
    .replace(/\\/g, "\\\\")
    .replace(/%/g, "\\%")
    .replace(/_/g, "\\_");
  return {
    raw: String(raw ?? ""),
    q: truncated,
    pattern: `%${escaped}%`,
    valid: true,
  };
}

/* 搜索结果类型(每行) */
export interface SearchHit {
  id: string;
  slug: string;
  title: string;       // App.name / Video.title / Guide.title 统一这个字段
  shortDesc: string | null;
  coverKey: string | null;  // App.iconKey / Video.coverKey / Guide.coverKey
  categorySlug: string | null;
  matchScore: number;  // 越小越优先(0=name 命中, 1=tag 命中, 2=desc 命中)
}

export interface SearchResult {
  apps: SearchHit[];
  videos: SearchHit[];
  guides: SearchHit[];
  q: string;
  tookMs: number;
}
```

> **顺序提醒**:`replace(/\\/g, "\\\\")` 必须在 `%` `_` 之前。否则后续转义引入的 `\` 会被前者再吞一次。

**Step 2: 在 `apps/web/lib/db.ts` 末尾追加 `searchAll`**

```ts
import { Prisma } from "@ghome/db";
import { type NormalizedQuery, type SearchHit, type SearchResult } from "./search";

/* ============== 搜索:apps + videos + guides 并行 + 简单权重 ============== */

const PER_TYPE_LIMIT = 10;

async function searchApps(p: NormalizedQuery): Promise<SearchHit[]> {
  // 表达式必须与 P1 GIN 索引表达式严格一致才命中 trgm 索引:
  //   coalesce(name, '') || ' ' || coalesce(short_desc, '') || ' ' || coalesce(detail, '')
  // 同时 tag 命中走子查询反查
  const rows = await prisma.$queryRaw<
    Array<{
      id: string;
      slug: string;
      name: string;
      short_desc: string | null;
      icon_key: string | null;
      category_slug: string | null;
      match_score: number;
    }>
  >`
    SELECT a.id, a.slug, a.name, a.short_desc, a.icon_key,
           c.slug AS category_slug,
           CASE
             WHEN a.name ILIKE ${p.pattern} ESCAPE '\' THEN 0
             WHEN a.id IN (
               SELECT at.app_id FROM app_tags at JOIN tags t ON t.id = at.tag_id
               WHERE t.label ILIKE ${p.pattern} ESCAPE '\'
             ) THEN 1
             ELSE 2
           END AS match_score
    FROM apps a
    LEFT JOIN categories c ON c.id = a.category_id
    WHERE a.status = 'published' AND a.deleted_at IS NULL
      AND (
        (coalesce(a.name, '') || ' ' || coalesce(a.short_desc, '') || ' ' || coalesce(a.detail, ''))
          ILIKE ${p.pattern} ESCAPE '\'
        OR a.id IN (
          SELECT at.app_id FROM app_tags at JOIN tags t ON t.id = at.tag_id
          WHERE t.label ILIKE ${p.pattern} ESCAPE '\'
        )
      )
    ORDER BY match_score ASC, a.updated_at DESC
    LIMIT ${PER_TYPE_LIMIT}
  `;
  return rows.map((r) => ({
    id: r.id,
    slug: r.slug,
    title: r.name,
    shortDesc: r.short_desc,
    coverKey: r.icon_key,
    categorySlug: r.category_slug,
    matchScore: r.match_score,
  }));
}

async function searchVideos(p: NormalizedQuery): Promise<SearchHit[]> {
  const rows = await prisma.$queryRaw<
    Array<{
      id: string;
      slug: string;
      title: string;
      short_desc: string | null;
      cover_key: string | null;
      category_slug: string | null;
      match_score: number;
    }>
  >`
    SELECT v.id, v.slug, v.title, v.short_desc, v.cover_key,
           c.slug AS category_slug,
           CASE
             WHEN v.title ILIKE ${p.pattern} ESCAPE '\' THEN 0
             WHEN v.id IN (
               SELECT vt.video_id FROM video_tags vt JOIN tags t ON t.id = vt.tag_id
               WHERE t.label ILIKE ${p.pattern} ESCAPE '\'
             ) THEN 1
             ELSE 2
           END AS match_score
    FROM videos v
    LEFT JOIN categories c ON c.id = v.category_id
    WHERE v.status = 'published' AND v.deleted_at IS NULL
      AND (
        (coalesce(v.title, '') || ' ' || coalesce(v.short_desc, '') || ' ' || coalesce(v.detail, ''))
          ILIKE ${p.pattern} ESCAPE '\'
        OR v.id IN (
          SELECT vt.video_id FROM video_tags vt JOIN tags t ON t.id = vt.tag_id
          WHERE t.label ILIKE ${p.pattern} ESCAPE '\'
        )
      )
    ORDER BY match_score ASC, v.updated_at DESC
    LIMIT ${PER_TYPE_LIMIT}
  `;
  return rows.map((r) => ({
    id: r.id,
    slug: r.slug,
    title: r.title,
    shortDesc: r.short_desc,
    coverKey: r.cover_key,
    categorySlug: r.category_slug,
    matchScore: r.match_score,
  }));
}

async function searchGuides(p: NormalizedQuery): Promise<SearchHit[]> {
  // guides 没有 tag 关联;只搜 title / summary / body_md
  const rows = await prisma.$queryRaw<
    Array<{
      id: string;
      slug: string;
      title: string;
      summary: string | null;
      cover_key: string | null;
      category_label: string | null;
      match_score: number;
    }>
  >`
    SELECT g.id, g.slug, g.title, g.summary, g.cover_key, g.category_label,
           CASE
             WHEN g.title ILIKE ${p.pattern} ESCAPE '\' THEN 0
             ELSE 2
           END AS match_score
    FROM guides g
    WHERE g.status = 'published' AND g.deleted_at IS NULL
      AND (coalesce(g.title, '') || ' ' || coalesce(g.summary, '') || ' ' || coalesce(g.body_md, ''))
            ILIKE ${p.pattern} ESCAPE '\'
    ORDER BY match_score ASC, g.updated_at DESC
    LIMIT ${PER_TYPE_LIMIT}
  `;
  return rows.map((r) => ({
    id: r.id,
    slug: r.slug,
    title: r.title,
    shortDesc: r.summary,
    coverKey: r.cover_key,
    categorySlug: r.category_label, // guides 用 category_label,展示同一字段
    matchScore: r.match_score,
  }));
}

/** 主入口 */
export async function searchAll(raw: unknown): Promise<SearchResult> {
  const { normalizeQuery } = await import("./search");
  const np = normalizeQuery(raw);
  if (!np.valid) {
    return { apps: [], videos: [], guides: [], q: np.q, tookMs: 0 };
  }
  const start = Date.now();
  const [apps, videos, guides] = await Promise.all([
    searchApps(np),
    searchVideos(np),
    searchGuides(np),
  ]);
  return { apps, videos, guides, q: np.q, tookMs: Date.now() - start };
}
```

> **关键 — GIN 索引命中**:WHERE 子句里 `(coalesce(name, '') || ' ' || coalesce(short_desc, '') || ' ' || coalesce(detail, ''))` 必须**逐字符**与 P1 migration 里 GIN 表达式一致(包括括号、空格、单引号),否则 planner 不会用索引,会退化成 seq scan。可以用 `EXPLAIN ANALYZE` 在本地验证;9-20 行小数据集即使 seq scan 也毫秒级。

> **`ESCAPE '\\'` SQL 子句**:声明 ILIKE 用 `\` 作元字符转义。Prisma raw 模板内字面值是 `'\'`,JS 源码层面写两个反斜杠。

**Step 3: 验证 — 跑 typecheck**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/web typecheck
```

Expected: pass。

**Step 4: 写一个 quick 单测(可选,T5 才补完整集成)**

可在 packages/db/tests 加一个 `apps/web/tests/search.test.ts`(更合适在 web 下,因为 `searchAll` 在 web/lib),T5 才落地。本 task 跳过。

**Step 5: 提交**

```bash
git add apps/web/lib/search.ts apps/web/lib/db.ts
git commit -m "feat(web): searchAll(q) over apps/videos/guides via pg_trgm with weight ordering"
```

## Tricky Bits (T1)

1. **GIN 表达式索引必须严格一致**:WHERE 表达式与 P1 索引表达式逐字符匹配。常见踩坑:`coalesce(x, '')` vs `coalesce(x,'')`(空格)、`||' '||` vs `|| ' ' ||` — 不要"美化"
2. **ILIKE 元字符转义**:`%` `_` `\` 必须转;否则用户输入 `100%` 会被解释成 ILIKE,语义漂移
3. **`ESCAPE '\'`**:让 ILIKE 把 `\%` 看成字面 `%` 而不是通配。所有四条 ILIKE 都加
4. **tag 反查子查询**:`a.id IN (SELECT app_id FROM app_tags JOIN tags WHERE label ILIKE)` — 用 `IN` 比 `EXISTS` 在 Prisma raw 下读起来更直观;两者计划等价
5. **CASE WHEN 权重**:`name/title ILIKE :q THEN 0` 是字段直接命中(注意是 `name/title` 单字段,不是组合表达式 — 让"标题包含 q"优先);`tag_match THEN 1`;`ELSE 2`(整个 coalesce-concat 字符串命中,但不在前两档)
6. **guides 没 tag 表**:权重只有 0/2 两档(title 命中 vs 其他)
7. **`Prisma` 在 web 端**:`apps/web/lib/db.ts` 顶部 `import { prisma, Prisma } from "@ghome/db"`;之前可能没 import `Prisma`,看是否需要加(本 task 用 `Prisma.sql` 不必 — 现在只用模板字符串)
8. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 2 — `/api/search` JSON 路由 + `/search` SSR 结果页

**Files:**
- Create: `apps/web/app/api/search/route.ts`
- Create: `apps/web/app/search/page.tsx`

### 5 Steps

**Step 1: 写 `apps/web/app/api/search/route.ts`**

```ts
import { NextResponse, type NextRequest } from "next/server";
import { searchAll } from "@/lib/db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") ?? "";
  const result = await searchAll(q);
  return NextResponse.json(result, {
    headers: {
      "cache-control": "no-store",
    },
  });
}
```

> **不做** rate limit、不做 CORS(同源)、不做鉴权。

**Step 2: 写 `apps/web/app/search/page.tsx`**

```tsx
import type { Metadata } from "next";
import Link from "next/link";
import { searchAll } from "@/lib/db";
import { AppCard } from "@/components/AppCard";
import { VideoCard } from "@/components/VideoCard";
import { GuideCard } from "@/components/GuideCard";
import { Crumb } from "@/components/Crumb";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "搜索",
  description: "在 Ghome 上搜索 LGBTQ+ 相关 App、视频、指南。",
};

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const sp = await searchParams;
  const raw = (sp.q ?? "").trim();
  const result = await searchAll(raw);
  const noQuery = !raw;
  const tooShort = raw.length > 0 && raw.length < 2;
  const noHits =
    result.apps.length === 0 && result.videos.length === 0 && result.guides.length === 0 && raw.length >= 2;

  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>{raw ? `搜索:${raw}` : "搜索"}</h1>
          {raw.length >= 2 && (
            <p>
              共 {result.apps.length + result.videos.length + result.guides.length} 条结果 · {result.tookMs} ms
            </p>
          )}
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "搜索" }]} />

      <section className="section" style={{ paddingBottom: 80 }}>
        <div className="container">
          {/* 搜索表单(允许在结果页继续输入)*/}
          <form
            method="get"
            action="/search"
            style={{ display: "flex", gap: 8, marginBottom: 32, maxWidth: 720 }}
          >
            <input
              name="q"
              defaultValue={raw}
              placeholder="搜索 App、视频、指南…"
              required
              minLength={2}
              maxLength={100}
              style={{ flex: 1, padding: "12px 16px", border: "1px solid var(--border)", borderRadius: 8, fontSize: 15 }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: "12px 24px" }}>
              搜索
            </button>
          </form>

          {noQuery && (
            <div style={{ color: "var(--text-3)", padding: 40, textAlign: "center" }}>
              请输入关键词
            </div>
          )}
          {tooShort && (
            <div style={{ color: "var(--text-3)", padding: 40, textAlign: "center" }}>
              请至少输入 2 个字符
            </div>
          )}
          {noHits && (
            <div style={{ color: "var(--text-3)", padding: 40, textAlign: "center" }}>
              没有找到与&ldquo;{raw}&rdquo;相关的内容。
            </div>
          )}

          {result.apps.length > 0 && (
            <div style={{ marginBottom: 40 }}>
              <h2 style={{ fontSize: 20, margin: "0 0 16px" }}>App({result.apps.length})</h2>
              <div className="app-grid">
                {result.apps.map((hit) => (
                  <Link
                    key={hit.id}
                    href={`/app/${hit.slug}`}
                    className="app-card"
                    style={{ textDecoration: "none" }}
                  >
                    <div className="app-icon" style={{ background: hit.coverKey ?? "var(--primary-light)" }} />
                    <div className="app-body">
                      <h4>{hit.title}</h4>
                      {hit.shortDesc && <p>{hit.shortDesc}</p>}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {result.videos.length > 0 && (
            <div style={{ marginBottom: 40 }}>
              <h2 style={{ fontSize: 20, margin: "0 0 16px" }}>视频({result.videos.length})</h2>
              <div className="v-grid">
                {result.videos.map((hit) => (
                  <Link
                    key={hit.id}
                    href={`/video/${hit.slug}`}
                    className="v-card"
                    style={{ textDecoration: "none" }}
                  >
                    <div className="v-cover" style={{ background: hit.coverKey ?? "var(--primary-light)" }} />
                    <div className="v-body">
                      <h4>{hit.title}</h4>
                      {hit.shortDesc && <p>{hit.shortDesc}</p>}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {result.guides.length > 0 && (
            <div>
              <h2 style={{ fontSize: 20, margin: "0 0 16px" }}>指南({result.guides.length})</h2>
              <div className="guide-grid">
                {result.guides.map((hit) => (
                  <Link
                    key={hit.id}
                    href={`/guide/${hit.slug}`}
                    className="guide-card"
                    style={{ textDecoration: "none" }}
                  >
                    <div className="guide-cover" style={{ background: hit.coverKey ?? "var(--primary-light)" }} />
                    <div className="guide-body">
                      <h4>{hit.title}</h4>
                      {hit.shortDesc && <p>{hit.shortDesc}</p>}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
```

> **避免直接 `import { AppCard } from "@/components/AppCard"`** — `AppCard` 期待 `AppWithRels`(完整 include),而搜索 hit 只有精简字段。**复制原型卡片 markup** 一次,简洁内联。**或者**给 AppCard / VideoCard / GuideCard 加 `compact` prop 走另一路渲染 — P8 内不做,内联 markup 更简单。

**Step 3: typecheck + build**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
```

Expected: pass。`/api/search` `/search` 都标 `ƒ`(动态)。

**Step 4: 本地冒烟**

```bash
pnpm --filter @ghome/web dev
# 浏览器:
#   http://localhost:3000/search           → "请输入关键词"
#   http://localhost:3000/search?q=a       → "请至少输入 2 个字符"
#   http://localhost:3000/search?q=健身     → 三栏混合结果(健身视频在 seed 里至少一个)
#   http://localhost:3000/api/search?q=健身 → JSON
```

**Step 5: 提交**

```bash
git add "apps/web/app/api/search/route.ts" "apps/web/app/search/page.tsx"
git commit -m "feat(web): /search SSR result page + /api/search JSON endpoint"
```

## Tricky Bits (T2)

1. **不复用 `AppCard` 等组件**:它们的 prop 是 `AppWithRels`(完整 include + tags + redirect 等),搜索 hit 只精简到必要字段。**内联** card markup 更简单且无类型摩擦
2. **`form action="/search"` GET**:表单提交到自己,浏览器把 input 拼成 query string;不需要 client JS
3. **`required minLength=2 maxLength=100`**:HTML5 校验在客户端;但 server action / SSR 仍走 `normalizeQuery` 校验,**不可信任客户端**(用户能改地址栏 URL)
4. **`/search` 与 `/api/search` 同走 `searchAll`**:同一份逻辑、同一份校验,不重复
5. **空态分三档**:无 query、过短、零命中。**确保**这三档在 UI 上视觉清晰,运营/用户能区分
6. **`force-dynamic`**:不做 ISR — 搜索缓存难失效(每个 q 不同),直查更简单。低频路径不会拖慢
7. **`<Link href="/app/${slug}">`**:必须确保 P2 已实现 `/app/[slug]` `/video/[slug]` `/guide/[slug]` 路由(已实现)
8. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 3 — 首页搜索框接通 + Header 入口

**Files:**
- Modify: `apps/web/app/page.tsx`(把 `disabled` 占位改成 GET form)
- Modify: `apps/web/components/Header.tsx`(顶部加搜索快捷入口 link;不放完整搜索框 — 太挤)

### 4 Steps

**Step 1: 改 `apps/web/app/page.tsx` 的 search-box 块**

将这一段:

```tsx
<div className="search-box">
  <span className="si">🔍</span>
  <input placeholder="搜索 App、视频、专题…" disabled />
  <button className="btn-primary" disabled>搜索</button>
</div>
```

改为:

```tsx
<form className="search-box" method="get" action="/search">
  <span className="si">🔍</span>
  <input
    name="q"
    placeholder="搜索 App、视频、指南…"
    required
    minLength={2}
    maxLength={100}
    aria-label="搜索"
  />
  <button type="submit" className="btn-primary">搜索</button>
</form>
```

> **保留 `.search-box` className** — 原型 CSS 已对其 styled,无需改 globals.css。`<form>` 替换 `<div>` 仅语义升级,flex 布局不动。

**Step 2: 改 `apps/web/components/Header.tsx`** — 末尾加一个轻量搜索图标 link

读现有 Header 内容,在导航末尾加:

```tsx
<Link href="/search" className="header-search-link" aria-label="搜索" title="搜索">🔍</Link>
```

> 不嵌入完整 form — Header 空间紧;点击图标进 `/search` 页填关键词更合适。

可选 CSS(若已有 `.header-search-link` 样式则跳过;若无,加到 globals.css):

```css
.header-search-link {
  font-size: 16px;
  padding: 4px 8px;
  border-radius: 6px;
  text-decoration: none;
}
.header-search-link:hover {
  background: var(--bg-2);
}
```

> 同 P7 T1 注意 — `--bg-2` 在本项目未定义,用 `var(--bg)` 替代。

**Step 3: typecheck + build + 冒烟**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build

pnpm --filter @ghome/web dev
# 首页 → 搜"健身"提交 → /search?q=健身 渲染结果
```

**Step 4: 提交**

```bash
git add apps/web/app/page.tsx apps/web/components/Header.tsx apps/web/app/globals.css
git commit -m "feat(web): wire homepage search-box GET form + header search link"
```

## Tricky Bits (T3)

1. **`<form className="search-box">`**:CSS 选择器是 class,不是 element 标签 — 改 div→form 不影响样式
2. **`required minLength` 客户端校验**:阻拦空提交 / < 2 字符提交;**仍**要服务端兜底(已有 `normalizeQuery`)
3. **`name="q"`**:必须叫 `q`,与 `/search` page 的 searchParams.q 对应
4. **Header 不放完整 form**:运营产品已分:首页 hero 是完整搜索入口、Header 上是快捷链接 — 不重复
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 4 — SEO异常验证 收尾:per-detail metadata + sitemap.ts + robots.ts + not-found 优化

**Files:**
- Create: `apps/web/app/sitemap.ts`
- Create: `apps/web/app/robots.ts`
- Modify: `apps/web/app/not-found.tsx`
- Modify: `apps/web/app/layout.tsx`(扩展 metadata 默认值)
- Modify: 7 个 detail 页(加 `generateMetadata`):
  - `apps/web/app/app/[slug]/page.tsx`
  - `apps/web/app/video/[slug]/page.tsx`
  - `apps/web/app/guide/[slug]/page.tsx`
  - `apps/web/app/topic/[slug]/page.tsx`
  - `apps/web/app/album/[slug]/page.tsx`
  - `apps/web/app/category/[slug]/page.tsx`
  - `apps/web/app/tag/[slug]/page.tsx`

### 6 Steps

**Step 1: 写 `apps/web/app/robots.ts`**

```ts
import type { MetadataRoute } from "next";

const WEB_BASE_URL = process.env.NEXT_PUBLIC_WEB_BASE_URL ?? "http://localhost:3000";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: "*", allow: "/" }],
    sitemap: `${WEB_BASE_URL}/sitemap.xml`,
  };
}
```

> 不禁任何路径 — `/r/:id` 是 302,搜索引擎一般不会索引中转;`/api/*` 是动态 API,搜索引擎也不索引(返回 JSON)。MVP 不细分。

**Step 2: 写 `apps/web/app/sitemap.ts`**

```ts
import type { MetadataRoute } from "next";
import {
  getPublishedApps,
  getPublishedVideos,
  getPublishedGuides,
  getCollectionsByKind,
  getAllTags,
  getAppCategories,
  getVideoCategories,
} from "@/lib/db";

const WEB_BASE_URL = process.env.NEXT_PUBLIC_WEB_BASE_URL ?? "http://localhost:3000";

export const revalidate = 86400; // 每日重建

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [apps, videos, guides, topics, albums, tags, appCats, videoCats] = await Promise.all([
    getPublishedApps(),
    getPublishedVideos(),
    getPublishedGuides(),
    getCollectionsByKind("topic"),
    getCollectionsByKind("album"),
    getAllTags(),
    getAppCategories(),
    getVideoCategories(),
  ]);

  const staticUrls = [
    "/",
    "/apps",
    "/videos",
    "/guides",
    "/topics",
    "/albums",
    "/categories",
    "/rankings",
    "/about",
    "/contact",
    "/terms",
    "/search",
  ];

  const now = new Date();
  const out: MetadataRoute.Sitemap = [
    ...staticUrls.map((p) => ({ url: `${WEB_BASE_URL}${p}`, lastModified: now })),
    ...apps.map((a) => ({ url: `${WEB_BASE_URL}/app/${a.slug}`, lastModified: a.updatedAt })),
    ...videos.map((v) => ({ url: `${WEB_BASE_URL}/video/${v.slug}`, lastModified: v.updatedAt })),
    ...guides.map((g) => ({ url: `${WEB_BASE_URL}/guide/${g.slug}`, lastModified: g.updatedAt })),
    ...topics.map((t) => ({ url: `${WEB_BASE_URL}/topic/${t.slug}`, lastModified: t.updatedAt })),
    ...albums.map((a) => ({ url: `${WEB_BASE_URL}/album/${a.slug}`, lastModified: a.updatedAt })),
    ...tags.map((t) => ({ url: `${WEB_BASE_URL}/tag/${t.slug}` })),
    ...appCats.map((c) => ({ url: `${WEB_BASE_URL}/category/${c.slug}` })),
    ...videoCats.map((c) => ({ url: `${WEB_BASE_URL}/category/${c.slug}` })),
  ];

  return out;
}
```

> **`getPublishedApps`/`getPublishedVideos`** 默认无 limit,会拉全量。本地 9 + 20 行无压力;生产规模再考虑分 sitemap chunk(`MetadataRoute.Sitemap` 单文件最多 50000 条 URL,目前距上限远)。
>
> **rankings 不入 sitemap** — 6 个内置榜单挂在 `/rankings` 静态页底下,不暴露 `/ranking/:slug` 子路由(P2 没建)。

**Step 3: 改 `apps/web/app/layout.tsx`** — 扩展默认 metadata

```ts
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_WEB_BASE_URL ?? "http://localhost:3000"),
  title: { default: "Ghome — LGBTQ+ 数字生活总入口", template: "%s · Ghome" },
  description: "Ghome 收录全球合规上架的 LGBTQ+ 相关 App、视频内容、内容平台,提供专题、榜单、指南等导航服务。",
  keywords: ["LGBTQ", "男同", "App", "视频", "指南", "导航", "Ghome"],
  openGraph: {
    type: "website",
    siteName: "Ghome",
  },
  alternates: { canonical: "/" },
};
```

> `metadataBase` 必填用于解析相对 og:url。

**Step 4: 给 7 个 detail 页加 `generateMetadata`**

每个 detail 页 pattern 一致(以 `apps/web/app/app/[slug]/page.tsx` 为例):

```tsx
import type { Metadata } from "next";
import { getAppBySlug } from "@/lib/db";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const app = await getAppBySlug(slug);
  if (!app) return { title: "未找到" };
  const desc = (app.shortDesc ?? app.detail ?? "").slice(0, 160);
  return {
    title: app.name,
    description: desc || `Ghome 收录的 App:${app.name}`,
    openGraph: {
      title: app.name,
      description: desc,
      type: "website",
      url: `/app/${app.slug}`,
    },
    alternates: { canonical: `/app/${app.slug}` },
  };
}
```

镜像写法对其他 6 个 detail 页(用对应的 fetcher / 字段):
- video: `getVideoBySlug` → `title` / `shortDesc` / `detail`
- guide: `getGuideBySlug` → `title` / `summary`
- topic: `getCollectionBySlug(slug, "topic")` → `title` / `description`
- album: `getCollectionBySlug(slug, "album")` → `title` / `description`
- category: `getVideoCategoryBySlug` → `name` / `description`(若有);`description` 字段可能没有,用 `'${name} 分类下的内容'`
- tag: `getTagBySlug` → `label` / 描述用模板 `'#${label} 标签下的 App 与视频'`

**Step 5: 改 `apps/web/app/not-found.tsx`** — 加快捷链 + metadata

```tsx
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "404 — 页面未找到" };

export default function NotFound() {
  return (
    <div className="container" style={{ padding: "120px 24px", textAlign: "center" }}>
      <h1 style={{ fontSize: 80, margin: 0, color: "var(--primary)" }}>404</h1>
      <p style={{ color: "var(--text-2)", margin: "16px 0 24px" }}>
        页面未找到,可能已被移除或链接错误。
      </p>
      <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
        <Link href="/" className="btn btn-primary" style={{ padding: "12px 32px" }}>回到首页</Link>
        <Link href="/apps" className="btn btn-secondary" style={{ padding: "12px 32px" }}>看 App</Link>
        <Link href="/videos" className="btn btn-secondary" style={{ padding: "12px 32px" }}>看视频</Link>
        <Link href="/guides" className="btn btn-secondary" style={{ padding: "12px 32px" }}>看指南</Link>
      </div>
    </div>
  );
}
```

**Step 6: 验证 + 提交**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build

# 冒烟:
pnpm --filter @ghome/web dev
# http://localhost:3000/sitemap.xml — 输出 XML(Next.js 自动从 sitemap.ts 编)
# http://localhost:3000/robots.txt
# 打开 /app/broconnect → view-source 看 <title>BroConnect · Ghome</title> + meta description

git add "apps/web/app/sitemap.ts" "apps/web/app/robots.ts" \
        apps/web/app/not-found.tsx apps/web/app/layout.tsx \
        "apps/web/app/app/[slug]/page.tsx" "apps/web/app/video/[slug]/page.tsx" \
        "apps/web/app/guide/[slug]/page.tsx" "apps/web/app/topic/[slug]/page.tsx" \
        "apps/web/app/album/[slug]/page.tsx" "apps/web/app/category/[slug]/page.tsx" \
        "apps/web/app/tag/[slug]/page.tsx"
git commit -m "feat(web): per-detail generateMetadata + sitemap.ts + robots.ts + 404 quicklinks"
```

## Tricky Bits (T4)

1. **`metadataBase`**:Next.js 警告"metadataBase is not set"会在 build 期出现,产环境影响 og:url 解析。设了就消失
2. **`generateMetadata` async**:与 page 同的 params Promise 模式;`if (!app) return { title: "未找到" }` 兜底 — 实际后面 page 会 `notFound()`,但 metadata 也要不崩
3. **`description` 长度 ≤ 160**:`.slice(0, 160)`。开头 `(short_desc ?? detail ?? "")` 兜底
4. **sitemap revalidate**:`export const revalidate = 86400` — 每日重建一次,不需要 admin 写后强制 revalidate
5. **`getAllTags` 没 `updatedAt`**:tags 表没 updated_at 字段(P1 schema);sitemap 中 tag URL 不带 lastModified
6. **`/categories` 是 list 页,`/category/:slug` 是 detail**:按 P2 命名约定,确保 sitemap 用对
7. **canonical 用相对路径**:`alternates: { canonical: "/app/slug" }` — 与 `metadataBase` 拼接后变绝对 URL
8. **不引入 og-image 生成器**:留下次。本 P8 不写 `og:image`(MVP)
9. **`getAllTags` 与 `getAppCategories` 已存在?**:`apps/web/lib/db.ts` 已有 `getAllTags()` 与 `getAppCategories()` `getVideoCategories()`(P2),sitemap 直接复用
10. **`NEXT_PUBLIC_WEB_BASE_URL`**:可能没在 `.env.example`,本 task 加一行(就在 admin `.env.example` 同一时期)。生产部署需配真实域名
11. **`/api/cron/aggregate-clicks` 不进 sitemap**:cron 不是公开页;sitemap 也别索引到它
12. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 5 — End-to-end smoke + 集成测试 + tag p8-search-wrapup

**Files:**
- Create: `apps/web/tests/search.test.ts`(可选 — 若 web 已有 vitest 配置则加,否则跳过 web 单测,只跑 db 集成)

> 当前 `apps/web/package.json` 大概率**没有** vitest 配置(P0-P7 没建)。本 task 把搜索集成测试放在 `packages/db/tests/search.test.ts`,与 url-policy 测试放一起 — `searchAll` 虽然在 web,但其核心是 SQL,在 db 包测试更合适。**改写文件名为** `packages/db/tests/search.test.ts`,但因为 `searchAll` 不在 packages/db,**改测试目标**:直接复用 search 的 normalizeQuery + 直接写 raw SQL 测三表查询。

> **简化决定**:本 task 不增加 vitest 文件,把搜索冒烟放在端到端 dev 服 + curl 验证。集成测试留作 P9 housekeeping(若有)。

### 5 Steps(精简版)

**Step 1: 跑全套本地 CI 等价命令**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
pnpm install
pnpm --filter @ghome/db db:migrate:deploy
pnpm --filter @ghome/db db:seed
pnpm --filter @ghome/db typecheck
pnpm --filter @ghome/db test                   # 38 + 1 skipped(无新测试)
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin lint
pnpm --filter @ghome/admin build
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web lint
pnpm --filter @ghome/web build
```

全过才算过关。

**Step 2: 端到端 UI 冒烟**

```bash
pnpm --filter @ghome/web dev
```

- 首页 → 搜索框输入"健身" → 提交 → `/search?q=健身`:
  - 视频栏至少 1 条命中(seed 里 weekly-fitness-vlog 等)
  - App 栏可能有命中(若 detail 含"健身")
  - 指南栏可能有命中
  - 结果页底部展示 `tookMs`
- `/search?q=a`:显示"请至少输入 2 个字符"
- `/search`:显示"请输入关键词"
- `/search?q=不存在的字符串zzz`:显示"没有找到"
- `/sitemap.xml`:浏览器看 XML,App / 视频 / 指南 / 专题 / 专辑 / tag URL 都在
- `/robots.txt`:看 `User-agent: * Allow: /`
- 任一 detail 页 view-source:`<title>` 含原型名 + ` · Ghome`,`<meta name="description">` 不空
- `/不存在的路径`:渲染 404 页 + 4 个快捷链可点

**Step 3: API 冒烟**

```bash
curl -s 'http://localhost:3000/api/search?q=健身' | head -100
# {"apps":[...], "videos":[...], "guides":[...], "q":"健身", "tookMs":...}

curl -s 'http://localhost:3000/api/search?q=a'
# {"apps":[],"videos":[],"guides":[],"q":"a","tookMs":0}

curl -s 'http://localhost:3000/api/search'
# {"apps":[],"videos":[],"guides":[],"q":"","tookMs":0}
```

**Step 4: 提交(若上一 task 有遗漏)+ 打 tag**

```bash
git status     # 应 clean
git tag p8-search-wrapup
```

**Step 5: 更新 spec 标注 P8 完成 (可选 — 不在本 task 范围,留给 controller)**

## Tricky Bits (T5)

1. **冒烟需要 docker compose 起来**:与 P3-P7 同一 dev DB
2. **API 的 q 缺失**:`searchParams.get("q")` 返回 `null`;`normalizeQuery(null)` → `valid=false` → 空结果。**不**返回 400(用户友好)
3. **tag 用 "p8-search-wrapup"**:与 P0-P7 风格一致
4. **若 git tag 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Final 验收清单(P8 整体)

- [ ] `apps/web/lib/search.ts` `normalizeQuery` 处理 trim / 长度 / `% _ \` 转义
- [ ] `apps/web/lib/db.ts` `searchAll(q)` 三表并行 + 简单权重 + LIMIT 10/类
- [ ] `/api/search?q=:q` 返回 `{ apps, videos, guides, q, tookMs }`
- [ ] `/search?q=:q` SSR 三栏混合结果 + 空态 / 过短 / 零命中三档分明
- [ ] 首页 `.search-box` 是真 GET form 提交到 `/search`
- [ ] `Header.tsx` 加搜索快捷入口
- [ ] `app/sitemap.ts` 输出全部 published 内容 URL,每日 ISR
- [ ] `app/robots.ts` 输出 `Allow: /` + sitemap 链接
- [ ] 7 个 detail 页有 `generateMetadata` + canonical
- [ ] `layout.tsx` 有 `metadataBase` + 默认 description / og 元
- [ ] `not-found.tsx` 有 metadata + 4 个快捷链
- [ ] 搜"健身"在 `/search` 三栏混合命中
- [ ] CI 通过(无新测试,但 lint/typecheck/build 必须绿)
- [ ] tag `p8-search-wrapup` 落在 main HEAD

## 不做(P8 范围外,留给后续)

- 即时联想 / typeahead(client fetch /api/search on keypress + debounce)
- 搜索分页(目前各类 LIMIT 10 即截断)
- 搜索结果高亮 `<mark>`
- 二级筛选(按 category / tag / status)
- 搜索点击打点
- rate limit / IP 节流(部署后再加)
- og:image 生成 / Twitter Cards / JSON-LD
- canonical 自动检测
- i18n / hreflang
- sitemap chunk(单文件 > 50000 URLs 才需)
- ranking 子路由(`/ranking/:slug`)— 当前只暴露 `/rankings` 列表
- 搜索热词榜 / 历史记录 / 个人化

---

**P8 完成 ⇒ Ghome MVP 全部交付完成。**

下一步选项(由用户决定):
1. **写 RELEASE.md** 把 P0-P8 的功能、数据模型、本地启动、测试一站说明
2. **进入运维阶段**:配置真实域名、Vercel/Cloudflare/Render 部署、监控、备份策略
3. **P9 housekeeping**(可选):
   - 把 P7 留下的 minor 修(redirect edit 用 tag helpers + 二次 fresh-fetch)
   - 即时联想 + 搜索分页
   - 搜索集成测试(打 seed 后 SQL 断言)
   - GIN 索引 EXPLAIN ANALYZE 验证 plan
   - admin 增加 redirect 创建 / 删除 UI
   - admin 批量勾选 / 批量切 disabled
4. **P10+:接入 cron** — 把 `/api/cron/aggregate-clicks` 接到外部调度器(Vercel cron / GitHub Actions / k8s CronJob)
