---
id: "doc-a313a3f80b40"
title: "Ghome P9 · 高保真原型对齐(Design Refresh) Implementation Plan"
date: "2026-05-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p9-design-refresh.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p9-design-refresh.md"
sourceSha256: "e9a32df96d1d2515237701c39812c91f97472718c0ad0380f5a6053a014e28c5"
sourceSystem: "project-doc"
---

# Ghome P9 · 高保真原型对齐(Design Refresh) Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605100000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20P9%20%C2%B7%20%E9%AB%98%E4%BF%9D%E7%9C%9F%E5%8E%9F%E5%9E%8B%E5%AF%B9%E9%BD%90%28Design%20Refresh%29%20Implementation%20Plan.md)

> 整理日期：2026-05-10 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 web 前端从 P2 视觉(基于 `docs/ghome.html`)升级到 P9 高保真视觉(基于 `docs/ghome-20260509.html`)。**不动数据模型** —— 14 表 schema 完全够用,只新增 3 个 nullable 字段(apps.age / apps.dev / apps.lang);**不动管理后台** —— admin 仍按现有 CRUD 工作,仅给 App 编辑器加 3 个字段。

完成后:
- 浏览器打开 `/`、`/app/:slug`、`/video/:slug`、`/topic/:slug`、`/guide/:slug`、`/about`、`/contact`、`/terms` 视觉与 `docs/ghome-20260509.html` 几乎一致
- 首页 hero 输入"健身"出现自动联想下拉(跨 App / 视频 / 创作者 / 指南 / 专题 / 分类 / 标签 7 类),回车跳 `/search?q=健身`(已 P8 落地)
- 移动端右上角汉堡按钮打开抽屉式导航
- App 详情页桌面悬停「下载」出现 QR 码气泡(扫码到 `/r/${redirectId}`);Android 端按钮直跳;iOS 端按钮置灰或跳详情
- 视频区分「精选首页 `/videos`」与「全部 `/videos/list?cat=...&sort=...`」两条路径
- 排行榜默认只显示 2 个榜单(周热视频 / 最新视频),其余 4 个在 admin 可手动 publish 回来

## Architecture

- **CSS 一次性 port**:把新原型 217 个 class 中**新增的 58 条**整体写入 `apps/web/app/globals.css`(尤其是 `.brand-hero` `.app-hero` `.v-hero` `.gd-hero` `.topic-hero` `.info-cell` `.install-tips` `.apk-pop` `.qrbox` `.mobile-drawer*` `.suggest-*` `.guide-row` 等组件块)。`:root` token 不动 —— 旧版逐字节一致
- **新组件全部 server component**(读 DB 直渲),除了三个必须客户端的:
  1. `<SearchSuggest>`(hero 联想下拉,需 client fetch + debounce)
  2. `<AppDownloadCTA>` 内的 OS 检测(client effect 设 body.os-* class)
  3. `<MobileDrawer>`(toggle state)
- **OS 检测策略**:小 client 组件挂在 `<body>`,基于 `navigator.userAgent` 设 `body.os-android` / `os-ios` / `os-desktop`;CSS 用属性选择器分支显示 / 隐藏不同 CTA(`body.os-android .btn-ios{display:none}` 等)。原型 line 140-153 就是这个模式
- **QR 码生成**:`apps/web/lib/qr.ts` 用一个轻量库(`qrcode-svg`,纯 JS,无 native deps)生成 SVG。**不引入 client-side qr** —— SSR 直接渲染 SVG 字符串到 `.qrbox`
- **联想下拉**:复用 P8 `searchAll()` 但前端只展示 top 5 / 类。新增 `apps/web/app/api/search/suggest/route.ts`(简化版返回更小的 SearchHit shape),debounce 200ms,客户端用 `useState + fetch`
- **Rankings 简化**:不删 6 条 ranking collections,改成 seed 时把 4 条非默认的状态设为 `archived`,web `/rankings` 已经 filter `published`,自然只显示 2 条;运营在 admin `/rankings/[id]/edit` 可手动 publish 回来
- **新增字段策略**:`apps.age` `apps.dev` `apps.lang` 全 nullable text,SeeD 中仅给 9 个 App 填默认值(age=`'17+'`,dev=`<name>+' Team'`,lang=`'等 5 种'`),admin App 编辑器加 3 行表单

## Tech Stack

- 新增依赖:`qrcode-svg ^1.0.0`(只在 SSR 用,纯 JS,~4KB)
- 已有依赖:Next.js 15, React 19, Prisma 5.22(都不动)
- **没有新数据模型 / 不动 click_events / 不动 audit_log / 不动 search 后端**

## Spec / 原型引用

- 主参考:[`docs/ghome-20260509.html`](../../ghome-20260509.html) —— 1.4MB / 3178 行高保真原型(20 张内嵌 base64 视频封面、Spec Mode 开发工具、完整新版 CSS / 交互)
- 旧参考:[`docs/ghome.html`](../../ghome.html) —— P2 实施时用的版本,不删,留作历史对照
- 14 表 schema 与 P0-P8 全部决策仍然有效,见 [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md)

## 前置假设

- P0-P8 已落地,`p8-search-wrapup` 标签存在
- `docs/ghome-20260509.html` 已 commit 到 docs/(若未 commit,T1 第一步先 commit)
- Postgres + admin + web 本地 dev 跑得起来
- 9 apps / 20 videos / 5 guides / 12 collections / 29 redirects seed 数据完整

## 不做(P9 范围外)

- **Spec Mode 开发工具**(`body.spec-mode` overlay + `showOpenFilePicker` 双向同步本地 .md):那是给设计师/开发者的内嵌工具,不是产品功能
- **真实视频封面图上传**:原型把 20 张图烤成 base64 是为了离线携带,生产应走对象存储(S3 / R2 / Cloudflare Images)。**P9 仍用 `coverCss(coverKey)` gradient 占位**,真实图上传留给 P10+
- **真实 APK 文件托管**:Android QR 编码的是 `/r/${redirectId}` URL,运营在 admin 把 redirect 的 targetUrl 设成 APK 直链即可。**不在 P9 内建对象存储**
- **联系页表单提交后端**:原型 contact 页只列出 3 个 mailto: 邮箱(`partner@` `content@` `bd@`),不是表单。沿用
- **评论 / 评分 / 用户登录 / UGC**:两版原型都没,延后
- **Rankings 算法升级**(自动按 click_events 重排序):仍走 seed 时冻结的策略
- **i18n / 多语言**:仍中文单语
- **PWA / 离线**
- **og:image 生成器** / Twitter Cards / JSON-LD

## File Structure(P9 末态)

```
apps/web/
├─ app/
│  ├─ globals.css                                      # T1:bulk port 58 新 class
│  ├─ layout.tsx                                       # T1:挂 <OsDetector />
│  ├─ page.tsx                                         # T2:首页 hero + 各 section 重写
│  ├─ video/[slug]/page.tsx                            # T4:视频详情 v-hero + 信息卡
│  ├─ videos/
│  │  ├─ page.tsx                                      # T4:精选首页(分 shelf)
│  │  └─ list/page.tsx                                 # T4:新增 /videos/list 筛选页
│  ├─ app/[slug]/page.tsx                              # T3:App 详情 app-hero + info-cell
│  ├─ guide/[slug]/page.tsx                            # T5:指南详情 gd-hero
│  ├─ guides/page.tsx                                  # T5:指南列表 row 化
│  ├─ topic/[slug]/page.tsx                            # T6:专题详情 hero-stats
│  ├─ about/page.tsx                                   # T7:about 4 卡 brand-grid
│  ├─ contact/page.tsx                                 # T7:contact 3 邮箱 + 收录标准
│  └─ terms/page.tsx                                   # T7:terms 重排
├─ components/
│  ├─ Header.tsx                                       # T8:加汉堡按钮 + drawer toggle
│  ├─ MobileDrawer.tsx                                 # T8:client,移动端抽屉
│  ├─ OsDetector.tsx                                   # T1:client,设 body.os-*
│  ├─ SearchSuggest.tsx                                # T2:client,首页联想下拉
│  ├─ AppDownloadCTA.tsx                               # T3:client(为了 OS 分支),Android QR
│  ├─ AppHero.tsx                                      # T3:server,App 详情顶部 banner
│  ├─ AppInfoGrid.tsx                                  # T3:server,info-cell 6 格
│  ├─ AppInstallTips.tsx                               # T3:server,安装步骤 + 注意
│  ├─ VideoHero.tsx                                    # T4:server
│  ├─ GuideHero.tsx                                    # T5:server
│  ├─ TopicHero.tsx                                    # T6:server,含 hero-stats
│  ├─ HeroSearch.tsx                                   # T2:server,hero 区搜索框 (含 SearchSuggest 客户端子组件)
│  └─ BrandGrid.tsx                                    # T7:server,about/contact 通用 4 卡
└─ lib/
   └─ qr.ts                                            # T3:服务端 QR SVG 生成

apps/admin/
└─ app/(admin)/apps/
   ├─ new/page.tsx                                     # T1:加 age/dev/lang 字段
   └─ [id]/edit/page.tsx                               # T1:加 age/dev/lang 字段

packages/db/
├─ prisma/
│  ├─ schema.prisma                                    # T1:apps 加 3 nullable 字段
│  ├─ migrations/20260510020000_app_meta_fields/       # T1:迁移
│  └─ seed.ts                                          # T1:9 App 填默认值;4 ranking 状态改 archived
└─ seed/data/apps.ts                                   # T1:补 age/dev/lang
```

新文件 ~14,改动 ~10,1 个迁移。

## Conventions(整个 P9 共享)

- **服务端组件优先**:除 `OsDetector` / `SearchSuggest` / `AppDownloadCTA` / `MobileDrawer` 4 个明确 client 之外都 server。原型 JS 状态(loading 转圈、悬停效果)能用纯 CSS 做的就 CSS
- **Class 命名沿用原型**:`.app-hero` `.info-cell` `.install-tips` `.apk-pop` 等等,**不要重起名**,免得后续比对原型 diff 有摩擦
- **Hero gradient 一致**:每个 hero 顶部 gradient 由该实体的 `gradientKey`(App / 指南)或 `coverKey`(视频)派生,首页/about/contact 的 brand-hero 用固定 `linear-gradient(135deg,#5B5BE8 0%,#7B5BE8 50%,#B85BE8 100%)`(原型 line 543)
- **不引入 client-side QR 库**:`qrcode-svg` 在 SSR 跑,SVG 字符串直接 inline。客户端 0 KB
- **OS 分支隐藏 / 显示用 CSS**(原型 line 140-153 模式),不在 React 里 if/else,避免水合不匹配
- **SearchSuggest debounce 200ms**:用户停止输入 200ms 后才发请求;最少 2 字符触发(沿用 `normalizeQuery`)
- **不做 i18n**:中文文案直写
- **每完成一个 task 提交一次**(Conventional Commits)。如果 git commit 被 permission rule 阻塞,报 DONE_WITH_CONCERNS

---

## Task 1 — 数据基建 + CSS 一次性 port + Rankings seed 简化

**Files:**
- Modify: `packages/db/prisma/schema.prisma`(apps 加 age / dev / lang nullable text)
- Create: `packages/db/prisma/migrations/20260510020000_app_meta_fields/migration.sql`
- Modify: `packages/db/seed/data/apps.ts`(9 个 App 各填默认值)
- Modify: `packages/db/prisma/seed.ts`(写入新字段;4 个非默认 ranking 状态改 archived)
- Modify: `apps/web/app/globals.css`(bulk port 58 新 class)
- Modify: `apps/admin/app/(admin)/apps/new/page.tsx`(加 3 字段)
- Modify: `apps/admin/app/(admin)/apps/[id]/edit/page.tsx`(加 3 字段)
- Create: `apps/web/components/OsDetector.tsx`
- Modify: `apps/web/app/layout.tsx`(挂 OsDetector + 给 body 留 className)
- Create: `apps/web/lib/qr.ts`
- Add dep: `qrcode-svg`

### 8 Steps

**Step 1: schema + migration**

```prisma
model App {
  // ... existing
  age   String?  @map("age")
  dev   String?  @map("dev")
  lang  String?  @map("lang")
}
```

```sql
-- migrations/20260510020000_app_meta_fields/migration.sql
ALTER TABLE "apps"
  ADD COLUMN "age"  TEXT,
  ADD COLUMN "dev"  TEXT,
  ADD COLUMN "lang" TEXT;
```

应用:`pnpm --filter @ghome/db db:migrate:deploy && pnpm --filter @ghome/db db:generate`

**Step 2: 给 9 个 App 填默认值**

`packages/db/seed/data/apps.ts` 每条加 `age / dev / lang`:
- age:统一 `'17+'`(原型 line ~700 fallback)
- dev:`{a.name} Team`(原型 fallback `name+' Team'`)
- lang:统一 `'中文 / 英文 等 5 种'`(原型 fallback `'等 5 种'`)

> seed 是 idempotent upsert,跑 `pnpm db:seed` 后 9 行被 update,新字段写入。

**Step 3: rankings seed 状态调整**

`packages/db/prisma/seed.ts` 在 RANKINGS 循环里:

```ts
const DEFAULT_PUBLISHED_RANKINGS = new Set(["weekly-hot-videos", "latest-videos"]);
// ...
status: DEFAULT_PUBLISHED_RANKINGS.has(r.slug) ? "published" : "archived",
```

> 所有 6 条 ranking collections 仍 seed,但 `top-liked-videos` `weekly-hot-apps` `top-rated-apps` `hot-tags` 默认 `archived`。`/rankings` 路由已 filter `published`,自动只显示 2 条;admin 可在 `/rankings/[id]/edit` 手动 publish 回。

**Step 4: bulk port CSS**

把 `docs/ghome-20260509.html` 的 `<style>` 块里**新增的 58 个 class 块**整体复制到 `apps/web/app/globals.css` 末尾。**不要复制**:
- `:root` token(已经一致)
- `body.spec-mode` 相关一切(P9 范围外)
- `.spec-stage` `.spec-edit` 等 Spec Mode 开发工具样式

具体要 port 的 class 列表(对照原型行号):
- `brand-hero` 系列(line 543-553)+ `app-hero` `v-hero` `gd-hero` `topic-hero` 共享样式
- `info-cell` (line 357-360) + `install-tips` (line 351-353) + `install-notes`
- `apk-wrap` `apk-pop` `qrbox` (line 145-153)
- `mobile-drawer-mask` `mobile-drawer` (line 35-38) + `nav-toggle` `md-head` `md-nav` `md-sub` `md-divider` `md-close`
- `suggest-wrap` `suggest-dd` `suggest-item` `suggest-group` `suggest-more` `suggest-empty`
- `guide-row`(指南列表 row 化新样式)
- `topic-hero-stats` `th-stat` `topic-creators-inline` `topic-badge`
- `gd-hero`(指南详情新 hero)
- `brand-card` `brand-grid` `brand-cta`(about/contact/terms 新 4 卡)
- `crumb-trail` `back-btn`(面包屑增强)
- `cat-block` `cat-count` `cat-dot`
- `sr-creator-grid` `sr-creator-item` `sr-group` `sr-empty`(搜索结果页 — 已 P8 落地,可借机优化)
- 各种 OS 状态分支:`body.os-android .btn-ios{display:none}` `body.os-ios .btn-android{display:none}` 等(line 140, 144, 153)

**整体 port,不要漏 media query。** 完成后直接 `pnpm --filter @ghome/web build` 确认 CSS 不报错。

**Step 5: admin App 编辑器加 3 字段**

在 `apps/admin/app/(admin)/apps/new/page.tsx` 与 `[id]/edit/page.tsx` 的 EditForm 里追加:

```tsx
<FormRow label="年龄分级(age)" hint="如 '17+',可空">
  <input name="age" className="form-input" defaultValue={app?.age ?? ""} />
</FormRow>
<FormRow label="开发者(dev)" hint="如 'BroConnect Team',可空">
  <input name="dev" className="form-input" defaultValue={app?.dev ?? ""} />
</FormRow>
<FormRow label="语言(lang)" hint="如 '中文 / 英文 等 5 种',可空">
  <input name="lang" className="form-input" defaultValue={app?.lang ?? ""} />
</FormRow>
```

并在 `create` / `save` server action 里读取这 3 个 form field 写入 prisma。null/空字符串都接受为 `null`。

**Step 6: 新建 OsDetector + qr.ts**

`apps/web/components/OsDetector.tsx`(client):

```tsx
"use client";
import { useEffect } from "react";

export function OsDetector() {
  useEffect(() => {
    const ua = navigator.userAgent.toLowerCase();
    const cls = /android/.test(ua) ? "os-android" : /iphone|ipad|ipod/.test(ua) ? "os-ios" : "os-desktop";
    document.body.classList.add(cls);
    return () => document.body.classList.remove(cls);
  }, []);
  return null;
}
```

挂在 `apps/web/app/layout.tsx` 的 `<body>` 内,与 SvgSprite 同层。

`apps/web/lib/qr.ts`:

```ts
import QRCode from "qrcode-svg";

export function qrSvg(text: string, size = 140): string {
  const qr = new QRCode({
    content: text,
    padding: 0,
    width: size,
    height: size,
    color: "#1f2937",
    background: "#fff",
    ecl: "M",
  });
  return qr.svg();
}
```

**Step 7: 装依赖 + 验证**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/web add qrcode-svg
pnpm --filter @ghome/db db:migrate:deploy
pnpm --filter @ghome/db db:seed
pnpm --filter @ghome/db typecheck
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
```

全过才进 Step 8。

**Step 8: 提交**

```bash
git add packages/db/prisma/schema.prisma \
        packages/db/prisma/migrations/20260510020000_app_meta_fields \
        packages/db/seed/data/apps.ts \
        packages/db/prisma/seed.ts \
        apps/web/app/globals.css \
        apps/web/app/layout.tsx \
        'apps/admin/app/(admin)/apps/new/page.tsx' \
        'apps/admin/app/(admin)/apps/[id]/edit/page.tsx' \
        apps/web/components/OsDetector.tsx \
        apps/web/lib/qr.ts \
        apps/web/package.json pnpm-lock.yaml
git commit -m "feat(p9): foundation — apps age/dev/lang fields + bulk-port 58 CSS classes + OsDetector + qrcode-svg + rankings seed default to 2 boards"
```

## Tricky Bits (T1)

1. **CSS bulk port 时不要把 `:root` 也复制过来** —— web globals.css 已有相同 tokens,重复了会冲突
2. **不复制 Spec Mode 样式**:`body.spec-mode` 整段直接跳过
3. **media query 边界**:原型在 `(max-width:960px)` `768px` `560px` `500px` 都有断点,port 时整段块复制,别只复制顶层规则
4. **Prisma 迁移文件不要让 `prisma migrate dev` 自动生成**:它会想 drop P1 加的生成列(`category_kind`)。手写 SQL,这是 P1/P7 已经踩过的坑
5. **rankings seed 状态条件**:确保 `DEFAULT_PUBLISHED_RANKINGS` 字符串与 RANKINGS 数据中的 `slug` 完全一致;否则全部变 archived 或全部 published
6. **OsDetector 不能 SSR 渲染分支**:必须 client-only,否则水合时 server-side 没 `os-*` class、客户端立刻加上,会引发 hydration mismatch。所以全部用 CSS body class 选择器
7. **`qrcode-svg` 是纯 JS,无 native deps**,但 ESM 兼容性需测试 —— 装完先在 web/lib/qr.ts 里 import 跑一次 build 看是否过
8. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 2 — 首页重写 + 搜索联想

**Files:**
- Modify: `apps/web/app/page.tsx`
- Create: `apps/web/components/HeroSearch.tsx`(server)
- Create: `apps/web/components/SearchSuggest.tsx`(client)
- Create: `apps/web/app/api/search/suggest/route.ts`
- Create: `apps/web/lib/hot-queries.ts`(配置文件)

### 7 Steps

**Step 1: hot queries 配置**

`apps/web/lib/hot-queries.ts`:

```ts
export const HOT_QUERIES: string[] = [
  "长期关系", "附近交友", "健身圈", "线下活动",
  "Vlog", "旅行", "访谈", "CP向",
];
```

**Step 2: `/api/search/suggest` 路由**

```ts
import { NextResponse, type NextRequest } from "next/server";
import { searchAll } from "@/lib/db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const PER_GROUP_LIMIT = 5; // 联想下拉每组只取 5

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") ?? "";
  const result = await searchAll(q);
  // 截断每组 5 条;补充创作者(从 fixtures)+ 分类(从 categories)+ 标签(从 tags)
  // ... TODO 详细在 Step 3
  return NextResponse.json(result, { headers: { "cache-control": "no-store" } });
}
```

> 复用 P8 `searchAll`,只在结果上做截断 + 加入 creators / categories / tags 的命中(各 ≤3 条)。**不重写搜索逻辑。**

**Step 3: SearchSuggest client 组件**

```tsx
"use client";
import { useEffect, useState, useCallback, useRef } from "react";

interface Hit { id: string; slug: string; title: string; }
interface Result { apps: Hit[]; videos: Hit[]; guides: Hit[]; q: string; }

export function SearchSuggest({ initialQ = "" }: { initialQ?: string }) {
  const [q, setQ] = useState(initialQ);
  const [data, setData] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const t = useRef<number | null>(null);

  useEffect(() => {
    if (q.trim().length < 2) { setData(null); return; }
    if (t.current) window.clearTimeout(t.current);
    t.current = window.setTimeout(async () => {
      setLoading(true);
      const res = await fetch(`/api/search/suggest?q=${encodeURIComponent(q.trim())}`);
      setData(await res.json());
      setLoading(false);
    }, 200);
    return () => { if (t.current) window.clearTimeout(t.current); };
  }, [q]);

  return (
    <div className="suggest-wrap">
      <form method="get" action="/search">
        <input
          name="q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="搜索 App、视频、指南、专题…"
          required
          minLength={2}
          maxLength={100}
        />
        <button type="submit">搜索</button>
      </form>

      {data && (data.apps.length + data.videos.length + data.guides.length > 0) && (
        <div className="suggest-dd">
          {data.apps.length > 0 && (
            <div className="suggest-group">
              <div className="suggest-group-title">App</div>
              {data.apps.map(h => (
                <a key={h.id} href={`/app/${h.slug}`} className="suggest-item">{h.title}</a>
              ))}
            </div>
          )}
          {data.videos.length > 0 && (
            <div className="suggest-group">
              <div className="suggest-group-title">视频</div>
              {data.videos.map(h => (
                <a key={h.id} href={`/video/${h.slug}`} className="suggest-item">{h.title}</a>
              ))}
            </div>
          )}
          {data.guides.length > 0 && (
            <div className="suggest-group">
              <div className="suggest-group-title">指南</div>
              {data.guides.map(h => (
                <a key={h.id} href={`/guide/${h.slug}`} className="suggest-item">{h.title}</a>
              ))}
            </div>
          )}
          <a href={`/search?q=${encodeURIComponent(q.trim())}`} className="suggest-more">
            查看全部「{q.trim()}」结果 →
          </a>
        </div>
      )}
      {data === null && q.trim().length >= 2 && loading && (
        <div className="suggest-dd"><div className="suggest-empty">搜索中…</div></div>
      )}
    </div>
  );
}
```

**Step 4: HeroSearch server 组件**

```tsx
import Link from "next/link";
import { SearchSuggest } from "./SearchSuggest";
import { HOT_QUERIES } from "@/lib/hot-queries";

export function HeroSearch() {
  return (
    <section className="brand-hero">
      <div className="container">
        <span className="hero-tag">🌈 Ghome · LGBTQ+ 数字生活总入口</span>
        <h1>探索更适合男同用户的 App、视频与内容平台</h1>
        <p>Ghome 为您精选并评测全球优质的 LGBTQ+ 社交软件、娱乐平台及实用工具,助您快速找到最契合的数字生活方式。</p>
        <SearchSuggest />
        <div className="hot">
          <span>热门:</span>
          {HOT_QUERIES.slice(0, 4).map((q) => (
            <Link key={q} href={`/search?q=${encodeURIComponent(q)}`}>{q}</Link>
          ))}
        </div>
      </div>
    </section>
  );
}
```

**Step 5: 重写 `apps/web/app/page.tsx`**

替换原首页的 hero block + featured + cards section 顺序为新原型版式(查 `docs/ghome-20260509.html` 的 `renderHome` 函数,从大约 line 1900 开始)。结构大致:

1. `<HeroSearch />` —— 新 brand-hero 区
2. 推荐 App / 视频(沿用现 `getPublishedApps()` `getPublishedVideos()`)
3. 精选专题 + 创作者(沿用现 fixtures)
4. 评论(沿用现 fixtures `SAMPLE_REVIEWS`)
5. 数据契约不变,只重排 + 改 class 名

**Step 6: 验证**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev
# 浏览器:
#   http://localhost:3000  → hero 重画
#   输入「健身」→ 200ms 后下拉出现命中
#   回车 → /search?q=健身
```

**Step 7: 提交**

```bash
git add apps/web/lib/hot-queries.ts \
        apps/web/app/api/search/suggest/route.ts \
        apps/web/components/HeroSearch.tsx \
        apps/web/components/SearchSuggest.tsx \
        apps/web/app/page.tsx
git commit -m "feat(web): home page hero + search autocomplete dropdown over 3 entity types"
```

## Tricky Bits (T2)

1. **debounce 不要做成 inline closure** —— 用 useRef 持有 timer id 才能正确 cleanup。否则用户连续打字会发起 N 个 fetch
2. **联想下拉点击外部应关闭** —— 加 `useEffect` 监听 document click,点 wrap 外则 setData(null) 或加 `[hidden]` 状态。**MVP 可不做**(每输入新字符自动重 fetch,旧结果会被刷新)
3. **空 query / 太短 query 不发请求** —— 客户端先校验 2 字符,服务端 normalizeQuery 也校验,双层兜底
4. **联想下拉的 link 用 `<a>` 不用 `<Link>`** —— 因为下拉里点击会 navigate,Next.js Link 在 client hydration 前可能慢。`<a>` 直接走浏览器,体验稳定
5. **不要在 Suggest 里用 React Server Action** —— Suggest 是纯 read,fetch JSON 比 server action 简单
6. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 3 — App 详情页重写 + Android QR popover + OS 分支

**Files:**
- Modify: `apps/web/app/app/[slug]/page.tsx`
- Create: `apps/web/components/AppHero.tsx`(server)
- Create: `apps/web/components/AppInfoGrid.tsx`(server)
- Create: `apps/web/components/AppInstallTips.tsx`(server)
- Create: `apps/web/components/AppDownloadCTA.tsx`(server,内含 QR SVG)

### 8 Steps

**Step 1: AppHero 组件**

读 App,渲染:

```tsx
<section className="app-hero" style={{ background: gradCss(app.gradientKey) }}>
  <div className="container">
    <span className="hero-tag">App · {app.category.label}</span>
    <h1>{app.name}</h1>
    <p>{app.shortDesc}</p>
    {/* AppDownloadCTA 在此挂 */}
    <AppDownloadCTA app={app} />
  </div>
</section>
```

**Step 2: AppInfoGrid 组件**

6 格 info-cell(原型 line ~1980 起):

```tsx
<section className="app-info">
  <InfoCell label="评分" value={app.rating} />
  <InfoCell label="用户量" value={app.usersLabel} />
  <InfoCell label="平台" value={app.platform} />
  <InfoCell label="大小" value={app.size} />
  <InfoCell label="年龄分级" value={app.age ?? "17+"} />
  <InfoCell label="语言" value={app.lang ?? "等 5 种"} />
</section>
```

(`InfoCell` 内联即可,不用单独组件)。

**Step 3: AppInstallTips 组件**

```tsx
<section className="install-block">
  <h3>安装步骤</h3>
  <ol className="install-tips">
    <li>点击「立即下载」按钮跳转到官网或应用商店</li>
    <li>按提示安装</li>
    <li>初次启动可能需要授权</li>
  </ol>
  <div className="install-notes">
    <h4>注意事项</h4>
    <ul>
      <li className="note-item">仅从官方渠道下载,警惕仿冒</li>
      <li className="note-item">合理设置隐私,保护账号</li>
      <li className="note-item">遵守当地法律法规</li>
    </ul>
  </div>
</section>
```

(文案沿用原型 fixtures,不入库)

**Step 4: AppDownloadCTA + QR 气泡**

```tsx
import { qrSvg } from "@/lib/qr";

export function AppDownloadCTA({ app }: { app: AppWithRels }) {
  const baseUrl = process.env.NEXT_PUBLIC_WEB_BASE_URL ?? "http://localhost:3000";
  const redirectUrl = `${baseUrl}/r/${app.redirect.id}`;
  const disabled = app.redirect.disabled;
  const svg = disabled ? null : qrSvg(redirectUrl, 140);

  if (disabled) {
    return <button className="btn btn-disabled" disabled>暂未开放</button>;
  }

  return (
    <div className="cta-row">
      {/* Android: 直接跳 redirect */}
      <a href={`/r/${app.redirect.id}`} className="btn btn-filled btn-android">前往下载</a>
      {/* iOS: 直跳同个 redirect(运营改 targetUrl 时分别处理 store URL) */}
      <a href={`/r/${app.redirect.id}`} className="btn btn-filled btn-ios">前往 App Store</a>
      {/* Desktop: 显示按钮 + 悬停出 QR */}
      <div className="apk-wrap btn-desktop" tabIndex={0}>
        <button className="btn btn-filled">扫码下载</button>
        <div className="apk-pop">
          <div className="qrbox" dangerouslySetInnerHTML={{ __html: svg! }} />
          <div className="qt">扫码下载</div>
          <div className="qs">手机摄像头对准二维码</div>
        </div>
      </div>
    </div>
  );
}
```

> CSS 通过 `body.os-android .btn-ios{display:none}` `body.os-ios .btn-android{display:none}` `body.os-android .btn-desktop, body.os-ios .btn-desktop{display:none}` 自动分支(都在 T1 已 port 过来的 CSS 里),所以同时渲染 3 个按钮,实际只显示一个。

**Step 5: 重写 `apps/web/app/app/[slug]/page.tsx`**

```tsx
export default async function AppDetailPage(...) {
  // ... fetch app
  return (
    <>
      <AppHero app={app} />
      <Crumb items={[...]} />
      <section className="section">
        <div className="container">
          <AppInfoGrid app={app} />
          <h2>应用详解</h2>
          <p>{app.detail}</p>
          <h2>核心亮点</h2>
          <ul>{app.highlights.map(...)}</ul>
          <AppInstallTips />
        </div>
      </section>
    </>
  );
}
```

**Step 6: 验证**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev
# /app/broconnect 桌面浏览器:看 hero gradient + info-cell 6 格 + 悬停下载按钮出现 QR
# 用 chrome devtools 切到 iPhone UA → 应该看到 「前往 App Store」单按钮,QR 区隐藏
```

**Step 7: 提交**

```bash
git add 'apps/web/app/app/[slug]/page.tsx' \
        apps/web/components/AppHero.tsx \
        apps/web/components/AppInfoGrid.tsx \
        apps/web/components/AppInstallTips.tsx \
        apps/web/components/AppDownloadCTA.tsx
git commit -m "feat(web): app detail page with hero, 6-cell info grid, install tips, OS-aware download CTA with desktop QR popover"
```

## Tricky Bits (T3)

1. **`dangerouslySetInnerHTML` 只在 `qrSvg` 上用** —— 那是受信任的 SVG 字符串(我们自己生成的)。用户输入永远不通过这条路径
2. **QR 编码的 URL 必须是绝对路径**(`http://...`),不能是 `/r/${id}`,否则手机扫码后浏览器不知道域名
3. **`NEXT_PUBLIC_WEB_BASE_URL` 在 build 期已 inline 到客户端 bundle**,本地用 `http://localhost:3000` 测试 OK,生产部署前在 web/.env 设真实 host
4. **disabled redirect 的 CTA 要置灰**,既不渲染 QR 也不渲染按钮跳转 link —— 走「暂未开放」单按钮分支
5. **CSS 分支对 prerender 有影响**:server side 渲染时 body 没 `os-*` class,会渲染 3 个按钮。但 T1 已加 `body:not(.os-android):not(.os-ios) .btn-android, body:not(.os-android):not(.os-ios) .btn-ios { display: none }` 这种规则保证 desktop default 时只显示 desktop btn(可优化);也可以留 3 按钮先全可见,几毫秒后 OsDetector 加 class 收敛 —— **接受这个微闪烁 (FOUC)**,P10 再做 SSR-side UA detect 优化
6. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 4 — 视频区:`/videos` 重写 + 新增 `/videos/list?cat=...&sort=...`

**Files:**
- Modify: `apps/web/app/videos/page.tsx`(改成精选首页)
- Create: `apps/web/app/videos/list/page.tsx`(全部视频筛选页)
- Modify: `apps/web/app/video/[slug]/page.tsx`(详情 v-hero)
- Create: `apps/web/components/VideoHero.tsx`

### 6 Steps

**Step 1: `/videos` 改精选首页(分 shelf)**

不再展示一个大网格;改成几条「shelf」:
- 周热(`getCollectionBySlug('weekly-hot-videos', 'ranking')` 横向滚动,8 条)
- 最新(`getCollectionBySlug('latest-videos', 'ranking')` 横向滚动,8 条)
- 按分类入口(每个 video category 一行卡)
- 「浏览全部 →」CTA → `/videos/list`

**Step 2: 新建 `/videos/list/page.tsx`**

```tsx
export default async function VideosListPage({
  searchParams,
}: {
  searchParams: Promise<{ cat?: string; sort?: "latest" | "popular" | "liked" }>;
}) {
  const sp = await searchParams;
  const cat = sp.cat;
  const sort = sp.sort ?? "latest";
  const videos = await getPublishedVideos({
    categorySlug: cat,
    // sort logic — orderBy mapped from sort param
  });
  // ... 渲染筛选栏 + 网格
}
```

筛选栏:类目下拉 + 排序下拉(latest / popular / liked)+ 当前结果数。

**Step 3: 视频详情 v-hero**

把现有 video detail 的顶部改成 `v-hero`(gradient + 标题 + 时长 + tags),沿用现有 detail/short_desc 的 body。

**Step 4: 验证**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
pnpm --filter @ghome/web dev
# /videos → 看到 2 个 shelf
# /videos/list → 看到全部 20 条 + 类目筛选
# /videos/list?cat=fitness → 看到健身分类的视频
```

**Step 5: 提交**

```bash
git add 'apps/web/app/videos/page.tsx' \
        'apps/web/app/videos/list/page.tsx' \
        'apps/web/app/video/[slug]/page.tsx' \
        apps/web/components/VideoHero.tsx
git commit -m "feat(web): videos curated home + new /videos/list filter+sort page + video detail v-hero"
```

## Tricky Bits (T4)

1. **横向滚动 shelf 用 CSS `overflow-x:auto`** —— 不需要 carousel 库;原型也是这样
2. **sort 参数转 Prisma orderBy**:`latest → publishedDate desc`,`popular → viewsLabel`(注意 `viewsLabel` 是文案 string `'12.3K'`,不能直接 sort —— 改成 `publishedDate desc` 兜底,或留 P10 加 `viewsCount` numeric 列)。**MVP:`popular` 与 `liked` 都暂等于 `latest`**,加 fallback 注释
3. **类目筛选用现成 `getPublishedVideos({ categorySlug })`** —— 不用新加 query
4. **`/videos/list` revalidate**:跟列表页一致 60s
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 5 — 指南列表 row 化 + 详情 gd-hero

**Files:**
- Modify: `apps/web/app/guides/page.tsx`(列表从卡片改 row)
- Modify: `apps/web/app/guide/[slug]/page.tsx`(详情加 gd-hero)
- Create: `apps/web/components/GuideHero.tsx`
- Modify: `apps/web/components/GuideCard.tsx`(若仍想保留卡片样式,加 row variant;或新建 `GuideRow.tsx`)

### 5 Steps

**Step 1: 新建 GuideRow**

`apps/web/components/GuideRow.tsx`(server):

```tsx
import Link from "next/link";
import { gradCss } from "@/lib/gradients";
import { IconWhite } from "@/lib/icons";

export function GuideRow({ guide }: { guide: Guide }) {
  return (
    <Link href={`/guide/${guide.slug}`} className="guide-row">
      <div className="guide-row-cover" style={{ background: gradCss(guide.gradientKey) }}>
        <IconWhite name={guide.iconKey} size={24} />
      </div>
      <div className="guide-row-body">
        <div className="guide-row-meta">
          <span className="guide-row-cat">{guide.categoryLabel}</span>
          {guide.isHot && <span className="guide-row-hot">热门</span>}
        </div>
        <h4>{guide.title}</h4>
        <p>{guide.summary}</p>
        <div className="guide-row-foot">
          <span>{formatPublishDate(guide.publishedDate)}</span>
          <span>· 阅读 {formatReadMinutes(guide.readMinutes)}</span>
          <span>· {guide.viewsLabel}</span>
        </div>
      </div>
    </Link>
  );
}
```

**Step 2: 改 `/guides/page.tsx`** 用 GuideRow 替换 GuideCard。

**Step 3: GuideHero**

```tsx
<section className="gd-hero" style={{ background: gradCss(guide.gradientKey) }}>
  <div className="container">
    <span className="hero-tag">{guide.categoryLabel}{guide.isHot && " · 热门"}</span>
    <h1>{guide.title}</h1>
    <p>{guide.summary}</p>
    <div className="gd-meta">
      <span>{formatPublishDate(guide.publishedDate)}</span>
      <span>阅读 {formatReadMinutes(guide.readMinutes)}</span>
      <span>{guide.viewsLabel}</span>
    </div>
  </div>
</section>
```

**Step 4: 改 `/guide/[slug]/page.tsx`** 顶部用 GuideHero,body 渲染 `<MarkdownBody source={guide.bodyMd} />`。

**Step 5: 验证 + 提交**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
git add apps/web/components/GuideRow.tsx \
        apps/web/components/GuideHero.tsx \
        'apps/web/app/guides/page.tsx' \
        'apps/web/app/guide/[slug]/page.tsx'
git commit -m "feat(web): guide list row layout + guide detail gd-hero"
```

## Tricky Bits (T5)

1. **GuideRow 不是替换 GuideCard,而是新文件并行存在** —— 可能搜索结果页等其它地方还用 GuideCard 卡片样式。检查 grep 后决定
2. **Markdown 渲染保留** —— P5 的 `<MarkdownBody />` 不变
3. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 6 — 专题详情 hero-stats + creators inline

**Files:**
- Modify: `apps/web/app/topic/[slug]/page.tsx`
- Create: `apps/web/components/TopicHero.tsx`

### 4 Steps

**Step 1: TopicHero**

```tsx
<section className="topic-hero" style={{ background: gradCss(topic.coverKey ?? "g-brand") }}>
  <div className="container">
    <span className="hero-tag">专题</span>
    <h1>{topic.title}</h1>
    {topic.description && <p>{topic.description}</p>}
    <div className="topic-hero-stats">
      <div className="th-stat"><b>{topic.items.length}</b><span>条内容</span></div>
      <div className="th-stat"><b>{appCount}</b><span>App</span></div>
      <div className="th-stat"><b>{videoCount}</b><span>视频</span></div>
    </div>
  </div>
</section>
```

`appCount` / `videoCount` 在 server component 里 reduce items 算。

**Step 2: TopicCreatorsInline**(可选)

如果 topic 关联 creators(从 fixtures 配匹配),展示一行 inline 创作者头像。**MVP 不做匹配,直接展示固定 fixtures 中的前 3 位即可。**

**Step 3: 改 `/topic/[slug]/page.tsx`** 顶部用 TopicHero。

**Step 4: 验证 + 提交**

```bash
git add apps/web/components/TopicHero.tsx 'apps/web/app/topic/[slug]/page.tsx'
git commit -m "feat(web): topic detail hero with stats and creators inline"
```

## Tricky Bits (T6)

1. **专辑(album)同模板**:可选地把 `/album/[slug]/page.tsx` 也加同样 hero(P9 范围内或留 P10)
2. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 7 — About / Contact / Terms 重写(brand-grid 4 卡)

**Files:**
- Modify: `apps/web/app/about/page.tsx`
- Modify: `apps/web/app/contact/page.tsx`
- Modify: `apps/web/app/terms/page.tsx`
- Create: `apps/web/components/BrandGrid.tsx`

### 5 Steps

**Step 1: BrandGrid 通用组件**

```tsx
interface BrandCard {
  iconKey: string;
  title: string;
  desc: string;
  cta?: { href: string; label: string };
}

export function BrandGrid({ cards }: { cards: BrandCard[] }) {
  return (
    <div className="brand-grid">
      {cards.map((c, i) => (
        <div key={i} className="brand-card">
          <div className="brand-card-ic"><IconWhite name={c.iconKey} size={28} /></div>
          <h3>{c.title}</h3>
          <p>{c.desc}</p>
          {c.cta && <Link href={c.cta.href} className="brand-cta">{c.cta.label} →</Link>}
        </div>
      ))}
    </div>
  );
}
```

**Step 2: about page** —— brand-hero + 4 卡(我们做什么 / 我们的价值 / 我们的承诺 / 联系我们)。

**Step 3: contact page** —— brand-hero + 3 邮箱卡 + 1 收录标准卡:

```tsx
const cards = [
  { iconKey: "i-handshake", title: "商务合作", desc: "投放、推广、品牌合作", cta: { href: "mailto:[邮箱已脱敏]", label: "[邮箱已脱敏]" } },
  { iconKey: "i-pencil",    title: "内容投稿", desc: "App / 视频 / 指南推荐", cta: { href: "mailto:[邮箱已脱敏]", label: "[邮箱已脱敏]" } },
  { iconKey: "i-briefcase", title: "BD 接洽", desc: "广告合作、流量置换",    cta: { href: "mailto:[邮箱已脱敏]",      label: "[邮箱已脱敏]" } },
];
const standards = [
  { iconKey: "i-check", title: "免费收录标准", desc: "原创内容、合规上架、明确受众标签、隐私安全合格" },
];
```

**Step 4: terms page** —— brand-hero + 4 卡(隐私 / 用户协议 / 内容标准 / 免责声明),内容沿用原 fixtures。

**Step 5: 验证 + 提交**

```bash
git add apps/web/components/BrandGrid.tsx \
        apps/web/app/about/page.tsx \
        apps/web/app/contact/page.tsx \
        apps/web/app/terms/page.tsx
git commit -m "feat(web): about/contact/terms upgraded to brand-grid 4-card layout"
```

## Tricky Bits (T7)

1. **3 个邮箱真实 mailto: 链接** —— 浏览器会调起本地邮件客户端,这是 OK 的
2. **图标 `i-handshake` `i-pencil` `i-briefcase` 等若不存在** —— 在 `apps/web/lib/icons.tsx` 的 SvgSprite 加新 symbol(从原型 `<svg style="display:none">` 块抓 path),或退化用现有图标
3. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 8 — 移动端抽屉导航

**Files:**
- Modify: `apps/web/components/Header.tsx`(加汉堡 icon + 触发 drawer)
- Create: `apps/web/components/MobileDrawer.tsx`(client)

### 5 Steps

**Step 1: MobileDrawer client 组件**

```tsx
"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

const NAV = [...]; // 同 Header.tsx 的 NAV 数组

export function MobileDrawer() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      <button className="nav-toggle" onClick={() => setOpen(true)} aria-label="打开菜单">
        <span /><span /><span />
      </button>
      <div className={`mobile-drawer-mask ${open ? "open" : ""}`} onClick={() => setOpen(false)} />
      <aside className={`mobile-drawer ${open ? "open" : ""}`}>
        <div className="md-head">
          <span>Ghome</span>
          <button className="md-close" onClick={() => setOpen(false)} aria-label="关闭">×</button>
        </div>
        <nav className="md-nav">
          {NAV.map(n => (
            <Link key={n.href} href={n.href} onClick={() => setOpen(false)}>{n.label}</Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
```

**Step 2: 改 Header.tsx** —— 桌面端保留现有 inline nav,移动端隐藏 inline nav(`@media (max-width: 768px)` 用 CSS),改显 `<MobileDrawer />`。

**Step 3: 移动端样式确认** —— `T1` 已 port `nav-toggle` `mobile-drawer*` 全部 CSS,Step 1 直接用。

**Step 4: 浏览器测试** —— Chrome devtools 切 iPhone 视口,看汉堡按钮 + 抽屉切换。

**Step 5: 提交**

```bash
git add apps/web/components/Header.tsx apps/web/components/MobileDrawer.tsx
git commit -m "feat(web): mobile drawer navigation with hamburger toggle"
```

## Tricky Bits (T8)

1. **Drawer 打开锁住 body 滚动**:`document.body.style.overflow = "hidden"`,关闭恢复
2. **点击外部 mask 关闭**:`onClick={() => setOpen(false)}` 在 `.mobile-drawer-mask` 上
3. **链接点击后自动关闭**:每个 `<Link onClick={() => setOpen(false)}>`
4. **桌面端不应渲染 drawer**(避免 SEO异常验证 噪音):用 CSS `@media (min-width: 769px) { .nav-toggle, .mobile-drawer, .mobile-drawer-mask { display: none } }`
5. **如果 git commit 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Task 9 — End-to-end smoke + tag p9-design-refresh

**Files:** 无新文件;只跑冒烟 + 打 tag。

### 5 Steps

**Step 1: 全量本地 CI 等价命令**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
pnpm install
pnpm --filter @ghome/db db:migrate:deploy
pnpm --filter @ghome/db db:seed
pnpm --filter @ghome/db typecheck
pnpm --filter @ghome/db test
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin lint
pnpm --filter @ghome/admin build
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web lint
pnpm --filter @ghome/web build
```

全过才进 Step 2。

**Step 2: UI 视觉冒烟(对照 `docs/ghome-20260509.html` 用浏览器并排)**

```bash
pnpm --filter @ghome/web start &
```

| 路由 | 检查点 |
|---|---|
| `/` | brand-hero 紫色渐变 + 搜索框 + 联想下拉(输「健身」200ms 后下拉)+ 推荐 / 视频 / 专题 / 创作者 / 评论 |
| `/app/broconnect` | app-hero gradient + 6 格 info(评分 / 用户 / 平台 / 大小 / 年龄 / 语言)+ 安装步骤 + 注意事项 + 桌面悬停下载出 QR |
| 切 iPhone UA | App 详情上「前往 App Store」单按钮,QR 隐藏 |
| 切 Android UA | App 详情上「前往下载」单按钮,QR 隐藏 |
| `/videos` | shelf 1(周热)+ shelf 2(最新)+ 类目入口 + 「浏览全部」 |
| `/videos/list?cat=fitness&sort=latest` | 健身类视频网格 |
| `/video/v01` | v-hero gradient + 详情 |
| `/guides` | 改 row 布局,5 行 |
| `/guide/choose-app` | gd-hero 紫色 + 元数据 + Markdown body |
| `/topic/dating-tips` | topic-hero + hero-stats(3 个数字格) |
| `/about` | brand-hero + 4 卡 brand-grid |
| `/contact` | 3 邮箱卡 + 1 收录标准卡 |
| `/terms` | 4 卡 |
| iPhone 视口 / | 汉堡按钮可见,点开抽屉 |
| `/sitemap.xml` `/robots.txt` | 200 |
| `/api/search/suggest?q=健身` | JSON 三类截断 5 条 |

**Step 3: 把冒烟结果记到 commit message**

```bash
# 已经 commit 各 task,本步无需新 commit
git status  # should be clean
```

**Step 4: 打 tag**

```bash
git tag p9-design-refresh
git tag --list 'p*'
```

**Step 5: 推 tag(用户决定)**

```bash
# git push origin p9-design-refresh   # 等用户授权
```

## Tricky Bits (T9)

1. **冒烟需要 docker compose 起来**
2. **OS UA 切换在 Chrome devtools 可做**:Sources → Sensors / Customize → User agent
3. **若汉堡按钮在桌面也显示** → CSS media query 写漏,回 T1 检查
4. **若 QR 在 iPhone UA 还显示** → CSS body.os-ios 选择器漏写,回 T1 检查
5. **如果 git tag 被 permission rule 阻塞**:报 DONE_WITH_CONCERNS

---

## Final 验收清单(P9 整体)

- [ ] `apps.age` `apps.dev` `apps.lang` 字段加入 schema + 迁移 + seed + admin 编辑器
- [ ] 58 个新 CSS class 全部 port 到 `apps/web/app/globals.css`
- [ ] `/` 首页 brand-hero + 搜索联想下拉(200ms debounce,跨 App / 视频 / 指南 3 类)+ 热搜词 chips
- [ ] `/app/[slug]` app-hero + 6 格 info-cell(含 age/lang)+ 安装步骤 + OS-aware download CTA + 桌面 QR 气泡
- [ ] `/videos` 改成精选首页(2 shelf)
- [ ] `/videos/list?cat=...&sort=...` 新增,筛选 + 排序
- [ ] `/video/[slug]` v-hero
- [ ] `/guides` row 布局
- [ ] `/guide/[slug]` gd-hero
- [ ] `/topic/[slug]` topic-hero + hero-stats
- [ ] `/about` `/contact` `/terms` brand-grid 4 卡
- [ ] `/contact` 3 个 mailto 邮箱 + 收录标准卡
- [ ] 移动端汉堡按钮 + 抽屉导航
- [ ] OS 检测 client 组件(`body.os-android` / `os-ios` / `os-desktop`)
- [ ] QR 码 SSR 生成(`qrcode-svg`)— 桌面端可见
- [ ] Rankings 默认 publish 状态简化为 2 条(weekly-hot-videos + latest-videos)
- [ ] CI(typecheck / lint / build / test)全绿
- [ ] tag `p9-design-refresh` 落在 main HEAD
- [ ] 视觉与 `docs/ghome-20260509.html` 几乎一致(对比浏览器并排)

---

**P9 完成 ⇒ 视觉层升级到高保真原型。**

下一步选项(由用户决定):
1. **真实视频封面图上传管线**(P10):object storage(R2/S3)+ admin 上传 + web 展示真图替换 gradient 占位
2. **真实 APK 文件托管**:运营在 admin 把 redirect targetUrl 设成 APK 直链或 store URL
3. **联系页表单后端**:把 mailto: 改成提交到 `/api/contact-form` → 转邮件 / 写 leads 表
4. **评论 / 评分 / 用户登录 / UGC**:产品形态扩展,需要重新走 brainstorm + spec
5. **Rankings 自动化**(基于 click_events 重排序)
6. **og:image 生成器** / Twitter Cards / JSON-LD
