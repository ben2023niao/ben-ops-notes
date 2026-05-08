---
id: "doc-6c1f9d5b279f"
title: "Ghome P0 · 脚手架 Implementation Plan"
date: "2026-05-09T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p0-scaffolding.md"
sourcePath: "~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p0-scaffolding.md"
sourceSha256: "c5ef9f361cf8331d8d3877b8edad33c4cb20acb6b7140455ed635d0d8f1e2ae8"
sourceSystem: "project-doc"
---

# Ghome P0 · 脚手架 Implementation Plan

> 来源文件：`~/Projects/work/game/ghome/docs/superpowers/plans/2026-05-09-ghome-p0-scaffolding.md`

> 整理日期：2026-05-09 00:00｜日期依据：文件名日期

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 立起 pnpm monorepo + 两个空白 Next.js app(web 3000、admin 3100)+ docker-compose Postgres + 极简 GitHub Actions CI(lint/typecheck/build,P0 不需要 Postgres service)。

**Architecture:** pnpm workspaces 单仓多包。`apps/web` 与 `apps/admin` 各为独立 Next.js 15(App Router)应用。`packages/db` 是 Prisma client 的占位包(P1 才填 schema)。Postgres 仅通过 docker-compose 起,P0 不连接。

**Tech Stack:**
- Node.js 20 LTS
- pnpm 9.x
- TypeScript 5.x
- Next.js 15.x(App Router)
- React 19.x
- Prisma 5.x(P0 仅安装客户端依赖)
- PostgreSQL 16(Docker)
- GitHub Actions

**Spec 引用:** [docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md](../specs/2026-05-08-ghome-product-shape-design.md) §1、§5 P0。

---

## File Structure(P0 落地的全部文件)

```
ghome/
├─ .github/workflows/ci.yml                 # GitHub Actions: lint + typecheck + build
├─ .gitignore
├─ .nvmrc                                   # 20
├─ .npmrc                                   # 启用 pnpm strict workspace
├─ docker-compose.yml                       # postgres:16 + adminer
├─ package.json                             # 根:devDeps + scripts
├─ pnpm-workspace.yaml                      # apps/* + packages/*
├─ tsconfig.base.json                       # 共享 TS 配置
├─ README.md
├─ apps/
│  ├─ web/
│  │  ├─ app/
│  │  │  ├─ layout.tsx                      # root layout(空)
│  │  │  ├─ page.tsx                        # 首页(P0 占位文案)
│  │  │  └─ globals.css
│  │  ├─ next.config.mjs
│  │  ├─ next-env.d.ts                      # 由 Next.js 生成,git ignore
│  │  ├─ package.json
│  │  ├─ postcss.config.mjs                 # P0 暂不上 Tailwind,留作后续 Hook
│  │  ├─ tsconfig.json
│  │  ├─ .env.example                       # DATABASE_URL 占位
│  │  └─ .eslintrc.cjs
│  └─ admin/
│     ├─ app/
│     │  ├─ layout.tsx
│     │  ├─ page.tsx                        # admin 占位文案
│     │  └─ globals.css
│     ├─ next.config.mjs                    # 内含 PORT=3100 启动配置
│     ├─ next-env.d.ts
│     ├─ package.json
│     ├─ postcss.config.mjs
│     ├─ tsconfig.json
│     ├─ .env.example
│     └─ .eslintrc.cjs
└─ packages/
   └─ db/
      ├─ src/
      │  └─ index.ts                        # PrismaClient 单例占位(P1 填 schema)
      ├─ package.json
      └─ tsconfig.json
```

**约定**:
- 所有命令默认在仓库根目录执行,除非显式 `cd`。
- 提交策略:每个 Task 末尾 `git commit`,Conventional Commits(`chore`/`feat`/`docs`/`ci` 等前缀)。
- 不删除原型 `docs/ghome.html`,保留作为 P1/P2 seed 来源。

---

## Task 1 — Git 仓库初始化与根级元文件

**Files:**
- Create: `.gitignore`
- Create: `.nvmrc`
- Create: `.npmrc`
- Create: `README.md`

- [ ] **Step 1: 在仓库根初始化 git 与 main 分支**

```bash
cd /Users/jeff/Work/workspace/uk/ghome
git init -b main
git status
```

Expected: `On branch main / nothing added to commit but untracked files present`(已存在 `CLAUDE.md` 和 `docs/`)。

- [ ] **Step 2: 写 `.gitignore`**

```gitignore
# Dependencies
node_modules
.pnpm-store

# Next.js
.next
out
*.tsbuildinfo
next-env.d.ts

# Env
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/*
!.vscode/extensions.json
.idea

# Test/coverage
coverage
.nyc_output

# Logs
*.log
npm-debug.log*
pnpm-debug.log*

# Docker volumes(本地数据)
.docker-data
```

- [ ] **Step 3: 写 `.nvmrc`**

```
20
```

- [ ] **Step 4: 写 `.npmrc`**

```ini
# 工作区严格依赖管理:子包不可隐式访问未声明依赖
strict-peer-dependencies=false
auto-install-peers=true
shamefully-hoist=false
# 防止 lockfile 跨平台漂移
prefer-frozen-lockfile=true
```

- [ ] **Step 5: 写 `README.md`(精简版)**

```markdown
# Ghome

LGBTQ+ 数字生活总入口的 monorepo:`apps/web`(用户站)、`apps/admin`(运营管理端)、`packages/db`(数据访问)。

## 设计文档

- 产品形态与架构:[docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md](docs/superpowers/specs/2026-05-08-ghome-product-shape-design.md)
- 行为准则:[CLAUDE.md](CLAUDE.md)

## 开发先决条件

- Node.js 20(`.nvmrc`)
- pnpm 9.x(`corepack enable && corepack prepare pnpm@latest --activate`)
- Docker(用于本地 Postgres)

## 一键起项目

```bash
pnpm install
docker compose up -d        # 起 Postgres(P1 起才会用到)
pnpm dev                    # 并行起 web (3000) + admin (3100)
```

## 当前阶段

P0 · 脚手架 — 两个空白 Next.js app + Postgres 容器 + CI。
```

- [ ] **Step 6: 提交初始结构**

```bash
git add .gitignore .nvmrc .npmrc README.md
git commit -m "chore: initialize repo metadata (gitignore, nvmrc, npmrc, README)"
```

Expected: 单 commit 创建 4 个文件,无 hooks(尚未配置 husky)。

---

## Task 2 — pnpm workspace + TypeScript 基础配置

**Files:**
- Create: `pnpm-workspace.yaml`
- Create: `package.json`
- Create: `tsconfig.base.json`

- [ ] **Step 1: 写 `pnpm-workspace.yaml`**

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

- [ ] **Step 2: 写根 `package.json`**

```json
{
  "name": "ghome",
  "version": "0.0.0",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=9.0.0"
  },
  "scripts": {
    "dev": "pnpm -r --parallel --stream run dev",
    "build": "pnpm -r run build",
    "lint": "pnpm -r run lint",
    "typecheck": "pnpm -r run typecheck",
    "clean": "pnpm -r run clean && rimraf node_modules"
  },
  "devDependencies": {
    "rimraf": "^6.0.1",
    "typescript": "^5.5.0"
  }
}
```

- [ ] **Step 3: 写 `tsconfig.base.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "jsx": "preserve",
    "incremental": true
  },
  "exclude": ["node_modules", ".next", "dist", "out"]
}
```

- [ ] **Step 4: 验证 pnpm 可识别 workspace**

```bash
corepack enable
corepack prepare pnpm@9.12.0 --activate
pnpm --version
pnpm install
```

Expected: pnpm 9.12.0 输出版本号;`pnpm install` 完成(此时还没有子包,会报 "no projects matched the filters" 但不影响)。可能输出 `Done in <X>s`。

- [ ] **Step 5: 提交**

```bash
git add pnpm-workspace.yaml package.json tsconfig.base.json pnpm-lock.yaml
git commit -m "chore: set up pnpm workspace and base TypeScript config"
```

---

## Task 3 — docker-compose:Postgres 16 + Adminer

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 写 `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: ghome-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ghome
      [敏感内容已脱敏]
      POSTGRES_DB: ghome
    ports:
      - "5432:5432"
    volumes:
      - ./.docker-data/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ghome -d ghome"]
      interval: 5s
      timeout: 5s
      retries: 10

  adminer:
    image: adminer:4
    container_name: ghome-adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
```

- [ ] **Step 2: 启动并验证连接**

```bash
docker compose up -d
docker compose ps
```

Expected: 两条记录都是 `Up`,`postgres` 状态包含 `(healthy)`(可能首次启动需要 ~10s,可重复 `docker compose ps` 直到健康)。

- [ ] **Step 3: 验证 Postgres 可访问**

```bash
docker compose exec postgres psql -U ghome -d ghome -c "SELECT version();"
```

Expected: 输出 `PostgreSQL 16.x ...`。

- [ ] **Step 4: 验证 Adminer 起来**

```bash
curl -fsS http://localhost:8080/ | head -c 200
```

Expected: HTML 包含 `<title>Login - Adminer</title>` 或类似,无 connection refused。

- [ ] **Step 5: 停止容器(节省资源,P1 才会持续用)**

```bash
docker compose down
```

Expected: `Network ghome_default Removed`(或类似)。本地 `./.docker-data/postgres/` 目录会保留数据,已在 .gitignore 里。

- [ ] **Step 6: 提交**

```bash
git add docker-compose.yml
git commit -m "chore: add docker-compose with postgres 16 and adminer"
```

---

## Task 4 — apps/web 脚手架(Next.js 15 空白页)

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.mjs`
- Create: `apps/web/postcss.config.mjs`
- Create: `apps/web/.eslintrc.cjs`
- Create: `apps/web/.env.example`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/globals.css`

- [ ] **Step 1: 写 `apps/web/package.json`**

```json
{
  "name": "@ghome/web",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3000",
    "build": "next build",
    "start": "next start --port 3000",
    "lint": "next lint --dir app",
    "typecheck": "tsc --noEmit",
    "clean": "rimraf .next out"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.14.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "rimraf": "^6.0.1",
    "typescript": "^5.5.0"
  }
}
```

- [ ] **Step 2: 写 `apps/web/tsconfig.json`**

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules", ".next"]
}
```

- [ ] **Step 3: 写 `apps/web/next.config.mjs`**

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
};

export default nextConfig;
```

- [ ] **Step 4: 写 `apps/web/postcss.config.mjs`(空配置占位,P2 上 Tailwind 时再填)**

```js
export default {
  plugins: {},
};
```

- [ ] **Step 5: 写 `apps/web/.eslintrc.cjs`**

```js
module.exports = {
  root: true,
  extends: ["next/core-web-vitals"],
};
```

- [ ] **Step 6: 写 `apps/web/.env.example`**

```bash
# 仅占位,P0 不连接 DB。P1 起会用到。
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome
```

- [ ] **Step 7: 写 `apps/web/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ghome",
  description: "LGBTQ+ 数字生活总入口",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 8: 写 `apps/web/app/page.tsx`**

```tsx
export default function HomePage() {
  return (
    <main style={{ padding: "48px 24px", fontFamily: "system-ui, sans-serif" }}>
      <h1>Ghome · web</h1>
      <p>P0 · 脚手架占位。当前阶段:apps/web 已起。</p>
    </main>
  );
}
```

- [ ] **Step 9: 写 `apps/web/app/globals.css`**

```css
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { color: #111827; background: #F5F7FA; }
```

- [ ] **Step 10: 安装依赖(在仓库根)**

```bash
pnpm install
```

Expected: pnpm 拉下 next/react/eslint 等;输出 `+ next 15.x.x` 等。

- [ ] **Step 11: 启动 web 验证可访问**

```bash
pnpm --filter @ghome/web dev &
sleep 8
curl -fsS http://localhost:3000/ | grep -o "P0 · 脚手架占位"
```

Expected: `P0 · 脚手架占位`。然后:

```bash
kill %1 2>/dev/null || true
```

(把后台 dev server 停掉。如果 `curl` 这一步在 macOS 上 grep 找不到中文,改用 `grep -o "Ghome · web"` 也行。)

- [ ] **Step 12: 验证 typecheck 与 build**

```bash
pnpm --filter @ghome/web typecheck
pnpm --filter @ghome/web build
```

Expected: 两步都成功;build 输出包含 `○ /` static route。

- [ ] **Step 13: 提交**

```bash
git add apps/web pnpm-lock.yaml
git commit -m "feat(web): scaffold blank Next.js 15 app on port 3000"
```

---

## Task 5 — apps/admin 脚手架(端口 3100)

**Files:**
- Create: `apps/admin/package.json`
- Create: `apps/admin/tsconfig.json`
- Create: `apps/admin/next.config.mjs`
- Create: `apps/admin/postcss.config.mjs`
- Create: `apps/admin/.eslintrc.cjs`
- Create: `apps/admin/.env.example`
- Create: `apps/admin/app/layout.tsx`
- Create: `apps/admin/app/page.tsx`
- Create: `apps/admin/app/globals.css`

- [ ] **Step 1: 写 `apps/admin/package.json`(端口 3100)**

```json
{
  "name": "@ghome/admin",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3100",
    "build": "next build",
    "start": "next start --port 3100",
    "lint": "next lint --dir app",
    "typecheck": "tsc --noEmit",
    "clean": "rimraf .next out"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.14.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "rimraf": "^6.0.1",
    "typescript": "^5.5.0"
  }
}
```

- [ ] **Step 2: 写 `apps/admin/tsconfig.json`(同 web)**

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules", ".next"]
}
```

- [ ] **Step 3: 写 `apps/admin/next.config.mjs`**

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
};

export default nextConfig;
```

- [ ] **Step 4: 写 `apps/admin/postcss.config.mjs`**

```js
export default {
  plugins: {},
};
```

- [ ] **Step 5: 写 `apps/admin/.eslintrc.cjs`**

```js
module.exports = {
  root: true,
  extends: ["next/core-web-vitals"],
};
```

- [ ] **Step 6: 写 `apps/admin/.env.example`**

```bash
DATABASE_URL=postgres://ghome:ghome@localhost:5432/ghome
# P4 起会加:GitHub OAuth、AUTH_SECRET、ADMIN_ALLOWED_GITHUB_LOGINS、REVALIDATE_SECRET
```

- [ ] **Step 7: 写 `apps/admin/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ghome Admin",
  description: "Ghome 运营管理端",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 8: 写 `apps/admin/app/page.tsx`**

```tsx
export default function AdminHomePage() {
  return (
    <main style={{ padding: "48px 24px", fontFamily: "system-ui, sans-serif" }}>
      <h1>Ghome · admin</h1>
      <p>P0 · 脚手架占位。当前阶段:apps/admin 已起(端口 3100)。</p>
    </main>
  );
}
```

- [ ] **Step 9: 写 `apps/admin/app/globals.css`**

```css
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { color: #111827; background: #FFFFFF; }
```

- [ ] **Step 10: 安装依赖**

```bash
pnpm install
```

Expected: pnpm 复用 cache,admin 的依赖几乎瞬时完成。

- [ ] **Step 11: 启动 admin 验证可访问(3100)**

```bash
pnpm --filter @ghome/admin dev &
sleep 8
curl -fsS http://localhost:3100/ | grep -o "Ghome · admin"
kill %1 2>/dev/null || true
```

Expected: 输出 `Ghome · admin`。

- [ ] **Step 12: 验证 typecheck 与 build**

```bash
pnpm --filter @ghome/admin typecheck
pnpm --filter @ghome/admin build
```

Expected: 都通过。

- [ ] **Step 13: 提交**

```bash
git add apps/admin pnpm-lock.yaml
git commit -m "feat(admin): scaffold blank Next.js 15 app on port 3100"
```

---

## Task 6 — packages/db 占位包(P0 不连 DB,只准备 PrismaClient 单例)

**Files:**
- Create: `packages/db/package.json`
- Create: `packages/db/tsconfig.json`
- Create: `packages/db/src/index.ts`

- [ ] **Step 1: 写 `packages/db/package.json`**

```json
{
  "name": "@ghome/db",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --noEmit",
    "clean": "rimraf dist"
  },
  "dependencies": {
    "@prisma/client": "^5.22.0"
  },
  "devDependencies": {
    "eslint": "^9.0.0",
    "prisma": "^5.22.0",
    "rimraf": "^6.0.1",
    "typescript": "^5.5.0"
  }
}
```

> 说明:P0 把 `@prisma/client` 与 `prisma` CLI 都装上,但**不**写 `schema.prisma`、不跑 generate、不连 DB。
> 仅用于让 `import { prisma } from '@ghome/db'` 在编译期可解析(P1 才真正落地 schema 与 client)。

- [ ] **Step 2: 写 `packages/db/tsconfig.json`**

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3: 写 `packages/db/src/index.ts`(P0 占位 — 不实例化 PrismaClient,因为没 schema)**

```ts
// P0 占位:Prisma schema 在 P1 才落地,目前只导出类型形状以让编译通过。
// P1 会替换为真正的 PrismaClient 单例 + queries 模块。

export const PRISMA_PLACEHOLDER = "P1 will replace this with a real PrismaClient singleton";

export function notReady(name: string): never {
  throw new Error(`@ghome/db.${name} is not yet implemented (P0 placeholder)`);
}
```

- [ ] **Step 4: 安装依赖**

```bash
pnpm install
```

Expected: 拉下 `prisma` 与 `@prisma/client`(包较大,可能花几十秒)。完成后 `pnpm-lock.yaml` 更新。

- [ ] **Step 5: 验证 typecheck**

```bash
pnpm --filter @ghome/db typecheck
```

Expected: 通过(虽然没有任何运行时逻辑,但类型可解析)。

- [ ] **Step 6: 提交**

```bash
git add packages/db pnpm-lock.yaml
git commit -m "feat(db): scaffold @ghome/db placeholder package (Prisma deps only)"
```

---

## Task 7 — 根级跨包脚本验证

无新文件。验证 Task 2 写的根 `package.json` 脚本对所有子包都生效。

- [ ] **Step 1: 验证 `pnpm typecheck` 走全部子包**

```bash
pnpm typecheck
```

Expected: 输出三段(`@ghome/web`、`@ghome/admin`、`@ghome/db`)的 typecheck,全通过。

- [ ] **Step 2: 验证 `pnpm lint` 走 web/admin**

```bash
pnpm lint
```

Expected: web 与 admin 输出 "No ESLint warnings or errors";`@ghome/db` 因为没声明 `lint` 脚本会被 pnpm 跳过(`pnpm` 默认 `--if-present` 行为对 `-r` 不严格;若报错可在 db 的 lint 脚本里写 `echo skip`)。

- [ ] **Step 3: 验证 `pnpm build` 走全部子包**

```bash
pnpm build
```

Expected: web 与 admin 都 build 成功(`@ghome/db` 没声明 `build` 脚本也跳过)。

- [ ] **Step 4: 验证 `pnpm dev` 并行起两个 app**

```bash
pnpm dev &
DEV_PID=$!
sleep 12
curl -fsS http://localhost:3000/ | grep -o "Ghome · web"
curl -fsS http://localhost:3100/ | grep -o "Ghome · admin"
kill $DEV_PID 2>/dev/null || true
```

Expected: 两条 grep 都命中。

- [ ] **Step 5: 没有新文件需要 commit,直接进 Task 8**

(本任务只做行为验证,Task 7 没有 commit。)

---

## Task 8 — GitHub Actions CI(极简版,P0 不需要 Postgres service)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 写 `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    runs-on: ubuntu-latest
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

      - name: Lint
        run: pnpm lint

      - name: Typecheck
        run: pnpm typecheck

      - name: Build
        run: pnpm build
```

> **注意**:P0 的 CI **不**包含 `postgres:16` service、**不**跑 `prisma migrate / db seed`。
> 因为页面是空白的,`pnpm build` 不会查 DB。详见 spec §4.1 的 "CI 含义(分阶段)" 部分。
> P1 任务里会把这个 ci.yml **整体重写**加上 Postgres service。

- [ ] **Step 2: 提交**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add minimal lint/typecheck/build workflow (no DB at P0)"
```

- [ ] **Step 3: 本地用 `act` 或人工远端验证(可选)**

```bash
# 选项 A:推到远端 PR(若已建仓库)
# 选项 B:用 nektos/act 本地跑(若已装):
#   act pull_request -W .github/workflows/ci.yml --container-architecture linux/amd64
```

> **如果 P0 还没有远端仓库**:跳过该步,本地终端按 Step 4 手动复刻一遍 CI 步骤即可。

- [ ] **Step 4: 本地手动复刻 CI 步骤(无 act 时的兜底)**

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
```

Expected: 4 步全过。这等价于 CI 在 ubuntu 跑通。

---

## Task 9 — 完整冒烟与最终提交

无新文件。本任务把 P0 的所有完成判据跑一遍。

- [ ] **Step 1: 干净环境冒烟**

```bash
pnpm clean 2>/dev/null || true
rm -rf node_modules apps/*/node_modules packages/*/node_modules
pnpm install
```

Expected: 完全重新安装成功。

- [ ] **Step 2: 起 Postgres 验证**

```bash
docker compose up -d
docker compose ps | grep -q "(healthy)"
echo "postgres healthy: $?"
```

Expected: `postgres healthy: 0`(0 = grep 匹配成功)。

- [ ] **Step 3: 起两个 app 验证**

```bash
pnpm dev &
DEV_PID=$!
sleep 12
curl -fsS http://localhost:3000/ | grep -q "Ghome · web" && echo "web OK"
curl -fsS http://localhost:3100/ | grep -q "Ghome · admin" && echo "admin OK"
kill $DEV_PID 2>/dev/null || true
wait 2>/dev/null
```

Expected: 输出 `web OK` 与 `admin OK`。

- [ ] **Step 4: build 全套**

```bash
pnpm typecheck
pnpm lint
pnpm build
```

Expected: 三步全过。

- [ ] **Step 5: 关闭 Postgres**

```bash
docker compose down
```

- [ ] **Step 6: 检查 git 状态干净**

```bash
git status --short
```

Expected: 空输出(或只有 `pnpm-lock.yaml` 改动 — 若有则一并提交):

```bash
git add pnpm-lock.yaml 2>/dev/null
git diff --cached --quiet || git commit -m "chore: refresh pnpm-lock after smoke test"
```

- [ ] **Step 7: 标签 P0 完成**

```bash
git tag -a p0-scaffolding -m "P0 · scaffolding complete: web(3000) + admin(3100) + postgres docker + CI"
git log --oneline -10
```

Expected: 看到 9 个左右的 commit + 1 个 tag。

---

## P0 完成判据(对应 spec §5)

- ✅ `pnpm dev` 起两个空白页(web 3000、admin 3100)— Task 5/9 已验证
- ✅ `docker compose up -d` 起来 Postgres,`pg_isready` 通过 — Task 3/9 已验证
- ✅ CI 在 PR 上绿勾(三步 lint/typecheck/build 全过)— Task 8 + Task 9 本地复刻通过
- ✅ 仓库结构对齐 spec §1.1 monorepo 布局 — Task 1–7 已落地

---

## 已知 P0 故意不做的事(P1 起补)

- **不写 `schema.prisma`、不跑 `prisma migrate`、不写 seed**(P1)
- **CI 不连 Postgres**、不跑 migrate / db seed(P1 升级 ci.yml)
- **不上 Tailwind**(P2 视觉重渲时再上)
- **不上 husky / lint-staged**(可选,后期视团队需要)
- **不发布远端 git 仓库**(由人决定何时建 GitHub repo;CI 推上去自然跑)
- **app 里没有任何 DB 查询**(`@ghome/db` 是占位)

---

## Self-Review

- **Spec 覆盖**:P0 范围 = "脚手架 + Postgres 容器 + 极简 CI" — 9 个 task 覆盖了 spec §5 P0 完成物的全部条目。
- **占位符扫描**:每一步都给出了具体内容(代码块 / 命令 / 期望输出);没有 "TBD" / "TODO" / "fill in" / "类似 Task X"。
- **类型一致性**:`@ghome/web` `@ghome/admin` `@ghome/db` 命名贯穿全文;端口 3000/3100 一致;`pnpm@9.12.0` 在根 package.json 与 CI 一致;Node 20 在 .nvmrc 与 CI `node-version-file` 一致;Next.js 15 / React 19 在两个 app 的 package.json 一致。
- **测试覆盖**:P0 是纯脚手架,不写单元测试;改用"行为冒烟"(curl + grep + build/typecheck/lint),已在 Task 4/5/7/9 显式验证。

---

## 下一步

P0 完成后,**写 P1 plan**(数据模型 + 迁移 + seed + CI 升级带 Postgres service)。P1 plan 会引用本 plan 的 `@ghome/db` 包占位,在那基础上落 14 张表 schema。
