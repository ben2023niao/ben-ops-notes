---
id: "doc-c1be2ef9333f"
title: "Ghome 产品形态与架构设计"
date: "2026-05-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Linux", "Shell", "Docker", "自动化", "CDN", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md"
sourceSha256: "4b8c15c02f413b67bbd1f873e81c2917e0a723f00b3a4f57bb1f4698deb1dfbb"
sourceSystem: "project-doc"
---

# Ghome 产品形态与架构设计

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605080000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BLinux-Ghome%20%E4%BA%A7%E5%93%81%E5%BD%A2%E6%80%81%E4%B8%8E%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1.md)

> 整理日期：2026-05-08 00:00｜日期依据：文件名日期

- **日期**:2026-05-08
- **状态**:草稿,待 user 审阅
- **作者**:与 user 协作整理(brainstorming skill)
- **范围**:Ghome 三段式产品(页面端 / 服务端 / 运营管理端)的整体架构、数据模型、关键交互、MVP 分阶段

---

## 0. 背景与定位

Ghome 定位为面向全球中文用户的 **LGBTQ+ 数字生活总入口**,是一个 **导航类站点**:

- 收录、组织并对外推荐 LGBTQ+ 友好的 App、视频内容平台、专题与指南
- 不托管 App 安装包,不托管视频文件,所有点击外跳第三方
- 不收录任何成人 / 擦边 / 违规内容
- 当前 `docs/ghome.html` 是页面端的纯前端原型(单文件 SPA、数据写死),本设计将其拆解为完整的三段式产品

### 已确认的核心约束

| 维度 | 选定 |
|---|---|
| 内容边界 | 纯导航站,**+** 运营端做专辑/专题/指南类编辑型内容,透出到页面端 |
| 核心场景 | App / 视频 / 专题 / 指南**平权**的总入口(以主题/场景驱动浏览) |
| 多端 | 仅 Web,响应式适配桌面 + 手机浏览器 |
| 部署区域 | 海外,面向全球中文用户;不走 ICP 备案 |
| 商业模式 | 暂不上付费/广告;但服务端预留中转跳转 + 点击追踪 + 推广位字段(可进化架构) |
| 用户体系 | **终端用户纯匿名**(无账号、无终端用户表);收藏/历史走浏览器 localStorage。管理端有运营账号表 `admin_users`(详见 §3.2) |
| 数据库 | Postgres 16(可移植性优先,先在本地 Docker 跑) |
| ORM | **Prisma** |
| 内容来源 | 运营编辑录入,不做 UGC、不做第三方抓取 |
| 搜索 | `ILIKE + pg_trgm` GIN 索引(Postgres 内置扩展);不上 FTS / Elasticsearch / Meilisearch(详见 §4.4) |
| 榜单 | MVP **手工维护**,seed 出 6 个 `collections(kind=ranking)`(5 内容榜各 8 条 + 1 标签榜 10 条,共 50 条 ranking_items,完全对齐原型 `renderRankings`);`/rankings` 直接读 DB;**不做运行时动态排序**(原型字段如 `users_label='800万+'` `rating='4.7'` 是字符串,排序需要先补 numeric 列,留给后期) |

### 不在 MVP 范围内

- 任何用户账号、登录、收藏、评论、点赞
- 邮件/Push 通知
- 多语言 / i18n
- A/B 测试、灰度发布
- CPS 联盟 / 广告售卖系统 / 会员订阅
- 移动端原生 App、微信小程序
- Cloudflare / Supabase / Neon / Vercel 等云托管的最终选型(推迟到 MVP 跑通后)

---

## 1. 整体架构

### 1.1 单仓多包(monorepo)

```
ghome/
├─ apps/
│  ├─ web/              # 页面端 — Next.js,SSG + ISR
│  └─ admin/            # 运营管理端 — Next.js,SSR,要登录
├─ packages/
│  └─ db/               # Prisma schema + queries + migrations
├─ docker-compose.yml   # 仅基础设施:Postgres(+ Adminer)
├─ docs/
└─ package.json         # pnpm workspaces
```

**"服务端" = `packages/db` + 两个 app 自己的 Route Handler**。不再起独立 backend 进程;数据库 Postgres 跑在本地 Docker,两个 app 通过 `DATABASE_URL` 共用同一份 schema。

### 1.2 `packages/db` 内部

```
packages/db/
├─ prisma/
│  ├─ schema.prisma        # 14 张表的 schema(Prisma DSL)
│  └─ migrations/          # prisma migrate 生成的 SQL 迁移
├─ src/
│  ├─ client.ts            # PrismaClient 单例,web/admin 共用
│  └─ queries/             # 复用查询(如 getPublishedAppsByCategory)
└─ package.json            # 导出 @ghome/db
```

### 1.3 本地开发拓扑

```
[host: macOS/Linux 开发机]
  ├─ pnpm --filter web dev   → http://localhost:3000   (apps/web)
  ├─ pnpm --filter admin dev → http://localhost:3100   (apps/admin)
  │
  └─ docker compose up -d    →
       ├─ postgres:16           localhost:5432   (持久化卷)
       └─ adminer(可选)         localhost:8080   (DB 浏览/排错)
```

- **Next.js 跑在宿主机**,HMR 体验最好
- **基础设施跑在 Docker**,`docker compose up -d` 一行起
- 两个 app 通过 `DATABASE_URL=postgres://...@localhost:5432/ghome` 直连

### 1.4 一键起项目

```bash
pnpm install
docker compose up -d
pnpm --filter @ghome/db prisma migrate deploy   # 应用迁移
pnpm --filter @ghome/db prisma db seed          # 从 docs/ghome.html 灌种子
pnpm dev                                        # 并行起 web + admin
```

### 1.5 关于"云"

不在 MVP 范围。选 Postgres + Prisma 是为了**未来不锁死**:任何托管 Postgres(Supabase / Neon / RDS / 自建 VPS)都能直接迁,只改 `DATABASE_URL`。

---

## 2. 三段产品的能力切片

### 2.1 页面端(`apps/web`)· 匿名访问

| 路由 | 用途 |
|---|---|
| `/` | 首页 — 搜索 + 主推 + 分类入口 + 专辑/专题腰部 + 热榜 |
| `/apps` `/app/:slug` | App 列表 / 详情 |
| `/videos` `/video/:slug` | 视频列表 / 详情 |
| `/categories` `/category/:slug` `/tag/:slug` | 分类与标签聚合(`/category/:slug` 仅解析视频分类;App 分类作为 `/apps?cat=:slug` 的筛选 tab,不独立成页 — 详见 §3.2 categories) |
| `/topics` `/topic/:slug` | 专题列表 / 详情 |
| `/albums` `/album/:slug` | 专辑(运营编排的混合卡片集)— **原型无此路由,P2 不实现;由 P6 同步交付前台列表/详情页** |
| `/guides` `/guide/:slug` | 指南列表 / 详情(Markdown) |
| `/rankings` | 榜单 |
| `/about` `/contact` `/terms` | 站点页 |
| `/r/:id` | 跳转中转:打点 → 302 到第三方目标 |

**不做**:账号、UGC、收藏(收藏走 localStorage)、内容上传。

### 2.2 服务端(`packages/db` + Route Handlers)

- API 命名空间:
  - 公开端点(无 /api 前缀,需要稳定外链):`/r/:id`(跳转中转)
  - 内部 API(/api 前缀):`apps/web/api/{search, revalidate}`、`apps/admin/api/*`(全套 CRUD)
- 内容状态机:`draft → published → archived`,软删除(`deleted_at`)
- 跳转中转表 `redirects`:外链统一被替换成 `/r/:id`,运营端可批量改目标
- 点击事件表 `click_events`:**采集最小化 + 假名化**(详见 §3.2 + §4.2)。`ip_hash` 是 GDPR 意义上的 *pseudonymous data*,不等同于"匿名"

### 2.3 运营管理端(`apps/admin`)· 登录后访问

- **Dashboard**:收录数(按状态:draft / published / archived)、近 7 日点击趋势、热门跳转 Top N
- **App / 视频 / 指南** — 列表 + 编辑(P5)
- **专题 / 专辑 / 榜单**(三类共用 collections CRUD)— 列表 + 编辑 + 拖拽排序(P6)
- **标签** — 仅"内联创建"(在 App / 视频编辑器里要打 tag 时,可即时新建一条 tag,要求 label + slug,P5 完成);**MVP 不做独立标签管理页**
- **分类**(categories) — **MVP seed-only,不做 admin 编辑**。原因:分类总数极少(3 App + 6 video,共 9 条)、改 slug 影响 URL、新增分类常牵动前端 UI 调整。如需新增/改名,本期通过迁移脚本走;P6 后视情况再做独立分类管理页(列入 §6 后续)
- **专题** — 标题 + 描述 + 封面 + 排序的视频/App 集合
- **专辑** — 编辑型混合卡片集(可同时混 App + 视频 + 外链)
- **指南** — Markdown 编辑器
- **跳转链管理** — `/r/:id` ↔ 真实 URL 的对照,批量改目标
- **操作日志** — 谁在什么时候改了什么

**MVP 不做**:多角色 RBAC(全员"编辑")、审批工作流(改完即发布)、定时发布、Webhook。

---

## 3. 数据模型

### 3.1 表清单(14 张)

| 类别 | 表 | 作用 |
|---|---|---|
| 内容 | `apps` `videos` `guides` | 三类一级内容 |
| 分类 | `categories` `tags` `app_tags` `video_tags` | 字典与多对多 |
| 编辑编排 | `collections` `collection_items` | 专题/专辑/榜单**三合一** |
| 跳转打点 | `redirects` `click_events` `click_daily_stats` | 外链中转 + 原始日志(30d 保留) + 聚合统计 |
| 管理 | `admin_users` `audit_log` | 运营账号与操作日志 |

> 内容表(apps / videos / guides / collections)共享 6 个公共字段:
> `id`(uuid)、`slug`(unique)、`status`(enum: draft/published/archived)、`created_at`、`updated_at`、`deleted_at`(soft delete)

> **关于"enum"的实现方式**:除 `categories.kind` 用 `text + CHECK` 之外(见 §3.2 categories 块的解释),
> 其他所有 `enum` 字段(`status`、`collection_items.ref_type`、`collections.kind`、`redirects.owner_kind`)
> 都用 Prisma DSL 的 `enum` 声明,Prisma 会在迁移中创建对应的 Postgres ENUM 类型。
> 这些字段都不是任何复合 FK 的目标,不存在跨表类型对齐问题。

### 3.2 关键表 schema(简写)

**`apps`**
```
id  slug  name  icon_key  gradient_key
category_id           ──→ categories.id    (FK 见下)
category_kind         text  GENERATED ALWAYS AS ('app') STORED   -- 生成列,固定值
short_desc            -- 卡片用
detail                -- 长文,markdown
highlights            -- text[]
audience  features  platform  size  rating  users_label
redirect_id ──→ redirects.id   -- 官网/下载跳转
status  ts  …

FOREIGN KEY (category_id, category_kind) REFERENCES categories (id, kind)
  -- 这条复合 FK 保证 apps 只能指向 kind='app' 的分类
```

**`videos`**
```
id  slug  title  emoji  cover_key  duration
views_label  likes_label  published_date
category_id           ──→ categories.id    (FK 见下)
category_kind         text  GENERATED ALWAYS AS ('video') STORED  -- 生成列,固定值
short_desc  detail
redirect_id ──→ redirects.id   -- 观看跳转
status  ts  …

FOREIGN KEY (category_id, category_kind) REFERENCES categories (id, kind)
  -- 这条复合 FK 保证 videos 只能指向 kind='video' 的分类
```

> **kind 错配防御**(关键):仅靠 `apps.category_id` 单字段 FK,DB 无法阻止把 App 指到 `kind='video'` 的分类。
> 解决(三个步骤,必须按顺序执行):
> 1. `categories.kind` 用 **`text + CHECK`** 而非 ENUM(理由见上)
> 2. `categories` 加 `UNIQUE (id, kind)`(在已有 PK `id` 之外补一个复合唯一,作为复合 FK 的目标)
> 3. `apps` / `videos` 各加一个 **`GENERATED ALWAYS AS ('app'/'video') STORED`** 的 `text` 列
> 4. `apps` / `videos` 的 FK 从 `(category_id) → categories(id)` 改为 `(category_id, category_kind) → categories(id, kind)`
>
> 这几条 ALTER 在迁移文件里手写(Prisma DSL 不支持生成列也不支持复合 FK 显式定义,需 raw SQL):
> ```sql
> -- categories.kind 用 text + CHECK,直接在 schema.prisma 用 String + Prisma 自动生成的 NOT NULL,
> -- 然后用 raw SQL 添加 CHECK + 复合 UNIQUE
> ALTER TABLE categories ADD CONSTRAINT categories_kind_check CHECK (kind IN ('app','video'));
> ALTER TABLE categories ADD CONSTRAINT categories_id_kind_unique UNIQUE (id, kind);
>
> -- apps/videos 加生成列(text,与 categories.kind 类型严格一致)
> ALTER TABLE apps   ADD COLUMN category_kind text GENERATED ALWAYS AS ('app')   STORED;
> ALTER TABLE videos ADD COLUMN category_kind text GENERATED ALWAYS AS ('video') STORED;
>
> -- 复合 FK
> ALTER TABLE apps   ADD CONSTRAINT apps_category_kind_fk
>   FOREIGN KEY (category_id, category_kind) REFERENCES categories(id, kind);
> ALTER TABLE videos ADD CONSTRAINT videos_category_kind_fk
>   FOREIGN KEY (category_id, category_kind) REFERENCES categories(id, kind);
> ```
> P1 完成判据:把一条 `apps.category_id` UPDATE 到一个 `kind='video'` 的分类应被 DB 拒绝。

> **Prisma 与生成列的协作策略**(关键 — 影响 schema.prisma 写法、Prisma Client、迁移工作流):
>
> Prisma DSL **不能表达** `GENERATED ALWAYS AS ... STORED`(属于 Prisma "unsupported database features",
> 见 https://www.prisma.io/docs/orm/prisma-migrate/workflows/unsupported-database-features)。
> 我们的策略:
>
> 1. **`schema.prisma` 中不声明 `categoryKind` 字段**。即 `model App` / `model Video` 里没有这个字段
> 2. **生成列的 ALTER 写在 raw migration SQL 里**(见上方 SQL 块),发生在 `prisma migrate dev` 之后追加的手写 migration 文件中
> 3. **Prisma Client 不感知该字段**:`prisma.app.create({...})` / `update({...})` 都不需要也不能传 `categoryKind`,DB 会自动填充。读出来的 `App` 对象也不含 `categoryKind`(应用层不需要,因为 kind 已经隐含在表归属里)
> 4. **复合 FK 的执行**完全在 DB 层。Prisma 只通过 `categoryId` 单字段关联,DB 用 `(categoryId, categoryKind)` 复合 FK 实际校验
> 5. **避免 introspection 漂移**:**绝对不跑 `prisma db pull`**(它会把生成列拉回 schema.prisma 并破坏前述策略)。CI 可加 `prisma migrate diff --from-schema-datamodel ... --to-schema-datasource ...` 检查 schema 与 DB 是否吻合;diff 中预期会显示"DB 多出 `category_kind` 列",这是已知差异,在 CI 脚本里允许这条差异
> 6. **新增/修改约束**:任何对 categories/apps/videos 的结构变更都必须先评估对生成列与复合 FK 的影响;在 Prisma 生成迁移之后,**手动在 migration SQL 末尾追加**生成列重建语句(如必要)
>
> 这条策略在 §3.4 取舍清单第 8 条记录(下文)。

**`guides`**
```
id              uuid PK
slug            text  unique  not null     -- e.g. 'choose-app'
title           text          not null
summary         text          not null     -- 列表页摘要 = 原型 desc
body_md         text          not null     -- 长文 markdown(由 :1612 bodies 转码)
category_slug   text          not null     -- e.g. 'app' / 'video' / 'privacy' / 'social'
category_label  text          not null     -- e.g. 'App 使用'(冗余,展示用)
gradient_key    text          not null     -- e.g. 'g-brand'(对应 §3.2 GRADS)
icon_key        text          not null     -- e.g. 'i-smartphone'(SVG sprite name)
read_minutes    int           not null     -- 原型 read 文案解析为整数(如 '8 分钟' → 8)
views_label     text          not null     -- 原型 views 直接保留为字符串(如 '2.3万')
is_hot          bool          not null  default false
published_date  date          not null     -- 来源 :623 的 date 字段
status  ts  …
```

> P2 列表/详情视觉所需的字段(date / cat / grad / svg)都在 schema 内,**不再依赖 fixture**。
> `category_slug` 与 `GUIDE_CATS` 的 id 对齐(`app` / `video` / `privacy` / `social`),
> 对应 `category_label` 是冗余存储的展示文案(避免每次查询都 JOIN 字典)。

**`categories`**
```
id           uuid PK
slug         text       not null
label        text       not null
description  text
kind         text       not null    CHECK (kind IN ('app','video'))
sort_order   int        not null  default 0
UNIQUE (kind, slug)        -- slug 在 kind 内唯一,跨 kind 可重复(如 'life')
UNIQUE (id, kind)          -- 复合 FK 目标(见 apps/videos)
```

> **`kind` 为什么是 `text + CHECK` 而不是 Postgres ENUM**:
> apps/videos 用 `GENERATED ... STORED` 列做复合 FK 指向 `categories(id, kind)`,
> Postgres 要求 FK 两端类型严格兼容。如果 `categories.kind` 是 ENUM,生成列也必须显式 cast 成同名 ENUM
> (`'app'::"CategoryKind"`),Prisma DSL + 我们手写迁移 SQL 一起维护这个 enum 名容易出错。
> 改用 `text + CHECK` 后,生成列就是普通 `text`,FK 直接对得上,Prisma 也不用声明 enum。
> 代价:DB 不再有原生 ENUM 的强类型保证,但 CHECK 等价覆盖。

App 与 Video 共用一张表,用 `kind` 区分。

**Slug 跨 kind 重复的处理**(关键):
- 原型里 `'life'` 同时是 App 分类(`APP_CATS`)和视频分类(`CATEGORIES`),seed 后会得到两条 `slug='life'` 的行,必须靠 `UNIQUE(kind, slug)` 容纳
- **不**用 `UNIQUE(slug)` 全局唯一(会 seed 失败)
- **路由语义**(避免 `/category/:slug` 歧义):
  - `/category/:slug` **仅解析视频分类**(对齐原型 `renderCategoryDetail`)。命中 `categories WHERE kind='video' AND slug=:slug`
  - **App 分类不走 `/category/:slug`**,只在 `/apps?cat=:slug` 作为筛选 tab 出现(对齐原型 `APP_CATS` 用法)
  - 这条规则写在 §2.1 路由表注脚 + `/category/[slug]/page.tsx` 的查询条件里

**`tags` + `app_tags` / `video_tags`**
```
tags
  id     uuid PK
  slug   text  not null  UNIQUE      -- kebab-case 英文
  label  text  not null  UNIQUE      -- 显示文案,通常中文。一个概念只允许一条记录
app_tags(app_id, tag_id)             -- 复合主键 (app_id, tag_id)
video_tags(video_id, tag_id)         -- 复合主键 (video_id, tag_id)
```

> **`label` 也必须 UNIQUE** 的原因:seed 走 `ALL_TAGS ∪ APPS[*].tags ∪ VIDEOS[*].tags` 并集去重,假设一个 label
> 只对应一条记录;如果 admin 后续允许同 label 不同 slug,会出现"两个『健身』,卡片显示一致但 URL 不同",
> 搜索/聚合行为会混乱。约束放 DB 里,admin 表单同步做 label 重复校验(返回 422)。
> 查询路径仍以 slug 为准(URL 友好);label 是显示用。

不做 polymorphic taggings,两张直白的关系表更简单。

**`collections`(专题/专辑/榜单三合一)**
```
id           uuid PK
slug         text  unique  not null
kind         enum (topic | album | ranking)  not null
title        text  not null
description  text
cover_key    text
sort_order   int   not null  default 0   -- 同一 kind 内的列表展示顺序
status  ts  …
```

三种业务概念结构完全一样:都是"有序内容集合"。用 `kind` 区分,运营端 UI 给三种独立入口,但底层是一套 CRUD + 排序逻辑。

> **`sort_order` 用途**(关键):
> - **`/topics`** 列表按 `(kind='topic', status='published') ORDER BY sort_order ASC, created_at ASC`
> - **`/rankings`** 6 个区块的展示顺序按 `(kind='ranking', status='published') ORDER BY sort_order ASC`
>   — seed 时按原型 `renderRankings` 的渲染顺序赋值:
>   `weekly-hot-videos=0` `latest-videos=1` `top-liked-videos=2` `weekly-hot-apps=3` `top-rated-apps=4` `hot-tags=5`
> - **`/albums`** 列表(P6)同样按 `sort_order ASC`
> - 不依赖 `created_at` / `slug` 字典序,排序行为可控可预测
>
> 与 `collection_items.position` 是不同维度:`sort_order` 决定"集合之间"的顺序,`position` 决定"集合内成员"的顺序。

**`collection_items`(多态成员,带排序)**
```
id              uuid PK                       -- 稳定主键,拖拽排序时按 id 更新
collection_id   ──→ collections.id
position        int        not null           -- 排序键,小=靠前
ref_type        enum: app | video | tag | external
app_id          ──→ apps.id          (nullable)
video_id        ──→ videos.id        (nullable)
tag_id          ──→ tags.id          (nullable)
redirect_id     ──→ redirects.id     (nullable, 仅 ref_type=external)
external_label  text                 (nullable, 仅 ref_type=external,卡片显示文案)
note            text                 -- 编辑可补充的卡片说明
UNIQUE (collection_id, position) DEFERRABLE INITIALLY DEFERRED
CHECK (恰好一个 *_id 非空,且与 ref_type 匹配:
       app→app_id, video→video_id, tag→tag_id, external→redirect_id)
```

> **不用 (collection_id, position) 做复合主键**。理由:拖拽重排时需要批量改 position,如果 position 是主键的一部分,
> 中间态会出现 PK 冲突。改用独立 `id uuid PK` + `DEFERRABLE INITIALLY DEFERRED` 唯一索引,事务内可经过中间态,
> 提交时再校验唯一性,Prisma `$transaction` 里就能稳妥重排。

> **关于 CHECK 约束与 DEFERRABLE 唯一索引的实现**:Prisma `schema.prisma` 不支持 CHECK 关键字,
> 也不支持 `DEFERRABLE INITIALLY DEFERRED` 修饰。这两条都必须在迁移文件里**手写 raw SQL**:
>
> **重要**:`schema.prisma` 里的 `CollectionItem` model **不要**写 `@@unique([collectionId, position])`。
> Prisma 的 `@@unique` 会生成普通(非 deferrable)的唯一索引;一旦同时存在普通 unique 与 deferrable unique,
> 拖拽交换 position 时会被普通 unique 拦截。**唯一约束完全由下面的 raw SQL 创建**,Prisma DSL 只声明字段、不声明约束。
> ```sql
> -- ref 字段互斥
> ALTER TABLE collection_items ADD CONSTRAINT collection_items_ref_match CHECK (
>   (ref_type = 'app'      AND app_id IS NOT NULL AND video_id IS NULL AND tag_id IS NULL AND redirect_id IS NULL) OR
>   (ref_type = 'video'    AND video_id IS NOT NULL AND app_id IS NULL AND tag_id IS NULL AND redirect_id IS NULL) OR
>   (ref_type = 'tag'      AND tag_id IS NOT NULL AND app_id IS NULL AND video_id IS NULL AND redirect_id IS NULL) OR
>   (ref_type = 'external' AND redirect_id IS NOT NULL AND app_id IS NULL AND video_id IS NULL AND tag_id IS NULL)
> );
> -- 同一 collection 内 position 唯一(事务结束时才校验,允许中间态冲突)
> ALTER TABLE collection_items ADD CONSTRAINT collection_items_position_unique
>   UNIQUE (collection_id, position) DEFERRABLE INITIALLY DEFERRED;
> ```
> P1 完成判据中包含"首版迁移文件包含此 CHECK + DEFERRABLE UNIQUE SQL"。

> 外链不再直接持有 URL,而是通过 `redirect_id` 指向 `redirects` 表的一行。这样:
> - URL 只存一份(`redirects.target_url`),改 redirect 同时改所有引用
> - 所有外链点击都自然走 `/r/:id`,统一打点
> - 运营端创建 external item 时,后台自动建一条 `redirects` 记录(owner_kind='collection_item')

**`redirects`**
```
id          uuid (即 /r/:id 的 :id)
target_url  text             not null         -- 真实第三方 URL,必须通过 §4.2 的校验
owner_kind  app | video | external | collection_item
owner_id    text             -- 反查归属
disabled    bool default false
created_at  …
```

> **`target_url` 安全校验规则**(防 open redirect / XSS / 内网 SSRF):
> 1. 协议白名单:**仅允许 `http://` 和 `https://`**(优先 https)。拒绝 `javascript:` / `data:` / `file:` / `ftp:` / 自定义 scheme
> 2. URL 能 `new URL()` 通过、不含换行、控制字符、空字节;长度 ≤ 2048
> 3. **hostname 字面值黑名单**(纯字符串判定,不查 DNS):
>    - `localhost` / `localhost.localdomain`
>    - IPv4 字面值落在 `0.0.0.0/8` `203.0.113.1/8` `203.0.113.1/8` `169.254.0.0/16` `203.0.113.1/12` `203.0.113.1/16` `100.64.0.0/10`
>    - IPv6 字面值落在 `::1` `fc00::/7` `fe80::/10`
> 4. **DNS 解析校验** — 仅 admin 保存时执行:
>    - 用 `dns.promises.lookup(hostname, {all: true})`,**2 秒 timeout**
>    - 若返回的任一 IP 落在上述私有/link-local/loopback 段 → 拒绝
>    - DNS 失败(超时 / NXDOMAIN)→ 拒绝并提示运营修正
>
> **校验落点 — 分层(避免 /r/:id 依赖 DNS)**:
>
> | 时机 | 阶段 | 做什么 | 不做什么 |
> |---|---|---|---|
> | Admin 保存 redirect | P5/P7 | 1+2+3+**4(完整 DNS)** | — |
> | `pnpm db:enable-redirect` 脚本 | P3 | 1+2+3+**4(完整 DNS)** | — |
> | `/r/:id` 请求时兜底 | P3 | 1+2+**3(字面值)** | **不做 DNS 解析**(避免运行时延迟与抖动) |
>
> 设计意图:DNS 解析仅在写入路径上发生,跳转路径只做无副作用的语法/字面值检查。
> 历史脏数据如果 hostname 字面值合法但 DNS 实际解到内网,**接受这个残余风险** — 写入门已经把好关。
>
> 校验函数放在 `packages/db/src/lib/url-policy.ts`,导出两个入口:
> - `validateForWrite(url): Promise<Result>` —— 含 DNS 校验(异步)
> - `validateForRedirect(url): Result` —— 仅字面值校验(同步、无 IO)

**`click_events`**(采集最小化)
```
id              uuid PK
redirect_id     ──→ redirects.id
ts              timestamptz      not null    -- indexed
ua_family       text             not null  default 'unknown'   -- 解析失败回落到 'unknown'
ua_os           text             not null  default 'unknown'
country         text             not null  default 'unknown'   -- 本地 dev 也是 'unknown'
referrer_origin text             not null  default 'unknown'   -- 仅 origin,去掉 path/query
ip_hash         text             not null                      -- pseudonymous data(非匿名)
```

> 这些维度字段都不可空,解析失败时回落 `'unknown'`。这样聚合表的主键不会因 NULL 而行为怪异
> (Postgres 里 NULL ≠ NULL,会导致同一组 NULL 行无法被 PK 合并)。

**字段口径(关键)**:
- 不存原始 UA、不存原始 referrer、不存原始 IP。原文不入库,解析后丢弃。
- `referrer_origin` 只保留来源站点身份,去除带个人偏好的 query/path。
- `ua_family + ua_os` 提供"什么设备"维度,但不构成可识别个人的指纹。
- `DAILY_SALT = HMAC(IP_HASH_SECRET, YYYY-MM-DD UTC)`(详见 §4.2),按日轮换 → 同一访客跨天的 hash 不同,弱化追踪。
- **取不到 IP 时**(本地 dev、缺少代理头、Header 被剥):`ip_hash = sha256('unknown' + DAILY_SALT)`,字段保持 NOT NULL。所有"取不到"的请求会落到同一个 hash,这是可接受的(对当日聚合表现为一个"unknown 访客桶")。

**保留期**:
- 原始 `click_events` 保留 **30 天**
- 30 天后聚合到 `click_daily_stats` 表(见下),原行被定时任务删除
- 这条管线 P3 不上线;P7 引入聚合任务

**`click_daily_stats`**(聚合表)
```
redirect_id   ──→ redirects.id
day           date          not null                      -- UTC 日期
ua_family     text          not null  default 'unknown'   -- 与 click_events 同口径
country       text          not null  default 'unknown'
count         bigint        not null
PRIMARY KEY (redirect_id, day, ua_family, country)
```

> **聚合 SQL — 必须在单个事务内,且加 advisory lock 防并发**:
> ```sql
> BEGIN;
>
>   -- 防并发:两个 cron 同时跑会双倍累加 count。固定的 lock key 让第二个调用阻塞或 try_lock 失败
>   SELECT pg_advisory_xact_lock(8131421);   -- 任意稳定整数,作为 click_events 聚合任务的 lock key
>
>   -- 1) upsert 聚合
>   INSERT INTO click_daily_stats (redirect_id, day, ua_family, country, count)
>   SELECT
>     redirect_id,
>     (ts AT TIME ZONE 'UTC')::date AS day,
>     COALESCE(ua_family, 'unknown'),
>     COALESCE(country, 'unknown'),
>     count(*)
>   FROM click_events
>   WHERE ts < now() - interval '30 days'
>   GROUP BY 1, 2, 3, 4
>   ON CONFLICT (redirect_id, day, ua_family, country)
>   DO UPDATE SET count = click_daily_stats.count + EXCLUDED.count;
>
>   -- 2) 同事务删除已聚合的原始行 — 失败则整段回滚,下次重新聚合,count 不会双倍
>   DELETE FROM click_events WHERE ts < now() - interval '30 days';
>
> COMMIT;
> ```
>
> **幂等性保证**:
> - INSERT 单独不幂等(`+= EXCLUDED.count` 每次累加),所以**必须**和 DELETE 同事务,失败一起回滚
> - `pg_advisory_xact_lock` 在事务结束时自动释放;两个并发任务里第二个会阻塞等锁,不会双跑
> - 因为 `click_events` 的字段已经 NOT NULL DEFAULT 'unknown',COALESCE 主要是防御性兜底

索引:`(redirect_id, ts DESC)`。MVP 单表;量大后再考虑分区或迁到 ClickHouse,**对外接口不变**。

**`admin_users`**
```
id              uuid PK
github_id       bigint  unique  not null    -- 主标识
github_login    text    unique  not null    -- 白名单匹配字段(GitHub username)
github_email    text                        -- 仅供展示,可为空(私有邮箱场景)
name            text                        -- 来自 GitHub profile.name
last_login_at   timestamptz
created_at      timestamptz
```

**Auth 模型**:
- 不存密码。Auth.js v5 + **GitHub OAuth Provider**(MVP 选定)
- **不使用 PrismaAdapter**。原因:PrismaAdapter 要求标准的 `User` / `Account`(/ `Session` / `VerificationToken`)四表才能正常工作,而我们只有 `admin_users` 一张内部表,语义也不同(这里是"运营成员"不是"用户")。强行套 PrismaAdapter 要么补 3 张无意义的 Auth.js 表、要么改 schema 名字去迁就它,得不偿失。
- **改用纯 callback 实现**:
  - `signIn` callback:① 校验 `profile.login` 在白名单 `ADMIN_ALLOWED_GITHUB_LOGINS`(env,逗号分隔)内,否则返回 false → 401;② Prisma 直接 upsert `admin_users` by `github_id`(不走 adapter);③ 写入 `last_login_at`
  - `jwt` callback:把 `admin_users.id` 注入 token
  - `session` callback:把 `adminUserId` 暴露给应用层
- 白名单字段是 `github_login`(GitHub username),**不用 email**(GitHub email 可为空/私有/多个,不可靠)
- Session 策略:**JWT session**(Auth.js 默认,无需 sessions 表)
- 这条决定使表数保持 14(不额外引入 Auth.js 的 `User` / `Account` 等标准表),代价是 ~30 行 callback 代码

**`audit_log`**
```
id  admin_user_id  action(text, e.g. "app.update")
target_type  target_id  diff_json  ts
```

每次写操作落一条,便于追溯与回滚证据链。

### 3.3 ER 关键链路

```
                 ┌──────────────────┐
                 │  collections     │      (kind: topic / album / ranking)
                 └────────┬─────────┘
                          │ 1:N (有序)
                 ┌────────▼─────────┐
                 │ collection_items │
                 └──┬───┬───┬───┬───┘
                    │   │   │   │  (多态:四选一,FK 互斥)
        ┌───────────┘   │   │   └───────────┐
        ▼               ▼   ▼               ▼
    ┌──────┐       ┌────────┐  ┌──────┐  ┌──────────┐
    │ apps │       │ videos │  │ tags │  │ redirects│ ← external 走这条
    └──┬───┘       └───┬────┘  └──────┘  └────┬─────┘
       │               │                       │
       │ N:1           │ N:1                   │
       │               │                       │  apps/videos 各自通过
       │               │                       │  redirect_id ──→ redirects
       ▼               ▼                       │  ──→ click_events
   ┌──────────────────────┐                    │
   │ categories (kind=…)  │                    ▼
   └──────────────────────┘             ┌──────────────┐
                                        │ click_events │
                                        └──────────────┘
```

### 3.4 有意识的取舍

1. **不做多对多 polymorphic taggings** — 两张直白表(`app_tags` / `video_tags`)更简单,索引更优,Prisma 类型清晰。代价:tag 复用语义靠应用层保证。
2. **collections 三合一** — topic/album/ranking 共表;若某种业务字段大量分叉,再拆。
3. **categories 单表 + kind** — 同理,有分叉再拆。
4. **不做 i18n** — 全站单一中文。
5. **不引入 Redis** — Postgres 索引 + Next.js cache 足够;部署形态确定后再考虑加边缘缓存。
6. **不用 Auth.js 标准表** — 只保留 `admin_users`,登录走 callback 手动 upsert。代价:多写 ~30 行 callback;收益:不引入 3 张语义不符的 Auth.js 表。
7. **CHECK 约束放迁移 SQL,不放 schema.prisma** — Prisma DSL 不支持 CHECK,只能在 migration 里手写。每次改 collection_items 结构时记得同步约束。
8. **生成列(`category_kind`)不出现在 `schema.prisma`** — 走 raw migration,Prisma Client 不感知,**禁用 `prisma db pull`**;CI 用 `prisma migrate diff` 时把 `category_kind` 列差异加白名单。详见 §3.2 apps/videos 块下的"Prisma 与生成列的协作策略"。

---

## 4. 关键交互与数据流

### 4.1 页面端读取(SSG + ISR)

```
[构建 / ISR 触发]
  apps/web 在构建期 / 后台再生时,通过 packages/db 直连 Postgres
  ──→ 查询 published 状态的内容
  ──→ 渲染为静态 HTML
  ──→ 用户浏览器拿到的是静态页 + 客户端 hydration

ISR 重新生成的触发条件:
  - 时间触发:列表页每 60 秒;详情页每 5 分钟
  - 主动触发:admin 发布动作 → 调 web 的 /api/revalidate(by tag/path)
```

> **CI 含义(分阶段)**:
> - **P0**:页面是空白,`pnpm build` 不查 DB,CI 只跑 `lint / typecheck / build`,不需要 Postgres service
> - **P1 起**:CI 升级到 `postgres:16` service + `DATABASE_URL` + `prisma migrate deploy` + `prisma db seed` + lint/typecheck/build。**P1 必须跑通这条闭环**,否则 P2 合入(页面开始 SSG 查 DB)后 CI 会在 build 阶段断在 "PrismaClientInitializationError"
> - 之后阶段沿用 P1 的 CI 配置,只是要保证 seed 的行数断言随 P1 完成判据更新而通过

### 4.2 跳转打点(用户点外链)

**路由位置**:`apps/web/app/r/[id]/route.ts` → 公开 URL `/r/:id`。
> 不放在 `app/api/r/[id]/route.ts` 下,否则会变成 `/api/r/:id`,与外链短链不符。

**Runtime(关键)**:文件顶部显式声明
```ts
export const runtime = 'nodejs';        // 不用 edge,Prisma 直连本地/自托管 Postgres 需要 nodejs
export const dynamic = 'force-dynamic';  // 不缓存,每次都打点
```

**MVP 写入策略 — 同步**:
- P3 内,`click_events` INSERT **同步**完成后再 302。本地 Postgres 单 INSERT 通常 < 5ms,可接受
- 不依赖 `waitUntil` / `unstable_after` / 队列。这些都是部署形态决定后才能选定的,与"本地 Docker 跑通"目标无关
- 真到了延迟瓶颈(单条 > 30ms 或 QPS 高),再引入异步(届时再决定:Node `setImmediate` + 内存缓冲 / pg `LISTEN/NOTIFY` / 平台专属 waitUntil / 独立队列)。**这条改造对外契约不变**

```
用户点 App 详情页"前往下载"
  → <a href="/r/{redirectId}">

apps/web/app/r/[id]/route.ts (runtime='nodejs'):
  1. SELECT target_url, disabled FROM redirects WHERE id = :id
  2. 若 disabled 或 not found → 302 到 /404
  3. 调 url-policy.validateForRedirect(target_url) — 同步、无 IO
     —— 协议白名单 + URL 语法 + hostname 字面值黑名单(不做 DNS)
     不通过 → 302 到 /404(不打点)
  4. 同步 INSERT INTO click_events(...) — 字段口径见 §3.2
     原始 IP / 原始 UA / 原始 referrer 不入库,在请求处理函数内解析后即丢弃
     - country: 从代理头取(本地 dev 取 'unknown',解析失败也回落 'unknown')
     - ip_hash: sha256(ip + DAILY_SALT)
       DAILY_SALT = HMAC(IP_HASH_SECRET, YYYY-MM-DD UTC) — 每天 0 点 UTC 自然轮换
     - ua_family / ua_os: 用 ua-parser-js 解析后只存解析结果(失败 'unknown')
     - referrer_origin: new URL(referrer).origin,失败 'unknown'
  5. 302 到 target_url
```

### 4.3 运营编辑 → 发布 → 透出

```
[admin 编辑器]
  保存草稿:status='draft' UPDATE
  发布:    status='published' UPDATE + audit_log INSERT
            → POST https://web/api/revalidate
                Authorization: Bearer ${REVALIDATE_SECRET}
                Body: { "tags": ["app:slug", "apps-list"] }
            → web 立即重新生成相关页面
```

**Secret 约定**:
- `REVALIDATE_SECRET` 是 web 与 admin 共享的 env(运维下发,本地 dev 用 `.env.local`)
- web 的 `/api/revalidate` handler 必须先校验 `Authorization` 头,失败返回 401
- 不把 secret 放进 URL 查询串,避免出现在日志里

### 4.4 搜索(MVP)

```
apps/web/api/search?q=:q
  → packages/db.search(q):
       三类内容并行查询 (apps / videos / guides),各 limit 10
       → 合并返回 + 简单按命中字段权重排序(name/title > tag > desc)
```

**实现路线**:
- **主**:`ILIKE '%q%'` 命中以下字段(取并集):
  - apps: name, short_desc, detail
  - videos: title, short_desc, detail
  - guides: title, summary, body_md
  - 标签命中:从 `tags.label ILIKE '%q%'` 反查 app/video
- **加速**:对上述 text 字段建 **`pg_trgm` GIN 索引**(`CREATE EXTENSION pg_trgm`)。pg_trgm 是 PostgreSQL 官方扩展,基础镜像就有,无需自定义镜像
- **不做**:Postgres `to_tsvector` 全文索引。`simple` 配置对中文(无空格)等价于把整段当一个 token,不能切词;声称"FTS 中文搜索"会误导。FTS 仅在未来若添加英文字段时再考虑

> 决定回顾:之前 §4.4 写了"PostgreSQL FTS + simple 配置",这个表述不准确。MVP 的实际查询路径是 `ILIKE + pg_trgm`。

### 4.5 数据初始化(从原型迁出)

**原型实际命名(已核对 `docs/ghome.html`):**

| 原型常量 | 行号 | 落到 |
|---|---|---|
| `APPS` | :525 | `apps` 表 |
| `VIDEOS` | :579 | `videos` 表 |
| `APP_CATS` | :537 | `categories` (kind=app) — **排除 `id='all'`**,这一项是前端筛选 tab,不是真实分类 |
| `CATEGORIES` | :602 | `categories` (kind=video) |
| `ALL_TAGS` ∪ `APPS[*].tags` ∪ `VIDEOS[*].tags` | :611 / :526+ / :580+ | `tags` 表(必须取**全并集**;见下"tag 来源与 slug 规则") |
| `TOPICS` | :613 | `collections` (kind=topic) + `collection_items` |
| `renderRankings` 6 个榜单 | :1412 | **`collections` (kind=ranking) + `collection_items`** — 每个榜单一条 `collections` 记录,`collection_items` 按原型 `renderRankings` 里的 sort + slice(5 内容榜 `slice(0,8)`、`hot-tags` `slice(0,10)`)结果**冻结**为有序成员(详见下"榜单 seed 来源") |
| `GUIDES`(元数据) | :622 | `guides` 表(meta 字段:title / summary / cover / category 等) |
| `renderGuideDetail` 内 `bodies` map | :1612 | `guides.body_md` — **见下"指南正文转码"** |
| `FEATURED_WEB` | :515 | **不入库,P2 用静态 fixture**(详见下) |
| `CREATORS` | :554 | **不入库,P2 用静态 fixture** |
| `SAMPLE_REVIEWS` | :548 | **不入库,P2 用静态 fixture** |
| `GUIDE_CATS` | :630 | 暂不建独立表,作为 `guides.category_label` 的字典在代码里 |

**外链(target_url)的处理 — 关键**:
原型里所有 CTA(如 `<a class="btn btn-filled" data-link="/app/${a.id}">立即下载</a>` :710)都是**站内 data-link**,**没有真实第三方 URL**。因此 seed 时:

- 对每个 App / Video 建一条 `redirects` 记录,字段:
  - `target_url` = `'https://example.com/seed/{kind}/{slug}'`(占位)
  - `disabled` = `true`(默认禁用,运营在 admin 填入真实 URL 并启用前不会向用户暴露)
  - `owner_kind` / `owner_id` 正常填写
- web 端渲染时:对 `disabled=true` 的 redirect,CTA 按钮置灰 + 文案改为"暂未开放",不渲染 `/r/:id` 链接
- **P3 启用方式**:`pnpm db:enable-redirect <id> <real-url>` 脚本(走 `validateForWrite`,DNS + 字面值都校验后才入库并 `disabled=false`)
- **P5+ 启用方式**:运营在 admin 编辑器里填真实 URL 并启用,服务侧同样调 `validateForWrite`

**榜单 seed 来源**:
原型 `renderRankings` (`docs/ghome.html` :1412) 在 JS 里对 APPS/VIDEOS/ALL_TAGS 做即时排序后渲染。MVP 把这一时刻的结果**冻结**进 6 条 ranking collections:

| collection.slug | kind | items 来源(seed 时计算一次,写入 collection_items) |
|---|---|---|
| `weekly-hot-videos` | ranking | VIDEOS 取 views_label 最大的**前 8**(views 文案手工解析为数,如 '38.1万' → 381000) |
| `latest-videos`     | ranking | VIDEOS 按 published_date desc **前 8** |
| `top-liked-videos`  | ranking | VIDEOS 按 likes_label desc **前 8** |
| `weekly-hot-apps`   | ranking | APPS 按 users_label desc **前 8**(共 9 个 App,取前 8 与原型一致) |
| `top-rated-apps`    | ranking | APPS 按 rating desc **前 8** |
| `hot-tags`          | ranking | **遍历 `ALL_TAGS`**,每条计数 = `count(VIDEOS where tag ∈ v.tags)`(只数视频,不数 App,与原型 `:1418` 一致),按计数 desc **前 10**;`ref_type='tag'` |

> 上述 take 数量(5 × 8 + 1 × 10 = **50 条** ranking_items)是直接对齐原型 `renderRankings` `:1413-1418` 的 `slice(0, 8)` / `slice(0, 10)`。
>
> **`hot-tags` 只统计视频** — 这是与原型有意识的对齐(原型只 `VIDEOS.filter(...)`,不数 App)。
> 后期如果要升级为"全站 tag 热度",需把它移出 §6 后续清单;现在保持冻结。
>
> **每条 collection 的 `sort_order` 赋值**(seed 时写入,影响 `/rankings` 6 区块顺序):
> `weekly-hot-videos`=0 / `latest-videos`=1 / `top-liked-videos`=2 / `weekly-hot-apps`=3 / `top-rated-apps`=4 / `hot-tags`=5。
> TOPICS 的 6 条按原型 `TOPICS` 数组顺序赋 0..5。

> **`/rankings` 路由**直接读这 6 条 collections,渲染 6 个榜单区块。不做运行时排序。运营可以在 admin 改顺序、置顶、增删,
> 但当前数据集小、变更不频繁,这条路径足够。
> 后续如要"自动按点击量"调权,会引入 `apps.users_count` `videos.views_count` 等 numeric 列 + 定时任务回写 ranking,
> 那时再切换路由策略。

**指南正文转码**:
- 原型里 5 篇指南的正文不在 `GUIDES` 常量里,而在 `renderGuideDetail` 函数内的 `bodies` 对象里(`docs/ghome.html` :1612 起),内容是 HTML 片段(`<h2>` / `<h3>` / `<p>` / `<ul>` / `<li>`)
- seed 时**手工把这 5 段 HTML 转成 Markdown**,放进 `packages/db/prisma/seed-data/guide-bodies.ts`(标题对应到 GUIDES.id)。HTML→MD 仅 5 篇、结构平直,人工转译比引入 turndown 库简单。
- 转换后写入 `guides.body_md`。P5 用 Markdown 编辑器编辑同一字段。

**Tag 来源与 slug 规则**:
- **来源 — 全并集**:`tags` 表必须 seed 出 `ALL_TAGS ∪ APPS[*].tags ∪ VIDEOS[*].tags` 三个集合的并集去重后的所有 label。**只 seed `ALL_TAGS` 是错的** — 大量 App/Video 自带的 tag(如 `'社交'` `'附近的人'` `'走心交友'` `'训练'` `'打卡'` `'风光'` `'长期关系'` `'毕业'`...)不在 `ALL_TAGS` 里,落不进 `tags` 表会让 `app_tags` / `video_tags` 的 FK 写入失败
- **slug 映射**:每个 label 必须有显式英文 slug 映射;无映射时 seed **直接 fail**(打印缺失 label 列表)
- **slug 规范**:`/^[a-z0-9-]+$/`,kebab-case
- **存放位置**:`packages/db/prisma/seed-data/tags.ts` 导出一个完整的 `Record<string, string>`;由 P1 任务一次性补齐(粗估 50~60 条)。spec 不嵌入完整列表,避免与代码漂移。`ALL_TAGS` 16 条的初版映射作为起点(下表)
- **DB 约束**:`tags.slug` UNIQUE;admin 新增 tag 表单做客户端校验(`/^[a-z0-9-]+$/`)+ 服务端二次校验

`ALL_TAGS` 部分的初版映射(完整版在 `seed-data/tags.ts`):
  ```
  '男同视频'   → 'gay-videos'      'Vlog'      → 'vlog'
  'LGBTQ+'    → 'lgbtq'           '生活方式'   → 'lifestyle'
  '情感'      → 'emotion'         '都市'       → 'urban'
  '校园'      → 'campus'          '高颜值'     → 'good-looking'
  'CP向'      → 'couple'          '健身'       → 'fitness'
  '旅行'      → 'travel'          '访谈'       → 'interview'
  '时尚'      → 'fashion'         '饮食'       → 'food'
  '文化'      → 'culture'         '阅读'       → 'reading'
  ```

**脚本入口**:`packages/db/prisma/seed.ts`,通过 `prisma db seed` 调用。脚本用静态导入(把 `docs/ghome.html` 里的 JS 数据**复制**为 TS 模块),不在 runtime 解析 HTML。

---

## 5. MVP 分阶段切片

每阶段都是 **端到端可演示**,不是"先做完后端再做前端"。

| Phase | 内容 | 完成判据 |
|---|---|---|
| **P0 · 脚手架** | pnpm workspace + Next.js × 2 + Prisma 客户端依赖(**先不写 schema**)+ docker-compose Postgres + 极简 GitHub Actions CI(`pnpm lint` → `pnpm typecheck` → `pnpm build`)。两个 app 是空白页,build 不查 DB,因此 CI 此阶段不需要 Postgres service | `pnpm dev` 起两个空白页;`docker compose up -d` 起来 Postgres(只是为了验证拓扑可用);CI 在 PR 上绿勾(三步 lint/typecheck/build 全过) |
| **P1 · 数据模型 + Seed** | 14 张表 schema(`schema.prisma`,**不**声明 `@@unique([collectionId, position])`)、首版迁移(含手写 SQL:`categories_kind_check` + `categories_id_kind_unique` + apps/videos `category_kind` 生成列与复合 FK + `collection_items_ref_match` CHECK + `collection_items_position_unique` DEFERRABLE UNIQUE)、`pg_trgm` 扩展启用、`url-policy` 工具函数、**tag 全并集** slug 映射表、guide bodies HTML→MD 转译、原型数据导入脚本(APP_CATS 排除 `all`,seed 出 disabled 占位 redirect);**CI 升级**:GitHub Actions 加 `postgres:16` service + `DATABASE_URL` env,步骤补 `prisma migrate deploy` → `prisma db seed` 在 lint/typecheck/build 之前(后续 P2 build 期会查 DB,P1 起 CI 必须能跑通这条闭环) | **行数断言**:apps=9 / videos=20 / 专题(`collections kind=topic`)=6 / **榜单(`collections kind=ranking`)=6** / 指南=5(5 篇正文字符数 > 0);`tags` 行数 = ALL_TAGS ∪ APPS[*].tags ∪ VIDEOS[*].tags 去重数;`app_tags` 行数 = `sum(APPS[*].tags.length)`(预期 27);`video_tags` 行数 = `sum(VIDEOS[*].tags.length)`(预期 60,以原型实际为准);`redirects WHERE disabled=true` ≥ 29;**ranking collection_items**:5 个内容榜各 8 条 + `hot-tags` 10 条 = **50 条**(完全对齐原型 `renderRankings`)。**抽样**:任取一个 App,JOIN `app_tags` `tags` 后 `tags.slug` 数量 = 原型该 App 的 tags 数;同样抽一个 Video。**约束自检**:错 ref_type 的 collection_items INSERT 被拒;事务内交换两行 position 不报错;把 `apps.category_id` 改成 `kind='video'` 的分类被拒;插入两条 `tags.label='健身'` 被拒 |
| **P2 · 页面端只读** | 用 SSG/ISR 把**原型**已有的所有页面用 DB 数据重渲(首页 / `/apps` / `/app/:slug` / `/videos` / `/video/:slug` / `/categories` / `/category/:slug` / `/tag/:slug` / `/topics` / `/topic/:slug` / `/guides` / `/guide/:slug` / `/rankings` / `/about` / `/contact` / `/terms`);**`/albums` `/album/:slug` 不在 P2 范围**(原型无此路由,留给 P6);`/rankings` 渲染 6 条 ranking collections;**FEATURED_WEB / CREATORS / SAMPLE_REVIEWS 暂作为 `apps/web/fixtures/*.ts` 静态数据**(显式不入库) | 浏览 web 站,App/视频/分类/专题/**榜单**/指南数据来自 DB;Featured/创作者/评论区数据来自 fixture(代码内常量);`/rankings` 显示 6 个榜单(5 内容榜各 8 条 + 标签榜 10 条),与原型一致;`/albums` 此阶段返回 404 或空态(明确 P6 实现) |
| **P3 · 跳转中转 + 点击打点** | `apps/web/app/r/[id]/route.ts`、`click_events` 写入(按 §3.2 字段口径)、详情页 CTA 改为渲染 `/r/:id`(disabled 时置灰)、提供一个 `pnpm db:enable-redirect <id> <url>` 脚本(走 url-policy 校验后启用一条 redirect) | 用脚本启用一条 redirect → 前台点击能 302 到目标;DB 能看到 click_events 行(无原始 IP/UA/referrer);用 `javascript:` 之类 URL 调脚本必须被 url-policy 拒绝 |
| **P4 · 运营端骨架 + Auth** | apps/admin 起来、Auth.js GitHub OAuth + `ADMIN_ALLOWED_GITHUB_LOGINS` 白名单、Dashboard 显示统计(草稿/已发布数 + 7 日点击趋势) | 白名单 GitHub 用户能登入 admin,看到统计数字 |
| **P5 · 内容 CRUD** | App / 视频 / 指南 的列表 + 编辑;状态机;触发 web revalidate(带 `REVALIDATE_SECRET` 校验);**标签内联 CRUD**(在 App/视频编辑器里新建 tag,字段:label + slug,服务端校验 slug 形如 `/^[a-z0-9-]+$/` 且 `label` / `slug` 不重复) | 在 admin 改 App 描述并发布,web 刷新后看到;在 App 编辑器里新建一个 tag(如 label='夜跑' slug='night-run')并应用到当前 App,保存后前台 App 详情页能看到这个 tag |
| **P6 · 编辑编排** | collections(**topic / album / ranking 三种 kind 共用同一套** CRUD + 拖拽排序);external item 创建时自动建 redirect;**前台同步交付 `/albums` 列表页 + `/album/:slug` 详情页**(此前 P2 占位,本阶段填充实现);`/rankings` 路由从 6 条 ranking collections 渲染 | 在 admin 建一个新专辑(kind=album)挑 5 张卡(混 App/视频/外链)发布;web `/albums` 列出该专辑、`/album/:slug` 渲染卡片网格;改 `weekly-hot-videos` 的成员顺序后 `/rankings` 同步更新 |
| **P7 · 跳转链管理 + 操作日志** | redirects 列表与批量编辑;audit_log 写入与展示;30 天 click_events 聚合定时任务 | 改一个 redirect 的 target,web 重新跳到新地址;日志能查到这次修改 |
| **P8 · 搜索 + 收尾** | ILIKE + pg_trgm 搜索接口、首页搜索框接通、404 / 性能 / SEO异常验证 收尾 | 搜"健身"返回 App + 视频 + 指南混合结果 |

- **P0–P3** = 用户端可体验的最小闭环;若资源紧张可在 P3 后先停下来对外灰度
- **P4–P7** = 运营端可工作的最小闭环
- **P8** = 收尾

---

## 6. 后续(超出本 spec 范围)

以下事项确认在本 spec **之后** 决定,不影响现有数据模型与 API 设计:

- 部署形态:云托管商选型(Vercel / Fly / Railway / 自建 VPS)、CDN 选型、域名/SSL
- 商业化:CPS 中转链结构、广告位字段细节
- 多语言:`*_translations` 子表
- UGC:用户账号、评论、点赞
- 自动榜单算法(MVP 是手工 seed 的 ranking collections,后期补 numeric 列 + 定时任务回写)
- 分类(categories)的独立 admin 管理页(MVP seed-only)
- 移动端原生 App 或小程序

这些都在当前架构上**叠加式**加,不需要重写既有代码。
