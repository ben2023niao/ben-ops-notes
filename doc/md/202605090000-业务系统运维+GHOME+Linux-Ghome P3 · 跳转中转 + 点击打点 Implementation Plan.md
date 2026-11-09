---
id: "doc-e18f4db5edd2"
title: "Ghome P3 · 跳转中转 + 点击打点 Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Linux", "Shell", "Docker", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p3-redirect-tracking.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p3-redirect-tracking.md"
sourceSha256: "b74312043205ffabbdb48574fcbc25089559ef1eb5e1610626ce0ea6b9b12dc5"
sourceSystem: "project-doc"
---

# Ghome P3 · 跳转中转 + 点击打点 Implementation Plan

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202605090000-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BLinux-Ghome%20P3%20%C2%B7%20%E8%B7%B3%E8%BD%AC%E4%B8%AD%E8%BD%AC%20%2B%20%E7%82%B9%E5%87%BB%E6%89%93%E7%82%B9%20Implementation%20Plan.md)

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 `/r/:id` 跳转中转 route handler(`runtime='nodejs'`,**同步**写 `click_events` 后再 302),把 P2 详情页里 `<a href={redirect.targetUrl}>` 的直跳改为 `<a href={`/r/${redirect.id}`}>`,引入 `ua-parser-js` 解析 UA,实现 `ip_hash = sha256(ip + HMAC(IP_HASH_SECRET, YYYY-MM-DD UTC))` 按日轮换的假名化。`/r/:id` 路由必须**仅**做静态字面值兜底校验(不查 DNS)。`pnpm db:enable-redirect` CLI 在 P1 已落,P3 用它端到端验证。

**Architecture:**
- **路由位置**:`apps/web/app/r/[id]/route.ts`(注意:**不是** `app/api/r/[id]`,见 spec §4.2)
- **Runtime**:文件顶部 `export const runtime = 'nodejs'` + `export const dynamic = 'force-dynamic'`
- **数据流**:`GET /r/:id` → `prisma.redirect.findUnique` → `validateForRedirect`(同步,bouncer)→ **同步** `prisma.clickEvent.create` → `302` 到 `redirect.targetUrl`。任何中间失败都 302 到 `/404`,失败也不写 click_event
- **隐私**:click_events 字段全部最小化(spec §3.2):`ua_family/ua_os` 解析后丢原文,`referrer_origin` 只存 origin,`ip_hash` 用 HMAC daily salt,所有 NOT NULL 字段失败回落 `'unknown'`
- **未实施 IP_HASH_SECRET 时**:模块加载阶段直接 throw(fail-fast)— 这是部署必填项,dev 与 CI 都必须设置

**Tech Stack:**
- Next.js 15 App Router(已 P0)
- Prisma `@ghome/db`(已 P1,需补 url-policy 导出)
- **新增**:`ua-parser-js ^1.0.39`(v1 同步 API,够用;v2 是 promise 化的,不必)
- 加密原语:Node 内置 `crypto`(`createHmac` / `createHash`)— 不引第三方
- Vitest(已 P1)

**Spec 引用:** [`docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md`](../specs/2026-05-08-ghome-product-shape-design.md) §3.2(redirects/click_events 字段)、§4.2(/r/:id 流程)、§5 P3。

**前置假设:** P2 已完成,`p2-frontend-readonly` 标签存在;DB 里有 9 apps + 20 videos 配套 redirects,**全部 disabled=true**(seed 默认);App / Video 详情页 CTA 当前直跳 `redirect.targetUrl`(P2 实现)。

---

## File Structure(P3 末态)

```
apps/web/
├─ app/
│  └─ r/
│      └─ [id]/
│          └─ route.ts                   # ★ 跳转中转 handler(T3)
├─ lib/
│  ├─ click-tracking.ts                  # ipHash / parseUa / refererOrigin / getIp / getCountry(T2)
│  ├─ db.ts                              # 已存在(T2 不动)
│  ├─ icons.tsx
│  ├─ gradients.ts
│  └─ format.ts
├─ tests/                                # 新建目录(本期 vitest 进 apps/web)
│  └─ click-tracking.test.ts             # ipHash 决定性 / 日切换 / parseUa / refererOrigin(T2 TDD)
├─ vitest.config.ts                      # 新建(T1)
├─ .env                                  # 加 IP_HASH_SECRET(T1)
├─ .env.example                          # 新建(T1)
├─ package.json                          # 加 ua-parser-js + vitest(T1)
└─ tsconfig.json                         # 已 OK

packages/db/
└─ src/
   └─ index.ts                           # T1 加 url-policy 导出

apps/web/app/app/[slug]/page.tsx         # T4:CTA 切到 /r/:id
apps/web/app/video/[slug]/page.tsx       # T4:CTA 切到 /r/:id

.github/workflows/ci.yml                 # T1 加 IP_HASH_SECRET 到 job env
```

---

## Conventions(整个 P3 共享)

- 所有 sync helper 都不能 throw(除模块顶层 IP_HASH_SECRET 缺失断言);失败回落 `'unknown'`
- click_events INSERT 在 redirect 302 之前完成(同步)。超时阈值预留 30ms — 单条 INSERT 在本地 Postgres 一般 < 5ms,极端情况(慢盘)50ms,P3 不引异步队列(spec §4.2)
- HTTP redirect 用 302(临时),不是 301(永久)— 让运营改 target 后立即生效,无 CDN 缓存包袱
- `IP_HASH_SECRET` 至少 32 字节,**绝不入库**;dev 用一个固定字符串,prod 是真随机 secret
- 提交风格:Conventional Commits;每 task 末尾 commit
- 不引 i18n、不动 admin、不接搜索

---

## Task 1 — Setup:`ua-parser-js` 依赖、`IP_HASH_SECRET` env、`@ghome/db` 导出 url-policy、CI

**Files:**
- Modify: `apps/web/package.json`(加 ua-parser-js + vitest + @types/ua-parser-js;若 vitest 已在 root devDeps,只加到 apps/web)
- Create: `apps/web/.env.example`(documenting required env)
- Modify: `apps/web/.env`(加 IP_HASH_SECRET)
- Create: `apps/web/vitest.config.ts`
- Modify: `packages/db/src/index.ts`(re-export url-policy)
- Modify: `.github/workflows/ci.yml`(加 IP_HASH_SECRET 到 ci job env)

- [ ] **Step 1: 修改 `apps/web/package.json`**

在 `dependencies` 加 `ua-parser-js`;在 `devDependencies` 加 `@types/ua-parser-js` 和 `vitest`(若不存在):

```json
"dependencies": {
  "@ghome/db": "workspace:*",
  "@prisma/client": "^5.22.0",
  "next": "^15.0.0",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "react-markdown": "^9.0.0",
  "remark-gfm": "^4.0.0",
  "ua-parser-js": "^1.0.39"
},
"devDependencies": {
  "@types/node": "^20.14.0",
  "@types/react": "^19.0.0",
  "@types/react-dom": "^19.0.0",
  "@types/ua-parser-js": "^0.7.39",
  "eslint": "^9.0.0",
  "eslint-config-next": "^15.0.0",
  "rimraf": "^6.0.1",
  "typescript": "^5.5.0",
  "vitest": "^2.1.0"
}
```

并把 `scripts` 里 `test` 与 `test:watch` 加上(若没有):

```json
"scripts": {
  "dev": "next dev --port 3000",
  "build": "next build",
  "start": "next start --port 3000",
  "lint": "next lint --dir app",
  "typecheck": "tsc --noEmit",
  "clean": "rimraf .next out",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] **Step 2: 创建 `apps/web/vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    globals: false,
    testTimeout: 10000,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
```

- [ ] **Step 3: 创建 `apps/web/.env.example`(documentation,可入库)**

```bash
# Postgres 连接(本地 docker-compose)
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome

# 必填:用于 click_events.ip_hash 的 HMAC 密钥。每天按 UTC 日期作为 message,
# 计算 daily salt,然后 sha256(ip + salt) 得到 ip_hash。
# - dev:可以用任意 ≥ 32 字节字符串
# - prod:用 `openssl rand -hex 32` 生成,**绝不入库**
# 缺失时模块加载阶段会 throw(fail-fast)
[敏感内容已脱敏]
```

- [ ] **Step 4: 修改 `apps/web/.env`(本地 dev 用,**不入库**)**

```bash
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome
[敏感内容已脱敏]
```

> 注:`apps/web/.env` 已经在 P2 T1 创建,这里只是追加 `IP_HASH_SECRET`。

- [ ] **Step 5: 修改 `packages/db/src/index.ts`** — re-export url-policy:

在文件末尾追加:

```ts
export { validateForRedirect, validateForWrite } from "./lib/url-policy";
export type { ValidationResult } from "./lib/url-policy";
```

- [ ] **Step 6: 修改 `.github/workflows/ci.yml`** — 在 `jobs.ci.env` 区域加上 `IP_HASH_SECRET`

```yaml
    env:
      DATABASE_URL: postgres://ghome:ghome@localhost:5432/ghome
      [敏感内容已脱敏]
```

> 注:CI 用一个稳定但仅限 CI 的 secret。**绝不**与 prod 共用。

- [ ] **Step 7: 安装依赖 + typecheck**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm install
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/db typecheck
```

Expected: 拉下 `ua-parser-js` + `@types/ua-parser-js` + `vitest`(若 root 已有则复用)。typecheck 通过(@ghome/db 的 url-policy 现在 export 了)。

- [ ] **Step 8: 提交**

```bash
git add apps/web/package.json apps/web/.env.example apps/web/vitest.config.ts \
        packages/db/src/index.ts .github/workflows/ci.yml pnpm-lock.yaml
git commit -m "feat(web): add ua-parser-js, IP_HASH_SECRET env, url-policy export, vitest config"
```

> `apps/web/.env` **不**入库(已 gitignored)。

---

## Task 2 — `lib/click-tracking.ts` 工具集(TDD:先测后实现)

**Files:**
- Create: `apps/web/tests/click-tracking.test.ts`
- Create: `apps/web/lib/click-tracking.ts`

> **TDD discipline**:Step 1 写完整测试,Step 2 跑测试确认全 fail,Step 3 实现,Step 4 跑测试期待全 pass。

- [ ] **Step 1: 写失败测试 `apps/web/tests/click-tracking.test.ts`**

```ts
import { describe, it, expect, beforeAll } from "vitest";
import {
  ipHash,
  parseUa,
  refererOrigin,
  getIp,
  getCountry,
  dailySaltUtc,
} from "../lib/click-tracking";

const 敏感凭据：[已脱敏]

describe("dailySaltUtc", () => {
  it("returns YYYY-MM-DD format from UTC", () => {
    expect(dailySaltUtc(new Date("2026-05-09T00:00:00Z"))).toBe("2026-05-09");
    expect(dailySaltUtc(new Date("2026-05-09T23:59:59Z"))).toBe("2026-05-09");
    // UTC 跨日(2026-05-10 00:30 UTC)
    expect(dailySaltUtc(new Date("2026-05-10T00:30:00Z"))).toBe("2026-05-10");
    // 本地北京时间 2026-05-10 08:00 = UTC 2026-05-10 00:00
    expect(dailySaltUtc(new Date("2026-05-10T00:00:00Z"))).toBe("2026-05-10");
  });
});

describe("ipHash", () => {
  it("is deterministic for same (ip, secret, date)", () => {
    const date = new Date("2026-05-09T12:00:00Z");
    const a = ipHash("203.0.113.1", SECRET, date);
    const b = ipHash("203.0.113.1", SECRET, date);
    expect(a).toBe(b);
    expect(a).toMatch(/^[a-f0-9]{64}$/); // sha256 hex
  });

  it("is different for different IPs", () => {
    const date = new Date("2026-05-09T12:00:00Z");
    const a = ipHash("203.0.113.1", SECRET, date);
    const b = ipHash("203.0.113.2", SECRET, date);
    expect(a).not.toBe(b);
  });

  it("rotates daily — same IP across UTC days yields different hashes", () => {
    const day1 = new Date("2026-05-09T12:00:00Z");
    const day2 = new Date("2026-05-10T12:00:00Z");
    const a = ipHash("203.0.113.1", SECRET, day1);
    const b = ipHash("203.0.113.1", SECRET, day2);
    expect(a).not.toBe(b);
  });

  it("differs across secrets", () => {
    const date = new Date("2026-05-09T12:00:00Z");
    const a = ipHash("203.0.113.1", "secret-A-32-bytes-aaaaaaaaaaaaaa", date);
    const b = ipHash("203.0.113.1", "secret-B-32-bytes-bbbbbbbbbbbbbb", date);
    expect(a).not.toBe(b);
  });

  it("handles 'unknown' IP fallback", () => {
    const date = new Date("2026-05-09T12:00:00Z");
    const a = ipHash("unknown", SECRET, date);
    expect(a).toMatch(/^[a-f0-9]{64}$/);
  });
});

describe("parseUa", () => {
  it("parses Chrome on macOS", () => {
    const r = parseUa(
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    );
    expect(r.family).toBe("Chrome");
    expect(r.os).toBe("macOS");
  });

  it("parses Safari on iOS", () => {
    const r = parseUa(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    );
    expect(r.family).toBe("Mobile Safari");
    expect(r.os).toBe("iOS");
  });

  it("parses Firefox on Linux", () => {
    const r = parseUa(
      "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    );
    expect(r.family).toBe("Firefox");
    expect(r.os).toBe("Linux");
  });

  it("returns 'unknown' for null/empty/garbage", () => {
    expect(parseUa(null)).toEqual({ family: "unknown", os: "unknown" });
    expect(parseUa("")).toEqual({ family: "unknown", os: "unknown" });
    // 完全无意义的字符串解析失败时返回 unknown
    const r = parseUa("blahblahblah");
    expect(r.family).toBe("unknown");
    expect(r.os).toBe("unknown");
  });

  it("never throws on bizarre inputs", () => {
    expect(() => parseUa("\x00\x01\x02")).not.toThrow();
    expect(() => parseUa("a".repeat(10000))).not.toThrow();
  });
});

describe("refererOrigin", () => {
  it("extracts origin from full URL", () => {
    expect(refererOrigin("https://example.com/path?q=1")).toBe("https://example.com");
    expect(refererOrigin("http://example.com:8080/x")).toBe("http://example.com:8080");
  });

  it("returns 'unknown' for null/empty/invalid", () => {
    expect(refererOrigin(null)).toBe("unknown");
    expect(refererOrigin("")).toBe("unknown");
    expect(refererOrigin("not a url")).toBe("unknown");
  });

  it("never throws on bizarre inputs", () => {
    expect(() => refererOrigin("\x00")).not.toThrow();
    expect(() => refererOrigin("javascript:alert(1)")).not.toThrow();
  });
});

describe("getIp", () => {
  it("uses x-forwarded-for first hop when present", () => {
    const headers = new Headers();
    headers.set("x-forwarded-for", "203.0.113.1, 203.0.113.1");
    expect(getIp(headers)).toBe("203.0.113.1");
  });

  it("falls back to x-real-ip", () => {
    const headers = new Headers();
    headers.set("x-real-ip", "203.0.113.5");
    expect(getIp(headers)).toBe("203.0.113.5");
  });

  it("returns 'unknown' if neither header present", () => {
    const headers = new Headers();
    expect(getIp(headers)).toBe("unknown");
  });
});

describe("getCountry", () => {
  it("uses cf-ipcountry when present", () => {
    const headers = new Headers();
    headers.set("cf-ipcountry", "CN");
    expect(getCountry(headers)).toBe("CN");
  });

  it("falls back to x-vercel-ip-country", () => {
    const headers = new Headers();
    headers.set("x-vercel-ip-country", "US");
    expect(getCountry(headers)).toBe("US");
  });

  it("returns 'unknown' if neither header present", () => {
    expect(getCountry(new Headers())).toBe("unknown");
  });
});

describe("module-load IP_HASH_SECRET assertion", () => {
  // 这个测试确认 ipHash 接收 secret 作为参数(显式),不直接读 process.env。
  // 模块加载本身不能依赖 process.env,因为 Vitest 测试模块 import 时间可能早于 env 注入。
  it("ipHash accepts an explicit secret param (not implicit env)", () => {
    expect(typeof ipHash).toBe("function");
    expect(ipHash.length).toBeGreaterThanOrEqual(2); // (ip, secret, ...)
  });
});
```

- [ ] **Step 2: 跑测试,确认全 fail**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/web test
```

Expected: 大量 fail / `Error: Failed to load url ../lib/click-tracking ...`(模块未实现)。

- [ ] **Step 3: 写实现 `apps/web/lib/click-tracking.ts`**

```ts
import { createHmac, createHash } from "node:crypto";
import { UAParser } from "ua-parser-js";

/**
 * UTC YYYY-MM-DD,作为 daily salt 的 message。
 */
export function dailySaltUtc(date: Date = new Date()): string {
  const yyyy = date.getUTCFullYear();
  const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(date.getUTCDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

/**
 * 当日 salt = HMAC-SHA256(secret, "YYYY-MM-DD")(hex)
 */
function dailySalt(敏感凭据：[已脱敏] date: Date): string {
  return createHmac("sha256", secret).update(dailySaltUtc(date)).digest("hex");
}

/**
 * ip_hash = sha256(ip + dailySalt)。
 * 同一访客跨 UTC 日 hash 不同,弱化追踪。
 *
 * 注意:secret 是显式参数(便于 mock 与 test);**调用方** 负责从 env 取
 * IP_HASH_SECRET 并断言非空。本模块不读 process.env。
 */
export function ipHash(ip: string, 敏感凭据：[已脱敏] date: Date = new Date()): string {
  const salt = dailySalt(secret, date);
  return createHash("sha256").update(`${ip}${salt}`).digest("hex");
}

/**
 * 解析 user-agent 字符串为 { family, os }。
 * 失败 / null / 解析无 name → 'unknown'。永不 throw。
 */
export function parseUa(uaString: string | null | undefined): { family: string; os: string } {
  if (!uaString) return { family: "unknown", os: "unknown" };
  try {
    const parser = new UAParser(uaString);
    const browser = parser.getBrowser();
    const os = parser.getOS();
    return {
      family: browser.name || "unknown",
      os: os.name || "unknown",
    };
  } catch {
    return { family: "unknown", os: "unknown" };
  }
}

/**
 * Referer 全 URL → 仅 origin(scheme + host[:port])。
 * 失败 / null / 无效 URL → 'unknown'。永不 throw。
 */
export function refererOrigin(referer: string | null | undefined): string {
  if (!referer) return "unknown";
  try {
    return new URL(referer).origin;
  } catch {
    return "unknown";
  }
}

/**
 * 从 request headers 取访客 IP。优先 x-forwarded-for 首跳,然后 x-real-ip,
 * 都没有则 'unknown'。
 */
export function getIp(headers: Headers): string {
  const forwarded = headers.get("x-forwarded-for");
  if (forwarded) {
    const first = forwarded.split(",")[0]?.trim();
    if (first) return first;
  }
  const realIp = headers.get("x-real-ip");
  if (realIp) return realIp;
  return "unknown";
}

/**
 * 从 request headers 取国家代码(ISO 2 letter)。优先 cf-ipcountry,然后
 * x-vercel-ip-country,都没有则 'unknown'。
 */
export function getCountry(headers: Headers): string {
  const cf = headers.get("cf-ipcountry");
  if (cf) return cf;
  const vercel = headers.get("x-vercel-ip-country");
  if (vercel) return vercel;
  return "unknown";
}
```

- [ ] **Step 4: 跑测试,期待全过**

```bash
pnpm --filter @ghome/web test
```

Expected: 所有用例 pass(共 ~22 用例)。

- [ ] **Step 5: 提交**

```bash
git add apps/web/lib/click-tracking.ts apps/web/tests/click-tracking.test.ts
git commit -m "feat(web): add click-tracking helpers (ipHash with daily salt, parseUa, refererOrigin) — TDD"
```

---

## Task 3 — `/r/[id]/route.ts` 跳转中转 handler

**Files:**
- Create: `apps/web/app/r/[id]/route.ts`

> **关键路径**:**`apps/web/app/r/[id]/route.ts`**(根目录直挂,不在 `/api/` 下)。这样公开 URL 是 `/r/:id`,与 spec §4.2 一致。

- [ ] **Step 1: 写 `apps/web/app/r/[id]/route.ts`**

```ts
import { NextResponse, type NextRequest } from "next/server";
import { prisma, validateForRedirect } from "@ghome/db";
import {
  ipHash,
  parseUa,
  refererOrigin,
  getIp,
  getCountry,
} from "@/lib/click-tracking";

/* 必须强制 nodejs runtime — Prisma + 加密原语都不能跑 edge */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * 模块加载时断言 IP_HASH_SECRET。fail-fast 比运行时退化更安全。
 * dev 与 CI 都必须在 env 里设。
 */
const [敏感内容已脱敏];
if (!IP_HASH_SECRET) {
  throw new Error(
    "[r/:id] IP_HASH_SECRET is not set. Required for click_events.ip_hash. " +
      "Set in apps/web/.env (dev) or job env (CI). See apps/web/.env.example.",
  );
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const notFoundUrl = new URL("/404", req.url);

  // 1. 查 redirect
  const redirect = await prisma.redirect.findUnique({ where: { id } });
  if (!redirect || redirect.disabled) {
    return NextResponse.redirect(notFoundUrl, 302);
  }

  // 2. Bouncer:同步、无 IO 校验(协议 / 语法 / 字面值黑名单)
  //    防御 admin 后台直改 DB / 历史脏数据。详见 spec §4.2 + §3.2.
  const policy = validateForRedirect(redirect.targetUrl);
  if (!policy.ok) {
    // 安全失败:不打点(避免授权安全测试者用未识别 URL 污染 click_events)
    return NextResponse.redirect(notFoundUrl, 302);
  }

  // 3. 同步写 click_events,失败也不阻断 302(降级:redirect 仍发生)
  try {
    const ip = getIp(req.headers);
    const ua = req.headers.get("user-agent");
    const ref = req.headers.get("referer");
    const { family, os } = parseUa(ua);

    await prisma.clickEvent.create({
      data: {
        redirectId: redirect.id,
        ts: new Date(),
        uaFamily: family,
        uaOs: os,
        country: getCountry(req.headers),
        referrerOrigin: refererOrigin(ref),
        ipHash: ipHash(ip, IP_HASH_SECRET),
      },
    });
  } catch (err) {
    // 不暴露错误细节给访客;日志保留让运营在 admin 看到
    console.error("[r/:id] click_event insert failed:", err);
  }

  // 4. 302 到 target
  return NextResponse.redirect(redirect.targetUrl, 302);
}
```

> **设计说明**:
> 1. **`runtime='nodejs'`** 与 `dynamic='force-dynamic'` 必须显式声明。Prisma 与 `node:crypto` 都不能跑 Edge runtime。`force-dynamic` 防 Next.js 把这条路由当 SSG 缓存。
> 2. **同步 INSERT**(不 fire-and-forget):本地 Postgres < 5ms,可接受;Edge 部署 + 远端 DB 时如果延迟成为瓶颈,P 后期再引入异步队列(spec §4.2)。
> 3. **3 步失败回落都 302 到 /404**:redirect 不存在 / disabled / url-policy 拒绝 → 都 302 /404。这样授权安全测试者无法通过响应差异探测 redirect 是否存在(timing-safe 不严格,但接口语义一致)。
> 4. **click_events 插入失败不阻 302**:跳转是核心功能,打点是次要;如果 DB 短暂不可用,redirect 仍要发生。日志留给运营。
> 5. **不读 cookies / sessions**:P3 不接 auth(spec §4.2)。

- [ ] **Step 2: 验证 build + 单元测试** —— route handler 本身不引入新单元测试(集成测试在 T5 通过 enable-redirect + curl 端到端验)

```bash
cd /Users/jeff/Work/workspace/uk/ghome
pnpm --filter @ghome/web build
```

Expected: build 通过,新路由 `/r/[id]` 出现在 build 输出中(`λ` 标记 = node runtime,而非 `○` 静态)。

- [ ] **Step 3: 提交**

```bash
git add apps/web/app/r/
git commit -m "feat(web): add /r/:id redirect handler with sync click_events tracking (nodejs runtime)"
```

---

## Task 4 — 详情页 CTA 切到 `/r/:id`(App detail + Video detail)

**Files:**
- Modify: `apps/web/app/app/[slug]/page.tsx`(DownloadButton href)
- Modify: `apps/web/app/video/[slug]/page.tsx`(WatchButton href)

> 切换 logic 简单:`<a href={app.redirect.targetUrl}>` → `<a href={`/r/${app.redirect.id}`}>`。disabled 行为不变。其余 UI 不动。

- [ ] **Step 1: 修改 `apps/web/app/app/[slug]/page.tsx` 中的 DownloadButton**

定位 `DownloadButton`(在 page.tsx 文件底部),修改 enabled 分支的 href:

```tsx
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
```

调用处把 prop 从 `targetUrl` 改为 `/r/:id`:

```tsx
<DownloadButton
  disabled={app.redirect.disabled}
  href={app.redirect.disabled ? undefined : `/r/${app.redirect.id}`}
/>
```

> 注意是 `app.redirect.id`,不是 `app.redirectId`(后者也可,但前者更明确)。两者值相同。

- [ ] **Step 2: 修改 `apps/web/app/video/[slug]/page.tsx` 中的 WatchButton**

同样模式。`WatchButton` 已存在(P2 T8),把 href 切为 `/r/${video.redirect.id}`。

- [ ] **Step 3: 验证 build**

```bash
pnpm --filter @ghome/web build
```

Expected: build 通过。

- [ ] **Step 4: 验证渲染(disabled 状态 — seed 默认全 disabled)**

```bash
docker compose up -d
sleep 3
pnpm --filter @ghome/web dev &
sleep 8

# 详情页应该显示"暂未开放"(因为 seed redirect 全 disabled=true)
curl -fsS http://localhost:3000/app/broconnect | grep -q "暂未开放" && echo "app disabled OK"
curl -fsS http://localhost:3000/video/v01 | grep -q "暂未开放" && echo "video disabled OK"

# 而 dev 渲染产物中**不应**出现 example.com seed URL(seed 占位 URL)
! curl -fsS http://localhost:3000/app/broconnect | grep -q "example.com/seed" && echo "no seed url leak OK"

kill %1 2>/dev/null || true
```

Expected: 3 个 grep 全过。

- [ ] **Step 5: 提交**

```bash
git add apps/web/app/app/[slug]/page.tsx apps/web/app/video/[slug]/page.tsx
git commit -m "feat(web): app/video detail CTAs use /r/:id redirect route"
```

---

## Task 5 — 端到端集成冒烟 + tag p3-redirect-tracking

无新文件。本 task 跑端到端冒烟,验证从 admin/CLI 启用 redirect → web 详情页渲染 `/r/:id` href → 用户点击 → `click_events` 表多一行 → 302 到真实 URL。

- [ ] **Step 1: 干净环境 reset**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
docker compose up -d
sleep 5
pnpm --filter @ghome/db db:reset --force   # drop + re-migrate + re-seed
```

Expected: seed 完成,29 个 redirect 全 disabled=true,click_events 表为空。

- [ ] **Step 2: 用 CLI 启用一条 broconnect 的 redirect**

```bash
RID=$(docker compose exec -T postgres psql -U ghome -d ghome -tAc \
  "SELECT id FROM redirects WHERE owner_kind='app' AND owner_id='broconnect' LIMIT 1")
echo "RID=$RID"

pnpm --filter @ghome/db db:enable-redirect "$RID" "https://www.example.com/broconnect-download"
# Expected: Enabled redirect ${RID}: https://www.example.com/broconnect-download
```

> 注:`https://www.example.com/...` 在 `validateForWrite` 的 DNS 校验下能通过(example.com 解析到公网 IP)。

- [ ] **Step 3: 起 dev,curl `/r/:id`**

```bash
pnpm --filter @ghome/web dev &
sleep 8

# 不跟随重定向,看 302 + Location
curl -sI "http://localhost:3000/r/$RID" | head -5
```

Expected:`HTTP/1.1 302 ...` + `Location: https://www.example.com/broconnect-download`。

- [ ] **Step 4: 验证 click_events 表多了一行**

```bash
docker compose exec postgres psql -U ghome -d ghome -c "
SELECT redirect_id, ts, ua_family, ua_os, country, referrer_origin, length(ip_hash) AS ip_hash_len
FROM click_events
WHERE redirect_id = '$RID'
ORDER BY ts DESC LIMIT 1;
"
```

Expected:
- 1 行
- `ua_family` 是 `curl` 或 `unknown`(curl 默认 UA 含 `curl/8.x`,被 ua-parser-js 识别为 `curl`)
- `ua_os` 是 `unknown`(curl 不暴露 OS)
- `country` 是 `unknown`(本地 dev 没代理头)
- `referrer_origin` 是 `unknown`
- `ip_hash_len` = 64(sha256 hex)

- [ ] **Step 5: 验证详情页 CTA 现在指向 `/r/:id`**

```bash
curl -fsS http://localhost:3000/app/broconnect > /tmp/broc.html

# 应该有 /r/$RID 形式的 href
grep -q "/r/$RID" /tmp/broc.html && echo "CTA href OK"

# 应该是"立即下载"(enabled),不是"暂未开放"
grep -q "立即下载" /tmp/broc.html && echo "enabled label OK"

# 不应该有 redirect.targetUrl 直接出现(P2 时旧的写法)
! grep -q "https://www.example.com/broconnect-download" /tmp/broc.html && echo "no targetUrl leak"
```

Expected: 3 个 grep 全过。

> 等等 — 注意到 ISR 缓存:`/app/broconnect` 是 `revalidate=300`,P2 build 时 redirect.disabled=true,渲染了"暂未开放"。运行时 admin/CLI 启用 redirect 后,detail 页**不会立即看到变化**,要等 ISR 过期或 admin 触发 revalidate。**P3 暂不接 revalidate webhook**(P5 才做),所以本 step 用 dev mode 跑(`pnpm dev` 不缓存),直接看到最新数据。生产 build mode 下需要等 5min。

- [ ] **Step 6: 验证 disabled redirect 仍然 302 到 /404**

```bash
DISABLED_RID=$(docker compose exec -T postgres psql -U ghome -d ghome -tAc \
  "SELECT id FROM redirects WHERE owner_kind='app' AND owner_id='matematch' LIMIT 1")
echo "DISABLED_RID=$DISABLED_RID"

curl -sI "http://localhost:3000/r/$DISABLED_RID" | head -3
```

Expected:`HTTP/1.1 302 ...` + `Location: http://localhost:3000/404`(因为 matematch 的 redirect 仍 disabled)。

- [ ] **Step 7: 验证 unknown id 也 302 到 /404**

```bash
curl -sI "http://localhost:3000/r/00000000-0000-0000-0000-000000000000" | head -3
```

Expected:`302` → `/404`。

- [ ] **Step 8: 验证 ip_hash 决定性 + 跨日轮换**

短时间内连续 2 次 curl 同一 redirect,新增 2 行 click_events,**ip_hash 应该相同**(同 IP + 同日 + 同 secret):

```bash
curl -sI "http://localhost:3000/r/$RID" > /dev/null
curl -sI "http://localhost:3000/r/$RID" > /dev/null

docker compose exec postgres psql -U ghome -d ghome -tAc "
SELECT count(DISTINCT ip_hash) FROM click_events WHERE redirect_id = '$RID';
"
```

Expected: 输出 `1`(同一 ip_hash 出现 N 次,distinct 计数为 1)。

跨日轮换的测试需要等到 UTC 跨日 — 不在端到端 test 内验,T2 单元测试已经覆盖。

- [ ] **Step 9: 关闭 dev + Postgres**

```bash
kill %1 2>/dev/null || true
docker compose down 2>/dev/null || true
```

- [ ] **Step 10: 4 步全套验证**

```bash
docker compose up -d
sleep 5
pnpm --filter @ghome/db db:migrate:deploy   # 应该 no-op,已是最新
pnpm --filter @ghome/db db:seed              # 重置回 seed 状态
pnpm typecheck
pnpm lint
pnpm --filter @ghome/db test                 # P1 的 38 测试
pnpm --filter @ghome/web test                # P3 新加的 click-tracking 测试
pnpm build
```

Expected: 全过。

- [ ] **Step 11: git 干净 + tag P3**

```bash
git status --short
# 期望:仅 untracked plan(P3 plan 文档),其它干净
git add docs/superpowers/plans/2026-05-09-ghome-p3-redirect-tracking.md
git commit -m "docs: commit P3 implementation plan"

git tag -a p3-redirect-tracking -m "P3 · redirect tracking: /r/:id route handler with sync click_events INSERT, ua-parser-js, daily-rotated ip_hash; detail CTAs migrated to /r/:id; 22 click-tracking unit tests + end-to-end smoke"

git tag -l
git log --oneline p2-frontend-readonly..HEAD
```

Expected: 3 个 tag 全在(`p0-scaffolding`、`p1-data-model`、`p2-frontend-readonly`、`p3-redirect-tracking`)。log 显示 P3 期间的 ~6 个 commit + tag。

---

## P3 完成判据(对应 spec §5)

- ✅ `/r/:id` route handler 在 `apps/web/app/r/[id]/route.ts`(spec §4.2 路径)— T3
- ✅ `runtime='nodejs'` + `dynamic='force-dynamic'` — T3
- ✅ 同步写 click_events 后再 302 — T3
- ✅ url-policy `validateForRedirect` 兜底校验(同步,无 DNS)— T3
- ✅ click_events 字段最小化:`ua_family/ua_os` 解析后丢原文,`referrer_origin` 仅 origin,country 从 cf/vercel 头取,fallback `'unknown'`— T2/T3
- ✅ `ip_hash = sha256(ip + HMAC(IP_HASH_SECRET, YYYY-MM-DD UTC))` 按日轮换 — T2
- ✅ App / Video 详情页 CTA 切到 `/r/:id` — T4
- ✅ 失败回落 302 → /404,不打点 — T3
- ✅ `IP_HASH_SECRET` 缺失时模块加载阶段 throw(fail-fast)— T3
- ✅ 端到端冒烟:CLI enable redirect → curl `/r/:id` → 302 + click_events 多 1 行 → ip_hash deterministic — T5
- ✅ CI 配置 IP_HASH_SECRET — T1

---

## 已知 P3 故意不做的事(P4+ 起补)

- **`waitUntil` / 异步队列**:同步 INSERT 在本地 / 中等流量都够;真到瓶颈再换(spec §4.2)
- **revalidate 触发器**:admin 改 redirect 后,web 详情页不会即时更新 disabled 状态(等 ISR 5min)。P5 加 admin webhook
- **rate limiting**:`/r/:id` 没接 rate limit。授权安全测试者可以批量请求伪造 click_events 行。P 后期接 Redis + middleware
- **bot 过滤**:User-Agent 是 bot/crawler 的请求也写 click_events。运营报表 P5 起再接入 ua-parser-js 的 `getDevice` 与启发式 bot 过滤
- **30 天聚合任务**:P1 已建 click_daily_stats 表,P7 才接定时聚合
- **i18n / language hint**:不接

---

## Self-Review

- **Spec 覆盖**:逐条核对 spec §4.2 + §3.2 click_events / §5 P3。所有完成判据有对应 task。
- **占位符扫描**:无 TBD/TODO。每 step 都有具体代码或命令。
- **TS 类型一致性**:`ipHash(ip, secret, date)` 三参签名一致;`parseUa` 返回 `{family, os}` shape 一致;`getIp/getCountry` 接收 `Headers` 不接收 `Request`(测试与实现一致)。
- **TDD 体现**:T2 严格 TDD(失败先 → 实现 → 通过)。route handler 本身的集成测试用 T5 端到端 curl 验,不写额外的 fake-Request 单元测试(过度工程)。
- **风险**:
  - `parseUa` 在某些异常 UA 上 ua-parser-js v1 可能 throw — 已用 try/catch 兜底
  - `ipHash` 用同步 createHmac,大量并发时 CPU 是瓶颈 — 单条事件 ~10μs,远低于 INSERT 时间
  - **`/r/:id` route handler 模块加载时 throw**:如果 IP_HASH_SECRET 缺失,**整个 web 服务都起不来**。这是有意的(部署必填),但 dev 忘记设置时会报错。`apps/web/.env.example` 与 .env 都已写明。

---

## 下一步

P3 完成后,**写 P4 plan**(运营端 admin 骨架 + GitHub OAuth + ADMIN_ALLOWED_GITHUB_LOGINS 白名单 + signIn callback 手动 upsert admin_users + Dashboard 显示统计)。
