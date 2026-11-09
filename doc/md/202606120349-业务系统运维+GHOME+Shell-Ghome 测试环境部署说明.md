---
id: "doc-53172ebf7562"
title: "Ghome 测试环境部署说明"
date: "2026-06-12T03:49:41+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Shell", "Docker", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/deployment/test-environment-deploy.md"
sourcePath: "~/Projects/work/game/ghome/docs/deployment/test-environment-deploy.md"
sourceSha256: "a0dc88487d7cb5f945cb9df81e34a8ffeb1798b25bb5ec00a16eb69c89b46b7d"
sourceSystem: "project-doc"
---

# Ghome 测试环境部署说明

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606120349-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BShell-Ghome%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%E8%AF%B4%E6%98%8E.md)

> 整理日期：2026-06-12 03:49｜日期依据：文件创建/修改时间

本文档记录 Ghome Web 工程在测试环境的容器化部署流程。当前测试环境采用应用容器部署到云服务器、数据库连接远程 PostgreSQL/RDS 的方式。

## 1. 部署架构

测试环境包含以下服务：

```text
云服务器
  ghome-test-migrate       一次性任务：执行 Prisma migration
  ghome-test-seed          一次性任务：灌入测试初始数据
  ghome-test-build-web     一次性任务：构建前台 .next
  ghome-test-build-admin   一次性任务：构建后台 .next
  ghome-test-web           常驻服务：前台 next start，端口 3000
  ghome-test-admin         常驻服务：后台 next start，端口 3100

远程 PostgreSQL/RDS
  ghome_test 空库
```

测试部署不再启动本地 `postgres` 和 `adminer` 容器。数据库通过 `.env.test` 中的连接串访问。

## 2. 前置条件

在宿主机执行，确认云服务器具备 Docker：

```bash title="宿主机执行"
docker --version
docker compose version
```

云服务器需要能访问远程 PostgreSQL/RDS 的 5432 端口。RDS 安全组建议只允许测试应用服务器私有 IP 和堡垒机访问，不建议开放公网 5432。

可以在宿主机执行临时 PostgreSQL 客户端容器，验证远程数据库连接：

```bash title="宿主机执行"
docker run --rm postgres:16.4-alpine \
  psql "postgresql://<user>:<password>@<rds-endpoint>:5432/ghome_test?sslmode=require" \
  -c "select current_database();"
```

## 3. 代码目录

进入包含 `docker-compose.test.yml` 的 Web 工程目录：

```bash title="宿主机执行"
cd /opt/ghome/web
```

实际路径按服务器上的代码目录调整。

## 4. 配置 .env.test

从模板创建真实测试配置：

```bash title="宿主机执行"
cp .env.test.example .env.test
vim .env.test
```

`.env.test` 不提交 Git，且已被 `.gitignore` 和 `.dockerignore` 忽略。

测试环境示例：

```env
NODE_ENV=production

DATABASE_URL_BUILD=postgresql://<user>:<password>@<rds-endpoint>:5432/ghome_test?sslmode=require&connection_limit=1
DATABASE_URL_RUNTIME=postgresql://<user>:<password>@<rds-endpoint>:5432/ghome_test?sslmode=require&connection_limit=5

NEXT_PUBLIC_WEB_BASE_URL=http://<test-app-public-ip>:3000

[敏感内容已脱敏] rand -hex 32>
[敏感内容已脱敏] rand -hex 32>

[敏感内容已脱敏] rand -hex 32>
AUTH_TRUST_HOST=true

WEB_BASE_URL=http://web:3000
ADMIN_BASE_URL=http://<test-app-public-ip>:3100

[敏感内容已脱敏] rand -hex 32>
```

说明：

- `DATABASE_URL_BUILD` 用于 `migrate`、`seed`、`build-web`、`build-admin`，建议 `connection_limit=1`，避免 Next.js 构建期预渲染大量页面时打满数据库连接。
- `DATABASE_URL_RUNTIME` 用于 `web`、`admin` 运行期，测试环境可从 `connection_limit=5` 起步。
- `WEB_BASE_URL=http://web:3000` 是 admin 容器访问 web 容器的 Docker 内部地址。
- `NEXT_PUBLIC_WEB_BASE_URL` 和 `ADMIN_BASE_URL` 是外部访问地址。测试期没有域名时可使用公网 IP + 端口；有域名后改为 HTTPS 地址。

## 5. 生成 Secret

在服务器上生成 4 个独立 secret：

```bash title="宿主机执行"
echo "[敏感内容已脱敏] rand -hex 32)"
echo "[敏感内容已脱敏] rand -hex 32)"
echo "[敏感内容已脱敏] rand -hex 32)"
echo "[敏感内容已脱敏] rand -hex 32)"
```

将输出填入 `.env.test` 对应变量。

各 secret 用途：

| 变量 | 用途 |
| --- | --- |
| `IP_HASH_SECRET` | 生成点击日志中的 IP 哈希，避免保存明文 IP |
| `REVALIDATE_SECRET` | admin 调 web `/api/revalidate` 的 Bearer token，web/admin 必须一致 |
| `AUTH_SECRET` | Auth.js/NextAuth 后台登录 session/JWT 签名密钥 |
| `CRON_SECRET` | 调用 `/api/cron/aggregate-clicks` 的 Bearer token |

测试环境和生产环境不要共用 secret。

## 6. 首次空库初始化

远程数据库为空时，先执行 migration：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml run --rm migrate
```

再灌入测试初始数据：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml run --rm seed
```

说明：

- `migrate` 会在容器内部执行 Prisma migration。
- `seed` 会在容器内部执行测试初始数据灌入。

测试环境可以重复执行 seed；生产环境是否 seed 需要单独评估。

## 7. 构建并启动服务

启动前台和后台：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml up -d web admin
```

该宿主机命令会触发以下容器依赖顺序：

```text
migrate
  -> build-web
  -> build-admin
  -> web
  -> admin
```

其中：

- `build-web` 和 `build-admin` 是一次性构建任务，构建完成后退出。
- `web` 和 `admin` 是常驻服务，只执行 `next start`。
- `.next` 构建产物通过 Docker named volume 在 build 容器和 runtime 容器之间共享。

查看状态：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml ps
```

查看日志：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml logs -f web admin
```

## 8. 访问验证

前台：

```text
http://<test-app-public-ip>:3000
http://<test-app-public-ip>:3000/apps
http://<test-app-public-ip>:3000/api/search?q=健身
```

后台：

```text
http://<test-app-public-ip>:3100/signin
```

数据库行数抽查：

```bash title="宿主机执行"
docker run --rm postgres:16.4-alpine \
  psql "postgresql://<user>:<password>@<rds-endpoint>:5432/ghome_test?sslmode=require" \
  -c "select count(*) from apps; select count(*) from videos; select count(*) from admin_users;"
```

当前 seed 后的典型结果：

```text
apps        9
videos      20
admin_users 3
```

## 9. 常用运维命令

重新构建并启动：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml up -d --build web admin
```

只重新跑 migration：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml run --rm migrate
```

只重新跑 seed：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml run --rm seed
```

停止应用：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml stop web admin
```

停止并移除测试应用容器和网络：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml down
```

清理构建产物 volume 后重新构建：

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d web admin
```

## 10. 版本升级发布

如果本次代码包含 `packages/db/prisma/migrations` 下的新目录，需要先在测试库执行数据库迁移，再重建应用容器。

```bash title="宿主机执行"
docker compose -f docker-compose.test.yml run --rm migrate
docker compose -f docker-compose.test.yml up --build -d web admin
```

近期涉及的数据库迁移：

- `20260610010000_outbound_redirect_tokens`：保存短期跳转 token、消费状态和基础访问风险数据。
- `20260610020000_search_query_stats`：保存站内搜索关键词聚合统计，用于首页和搜索页展示动态热门搜索。

发布时必须先完成 migration，否则相关功能会因为缺少表结构而失败。

本地开发环境如果已经启动过容器，命名卷里可能缓存旧版 Prisma Client。迁移后如遇到 `prisma.outboundRedirectToken` 或 `prisma.searchQueryStat` 不存在，执行：

```bash title="宿主机执行"
docker compose exec -T web sh -c 'pnpm --filter @ghome/db exec prisma generate'
docker compose restart web
```

## 11. 常见问题

### 11.1 Next.js build 报数据库连接失败

如果日志中有：

```text
sorry, too many clients already
```

或 Prisma 报：

```text
P1001 Can't reach database server
```

可能是构建期并行预渲染页面导致数据库连接数被打满。确认：

```env
DATABASE_URL_BUILD=...&connection_limit=1
```

远程 RDS 的最大连接数也需要足够支撑构建和运行。

### 11.2 admin 调 web revalidate 失败

确认：

```env
REVALIDATE_SECRET
WEB_BASE_URL=http://web:3000
```

`REVALIDATE_SECRET` 在 web/admin 中必须一致。`WEB_BASE_URL` 在 Docker 网络内应指向 `web:3000`。

### 11.3 后台登录 session 异常

确认：

```env
AUTH_SECRET
AUTH_TRUST_HOST=true
ADMIN_BASE_URL=http://<test-app-public-ip>:3100
```

修改 `AUTH_SECRET` 会导致已有登录 session 失效。

## 12. 安全注意事项

- `.env.test` 不提交 Git。
- 不要将 `.env.test` 打入 Docker 镜像或公开传输。
- 测试环境 `3100` 后台端口建议只开放给测试人员 IP。
- RDS 5432 不对公网开放。
- 测试环境和生产环境使用不同 secret。
- 如果截图或日志暴露了数据库密码，应及时轮换测试库密码。
