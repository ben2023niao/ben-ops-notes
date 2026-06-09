---
id: "doc-6e38cb7f7b6c"
title: "2026-06-10 production admin captcha fix"
date: "2026-06-10T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Shell", "Go", "Docker", "Redis", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-prod-admin-captcha-redis-cluster.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-prod-admin-captcha-redis-cluster.md"
sourceSha256: "58054e35b3381e253fe5936350b5cda1cdf7288341810070cc95d949641274cb"
sourceSystem: "project-doc"
---

# 2026-06-10 production admin captcha fix

> 来源文件：`~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-10-prod-admin-captcha-redis-cluster.md`

> 整理日期：2026-06-10 00:00｜日期依据：文件名日期

## Task

Production admin login captcha failed after main deployment.

## Data Flow

- Entry: `https://admin.shijiebeixl.com/auth/login`
- Frontend request: admin `requestClient.get('/auth/captcha')`
- Expected API base: `https://admin-api.shijiebeixl.com/api/v1/admin`
- Backend route: `GET /api/v1/admin/auth/captcha`
- Handler: `internal/http/adminapi.AuthHandler.Captcha`
- Service: `internal/service/admin.AuthService.GenerateCaptcha`
- Storage: Redis key `admin:captcha:{captcha_id}` with TTL
- Response fields: `captcha_id`, `image_data_url`, `expires_in`

## Root Cause

1. Production Redis is AWS ElastiCache Redis Cluster, but the Go app initialized go-redis as a single-node client. Redis returned `MOVED ... redis-prod-000x...`, causing captcha generation to fail with `code=10001`.
2. The admin frontend production build passed `VITE_GLOB_API_URL` as an environment variable, but the Vben extra app config plugin reads `.env.<mode>` files. The generated `_app-config` was `{}`, so the admin frontend called the wrong same-origin path.

## Fix

- Bind `APP_REDIS_MODE` into Go config.
- Set go-redis `UniversalOptions.IsClusterMode` when `redis.mode=cluster`.
- Pass `APP_REDIS_MODE` through production compose/deploy scripts and document `APP_REDIS_MODE=cluster`.
- Generate `apps/admin/.env.<mode>` during Docker frontend builds so `_app-config` contains the production admin API base URL.

## Verification

| Command | Result |
| --- | --- |
| `go test ./internal/config ./internal/infra` | passed |
| `go test ./...` in `services/go-app` | passed |
| `docker compose -f infra/deploy/docker-compose.main.yml --env-file <tmp> config` | confirmed `APP_REDIS_MODE=cluster` in service env |
| local admin build with `.env.prod` | `_app-config` contained `https://admin-api.shijiebeixl.com/api/v1/admin` |

## Frontend Contract

No API contract change. The admin frontend continues to call `/auth/captcha` relative to its configured API base.

## Deployment Note

Production `/opt/xiaolan_watches_the_game_at_night/.cicd.env` must include:

```bash
APP_REDIS_MODE=cluster
```
