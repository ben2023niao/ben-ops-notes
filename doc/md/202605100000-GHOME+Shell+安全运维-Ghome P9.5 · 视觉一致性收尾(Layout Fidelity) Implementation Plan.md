---
id: "doc-1780d88dd0cf"
title: "Ghome P9.5 · 视觉一致性收尾(Layout Fidelity) Implementation Plan"
date: "2026-05-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p9.5-layout-fidelity.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p9.5-layout-fidelity.md"
sourceSha256: "3574f9bb59ccdbe02cfb63ee688d66db63577e5b309b0fa5adf87021bfa6ef3f"
sourceSystem: "project-doc"
---

# Ghome P9.5 · 视觉一致性收尾(Layout Fidelity) Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605100000-GHOME%2BShell%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4-Ghome%20P9.5%20%C2%B7%20%E8%A7%86%E8%A7%89%E4%B8%80%E8%87%B4%E6%80%A7%E6%94%B6%E5%B0%BE%28Layout%20Fidelity%29%20Implementation%20Plan.md)

> 整理日期：2026-05-10 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** P9 把原型的 58 个 CSS class 全 port 到 `apps/web/app/globals.css`,但 10 个页面的 React markup 没跟着升级 —— 类齐全但页面不用。本阶段做 markup 重组让真实呈现与 `docs/ghome-20260509.html` 高保真原型对齐。**0 个新数据模型 / 0 个新路由 / 0 个新 CSS 类**,纯 markup + 少量小组件。

完成后,以下 10 处差距全部闭合(按严重度):

**High (5)**
1. `/guide/[slug]` 单栏 → 双栏(右侧 sticky TOC + author-card + 更多指南 + 推荐 App)+ 上下篇卡片化
2. `/categories` topic 卡片 → 「每类一段」`.cat-block` + 4 视频预览
3. `/search` 3 组 → 7 组(+创作者 / 专题 / 分类 / 标签)+ `<mark>` 关键词高亮 + 热搜词空态
4. `/apps` `/guides` `/topics` 三个列表页头部 → `.app-hero` 紫色 + `.hero-stats` 数字格
5. `/app/[slug]` 单栏 → 加右 `<aside>` 三个 side-card(相关专题 / 热门标签 / 使用指南)

**Medium (4)**
6. `/category/[slug]` 加 `.cat-head` 主题色 hero + 标签云侧栏
7. `/videos/list` `<select>` → `.filter-tabs` chip
8. `/video/[slug]` `.vdx-cover` 加时长角标 + 右侧 extras
9. `/topics` TopicCard 加 `.meta` 底部行

**Low (1)**
10. `/tag/[slug]` 加 `.toolbar` 计数

## Architecture

- **新组件全 server,除 `<GuideToc>`**(必须 client,因为要在浏览器内根据 markdown 渲染后的 `<h2>` 抽 anchors;SSR 拿不到渲染后 DOM)
- **共享 `<HeroWithStats>`**:封装 `.app-hero` + h1 + p + `.hero-stats` cells(数据传 `stats: {label, value}[]`),三个列表页共用
- **`/categories` 的 cat-block 不需要分类详情数据**,只需 `getPublishedVideos({ categorySlug, limit: 4 })` 拿每类 4 条预览。Promise.all 6 类并发查
- **`/search` 扩 4 类**:`searchAll` 已有 apps/videos/guides;扩展返回 `creators/topics/categories/tags`(creators 来自 fixtures,其它走现有 lib/db 函数 + ILIKE 字段)
- **`<mark>` 关键词高亮**:server 端 `escapeHtml + replaceAll(query)` 封装为 `<mark>q</mark>`,转回 React 时用 `dangerouslySetInnerHTML`(安全 — 输入已 escape)
- **`<GuideToc>` client 组件**:`useEffect` 后查 `document.querySelectorAll('.md-body h2')` 抽出 id+text,渲染列表;同时 `IntersectionObserver` 跟踪当前可视 heading 高亮

## Spec / 原型引用

- 主参考:[`docs/ghome-20260509.html`](../../ghome-20260509.html)
- P9 plan:[`2026-05-10-ghome-p9-design-refresh.md`](2026-05-10-ghome-p9-design-refresh.md)
- 原型对应函数(用 `grep -n "function render" docs/ghome-20260509.html` 找行号):
  - `renderHome` `renderAppsList` `renderAppDetail` `renderVideoListPage` `renderVideoDetail` `renderGuidesList` `renderGuideDetail` `renderTopicsList` `renderTopicDetail` `renderCategoriesList` `renderCategoryDetail` `renderTagDetail` `renderSearch` `renderSuggest`

## 不做(明确范围外)

- 真实视频封面图 / APK 上传(P10 #1 #2)
- 评论 / UGC / 用户登录(P10 #6)
- og:image 生成器(P10 #5)
- E2E 测试(P10 #9)
- i18n(P10 #7)
- 任何后端 / schema 变化

## File Structure(P9.5 末态)

```
apps/web/
├─ app/
│  ├─ apps/page.tsx                                    # T1 改:HeroWithStats
│  ├─ guides/page.tsx                                  # T1 改:HeroWithStats
│  ├─ topics/page.tsx                                  # T1 改:HeroWithStats
│  ├─ categories/page.tsx                              # T1 改:cat-block 4 预览
│  ├─ guide/[slug]/page.tsx                            # T2 大改:two-col + side-cards
│  ├─ app/[slug]/page.tsx                              # T3 改:加右 aside
│  ├─ video/[slug]/page.tsx                            # T3 改:duration 角标 + 右 extras
│  ├─ category/[slug]/page.tsx                         # T3 改:cat-head + 标签云
│  ├─ videos/list/page.tsx                             # T4 改:filter-tabs chips
│  ├─ search/page.tsx                                  # T4 改:7 组 + mark 高亮
│  └─ tag/[slug]/page.tsx                              # T4 改:toolbar 计数
├─ components/
│  ├─ HeroWithStats.tsx                                # T1 新:共享 hero
│  ├─ CatBlock.tsx                                     # T1 新:每类一段
│  ├─ GuideToc.tsx                                     # T2 新:client TOC
│  ├─ AuthorCard.tsx                                   # T2 新:作者卡
│  ├─ SideCard.tsx                                     # T2/T3 新:侧栏卡通用容器
│  ├─ AppDetailAside.tsx                               # T3 新:App 详情右栏
│  ├─ VideoDetailAside.tsx                             # T3 新:视频详情右栏
│  ├─ TagCloud.tsx                                     # T3 新:标签云
│  ├─ FilterTabs.tsx                                   # T4 新:chip 形式分类筛选
│  └─ TopicCard.tsx                                    # T4 改:加 meta 行
└─ lib/
   └─ search-extras.ts                                 # T4 新:扩展 search 到 7 类 + mark 高亮 helper
```

新组件 ~10,改动 ~12 个页面文件。

## Conventions(整个 P9.5 共享)

- **服务端组件优先**,仅 `<GuideToc>` 是 client(`useEffect` + `IntersectionObserver`)
- **HeroWithStats props**:`{ tag: string; title: string; subtitle: string; stats: { label: string; value: string | number }[] }`
- **CatBlock props**:`{ category: Category; videos: Video[] }`
- **SideCard 通用容器**:`{ title, children }` — 内容自由
- **`<mark>` 高亮**:`apps/web/lib/search-extras.ts` 的 `highlightHtml(text, query)` 函数;先 `escapeHtml(text)` 再 `replaceAll(escapedQuery, '<mark>$&</mark>')`,return safe HTML 字符串。React 端用 `dangerouslySetInnerHTML`,安全因为已 escape
- **TOC anchor**:`MarkdownBody` 已用 `react-markdown` + `remark-gfm`,自动给 `<h2>` 加 id?需验证;若没,client 端 useEffect 后用 slug 算法补 id 再抽
- 提交风格:Conventional Commits,每 task 末尾 commit。如果 git commit 被 permission rule 阻塞,报 DONE_WITH_CONCERNS

## 前置假设

- P9 已完成,`p9-design-refresh` 标签存在
- web globals.css 已有所有需要的 class(spec recon agent 验证 0 missing)
- web 服务可在 3000 端口跑 production
- Postgres + admin + web 本地 dev 环境正常

---

## Task 1 — 三个列表页头部 + /categories cat-block

**Files:**
- Create: `apps/web/components/HeroWithStats.tsx`
- Create: `apps/web/components/CatBlock.tsx`
- Modify: `apps/web/app/apps/page.tsx`
- Modify: `apps/web/app/guides/page.tsx`
- Modify: `apps/web/app/topics/page.tsx`
- Modify: `apps/web/app/categories/page.tsx`

### Steps

1. 写 `<HeroWithStats>` 组件:渲染 `.app-hero` + `.hero-tag` + h1 + lead p + `.hero-stats` (`.hero-stat` 内 `.v` 大数 + `.l` 小标签)。stats 是必传数组(2-4 个)。

2. `/apps` 改:计算 `getPublishedApps()` 总数 / `getAppCategories()` 数。stats:`{App 总数, 分类数, 平均评分}`(平均评分要 `apps.reduce` 算)。

3. `/guides` 改:`getPublishedGuides()` 总数 / 分类数(沿用 P9 GUIDE_CATS hardcoded 4) / 累计阅读量(可从 `viewsLabel` 解析数字 sum)。stats:`{指南总数, 分类数, 累计阅读}`。

4. `/topics` 改:`getCollectionsByKind('topic')` 总数 / 累计涉及 items 数 / 创作者数。stats:`{专题总数, 收录视频, 涉及创作者}`。

5. 写 `<CatBlock>` 组件:接收 `category: Category, videos: Video[]`。布局:左 `.cat-dot` 圆形主题色 + 右 `.cat-block-head`(分类名 + `.cat-count` 视频数 + 「查看更多 →」link 到 `/category/{slug}`)+ 下方 `.v-grid` 4 个 `<VideoCard>`。

6. `/categories` 改:`Promise.all` 6 个分类的预览(各 4 条);for-each 渲染 `<CatBlock>`。

7. typecheck + build + smoke(curl 4 个页面看 hero-stats / cat-block / cat-dot 类是否在 HTML 里)。

8. Commit: `feat(web): HeroWithStats on apps/guides/topics + cat-block layout on /categories`

### Tricky Bits (T1)

1. 平均评分:`apps.rating` 是 string 如 `"4.6"`,要 `parseFloat` 后求平均,显示 `.toFixed(1)`
2. 累计阅读:`guides.viewsLabel` 是文案如 `"12.3K"`,需要简单解析(写个 helper `parseLabelNumber("12.3K") => 12300`)
3. 累计创作者数:topics 里没直接关联 creators;用 fixtures `CREATORS.length` 兜底
4. CatBlock 里的 `.cat-dot` 主题色:已有 globals.css 规则;若没设 `style={{ background: cat.label-derived-color }}` 就用 `var(--primary)` 默认
5. 使用 `Promise.all` 让 6 个 category 的视频查询并行,**不要顺序 await**

---

## Task 2 — `/guide/[slug]` 双栏大改

**Files:**
- Create: `apps/web/components/GuideToc.tsx` (client)
- Create: `apps/web/components/AuthorCard.tsx` (server)
- Create: `apps/web/components/SideCard.tsx` (server,通用)
- Modify: `apps/web/app/guide/[slug]/page.tsx`
- Modify: `apps/web/components/MarkdownBody.tsx`(若需要给 h2 加 id)

### Steps

1. 写 `<GuideToc>` client 组件:
   - `"use client"`
   - useEffect:从 `document.querySelectorAll('.md-body h2[id]')` 抽出 `{ id, text }` 列表
   - 用 `IntersectionObserver` 监听各 h2,active heading 高亮
   - 渲染 `<aside class="toc">` + sticky 定位

2. 验证 / 修改 `MarkdownBody.tsx`:确认 `react-markdown` + `remark-gfm` 自动给 h2 加 slug-id;若没,加 `rehype-slug` 或者手写 plugin。

3. 写 `<AuthorCard>`:固定 hardcoded 作者(Ghome 编辑团队)的 `.author-card` 渲染。

4. 写 `<SideCard>` 通用:`{ title, children }` → `<aside class="side-card"><h5>{title}</h5>{children}</aside>`。

5. 改 `/guide/[slug]/page.tsx`:
   - 改成 `.two-col` 布局(左 main 右 aside)
   - 左:`gd-hero` + Markdown body + `.lead-quote` 块包前 1-2 段?(可选)+ `.pn-nav` 上下篇 cards
   - 右:`<GuideToc />` (sticky) + `<AuthorCard />` + `<SideCard title="更多指南">` 推 5 篇 + `<SideCard title="推荐 App">` 推 3 个

6. 把现有的 prev/next 普通 link 改成 `.pn-nav` 双卡布局(globals.css 应该有 `.pn-nav` 和 `.pn-card` — 若没就用 inline style 兜底)。

7. typecheck + build + smoke。

8. Commit: `feat(web): /guide/[slug] two-col with TOC + author-card + side-cards + pn-nav`

### Tricky Bits (T2)

1. **TOC client 动态注入**:server 渲染 markdown 后客户端才能拿到 DOM。useEffect 内查询 + setState。SSR 时 TOC 是空容器
2. **`react-markdown` h2 id 添加**:默认不加 id;用 `rehype-slug` plugin 是最干净方案。需要 `pnpm add rehype-slug`
3. **Sticky TOC**:`position: sticky; top: 80px` (header 高度)。globals.css 应该有 `.toc { position: sticky }`
4. **IntersectionObserver 性能**:不要给所有 h2 单独 observer,用一个 observer + multiple targets
5. **`.lead-quote` 块**:从 markdown body 第一段自动抽,或者手动在 admin guide 编辑器加;**MVP 简化** — 不做 lead-quote 自动抽取,仅当 guide.bodyMd 第一行是 `> ...` 引用块时,react-markdown 自动把 blockquote 渲染对了 — 这里不动
6. **`.pn-nav` 缺类时 fallback**:globals.css 有 `.pn-nav` 在 354 行?若没,加几行内联样式

---

## Task 3 — App / Video 详情右栏 + Category 主题色 hero

**Files:**
- Create: `apps/web/components/AppDetailAside.tsx`
- Create: `apps/web/components/VideoDetailAside.tsx`
- Create: `apps/web/components/TagCloud.tsx`
- Modify: `apps/web/app/app/[slug]/page.tsx`
- Modify: `apps/web/app/video/[slug]/page.tsx`
- Modify: `apps/web/app/category/[slug]/page.tsx`

### Steps

1. 写 `<AppDetailAside>`:接收 `app: AppWithRels`,渲染 3 个 SideCard:
   - 「相关专题」:查 collections kind=topic 含此 app 的 ≤3 个
   - 「热门标签」:此 app 的 tags + 跨 tags 的相关 apps 推荐
   - 「使用指南」:推 ≤3 篇相关 guides(按 categorySlug 大致匹配)

2. 写 `<VideoDetailAside>`:类似但内容不同
   - 「相关专题」:topics 含此 video
   - 「推荐 App」:同分类下 4 个 apps
   - 「相关视频」:已有 `sameCatVideos` — 复用即可

3. 写 `<TagCloud>`:接收 `tags: { slug, label }[]`,渲染 `.tag-cloud` 含 `<Link>` 圆角 chips 列表。

4. 改 `/app/[slug]`:外层加 `.two-col`,左原内容,右 `<AppDetailAside />`。

5. 改 `/video/[slug]`:类似;另外给 `.vdx-cover` 加 `<span class="dur">{video.duration}</span>` 时长角标(原型 vdx-cover 内有 `.dur` 类)。

6. 改 `/category/[slug]`:
   - 顶部 `.cat-head` 用 cat 名首字母 + 渐变背景(`coverCss(cat.slug)`)
   - 下方 `.cat-extras` 两栏:左是 cat 简介(`cat.description`)+ 右是 `<TagCloud>` 与该分类视频相关的 top tags

7. typecheck + build + smoke。

8. Commit: `feat(web): app/video detail asides + category cat-head with tag cloud`

### Tricky Bits (T3)

1. **「相关专题」查询**:Prisma 没现成 reverse 查询,用 `prisma.collection.findMany({ where: { items: { some: { appId: app.id } } } })`
2. **「使用指南」推荐**:简单按 `guide.categorySlug == "app"` 过滤;若 guide 与 app 没强关联,就拿前 3 篇 hot 指南
3. **TagCloud**:复用现有 `.chips` + `<TagPill>` 即可,不必新做
4. **vdx-cover 的 `.dur` 角标**:globals.css 应该已有 `.dur { position: absolute; bottom: 8px; right: 8px; ... }`
5. **`.cat-head` 主题色**:基于 cat.slug 算 coverCss(直接用 P9 已建好的 `coverCss('fitness')` 等)
6. **`.cat-extras` 两栏**:CSS grid 2 cols + responsive

---

## Task 4 — `/search` 7 组 + 高亮 + filter-tabs + topic card meta

**Files:**
- Create: `apps/web/lib/search-extras.ts` (扩 search + mark 高亮 helper)
- Create: `apps/web/components/FilterTabs.tsx` (chip 形分类筛选)
- Modify: `apps/web/app/search/page.tsx`
- Modify: `apps/web/app/videos/list/page.tsx` (替换 select 为 chip)
- Modify: `apps/web/components/TopicCard.tsx` (加 meta 底部行)
- Modify: `apps/web/app/tag/[slug]/page.tsx` (加 toolbar 计数)

### Steps

1. 写 `lib/search-extras.ts`:
   - `escapeHtml(s: string): string` — 转 `<>&"'`
   - `highlightHtml(text: string, query: string): string` — escape text + insert `<mark>q</mark>`(case-insensitive)
   - `searchAllExtended(q)` — 调 `searchAll` 拿 apps/videos/guides,再加查 creators(fixtures filter)+ topics + categories + tags(走 lib/db 拿到所有,client filter by ILIKE label)。返回 7 类。

2. 改 `/search/page.tsx`:
   - 调 `searchAllExtended` 而非 `searchAll`
   - 渲染 7 个 `.sr-group` + `.sr-group-head` 含 count pill
   - 每条命中的 title 用 `dangerouslySetInnerHTML` + `highlightHtml(...)`
   - 空态:`.sr-empty` 含 hot-query chips(复用 HOT_QUERIES)
   - 创作者用 `.sr-creator-grid` + `.sr-creator-item`

3. 写 `<FilterTabs>` 组件:接收 `{ items: { value, label, href }[], current: string }`,渲染 `.filter-tabs` chip 行,active chip 高亮。

4. 改 `/videos/list`:把 `<select name="cat">` 替换成 `<FilterTabs>`(chip 风);提交方式改 Link 直接导航(每个 chip 是个 Link 到 `/videos/list?cat=...`)。

5. 改 `<TopicCard>`:在底部加 `.meta` 行 `🎬 N 视频 →`(N 来自 collection.items length 但 TopicCard 现在不接收 items… 要传额外 prop `videoCount: number` 或者直接加 `_count.items`)。

6. 改 `/tag/[slug]`:加 `.toolbar` + 「共 N 条带「{tag}」标签的视频」prose。

7. typecheck + build + smoke。

8. Commit: `feat(web): search 7 groups with highlight + filter-tabs chips + topic card meta + tag toolbar`

### Tricky Bits (T4)

1. **`<mark>` XSS 安全**:`escapeHtml` 必须先于 mark 注入。`replaceAll` 用全局 case-insensitive regex
2. **case-insensitive replaceAll**:`new RegExp(escapedQuery, 'gi')` 的全局 + i flag
3. **creators 不在 DB**:从 `fixtures/creators.ts` 取,在内存中 filter by name/bio ILIKE q
4. **categories / tags 命中**:`prisma.category.findMany({ where: { label: { contains: q } } })` + `prisma.tag.findMany({ where: { OR: [{ label: { contains: q } }, { slug: { contains: q } }] } })`
5. **TopicCard meta**:简单方法是 prop 传 `videoCount`,在调用方算;复杂方法是 lib/db 改 `getCollectionsByKind` include `_count: { items: true }`。**用复杂方法** —— 一次性升级所有调用方
6. **FilterTabs 在 SSR**:每个 chip 是 `<Link href>`,active 状态由 server 端比较 current

---

## Task 5 — End-to-end smoke + tag p9.5-layout-fidelity

**Files:** 无新文件;只跑冒烟 + 打 tag。

### Steps

1. 全套本地 CI 等价命令:
   ```bash
   docker compose up -d
   pnpm install
   pnpm --filter @ghome/db db:migrate:deploy
   pnpm --filter @ghome/db typecheck
   pnpm --filter @ghome/db test
   pnpm --filter @ghome/admin typecheck
   pnpm --filter @ghome/admin lint
   pnpm --filter @ghome/admin build
   pnpm --filter @ghome/web typecheck
   pnpm --filter @ghome/web lint
   pnpm --filter @ghome/web build
   ```

2. UI 视觉冒烟,逐一访问每个改过的页面,确认对应 class 都在 rendered HTML 中:
   - `/apps` → `class="app-hero"` + `class="hero-stats"` + 3 个 `class="hero-stat"`
   - `/guides` → 同上
   - `/topics` → 同上
   - `/categories` → 6 个 `class="cat-block"` + `class="cat-dot"` + `class="cat-count"`
   - `/guide/choose-app` → `class="two-col"` + `class="toc"` + `class="author-card"` + `class="side-card"` + `class="pn-nav"`
   - `/app/broconnect` → `class="two-col"` + 至少 3 个 `class="side-card"`
   - `/video/v01` → `class="dur"` 时长角标 + 右侧 extras
   - `/category/fitness` → `class="cat-head"` + `class="cat-extras"` + `class="tag-cloud"`
   - `/videos/list` → `class="filter-tabs"` + 多个 `class="filter-tab"`
   - `/search?q=健身` → 多个 `class="sr-group"` + `<mark>` + `.sr-creator-grid`
   - `/tag/lgbtq` → `class="toolbar"` + 计数 prose

3. 打 tag:
   ```bash
   git tag p9.5-layout-fidelity
   ```

## Final 验收清单(P9.5 整体)

- [ ] `<HeroWithStats>` 复用于 /apps /guides /topics 三个列表页
- [ ] `/categories` 显示 6 个 cat-block
- [ ] `/guide/[slug]` 双栏 + TOC + author-card + 2 side-cards + pn-nav
- [ ] `/app/[slug]` 加右 aside 三 side-cards
- [ ] `/video/[slug]` 加 .dur 角标 + 右 extras
- [ ] `/category/[slug]` 顶部 cat-head + 标签云
- [ ] `/videos/list` filter-tabs chips 取代 select
- [ ] `/search` 7 组(apps / videos / guides / creators / topics / categories / tags)+ `<mark>` 高亮
- [ ] TopicCard 底部加 meta 行
- [ ] /tag/[slug] 加 toolbar 计数
- [ ] CI(typecheck + lint + build + test)全绿
- [ ] tag p9.5-layout-fidelity 在 main HEAD

**P9.5 完成 ⇒ 视觉与 docs/ghome-20260509.html 高度一致。** 接着进 P10 路线图选项 A/B/C/D。
