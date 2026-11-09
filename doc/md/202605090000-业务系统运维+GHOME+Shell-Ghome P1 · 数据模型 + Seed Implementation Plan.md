---
id: "doc-7ee18dad49c1"
title: "Ghome P1 · 数据模型 + Seed Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/operator/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p1-data-model-and-seed.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p1-data-model-and-seed.md"
sourceSha256: "5d0d97b6df983a61c3e35c99449e54e403b85777f6ce8aa1048ff48a2764d0e7"
sourceSystem: "project-doc"
---

# Ghome P1 · 数据模型 + Seed Implementation Plan

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605090000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20P1%20%C2%B7%20%E6%95%B0%E6%8D%AE%E6%A8%A1%E5%9E%8B%20%2B%20Seed%20Implementation%20Plan.md)

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 Ghome 14 张表的 Prisma schema + 首版迁移 + 手写 raw SQL 约束(生成列/复合 FK/CHECK/DEFERRABLE UNIQUE/pg_trgm)+ url-policy 工具 + 从原型 `docs/ghome.html` 迁出的全套 seed 数据(9 App / 20 Video / 6 Topic / 6 Ranking 50 items / 5 Guide w/ markdown bodies / 全并集 tags + 全英文 slug 映射 / 各种 disabled 占位 redirect),并把 GitHub Actions CI 升级为带 `postgres:16` service + migrate + seed 的完整闭环。

**Architecture:** P0 已落地的 `@ghome/db` 占位包在 P1 被填充为真实数据访问层。Prisma schema 用 DSL 表达字段、关系与 Prisma enums(`ContentStatus` / `CollectionKind` / `CollectionItemRefType` / `RedirectOwnerKind`),但**不**声明:① `categories.kind` 用 `text + CHECK`(避免 ENUM/text FK 类型不兼容);② `collection_items.@@unique([collectionId, position])`(避免与 DEFERRABLE UNIQUE 双约束冲突);③ apps/videos `category_kind` 生成列(Prisma DSL 不支持 GENERATED ALWAYS AS STORED)。这些走第二个 raw-SQL migration。

**Tech Stack:**
- Prisma `^5.22.0`(已在 P0 安装)
- @prisma/client `^5.22.0`(已在 P0 安装)
- Postgres 16(本地 docker-compose,已在 P0 配置)
- Vitest 2.x(P1 新增,运行 url-policy 单元测试 + DB 约束集成测试)
- ua-parser-js(P3 才用,本期不引入)

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §3(数据模型)、§4.4(搜索 ILIKE+pg_trgm)、§4.5(seed 来源)、§5 P1。

**前置假设:** P0 已完成,`p0-scaffolding` 标签存在;`docker compose up -d` 起得来 Postgres;`packages/db/src/index.ts` 当前是占位代码。

---

## File Structure(P1 末态)

```
packages/db/
├─ prisma/
│  ├─ schema.prisma                     # 14 models + 4 enums
│  ├─ migrations/
│  │  ├─ <ts1>_init/migration.sql        # Prisma autogen(T2)
│  │  ├─ <ts2>_constraints/migration.sql # 手写 raw SQL(T3)
│  │  └─ migration_lock.toml
│  └─ seed.ts                            # `prisma db seed` 入口(T9)
├─ seed/
│  ├─ data/
│  │  ├─ apps.ts                         # APPS 数据(T6)
│  │  ├─ videos.ts                       # VIDEOS 数据(T6)
│  │  ├─ app-cats.ts                     # APP_CATS 排除 'all'(T6)
│  │  ├─ video-cats.ts                   # CATEGORIES 视频分类(T6)
│  │  ├─ tags.ts                         # 全并集 label→slug 映射(T7)
│  │  ├─ topics.ts                       # 6 个专题 specs(T7)
│  │  ├─ guides.ts                       # GUIDES 元数据(T8)
│  │  └─ guide-bodies.ts                 # 5 篇 HTML→MD 正文(T8)
│  └─ helpers/
│      ├─ parse-labels.ts                # 解析 '38.1万' / '800万+' 等(T8)
│      └─ rankings.ts                    # 从 apps/videos/tags 算出 6 个 ranking specs(T8)
├─ src/
│  ├─ index.ts                           # 重写 — 公开 client + 工具(T4)
│  ├─ client.ts                          # PrismaClient 单例(T4)
│  └─ lib/
│      └─ url-policy.ts                  # validateForWrite / validateForRedirect(T5)
├─ scripts/
│  └─ enable-redirect.ts                 # `pnpm db:enable-redirect`(T10)
├─ tests/
│  ├─ url-policy.test.ts                 # T5 单元测试
│  └─ db-constraints.test.ts             # T9 集成测试
├─ vitest.config.ts                      # T5 添加
├─ package.json                          # 多次扩展(scripts、deps)
└─ tsconfig.json                         # 已存在,P1 不动

apps/web/.env, apps/admin/.env           # 本地开发各自 DATABASE_URL(各自创建,不入库)
packages/db/.env                         # Prisma CLI 用,T2 创建,不入库

.github/workflows/ci.yml                 # T11 整体重写,加 postgres service + migrate + seed
```

---

## Constants & Conventions(整个 P1 共享)

- `IP_HASH_SECRET` env(P3 才用,但 url-policy 不依赖)
- 所有 redirect 的占位 URL 形如 `https://example.com/seed/{kind}/{slug}`,`disabled=true`
- ranking collection slug:`weekly-hot-videos` / `latest-videos` / `top-liked-videos` / `weekly-hot-apps` / `top-rated-apps` / `hot-tags`
- ranking sort_order:0..5(同上顺序)
- topic collection sort_order:按原型 `TOPICS` 数组顺序赋 0..5
- 提交风格:Conventional Commits(`feat`/`fix`/`chore`/`ci`/`test`/`docs`)
- 每个 task 末尾 `git commit`

---

## Task 1 — Prisma schema:14 models + 4 enums(不含 generated 列与 CHECK)

**Files:**
- Create: `packages/db/prisma/schema.prisma`
- Create: `packages/db/.env`(本地 Prisma CLI 读)
- Modify: `packages/db/.gitignore` — 创建并把 `.env` 写进去
- Modify: `packages/db/package.json` — 加 `prisma` 配置块

- [ ] **Step 1: 创建 `packages/db/.env`(本地用,不入库)**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
cat > packages/db/.env <<'EOF'
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome
EOF
```

- [ ] **Step 2: 创建 `packages/db/.gitignore`**

```
.env
.env.local
node_modules
dist
generated
```

- [ ] **Step 3: 写 `packages/db/prisma/schema.prisma`**

```prisma
generator client {
  provider = "prisma-client-js"
  output   = "../node_modules/.prisma/client"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ============== Enums ==============
// categories.kind 故意用 text+CHECK,不在这里声明 enum(详见 spec §3.2)

enum ContentStatus {
  draft
  published
  archived
}

enum CollectionKind {
  topic
  album
  ranking
}

enum CollectionItemRefType {
  app
  video
  tag
  external
}

enum RedirectOwnerKind {
  app
  video
  external
  collection_item
}

// ============== Content ==============

model App {
  id            String        @id @default(uuid()) @db.Uuid
  slug          String        @unique
  name          String
  iconKey       String        @map("icon_key")
  gradientKey   String        @map("gradient_key")
  categoryId    String        @map("category_id") @db.Uuid

  shortDesc     String        @map("short_desc")
  detail        String
  highlights    String[]
  audience      String
  features      String
  platform      String
  size          String
  rating        String
  usersLabel    String        @map("users_label")

  redirectId    String        @unique @map("redirect_id") @db.Uuid

  status        ContentStatus @default(draft)
  createdAt     DateTime      @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt     DateTime      @updatedAt @map("updated_at") @db.Timestamptz(6)
  deletedAt     DateTime?     @map("deleted_at") @db.Timestamptz(6)

  // category 关系:T3 的 raw SQL 把 FK 改为 (category_id, category_kind) 复合 FK
  category      Category      @relation(fields: [categoryId], references: [id])
  redirect      Redirect      @relation(fields: [redirectId], references: [id])
  tags          AppTag[]

  @@map("apps")
}

model Video {
  id              String        @id @default(uuid()) @db.Uuid
  slug            String        @unique
  title           String
  emoji           String
  coverKey        String        @map("cover_key")
  duration        String

  viewsLabel      String        @map("views_label")
  likesLabel      String        @map("likes_label")
  publishedDate   DateTime      @map("published_date") @db.Date
  categoryId      String        @map("category_id") @db.Uuid

  shortDesc       String        @map("short_desc")
  detail          String

  redirectId      String        @unique @map("redirect_id") @db.Uuid

  status          ContentStatus @default(draft)
  createdAt       DateTime      @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt       DateTime      @updatedAt @map("updated_at") @db.Timestamptz(6)
  deletedAt       DateTime?     @map("deleted_at") @db.Timestamptz(6)

  category        Category      @relation(fields: [categoryId], references: [id])
  redirect        Redirect      @relation(fields: [redirectId], references: [id])
  tags            VideoTag[]

  @@map("videos")
}

model Guide {
  id             String        @id @default(uuid()) @db.Uuid
  slug           String        @unique
  title          String
  summary        String
  bodyMd         String        @map("body_md")
  categorySlug   String        @map("category_slug")   // 'app' / 'video' / 'privacy' / 'social'
  categoryLabel  String        @map("category_label")  // 显示文案,冗余存
  gradientKey    String        @map("gradient_key")
  iconKey        String        @map("icon_key")
  readMinutes    Int           @map("read_minutes")
  viewsLabel     String        @map("views_label")
  isHot          Boolean       @default(false) @map("is_hot")
  publishedDate  DateTime      @map("published_date") @db.Date

  status         ContentStatus @default(draft)
  createdAt      DateTime      @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt      DateTime      @updatedAt @map("updated_at") @db.Timestamptz(6)
  deletedAt      DateTime?     @map("deleted_at") @db.Timestamptz(6)

  @@map("guides")
}

// ============== Taxonomy ==============

model Category {
  id          String   @id @default(uuid()) @db.Uuid
  slug        String
  label       String
  description String?
  kind        String   // text + CHECK ('app','video') — see T3 raw SQL
  sortOrder   Int      @default(0) @map("sort_order")

  apps        App[]
  videos      Video[]

  @@unique([kind, slug])  // slug 在 kind 内唯一,跨 kind 可重复(如 'life')
  @@unique([id, kind])    // 复合 FK 目标(T3 raw SQL 使用)
  @@map("categories")
}

model Tag {
  id     String     @id @default(uuid()) @db.Uuid
  slug   String     @unique  // kebab-case 英文
  label  String     @unique  // 显示文案,通常中文,一个概念一条

  apps   AppTag[]
  videos VideoTag[]

  @@map("tags")
}

model AppTag {
  appId  String @map("app_id") @db.Uuid
  tagId  String @map("tag_id") @db.Uuid

  app    App    @relation(fields: [appId], references: [id], onDelete: Cascade)
  tag    Tag    @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@id([appId, tagId])
  @@map("app_tags")
}

model VideoTag {
  videoId String @map("video_id") @db.Uuid
  tagId   String @map("tag_id") @db.Uuid

  video   Video  @relation(fields: [videoId], references: [id], onDelete: Cascade)
  tag     Tag    @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@id([videoId, tagId])
  @@map("video_tags")
}

// ============== Curation(三合一) ==============

model Collection {
  id          String         @id @default(uuid()) @db.Uuid
  slug        String         @unique
  kind        CollectionKind
  title       String
  description String?
  coverKey    String?        @map("cover_key")
  sortOrder   Int            @default(0) @map("sort_order")

  status      ContentStatus  @default(draft)
  createdAt   DateTime       @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt   DateTime       @updatedAt @map("updated_at") @db.Timestamptz(6)
  deletedAt   DateTime?      @map("deleted_at") @db.Timestamptz(6)

  items       CollectionItem[]

  @@map("collections")
}

model CollectionItem {
  id            String                @id @default(uuid()) @db.Uuid
  collectionId  String                @map("collection_id") @db.Uuid
  position      Int
  refType       CollectionItemRefType @map("ref_type")
  appId         String?               @map("app_id") @db.Uuid
  videoId       String?               @map("video_id") @db.Uuid
  tagId         String?               @map("tag_id") @db.Uuid
  redirectId    String?               @map("redirect_id") @db.Uuid
  externalLabel String?               @map("external_label")
  note          String?

  collection    Collection            @relation(fields: [collectionId], references: [id], onDelete: Cascade)

  // ⚠️ 故意不声明 @@unique([collectionId, position])
  //   raw SQL 在 T3 添加 DEFERRABLE INITIALLY DEFERRED 唯一约束;Prisma 普通 unique 与 deferrable 共存会拦掉 position 交换
  // ⚠️ ref_type 互斥的 CHECK 约束也在 T3 raw SQL 里
  @@map("collection_items")
}

// ============== Navigation(redirect 与点击日志) ==============

model Redirect {
  id         String              @id @default(uuid()) @db.Uuid
  targetUrl  String              @map("target_url")
  ownerKind  RedirectOwnerKind   @map("owner_kind")
  ownerId    String?             @map("owner_id")  // 反查归属(text)
  disabled   Boolean             @default(false)
  createdAt  DateTime            @default(now()) @map("created_at") @db.Timestamptz(6)

  app        App?
  video      Video?
  events     ClickEvent[]
  dailyStats ClickDailyStat[]

  @@map("redirects")
}

model ClickEvent {
  id              String   @id @default(uuid()) @db.Uuid
  redirectId      String   @map("redirect_id") @db.Uuid
  ts              DateTime @db.Timestamptz(6)
  uaFamily        String   @default("unknown") @map("ua_family")
  uaOs            String   @default("unknown") @map("ua_os")
  country         String   @default("unknown")
  referrerOrigin  String   @default("unknown") @map("referrer_origin")
  ipHash          String   @map("ip_hash")

  redirect        Redirect @relation(fields: [redirectId], references: [id], onDelete: Cascade)

  @@index([redirectId, ts(sort: Desc)])
  @@map("click_events")
}

model ClickDailyStat {
  redirectId String   @map("redirect_id") @db.Uuid
  day        DateTime @db.Date
  uaFamily   String   @default("unknown") @map("ua_family")
  country    String   @default("unknown")
  count      BigInt

  redirect   Redirect @relation(fields: [redirectId], references: [id], onDelete: Cascade)

  @@id([redirectId, day, uaFamily, country])
  @@map("click_daily_stats")
}

// ============== Admin ==============

model AdminUser {
  id           String    @id @default(uuid()) @db.Uuid
  githubId     BigInt    @unique @map("github_id")
  githubLogin  String    @unique @map("github_login")
  githubEmail  String?   @map("github_email")
  name         String?
  lastLoginAt  DateTime? @map("last_login_at") @db.Timestamptz(6)
  createdAt    DateTime  @default(now()) @map("created_at") @db.Timestamptz(6)

  auditEntries AuditLogEntry[]

  @@map("admin_users")
}

model AuditLogEntry {
  id            String    @id @default(uuid()) @db.Uuid
  adminUserId   String    @map("admin_user_id") @db.Uuid
  action        String
  targetType    String    @map("target_type")
  targetId      String    @map("target_id")
  diffJson      Json      @map("diff_json")
  ts            DateTime  @default(now()) @db.Timestamptz(6)

  adminUser     AdminUser @relation(fields: [adminUserId], references: [id])

  @@index([adminUserId, ts(sort: Desc)])
  @@map("audit_log")
}
```

> ⚠️ **故意不声明的项**(都在 T3 raw SQL):
> - `categories.kind` 没有 enum(用 text + CHECK 配复合 FK)
> - `collection_items` 没有 `@@unique([collectionId, position])`
> - `apps.categoryKind` / `videos.categoryKind` 不在 schema 里(GENERATED ALWAYS AS ... STORED)
> - `apps.category` / `videos.category` 关系暂用单字段 FK,T3 raw SQL 重建为复合 FK

- [ ] **Step 4: 修改 `packages/db/package.json` 加 prisma 配置 + scripts**

把 packages/db/package.json 改为(注意:已有的字段保留,扩展以下):

```json
{
  "name": "@ghome/db",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "prisma": {
    "schema": "prisma/schema.prisma",
    "seed": "tsx prisma/seed.ts"
  },
  "scripts": {
    "lint": "echo \"lint skipped at P0 (no eslint config yet)\"",
    "typecheck": "tsc --noEmit",
    "clean": "rimraf dist .prisma",
    "db:generate": "prisma generate",
    "db:migrate:dev": "prisma migrate dev",
    "db:migrate:deploy": "prisma migrate deploy",
    "db:seed": "prisma db seed",
    "db:reset": "prisma migrate reset --force",
    "db:enable-redirect": "tsx scripts/enable-redirect.ts",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@prisma/client": "^5.22.0"
  },
  "devDependencies": {
    "eslint": "^9.0.0",
    "prisma": "^5.22.0",
    "rimraf": "^6.0.1",
    "tsx": "^4.19.0",
    "typescript": "^5.5.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 5: 安装新增依赖**

```bash
pnpm install
```

Expected: 拉下 `tsx` 与 `vitest`(并各自的依赖)。

- [ ] **Step 6: 验证 schema 语法 + Prisma format**

```bash
pnpm --filter @ghome/db exec prisma format
pnpm --filter @ghome/db exec prisma validate
```

Expected: `format` 输出 `Formatted ...`;`validate` 输出 `The schema at <path> is valid 🚀`。

- [ ] **Step 7: 提交**

```bash
git add packages/db/prisma/schema.prisma packages/db/.gitignore packages/db/package.json pnpm-lock.yaml
git commit -m "feat(db): add Prisma schema with 14 models and 4 enums (constraints in T3)"
```

---

## Task 2 — 首版迁移 `init`(只覆盖 Prisma DSL 能表达的部分)

**Files:**
- Create: `packages/db/prisma/migrations/<ts>_init/migration.sql`(由 Prisma 生成)
- Create: `packages/db/prisma/migrations/migration_lock.toml`

- [ ] **Step 1: 用 prisma migrate dev 生成首版迁移**

```bash
docker compose up -d
pnpm --filter @ghome/db exec prisma migrate dev --name init --create-only
```

Expected: 输出 `Created the following migration: <ts>_init`;DB **不**会被 apply(因为 `--create-only`)。`prisma/migrations/<ts>_init/migration.sql` 出现。

- [ ] **Step 2: 检查生成的 migration SQL**

```bash
ls -la packages/db/prisma/migrations/
cat packages/db/prisma/migrations/*_init/migration.sql | head -50
```

Expected: 看到 `CREATE TYPE "ContentStatus" AS ENUM ('draft', 'published', 'archived');` 等;能看到 14 个 `CREATE TABLE`。注意 `categories.kind` 应该是 `TEXT NOT NULL`(不是 enum)— 这正是我们想要的。

- [ ] **Step 3: 应用迁移到本地 DB**

```bash
pnpm --filter @ghome/db exec prisma migrate deploy
```

Expected: `1 migration applied`。

- [ ] **Step 4: 验证 DB 里有 14 张表 + 4 个 enum 类型**

```bash
docker compose exec postgres psql -U ghome -d ghome -c "\dt"
docker compose exec postgres psql -U ghome -d ghome -c "\dT"
```

Expected: `\dt` 列出 14 张表(`apps`, `videos`, `guides`, `categories`, `tags`, `app_tags`, `video_tags`, `collections`, `collection_items`, `redirects`, `click_events`, `click_daily_stats`, `admin_users`, `audit_log`)。`\dT` 列出 4 个 enum 类型 + 一个 Prisma 元表 `_prisma_migrations`。

- [ ] **Step 5: 提交**

```bash
git add packages/db/prisma/migrations/
git commit -m "feat(db): generate initial Prisma migration (14 tables, no constraints yet)"
```

---

## Task 3 — 手写约束迁移:CHECK / DEFERRABLE UNIQUE / 生成列 / 复合 FK / pg_trgm

**Files:**
- Create: `packages/db/prisma/migrations/<ts>_constraints/migration.sql`

- [ ] **Step 1: 创建空 migration 占位**

```bash
mkdir -p packages/db/prisma/migrations/$(date -u +%Y%m%d%H%M%S)_constraints
```

得到目录名形如 `20260509093000_constraints/`。把目录名记下来 — 后续 step 写文件用。

> 注:Prisma 接受手工创建的 migration 目录,只要按 `<14位时间戳>_<name>/migration.sql` 命名。

- [ ] **Step 2: 写 `migration.sql`**

```sql
-- ============== categories.kind: text + CHECK ==============
ALTER TABLE "categories"
  ADD CONSTRAINT "categories_kind_check"
  CHECK (kind IN ('app', 'video'));

-- ============== apps / videos: 生成列 + 复合 FK 防 kind 错配 ==============
-- 1. categories 加 (id, kind) 复合唯一,作为复合 FK 的 target
ALTER TABLE "categories"
  ADD CONSTRAINT "categories_id_kind_unique" UNIQUE ("id", "kind");

-- 2. apps / videos 加生成列(text,与 categories.kind 严格类型一致)
ALTER TABLE "apps"
  ADD COLUMN "category_kind" TEXT GENERATED ALWAYS AS ('app') STORED;

ALTER TABLE "videos"
  ADD COLUMN "category_kind" TEXT GENERATED ALWAYS AS ('video') STORED;

-- 3. 删除 Prisma 默认的单字段 FK,改为复合 FK(同时校验 categoryId 与 category_kind 都对)
ALTER TABLE "apps"
  DROP CONSTRAINT "apps_category_id_fkey";
ALTER TABLE "apps"
  ADD CONSTRAINT "apps_category_kind_fk"
    FOREIGN KEY ("category_id", "category_kind")
    REFERENCES "categories" ("id", "kind");

ALTER TABLE "videos"
  DROP CONSTRAINT "videos_category_id_fkey";
ALTER TABLE "videos"
  ADD CONSTRAINT "videos_category_kind_fk"
    FOREIGN KEY ("category_id", "category_kind")
    REFERENCES "categories" ("id", "kind");

-- ============== collection_items: ref_type 互斥 CHECK ==============
ALTER TABLE "collection_items"
  ADD CONSTRAINT "collection_items_ref_match" CHECK (
    (ref_type = 'app'      AND app_id IS NOT NULL  AND video_id IS NULL AND tag_id IS NULL AND redirect_id IS NULL) OR
    (ref_type = 'video'    AND video_id IS NOT NULL AND app_id IS NULL  AND tag_id IS NULL AND redirect_id IS NULL) OR
    (ref_type = 'tag'      AND tag_id IS NOT NULL  AND app_id IS NULL  AND video_id IS NULL AND redirect_id IS NULL) OR
    (ref_type = 'external' AND redirect_id IS NOT NULL AND app_id IS NULL AND video_id IS NULL AND tag_id IS NULL)
  );

-- ============== collection_items: DEFERRABLE UNIQUE on (collection_id, position) ==============
-- 故意不在 schema.prisma 写 @@unique;Prisma 普通 unique 与 deferrable 共存会拦掉 position 交换
ALTER TABLE "collection_items"
  ADD CONSTRAINT "collection_items_position_unique"
    UNIQUE ("collection_id", "position")
    DEFERRABLE INITIALLY DEFERRED;

-- ============== Extensions ==============
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- pg_trgm GIN 索引(P8 搜索接接此处;此处先建,空表无成本)
CREATE INDEX "apps_search_idx" ON "apps"
  USING GIN ((coalesce(name, '') || ' ' || coalesce(short_desc, '') || ' ' || coalesce(detail, '')) gin_trgm_ops);
CREATE INDEX "videos_search_idx" ON "videos"
  USING GIN ((coalesce(title, '') || ' ' || coalesce(short_desc, '') || ' ' || coalesce(detail, '')) gin_trgm_ops);
CREATE INDEX "guides_search_idx" ON "guides"
  USING GIN ((coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(body_md, '')) gin_trgm_ops);
```

把上面整段写入 `packages/db/prisma/migrations/<ts>_constraints/migration.sql`。

- [ ] **Step 3: 应用约束迁移**

```bash
pnpm --filter @ghome/db exec prisma migrate deploy
```

Expected: `1 migration applied`(就是 `_constraints`)。

- [ ] **Step 4: 验证 5 类约束生效(逐条 SQL)**

```bash
docker compose exec postgres psql -U ghome -d ghome <<'SQL'
-- A. categories.kind CHECK
SELECT conname FROM pg_constraint WHERE conname = 'categories_kind_check';
-- B. categories (id, kind) UNIQUE
SELECT conname FROM pg_constraint WHERE conname = 'categories_id_kind_unique';
-- C. apps.category_kind 是生成列
SELECT column_name, generation_expression
  FROM information_schema.columns
  WHERE table_name = 'apps' AND column_name = 'category_kind';
-- D. apps_category_kind_fk 复合 FK
SELECT conname, pg_get_constraintdef(oid)
  FROM pg_constraint WHERE conname = 'apps_category_kind_fk';
-- E. collection_items_ref_match CHECK
SELECT conname FROM pg_constraint WHERE conname = 'collection_items_ref_match';
-- F. collection_items_position_unique DEFERRABLE
SELECT conname, condeferrable, condeferred
  FROM pg_constraint WHERE conname = 'collection_items_position_unique';
-- G. pg_trgm extension
SELECT extname FROM pg_extension WHERE extname = 'pg_trgm';
-- H. GIN 索引
SELECT indexname FROM pg_indexes WHERE indexname IN ('apps_search_idx','videos_search_idx','guides_search_idx');
SQL
```

Expected:
- A: `categories_kind_check`
- B: `categories_id_kind_unique`
- C: `category_kind`(text)生成表达式 `'app'::text`
- D: 显示 `FOREIGN KEY (category_id, category_kind) REFERENCES categories(id, kind)`
- E: `collection_items_ref_match`
- F: `collection_items_position_unique` `t | t`(deferrable + deferred 都是 true)
- G: `pg_trgm`
- H: 三个索引名都列出

- [ ] **Step 5: 提交**

```bash
git add packages/db/prisma/migrations/
git commit -m "feat(db): add raw SQL constraints (CHECK / DEFERRABLE UNIQUE / generated cols / composite FK / pg_trgm)"
```

---

## Task 4 — PrismaClient 单例 + 重写 `@ghome/db` 公开 API

**Files:**
- Modify: `packages/db/src/index.ts`(重写,删占位)
- Create: `packages/db/src/client.ts`

- [ ] **Step 1: 写 `packages/db/src/client.ts`(单例,避免热重载下连接泄漏)**

```ts
import { PrismaClient } from "@prisma/client";

declare global {
  // eslint-disable-next-line no-var
  var __ghomePrisma: PrismaClient | undefined;
}

export const prisma: PrismaClient =
  globalThis.__ghomePrisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "production" ? ["warn", "error"] : ["query", "warn", "error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalThis.__ghomePrisma = prisma;
}
```

- [ ] **Step 2: 重写 `packages/db/src/index.ts`**

```ts
export { prisma } from "./client";
export type {
  App,
  Video,
  Guide,
  Category,
  Tag,
  Collection,
  CollectionItem,
  Redirect,
  ClickEvent,
  ClickDailyStat,
  AdminUser,
  AuditLogEntry,
  ContentStatus,
  CollectionKind,
  CollectionItemRefType,
  RedirectOwnerKind,
  Prisma,
} from "@prisma/client";
```

- [ ] **Step 3: 生成 Prisma Client(把类型物化到 `node_modules/.prisma`)**

```bash
pnpm --filter @ghome/db exec prisma generate
```

Expected: `✔ Generated Prisma Client (v5.x.x) to ./node_modules/.prisma/client`。

- [ ] **Step 4: 验证 typecheck**

```bash
pnpm --filter @ghome/db typecheck
```

Expected: 通过。

- [ ] **Step 5: 提交**

```bash
git add packages/db/src/
git commit -m "feat(db): add PrismaClient singleton and re-export model types"
```

---

## Task 5 — `url-policy` 库(TDD:先测后实现)

**Files:**
- Create: `packages/db/tests/url-policy.test.ts`
- Create: `packages/db/src/lib/url-policy.ts`
- Create: `packages/db/vitest.config.ts`

- [ ] **Step 1: 写 `packages/db/vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    globals: false,
    testTimeout: 10000,
  },
});
```

- [ ] **Step 2: 写失败测试 `packages/db/tests/url-policy.test.ts`**

```ts
import { describe, it, expect } from "vitest";
import { validateForRedirect, validateForWrite } from "../src/lib/url-policy";

describe("validateForRedirect (sync, no IO)", () => {
  it.each([
    "https://example.com/",
    "https://example.com/path?q=1",
    "http://公开站点.com/路径",
    "https://sub.domain.example/x",
  ])("accepts public https/http URL: %s", (url) => {
    expect(validateForRedirect(url).ok).toBe(true);
  });

  it.each([
    "javascript:alert(1)",
    "data:text/html,<script>1</script>",
    "file:///etc/passwd",
    "ftp://example.com/",
    "ssh://x.com",
    "about:blank",
  ])("rejects non-http(s) scheme: %s", (url) => {
    const r = validateForRedirect(url);
    expect(r.ok).toBe(false);
    expect(r.reason).toMatch(/protocol/i);
  });

  it.each([
    "https://localhost/",
    "http://192.0.2.1:8080/",
    "https://192.0.2.1/",
    "http://192.0.2.1/",
    "http://192.0.2.1/",
    "https://192.0.2.1/",
    "https://192.0.2.2/aws-mevendor_ata",
    "http://192.0.2.3/",
    "https://[::1]/",
    "https://localhost.localdomain/",
    "http://192.0.2.4/",  // CGNAT
  ])("rejects private/loopback/link-local literal: %s", (url) => {
    const r = validateForRedirect(url);
    expect(r.ok).toBe(false);
    expect(r.reason).toMatch(/private|loopback|link-local|literal/i);
  });

  it("rejects empty / non-URL strings", () => {
    expect(validateForRedirect("").ok).toBe(false);
    expect(validateForRedirect("not a url").ok).toBe(false);
  });

  it("rejects URLs longer than 2048 chars", () => {
    const long = "https://example.com/" + "a".repeat(2050);
    expect(validateForRedirect(long).ok).toBe(false);
  });

  it("rejects URLs with control chars / null bytes", () => {
    expect(validateForRedirect("https://example.com/\n").ok).toBe(false);
    expect(validateForRedirect("https://example.com/\x00").ok).toBe(false);
  });
});

describe("validateForWrite (async, includes DNS)", () => {
  it("accepts a public hostname (example.com)", async () => {
    const r = await validateForWrite("https://example.com/");
    expect(r.ok).toBe(true);
  });

  it("rejects unresolvable hostname within timeout", async () => {
    const r = await validateForWrite("https://this-domain-does-not-exist-xyzqq.invalid/");
    expect(r.ok).toBe(false);
    expect(r.reason).toMatch(/dns|resolve|nxdomain/i);
  }, 8000);

  it("rejects public-looking host that resolves to private IP", async () => {
    // 这个测试用一个故意指向私有段的真实 hostname。如果 DNS 抗 mock 困难,
    // 可以接受跳过该用例并加 `it.skip`,在 README 里说明手工验证步骤。
    // 备选 hostname:`localtest.me` → 192.0.2.1。
    const r = await validateForWrite("https://localtest.me/");
    expect(r.ok).toBe(false);
    expect(r.reason).toMatch(/private|loopback|literal/i);
  }, 8000);
});
```

- [ ] **Step 3: 跑测试,确认全 fail(实现还没写)**

```bash
pnpm --filter @ghome/db test
```

Expected: 大量 fail,因为 `src/lib/url-policy.ts` 还不存在。

- [ ] **Step 4: 实现 `packages/db/src/lib/url-policy.ts`**

```ts
import { promises as dns } from "node:dns";
import { isIP } from "node:net";

export type ValidationResult =
  | { ok: true }
  | { ok: false; reason: string };

const ALLOWED_PROTOCOLS = new Set(["http:", "https:"]);
const MAX_LEN = 2048;

const PRIVATE_IPV4_LITERAL_PATTERNS = [
  /^0\./,                                  // 192.0.2.3/8
  /^10\./,                                 // 192.0.2.1/8
  /^127\./,                                // 192.0.2.1/8 loopback
  /^169\.254\./,                           // 192.0.2.5/16 link-local
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,        // 192.0.2.1/12
  /^192\.168\./,                           // 192.0.2.1/16
  /^100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])\./, // 192.0.2.6/10 CGNAT
];

const HOSTNAME_LITERAL_BLACKLIST = new Set([
  "localhost",
  "localhost.localdomain",
]);

const IPV6_BLOCK_PREFIXES = ["::1", "fc", "fd", "fe8", "fe9", "fea", "feb"];

function isPrivateIPv4(ip: string): boolean {
  return PRIVATE_IPV4_LITERAL_PATTERNS.some((re) => re.test(ip));
}

function isPrivateIPv6(ip: string): boolean {
  const lower = ip.toLowerCase();
  if (lower === "::1") return true;
  if (lower.startsWith("fc") || lower.startsWith("fd")) return true;          // fc00::/7 ULA
  if (lower.startsWith("fe8") || lower.startsWith("fe9") ||
      lower.startsWith("fea") || lower.startsWith("feb")) return true;        // fe80::/10 link-local
  return false;
}

function isPrivateIP(ip: string): boolean {
  const ver = isIP(ip);
  if (ver === 4) return isPrivateIPv4(ip);
  if (ver === 6) return isPrivateIPv6(ip);
  return false;
}

function staticChecks(url: string): ValidationResult {
  if (!url || url.length === 0) return { ok: false, reason: "empty URL" };
  if (url.length > MAX_LEN) return { ok: false, reason: "URL too long" };
  // 控制字符 / null
  for (let i = 0; i < url.length; i++) {
    const c = url.charCodeAt(i);
    if (c < 0x20 || c === 0x7f) {
      return { ok: false, reason: "URL contains control characters" };
    }
  }

  let parsed: URL;
  try { parsed = new URL(url); } catch { return { ok: false, reason: "not a valid URL" }; }
  if (!ALLOWED_PROTOCOLS.has(parsed.protocol)) {
    return { ok: false, reason: `protocol ${parsed.protocol} not allowed` };
  }

  const host = parsed.hostname.toLowerCase();
  // strip IPv6 brackets
  const hostNoBrackets = host.startsWith("[") && host.endsWith("]")
    ? host.slice(1, -1)
    : host;

  if (HOSTNAME_LITERAL_BLACKLIST.has(host)) {
    return { ok: false, reason: `hostname literal '${host}' blocked` };
  }

  // IP literal in host
  if (isIP(hostNoBrackets)) {
    if (isPrivateIP(hostNoBrackets)) {
      return { ok: false, reason: `IP literal ${hostNoBrackets} is private/loopback/link-local` };
    }
  }

  return { ok: true };
}

export function validateForRedirect(url: string): ValidationResult {
  return staticChecks(url);
}

export async function validateForWrite(url: string): Promise<ValidationResult> {
  const s = staticChecks(url);
  if (!s.ok) return s;

  let parsed: URL;
  try { parsed = new URL(url); } catch { return { ok: false, reason: "not a valid URL" }; }
  const host = parsed.hostname;
  const hostNoBrackets = host.startsWith("[") && host.endsWith("]")
    ? host.slice(1, -1)
    : host;
  // 已经是 IP literal 就不用再 DNS
  if (isIP(hostNoBrackets)) return { ok: true };

  // DNS resolve with 2s timeout
  try {
    const addrs = await Promise.race([
      dns.lookup(hostNoBrackets, { all: true }),
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error("dns timeout")), 2000)),
    ]);
    for (const a of addrs as Array<{ address: string }>) {
      if (isPrivateIP(a.address)) {
        return { ok: false, reason: `host ${hostNoBrackets} resolves to private/loopback IP ${a.address}` };
      }
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, reason: `dns failure: ${(e as Error).message}` };
  }
}
```

- [ ] **Step 5: 跑测试,期待全过**

```bash
pnpm --filter @ghome/db test
```

Expected: 所有 url-policy 测试 pass。如果"`localtest.me` → 192.0.2.1"那个用例因 DNS 配置不一致失败,允许临时 `it.skip` 并在 task report 里注明。

- [ ] **Step 6: 提交**

```bash
git add packages/db/tests/url-policy.test.ts packages/db/src/lib/url-policy.ts packages/db/vitest.config.ts
git commit -m "feat(db): add url-policy with static + DNS-aware validators (TDD)"
```

---

## Task 6 — Seed 数据(content):apps + videos + categories

**Files:**
- Create: `packages/db/seed/data/apps.ts`
- Create: `packages/db/seed/data/videos.ts`
- Create: `packages/db/seed/data/app-cats.ts`
- Create: `packages/db/seed/data/video-cats.ts`

> **来源**:`docs/ghome.html` 的 `APPS` (:525)、`VIDEOS` (:579)、`APP_CATS` (:537,**排除 `id='all'`**)、`CATEGORIES` (:602)。
> **任务范围**:把这四个 JS 数组**手工抄成 TS**(typed),不上 HTML 解析。

- [ ] **Step 1: 写 `seed/data/app-cats.ts`(3 条)**

```ts
export interface AppCatSeed {
  slug: string;
  label: string;
  description: string;
  sortOrder: number;
}

export const APP_CATS: AppCatSeed[] = [
  { slug: "social", label: "社交交友", description: "交友、社交、附近的人类 App", sortOrder: 0 },
  { slug: "life",   label: "生活实用", description: "健身、旅行、心理、活动等生活实用类 App", sortOrder: 1 },
  { slug: "media",  label: "娱乐资讯", description: "资讯、艺术、文化等内容平台", sortOrder: 2 },
];
```

> 原型 `APP_CATS[0]` 的 `id='all'` 是前端筛选 tab,**不入库**(spec §4.5)。

- [ ] **Step 2: 写 `seed/data/video-cats.ts`(6 条)**

```ts
export interface VideoCatSeed {
  slug: string;
  label: string;
  description: string;
  sortOrder: number;
}

export const VIDEO_CATS: VideoCatSeed[] = [
  { slug: "vlog",      label: "Vlog", description: "生活记录、日常分享、城市漫游等主题的 Vlog 视频内容", sortOrder: 0 },
  { slug: "fitness",   label: "健身", description: "训练动作、饮食计划、身材管理与健身励志类视频",         sortOrder: 1 },
  { slug: "travel",    label: "旅行", description: "国内外旅行指南、风光记录、文化体验等主题视频",         sortOrder: 2 },
  { slug: "interview", label: "访谈", description: "情感、职场、成长、家庭等深度对话访谈内容",             sortOrder: 3 },
  { slug: "life",      label: "生活", description: "穿搭、美食、宅家、技巧等生活方式类视频",               sortOrder: 4 },
  { slug: "campus",    label: "校园", description: "校园生活、毕业记录、宿舍改造等青春主题",               sortOrder: 5 },
];
```

- [ ] **Step 3: 写 `seed/data/apps.ts`(9 条)**

把原型 `APPS` 数组逐字段翻译成 TS object。Schema 保留所有字段;`tags` 数组留作 T9 在 seed 里转 AppTag 关系。`categorySlug` 必填,对应 `app-cats.ts` 的 slug。

```ts
export interface AppSeed {
  slug: string;
  name: string;
  iconKey: string;
  gradientKey: string;
  categorySlug: "social" | "life" | "media";
  shortDesc: string;
  detail: string;
  highlights: string[];
  audience: string;
  features: string;
  platform: string;
  size: string;
  rating: string;       // 字符串保留 — schema 是 text
  usersLabel: string;
  tags: string[];       // 中文 label,T7 的 tag map 必须覆盖
}

export const APPS: AppSeed[] = [
  {
    slug: "broconnect",
    name: "BroConnect",
    iconKey: "i-chat",
    gradientKey: "g-brand",
    categorySlug: "social",
    shortDesc: "主打附近交友与真实动态分享的社交软件,快速建立连接。",
    detail: "BroConnect 基于 LBS 技术打造真实可信的男同社交体验,强调「真人、真实、真交朋友」。所有用户需完成实名与动态认证后才能发布与私聊,有效过滤虚假账号。动态广场以生活分享为主,不允许任何擦边内容。",
    highlights: [
      "实名 + 人脸双认证机制",
      "地理围栏动态广场,兴趣圈层清晰",
      "消息阅后即焚与隐身模式",
      "严格社区公约,违规 24h 内处理",
      "支持 150+ 国家地区用户",
    ],
    audience: "希望快速结识附近新朋友的活跃人士",
    features: "精准定位 · 真实认证 · 即时聊天",
    platform: "iOS / Android",
    size: "56MB",
    rating: "4.7",
    usersLabel: "800万+",
    tags: ["社交", "附近的人", "动态广场"],
  },
  {
    slug: "matematch",
    name: "MateMatch",
    iconKey: "i-heart",
    gradientKey: "g-rose",
    categorySlug: "social",
    shortDesc: "基于性格测试与深度匹配的长期关系交友平台,拒绝快餐式社交。",
    detail: "MateMatch 用 MBTI 与 28 维度性格雷达评估你的情感偏好,推送真正契合的对象。主打「慢社交」,每日仅推荐 3 人,强调深度对话而非海量滑动。平台定位严肃长期关系,不支持一夜情或线下速配。",
    highlights: [
      "28 维度深度匹配算法",
      "每日 3 人精准推荐",
      "情感话题社区,写日记打卡",
      "认证心理咨询师入驻",
      "匿名通话保护隐私",
    ],
    audience: "寻找稳定长期关系的单身人士",
    features: "深度匹配 · 隐私保护 · 情感话题",
    platform: "iOS / Android",
    size: "48MB",
    rating: "4.8",
    usersLabel: "210万+",
    tags: ["走心交友", "恋爱", "性格测试"],
  },
  {
    slug: "gymbros",
    name: "GymBros",
    iconKey: "i-dumbbell",
    gradientKey: "g-fire",
    categorySlug: "life",
    shortDesc: "专为喜欢健身的运动达人打造的运动与交友专属社区。",
    detail: "GymBros 把健身社交和运动工具打包在一起,既是运动日记,又是找搭子的地方。内置 500+ 动作库、智能训练计划、周期性打卡榜单,同城健身房专属圈子让你找到附近运动伙伴。",
    highlights: [
      "500+ 动作标准示范库",
      "AI 训练计划自动生成",
      "同城健身房圈子",
      "饮食记录 + TDEE 智能计算",
      "身材变化时间轴对比",
    ],
    audience: "热爱健身、寻找运动搭子的达人",
    features: "健身打卡 · 结伴锻炼 · 体型筛选",
    platform: "iOS / Android",
    size: "62MB",
    rating: "4.6",
    usersLabel: "150万+",
    tags: ["健身", "运动", "肌肉圈"],
  },
  {
    slug: "travelg",
    name: "TravelG",
    iconKey: "i-map",
    gradientKey: "g-sky",
    categorySlug: "life",
    shortDesc: "全球同志友好旅行指南与拼房搭子寻找工具,让出行更安心。",
    detail: "TravelG 整合全球 120+ 城市的同志友好商家、酒店、餐厅与活动信息,并提供拼房/拼团功能降低出行成本。所有商家均经过实地或社区反馈验证,数据由官方团队与志愿者共同维护。",
    highlights: [
      "120+ 城市友好地图",
      "官方认证民宿拼房",
      "全球 Pride 活动日历",
      "境外安全指南 & 法律速查",
      "旅行日记云端同步",
    ],
    audience: "喜欢探索世界、寻找旅行搭子的人",
    features: "友好商家地图 · 拼房大厅 · 旅行日记",
    platform: "iOS / Android",
    size: "72MB",
    rating: "4.9",
    usersLabel: "85万+",
    tags: ["旅行", "攻略", "拼团"],
  },
  {
    slug: "voicechat",
    name: "VoiceChat",
    iconKey: "i-mic",
    gradientKey: "g-grape",
    categorySlug: "social",
    shortDesc: "匿名语音连麦,用声音寻找共鸣的灵魂伴侣,深夜不孤单。",
    detail: "VoiceChat 不需要头像与真实身份,只凭声音结交朋友。随机 1v1 连麦、多人房间派对、声纹相似度匹配,全套都有。后台 AI 实时识别违规内容,保障纯净社交空间。",
    highlights: [
      "随机语音连麦",
      "多人派对房(KTV / 狼人杀 / 闲聊)",
      "声纹相似度推荐",
      "AI 实时违规检测",
      "每日免费 60 分钟通话",
    ],
    audience: "声控、不喜欢露脸的社恐用户或深夜感性人群",
    features: "随机匹配 · 多人派对 · 变声滤镜",
    platform: "iOS / Android",
    size: "44MB",
    rating: "4.7",
    usersLabel: "320万+",
    tags: ["语音交友", "匿名", "派对"],
  },
  {
    slug: "rainbownews",
    name: "RainbowNews",
    iconKey: "i-news",
    gradientKey: "g-leaf",
    categorySlug: "media",
    shortDesc: "聚焦 LGBTQ+ 群体的每日新闻资讯与生活方式数字杂志。",
    detail: "RainbowNews 是一本数字化的 LGBTQ+ 杂志,每天推送 8-12 条精选新闻,涵盖全球平权、文化影视、人物故事、科普健康等栏目。长期合作记者团队分布在 30+ 国家。",
    highlights: [
      "每日速递 + 周刊深度",
      "独家人物专访",
      "线上沙龙直播",
      "高品质电子书库",
      "无弹窗广告,纯净阅读",
    ],
    audience: "关注群体文化与全球热点发展的人士",
    features: "每日速递 · 深度专栏 · 线上沙龙",
    platform: "iOS / Android",
    size: "38MB",
    rating: "4.8",
    usersLabel: "60万+",
    tags: ["资讯", "杂志", "文化"],
  },
  {
    slug: "datenight",
    name: "DateNight",
    iconKey: "i-calendar",
    gradientKey: "g-gold",
    categorySlug: "life",
    shortDesc: "周末活动与同城线下聚会报名平台,打破线上社交壁垒。",
    detail: "DateNight 每周为同城用户精选 10-30 场主题活动:桌游、观影、读书会、徒步、烘焙课、脱口秀。活动由平台与在地主理人共同策划,均为安全合规的友好空间。",
    highlights: [
      "每周 30+ 同城活动",
      "扫码签到 + 活动评价",
      "主理人 / 场地认证",
      "活动保险覆盖",
      "社群运营指南",
    ],
    audience: "喜欢线下社交、参加派对与桌游的活跃分子",
    features: "活动报名 · 同城社群 · 扫码签到",
    platform: "iOS / Android",
    size: "52MB",
    rating: "4.6",
    usersLabel: "95万+",
    tags: ["线下活动", "聚会", "同城"],
  },
  {
    slug: "safezone",
    name: "SafeZone",
    iconKey: "i-shield",
    gradientKey: "g-mint",
    categorySlug: "life",
    shortDesc: "提供心理咨询、健康科普与匿名倾诉的温暖互助社区。",
    detail: "SafeZone 邀请 200+ 持证心理咨询师与健康科普专家常驻,提供匿名咨询、文字树洞、危机热线与健康知识库。所有聊天记录端到端加密,平台不保留副本。",
    highlights: [
      "200+ 持证咨询师",
      "端到端加密聊天",
      "24h 危机援助热线",
      "匿名树洞 + AI 陪伴",
      "公益咨询名额每日开放",
    ],
    audience: "需要情感支持与专业健康建议的用户",
    features: "专业问答 · 树洞倾诉 · 在线咨询",
    platform: "iOS / Android",
    size: "40MB",
    rating: "4.9",
    usersLabel: "72万+",
    tags: ["心理健康", "科普", "医疗"],
  },
  {
    slug: "prideart",
    name: "PrideArt",
    iconKey: "i-palette",
    gradientKey: "g-pink",
    categorySlug: "media",
    shortDesc: "LGBTQ+ 艺术家作品集与独立影像展映的文化内容平台。",
    detail: "PrideArt 是一个为 LGBTQ+ 艺术家提供展示空间的平台,收录摄影、插画、独立电影、诗歌与音乐作品。每月策划主题展映,支持艺术家直连关注者,购买作品 / 门票一站式完成。",
    highlights: [
      "500+ 认证艺术家入驻",
      "每月主题线上展映",
      "作品收藏 & 限量购买",
      "艺术家直连粉丝问答",
      "无版权纠纷合规授权体系",
    ],
    audience: "热爱独立艺术与文化内容的审美派用户",
    features: "作品集 · 线上展映 · 艺术家专访",
    platform: "iOS / Android",
    size: "58MB",
    rating: "4.8",
    usersLabel: "28万+",
    tags: ["艺术", "影像", "文化"],
  },
];
```

- [ ] **Step 4: 写 `seed/data/videos.ts`(20 条)**

照原型 `VIDEOS` (:579-599) 逐条翻译。每条字段:`slug`(原型 id 如 `'v01'`,seed 时直接用)、`title`、`emoji`、`coverKey`(原型 cover)、`duration`(原型 dur)、`viewsLabel`、`likesLabel`(原型 likes 是字符串数字,直接保留)、`publishedDate`(原型 date)、`categorySlug`(原型 cat)、`shortDesc`(原型 desc)、`detail`(P1 暂用 desc 的同样文本,P5 admin 编辑时再填长文)、`tags`。

```ts
export interface VideoSeed {
  slug: string;
  title: string;
  emoji: string;
  coverKey: string;
  duration: string;
  viewsLabel: string;
  likesLabel: string;
  publishedDate: string; // ISO date 'YYYY-MM-DD'
  categorySlug: "vlog" | "fitness" | "travel" | "interview" | "life" | "campus";
  shortDesc: string;
  detail: string;
  tags: string[];
}

export const VIDEOS: VideoSeed[] = [
  { slug:"v01", title:"都市生活Vlog — 在上海的周末日常", emoji:"🏙", coverKey:"city",      duration:"12:34", viewsLabel:"15.2万", likesLabel:"3821",  publishedDate:"2026-04-28", categorySlug:"vlog",      shortDesc:"周末的上海、咖啡馆、市集、夕阳下的外滩。一条平静放松的都市生活记录。", detail:"周末的上海、咖啡馆、市集、夕阳下的外滩。一条平静放松的都市生活记录。", tags:["Vlog","都市","生活方式"] },
  { slug:"v02", title:"健身房打卡 — 胸肌训练全记录",     emoji:"🏋", coverKey:"fitness",   duration:"08:20", viewsLabel:"22.7万", likesLabel:"6210",  publishedDate:"2026-04-25", categorySlug:"fitness",   shortDesc:"跟练一条完整的胸肌日训练,包含热身、动作示范与放松拉伸。", detail:"跟练一条完整的胸肌日训练,包含热身、动作示范与放松拉伸。", tags:["健身","训练","打卡"] },
  { slug:"v03", title:"冰岛旅行日记 — 极光追光之旅",     emoji:"✈",  coverKey:"travel",    duration:"18:45", viewsLabel:"38.1万", likesLabel:"9920",  publishedDate:"2026-04-22", categorySlug:"travel",    shortDesc:"用 7 天时间横跨冰岛,从黄金圈到钻石沙滩,最后在极光下露营。", detail:"用 7 天时间横跨冰岛,从黄金圈到钻石沙滩,最后在极光下露营。", tags:["旅行","Vlog","风光"] },
  { slug:"v04", title:"情感访谈:长期关系如何保鲜",       emoji:"🎤", coverKey:"interview", duration:"24:10", viewsLabel:"12.5万", likesLabel:"4012",  publishedDate:"2026-04-20", categorySlug:"interview", shortDesc:"两对在一起五年以上的情侣分享他们保持关系新鲜的小秘密。", detail:"两对在一起五年以上的情侣分享他们保持关系新鲜的小秘密。", tags:["访谈","情感","长期关系"] },
  { slug:"v05", title:"校园时光 — 毕业季留念",           emoji:"🎓", coverKey:"campus",    duration:"06:30", viewsLabel:"8.7万",  likesLabel:"2180",  publishedDate:"2026-04-18", categorySlug:"campus",    shortDesc:"一条关于校园最后一个夏天的温柔记录,与朋友们的临别留影。", detail:"一条关于校园最后一个夏天的温柔记录,与朋友们的临别留影。", tags:["校园","毕业","Vlog"] },
  { slug:"v06", title:"都市夜行 — 深夜便利店的故事",     emoji:"🌃", coverKey:"city",      duration:"04:55", viewsLabel:"6.2万",  likesLabel:"1540",  publishedDate:"2026-04-17", categorySlug:"vlog",      shortDesc:"凌晨两点的便利店,是都市里最温柔的避风港。", detail:"凌晨两点的便利店,是都市里最温柔的避风港。", tags:["Vlog","都市","夜晚"] },
  { slug:"v07", title:"健康饮食一周挑战",                 emoji:"🥗", coverKey:"food",      duration:"15:20", viewsLabel:"18.4万", likesLabel:"5120",  publishedDate:"2026-04-15", categorySlug:"life",      shortDesc:"连续 7 天记录低脂高蛋白饮食,附赠 5 个简易食谱。", detail:"连续 7 天记录低脂高蛋白饮食,附赠 5 个简易食谱。", tags:["生活","饮食","健康"] },
  { slug:"v08", title:"京都和服体验",                     emoji:"🏯", coverKey:"culture",   duration:"10:40", viewsLabel:"25.3万", likesLabel:"7210",  publishedDate:"2026-04-12", categorySlug:"travel",    shortDesc:"换上和服走在京都的青石板路,感受一次穿越时光的慢旅行。", detail:"换上和服走在京都的青石板路,感受一次穿越时光的慢旅行。", tags:["旅行","文化","日本"] },
  { slug:"v09", title:"CP 日常:一起做饭",                 emoji:"🍳", coverKey:"life",      duration:"07:15", viewsLabel:"32.8万", likesLabel:"11200", publishedDate:"2026-04-10", categorySlug:"life",      shortDesc:"周末下午的厨房,是我们最自在的时间。一条治愈系的日常小片。", detail:"周末下午的厨房,是我们最自在的时间。一条治愈系的日常小片。", tags:["情感","生活","CP向"] },
  { slug:"v10", title:"自拍教程 — 如何拍出好看的照片",   emoji:"📸", coverKey:"fashion",   duration:"09:28", viewsLabel:"14.7万", likesLabel:"3980",  publishedDate:"2026-04-08", categorySlug:"life",      shortDesc:"从构图到光线到姿势,教你用手机拍出高级感自拍。", detail:"从构图到光线到姿势,教你用手机拍出高级感自拍。", tags:["生活","技巧","摄影"] },
  { slug:"v11", title:"健身前后对比 — 半年蜕变",         emoji:"💪", coverKey:"fitness",   duration:"12:00", viewsLabel:"42.1万", likesLabel:"15200", publishedDate:"2026-04-05", categorySlug:"fitness",   shortDesc:"从瘦弱到精瘦型的半年时间,记录每周的变化与心得。", detail:"从瘦弱到精瘦型的半年时间,记录每周的变化与心得。", tags:["健身","励志","蜕变"] },
  { slug:"v12", title:"穿搭分享 — 夏日简约风",           emoji:"👕", coverKey:"fashion",   duration:"05:45", viewsLabel:"11.3万", likesLabel:"3021",  publishedDate:"2026-04-02", categorySlug:"life",      shortDesc:"5 套夏日通勤 + 周末穿搭,全部选用基础款易于复制。", detail:"5 套夏日通勤 + 周末穿搭,全部选用基础款易于复制。", tags:["时尚","穿搭","夏季"] },
  { slug:"v13", title:"访谈:出柜后和父母的关系",         emoji:"💬", coverKey:"interview", duration:"22:30", viewsLabel:"28.6万", likesLabel:"9840",  publishedDate:"2026-03-30", categorySlug:"interview", shortDesc:"三位不同年龄的嘉宾分享出柜之后,和父母重建关系的真实历程。", detail:"三位不同年龄的嘉宾分享出柜之后,和父母重建关系的真实历程。", tags:["访谈","情感","家庭"] },
  { slug:"v14", title:"海边落日 Vlog",                    emoji:"🌅", coverKey:"travel",    duration:"06:20", viewsLabel:"9.8万",  likesLabel:"2510",  publishedDate:"2026-03-28", categorySlug:"travel",    shortDesc:"无对白,一支纯粹记录日落的短片,搭配钢琴配乐。", detail:"无对白,一支纯粹记录日落的短片,搭配钢琴配乐。", tags:["旅行","Vlog","风光"] },
  { slug:"v15", title:"周末宅家日常 — 咖啡与电影",       emoji:"☕", coverKey:"life",      duration:"08:50", viewsLabel:"7.2万",  likesLabel:"1830",  publishedDate:"2026-03-26", categorySlug:"life",      shortDesc:"下雨天,窗边冲一杯手冲咖啡,重看一部老电影。", detail:"下雨天,窗边冲一杯手冲咖啡,重看一部老电影。", tags:["生活","Vlog","治愈"] },
  { slug:"v16", title:"校园宿舍改造",                     emoji:"🛏", coverKey:"campus",    duration:"14:10", viewsLabel:"16.5万", likesLabel:"4420",  publishedDate:"2026-03-24", categorySlug:"campus",    shortDesc:"预算 800 元把普通宿舍改造成自己的小天地,附清单。", detail:"预算 800 元把普通宿舍改造成自己的小天地,附清单。", tags:["校园","改造","DIY"] },
  { slug:"v17", title:"自由潜水第一次体验",               emoji:"🐠", coverKey:"travel",    duration:"11:25", viewsLabel:"19.8万", likesLabel:"5710",  publishedDate:"2026-03-22", categorySlug:"travel",    shortDesc:"巴厘岛 AIDA 2 的 3 天课程记录,从紧张到自如的心路历程。", detail:"巴厘岛 AIDA 2 的 3 天课程记录,从紧张到自如的心路历程。", tags:["旅行","运动","挑战"] },
  { slug:"v18", title:"减脂餐一周食谱",                   emoji:"🍱", coverKey:"food",      duration:"13:30", viewsLabel:"21.4万", likesLabel:"6320",  publishedDate:"2026-03-20", categorySlug:"fitness",   shortDesc:"7 天不重样的减脂餐做法,均可 20 分钟完成。", detail:"7 天不重样的减脂餐做法,均可 20 分钟完成。", tags:["健身","饮食","减脂"] },
  { slug:"v19", title:"城市骑行 Vlog — 北京胡同",         emoji:"🚴", coverKey:"city",      duration:"09:15", viewsLabel:"10.2万", likesLabel:"2810",  publishedDate:"2026-03-18", categorySlug:"vlog",      shortDesc:"一辆自行车穿过南锣鼓巷与钟楼,记录一个工作日的慢下午。", detail:"一辆自行车穿过南锣鼓巷与钟楼,记录一个工作日的慢下午。", tags:["Vlog","骑行","北京"] },
  { slug:"v20", title:"阅读分享:推荐 5 本 LGBTQ+ 小说",   emoji:"📚", coverKey:"culture",   duration:"16:00", viewsLabel:"13.8万", likesLabel:"4720",  publishedDate:"2026-03-15", categorySlug:"interview", shortDesc:"从《亚瑟之死》到《月光男孩》,五本值得反复读的作品。", detail:"从《亚瑟之死》到《月光男孩》,五本值得反复读的作品。", tags:["文化","阅读","推荐"] },
];
```

- [ ] **Step 5: 验证 typecheck**

```bash
pnpm --filter @ghome/db typecheck
```

Expected: 通过(seed/ 目录尚不被任何运行时引用,但被 tsc 包含)。

- [ ] **Step 6: 提交**

```bash
git add packages/db/seed/data/apps.ts packages/db/seed/data/videos.ts \
        packages/db/seed/data/app-cats.ts packages/db/seed/data/video-cats.ts
git commit -m "feat(db): seed data — 9 apps, 20 videos, 3 app cats, 6 video cats"
```

---

## Task 7 — Seed 数据(taxonomy + curation):tags 全并集 + topics

**Files:**
- Create: `packages/db/seed/data/tags.ts`
- Create: `packages/db/seed/data/topics.ts`

- [ ] **Step 1: 写 `seed/data/tags.ts` — 全并集 label→slug 映射(63 条)**

```ts
/**
 * 全并集 = ALL_TAGS ∪ APPS[*].tags ∪ VIDEOS[*].tags(去重)。
 * 缺映射时 seed 直接 fail。slug 必须 /^[a-z0-9-]+$/。
 */
export const TAG_SLUGS: Record<string, string> = {
  // ---- ALL_TAGS(原型 :611,16 条)----
  "男同视频": "gay-videos",
  "Vlog": "vlog",
  "LGBTQ+": "lgbtq",
  "生活方式": "lifestyle",
  "情感": "emotion",
  "都市": "urban",
  "校园": "campus-tag",          // 注:与 video category 'campus' slug 区分(category 在 categories 表,tags.slug 不冲突)
  "高颜值": "good-looking",
  "CP向": "couple",
  "健身": "fitness-tag",         // 同理:与 video category slug 区分
  "旅行": "travel-tag",
  "访谈": "interview-tag",
  "时尚": "fashion",
  "饮食": "food",
  "文化": "culture",
  "阅读": "reading",

  // ---- App-only tags(23 条)----
  "社交": "social",
  "附近的人": "nearby",
  "动态广场": "feed",
  "走心交友": "serious-dating",
  "恋爱": "romance",
  "性格测试": "personality-test",
  "运动": "sports",
  "肌肉圈": "muscle-circle",
  "攻略": "travel-guide",
  "拼团": "group-buy",
  "语音交友": "voice-chat",
  "匿名": "anonymous",
  "派对": "party",
  "资讯": "news",
  "杂志": "magazine",
  "线下活动": "offline-events",
  "聚会": "gathering",
  "同城": "local",
  "心理健康": "mental-health",
  "科普": "science-popular",
  "医疗": "medical",
  "艺术": "art",
  "影像": "imagery",

  // ---- Video-only tags(24 条)----
  "训练": "training",
  "打卡": "check-in",
  "风光": "scenery",
  "长期关系": "long-term-relationship",
  "毕业": "graduation",
  "夜晚": "night",
  "生活": "daily-life",
  "健康": "health",
  "日本": "japan",
  "技巧": "skills",
  "摄影": "photography",
  "励志": "inspiring",
  "蜕变": "transformation",
  "穿搭": "outfit",
  "夏季": "summer",
  "家庭": "family",
  "治愈": "healing",
  "改造": "remodel",
  "DIY": "diy",
  "挑战": "challenge",
  "减脂": "weight-loss",
  "骑行": "cycling",
  "北京": "beijing",
  "推荐": "recommendation",
};

/**
 * ALL_TAGS 来源(原型 :611),`hot-tags` 榜单遍历这 16 个 label。
 */
export const ALL_TAGS_LABELS: readonly string[] = [
  "男同视频","Vlog","LGBTQ+","生活方式","情感","都市","校园","高颜值",
  "CP向","健身","旅行","访谈","时尚","饮食","文化","阅读",
];
```

> 设计说明:`'校园'` / `'健身'` / `'旅行'` / `'访谈'` 在 categories 表(kind=video)也有同名 slug。
> 由于 `tags` 与 `categories` 是两张独立表,各自的 `slug` UNIQUE 互不影响,但为减少混淆,
> 这几个标签 slug 后缀 `-tag` / `-tag` 作区别。运营在 admin 看到这些时,以 label 为准识别。

- [ ] **Step 2: 写 `seed/data/topics.ts`(6 条 topic + items)**

```ts
import type { CollectionItemRefType } from "@prisma/client";

export interface TopicItemSpec {
  refType: Extract<CollectionItemRefType, "video">;
  videoSlug: string;
  position: number;
}

export interface TopicSeed {
  slug: string;
  title: string;
  description: string;
  coverKey: string | null;     // 原型用 cover gradient,此处放 gradient 字符串
  sortOrder: number;
  items: TopicItemSpec[];
}

export const TOPICS: TopicSeed[] = [
  {
    slug: "entry",
    title: "男同视频入门推荐",
    description: "新用户必看的 10 个主题合集,从 Vlog 到访谈一网打尽",
    coverKey: "linear-gradient(135deg,#667eea,#764ba2)",
    sortOrder: 0,
    items: [
      { refType: "video", videoSlug: "v01", position: 0 },
      { refType: "video", videoSlug: "v04", position: 1 },
      { refType: "video", videoSlug: "v05", position: 2 },
      { refType: "video", videoSlug: "v07", position: 3 },
      { refType: "video", videoSlug: "v09", position: 4 },
    ],
  },
  {
    slug: "handsome",
    title: "高颜值男同视频合集",
    description: "编辑精选:画面与气质并存的创作者作品",
    coverKey: "linear-gradient(135deg,#f093fb,#f5576c)",
    sortOrder: 1,
    items: [
      { refType: "video", videoSlug: "v01", position: 0 },
      { refType: "video", videoSlug: "v06", position: 1 },
      { refType: "video", videoSlug: "v09", position: 2 },
      { refType: "video", videoSlug: "v12", position: 3 },
      { refType: "video", videoSlug: "v15", position: 4 },
    ],
  },
  {
    slug: "vlog",
    title: "男同 Vlog 内容合集",
    description: "最具生活感的 Vlog 推荐,治愈一整个疲惫的下午",
    coverKey: "linear-gradient(135deg,#4facfe,#00f2fe)",
    sortOrder: 2,
    items: [
      { refType: "video", videoSlug: "v01", position: 0 },
      { refType: "video", videoSlug: "v05", position: 1 },
      { refType: "video", videoSlug: "v06", position: 2 },
      { refType: "video", videoSlug: "v14", position: 3 },
      { refType: "video", videoSlug: "v19", position: 4 },
    ],
  },
  {
    slug: "lifestyle",
    title: "男同生活方式视频合集",
    description: "从穿搭到饮食,从宅家到骑行,生活方式全指南",
    coverKey: "linear-gradient(135deg,#fa709a,#fee140)",
    sortOrder: 3,
    items: [
      { refType: "video", videoSlug: "v07", position: 0 },
      { refType: "video", videoSlug: "v10", position: 1 },
      { refType: "video", videoSlug: "v12", position: 2 },
      { refType: "video", videoSlug: "v15", position: 3 },
      { refType: "video", videoSlug: "v16", position: 4 },
    ],
  },
  {
    slug: "emotion",
    title: "男同情感向视频推荐",
    description: "关于爱、陪伴、家庭与成长的温暖故事",
    coverKey: "linear-gradient(135deg,#43e97b,#38f9d7)",
    sortOrder: 4,
    items: [
      { refType: "video", videoSlug: "v04", position: 0 },
      { refType: "video", videoSlug: "v09", position: 1 },
      { refType: "video", videoSlug: "v13", position: 2 },
    ],
  },
  {
    slug: "platform",
    title: "LGBTQ+ 内容平台推荐",
    description: "Ghome 精选的优质内容平台指引,合规合法出海",
    coverKey: "linear-gradient(135deg,#a8edea,#fed6e3)",
    sortOrder: 5,
    items: [
      { refType: "video", videoSlug: "v20", position: 0 },
    ],
  },
];
```

- [ ] **Step 3: 验证 typecheck**

```bash
pnpm --filter @ghome/db typecheck
```

- [ ] **Step 4: 提交**

```bash
git add packages/db/seed/data/tags.ts packages/db/seed/data/topics.ts
git commit -m "feat(db): seed data — 63 tags (full union with English slug map) and 6 topics"
```

---

## Task 8 — Seed 数据(rankings + guides + helpers)

**Files:**
- Create: `packages/db/seed/data/guides.ts`
- Create: `packages/db/seed/data/guide-bodies.ts`
- Create: `packages/db/seed/helpers/parse-labels.ts`
- Create: `packages/db/seed/helpers/rankings.ts`

- [ ] **Step 1: 写 `seed/helpers/parse-labels.ts`**

```ts
/**
 * 把 '15.2万' / '800万+' / '12.5万' 解析成数字。
 * 支持:'万' (10000)、'亿' (100000000)、'+'(忽略)、纯数字字符串。
 */
export function parseChineseCount(s: string): number {
  if (!s) return 0;
  const trimmed = s.replace(/\+$/, "").trim();
  let multiplier = 1;
  let stripped = trimmed;
  if (trimmed.endsWith("亿")) { multiplier = 1e8;  stripped = trimmed.slice(0, -1); }
  else if (trimmed.endsWith("万")) { multiplier = 1e4; stripped = trimmed.slice(0, -1); }
  const n = parseFloat(stripped);
  if (Number.isNaN(n)) return 0;
  return Math.round(n * multiplier);
}

/** rating '4.7' → 4.7 (number),失败返 0 */
export function parseRating(s: string): number {
  const n = parseFloat(s);
  return Number.isNaN(n) ? 0 : n;
}

/** likes '11200' → 11200 (number) */
export function parseLikes(s: string): number {
  const n = parseInt(s, 10);
  return Number.isNaN(n) ? 0 : n;
}
```

- [ ] **Step 2: 写 `seed/helpers/rankings.ts`(从 apps/videos/tags 数据计算 6 个 ranking specs)**

```ts
import { APPS } from "../data/apps";
import { VIDEOS } from "../data/videos";
import { ALL_TAGS_LABELS } from "../data/tags";
import { parseChineseCount, parseRating, parseLikes } from "./parse-labels";

export interface RankingItemSpec {
  refType: "app" | "video" | "tag";
  appSlug?: string;
  videoSlug?: string;
  tagLabel?: string;
  position: number;
}

export interface RankingSeed {
  slug: string;
  title: string;
  description: string;
  sortOrder: number;
  items: RankingItemSpec[];
}

function topVideos(by: (v: typeof VIDEOS[number]) => number, take = 8): RankingItemSpec[] {
  return [...VIDEOS]
    .sort((a, b) => by(b) - by(a))
    .slice(0, take)
    .map((v, i) => ({ refType: "video", videoSlug: v.slug, position: i }));
}

function topApps(by: (a: typeof APPS[number]) => number, take = 8): RankingItemSpec[] {
  return [...APPS]
    .sort((a, b) => by(b) - by(a))
    .slice(0, take)
    .map((a, i) => ({ refType: "app", appSlug: a.slug, position: i }));
}

function topTagsByVideoCount(take = 10): RankingItemSpec[] {
  // 对齐原型 `:1418`:遍历 ALL_TAGS,按命中视频数降序
  const stats = ALL_TAGS_LABELS.map((label) => ({
    label,
    n: VIDEOS.filter((v) => (v.tags as string[]).includes(label)).length,
  }));
  return stats
    .sort((a, b) => b.n - a.n)
    .slice(0, take)
    .map((s, i) => ({ refType: "tag", tagLabel: s.label, position: i }));
}

export const RANKINGS: RankingSeed[] = [
  {
    slug: "weekly-hot-videos",
    title: "本周热门视频榜",
    description: "按观看次数排序的本周热门视频",
    sortOrder: 0,
    items: topVideos((v) => parseChineseCount(v.viewsLabel)),
  },
  {
    slug: "latest-videos",
    title: "最新上线视频榜",
    description: "按上线时间倒序的最新视频",
    sortOrder: 1,
    items: topVideos((v) => new Date(v.publishedDate).getTime()),
  },
  {
    slug: "top-liked-videos",
    title: "高收藏视频榜",
    description: "按点赞数排序的高人气视频",
    sortOrder: 2,
    items: topVideos((v) => parseLikes(v.likesLabel)),
  },
  {
    slug: "weekly-hot-apps",
    title: "本周热门 App 榜",
    description: "按用户量排序的本周热门 App",
    sortOrder: 3,
    items: topApps((a) => parseChineseCount(a.usersLabel)),
  },
  {
    slug: "top-rated-apps",
    title: "高评分 App 榜",
    description: "按评分排序的口碑 App",
    sortOrder: 4,
    items: topApps((a) => parseRating(a.rating)),
  },
  {
    slug: "hot-tags",
    title: "热门标签榜",
    description: "ALL_TAGS 中被视频引用最多的标签",
    sortOrder: 5,
    items: topTagsByVideoCount(),
  },
];
```

- [ ] **Step 3: 写 `seed/data/guides.ts`(5 条元数据)**

```ts
export interface GuideSeed {
  slug: string;
  title: string;
  summary: string;
  publishedDate: string;
  readMinutes: number;
  categorySlug: "app" | "video" | "privacy" | "social";
  categoryLabel: string;
  gradientKey: string;
  iconKey: string;
  viewsLabel: string;
  isHot: boolean;
}

export const GUIDES: GuideSeed[] = [
  {
    slug: "choose-app",
    title: "如何选择适合自己的男同 App",
    summary: "从社交、交友、健身到资讯,不同需求选不同的 App。",
    publishedDate: "2026-04-30",
    readMinutes: 8,
    categorySlug: "app",
    categoryLabel: "App 使用",
    gradientKey: "g-brand",
    iconKey: "i-smartphone",
    viewsLabel: "2.3万",
    isHot: true,
  },
  {
    slug: "where-watch",
    title: "男同视频在哪里看?合规渠道盘点",
    summary: "哪些平台收录了合规的男同生活方式视频内容?",
    publishedDate: "2026-04-25",
    readMinutes: 6,
    categorySlug: "video",
    categoryLabel: "内容观看",
    gradientKey: "g-fire",
    iconKey: "i-film",
    viewsLabel: "1.8万",
    isHot: false,
  },
  {
    slug: "privacy",
    title: "男同 App 隐私保护指南",
    summary: "从账号注册到日常使用,8 条实用的隐私保护建议。",
    publishedDate: "2026-04-20",
    readMinutes: 10,
    categorySlug: "privacy",
    categoryLabel: "隐私安全",
    gradientKey: "g-mint",
    iconKey: "i-shield",
    viewsLabel: "3.5万",
    isHot: true,
  },
  {
    slug: "community",
    title: "男同社区使用指南",
    summary: "融入一个新社区的 5 条礼仪,让社交更自在。",
    publishedDate: "2026-04-15",
    readMinutes: 7,
    categorySlug: "social",
    categoryLabel: "社区文化",
    gradientKey: "g-rose",
    iconKey: "i-users",
    viewsLabel: "1.2万",
    isHot: false,
  },
  {
    slug: "watch-video",
    title: "男同视频观看指南",
    summary: "如何通过标签、分类、榜单更高效地发现喜欢的内容。",
    publishedDate: "2026-04-10",
    readMinutes: 5,
    categorySlug: "video",
    categoryLabel: "内容观看",
    gradientKey: "g-sky",
    iconKey: "i-eye",
    viewsLabel: "9.8千",
    isHot: false,
  },
];
```

- [ ] **Step 4: 写 `seed/data/guide-bodies.ts`(5 篇 HTML→Markdown 转译)**

> 来源:`docs/ghome.html` :1612 起的 `bodies` 对象。手工转换成 Markdown。

```ts
export const GUIDE_BODIES: Record<string, string> = {
  "choose-app": `## 一、明确你的核心需求

选择男同 App 之前,先想清楚一个问题:你用这个 App 到底想解决什么?

- 快速认识附近的人 → BroConnect 这类 LBS 社交型
- 寻找稳定长期关系 → MateMatch 这类深度匹配型
- 找健身搭子 → GymBros 这类垂直社区
- 想了解群体文化、资讯 → RainbowNews 这类内容媒体
- 希望参加线下活动 → DateNight 这类活动平台

## 二、评估隐私保护程度

隐私是男同 App 使用中非常重要的维度。选择 App 时请重点查看:是否支持匿名模式、是否可以限制位置精度、聊天记录是否端到端加密、账号是否可一键注销。

## 三、看活跃度与社区氛围

活跃度高的 App 能让你更快匹配到合适的人,但同样重要的是社区氛围 — 是否有明确的社区公约、是否严格审核违规内容、客服响应是否及时。

## 四、从 Ghome 推荐开始

如果没有头绪,可以直接参考 Ghome 的「男同 App 导航」,我们已经按场景做了分类,每一款都经过上架审核和人工评测。
`,
  "where-watch": `## 合规渠道优先

观看男同视频内容,请优先选择合规的生活方式分享平台,如 Ghome 合作站 G-Video Hub。这类平台所有内容都经过审核,不含违规信息。

## 主题方向

目前合规的男同视频内容主要覆盖以下方向:Vlog、健身、旅行、情感访谈、生活记录、穿搭、美食。

## 如何发现好内容

- 按分类浏览 — 选择你感兴趣的主题
- 使用标签 — 组合标签可以精准发现
- 看排行榜 — 快速了解本周热门
- 关注创作者 — 长期订阅你喜欢的人
`,
  "privacy": `## 8 条男同 App 隐私保护建议

### 1. 使用独立邮箱与手机号

为男同 App 注册一个独立的邮箱账户,避免与工作、家庭信息关联。

### 2. 限制位置精度

在系统设置中,只授予 App「大致位置」而非「精确位置」。

### 3. 谨慎设置头像与资料

避免使用真实姓名、工作信息、熟人可辨认的照片。

### 4. 开启消息阅后即焚

支持该功能的 App 优先开启,减少敏感对话留痕。

### 5. 定期清理账号

不再使用的 App 及时注销账号并删除应用。

### 6. 警惕虚假账号与诈骗

不向陌生人透露身份证、银行卡等敏感信息。

### 7. 使用平台认证机制

认证过的账号更安全,也能获得更好的匹配。

### 8. 了解平台的隐私政策

在注册前花 2 分钟阅读隐私政策,了解数据如何被使用。
`,
  "community": `## 融入新社区的 5 条礼仪

### 1. 先观察再发言

新加入一个社区时,先花几天时间观察社区氛围、规则与常用术语。

### 2. 尊重每一位成员

不嘲讽、不歧视、不评头论足。男同社区内部也存在多元身份,保持基本的尊重。

### 3. 发言前注意隐私

不随便透露他人的真实身份、位置、工作信息。

### 4. 积极分享高质量内容

原创的生活分享、经验贴、干货回答,远比转发和灌水更受欢迎。

### 5. 使用举报机制维护社区

看到违规内容及时举报,是每一位成员的责任。
`,
  "watch-video": `## 如何更高效地发现你喜欢的视频

### 通过分类找方向

Ghome 合作的 G-Video Hub 把视频分为 Vlog、健身、旅行、访谈、生活、校园 6 大类,先选方向大大缩小范围。

### 通过标签精准筛选

每条视频都有 3-5 个标签,可以组合标签筛选。例如「旅行 + 美食」、「健身 + 励志」。

### 看榜单了解趋势

热门榜、最新榜、高收藏榜,各有侧重。热门榜适合跟流行,最新榜适合追更,高收藏榜适合精挑。

### 关注喜欢的创作者

找到风格契合的创作者,长期订阅比散看更能建立稳定的观看习惯。
`,
};
```

- [ ] **Step 5: 验证 typecheck**

```bash
pnpm --filter @ghome/db typecheck
```

- [ ] **Step 6: 提交**

```bash
git add packages/db/seed/
git commit -m "feat(db): seed data — 5 guides with markdown bodies, 6 rankings (50 items frozen from prototype), parse helpers"
```

---

## Task 9 — 主 seed 脚本 + DB 约束集成测试

**Files:**
- Create: `packages/db/prisma/seed.ts`
- Create: `packages/db/tests/db-constraints.test.ts`

> **必读**:seed 必须**幂等**(`prisma db seed` 反复跑不报错),用 `upsert` + `deleteMany` 清理 join 表。

- [ ] **Step 1: 写 `packages/db/prisma/seed.ts`**

```ts
import { PrismaClient, Prisma } from "@prisma/client";

import { APP_CATS } from "../seed/data/app-cats";
import { VIDEO_CATS } from "../seed/data/video-cats";
import { APPS } from "../seed/data/apps";
import { VIDEOS } from "../seed/data/videos";
import { TAG_SLUGS } from "../seed/data/tags";
import { TOPICS } from "../seed/data/topics";
import { GUIDES } from "../seed/data/guides";
import { GUIDE_BODIES } from "../seed/data/guide-bodies";
import { RANKINGS } from "../seed/helpers/rankings";

const prisma = new PrismaClient();

const SLUG_RE = /^[a-z0-9-]+$/;

async function main() {
  console.log("[seed] start");

  // ---------- 0. 校验 tag slug 全覆盖 + 格式 ----------
  const allTagLabels = new Set<string>();
  APPS.forEach((a) => a.tags.forEach((t) => allTagLabels.add(t)));
  VIDEOS.forEach((v) => v.tags.forEach((t) => allTagLabels.add(t)));
  // ALL_TAGS 来自 tags.ts 的 ALL_TAGS_LABELS — 自动覆盖在 RANKINGS 里
  // 但更稳妥:把 TAG_SLUGS 的所有 key 也加入断言集合
  Object.keys(TAG_SLUGS).forEach((l) => allTagLabels.add(l));

  const missing: string[] = [];
  const badSlugs: string[] = [];
  for (const label of allTagLabels) {
    const slug = TAG_SLUGS[label];
    if (!slug) { missing.push(label); continue; }
    if (!SLUG_RE.test(slug)) badSlugs.push(`${label} → ${slug}`);
  }
  if (missing.length || badSlugs.length) {
    throw new Error(
      `[seed] tag slug map invalid:\n  missing: ${missing.join(", ")}\n  bad slug format: ${badSlugs.join(", ")}`
    );
  }

  // ---------- 1. categories(app + video) ----------
  for (const c of APP_CATS) {
    await prisma.category.upsert({
      where: { kind_slug: { kind: "app", slug: c.slug } },
      update: { label: c.label, description: c.description, sortOrder: c.sortOrder },
      create: { kind: "app", slug: c.slug, label: c.label, description: c.description, sortOrder: c.sortOrder },
    });
  }
  for (const c of VIDEO_CATS) {
    await prisma.category.upsert({
      where: { kind_slug: { kind: "video", slug: c.slug } },
      update: { label: c.label, description: c.description, sortOrder: c.sortOrder },
      create: { kind: "video", slug: c.slug, label: c.label, description: c.description, sortOrder: c.sortOrder },
    });
  }

  // ---------- 2. tags ----------
  for (const [label, slug] of Object.entries(TAG_SLUGS)) {
    await prisma.tag.upsert({
      where: { slug },
      update: { label },
      create: { slug, label },
    });
  }

  // ---------- 3. apps + redirects + app_tags ----------
  for (const a of APPS) {
    const cat = await prisma.category.findUniqueOrThrow({ where: { kind_slug: { kind: "app", slug: a.categorySlug } } });
    // 同 slug 已存在则复用 redirect_id;否则新建 disabled redirect
    const existing = await prisma.app.findUnique({ where: { slug: a.slug }, select: { redirectId: true } });
    const redirect = existing
      ? await prisma.redirect.update({
          where: { id: existing.redirectId },
          data: {
            targetUrl: `https://example.com/seed/app/${a.slug}`,
            ownerKind: "app",
            ownerId: a.slug,
            disabled: true,
          },
        })
      : await prisma.redirect.create({
          data: {
            targetUrl: `https://example.com/seed/app/${a.slug}`,
            ownerKind: "app",
            ownerId: a.slug,
            disabled: true,
          },
        });

    const upserted = await prisma.app.upsert({
      where: { slug: a.slug },
      update: {
        name: a.name, iconKey: a.iconKey, gradientKey: a.gradientKey, categoryId: cat.id,
        shortDesc: a.shortDesc, detail: a.detail, highlights: a.highlights,
        audience: a.audience, features: a.features, platform: a.platform,
        size: a.size, rating: a.rating, usersLabel: a.usersLabel,
        status: "published",
      },
      create: {
        slug: a.slug, name: a.name, iconKey: a.iconKey, gradientKey: a.gradientKey, categoryId: cat.id,
        shortDesc: a.shortDesc, detail: a.detail, highlights: a.highlights,
        audience: a.audience, features: a.features, platform: a.platform,
        size: a.size, rating: a.rating, usersLabel: a.usersLabel,
        redirectId: redirect.id,
        status: "published",
      },
    });

    // app_tags 全量重置
    await prisma.appTag.deleteMany({ where: { appId: upserted.id } });
    for (const tagLabel of a.tags) {
      const tag = await prisma.tag.findUniqueOrThrow({ where: { slug: TAG_SLUGS[tagLabel]! } });
      await prisma.appTag.create({ data: { appId: upserted.id, tagId: tag.id } });
    }
  }

  // ---------- 4. videos + redirects + video_tags ----------
  for (const v of VIDEOS) {
    const cat = await prisma.category.findUniqueOrThrow({ where: { kind_slug: { kind: "video", slug: v.categorySlug } } });
    const existing = await prisma.video.findUnique({ where: { slug: v.slug }, select: { redirectId: true } });
    const redirect = existing
      ? await prisma.redirect.update({
          where: { id: existing.redirectId },
          data: {
            targetUrl: `https://example.com/seed/video/${v.slug}`,
            ownerKind: "video",
            ownerId: v.slug,
            disabled: true,
          },
        })
      : await prisma.redirect.create({
          data: {
            targetUrl: `https://example.com/seed/video/${v.slug}`,
            ownerKind: "video",
            ownerId: v.slug,
            disabled: true,
          },
        });

    const upserted = await prisma.video.upsert({
      where: { slug: v.slug },
      update: {
        title: v.title, emoji: v.emoji, coverKey: v.coverKey, duration: v.duration,
        viewsLabel: v.viewsLabel, likesLabel: v.likesLabel,
        publishedDate: new Date(v.publishedDate),
        categoryId: cat.id, shortDesc: v.shortDesc, detail: v.detail,
        status: "published",
      },
      create: {
        slug: v.slug, title: v.title, emoji: v.emoji, coverKey: v.coverKey, duration: v.duration,
        viewsLabel: v.viewsLabel, likesLabel: v.likesLabel,
        publishedDate: new Date(v.publishedDate),
        categoryId: cat.id, shortDesc: v.shortDesc, detail: v.detail,
        redirectId: redirect.id,
        status: "published",
      },
    });

    await prisma.videoTag.deleteMany({ where: { videoId: upserted.id } });
    for (const tagLabel of v.tags) {
      const tag = await prisma.tag.findUniqueOrThrow({ where: { slug: TAG_SLUGS[tagLabel]! } });
      await prisma.videoTag.create({ data: { videoId: upserted.id, tagId: tag.id } });
    }
  }

  // ---------- 5. guides ----------
  for (const g of GUIDES) {
    const body = GUIDE_BODIES[g.slug];
    if (!body) throw new Error(`[seed] missing body for guide ${g.slug}`);
    await prisma.guide.upsert({
      where: { slug: g.slug },
      update: {
        title: g.title, summary: g.summary, bodyMd: body,
        categorySlug: g.categorySlug, categoryLabel: g.categoryLabel,
        gradientKey: g.gradientKey, iconKey: g.iconKey,
        readMinutes: g.readMinutes, viewsLabel: g.viewsLabel, isHot: g.isHot,
        publishedDate: new Date(g.publishedDate),
        status: "published",
      },
      create: {
        slug: g.slug, title: g.title, summary: g.summary, bodyMd: body,
        categorySlug: g.categorySlug, categoryLabel: g.categoryLabel,
        gradientKey: g.gradientKey, iconKey: g.iconKey,
        readMinutes: g.readMinutes, viewsLabel: g.viewsLabel, isHot: g.isHot,
        publishedDate: new Date(g.publishedDate),
        status: "published",
      },
    });
  }

  // ---------- 6. topics(collections kind=topic + items) ----------
  for (const t of TOPICS) {
    const col = await prisma.collection.upsert({
      where: { slug: t.slug },
      update: {
        kind: "topic", title: t.title, description: t.description,
        coverKey: t.coverKey, sortOrder: t.sortOrder, status: "published",
      },
      create: {
        slug: t.slug, kind: "topic", title: t.title, description: t.description,
        coverKey: t.coverKey, sortOrder: t.sortOrder, status: "published",
      },
    });
    await prisma.collectionItem.deleteMany({ where: { collectionId: col.id } });
    for (const item of t.items) {
      const video = await prisma.video.findUniqueOrThrow({ where: { slug: item.videoSlug } });
      await prisma.collectionItem.create({
        data: {
          collectionId: col.id,
          position: item.position,
          refType: "video",
          videoId: video.id,
        },
      });
    }
  }

  // ---------- 7. rankings(collections kind=ranking + items) ----------
  for (const r of RANKINGS) {
    const col = await prisma.collection.upsert({
      where: { slug: r.slug },
      update: {
        kind: "ranking", title: r.title, description: r.description,
        sortOrder: r.sortOrder, status: "published",
      },
      create: {
        slug: r.slug, kind: "ranking", title: r.title, description: r.description,
        sortOrder: r.sortOrder, status: "published",
      },
    });
    await prisma.collectionItem.deleteMany({ where: { collectionId: col.id } });
    for (const item of r.items) {
      let appId: string | null = null;
      let videoId: string | null = null;
      let tagId: string | null = null;
      if (item.refType === "app") {
        const app = await prisma.app.findUniqueOrThrow({ where: { slug: item.appSlug! } });
        appId = app.id;
      } else if (item.refType === "video") {
        const video = await prisma.video.findUniqueOrThrow({ where: { slug: item.videoSlug! } });
        videoId = video.id;
      } else if (item.refType === "tag") {
        const tag = await prisma.tag.findUniqueOrThrow({ where: { slug: TAG_SLUGS[item.tagLabel!]! } });
        tagId = tag.id;
      }
      await prisma.collectionItem.create({
        data: {
          collectionId: col.id,
          position: item.position,
          refType: item.refType,
          appId, videoId, tagId,
        },
      });
    }
  }

  console.log("[seed] done");
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });
```

- [ ] **Step 2: 写 `packages/db/tests/db-constraints.test.ts`**(集成测试,需要 Postgres 已起 + 已 migrate,但 **不**依赖已 seed)

```ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

beforeAll(async () => { await prisma.$connect(); });
afterAll(async () => { await prisma.$disconnect(); });

describe("DB-level constraints (post-T3)", () => {
  it("rejects categories.kind not in ('app','video')", async () => {
    await expect(
      prisma.$executeRawUnsafe(
        `INSERT INTO categories (id, slug, label, kind, sort_order) VALUES (gen_random_uuid(), 'badcat', 'bad', 'wrong-kind', 0)`,
      ),
    ).rejects.toThrow(/check|constraint/i);
  });

  it("rejects collection_items where ref_type does not match the FK", async () => {
    // 先建一个空 collection
    const col = await prisma.collection.create({
      data: { slug: `test-${Date.now()}`, kind: "topic", title: "t", sortOrder: 999 },
    });
    await expect(
      prisma.$executeRawUnsafe(
        `INSERT INTO collection_items (id, collection_id, position, ref_type, app_id) VALUES (gen_random_uuid(), '${col.id}', 0, 'video', gen_random_uuid())`,
      ),
    ).rejects.toThrow(/check|constraint/i);
    await prisma.collection.delete({ where: { id: col.id } });
  });

  it("allows position swap inside a transaction (DEFERRABLE UNIQUE)", async () => {
    const col = await prisma.collection.create({
      data: { slug: `swap-${Date.now()}`, kind: "topic", title: "swap test", sortOrder: 998 },
    });
    // 准备两条项
    const v = await prisma.video.findFirstOrThrow();
    const v2 = await prisma.video.findFirstOrThrow({ skip: 1 });
    const a = await prisma.collectionItem.create({ data: { collectionId: col.id, position: 0, refType: "video", videoId: v.id } });
    const b = await prisma.collectionItem.create({ data: { collectionId: col.id, position: 1, refType: "video", videoId: v2.id } });

    // swap inside transaction(中间态会有重复 position,deferred 应允许)
    await prisma.$transaction([
      prisma.collectionItem.update({ where: { id: a.id }, data: { position: 1 } }),
      prisma.collectionItem.update({ where: { id: b.id }, data: { position: 0 } }),
    ]);

    const after = await prisma.collectionItem.findMany({ where: { collectionId: col.id }, orderBy: { position: "asc" } });
    expect(after[0]!.id).toBe(b.id);
    expect(after[1]!.id).toBe(a.id);

    await prisma.collectionItem.deleteMany({ where: { collectionId: col.id } });
    await prisma.collection.delete({ where: { id: col.id } });
  });

  it("rejects pointing apps.category_id at a kind='video' category", async () => {
    const videoCat = await prisma.category.findFirstOrThrow({ where: { kind: "video" } });
    const someApp = await prisma.app.findFirstOrThrow();
    await expect(
      prisma.app.update({ where: { id: someApp.id }, data: { categoryId: videoCat.id } }),
    ).rejects.toThrow(/foreign key|constraint/i);
  });

  it("rejects duplicate tags.label", async () => {
    const t = await prisma.tag.findFirstOrThrow();
    await expect(
      prisma.tag.create({ data: { slug: `${t.slug}-dup-${Date.now()}`, label: t.label } }),
    ).rejects.toThrow(/unique|duplicate|constraint/i);
  });
});
```

- [ ] **Step 3: 跑 seed**

```bash
docker compose up -d
pnpm --filter @ghome/db db:seed
```

Expected: 输出 `[seed] start` ... `[seed] done`,无错误。

- [ ] **Step 4: 行数断言(对应 spec P1 完成判据)**

```bash
docker compose exec postgres psql -U ghome -d ghome <<'SQL' | tee /tmp/seed-counts.txt
SELECT 'apps' tbl, count(*) FROM apps
UNION ALL SELECT 'videos', count(*) FROM videos
UNION ALL SELECT 'guides', count(*) FROM guides
UNION ALL SELECT 'guides_bodies_nonempty', count(*) FROM guides WHERE length(body_md) > 0
UNION ALL SELECT 'tags', count(*) FROM tags
UNION ALL SELECT 'app_tags', count(*) FROM app_tags
UNION ALL SELECT 'video_tags', count(*) FROM video_tags
UNION ALL SELECT 'collections_topic', count(*) FROM collections WHERE kind='topic'
UNION ALL SELECT 'collections_ranking', count(*) FROM collections WHERE kind='ranking'
UNION ALL SELECT 'collection_items_ranking',
  (SELECT count(*) FROM collection_items ci JOIN collections c ON c.id=ci.collection_id WHERE c.kind='ranking')
UNION ALL SELECT 'redirects_disabled', count(*) FROM redirects WHERE disabled=true;
SQL
```

Expected:
- apps = 9
- videos = 20
- guides = 5(同时 guides_bodies_nonempty = 5)
- tags = 63
- app_tags = 27
- video_tags = 60
- collections_topic = 6
- collections_ranking = 6
- collection_items_ranking = 50
- redirects_disabled ≥ 29(9 apps + 20 videos = 29)

如果任何一个不达标,STOP 并 BLOCKED report 给 controller。

- [ ] **Step 5: 抽样校验(任取 1 App / 1 Video,JOIN tags 后数量与原型一致)**

```bash
docker compose exec postgres psql -U ghome -d ghome <<'SQL'
SELECT a.slug, count(*) AS tag_count
FROM apps a
JOIN app_tags at ON at.app_id = a.id
WHERE a.slug = 'broconnect'
GROUP BY a.slug;

SELECT v.slug, array_agg(t.label ORDER BY t.label) AS tag_labels
FROM videos v
JOIN video_tags vt ON vt.video_id = v.id
JOIN tags t ON t.id = vt.tag_id
WHERE v.slug = 'v02'
GROUP BY v.slug;
SQL
```

Expected:
- broconnect tag_count = 3
- v02 tag_labels = `{健身,打卡,训练}`(顺序可能不同,但元素必须包含这三个)

- [ ] **Step 6: 跑约束集成测试**

```bash
pnpm --filter @ghome/db test
```

Expected: 全过(包括 url-policy 测试与 db-constraints 测试)。

- [ ] **Step 7: 提交**

```bash
git add packages/db/prisma/seed.ts packages/db/tests/db-constraints.test.ts
git commit -m "feat(db): add main seed script and DB constraint integration tests"
```

---

## Task 10 — `db:enable-redirect` CLI 脚本

**Files:**
- Create: `packages/db/scripts/enable-redirect.ts`

- [ ] **Step 1: 写 `scripts/enable-redirect.ts`**

```ts
import { PrismaClient } from "@prisma/client";
import { validateForWrite } from "../src/lib/url-policy";

async function main() {
  const [, , id, url] = process.argv;
  if (!id || !url) {
    console.error("Usage: pnpm db:enable-redirect <redirect-id> <real-url>");
    process.exit(2);
  }

  const result = await validateForWrite(url);
  if (!result.ok) {
    console.error(`URL rejected by url-policy: ${result.reason}`);
    process.exit(1);
  }

  const prisma = new PrismaClient();
  try {
    const updated = await prisma.redirect.update({
      where: { id },
      data: { targetUrl: url, disabled: false },
    });
    console.log(`Enabled redirect ${updated.id}: ${updated.targetUrl}`);
  } finally {
    await prisma.$disconnect();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
```

- [ ] **Step 2: 测试 — 用一条 seed 出来的 disabled redirect**

```bash
# 拿一条 redirect id
RID=$(docker compose exec -T postgres psql -U ghome -d ghome -tAc \
  "SELECT id FROM redirects WHERE owner_kind='app' AND owner_id='broconnect' LIMIT 1")

# 1) 用合法 URL 启用
pnpm --filter @ghome/db db:enable-redirect "$RID" "https://broconnect.example/download"

# 2) 用 javascript: URL 应被拒
pnpm --filter @ghome/db db:enable-redirect "$RID" "javascript:alert(1)" || echo "rejected as expected"

# 3) 用 localhost 应被拒
pnpm --filter @ghome/db db:enable-redirect "$RID" "http://localhost/x" || echo "rejected as expected"
```

Expected:
- 第 1 条:`Enabled redirect <RID>: https://broconnect.example/download`
- 第 2、3 条:输出 `URL rejected by url-policy: ...` 并退出码 1,然后 `rejected as expected`

- [ ] **Step 3: 把第 1 步的 redirect 重置回 disabled 状态(还原 seed)**

```bash
docker compose exec postgres psql -U ghome -d ghome \
  -c "UPDATE redirects SET target_url='https://example.com/seed/app/broconnect', disabled=true WHERE owner_kind='app' AND owner_id='broconnect';"
```

- [ ] **Step 4: 提交**

```bash
git add packages/db/scripts/enable-redirect.ts
git commit -m "feat(db): add db:enable-redirect CLI for P3 redirect activation"
```

---

## Task 11 — CI 升级:加 `postgres:16` service + migrate + seed

**Files:**
- Modify: `.github/workflows/ci.yml`(整体重写)

- [ ] **Step 1: 整体重写 `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

jobs:
  ci:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: ghome
          [敏感内容已脱敏]
          POSTGRES_DB: ghome
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U ghome -d ghome"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

    env:
      DATABASE_URL: postgres://ghome:ghome@localhost:5432/ghome

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9.12.0
          run_install: false

      - name: Get pnpm store directory
        id: pnpm-cache
        run: echo "STORE_PATH=$(pnpm store path --silent)" >> $GITHUB_OUTPUT

      - name: Setup pnpm cache
        uses: actions/cache@v4
        with:
          path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pnpm-store-

      - name: Install
        run: pnpm install --frozen-lockfile

      - name: Generate Prisma Client
        run: pnpm --filter @ghome/db exec prisma generate

      - name: Apply Prisma migrations
        run: pnpm --filter @ghome/db db:migrate:deploy

      - name: Seed database
        run: pnpm --filter @ghome/db db:seed

      - name: Lint
        run: pnpm lint

      - name: Typecheck
        run: pnpm typecheck

      - name: Test (vitest, includes db constraints)
        run: pnpm --filter @ghome/db test

      - name: Build
        run: pnpm build
```

- [ ] **Step 2: 本地复刻 CI 步骤(无 act 时的兜底)**

```bash
# 干净环境
docker compose down -v
docker compose up -d
pnpm install --frozen-lockfile
pnpm --filter @ghome/db exec prisma generate
pnpm --filter @ghome/db db:migrate:deploy
pnpm --filter @ghome/db db:seed
pnpm lint
pnpm typecheck
pnpm --filter @ghome/db test
pnpm build
```

Expected: 8 步全过。

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: upgrade workflow to include postgres service, prisma migrate, seed, and tests"
```

---

## Task 12 — 完整冒烟 + 移动 P1 标签

无新文件。本 task 跑端到端冒烟,把 `p0-scaffolding` 的下一个里程碑 `p1-data-model` 标上。

- [ ] **Step 1: 干净环境 reset**

```bash
docker compose down -v
docker compose up -d
sleep 10  # 等 postgres healthy
pnpm install
pnpm --filter @ghome/db db:reset --force  # drop + re-migrate + re-seed
```

> `db:reset` 会先 drop schema,再 apply 全部 migrations,再跑 seed。等同于全新克隆体验。

- [ ] **Step 2: 全套验证**

```bash
pnpm typecheck
pnpm lint
pnpm --filter @ghome/db test
pnpm build
```

Expected: 4 步全过。

- [ ] **Step 3: 关闭 Postgres**

```bash
docker compose down
```

- [ ] **Step 4: 检查 git 干净**

```bash
git status --short
```

Expected: 空(或仅 `pnpm-lock.yaml`,有则 commit)。

- [ ] **Step 5: 标签 P1**

```bash
git tag -a p1-data-model -m "P1 · data model + seed: 14 tables, raw SQL constraints, 9 apps + 20 videos + 6 topics + 6 rankings (50 items) + 5 guides; CI with postgres service + migrate + seed"
git log --oneline -15
```

Expected: 看到 P1 期间的 ~12 个 commit + tag。

---

## P1 完成判据(对应 spec §5)

- ✅ 14 表 schema(`schema.prisma`,**不**声明 `@@unique([collectionId, position])`)— T1
- ✅ 首版迁移 + raw SQL constraints 迁移(`categories_kind_check` + `categories_id_kind_unique` + `category_kind` 生成列与复合 FK + `collection_items_ref_match` CHECK + `collection_items_position_unique` DEFERRABLE UNIQUE)— T2 / T3
- ✅ `pg_trgm` 扩展启用 + 三类 GIN 索引(为 P8 搜索做准备)— T3
- ✅ `url-policy` 工具函数(`validateForWrite` 含 DNS / `validateForRedirect` 同步)— T5
- ✅ tag 全并集 slug 映射表 — T7
- ✅ 5 篇 guide bodies HTML→MD 转译 — T8
- ✅ 原型数据导入脚本(APP_CATS 排除 `'all'`,seed 出 disabled 占位 redirect)— T9
- ✅ 行数断言:apps=9 / videos=20 / 专题=6 / 榜单=6 / 指南=5(5 篇正文字符数 > 0)— T9 Step 4
- ✅ tags 行数 = 63;app_tags=27;video_tags=60 — T9 Step 4
- ✅ ranking_items = 50 条(5×8 + 1×10)— T9 Step 4
- ✅ disabled redirect ≥ 29 — T9 Step 4
- ✅ 抽样:App / Video JOIN tags 后数量正确 — T9 Step 5
- ✅ 约束自检(5 用例)— T9 Step 6 通过 db-constraints 集成测试
- ✅ CI 升级带 Postgres service + migrate + seed + test + build — T11
- ✅ `db:enable-redirect` CLI 走 `validateForWrite`(协议、DNS 都校验) — T10

---

## 已知 P1 故意不做的事(P2 起补)

- **页面端不查 DB**:apps/web 与 apps/admin 页面仍是 P0 占位文案,不连 packages/db。P2 才把 SSG/ISR 接上。
- **跳转中转 `/r/:id` 不实现**:redirects 已 seed 但 web 还没有 `app/r/[id]/route.ts`(P3)。
- **运营端不接入**:apps/admin 不能编辑(P5/P6)。
- **不引入 ua-parser-js**(P3 才用)。
- **Auth.js 不接入**(P4)。
- **Vercel / Supabase / Neon / Cloudflare 部署形态依然不决定**。

---

## Self-Review

- **Spec 覆盖**:逐条核对 spec §3 + §4.5 + §5 P1。schema 14 表全部建模(`@ghome/db` 不声明 `category_kind` / collection_items 复合 unique / `categories.kind` enum,均有 raw SQL 兜底);搜索路径 `pg_trgm` GIN 索引 P8 才用,但 P1 已建,符合 "Postgres 自带不污染镜像";seed 13 模块逐一对应 spec §4.5 的来源表(包括 `'all'` 排除 / disabled redirect / guide body HTML→MD 转译 / tag 全并集 / ranking 5×8+1×10 / sort_order 赋值 0..5)。完成判据每条都有对应 task 步骤。

- **占位符扫描**:无 "TBD" / "TODO" / "fill in"。每段代码块都是完整、可执行的内容。约束/类型一致性:
  - `@ghome/db` 包名贯穿 12 个 task
  - Prisma model 字段名(camelCase)与 SQL 列名(snake_case)在 schema.prisma `@map` 处 1:1 对齐
  - tag slug 在 `seed/data/tags.ts` 定义,被 `topics.ts` 通过 label 反查、被 `rankings.ts` 通过 `TAG_SLUGS[label]` 查;名字一致
  - ranking sort_order 0..5 在 `rankings.ts` 中明确,seed 主脚本的 upsert 也尊重
  - `collection_items_position_unique` DEFERRABLE 在 T3 raw SQL 与 T9 swap 测试两处呼应

- **TDD 体现**:T5 严格 TDD(失败测试先行 → 实现 → 通过)。T9 db-constraints 测试在 seed 之后运行,验证 T3 SQL 实际生效。

- **风险**:T5 的 `localtest.me → 192.0.2.1` 那条用例在某些 DNS 环境下可能不解析,允许 `it.skip`。其余无已知风险。

---

## 下一步

P1 完成后,**写 P2 plan**(把页面端的 17 条原型路由接到 DB,SSG/ISR 出 HTML;`/albums` 不在 P2 范围;FEATURED_WEB / CREATORS / SAMPLE_REVIEWS 留 fixture)。
