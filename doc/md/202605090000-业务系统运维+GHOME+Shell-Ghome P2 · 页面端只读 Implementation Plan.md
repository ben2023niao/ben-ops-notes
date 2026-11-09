---
id: "doc-29b831214138"
title: "Ghome P2 · 页面端只读 Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/operator/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p2-frontend-readonly.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p2-frontend-readonly.md"
sourceSha256: "e0d141606d9a3d047f5bd645a621f18d06ae8bb3e4f2860475696d94a360dd86"
sourceSystem: "project-doc"
---

# Ghome P2 · 页面端只读 Implementation Plan

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605090000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20P2%20%C2%B7%20%E9%A1%B5%E9%9D%A2%E7%AB%AF%E5%8F%AA%E8%AF%BB%20Implementation%20Plan.md)

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把原型 `docs/ghome.html` 的 **16 条原型路由**(不含 `/albums`)用 Next.js 15 App Router + SSG/ISR 重渲,数据全部来自 P1 落库的 14 张表 + 3 个 fixture(FEATURED_WEB / CREATORS / SAMPLE_REVIEWS)。视觉对齐原型(把原型 `<style>` 块整体抄进 `globals.css`,不重写)。`/albums` 与 `/album/:slug` **本期返回 404 占位**,P6 才落地。

**Architecture:**
- `apps/web` 引入 `@ghome/db` workspace 依赖,P1 的 PrismaClient + 14 model 类型 + url-policy 全部可用
- 数据访问统一收口在 `apps/web/lib/db.ts`(查询辅助函数),不在页面组件里直写 Prisma 查询
- ISR:列表页 60s 重生,详情页 300s,静态页(about/contact/terms)纯 SSG
- Fixtures(FEATURED_WEB / CREATORS / SAMPLE_REVIEWS)单独放 `apps/web/fixtures/*.ts`,代码内常量
- Markdown 用 `react-markdown`(P1 没装,本期引入)
- 样式策略:原型的 `<style>` 块(`docs/ghome.html` :8-432)整体抄进 `apps/web/app/globals.css`,加少量 P2 新增类(如 markdown body)。**不上 Tailwind**(留 P3+)

**Tech Stack:**
- Next.js 15 App Router(已 P0 装)
- React 19(已 P0 装)
- `@ghome/db`(P1 已发)
- `react-markdown ^9.0.0`(P2 新增,渲染 guide bodies)
- `remark-gfm ^4.0.0`(GFM 表格、checkbox 等;guide markdown 可能需要)
- 所有 SVG icons 从原型 `<defs>` 提取成 React 组件

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §2.1(路由表)、§4.1(SSG/ISR)、§5 P2。

**前置假设:** P1 已完成,`p1-data-model` 标签存在;`pnpm --filter @ghome/db db:seed` 跑过,DB 里有 9 apps + 20 videos + 5 guides + 6 topics + 6 rankings + 63 tags;`apps/web` 还是 P0 占位空白页。

---

## File Structure(P2 末态)

```
apps/web/
├─ app/
│  ├─ globals.css                        # 整体抄自原型 :8-432 + P2 markdown 样式
│  ├─ layout.tsx                         # 已存在(P0),T4 重写
│  ├─ not-found.tsx                      # 自定义 404(T4)
│  ├─ page.tsx                           # 首页(T6)
│  ├─ apps/
│  │  └─ page.tsx                        # /apps 列表 + 筛选(T7)
│  ├─ app/
│  │  └─ [slug]/page.tsx                 # /app/:slug 详情(T7)
│  ├─ videos/
│  │  └─ page.tsx                        # /videos 列表 + featured(T8)
│  ├─ video/
│  │  └─ [slug]/page.tsx                 # /video/:slug 详情(T8)
│  ├─ categories/
│  │  └─ page.tsx                        # /categories(T9)
│  ├─ category/
│  │  └─ [slug]/page.tsx                 # /category/:slug 仅 video kind(T9)
│  ├─ tag/
│  │  └─ [slug]/page.tsx                 # /tag/:slug(T9)
│  ├─ topics/
│  │  └─ page.tsx                        # /topics 列表(T10)
│  ├─ topic/
│  │  └─ [slug]/page.tsx                 # /topic/:slug(T10)
│  ├─ rankings/
│  │  └─ page.tsx                        # /rankings 6 区块(T10)
│  ├─ albums/
│  │  └─ page.tsx                        # P2 占位 → notFound()(T10)
│  ├─ album/
│  │  └─ [slug]/page.tsx                 # P2 占位 → notFound()(T10)
│  ├─ guides/
│  │  └─ page.tsx                        # /guides 列表(T11)
│  ├─ guide/
│  │  └─ [slug]/page.tsx                 # /guide/:slug 含 markdown(T11)
│  ├─ about/
│  │  └─ page.tsx                        # 静态 markdown 文案(T12)
│  ├─ contact/
│  │  └─ page.tsx                        # 静态(T12)
│  └─ terms/
│      └─ page.tsx                       # 静态(T12)
├─ components/
│  ├─ Header.tsx                         # 顶栏 + nav(T4)
│  ├─ Footer.tsx                         # 页脚(T4)
│  ├─ AppCard.tsx                        # App 卡片(T5)
│  ├─ VideoCard.tsx                      # 视频卡片(T5)
│  ├─ GuideCard.tsx                      # 指南卡片(T5)
│  ├─ TopicCard.tsx                      # 专题卡片(T5)
│  ├─ RankingCard.tsx                    # 榜单卡片(T5)
│  ├─ Crumb.tsx                          # 面包屑(T5)
│  ├─ TagPill.tsx                        # tag 小标签(T5)
│  ├─ FeaturedHero.tsx                   # FEATURED_WEB hero 区块(T6)
│  └─ MarkdownBody.tsx                   # react-markdown 包装(T11)
├─ lib/
│  ├─ db.ts                              # Prisma 查询辅助(T2)
│  ├─ icons.tsx                          # SVG sprite + <Icon> 组件(T2)
│  ├─ gradients.ts                       # GRADS 映射(T2)
│  └─ format.ts                          # 数字 / 日期等格式化(T2)
├─ fixtures/
│  ├─ featured-web.ts                    # FEATURED_WEB(T3)
│  ├─ creators.ts                        # CREATORS(T3)
│  └─ sample-reviews.ts                  # SAMPLE_REVIEWS(T3)
├─ .env                                  # DATABASE_URL,本地 dev 用(T1)
├─ next.config.mjs                       # 已存在(P0)
├─ next-env.d.ts                         # 自动生成,gitignore
├─ package.json                          # T1 加 @ghome/db / react-markdown / remark-gfm
└─ tsconfig.json                         # P0 已配置,T1 不动
```

新增文件总数:**~30**。`@ghome/admin` 在 P2 期间不动(P4 才接入)。

---

## Conventions(整个 P2 共享)

- 所有 page 都是 **server components**(默认),数据查询直接 await Prisma
- ISR:
  - 列表页 + 首页:`export const revalidate = 60`
  - 详情页:`export const revalidate = 300`
  - 静态页(about/contact/terms):**不**写 revalidate(全 SSG)
- 路由 `not-found.tsx` 走 Next.js 标准 `notFound()` API
- 外链按钮在 P2 暂用 `<a>` 渲染(href 是 `redirect.targetUrl`,但 `redirect.disabled=true` 时按钮置灰且不渲染 href);**不实现 `/r/:id` 中转**(P3)
- 提交风格:Conventional Commits,每 task 末尾 commit
- 不引 i18n、不引 auth、不接搜索(都在后续 P)

---

## Task 1 — `apps/web` 接入 `@ghome/db` + 引入 markdown 依赖 + 复制原型 CSS

**Files:**
- Modify: `apps/web/package.json`
- Create: `apps/web/.env`(本地 DATABASE_URL,gitignored)
- Create: `apps/web/.gitignore`(已存在 root level,加 .env)
- Modify: `apps/web/app/globals.css`(整体替换为原型 `<style>` 块)
- Modify: `apps/web/app/page.tsx`(临时改成"P2 接入中"占位,T6 才正式实现首页)

- [ ] **Step 1: 修改 `apps/web/package.json`,加 workspace 依赖与 markdown 库**

在 `dependencies` 里加:
```json
"@ghome/db": "workspace:*",
"react-markdown": "^9.0.0",
"remark-gfm": "^4.0.0"
```

完整 package.json 变化:
- `dependencies` 加 3 条
- 其它字段保持

- [ ] **Step 2: 创建 `apps/web/.env`(local dev only)**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
cat > apps/web/.env <<'EOF'
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome
EOF
```

- [ ] **Step 3: 创建 `apps/web/.gitignore`(已存在 root,这里只 ignore env)**

```
.env
.env.local
.env.*.local
```

- [ ] **Step 4: 复制原型 CSS 到 `apps/web/app/globals.css`**

读 `docs/ghome.html` 第 8-432 行(`<style>` 块内容),整体覆盖到 `apps/web/app/globals.css`。**不要改任何选择器、颜色、间距**,这是 P2 的"视觉冻结"原则。

```bash
# 推荐做法:用 Read tool 读 docs/ghome.html offset=8 limit=425(取 8-432 行),
# 然后 Write 到 apps/web/app/globals.css。
```

末尾追加 P2 自己的样式块(`MarkdownBody` 用):

```css

/* P2 additions — markdown body */
.md-body { color: var(--text); line-height: 1.8; font-size: 15.5px; }
.md-body h2 { font-size: 20px; font-weight: 700; margin: 28px 0 12px; }
.md-body h3 { font-size: 17px; font-weight: 600; margin: 20px 0 10px; }
.md-body p { margin: 0 0 14px; color: var(--text-2); }
.md-body ul { padding-left: 22px; margin: 0 0 14px; color: var(--text-2); }
.md-body li { margin: 4px 0; }
.md-body a { color: var(--primary); text-decoration: underline; }
.md-body code { background: var(--bg); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
```

- [ ] **Step 5: 临时改 `apps/web/app/page.tsx`(P0 占位 → P2 接入中占位)**

```tsx
export default function HomePage() {
  return (
    <main style={{ padding: "48px 24px", fontFamily: "system-ui, sans-serif" }}>
      <h1>Ghome · web</h1>
      <p>P2 · 页面端接入 DB 中。当前任务:T1 · 接入 @ghome/db。</p>
    </main>
  );
}
```

- [ ] **Step 6: 安装依赖**

```bash
pnpm install
```

Expected: 拉下 `react-markdown`、`remark-gfm`、`@ghome/db`(workspace link,无网络下载)。

- [ ] **Step 7: 验证 build / dev**

```bash
docker compose up -d  # postgres 必须起,否则后续 task SSG 会断
sleep 5
pnpm --filter @ghome/db db:migrate:deploy   # 确保 schema 是最新
pnpm --filter @ghome/db db:seed              # 确保数据已 seed
pnpm --filter @ghome/web build
```

Expected: build 成功(P2 占位首页是纯静态)。

- [ ] **Step 8: 提交**

```bash
git add apps/web/package.json apps/web/.gitignore apps/web/app/globals.css apps/web/app/page.tsx pnpm-lock.yaml
git commit -m "feat(web): wire @ghome/db dependency and import prototype CSS verbatim"
```

> `apps/web/.env` **不**入库(已 gitignored)。

---

## Task 2 — `lib/`:db queries + icons + gradients + format

**Files:**
- Create: `apps/web/lib/db.ts`
- Create: `apps/web/lib/icons.tsx`
- Create: `apps/web/lib/gradients.ts`
- Create: `apps/web/lib/format.ts`

- [ ] **Step 1: 写 `apps/web/lib/db.ts`(查询辅助)**

```ts
import { prisma, type App, type Video, type Guide, type Category, type Tag, type Collection, type CollectionItem } from "@ghome/db";

/* ============== 通用过滤:仅返回已发布、未删除 ============== */
const PUBLISHED = { status: "published" as const, deletedAt: null };

/* ============== Apps ============== */

export async function getPublishedApps(opts?: { categorySlug?: string; limit?: number }) {
  return prisma.app.findMany({
    where: {
      ...PUBLISHED,
      ...(opts?.categorySlug ? { category: { slug: opts.categorySlug, kind: "app" } } : {}),
    },
    include: {
      category: true,
      redirect: true,
      tags: { include: { tag: true } },
    },
    take: opts?.limit,
    orderBy: { createdAt: "desc" },
  });
}

export async function getAppBySlug(slug: string) {
  return prisma.app.findFirst({
    where: { ...PUBLISHED, slug },
    include: {
      category: true,
      redirect: true,
      tags: { include: { tag: true } },
    },
  });
}

export async function getAppCategories() {
  return prisma.category.findMany({
    where: { kind: "app" },
    orderBy: { sortOrder: "asc" },
  });
}

/* ============== Videos ============== */

export async function getPublishedVideos(opts?: { categorySlug?: string; tagSlug?: string; limit?: number }) {
  return prisma.video.findMany({
    where: {
      ...PUBLISHED,
      ...(opts?.categorySlug ? { category: { slug: opts.categorySlug, kind: "video" } } : {}),
      ...(opts?.tagSlug ? { tags: { some: { tag: { slug: opts.tagSlug } } } } : {}),
    },
    include: {
      category: true,
      redirect: true,
      tags: { include: { tag: true } },
    },
    take: opts?.limit,
    orderBy: { publishedDate: "desc" },
  });
}

export async function getVideoBySlug(slug: string) {
  return prisma.video.findFirst({
    where: { ...PUBLISHED, slug },
    include: {
      category: true,
      redirect: true,
      tags: { include: { tag: true } },
    },
  });
}

export async function getVideoCategories() {
  return prisma.category.findMany({
    where: { kind: "video" },
    orderBy: { sortOrder: "asc" },
  });
}

/* ============== Guides ============== */

export async function getPublishedGuides() {
  return prisma.guide.findMany({
    where: PUBLISHED,
    orderBy: { publishedDate: "desc" },
  });
}

export async function getGuideBySlug(slug: string) {
  return prisma.guide.findFirst({ where: { ...PUBLISHED, slug } });
}

/* ============== Categories(generic) ============== */

export async function getVideoCategoryBySlug(slug: string) {
  return prisma.category.findUnique({ where: { kind_slug: { kind: "video", slug } } });
}

/* ============== Tags ============== */

export async function getTagBySlug(slug: string) {
  return prisma.tag.findUnique({ where: { slug } });
}

export async function getAllTags() {
  return prisma.tag.findMany({ orderBy: { label: "asc" } });
}

/* ============== Collections(topic / album / ranking)============== */

export async function getCollectionsByKind(kind: "topic" | "album" | "ranking") {
  return prisma.collection.findMany({
    where: { ...PUBLISHED, kind },
    orderBy: { sortOrder: "asc" },
  });
}

export async function getCollectionBySlug(slug: string, kind?: "topic" | "album" | "ranking") {
  return prisma.collection.findFirst({
    where: {
      ...PUBLISHED,
      slug,
      ...(kind ? { kind } : {}),
    },
    include: {
      items: {
        orderBy: { position: "asc" },
        include: {
          app: { include: { category: true, redirect: true } },
          video: { include: { category: true, redirect: true } },
          tag: true,
          redirect: true,
        },
      },
    },
  });
}

/* ============== Type helpers ============== */
// 从查询返回类型推导,组件 prop 用
export type AppWithRels = NonNullable<Awaited<ReturnType<typeof getAppBySlug>>>;
export type VideoWithRels = NonNullable<Awaited<ReturnType<typeof getVideoBySlug>>>;
export type CollectionWithItems = NonNullable<Awaited<ReturnType<typeof getCollectionBySlug>>>;
export type CollectionItemWithRefs = CollectionWithItems["items"][number];
```

- [ ] **Step 2: 写 `apps/web/lib/icons.tsx`(SVG sprite + <Icon> 组件)**

读原型 `docs/ghome.html` 第 ~440-480 行(`<defs>` 块,含 `<linearGradient>` 与 `<symbol>`)。把 sprite 整体复制为 React 组件:

```tsx
import type { CSSProperties } from "react";

/**
 * SVG sprite — 来自原型 docs/ghome.html :440-480 的 <defs> 块。
 * 使用方式:在 layout 顶部渲染一次 <SvgSprite />,然后所有页面用 <Icon name="i-chat" grad="g-brand" />。
 */

export function SvgSprite() {
  return (
    <svg width={0} height={0} style={{ position: "absolute" }} aria-hidden>
      <defs>
        {/* 从原型逐字 paste linearGradient + symbol 定义 */}
        {/* g-brand / g-fire / g-sky / g-leaf / g-rose / g-grape / g-gold / g-mute / g-mint / g-pink */}
        {/* i-chat / i-heart / i-dumbbell / i-map / i-mic / i-news / i-calendar / i-shield / i-palette */}
        {/* i-search / i-home / i-fire / i-sparkle / i-users / i-check / i-arrow-right / etc. */}
        {/* 详见原型 :440-480 */}
      </defs>
    </svg>
  );
}

export function Icon({
  name,
  grad = "g-brand",
  size = 22,
  style,
}: {
  name: string;
  grad?: string;
  size?: number;
  style?: CSSProperties;
}) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={style}>
      <use href={`#${name}`} fill={`url(#${grad})`} />
    </svg>
  );
}

export function IconWhite({ name, size = 24 }: { name: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <use href={`#${name}`} fill="#fff" />
    </svg>
  );
}
```

> 实现细节:Step 2 的占位注释(`{/* ... */}`)需要 implementer 根据原型行 :440-480 的实际 SVG 内容**完整 paste**。这块 ~40 行 SVG 不在 plan 里嵌入,以保持 plan 长度可控。implementer 必须读原型并复制。

- [ ] **Step 3: 写 `apps/web/lib/gradients.ts`(GRADS 映射)**

```ts
/**
 * 与原型 docs/ghome.html :663-668 GRADS 一致。
 * 用于 CSS gradient 字符串(如 hero 背景)。
 */
export const GRADS: Record<string, [string, string]> = {
  "g-brand": ["#7C7CFF", "#5B5BE8"],
  "g-fire":  ["#FF8A65", "#F5576C"],
  "g-sky":   ["#4FACFE", "#00D4FE"],
  "g-leaf":  ["#43E97B", "#38B89C"],
  "g-rose":  ["#FA709A", "#FE9568"],
  "g-grape": ["#A78BFA", "#7C3AED"],
  "g-gold":  ["#FCD34D", "#F59E0B"],
  "g-mute":  ["#9CA3AF", "#6B7280"],
  "g-mint":  ["#5EEAD4", "#14B8A6"],
  "g-pink":  ["#F472B6", "#DB2777"],
};

export function gradStops(name: string): [string, string] {
  return GRADS[name] ?? GRADS["g-brand"];
}

export function gradCss(name: string, angle = 135): string {
  const [a, b] = gradStops(name);
  return `linear-gradient(${angle}deg,${a},${b})`;
}

/**
 * 视频 cover 的 gradient(原型 docs/ghome.html :566-577 COVERS)。
 * coverKey 来自 videos.coverKey,例如 'city' / 'fitness' / 'travel'。
 */
export const COVERS: Record<string, string> = {
  city:     "linear-gradient(135deg,#667eea 0%,#764ba2 100%)",
  fitness:  "linear-gradient(135deg,#f093fb 0%,#f5576c 100%)",
  travel:   "linear-gradient(135deg,#4facfe 0%,#00f2fe 100%)",
  interview:"linear-gradient(135deg,#43e97b 0%,#38f9d7 100%)",
  life:     "linear-gradient(135deg,#fa709a 0%,#fee140 100%)",
  vlog:     "linear-gradient(135deg,#a8edea 0%,#fed6e3 100%)",
  campus:   "linear-gradient(135deg,#d299c2 0%,#fef9d7 100%)",
  food:     "linear-gradient(135deg,#ffecd2 0%,#fcb69f 100%)",
  culture:  "linear-gradient(135deg,#84fab0 0%,#8fd3f4 100%)",
  fashion:  "linear-gradient(135deg,#fbc2eb 0%,#a6c1ee 100%)",
};

export function coverCss(coverKey: string): string {
  return COVERS[coverKey] ?? COVERS.life;
}

/** 视频图片占位:与原型 :671 vimg 一致 */
export function videoImg(slug: string, w = 800, h = 500): string {
  return `https://picsum.photos/seed/ghome${slug}/${w}/${h}`;
}
```

- [ ] **Step 4: 写 `apps/web/lib/format.ts`**

```ts
/** ISO date 'YYYY-MM-DD' → '2026-04-28' 显示用 */
export function formatPublishDate(d: Date): string {
  // 直接用 ISO 切片;不引 date-fns
  return d.toISOString().slice(0, 10);
}

/** 阅读时长 '8 分钟' 显示 */
export function formatReadMinutes(min: number): string {
  return `${min} 分钟`;
}
```

- [ ] **Step 5: 验证 typecheck**

```bash
pnpm --filter @ghome/web typecheck
```

Expected: 通过(虽然 lib 还没被 page 引用,但作为 module typecheck 必须过)。

- [ ] **Step 6: 提交**

```bash
git add apps/web/lib/
git commit -m "feat(web): add db query helpers, icon registry, gradients, and format utils"
```

---

## Task 3 — Fixtures:FEATURED_WEB / CREATORS / SAMPLE_REVIEWS

**Files:**
- Create: `apps/web/fixtures/featured-web.ts`
- Create: `apps/web/fixtures/creators.ts`
- Create: `apps/web/fixtures/sample-reviews.ts`

> 来源:原型 `docs/ghome.html` :515(FEATURED_WEB)、:548-552(SAMPLE_REVIEWS)、:554-559(CREATORS)。这三组数据 P2 不入库,保持 fixture(spec §4.5)。

- [ ] **Step 1: 写 `apps/web/fixtures/featured-web.ts`**

```ts
export const FEATURED_WEB = {
  id: "g-video-hub",
  name: "G-Video Hub",
  type: "WEB端视频",
  desc: "聚合全球优质的男同高清原创短片与长视频,支持无广告极速播放,打造纯净的沉浸式观影体验。",
  tags: ["超清画质", "原创内容", "无广告", "创作者社区"],
  audience: "喜欢沉浸式观影、追求高品质视频内容的视觉控",
  features: "智能推荐 · 弹幕互动 · 多端同步",
  stats: { videos: "3,200+", creators: "520+", plays: "2,100万+", rating: "9.2" },
  about: "G-Video Hub 是 Ghome 全力推荐的男同生活方式视频站,收录内容均为合规的 Vlog、健身、旅行、情感访谈、生活记录等题材。所有内容由认证创作者上传,经编辑团队审核后上线,不含任何成人或违规内容。",
} as const;

export type FeaturedWeb = typeof FEATURED_WEB;
```

- [ ] **Step 2: 写 `apps/web/fixtures/creators.ts`**

```ts
export interface Creator {
  id: string;
  name: string;
  avatar: string;
  grad: string;
  followers: string;
  videos: number;
  bio: string;
}

export const CREATORS: Creator[] = [
  { id: "c01", name: "小阳的城市笔记",  avatar: "阳", grad: "g-brand", followers: "12.5万", videos: 48, bio: "记录都市生活的细节与温度,主要拍 Vlog 和访谈类内容。" },
  { id: "c02", name: "Justin Trains",   avatar: "J",  grad: "g-fire",  followers: "28.3万", videos: 62, bio: "健身教练 / 训练计划与饮食方案分享,认证创作者。" },
  { id: "c03", name: "地球漫步 Geo",    avatar: "地", grad: "g-sky",   followers: "15.8万", videos: 35, bio: "走过 30+ 国家的旅行 Vlogger,分享同志友好城市指南。" },
  { id: "c04", name: "晚安咖啡",        avatar: "咖", grad: "g-rose",  followers: "8.7万",  videos: 90, bio: "治愈系慢生活内容创作者,每周更新两条 Vlog。" },
];

/** 从原型 videoCreator 函数:按 video.cat 反查 creator */
const VIDEO_CAT_TO_CREATOR: Record<string, string> = {
  fitness: "c02",
  travel: "c03",
  life: "c04",
  vlog: "c01",
  interview: "c04",
  campus: "c01",
};

export function creatorForVideoCategorySlug(catSlug: string): Creator {
  const id = VIDEO_CAT_TO_CREATOR[catSlug] ?? "c01";
  return CREATORS.find((c) => c.id === id) ?? CREATORS[0]!;
}
```

- [ ] **Step 3: 写 `apps/web/fixtures/sample-reviews.ts`**

```ts
export interface SampleReview {
  name: string;
  avatar: string;
  grad: string;
  stars: number;
  date: string;
  body: string;
}

export const SAMPLE_REVIEWS: SampleReview[] = [
  { name: "Alex",  avatar: "A", grad: "g-brand", stars: 5, date: "2026-04-22", body: "功能很完整,社区氛围友好,已经用了三个月,认识了几个不错的朋友,强烈推荐给同样想拓展生活圈的人。" },
  { name: "Marco", avatar: "M", grad: "g-rose",  stars: 4, date: "2026-04-15", body: "整体体验不错,UI 干净利落。隐私保护做得很到位,唯一希望能再增加一些深度兴趣社群功能。" },
  { name: "Jay",   avatar: "J", grad: "g-leaf",  stars: 5, date: "2026-04-08", body: "用过好几款类似的产品,这个的认证机制最让人放心,客服响应也很及时,值得长期使用。" },
];
```

- [ ] **Step 4: 验证 typecheck**

```bash
pnpm --filter @ghome/web typecheck
```

- [ ] **Step 5: 提交**

```bash
git add apps/web/fixtures/
git commit -m "feat(web): add fixtures for featured-web, creators, sample-reviews (P2 placeholder)"
```

---

## Task 4 — Layout + Header + Footer + Custom 404

**Files:**
- Modify: `apps/web/app/layout.tsx`
- Create: `apps/web/components/Header.tsx`
- Create: `apps/web/components/Footer.tsx`
- Create: `apps/web/components/Crumb.tsx`
- Create: `apps/web/app/not-found.tsx`

参考原型 `docs/ghome.html`:
- Header: :486-494(`.header`、`.header-inner`、`.logo`、`.nav`、`.icon-btn`)
- Footer: :498-510(`.footer`、`.footer-grid`)
- 导航数据:原型 NAV array :638-647

- [ ] **Step 1: 写 `apps/web/components/Header.tsx`**

```tsx
import Link from "next/link";
import { Icon } from "@/lib/icons";

const NAV = [
  { href: "/",         label: "首页" },
  { href: "/apps",     label: "男同 App" },
  { href: "/videos",   label: "男同视频" },
  { href: "/categories", label: "分类导航" },
  { href: "/rankings", label: "排行榜" },
  { href: "/topics",   label: "专题" },
  { href: "/guides",   label: "指南" },
  { href: "/about",    label: "关于我们" },
];

export function Header({ activePath }: { activePath: string }) {
  return (
    <header className="header">
      <div className="container header-inner">
        <Link href="/" className="logo">
          <span className="logo-icon">{/* Ghome 字母 logo */}G</span>
          <span>Ghome</span>
        </Link>
        <nav className="nav">
          {NAV.map((n) => {
            const active = n.href === "/" ? activePath === "/" : activePath.startsWith(n.href);
            return (
              <Link key={n.href} href={n.href} className={active ? "active" : ""}>
                {n.label}
              </Link>
            );
          })}
        </nav>
        <div className="header-right">
          <Link href="/about" className="icon-btn" aria-label="关于">
            <Icon name="i-info" size={20} />
          </Link>
        </div>
      </div>
    </header>
  );
}
```

> 注:`icon-btn` 的 hover 效果与 `.nav .active::after` 下划线效果都来自原型 CSS,已在 globals.css 里。

- [ ] **Step 2: 写 `apps/web/components/Footer.tsx`**

读原型 :498-510 的 `.footer` 区段,构造对应 JSX。Footer 包含:
- 4 列(品牌 / 产品 / 内容 / 关于),每列若干 link
- 底部版权行 + 「免责声明」link

按原型实际链接结构 paste:

```tsx
import Link from "next/link";

export function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <div className="footer-brand">Ghome</div>
            <p className="footer-desc">LGBTQ+ 数字生活总入口</p>
          </div>
          <div>
            <h5>产品</h5>
            <ul>
              <li><Link href="/apps">男同 App</Link></li>
              <li><Link href="/videos">男同视频</Link></li>
              <li><Link href="/categories">分类导航</Link></li>
              <li><Link href="/rankings">排行榜</Link></li>
            </ul>
          </div>
          <div>
            <h5>内容</h5>
            <ul>
              <li><Link href="/topics">专题合集</Link></li>
              <li><Link href="/guides">使用指南</Link></li>
            </ul>
          </div>
          <div>
            <h5>关于</h5>
            <ul>
              <li><Link href="/about">关于我们</Link></li>
              <li><Link href="/contact">联系合作</Link></li>
              <li><Link href="/terms">免责声明</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          © {new Date().getFullYear()} Ghome · LGBTQ+ 数字生活总入口
        </div>
      </div>
    </footer>
  );
}
```

> 如果原型 Footer 与上述结构不完全一致,**以原型为准**(读 :498-510 校对)。

- [ ] **Step 3: 写 `apps/web/components/Crumb.tsx`(面包屑)**

```tsx
import Link from "next/link";
import type { ReactNode } from "react";

export function Crumb({ items }: { items: Array<{ href?: string; label: ReactNode }> }) {
  return (
    <div className="container">
      <div className="crumb">
        {items.map((it, i) => (
          <span key={i}>
            {i > 0 && <span className="sep">/</span>}
            {it.href ? <Link href={it.href}>{it.label}</Link> : <span>{it.label}</span>}
          </span>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: 重写 `apps/web/app/layout.tsx`(加 SvgSprite + Header + Footer)**

```tsx
import type { Mevendor_ata } from "next";
import { headers } from "next/headers";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { SvgSprite } from "@/lib/icons";

export const mevendor_ata: Mevendor_ata = {
  title: { default: "Ghome", template: "%s · Ghome" },
  description: "LGBTQ+ 数字生活总入口 — App / 视频 / 专题 / 指南",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const h = await headers();
  const pathname = h.get("x-pathname") ?? "/";  // see middleware note below
  return (
    <html lang="zh-CN">
      <body>
        <SvgSprite />
        <Header activePath={pathname} />
        {children}
        <Footer />
      </body>
    </html>
  );
}
```

> **注**:Next.js 15 不直接暴露当前 pathname 给 server layout。两种解法:
> - **A(简单)**:不做 active 高亮,Header `activePath=""` 始终为空,nav 不高亮 active state(可接受)。
> - **B(精确)**:写一个 `apps/web/middleware.ts`,把 `x-pathname` header 注入。
>
> **P2 决定 A**:Header 的 `active` 高亮**不依赖 server pathname**,改成在 client 用 `usePathname` hook 推断:

修订 Header.tsx 顶部加 `"use client"`,并用 `usePathname`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/lib/icons";

const NAV = [/* ...同上... */];

export function Header() {
  const pathname = usePathname();
  return (
    <header className="header">
      {/* ... 同上,但用 pathname 判断 active */}
    </header>
  );
}
```

并把 layout 里 `<Header activePath={pathname} />` 改回 `<Header />`,删掉 `headers()` 调用。

> 这是 P2 决定:Header 是 client component,因为需要 `usePathname` 跟踪 active nav。其它 page/section 都是 server。

- [ ] **Step 5: 写 `apps/web/app/not-found.tsx`**

```tsx
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container" style={{ padding: "120px 24px", textAlign: "center" }}>
      <h1 style={{ fontSize: 80, margin: 0, color: "var(--primary)" }}>404</h1>
      <p style={{ color: "var(--text-2)", margin: "16px 0 32px" }}>
        页面未找到,可能已被移除或链接错误。
      </p>
      <Link href="/" className="btn btn-primary" style={{ display: "inline-flex", padding: "12px 40px" }}>
        回到首页
      </Link>
    </div>
  );
}
```

- [ ] **Step 6: 验证 build**

```bash
pnpm --filter @ghome/web build
```

Expected: 通过。/ (首页占位)路由 + /not-found 静态生成。

- [ ] **Step 7: 提交**

```bash
git add apps/web/app/layout.tsx apps/web/app/not-found.tsx apps/web/components/Header.tsx apps/web/components/Footer.tsx apps/web/components/Crumb.tsx
git commit -m "feat(web): layout with header/footer + custom 404"
```

---

## Task 5 — 卡片组件:AppCard / VideoCard / GuideCard / TopicCard / RankingCard / TagPill

**Files:**
- Create: `apps/web/components/AppCard.tsx`
- Create: `apps/web/components/VideoCard.tsx`
- Create: `apps/web/components/GuideCard.tsx`
- Create: `apps/web/components/TopicCard.tsx`
- Create: `apps/web/components/RankingCard.tsx`
- Create: `apps/web/components/TagPill.tsx`

参考原型(`docs/ghome.html`):
- AppCard:`.app-card` 与 `.atr` 结构,渲染于 :695-715(`renderAppCard`)
- VideoCard:`.video-card` 与 `.feat-video` 结构,:679-693(`renderVCard`)
- GuideCard:guides 列表 :1568+ 的卡片
- TopicCard:`.topic-card` :876-878 区
- RankingCard:`.rank-card` :1430-1480
- TagPill:`.pill` 全局样式

- [ ] **Step 1: 写 `AppCard.tsx`**

```tsx
import Link from "next/link";
import { Icon } from "@/lib/icons";
import type { AppWithRels } from "@/lib/db";

export function AppCard({ app }: { app: AppWithRels }) {
  return (
    <Link href={`/app/${app.slug}`} className="app-card">
      <div className="app-card-head">
        <div className="featured-icon" style={{ background: `linear-gradient(135deg, ...)` }}>
          <Icon name={app.iconKey} grad="g-mute" size={28} />  {/* 实际用 grad={app.gradientKey} */}
        </div>
        <div className="atr">
          <h4>{app.name}</h4>
          <span className="pill">APP</span>
        </div>
      </div>
      <p className="app-card-desc">{app.shortDesc}</p>
      <div className="app-card-tags">
        {app.tags.map(({ tag }) => (
          <span key={tag.id} className="pill">{tag.label}</span>
        ))}
      </div>
      <div className="app-card-meta">
        <span>评分 {app.rating}</span>
        <span>·</span>
        <span>{app.usersLabel}</span>
      </div>
    </Link>
  );
}
```

> 实际渲染细节按原型 :695-715。CSS 类名与原型保持一致;**不**自创新类。

- [ ] **Step 2: 写 `VideoCard.tsx`**

```tsx
import Link from "next/link";
import { coverCss } from "@/lib/gradients";
import type { VideoWithRels } from "@/lib/db";

export function VideoCard({ video }: { video: VideoWithRels }) {
  return (
    <Link href={`/video/${video.slug}`} className="feat-video">
      <div className="feat-video-cover" style={{ background: coverCss(video.coverKey), aspectRatio: "16/10" }}>
        <span className="fc">{video.category.label}</span>
        <span className="ft">{video.title}</span>
      </div>
      <div className="feat-video-meta">
        <span>{video.duration}</span>
        <span>·</span>
        <span>{video.viewsLabel}</span>
      </div>
    </Link>
  );
}
```

- [ ] **Step 3: 写 `GuideCard.tsx`** — 参考原型 guides 列表卡片(:1568+):

```tsx
import Link from "next/link";
import { Icon } from "@/lib/icons";
import type { Guide } from "@ghome/db";
import { gradCss } from "@/lib/gradients";
import { formatPublishDate, formatReadMinutes } from "@/lib/format";

export function GuideCard({ guide }: { guide: Guide }) {
  return (
    <Link href={`/guide/${guide.slug}`} className="guide-card">
      <div className="guide-card-head" style={{ background: gradCss(guide.gradientKey) }}>
        <Icon name={guide.iconKey} grad="g-mute" size={36} />
      </div>
      <div className="guide-card-body">
        <span className="pill">{guide.categoryLabel}</span>
        <h4>{guide.title}</h4>
        <p>{guide.summary}</p>
        <div className="guide-card-meta">
          <span>{formatPublishDate(guide.publishedDate)}</span>
          <span>·</span>
          <span>{formatReadMinutes(guide.readMinutes)}</span>
          <span>·</span>
          <span>{guide.viewsLabel}</span>
          {guide.isHot && <span className="pill pill-hot">HOT</span>}
        </div>
      </div>
    </Link>
  );
}
```

- [ ] **Step 4: 写 `TopicCard.tsx`** — 参考原型 :876-878:

```tsx
import Link from "next/link";
import type { Collection } from "@ghome/db";

export function TopicCard({ topic }: { topic: Collection }) {
  return (
    <Link href={`/topic/${topic.slug}`} className="topic-card" style={{ background: topic.coverKey ?? "var(--primary-light)" }}>
      <div className="topic-body">
        <h4>{topic.title}</h4>
        <p>{topic.description}</p>
      </div>
    </Link>
  );
}
```

- [ ] **Step 5: 写 `RankingCard.tsx`** — 参考原型 :1430-1480 `.rank-card`:

接收一个 collection(kind=ranking),渲染 6 区块之一。详细实现见 T10。本 task 写一个**通用的** RankingCard,接收 `{ title, items: Array<{ rank, title, hot, href }> }`:

```tsx
import Link from "next/link";

interface RankingCardItem {
  rank: number;
  title: React.ReactNode;
  hot: string;
  href: string;
}

export function RankingCard({
  title,
  emoji,
  items,
}: {
  title: string;
  emoji: string;
  items: RankingCardItem[];
}) {
  return (
    <div className="rank-card">
      <h3>
        <span>{emoji}</span>
        {title}
      </h3>
      {items.map((it) => (
        <Link key={it.rank} href={it.href} className={`rank-item ${it.rank <= 3 ? "top" : ""}`}>
          <span className="rank-num">{it.rank}</span>
          <span className="rank-name">{it.title}</span>
          <span className="rank-hot">{it.hot}</span>
        </Link>
      ))}
    </div>
  );
}
```

- [ ] **Step 6: 写 `TagPill.tsx`**

```tsx
import Link from "next/link";

export function TagPill({ slug, label, asLink = true }: { slug: string; label: string; asLink?: boolean }) {
  if (!asLink) return <span className="pill">{label}</span>;
  return (
    <Link href={`/tag/${slug}`} className="pill pill-link">
      #{label}
    </Link>
  );
}
```

- [ ] **Step 7: 验证 typecheck**

```bash
pnpm --filter @ghome/web typecheck
```

- [ ] **Step 8: 提交**

```bash
git add apps/web/components/
git commit -m "feat(web): card components — App/Video/Guide/Topic/Ranking/TagPill"
```

---

## Task 6 — 首页 `/`

**Files:**
- Modify: `apps/web/app/page.tsx`(从 P0 占位 → 完整首页)
- Create: `apps/web/components/FeaturedHero.tsx`(FEATURED_WEB hero 区块)

参考原型 `renderHome` :768-893 与 hero / 重点推荐 / app 列表 / 视频列表 / 专题这几块 CSS。

- [ ] **Step 1: 写 `FeaturedHero.tsx`** — 用 fixtures.featured-web,渲染原型的"重点推荐"卡片(`.featured-card` :61-96):

```tsx
import { FEATURED_WEB } from "@/fixtures/featured-web";
import { Icon } from "@/lib/icons";

export function FeaturedHero() {
  const fw = FEATURED_WEB;
  return (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">
            <span className="i">🔥</span>重点推荐
          </h2>
        </div>
        <div className="featured-card">
          <div className="feat-top">
            <div className="feat-banner">
              <div className="feat-brand">
                <div className="feat-brand-ic">{/* logo */}</div>
                <div>
                  <div className="feat-brand-name">{fw.name}</div>
                  <div className="feat-brand-sub">{fw.type} · 男同生活方式视频站</div>
                </div>
              </div>
              <p className="feat-tagline">{fw.desc}</p>
              <div className="feat-stat-grid">
                <div className="feat-stat"><div className="v">{fw.stats.videos}</div><div className="l">视频</div></div>
                <div className="feat-stat"><div className="v">{fw.stats.creators}</div><div className="l">创作者</div></div>
                <div className="feat-stat"><div className="v">{fw.stats.plays}</div><div className="l">累计播放</div></div>
                <div className="feat-stat"><div className="v">{fw.stats.rating}</div><div className="l">综合评分</div></div>
              </div>
            </div>
            <div className="feat-detail">
              <div className="feat-head"><h3>{fw.name}</h3><span className="pill">{fw.type}</span></div>
              <p className="feat-desc">{fw.desc}</p>
              <div className="feat-features">
                {fw.tags.map((t) => (
                  <div key={t} className="feat-feat">
                    <Icon name="i-check" grad="g-leaf" size={16} />
                    <span>{t}</span>
                  </div>
                ))}
              </div>
              <div className="feat-meta-row">
                <div className="meta">
                  <Icon name="i-users" size={16} />
                  <div><b>适合人群:</b>{fw.audience}</div>
                </div>
                <div className="meta">
                  <Icon name="i-sparkle" size={16} />
                  <div><b>主要功能:</b>{fw.features}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: 写首页 `apps/web/app/page.tsx`**

```tsx
import Link from "next/link";
import {
  getPublishedApps,
  getPublishedVideos,
  getCollectionsByKind,
} from "@/lib/db";
import { AppCard } from "@/components/AppCard";
import { VideoCard } from "@/components/VideoCard";
import { TopicCard } from "@/components/TopicCard";
import { FeaturedHero } from "@/components/FeaturedHero";

export const revalidate = 60;

export default async function HomePage() {
  const [apps, videos, topics] = await Promise.all([
    getPublishedApps({ limit: 6 }),
    getPublishedVideos({ limit: 8 }),
    getCollectionsByKind("topic"),
  ]);

  return (
    <>
      {/* Hero(原型 :770-784) */}
      <section className="hero">
        <div className="container">
          <h1>探索更适合男同用户的 App、视频与内容平台</h1>
          <p>Ghome 为您精选并评测全球优质的 LGBTQ+ 社交软件、娱乐平台及实用工具,<br />助您快速找到最契合的数字生活方式</p>
          <div className="search-box">
            <span className="si">🔍</span>
            <input placeholder="搜索 App、视频、专题…" disabled />
            <button className="btn-primary" disabled>搜索</button>
          </div>
          <div className="hot">
            <span>热门:</span>
            <Link href="/category/fitness">健身</Link>
            <Link href="/category/travel">旅行</Link>
            <Link href="/category/vlog">Vlog</Link>
            <Link href="/category/interview">访谈</Link>
          </div>
        </div>
      </section>

      <FeaturedHero />

      {/* App 导航(原型 :842-852) */}
      <section className="section" style={{ paddingTop: 20 }}>
        <div className="container">
          <div className="section-header">
            <h2 className="section-title"><span className="i">⊞</span>优质 App 导航</h2>
            <Link href="/apps" className="view-more">浏览全部 →</Link>
          </div>
          <div className="app-grid">
            {apps.map((a) => <AppCard key={a.id} app={a} />)}
          </div>
        </div>
      </section>

      {/* 热门视频(原型 :854-865) */}
      <section className="section" style={{ paddingTop: 20 }}>
        <div className="container">
          <div className="section-header">
            <h2 className="section-title"><span className="i">🎬</span>热门男同视频</h2>
            <Link href="/videos" className="view-more">浏览全部 →</Link>
          </div>
          <div className="video-grid">
            {videos.map((v) => <VideoCard key={v.id} video={v} />)}
          </div>
        </div>
      </section>

      {/* 精选专题(原型 :867-880) */}
      <section className="section" style={{ paddingTop: 20, paddingBottom: 80 }}>
        <div className="container">
          <div className="section-header">
            <h2 className="section-title"><span className="i">📑</span>精选专题</h2>
            <Link href="/topics" className="view-more">浏览全部 →</Link>
          </div>
          <div className="topics-grid">
            {topics.map((t) => <TopicCard key={t.id} topic={t} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 3: 验证 build + 起 dev 看效果**

```bash
docker compose up -d
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev &
sleep 8
curl -fsS http://localhost:3000/ | grep -q "探索更适合男同用户" && echo "OK"
curl -fsS http://localhost:3000/ | grep -q "G-Video Hub" && echo "featured OK"
kill %1 2>/dev/null || true
```

Expected: 两个 grep 都命中。

- [ ] **Step 4: 提交**

```bash
git add apps/web/app/page.tsx apps/web/components/FeaturedHero.tsx
git commit -m "feat(web): home page with hero, featured, apps, videos, topics sections"
```

---

## Task 7 — `/apps` 列表 + `/app/[slug]` 详情

**Files:**
- Create: `apps/web/app/apps/page.tsx`
- Create: `apps/web/app/app/[slug]/page.tsx`

参考原型 `renderAppsList` :896-958、`renderAppDetail` :960-1083。

- [ ] **Step 1: 写 `app/apps/page.tsx` — App 列表 + 分类筛选**

```tsx
import { getPublishedApps, getAppCategories } from "@/lib/db";
import { AppCard } from "@/components/AppCard";
import { Crumb } from "@/components/Crumb";
import Link from "next/link";

export const revalidate = 60;

export default async function AppsListPage({
  searchParams,
}: {
  searchParams: Promise<{ cat?: string }>;
}) {
  const sp = await searchParams;
  const [apps, cats] = await Promise.all([
    getPublishedApps({ categorySlug: sp.cat }),
    getAppCategories(),
  ]);

  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>男同 App 矩阵导航</h1>
          <p>覆盖社交、生活、娱乐三大场景的优质 App 推荐</p>
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "男同 App" }]} />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="filter-tabs">
            <Link href="/apps" className={!sp.cat ? "active" : ""}>全部</Link>
            {cats.map((c) => (
              <Link key={c.id} href={`/apps?cat=${c.slug}`} className={sp.cat === c.slug ? "active" : ""}>
                {c.label}
              </Link>
            ))}
          </div>
          <div className="app-grid">
            {apps.map((a) => <AppCard key={a.id} app={a} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: 写 `app/app/[slug]/page.tsx` — App 详情**

```tsx
import { notFound } from "next/navigation";
import { getAppBySlug, getPublishedApps } from "@/lib/db";
import { AppCard } from "@/components/AppCard";
import { TagPill } from "@/components/TagPill";
import { Crumb } from "@/components/Crumb";
import { SAMPLE_REVIEWS } from "@/fixtures/sample-reviews";
import { gradCss } from "@/lib/gradients";
import { Icon } from "@/lib/icons";

export const revalidate = 300;

export async function generateStaticParams() {
  const apps = await getPublishedApps();
  return apps.map((a) => ({ slug: a.slug }));
}

export default async function AppDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const app = await getAppBySlug(slug);
  if (!app) notFound();

  const sameCategoryApps = (await getPublishedApps({ categorySlug: app.category.slug }))
    .filter((a) => a.id !== app.id)
    .slice(0, 4);

  return (
    <>
      <Crumb items={[
        { href: "/", label: "首页" },
        { href: "/apps", label: "男同 App" },
        { label: app.name },
      ]} />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="app-detail-head">
            <div className="featured-icon" style={{ background: gradCss(app.gradientKey) }}>
              <Icon name={app.iconKey} grad="g-mute" size={36} />
            </div>
            <div className="app-detail-meta">
              <h1>{app.name}</h1>
              <p>{app.shortDesc}</p>
              <div className="app-detail-tags">
                {app.tags.map(({ tag }) => <TagPill key={tag.id} slug={tag.slug} label={tag.label} />)}
              </div>
              <div className="app-detail-stats">
                <span>{app.usersLabel} 用户</span>
                <span>·</span>
                <span>{app.rating} 评分</span>
                <span>·</span>
                <span>{app.platform}</span>
                <span>·</span>
                <span>{app.size}</span>
              </div>
              {/* 下载按钮:redirect.disabled=true 时置灰,P3 才接 /r/:id */}
              <DownloadButton disabled={app.redirect.disabled} href={app.redirect.disabled ? undefined : `/r/${app.redirect.id}`} />
            </div>
          </div>

          <div className="grid-2col">
            <div>
              <h2>产品介绍</h2>
              <p>{app.detail}</p>
              <h2>核心亮点</h2>
              <ul className="hl-list">
                {app.highlights.map((h, i) => <li key={i}>{h}</li>)}
              </ul>
              <h2>适合人群</h2>
              <p>{app.audience}</p>
              <h2>主要功能</h2>
              <p>{app.features}</p>
            </div>
            <div>
              <h2 style={{ marginTop: 0 }}>用户评价</h2>
              {/* SAMPLE_REVIEWS 是 fixture */}
              {SAMPLE_REVIEWS.map((r, i) => (
                <ReviewItem key={i} review={r} />
              ))}
              <p className="muted" style={{ marginTop: 16 }}>* 评价示例,P5 后接入真实评价系统</p>
            </div>
          </div>

          <div className="section-header" style={{ marginTop: 40 }}>
            <h2 className="section-title">同类推荐</h2>
            <Link href="/apps" className="view-more">浏览全部 →</Link>
          </div>
          <div className="app-grid">
            {sameCategoryApps.map((a) => <AppCard key={a.id} app={a} />)}
          </div>
        </div>
      </section>
    </>
  );
}

function DownloadButton({ disabled, href }: { disabled: boolean; href?: string }) {
  if (disabled) {
    return (
      <button className="btn btn-primary" disabled style={{ opacity: 0.5, cursor: "not-allowed" }}>
        暂未开放
      </button>
    );
  }
  return (
    <a className="btn btn-primary" href={href}>立即下载</a>
  );
}

function ReviewItem({ review }: { review: typeof SAMPLE_REVIEWS[number] }) {
  return (
    <div className="review">
      <div className="avatar" style={{ background: `var(--primary-light)` }}>{review.avatar}</div>
      <div>
        <div><b>{review.name}</b> · {"⭐".repeat(review.stars)} · <small>{review.date}</small></div>
        <p>{review.body}</p>
      </div>
    </div>
  );
}

import Link from "next/link";  // 注:这里实际放文件顶部
```

- [ ] **Step 3: 验证 build + dev**

```bash
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev &
sleep 8
curl -fsS http://localhost:3000/apps | grep -q "男同 App 矩阵导航" && echo "list OK"
curl -fsS http://localhost:3000/app/broconnect | grep -q "BroConnect" && echo "detail OK"
curl -fsS http://localhost:3000/app/nonexistent -o /dev/null -w "%{http_code}\n" | grep 404 && echo "404 OK"
kill %1 2>/dev/null || true
```

- [ ] **Step 4: 提交**

```bash
git add apps/web/app/apps/ apps/web/app/app/
git commit -m "feat(web): /apps list with category filter and /app/:slug detail"
```

---

## Task 8 — `/videos` 列表 + `/video/[slug]` 详情

**Files:**
- Create: `apps/web/app/videos/page.tsx`
- Create: `apps/web/app/video/[slug]/page.tsx`

参考原型 `renderVideosHome` :1085-1183、`renderVideoDetail` :1185-1288。

- [ ] **Step 1: 写 `app/videos/page.tsx`** — 视频首页(含 FEATURED_WEB hero + 热门 + 最新 + 创作者 + 分类)

数据来源:
- `getPublishedVideos({ limit: 8 })` — 热门(实际按 publishedDate desc 来代替)
- `getCollectionsByKind("ranking")` — 取 weekly-hot-videos 与 latest-videos 来覆盖"热门"和"最新"区块
- CREATORS fixture
- VIDEO_CATS

参照原型 :1085-1183 渲染 hero(FEATURED_WEB)+ "热门视频" + "最新上线" + "认证创作者" + "视频分类"。

- [ ] **Step 2: 写 `app/video/[slug]/page.tsx`** — 视频详情

数据来源:`getVideoBySlug(slug)`,fallback notFound;同类视频 `getPublishedVideos({ categorySlug: video.category.slug, limit: 4 })`;同标签视频通过 video.tags[*].tag.slug 第一个查 `getPublishedVideos({ tagSlug })` 4 条。

引用 `creatorForVideoCategorySlug(video.category.slug)` 显示创作者(fixture)。

外链按钮逻辑同 App detail 的 DownloadButton。

ISR `revalidate = 300`。

`generateStaticParams()` 返回所有 published video slugs。

- [ ] **Step 3: 验证**

```bash
curl localhost:3000/videos | grep "热门视频"
curl localhost:3000/video/v01 | grep "都市生活"
curl localhost:3000/video/missing -o /dev/null -w "%{http_code}" | grep 404
```

- [ ] **Step 4: 提交**

```bash
git add apps/web/app/videos/ apps/web/app/video/
git commit -m "feat(web): /videos home and /video/:slug detail with creators fixture"
```

---

## Task 9 — `/categories` + `/category/[slug]` + `/tag/[slug]`

**Files:**
- Create: `apps/web/app/categories/page.tsx`
- Create: `apps/web/app/category/[slug]/page.tsx`
- Create: `apps/web/app/tag/[slug]/page.tsx`

参考原型 :1290-1410。**注意:`/category/:slug` 仅解析视频分类**(spec §3.2),App 分类只在 `/apps?cat=:slug` 出现。

- [ ] **Step 1: 写 `app/categories/page.tsx`** — 列出 6 个视频分类(每个含视频计数):

```tsx
import { getVideoCategories, getPublishedVideos } from "@/lib/db";
import Link from "next/link";
import { Crumb } from "@/components/Crumb";

export const revalidate = 60;

export default async function CategoriesPage() {
  const cats = await getVideoCategories();
  // 计数:对每个 cat 查一次 video count
  const withCount = await Promise.all(
    cats.map(async (c) => ({
      ...c,
      count: (await getPublishedVideos({ categorySlug: c.slug })).length,
    })),
  );
  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>视频分类导航</h1>
          <p>按主题浏览,快速找到你想看的内容</p>
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "分类导航" }]} />
      <section className="section" style={{ paddingTop: 10 }}>
        <div className="container">
          <div className="topics-grid">
            {withCount.map((c) => (
              <Link key={c.id} href={`/category/${c.slug}`} className="topic-card">
                <div className="topic-body">
                  <h4>{c.label} · {c.count} 条视频</h4>
                  <p>{c.description ?? ""}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: 写 `app/category/[slug]/page.tsx`** — 仅 video kind:

```tsx
import { notFound } from "next/navigation";
import { getVideoCategoryBySlug, getPublishedVideos, getPublishedApps } from "@/lib/db";
import { VideoCard } from "@/components/VideoCard";
import { AppCard } from "@/components/AppCard";
import { Crumb } from "@/components/Crumb";
import Link from "next/link";

export const revalidate = 300;

export async function generateStaticParams() {
  // 仅 video kind
  const cats = await (await import("@/lib/db")).getVideoCategories();
  return cats.map((c) => ({ slug: c.slug }));
}

export default async function CategoryDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const cat = await getVideoCategoryBySlug(slug);
  if (!cat) notFound();

  const [videos, recommendedApps] = await Promise.all([
    getPublishedVideos({ categorySlug: slug, limit: 24 }),
    getPublishedApps({ limit: 4 }),
  ]);

  return (
    <>
      <div className="page-head" style={{ background: "var(--primary-light)" }}>
        <div className="container">
          <h1>{cat.label} · 男同视频推荐</h1>
        </div>
      </div>
      <Crumb items={[
        { href: "/", label: "首页" },
        { href: "/categories", label: "分类导航" },
        { label: cat.label },
      ]} />
      <section className="section" style={{ paddingTop: 10 }}>
        <div className="container">
          <div className="cat-intro">
            <h3>关于「{cat.label}」分类</h3>
            <p>{cat.description}</p>
          </div>
          <div className="video-grid" style={{ marginTop: 24 }}>
            {videos.map((v) => <VideoCard key={v.id} video={v} />)}
          </div>

          <div className="section-header" style={{ marginTop: 40 }}>
            <h2 className="section-title">推荐 App</h2>
            <Link href="/apps" className="view-more">浏览全部 →</Link>
          </div>
          <div className="app-grid">
            {recommendedApps.map((a) => <AppCard key={a.id} app={a} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 3: 写 `app/tag/[slug]/page.tsx`**:

```tsx
import { notFound } from "next/navigation";
import { getTagBySlug, getPublishedVideos, getPublishedApps, getAllTags } from "@/lib/db";
import { VideoCard } from "@/components/VideoCard";
import { AppCard } from "@/components/AppCard";
import { TagPill } from "@/components/TagPill";
import { Crumb } from "@/components/Crumb";

export const revalidate = 300;

export async function generateStaticParams() {
  const tags = await getAllTags();
  return tags.map((t) => ({ slug: t.slug }));
}

export default async function TagPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const tag = await getTagBySlug(slug);
  if (!tag) notFound();

  const [videos, allTags, apps] = await Promise.all([
    getPublishedVideos({ tagSlug: slug, limit: 24 }),
    getAllTags(),
    getPublishedApps({ limit: 4 }),
  ]);

  const otherTags = allTags.filter((t) => t.slug !== slug).slice(0, 12);

  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>#{tag.label}</h1>
        </div>
      </div>
      <Crumb items={[
        { href: "/", label: "首页" },
        { label: `#${tag.label}` },
      ]} />
      <section className="section" style={{ paddingTop: 10 }}>
        <div className="container">
          <div className="video-grid">
            {videos.map((v) => <VideoCard key={v.id} video={v} />)}
          </div>

          <div className="section-header" style={{ marginTop: 40 }}>
            <h2 className="section-title">其他热门标签</h2>
          </div>
          <div className="tag-pills-row">
            {otherTags.map((t) => <TagPill key={t.id} slug={t.slug} label={t.label} />)}
          </div>

          <div className="section-header" style={{ marginTop: 40 }}>
            <h2 className="section-title">推荐 App</h2>
          </div>
          <div className="app-grid">
            {apps.map((a) => <AppCard key={a.id} app={a} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 4: 验证**

```bash
curl localhost:3000/categories | grep "视频分类导航"
curl localhost:3000/category/fitness | grep "健身 · 男同视频推荐"
curl localhost:3000/tag/fitness-tag | grep "#健身"
curl localhost:3000/category/social -o /dev/null -w "%{http_code}" | grep 404  # social 是 app 分类,不应在 /category/ 出现
```

> 注:`/category/social` 应该 404,因为 social 是 kind='app',`getVideoCategoryBySlug` 找不到。

- [ ] **Step 5: 提交**

```bash
git add apps/web/app/categories/ apps/web/app/category/ apps/web/app/tag/
git commit -m "feat(web): /categories, /category/:slug (video-only), /tag/:slug pages"
```

---

## Task 10 — `/topics` + `/topic/[slug]` + `/rankings` + `/albums` 占位

**Files:**
- Create: `apps/web/app/topics/page.tsx`
- Create: `apps/web/app/topic/[slug]/page.tsx`
- Create: `apps/web/app/rankings/page.tsx`
- Create: `apps/web/app/albums/page.tsx`(`notFound()`)
- Create: `apps/web/app/album/[slug]/page.tsx`(`notFound()`)

参考原型 `renderTopicsList` :1485+、`renderTopicDetail` :1510+、`renderRankings` :1412-1483。

- [ ] **Step 1: `/topics` 列表**

```tsx
import { getCollectionsByKind } from "@/lib/db";
import { TopicCard } from "@/components/TopicCard";
import { Crumb } from "@/components/Crumb";

export const revalidate = 60;

export default async function TopicsListPage() {
  const topics = await getCollectionsByKind("topic");
  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>专题合集</h1>
          <p>由 Ghome 编辑精心策划的主题专题</p>
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "专题合集" }]} />
      <section className="section" style={{ paddingTop: 10, paddingBottom: 80 }}>
        <div className="container">
          <div className="topics-grid">
            {topics.map((t) => <TopicCard key={t.id} topic={t} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: `/topic/[slug]` 详情**

```tsx
import { notFound } from "next/navigation";
import { getCollectionBySlug, getCollectionsByKind } from "@/lib/db";
import { VideoCard } from "@/components/VideoCard";
import { TopicCard } from "@/components/TopicCard";
import { Crumb } from "@/components/Crumb";

export const revalidate = 300;

export async function generateStaticParams() {
  const topics = await getCollectionsByKind("topic");
  return topics.map((t) => ({ slug: t.slug }));
}

export default async function TopicDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const topic = await getCollectionBySlug(slug, "topic");
  if (!topic) notFound();

  const otherTopics = (await getCollectionsByKind("topic"))
    .filter((t) => t.slug !== slug)
    .slice(0, 6);

  return (
    <>
      <div className="page-head" style={{ background: topic.coverKey ?? "var(--primary-light)" }}>
        <div className="container">
          <h1>{topic.title}</h1>
          <p>{topic.description}</p>
        </div>
      </div>
      <Crumb items={[
        { href: "/", label: "首页" },
        { href: "/topics", label: "专题" },
        { label: topic.title },
      ]} />
      <section className="section" style={{ paddingTop: 10 }}>
        <div className="container">
          <div className="video-grid">
            {topic.items.map((it) =>
              it.video ? <VideoCard key={it.id} video={it.video as any} /> : null,
            )}
          </div>

          <div className="section-header" style={{ marginTop: 40 }}>
            <h2 className="section-title">其他专题</h2>
          </div>
          <div className="topics-grid">
            {otherTopics.map((t) => <TopicCard key={t.id} topic={t} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

> 注:`it.video` 类型是 `(Video & {category, redirect}) | null`。`as any` 临时绕过 — 更好的写法是把 `getCollectionBySlug` 的 include 在 `lib/db.ts` 里加上 tags 让类型完整,然后在 VideoCard 用更宽泛的类型。本 P2 先 `as any`,P3 再清。

- [ ] **Step 3: `/rankings` — 6 区块,从 6 条 ranking collection 渲染**

```tsx
import { getCollectionsByKind, getCollectionBySlug } from "@/lib/db";
import { RankingCard } from "@/components/RankingCard";
import { Crumb } from "@/components/Crumb";

export const revalidate = 60;

export default async function RankingsPage() {
  const rankings = await getCollectionsByKind("ranking");
  const detailed = await Promise.all(
    rankings.map((r) => getCollectionBySlug(r.slug, "ranking")),
  );

  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>Ghome 排行榜</h1>
          <p>每周基于用户行为数据更新的男同 App 与视频内容榜单。</p>
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "排行榜" }]} />
      <section className="section" style={{ paddingTop: 10 }}>
        <div className="container">
          <div className="rank-grid">
            {detailed.filter(Boolean).map((rk) => (
              <RankingCard
                key={rk!.id}
                title={rk!.title}
                emoji={rankingEmoji(rk!.slug)}
                items={rk!.items.map((it, i) => ({
                  rank: i + 1,
                  title: itemTitle(it),
                  hot: itemHot(it),
                  href: itemHref(it),
                }))}
              />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

function rankingEmoji(slug: string): string {
  switch (slug) {
    case "weekly-hot-videos": return "🔥";
    case "latest-videos":     return "✨";
    case "top-liked-videos":  return "💜";
    case "weekly-hot-apps":   return "📱";
    case "top-rated-apps":    return "⭐";
    case "hot-tags":          return "🏷";
    default: return "🔥";
  }
}

function itemTitle(it: any): React.ReactNode {
  if (it.video) return it.video.title;
  if (it.app) return it.app.name;
  if (it.tag) return `#${it.tag.label}`;
  return "—";
}

function itemHot(it: any): string {
  if (it.video) {
    const slug = it.collection?.slug ?? "";
    if (slug === "latest-videos") return it.video.publishedDate.toISOString().slice(0, 10);
    if (slug === "top-liked-videos") return `♥ ${it.video.likesLabel}`;
    return it.video.viewsLabel;
  }
  if (it.app) {
    const slug = it.collection?.slug ?? "";
    if (slug === "top-rated-apps") return `${it.app.rating} 分`;
    return it.app.usersLabel;
  }
  if (it.tag) {
    // count of videos with this tag — already implicit; fall back to label
    return "";
  }
  return "";
}

function itemHref(it: any): string {
  if (it.video) return `/video/${it.video.slug}`;
  if (it.app)   return `/app/${it.app.slug}`;
  if (it.tag)   return `/tag/${it.tag.slug}`;
  return "/";
}
```

> 注:`itemHot` 内部需要知道当前 ranking 的 slug;实际实现时把 ranking 的 slug 通过闭包/参数传入(上述代码用 `it.collection?.slug` 是不准确的,应该在 `RankingsPage` map 时 `(it, i)` 之外把 ranking slug 也传进来 — implementer 修正实现)。

- [ ] **Step 4: `/albums` + `/album/[slug]` 占位 → notFound()**

```tsx
// apps/web/app/albums/page.tsx
import { notFound } from "next/navigation";
export default function AlbumsPlaceholder() { notFound(); }
```

```tsx
// apps/web/app/album/[slug]/page.tsx
import { notFound } from "next/navigation";
export default function AlbumDetailPlaceholder() { notFound(); }
```

> 这两条路由在 P2 故意 404。P6 会落地真正实现。

- [ ] **Step 5: 验证**

```bash
curl localhost:3000/topics | grep "专题合集"
curl localhost:3000/topic/entry | grep "男同视频入门推荐"
curl localhost:3000/rankings | grep "本周热门视频榜"
curl localhost:3000/albums -o /dev/null -w "%{http_code}" | grep 404
curl localhost:3000/album/anything -o /dev/null -w "%{http_code}" | grep 404
```

- [ ] **Step 6: 提交**

```bash
git add apps/web/app/topics/ apps/web/app/topic/ apps/web/app/rankings/ apps/web/app/albums/ apps/web/app/album/
git commit -m "feat(web): /topics, /topic/:slug, /rankings (6 boards), /albums placeholder (notFound)"
```

---

## Task 11 — `/guides` + `/guide/[slug]` 含 markdown 渲染

**Files:**
- Create: `apps/web/components/MarkdownBody.tsx`
- Create: `apps/web/app/guides/page.tsx`
- Create: `apps/web/app/guide/[slug]/page.tsx`

参考原型 :1540+(列表)与 :1590+(详情含 TOC)。

- [ ] **Step 1: 写 `MarkdownBody.tsx`**

```tsx
"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MarkdownBody({ source }: { source: string }) {
  return (
    <div className="md-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{source}</ReactMarkdown>
    </div>
  );
}
```

> 用 client component 是因为 react-markdown 在 server component 渲染时偶尔有 hydration 问题(实际上 server 也行,但 client 更稳)。

- [ ] **Step 2: 写 `/guides` 列表**

```tsx
import { getPublishedGuides } from "@/lib/db";
import { GuideCard } from "@/components/GuideCard";
import { Crumb } from "@/components/Crumb";

export const revalidate = 60;

export default async function GuidesListPage() {
  const guides = await getPublishedGuides();
  return (
    <>
      <div className="page-head">
        <div className="container">
          <h1>使用指南</h1>
          <p>选 App、看视频、保护隐私的全套指南</p>
        </div>
      </div>
      <Crumb items={[{ href: "/", label: "首页" }, { label: "使用指南" }]} />
      <section className="section" style={{ paddingTop: 10, paddingBottom: 80 }}>
        <div className="container">
          <div className="guides-grid">
            {guides.map((g) => <GuideCard key={g.id} guide={g} />)}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 3: 写 `/guide/[slug]` 详情**

```tsx
import { notFound } from "next/navigation";
import { getGuideBySlug, getPublishedGuides } from "@/lib/db";
import { MarkdownBody } from "@/components/MarkdownBody";
import { Crumb } from "@/components/Crumb";
import { gradCss } from "@/lib/gradients";
import { Icon } from "@/lib/icons";
import { formatPublishDate, formatReadMinutes } from "@/lib/format";
import Link from "next/link";

export const revalidate = 300;

export async function generateStaticParams() {
  const guides = await getPublishedGuides();
  return guides.map((g) => ({ slug: g.slug }));
}

export default async function GuideDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const guide = await getGuideBySlug(slug);
  if (!guide) notFound();

  const all = await getPublishedGuides();
  const idx = all.findIndex((g) => g.slug === slug);
  const prev = idx > 0 ? all[idx - 1] : null;
  const next = idx < all.length - 1 ? all[idx + 1] : null;

  return (
    <>
      <section className="gd-hero" style={{ background: gradCss(guide.gradientKey) }}>
        <div className="container">
          <span className="pill">{guide.categoryLabel}</span>
          <h1>{guide.title}</h1>
          <p>{guide.summary}</p>
          <div className="gd-meta">
            <span><Icon name="i-calendar" size={14} /> {formatPublishDate(guide.publishedDate)}</span>
            <span><Icon name="i-clock" size={14} /> {formatReadMinutes(guide.readMinutes)}</span>
            <span><Icon name="i-eye" size={14} /> {guide.viewsLabel}</span>
          </div>
        </div>
      </section>
      <Crumb items={[
        { href: "/", label: "首页" },
        { href: "/guides", label: "使用指南" },
        { label: guide.title },
      ]} />
      <section className="section" style={{ paddingTop: 20, paddingBottom: 80 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <MarkdownBody source={guide.bodyMd} />

          <div className="gd-nav">
            {prev && <Link href={`/guide/${prev.slug}`} className="gd-prev">← {prev.title}</Link>}
            {next && <Link href={`/guide/${next.slug}`} className="gd-next">{next.title} →</Link>}
          </div>
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 4: 验证**

```bash
curl localhost:3000/guides | grep "使用指南"
curl localhost:3000/guide/choose-app | grep "如何选择适合自己的男同 App"
curl localhost:3000/guide/choose-app | grep "明确你的核心需求"  # markdown body 渲染
curl localhost:3000/guide/missing -o /dev/null -w "%{http_code}" | grep 404
```

- [ ] **Step 5: 提交**

```bash
git add apps/web/components/MarkdownBody.tsx apps/web/app/guides/ apps/web/app/guide/
git commit -m "feat(web): /guides list and /guide/:slug detail with react-markdown"
```

---

## Task 12 — 静态页 + ISR 配置整理 + 完整冒烟 + tag

**Files:**
- Create: `apps/web/app/about/page.tsx`
- Create: `apps/web/app/contact/page.tsx`
- Create: `apps/web/app/terms/page.tsx`

参考原型 `renderAbout` :1754-1781、`renderContact` :1783-1808、`renderTerms` :1810-1830。

- [ ] **Step 1: 写 `app/about/page.tsx`**

文案直接参 prototype `renderAbout` 内的 about-card,转成 React JSX。无 DB 查询、无 ISR(纯 SSG)。

- [ ] **Step 2: 写 `app/contact/page.tsx`** — 同样转 prototype `renderContact`。

- [ ] **Step 3: 写 `app/terms/page.tsx`** — 同样转 prototype `renderTerms`。

- [ ] **Step 4: 完整冒烟(干净环境)**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
sleep 5
pnpm --filter @ghome/db db:reset --force
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev &
sleep 10

# 16 条原型路由
for path in / /apps /app/broconnect /videos /video/v01 /categories /category/fitness /tag/fitness-tag /topics /topic/entry /rankings /guides /guide/choose-app /about /contact /terms; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$path")
  echo "GET $path → $status"
done

# /albums 与 /album/:slug 应 404
for path in /albums /album/whatever; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$path")
  echo "GET $path → $status (expect 404)"
done

kill %1 2>/dev/null || true
docker compose down
```

Expected: 前 16 条都返回 200;后 2 条都返回 404。

- [ ] **Step 5: typecheck + lint + test 全套**

```bash
pnpm typecheck
pnpm lint
pnpm --filter @ghome/db test
pnpm build
```

Expected: 4 步全过。

- [ ] **Step 6: 提交 + 标签 P2**

```bash
git add apps/web/app/about/ apps/web/app/contact/ apps/web/app/terms/
git commit -m "feat(web): static about/contact/terms pages"

# 顺手把 plan 文件提交(同 P0/P1 末端的惯例)
git add docs/superpowers/plans/2026-05-09-ghome-p2-frontend-readonly.md
git commit -m "docs: commit P2 implementation plan"

git tag -a p2-frontend-readonly -m "P2 · frontend read-only: 16 prototype routes connected to DB; FEATURED_WEB/CREATORS/SAMPLE_REVIEWS as fixtures; /albums placeholder; ISR 60s/300s; CSS frozen from prototype"
git log --oneline p1-data-model..HEAD
git tag -l
```

---

## P2 完成判据(对应 spec §5)

- ✅ 16 条原型路由用 SSG/ISR 渲染,数据来自 DB(T1-T11 + T12 静态页)
- ✅ `/rankings` 渲染 6 条 ranking collections(T10),5 内容榜各 8 + tag 榜 10 与原型一致
- ✅ FEATURED_WEB / CREATORS / SAMPLE_REVIEWS 作为 fixture(T3 + 各页面引用)
- ✅ `/albums` 与 `/album/:slug` 在 P2 返回 404 占位(T10)
- ✅ ISR 配置:列表 60s / 详情 300s / 静态页全 SSG(分布在各 task)
- ✅ markdown 渲染(react-markdown)用于 guide bodies(T11)
- ✅ 视觉对齐原型(整体 CSS 抄自 prototype,T1)

---

## 已知 P2 故意不做的事(P3+ 起补)

- **`/r/:id` 跳转中转**:P2 详情页的下载按钮在 `redirect.disabled=true` 时置灰,不渲染外链;启用后用 `<a href={redirect.targetUrl}>` 占位,**不**走中转(P3 才接 `/r/:id` route handler + click_events 写入)
- **搜索框接通**:首页 `<input disabled>`,P8 才接
- **admin 编辑**:web 仅读(P5/P6 起 admin 能写 → revalidate web)
- **i18n / 多语言**:全中文
- **`/albums`、`/album/:slug` 实际页面**:P6 才出
- **active state on Header**:用 `usePathname` 在 client 侧推断 — 已 P2 实现

---

## Self-Review

- **Spec 覆盖**:逐条核对 spec §2.1 路由表,16 条原型路由 + 2 条 albums 占位全部有 task 覆盖。`/category/:slug` 仅解析 video kind(spec §3.2)在 T9 Step 2 显式要求(getVideoCategoryBySlug 限定 kind=video)。`/rankings` 直接读 DB 不做运行时排序(spec §0)在 T10 Step 3 实现。

- **占位符扫描**:plan 内有 2 处 `// 实际...` 与 `// 详见原型...` 是有意的引用注释,告诉 implementer 去 prototype 读对应 HTML 片段。这些不是 TBD,而是因为 prototype 的 SVG defs(T2 Step 2 ~40 行)与 Footer 内容(T4 Step 2)若全嵌入会让 plan 超 4500 行;让 implementer 去原型读对应 line 是更合理的做法。其余无 TBD/fill in。

- **TS 类型一致性**:`AppWithRels` / `VideoWithRels` / `CollectionWithItems` 在 `lib/db.ts` 定义,各 page 与 component 引用名一致。

- **风险**:T10 Step 3 `itemHot` 函数中 `it.collection?.slug` 是错的(CollectionItem 没有反向 collection 关系直接 expose);implementer 在实现时**应**改成在 RankingsPage `.map((rk) => ...)` 时把 `rk.slug` 传给 RankingCard 的 children,然后 RankingCard 内部根据 ranking slug 决定 hot 文案。已经在 plan 注释里点出。

---

## 下一步

P2 完成后,**写 P3 plan**(`/r/:id` 跳转中转 + `click_events` 写入 + 详情页 CTA 渲染 `/r/:id`;`pnpm db:enable-redirect` 验证管线 — 已 P1 落 CLI,但 P3 把 web 端的真实链接接上;`runtime='nodejs'` + 同步 INSERT;ip_hash 用 `HMAC(SECRET, YYYY-MM-DD UTC)`;`ua-parser-js` 引入)。
