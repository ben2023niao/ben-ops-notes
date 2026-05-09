---
id: "doc-eac8739d5b3c"
title: "Ghome P10a · 收尾(Path A from P10 Roadmap) Implementation Plan"
date: "2026-05-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Docker", "监控告警", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p10a-finishing.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p10a-finishing.md"
sourceSha256: "0154b60d115e3ab68649cf40561c6f4aa2dc1f04b98c9a6a82187dcadbb7bf3e"
sourceSystem: "project-doc"
---

# Ghome P10a · 收尾(Path A from P10 Roadmap) Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-10-ghome-p10a-finishing.md`

> 整理日期：2026-05-10 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this plan task-by-task.

**Goal:** P10 路线图选项 A —— 完成 A 档 5 项纯代码 + B 档 3 项本地桩。共 8 项工作,涵盖 P10 完整范围 80%,不依赖外部凭证(R2 / SES / Resend 等),不触发产品方向决策。

完成后 Ghome 在以下方面到位:
- 视频/App 有真实 numeric 计数(`views_count` `likes_count` `users_count`),榜单按计数自动重排
- 每个 detail 页有动态 og:image(brand-hero gradient + 标题 + Ghome logo)+ JSON-LD 结构化数据 + Twitter Cards
- Playwright E2E 覆盖关键流程(20+ 用例)
- redirect 列表支持批量勾选 + 批量切 disabled,APK URL 加严校验(白名单域名)
- i18n 脚手架就绪(next-intl,中文默认,英文/日文等留扩展点)
- 视频封面图可在 admin 上传(本地 `/public/uploads/videos/`,生产换 R2 即可)
- 联系页表单提交到 `contact_submissions` 表,admin 列表查看 + 状态管理

## Architecture

- **数据层一次性迁移**:T1 一个手写 migration 加 3 处变更:
  1. `videos.views_count` + `videos.likes_count` int(从 `views_label` `likes_label` 解析回填)
  2. `apps.users_count` int(从 `users_label` 解析回填)
  3. 新表 `contact_submissions`(id / email / name / subject / body / status enum / created_at / replied_at / replied_by)

- **自动榜单重排**:扩展 P7 已有的 `aggregateClickEvents` cron 任务,改名 `runScheduledJobs`,增加 `recomputeRankings()` 步骤 —— 按 numeric 列重排 collection_items 的 position(沿用 P1 的 DEFERRABLE UNIQUE 约束保证中间态)

- **og:image 用 `@vercel/og`**:Edge runtime,SSR 时给每个 detail 路由暴露 `opengraph-image.tsx`(Next 15 约定)。SVG 渲染品牌 gradient + 大标题 + Ghome 字标。**不接外部图片服务**

- **JSON-LD**:每个 detail 页加 `<script type="application/ld+json">`(server component 直渲),按 schema.org 类型:Article / VideoObject / SoftwareApplication / WebPage

- **Playwright**:配 `pnpm --filter @ghome/web add -D @playwright/test`;新建 `apps/web/e2e/`;CI 加 `playwright test --project=chromium` 步骤

- **redirect 批量**:`/redirects` 页加 client component `<RedirectBulkBar>` (checkbox 选区 + Disable/Enable 按钮);后端 `PATCH /api/redirects/bulk` 走 `prisma.$transaction` 批量 update

- **APK 加严**:`packages/db/src/lib/url-policy.ts` 加可选选项 `requireApk?: boolean`,启用时检查 URL 末尾 `.apk` 或来自白名单(Google Play / App Store / Galaxy Store)

- **i18n 脚手架**:`next-intl` v4,改 `apps/web/app/[locale]/...` 路由结构,默认 `zh-CN`,留 `en` / `ja` 占位空文件;**不真实翻译**,P11+ 决定语种再补译文

- **视频封面上传**:admin video 编辑器加 `<input type="file" accept="image/*">`;server action 写到 `apps/web/public/uploads/videos/{slug}.{ext}`(本地 dev 走文件系统);新增 `videos.cover_image_url text?` 字段;web `VideoCard`/`VideoHero` 优先用真实图,fallback 现有 `coverKey` gradient

- **APK URL 加严**(无文件托管):redirect 编辑器在 `validateForWrite(url, { requireApk: true })` 时强校验 — 不通过则 throw

- **联系表单**:`/contact` 表单 → server action → `prisma.contactSubmission.create`;admin 加 `/contact-submissions` 列表 + 详情页 + 状态切换(`pending → read → replied → spam`)。**不发邮件**,运营在 admin 看板处理

## Tech Stack

新依赖:
- `@vercel/og ^0.6` (web)
- `next-intl ^4` (web)
- `@playwright/test ^1.49` (web devDep)
- `negotiator` + `@formatjs/intl-localematcher` (web,i18n locale 协商)

不新增任何后端服务 / 邮件 / 对象存储依赖。

## Spec / 引用

- 路线图:[`2026-05-10-ghome-p10-roadmap.html`](2026-05-10-ghome-p10-roadmap.html)
- P9 plan: 已完成
- P9.5 plan: 已完成,tag `p9.5-layout-fidelity` 在 main HEAD

## 不做(P10a 范围外)

- 真实对象存储接入(R2/S3/Cloudflare Images)— P10b
- 真实邮件服务(Resend/SES)— P10b
- 真实 APK 托管 — 规避合规风险,永远不做
- 真实多语种翻译(英文/日文)— 等市场决策
- PWA / 离线 — 等离线策略决策
- 评论 / 评分 / 用户登录 / UGC — P11+
- A/B 测试 / Sentry / 监控接入 — 部署相关

## File Structure(P10a 末态)

```
packages/db/
├─ prisma/
│  ├─ schema.prisma                                 # T1:videos.views/likes_count, apps.users_count, ContactSubmission, videos.cover_image_url
│  └─ migrations/20260511010000_p10a_extensions/    # T1
├─ src/lib/
│  ├─ click-aggregate.ts                            # T1 extend: + recomputeRankings()
│  └─ url-policy.ts                                 # T2 extend: requireApk option

apps/web/
├─ app/
│  ├─ [locale]/                                     # T6 i18n route group(空 default zh-CN)
│  │  └─ ...                                        # 现有页面迁入
│  ├─ middleware.ts                                 # T6 next-intl middleware
│  ├─ app/[slug]/opengraph-image.tsx                # T2:每个 detail 类型一个 og:image
│  ├─ video/[slug]/opengraph-image.tsx              # T2
│  ├─ guide/[slug]/opengraph-image.tsx              # T2
│  ├─ topic/[slug]/opengraph-image.tsx              # T2
│  ├─ contact/page.tsx                              # T5:替换 mailto 为真实表单
│  └─ api/contact/route.ts                          # T5:server action / API route
├─ components/
│  ├─ JsonLd.tsx                                    # T2:server,渲染 <script type=application/ld+json>
│  └─ ContactForm.tsx                               # T5:client form
├─ messages/                                        # T6 next-intl
│  ├─ zh-CN.json                                    # T6:中文文案抽出
│  └─ en.json                                       # T6:占位空文件
├─ e2e/                                             # T7 Playwright
│  ├─ home.spec.ts
│  ├─ search.spec.ts
│  ├─ app-detail.spec.ts
│  ├─ video-detail.spec.ts
│  ├─ guide-detail.spec.ts
│  ├─ admin-login.spec.ts
│  ├─ admin-app-create.spec.ts
│  └─ playwright.config.ts
└─ public/uploads/videos/                           # T4 视频封面上传目标(gitignored)

apps/admin/
├─ app/(admin)/
│  ├─ contact-submissions/                          # T5:列表 + 详情
│  │  ├─ page.tsx
│  │  └─ [id]/page.tsx
│  ├─ redirects/page.tsx                            # T3 改:加批量勾选 toolbar
│  ├─ videos/[id]/edit/page.tsx                     # T4 改:加封面上传
│  └─ api/redirects/bulk/route.ts                   # T3:批量 PATCH
└─ components/
   └─ RedirectBulkBar.tsx                           # T3:client,checkbox 状态 + 批量按钮
   └─ VideoCoverUploader.tsx                        # T4:client,文件选择 + 预览
```

## Conventions

- **migrations 一次性**:T1 一个 migration 包含 3 处变更(添加列 + 添加表),手写 SQL 避开 Prisma 自动 drop 生成列的坑(P1/P7/P9 都踩过)
- **Auto-rank 仅重排现有 6 条 ranking collections,不新建**:沿用 P1/P9 seed 时已落地的 `weekly-hot-videos` 等 slug
- **og:image runtime = "edge"**:Next.js 限制(`@vercel/og` 只在 edge 跑)
- **JSON-LD 渲染时机**:server component,`<script>` 直接写在 page 顶部
- **i18n 默认 locale = `zh-CN`**;URL 不带前缀(`/` 默认 zh-CN,`/en/...` 才显示英文 — 等真有翻译再启用)
- **视频封面上传文件路径**:`/uploads/videos/{slug}.{ext}`;数据库存 URL 路径 `/uploads/videos/abc.jpg`(相对路径,生产换 R2 时只改 `lib/upload.ts`)
- **`contact_submissions` 是 admin 独占资源**,不暴露给 web
- **APK 加严策略**:**白名单域名**(`apps.apple.com` `play.google.com` `samsung.com` `huawei.com`)+ 拒绝 raw `.apk` 链接(避免被引导托管)
- **Playwright 测试在 dev 跑**:测试时启动 `next dev` + Postgres,不依赖 prod build。CI 用 service container
- 提交风格:Conventional Commits;每 task commit。permission 阻塞→DONE_WITH_CONCERNS

## 前置假设

- P9.5 完成,`p9.5-layout-fidelity` 标签存在
- Postgres 5432、admin 3100、web 3001(P9.5 临时)正常
- web build 在新增 `@vercel/og` 后仍能跑通
- 9 + 20 + 5 seed 数据在 DB

## Task 依赖关系

```
T1 (数据基建) ─┐
              ├──→ T2 (auto-rank — 用 T1 列)
              ├──→ T4 (视频封面 — 用 T1 列)
              └──→ T5 (联系表单 — 用 T1 表)
T3 (redirect 批量 + APK 校验) — 独立
T6 (og:image + JSON-LD + Twitter) — 独立
T7 (i18n 脚手架) — 独立但 touches everything,推荐靠后
T8 (Playwright E2E) — 必须最后(测试已落地的 UI)
T9 smoke + tag — 最后
```

实施顺序:T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9。

---

## Task 1 — 数据基建:迁移 + seed 回填

**Files:**
- Modify: `packages/db/prisma/schema.prisma`
- Create: `packages/db/prisma/migrations/20260511010000_p10a_extensions/migration.sql`
- Modify: `packages/db/seed/data/videos.ts` + `apps.ts`(parseLabelNumber + 写入 numeric)
- Modify: `packages/db/prisma/seed.ts`

### 改动

1. **schema.prisma**:
   ```prisma
   model Video {
     // ... existing
     viewsCount Int @default(0) @map("views_count")
     likesCount Int @default(0) @map("likes_count")
     coverImageUrl String? @map("cover_image_url")  // T4 用
   }
   model App {
     // ... existing
     usersCount Int @default(0) @map("users_count")
   }
   model ContactSubmission {
     id         String                 @id @default(uuid()) @db.Uuid
     email      String
     name       String?
     subject    String
     body       String                 // markdown ok
     status     ContactSubmissionStatus @default(pending)
     createdAt  DateTime               @default(now()) @map("created_at") @db.Timestamptz(6)
     repliedAt  DateTime?              @map("replied_at") @db.Timestamptz(6)
     repliedBy  String?                @map("replied_by") @db.Uuid  // 关联 admin_users
     adminUser  AdminUser?             @relation(fields: [repliedBy], references: [id])

     @@index([status, createdAt(sort: Desc)])
     @@map("contact_submissions")
   }
   enum ContactSubmissionStatus {
     pending
     read
     replied
     spam
   }
   ```

2. **migration.sql**(手写):
   ```sql
   ALTER TABLE "videos" ADD COLUMN "views_count" INT NOT NULL DEFAULT 0;
   ALTER TABLE "videos" ADD COLUMN "likes_count" INT NOT NULL DEFAULT 0;
   ALTER TABLE "videos" ADD COLUMN "cover_image_url" TEXT;
   ALTER TABLE "apps" ADD COLUMN "users_count" INT NOT NULL DEFAULT 0;

   CREATE TYPE "ContactSubmissionStatus" AS ENUM ('pending', 'read', 'replied', 'spam');

   CREATE TABLE "contact_submissions" (
     "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     "email" TEXT NOT NULL,
     "name" TEXT,
     "subject" TEXT NOT NULL,
     "body" TEXT NOT NULL,
     "status" "ContactSubmissionStatus" NOT NULL DEFAULT 'pending',
     "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT now(),
     "replied_at" TIMESTAMPTZ(6),
     "replied_by" UUID REFERENCES "admin_users"("id")
   );
   CREATE INDEX "idx_cs_status_created" ON "contact_submissions"("status", "created_at" DESC);
   ```

3. **seed.ts**:在 `videos.upsert` 和 `apps.upsert` 中加 numeric 字段,从 `views_label` `likes_label` `users_label` 用 `parseLabelNumber`(P9.5 T1 已有同名 helper,可复用或共享到 `seed/helpers/parse-label.ts`)

### Steps
1. 改 schema + 写 migration
2. 跑 migrate:`pnpm --filter @ghome/db db:migrate:deploy`
3. 改 seed → 跑 `pnpm --filter @ghome/db db:seed`
4. 验证:`docker exec ghome-postgres psql -U ghome -d ghome -c "SELECT slug, views_count, likes_count FROM videos LIMIT 3;"`(应非零)
5. typecheck + commit

### Tricky Bits
- 不要让 Prisma 自动生成 migration(会 drop `category_kind` 生成列)
- `gen_random_uuid()` 需要 `pgcrypto`,Postgres 16 默认有
- seed 是 idempotent upsert,跑两次结果一致
- `parseLabelNumber` 与 P9.5 T1 重复,抽到 `packages/db/seed/helpers/parse-label.ts` 共享

---

## Task 2 — Auto-rank cron 扩展

**Files:**
- Modify: `packages/db/src/lib/click-aggregate.ts` → 改名 `scheduled-jobs.ts`,加 `recomputeRankings()`
- Modify: `apps/admin/app/api/cron/aggregate-clicks/route.ts` → 调用新 wrapper(或新建 `/api/cron/run/route.ts`)

### Steps
1. 抽 `recomputeRankings(prisma)`:对 6 条 ranking collections 各自重新计算 items 顺序:
   - `weekly-hot-videos` / `latest-videos` / `top-liked-videos`:按 `views_count desc / published_date desc / likes_count desc` 分别重排前 8 条 video items
   - `weekly-hot-apps` / `top-rated-apps`:按 `users_count desc / rating desc` 重排前 8 条 app items
   - `hot-tags`:按各 tag 关联 video 数 desc 重排前 10 条 tag items
   - 用 `prisma.$transaction` + DEFERRABLE UNIQUE 约束允许中间态冲突
2. 新 export `runScheduledJobs(prisma)` = `aggregateClickEvents` + `recomputeRankings`
3. cron route 调 `runScheduledJobs`
4. 测试:跑一次 → 看 ranking_items.position 重排
5. commit

### Tricky Bits
- 6 条 ranking 每条 items 数量不同,要先 `deleteMany({ collectionId: r.id })` 再 batch create —— 比 in-place update 简单
- DEFERRABLE INITIALLY DEFERRED 约束确保事务内 position 重排不冲突
- 不动 `aggregateClickEvents` 的现有逻辑(advisory lock 仍生效)

---

## Task 3 — Redirect 批量 + APK URL 加严

**Files:**
- Create: `apps/admin/components/RedirectBulkBar.tsx` (client)
- Modify: `apps/admin/app/(admin)/redirects/page.tsx`(加 checkbox 列 + bulk bar)
- Create: `apps/admin/app/api/redirects/bulk/route.ts`
- Modify: `packages/db/src/lib/url-policy.ts` (加 `requireApkSafe` 选项)

### Steps
1. URL 校验加严:
   ```ts
   // url-policy.ts
   const APK_SAFE_HOSTS = new Set([
     "apps.apple.com",
     "play.google.com",
     "galaxy.store",       // Samsung
     "appgallery.huawei.com", // Huawei
     "www.apple.com",
   ]);
   export async function validateForWrite(url, opts = {}) {
     // ... existing checks
     if (opts.requireApkSafe) {
       const u = new URL(url);
       if (!APK_SAFE_HOSTS.has(u.hostname)) {
         return { ok: false, reason: `host '${u.hostname}' 不在 APK 白名单。仅允许官方应用商店。` };
       }
     }
     return { ok: true };
   }
   ```
2. RedirectBulkBar:勾选状态用 `useState<Set<string>>`,顶部 toolbar 显示选中数 + 「批量启用 / 批量禁用」按钮
3. PATCH `/api/redirects/bulk`:body `{ ids: string[], action: "enable" | "disable" }` → `prisma.redirect.updateMany` + 单条 audit_log
4. 列表页加 checkbox 列(每行一个,顶部一个全选)
5. typecheck + build + smoke + commit

### Tricky Bits
- 全选 checkbox 是 indeterminate 三态(无 / 部分 / 全选)
- 批量操作完后用 `router.refresh()` 拉最新数据
- audit_log 写一条 `redirect.bulk_update` 记录 + diff 列表

---

## Task 4 — 视频封面图上传(本地桩)

**Files:**
- Create: `apps/admin/components/VideoCoverUploader.tsx` (client)
- Create: `packages/db/src/lib/upload.ts`(local file storage helper)
- Modify: `apps/admin/app/(admin)/videos/[id]/edit/page.tsx`(加上传 row)
- Modify: `apps/web/components/VideoCard.tsx` + `VideoHero.tsx`(优先用真实图)

### Steps
1. `lib/upload.ts`:`saveImageToLocal(file: File, slug: string): Promise<string>`,返回 URL 路径
   - 验证:文件类型 image/*,大小 ≤ 5MB,扩展名 jpg/png/webp
   - 写到 `apps/web/public/uploads/videos/{slug}.{ext}`
2. VideoCoverUploader:`<input type="file" accept="image/*">` + 客户端预览(FileReader)+ submit 走 server action
3. videos edit page server action 接收上传后,调 saveImageToLocal,把返回的 URL 写到 `videos.cover_image_url`
4. web `VideoCard`/`VideoHero` 改成 `cover_image_url ? <img> : <div style={{background: coverCss}}>`
5. typecheck + build + smoke + commit

### Tricky Bits
- Next.js Server Actions 默认 body 上限 1MB,文件上传要扩 `serverActions: { bodySizeLimit: '5mb' }` 在 next.config
- `apps/web/public/uploads/` 加到 `.gitignore`,但目录本身保留(用 `.gitkeep`)
- 真实生产场景换 R2 / S3 时,`saveImageToLocal` 接口不变,实现换成 S3 SDK
- VideoCard 接受 `coverImageUrl?: string` prop,fallback 现有 gradient 逻辑

---

## Task 5 — 联系表单后端

**Files:**
- Modify: `apps/web/app/contact/page.tsx`(把 4 张 brand-card 中的「商务合作」「内容投稿」「BD 接洽」三张的 mailto: 替换成统一表单)
- Create: `apps/web/components/ContactForm.tsx` (client)
- Create: `apps/web/app/api/contact/route.ts`
- Create: `apps/admin/app/(admin)/contact-submissions/page.tsx`(列表 + 状态过滤 + 分页)
- Create: `apps/admin/app/(admin)/contact-submissions/[id]/page.tsx`(详情 + 状态切换)

### Steps
1. ContactForm:client 表单,字段 `email / name / subject / body`,客户端校验 + 提交到 `/api/contact`
2. `/api/contact` POST:基础校验(email 格式 / 长度) + spam 简单防(蜜罐字段 honey + rate limit by IP hash from P3)→ `prisma.contactSubmission.create({ status: "pending" })`
3. /contact 页面:hero 上方 brand-card 4 张保留,下方加表单 section
4. admin /contact-submissions:列表 + 5 维过滤(status / 邮箱子串 / 关键词 / since / until)+ 分页(沿用 audit-log 模板)
5. admin /contact-submissions/[id]:详情 + 「标记为已读」「标记为已回复」「标记为垃圾邮件」按钮 → 写 `status` + `replied_at` + `replied_by = session.user.adminUserId`
6. typecheck + build + commit

### Tricky Bits
- 蜜罐字段:`<input name="hp" hidden>`;后端检查空才接受
- email 校验:简单 `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- 长度上限:subject ≤ 200,body ≤ 5000
- admin 列表 / 详情按 audit-log 模板模仿(P7 已写过同类)
- 不发邮件,不通知 — 运营看 admin 看板

---

## Task 6 — og:image + JSON-LD + Twitter Cards

**Files:**
- Create: `apps/web/app/app/[slug]/opengraph-image.tsx`
- Create: `apps/web/app/video/[slug]/opengraph-image.tsx`
- Create: `apps/web/app/guide/[slug]/opengraph-image.tsx`
- Create: `apps/web/app/topic/[slug]/opengraph-image.tsx`
- Create: `apps/web/components/JsonLd.tsx` (server)
- Modify: 4 detail pages(挂 JsonLd + Twitter Card metadata)
- Modify: `apps/web/app/layout.tsx`(默认 Twitter Card)

### Steps
1. 装 `@vercel/og`
2. opengraph-image.tsx 模板(每个 detail 一个):
   ```tsx
   import { ImageResponse } from "next/og";

   export const runtime = "edge";
   export const size = { width: 1200, height: 630 };
   export const contentType = "image/png";

   export default async function Image({ params }) {
     // 拉数据
     return new ImageResponse(
       <div style={{ display: "flex", height: "100%", width: "100%",
         background: "linear-gradient(135deg,#5B5BE8 0%,#B85BE8 100%)",
         color: "#fff", padding: 80, alignItems: "flex-end" }}>
         <div>
           <div style={{ fontSize: 28, opacity: 0.85 }}>{tag}</div>
           <h1 style={{ fontSize: 80, fontWeight: 800, lineHeight: 1.1 }}>{title}</h1>
           <div style={{ fontSize: 32, opacity: 0.85, marginTop: 24 }}>Ghome</div>
         </div>
       </div>,
       size,
     );
   }
   ```
3. JsonLd 组件:server 渲染 `<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}>`
4. 每个 detail 页加:
   - App: `SoftwareApplication` schema
   - Video: `VideoObject` schema
   - Guide: `Article` schema
   - Topic: `CollectionPage` schema
5. layout.tsx 加默认 `metadata.twitter = { card: "summary_large_image", site: "@Ghome" }`
6. 各 detail 页 generateMetadata 加 `twitter: { card: ..., images: [`/${path}/opengraph-image`] }`
7. typecheck + build + smoke(curl 看 og: 与 application/ld+json 字符串)+ commit

### Tricky Bits
- `runtime = "edge"` 不能用 Prisma — 在 og 函数里再 `fetch` 自家 API 拉数据,或加查 prisma 的 fallback(可能 build 失败)
- 实际更简单:在 opengraph-image.tsx 里只用 params.slug 显示标题(不查 DB,从 URL 推),或 inline 一个最小 fetch
- ImageResponse 默认 fonts 需要嵌入字体文件 — 中文字符可能渲染成方框。MVP 先用英文 placeholder,标题从 slug 推断
- JsonLd `dangerouslySetInnerHTML` 安全:JSON.stringify 自动转义

---

## Task 7 — i18n 脚手架(中文默认)

**Files:**
- 装 `next-intl` + `negotiator` + `@formatjs/intl-localematcher`
- Create: `apps/web/middleware.ts`
- Create: `apps/web/i18n.ts`
- Create: `apps/web/messages/zh-CN.json`
- Create: `apps/web/messages/en.json` (空对象,占位)
- Move: `apps/web/app/*` → `apps/web/app/[locale]/*`(除 `api/` `r/[id]` `sitemap.ts` `robots.ts`)
- Modify: 所有页面 `import { useTranslations } from "next-intl"` 替换硬编码中文

### Steps
1. 装依赖
2. 配 `next-intl` 中间件 + 路由分组
3. 抽中文文案到 `messages/zh-CN.json`(分模块:home / app / video / guide / common)
4. 替换页面 / 组件中硬编码字符串为 `t('home.hero.title')` 形式
5. URL 策略:默认 `/`(zh-CN 不带前缀),`/en/...` 走英文(messages/en.json 暂空,fallback 到 zh-CN)
6. 验证:`/` 仍中文,`/en/` 也中文(因 en messages 空)— 这是预期的脚手架状态
7. typecheck + build + commit

### Tricky Bits
- next-intl 与 Next 15 App Router 配合需要 `i18n.ts` 入口 — 看官方文档样例
- 不要把 `/r/[id]` 重定向放到 [locale] 下(应该是无 locale 的全局短链)
- sitemap.ts 和 robots.ts 也保持在根 app/ 下
- admin 不动 — i18n 仅 web

---

## Task 8 — Playwright E2E 测试

**Files:**
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/e2e/{home,search,app-detail,video-detail,guide-detail,videos-list,topic-detail,categories,contact-form,redirect,sitemap}.spec.ts`
- Modify: `apps/web/package.json`(加 `e2e` script)
- Modify: `.github/workflows/ci.yml`(加 e2e job)

### Steps
1. 装 `@playwright/test` devDep + `pnpm --filter @ghome/web exec playwright install chromium`
2. playwright.config.ts:`baseURL: 'http://localhost:3001'`(临时端口)+ `webServer: { command: 'pnpm dev' }`(playwright 自启 web)
3. 写 ~12 个 spec:
   - home.spec:hero + 搜索 + 各 shelf 渲染
   - search.spec:输入查询 → 跳 /search?q= → 至少 1 条结果
   - app-detail.spec:open `/app/broconnect` → 6 格 info + 安装步骤 + CTA
   - video-detail.spec:dur 角标 + 推荐 App
   - guide-detail.spec:two-col + TOC click → 滚动到 anchor
   - videos-list.spec:filter chip 切换 → URL 更新
   - topic-detail.spec:hero stats
   - categories.spec:6 cat-block
   - contact-form.spec:填表单 → 提交 → 后端入库(查 DB 断言)
   - redirect.spec:点 App CTA → 302 → DB click_events +1
   - sitemap.spec:`/sitemap.xml` 200 + 含 /app/broconnect
   - admin-login.spec:登录 → /redirects 列表 + 批量勾选 → 批量禁用 → 重 fetch 看 disabled=true
4. CI 加 job:`pnpm test:e2e` 在 postgres + dev 启动后跑
5. commit

### Tricky Bits
- Playwright 启 next dev 比 next start 慢,但 dev 模式下 server actions 等更稳
- contact-form.spec 需要直接连 DB 断言入库 → 用 `pg` lib 或调 `/api/admin/...` API
- redirect.spec 检查 click_events 入库 → 同 DB 断言
- CI 时长会显著增加(可能 +5-8 分钟),并行 chromium worker 缓解

---

## Task 9 — End-to-end smoke + tag p10a-finishing

**Files:** 无新文件;只跑 CI 全套 + 打 tag。

### Steps
1. 跑全套本地 CI 等价命令:
   ```bash
   docker compose up -d
   pnpm install
   pnpm --filter @ghome/db db:migrate:deploy
   pnpm --filter @ghome/db db:seed
   pnpm --filter @ghome/db typecheck && pnpm --filter @ghome/db test
   pnpm --filter @ghome/admin typecheck && pnpm --filter @ghome/admin lint && pnpm --filter @ghome/admin build
   pnpm --filter @ghome/web typecheck && pnpm --filter @ghome/web lint && pnpm --filter @ghome/web build
   pnpm --filter @ghome/web exec playwright test
   ```
2. UI 视觉冒烟:
   - 上传一张视频封面图,/video/[slug] 显示真图
   - admin 编辑 redirect,白名单外 URL 校验失败
   - admin 批量勾选 3 个 redirect → 批量禁用 → 列表全部变灰
   - 提交联系表单 → admin /contact-submissions 看到一条 pending
   - cron 跑一次 → ranking_items.position 重排
3. 打 tag `p10a-finishing`
4. 推 tag(等用户授权)

## Final 验收清单

- [ ] `videos.views_count` `videos.likes_count` `apps.users_count` 列存在 + 回填
- [ ] `videos.cover_image_url` 字段存在 + admin 可上传 + web 优先用真图
- [ ] `contact_submissions` 表存在 + admin 列表 / 详情可用
- [ ] cron 跑一次 → 6 条 ranking 重排成功
- [ ] redirect 批量勾选 / 批量禁用工作
- [ ] APK URL 校验:仅白名单域名通过
- [ ] 4 个 detail 页有 og:image(curl 看 image/png 200)
- [ ] 4 个 detail 页有 application/ld+json
- [ ] Twitter Cards meta 在 layout.tsx 默认 + detail 覆盖
- [ ] i18n 脚手架就绪:`/` 中文,`/en/` fallback 到中文
- [ ] Playwright 12 个 spec 全过
- [ ] CI 全绿(typecheck / lint / build / unit + e2e)
- [ ] tag `p10a-finishing` 在 main HEAD

**P10a 完成 ⇒ 可以接 P10b(R2 / Resend / 真实部署)或 P11+(UGC / i18n 真实落地)。**
