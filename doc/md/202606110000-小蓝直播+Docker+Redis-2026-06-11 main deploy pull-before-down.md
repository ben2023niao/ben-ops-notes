---
id: "doc-92d91b4c6d96"
title: "2026-06-11 main deploy pull-before-down"
date: "2026-06-11T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播", "Docker", "Redis", "自动化", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-deploy-pull-before-down.md"
sourcePath: "~/Projects/work/game/xiaolan-watches/main/docs/agents/logs/2026-06-11-main-deploy-pull-before-down.md"
sourceSha256: "be1748d0d7dee5ce3b57d1c4902ca4991223c07538369f74da64225b94f4925d"
sourceSystem: "project-doc"
---

# 2026-06-11 main deploy pull-before-down

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606110000-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD%2BDocker%2BRedis-2026-06-11%20main%20deploy%20pull-before-down.md)

> 整理日期：2026-06-11 00:00｜日期依据：文件名日期

## Task

Fix the main deployment script so a missing image tag in GitLab Registry does not
stop currently running services during production release rehearsal.

## Data Flow

- Entry: Spug task `main正式发布` or GitLab manual job `deploy-production-spug`
- Script: `infra/deploy/spug-main-update.sh`
- Source update: `git fetch` + `git pull --ff-only origin main`
- Image tag: defaults to current main short SHA unless `IMAGE_TAG` is provided
- Runtime: `docker compose -f infra/deploy/docker-compose.main.yml --profile deploy`
- Services: `migrate api admin-api ws worker web-prod admin-prod live-host-prod`
- Registry: GitLab Container Registry backend/frontend images

## Root Cause

The script executed `docker compose down --remove-orphans` before `docker compose
pull`. If CI had not pushed `kickoff-backend:<main-sha>` and
`kickoff-frontend:<main-sha>` yet, `compose pull` failed after the current
containers were already stopped.

## Fix

- Move artifact preparation before service restart.
- `DEPLOY_MODE=pull`: run `docker compose pull <services>` first.
- `DEPLOY_MODE=build`: run `docker compose build <services>` first.
- Only after pull/build succeeds, run optional `docker compose down
  --remove-orphans`.
- Start services with `docker compose up -d --no-build <services>` so the up
  step uses already prepared artifacts instead of building unexpectedly after
  downtime.

## Verification

- `sh -n infra/deploy/spug-main-update.sh`
- Reviewed deployment docs and aligned the documented order with the script.

## Frontend Contract

No frontend API contract change.

## DB / Redis Impact

No database or Redis schema/config change.
