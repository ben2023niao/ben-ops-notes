---
id: "doc-7f02cccc6cb8"
title: "Ghome 上线和维护速查"
date: "2026-06-16T22:41:01+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "GHOME"]
tags: ["GHOME", "Linux", "Shell", "Docker", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/ghome/docs/deployment/production-deploy.md"
sourcePath: "~/Projects/work/game/ghome/docs/deployment/production-deploy.md"
sourceSha256: "5afba6e6fc102a43ae280b722206a7dffcd5b945330cc40066e17480c9fe9e88"
sourceSystem: "project-doc"
---

# Ghome 上线和维护速查

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606162241-%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%BF%90%E7%BB%B4%2BGHOME%2BLinux-Ghome%20%E4%B8%8A%E7%BA%BF%E5%92%8C%E7%BB%B4%E6%8A%A4%E9%80%9F%E6%9F%A5.md)

> 整理日期：2026-06-16 22:41｜日期依据：文件创建/修改时间

日常发布不执行数据库 migration。脚本最后只发一条简体中文 Telegram 汇总卡片。

## 0. 线上信息

```text
服务器：52.77.246.213
目录：/opt/ghome
前台：https://www.ghome-main.xyz/
后台：https://admin.ghome-main.xyz/signin
数据库：RDS PostgreSQL / ghome_prod
发布脚本：scripts/spug-prod-deploy.sh
```

## 1. 普通上线

开发本地提交：

```bash
cd /Users/ben/Documents/main/ghome
git status --short
sh -n scripts/spug-prod-deploy.sh
docker compose -f docker-compose.prod.yml config --quiet
git add <changed-files>
git commit -m "<message>"
git push origin main
```

Spug 发布命令：

```bash
cd /opt/ghome
sudo -E ./scripts/spug-prod-deploy.sh
```

Spug 模板直接执行：

```bash
sh /opt/ghome/scripts/spug-prod-template.sh
```

有数据库 migration 时，在 Spug 模板中设置：

```bash
RUN_MIGRATIONS=1 sh /opt/ghome/scripts/spug-prod-template.sh
```

手动发布：

```bash
ssh -i Ghomie.pem ubuntu@52.77.246.213
cd /opt/ghome
grep -Eq '^[敏感内容已脱敏] .cicd.env && echo 'TG_BOT_TOKEN ok'
grep -Eq '^TG_CHAT_ID=.' .cicd.env && echo 'TG_CHAT_ID ok'
sudo -E ./scripts/spug-prod-deploy.sh
```

脚本流程：

```text
拉代码 -> 构建镜像 -> 跳过 migration -> 构建前后台 -> 重启服务 -> 健康检查 -> Telegram 汇总
```

## 2. 带数据库 Migration 上线

只有改了 `packages/db/prisma/schema.prisma` 才走本节。

开发生成并提交 migration：

```bash
cd /Users/ben/Documents/main/ghome
docker compose run --rm migrate \
  pnpm --filter @ghome/db exec prisma migrate dev --name <migration_name>
git status --short packages/db/prisma
git diff -- packages/db/prisma/schema.prisma packages/db/prisma/migrations
find packages/db/prisma/migrations -maxdepth 2 -name migration.sql | sort | tail -5
git add packages/db/prisma/schema.prisma packages/db/prisma/migrations
git commit -m "Add <migration_name> migration"
git push origin main
```

运维先做 RDS 手动快照：

```text
RDS -> Databases -> ghome-prod-postgres-01 -> Actions -> Take snapshot
等快照状态可用
```

再发布：

```bash
ssh -i Ghomie.pem ubuntu@52.77.246.213
cd /opt/ghome
sudo -E env RUN_MIGRATIONS=1 ./scripts/spug-prod-deploy.sh
```

成功卡片应看到：

```text
数据库：有 migration/schema 变更 N 个；已执行 prisma migrate deploy
```

忘记加 `RUN_MIGRATIONS=1` 时，脚本会停止发布，避免代码和数据库结构不一致。

## 3. 发布后检查

```bash
cd /opt/ghome
docker compose -f docker-compose.prod.yml --project-directory /opt/ghome ps
curl -I https://www.ghome-main.xyz/
curl -I https://admin.ghome-main.xyz/signin
curl -I https://www.ghome-main.xyz/uploads/apps/xiaolan-video-logo.png
```

## 4. 日常维护

看日志：

```bash
cd /opt/ghome
docker compose -f docker-compose.prod.yml --project-directory /opt/ghome logs -f web admin
```

只重启前后台：

```bash
cd /opt/ghome
docker compose -f docker-compose.prod.yml --project-directory /opt/ghome restart web admin
```

看磁盘：

```bash
df -h
docker system df
```

## 5. 回滚

只回滚代码：

```bash
cd /opt/ghome
sudo git checkout <previous-commit>
sudo -E ./scripts/spug-prod-deploy.sh
```

数据库 migration 已执行后，优先用新 migration 前滚修复。必须恢复数据时，用 RDS 快照。

## 6. 禁止命令

生产不要执行：

```bash
docker compose -f docker-compose.prod.yml down -v
pnpm --filter @ghome/db exec prisma migrate reset
pnpm --filter @ghome/db exec prisma db push
```

原因：

```text
down -v 会删 uploads volume
migrate reset 会清空数据库
db push 会绕过 migration 历史直接改库
```
