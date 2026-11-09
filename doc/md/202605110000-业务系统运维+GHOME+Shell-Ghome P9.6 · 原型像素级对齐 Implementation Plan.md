---
id: "doc-ea05e325ad48"
title: "Ghome P9.6 · 原型像素级对齐 Implementation Plan"
date: "2026-05-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-11-ghome-p9.6-prototype-parity.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-11-ghome-p9.6-prototype-parity.md"
sourceSha256: "0d80f09ad1063528971e35d526b95d1c23357eb4caf384d28655aaf9ef104417"
sourceSystem: "project-doc"
---

# Ghome P9.6 · 原型像素级对齐 Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605110000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20P9.6%20%C2%B7%20%E5%8E%9F%E5%9E%8B%E5%83%8F%E7%B4%A0%E7%BA%A7%E5%AF%B9%E9%BD%90%20Implementation%20Plan.md)

> 整理日期：2026-05-11 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: `superpowers:subagent-driven-development`.

**Goal:** 把 P9.5 留下的 ~5% 视觉差 + ~3% 交互差 + 视频封面图占位补到 100%。**全程不依赖外部凭证或服务**:视频封面直接从原型 `docs/ghome-20260509.html` 的 base64 `VIMAGES` 常量里抽出,落到本地 `/public/uploads/videos/`。

完成后:
- 视频封面 100% 真图(20/20)
- 视觉与原型像素级对齐(逐页 side-by-side diff,主观差异忽略)
- 交互与原型一致(除 Spec Mode 开发者工具,刻意永远不做)

## Architecture

- **T1 视频封面抽取**:写一次性 Node 脚本 `packages/db/scripts/extract-prototype-covers.ts`,读原型 HTML,正则匹配 `const VIMAGES = { v01: "data:image/jpeg;base64,...", ... }`,base64 解码 → 写 `apps/web/public/uploads/videos/v01.jpg ... v20.jpg`。然后修改 `seed/data/videos.ts` 给每条记录加 `coverImageUrl: "/uploads/videos/{slug}.jpg"`,seed 时写入 DB。

- **T2 视觉 diff 审计**:子 agent 并排打开两个 URL(原型本地 file://、运行时 http://localhost:3001),逐页 13 个核心路由对比,生成具体 diff 清单 + 批改 CSS/markup。

- **T3 交互补遗**:逐项查原型 JS 行为(鼠标悬停过渡、焦点态、滚动锚点、抽屉动画曲线),与当前实现对比,补漏。

## Spec / 引用

- 原型:`docs/ghome-20260509.html`(line 545+ 是 `<script>const VIMAGES = {...}` 块)
- P9.5 plan:`docs/superpowers/plans/2026-05-10-ghome-p9.5-layout-fidelity.md`
- P10a T4 已就绪的 web fallback 逻辑:`VideoCard.tsx` / `VideoHero.tsx` 优先用 `coverImageUrl`,fallback 到 `coverCss(coverKey)`

## 不做(P9.6 范围外)

- **Spec Mode 开发者工具**:永远不做
- **视频文件托管**:仍用 picsum.photos 占位(P10b 接 R2 时再改)
- **App / Guide 真实图片**:它们本来就是 SVG glyph + gradient 设计意图,原型亦如此

## 前置假设

- P10a 完成,`p10a-finishing` 标签存在
- 原型 HTML 已 commit(`docs/ghome-20260509.html` 在 P9 commit `1f394fe`)
- `videos.cover_image_url` 字段在 P10a T1 已加(`coverImageUrl String?`)
- web `VideoCard` / `VideoHero` 已支持 fallback(P10a T4)

## File Structure(P9.6 末态)

```
packages/db/
├─ scripts/
│  └─ extract-prototype-covers.ts                     # T1 一次性脚本
└─ seed/data/videos.ts                                # T1 改:加 coverImageUrl

apps/web/
└─ public/uploads/videos/                             # T1 写入 20 张 .jpg(.gitignore 已排除)
   └─ v01.jpg ... v20.jpg                             # 一次性写入,然后 .gitignore 但有 .gitkeep
```

T2 / T3 的改动散落在 `apps/web/app/**/page.tsx` + `apps/web/components/*.tsx` + `apps/web/app/globals.css`,具体由 diff 清单决定。

## Conventions

- T1 是 build-time 脚本,跑一次写文件即可;不进运行时路径
- T2 / T3 的 CSS / markup 改动小步快跑,**每页一个 commit** 方便回退
- 不引入新依赖
- 提交风格:Conventional Commits;permission 阻塞→DONE_WITH_CONCERNS

---

## Task 1 — 抽取 20 张视频封面 + seed 写入

**Files:**
- Create: `packages/db/scripts/extract-prototype-covers.ts`
- Modify: `packages/db/seed/data/videos.ts`(每条加 `coverImageUrl`)
- Modify: `packages/db/prisma/seed.ts`(upsert 写入 coverImageUrl)
- Files written at runtime: `apps/web/public/uploads/videos/v01.jpg ... v20.jpg`(gitignored,运行 seed 后产生)

### Steps

1. 写脚本:
   ```ts
   // packages/db/scripts/extract-prototype-covers.ts
   import { readFile, mkdir, writeFile } from "node:fs/promises";
   import { resolve } from "node:path";

   const PROTOTYPE = resolve(process.cwd(), "..", "..", "docs", "ghome-20260509.html");
   const TARGET_DIR = resolve(process.cwd(), "..", "..", "apps", "web", "public", "uploads", "videos");

   async function main() {
     const html = await readFile(PROTOTYPE, "utf8");
     // VIMAGES = { v01: "data:image/jpeg;base64,..." } — extract entire object literal then parse
     const m = html.match(/const VIMAGES\s*=\s*\{([\s\S]*?)\};/);
     if (!m) throw new Error("VIMAGES literal not found in prototype");
     const body = m[1]!;

     // Parse each "v01": "data:image/jpeg;base64,..." entry
     const entryRe = /(["']?)(v\d{2})\1\s*:\s*"data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)"/g;
     await mkdir(TARGET_DIR, { recursive: true });
     let count = 0;
     for (const match of body.matchAll(entryRe)) {
       const [, , slug, fmt, base64] = match;
       const ext = fmt === "jpeg" ? "jpg" : fmt;
       const filepath = resolve(TARGET_DIR, `${slug}.${ext}`);
       await writeFile(filepath, Buffer.from(base64!, "base64"));
       count++;
     }
     console.log(`extracted ${count} cover images to ${TARGET_DIR}`);
   }

   main().catch((e) => { console.error(e); process.exit(1); });
   ```

2. 加 npm script `db:extract-covers` 到 `packages/db/package.json`:
   ```json
   "db:extract-covers": "tsx scripts/extract-prototype-covers.ts"
   ```

3. 跑一次:`pnpm --filter @ghome/db db:extract-covers` —— 预期输出 `extracted 20 cover images to ...`

4. 验证文件:`ls apps/web/public/uploads/videos/ | wc -l` 应 ≥ 20

5. 修改 `seed/data/videos.ts`:每条 video 加 `coverImageUrl: "/uploads/videos/${slug}.jpg"`(注意 ext 与脚本输出一致,需要看 base64 实际格式 — 通常 jpeg 即 .jpg)

6. 修改 `prisma/seed.ts`:在 video upsert 的 update + create 块都加 `coverImageUrl: v.coverImageUrl`

7. 跑 seed:`pnpm --filter @ghome/db db:seed`,验证:
   ```bash
   docker exec ghome-postgres psql -U ghome -d ghome -c "SELECT slug, cover_image_url FROM videos LIMIT 5;"
   ```
   每条应有 `/uploads/videos/{slug}.jpg`

8. typecheck + 启动 web,curl `/video/v01` 确认 `<img src="/uploads/videos/v01.jpg">` 渲染

9. commit:
   ```bash
   git add packages/db/scripts/extract-prototype-covers.ts \
           packages/db/seed/data/videos.ts \
           packages/db/prisma/seed.ts \
           packages/db/package.json
   # 不 add public/uploads/videos/ 内容(gitignored),只 add .gitkeep 已存在
   git commit -m "feat(db): extract 20 prototype video covers + seed coverImageUrl"
   ```

### Tricky Bits (T1)

1. **正则解析 base64 块**:VIMAGES 对象可能跨多行,base64 本身可能含 `+` `/` `=`,正则要小心。如果原型源用单引号 vs 双引号 vs 模板字符串,要 robust 处理
2. **文件扩展名**:base64 前缀 `data:image/jpeg` → `.jpg`(注意:不是 jpeg)。脚本里做 `fmt === "jpeg" ? "jpg" : fmt` 转换
3. **路径**:脚本从 `packages/db/scripts/` 跑,要解析到 monorepo 根再回 `apps/web/public/uploads/videos/`。用 `resolve(process.cwd(), "..", "..", ...)` (cwd = packages/db)
4. **`.gitignore` 已忽略 `apps/web/public/uploads/`**(P10a T4 加的),所以提交不会带二进制图片。**重新跑一次 seed 时**(开发新机器 / CI)需要先跑 `db:extract-covers`
5. **Prototype HTML 必须 commit 在 repo**(已 commit `docs/ghome-20260509.html`)— 否则脚本找不到源
6. **大约 1.27MB 总图片**:解码后落地的 20 张 jpg 累计大小,本地磁盘 OK
7. **如果 VIMAGES 实际不存在或格式变了**:脚本 throw,不影响其它代码

---

## Task 2 — 逐页视觉 diff 审计 + 批改

**Files:** 散落,具体由 diff 决定。预期:`apps/web/app/globals.css`、各 page.tsx、各 component.tsx 微调。

### Steps

1. **打开两个浏览器窗口并排**:
   - 原型:`file:///Users/jeff/Work/workspace/uk/ghome/docs/ghome-20260509.html`(直接打开,SPA)
   - 实现:`http://localhost:3001/...`

2. **逐页对比 13 个核心路由**:`/`, `/apps`, `/app/broconnect`, `/videos`, `/video/v01`, `/categories`, `/category/fitness`, `/topics`, `/topic/<slug>`, `/guides`, `/guide/choose-app`, `/about`, `/contact`, `/terms`, `/search?q=健身`

3. **每页对比维度**:
   - 主要 section 块的 padding / margin
   - 字号 / 行距
   - 卡片之间的 gap
   - hover / focus 视觉
   - 移动断点(模拟 iPhone / Android UA)

4. **生成 diff 清单**(markdown 表格):
   ```
   | 页 | 差异 | 修复 |
   |---|---|---|
   | / | brand-hero h1 行距偏紧 | line-height: 1.15 → 1.1 |
   | /apps | hero-stat .v 字重比原型轻 | font-weight: 700 → 800 |
   | ... |
   ```

5. **批改 CSS / markup**(优先 CSS — 改一行影响多处)。每处改完跑 `pnpm --filter @ghome/web build` 跟一次 typecheck

6. **每完成 3-5 处差异 commit 一次**,message 形如:
   - `fix(web): home brand-hero h1 line-height + lead font-size to match prototype`
   - `fix(web): apps page hero-stats label opacity`

### Tricky Bits (T2)

1. **不要主观改进**:目标是与原型对齐,**不是**"做得比原型更好"。如果原型字号偏小,我们也用偏小的
2. **响应式测试**:iPhone 视口、平板视口、桌面 1280px / 1920px 各看一遍
3. **跨浏览器**:Chrome 是基线;Safari 字体 metrics 有差但不必匹配 Chrome 100%
4. **图片对比**:T1 已经把视频封面改成真图,T2 只看布局,不再担心封面差
5. **subjective 项目**:5% 中可能有"颜色看起来稍微不同"这种感觉,实际是 sub-pixel rendering 差异 — 不动它
6. **如果某项需要重大改动**(如重写一个组件):升级到独立 task,不混在 T2 里

---

## Task 3 — 交互 / 动画补遗 + 冒烟 + tag

**Files:** 视审计结果而定。

### Steps

1. **审计原型 JS 行为**(读原型 line 1900+ render 函数,主要交互):
   - `.app-card` hover 效果(原型 line ~165-170 可能有 transform)
   - `.v-card:hover .v-cover img { transform: scale(1.05) }` 已有
   - `.suggest-dd` 入场动画(transform / opacity)
   - mobile drawer cubic-bezier 动画曲线
   - `.apk-pop` hover focus-within 出现的过渡时长

2. **逐项 grep 原型 CSS** + 当前 globals.css 比较:
   ```bash
   grep -E "transition:|@keyframes" docs/ghome-20260509.html > /tmp/proto-anim.txt
   grep -E "transition:|@keyframes" apps/web/app/globals.css > /tmp/web-anim.txt
   diff /tmp/proto-anim.txt /tmp/web-anim.txt | head -30
   ```

3. **补漏**:每条缺的 transition 加到 globals.css。**不引入** `@keyframes` 除非原型有(原型实际没有 keyframes)

4. **冒烟最终 CI 矩阵**:
   ```bash
   pnpm --filter @ghome/db typecheck
   pnpm --filter @ghome/db test
   pnpm --filter @ghome/admin typecheck
   pnpm --filter @ghome/admin lint
   pnpm --filter @ghome/admin build
   pnpm --filter @ghome/web typecheck
   pnpm --filter @ghome/web lint
   pnpm --filter @ghome/web build
   pnpm --filter @ghome/web e2e   # 25 用例 (24 通过 + 1 文档化跳过)
   ```

5. **打 tag**:
   ```bash
   git tag p9.6-prototype-parity
   ```

### Tricky Bits (T3)

1. **Spec Mode 永远不做**:原型 line 610+ 任何 `body.spec-mode` / `.spec-*` 规则都跳
2. **transition 优先于 @keyframes**:原型主要用 transition,不要引入复杂动画
3. **tag 名:`p9.6-prototype-parity`**,与 P9.5 风格一致
4. **如果 git tag 阻塞**:DONE_WITH_CONCERNS

---

## Final 验收清单(P9.6 整体)

- [ ] `apps/web/public/uploads/videos/v01.jpg ... v20.jpg` 存在,各 ≤ 100KB
- [ ] DB videos 表 `cover_image_url` 全部填充,指向 `/uploads/videos/{slug}.jpg`
- [ ] `/videos` 首页 + `/video/v01` 显示真图(curl 看 `<img src="/uploads/videos/v01.jpg">`)
- [ ] 13 个核心路由逐页对比原型,主观判定 95%+ 接近
- [ ] 缺失的 CSS transition 全部补上
- [ ] CI 全绿(typecheck / lint / build / unit / e2e 24+1)
- [ ] tag `p9.6-prototype-parity` 在 main HEAD

**P9.6 完成 ⇒ 视觉/交互/真图 100%(扣除 Spec Mode 与等 R2 的视频文件托管)。**

后续可继续 P10b(R2/邮件/部署等真实凭证),或直接走上线流程。
