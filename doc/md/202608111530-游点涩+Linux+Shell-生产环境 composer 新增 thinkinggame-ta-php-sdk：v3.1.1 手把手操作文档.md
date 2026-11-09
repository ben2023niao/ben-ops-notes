---
id: "doc-d66e40fd8fc4"
title: "生产环境 composer 新增 thinkinggame/ta-php-sdk：v3.1.1 手把手操作文档"
date: "2026-08-11T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-11-1530-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%88%B0%E6%AD%A3%E5%BC%8F%E7%8E%AF%E5%A2%83composer%E6%96%B0%E5%A2%9Eta-php-sdk%E6%89%8B%E6%8A%8A%E6%89%8B%E6%93%8D%E4%BD%9C%E6%96%87%E6%A1%A3.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-11-1530-【运维记录】测试环境到正式环境composer新增ta-php-sdk手把手操作文档.md"
sourceSha256: "b70ce81db0471afa411e5c270d2c98149079fae4484b2cc70f19f2b8f0fff2dc"
sourceSystem: "project-doc"
---

# 生产环境 composer 新增 thinkinggame/ta-php-sdk：v3.1.1 手把手操作文档

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608111530-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E7%94%9F%E4%BA%A7%E7%8E%AF%E5%A2%83%20composer%20%E6%96%B0%E5%A2%9E%20thinkinggame-ta-php-sdk%EF%BC%9Av3.1.1%20%E6%89%8B%E6%8A%8A%E6%89%8B%E6%93%8D%E4%BD%9C%E6%96%87%E6%A1%A3.md)

> 整理日期：2026-08-11 15:30｜日期依据：文件名日期

环境标签：混合（测试环境参考 / 正式环境 main 执行）

文档日期：2026-08-11

## 变更信息

```text
平台：youdianse
是否影响用户：无
影响范围（功能）：后台代码新增 composer 包（大数据上报）
前端/后端：后端
环境：生产环境（main）
升级内容：无需业务代码发布，只是 composer 新增一个包
开发：@ck80605
测试：@xiaoheitu777
运维：@Kermit0824 @jett_yunwei @Ben_Bird @melo_sre
依赖：composer require thinkinggame/ta-php-sdk:v3.1.1
```

## 重要注意

```text
该包用于大数据上报，创建 docker 容器时镜像内必须时刻包含该包。
即：任何一次镜像构建/容器发布，composer install 都必须成功且
vendor/thinkinggame/ta-php-sdk 必须存在，不能因为后续 composer 调整被删除。
```

## 背景与参考

```text
测试环境已于 2026-08-06 完成相同操作：
  业务提交：b3706f8c chore: add thinking analytics sdk
  镜像：youdianse-php:dev-b3706f8c
  容器内验证：thinkinggame/ta-php-sdk v3.1.1
  文档：docs/2026-08-06-1748-【运维记录】测试环境新增大数据上报SDK与te-sdk配置.md

正式环境 main 已于 2026-08-11 参考该操作完成 composer require。
本文档把完整流程固化为“手把手”步骤，供正式环境加 composer 依赖复用。
```

## 前置信息（执行前补全占位符）

```text
本地正式运维仓库：<LOCAL_MAIN_OPS_REPO_PATH>
本地正式业务仓库：<LOCAL_MAIN_PHP_REPO_PATH>
正式服务器 SSH：<MAIN_SSH_USER>@<MAIN_SERVER_IP>
服务器运维目录：<MAIN_OPS_DIR>
服务器业务目录：<MAIN_OPS_DIR>/src/youdianse-php
正式 CICD Web：https://cicd.youdianse-main.xyz
业务仓库：18game.18git.com/php/youdianse-php.git（main 分支）
```

## 目标

```text
1. 业务仓库 main 的 composer.dev.json / composer.prod.json 新增
   "thinkinggame/ta-php-sdk": "v3.1.1"。
2. 提交并推送 main。
3. 正式服务器拉取 main，构建镜像并重建 web/nginx/cron 容器。
4. 验证容器内 vendor/thinkinggame/ta-php-sdk 存在且版本为 v3.1.1。
5. 以后所有 docker 容器创建/发布都必须保证该包仍在镜像内。
```

## 边界与安全（每步都必须遵守）

```text
1. 只操作正式环境 main；不在测试仓库直接执行正式操作。
2. 不输出、不记录、不提交：Telegram token/chat_id、SSH 密码、发布密码、
   webhook token、私钥、带凭据仓库 URL。
3. composer.json / composer.lock 不入库，只维护 composer.dev.json / composer.prod.json。
4. 每完成一个明确步骤，向运维群发送【正式环境｜步骤 N 完成】普通文本通知。
```

## 操作步骤

### 1. 本地核验仓库与分支

```bash
cd <LOCAL_MAIN_PHP_REPO_PATH>
git branch --show-current   # 期望 main
git status --short --branch
git pull --ff-only origin main
```

要求：main 分支、工作区干净或仅预期改动、能 fast-forward。

### 2. 新增依赖

方式 A（推荐，与测试环境一致）：直接编辑依赖清单

```text
编辑 composer.dev.json 与 composer.prod.json 的 require，新增：
    "thinkinggame/ta-php-sdk": "v3.1.1"
```

方式 B（想走真实 composer 命令）：

```bash
cp composer.dev.json composer.json
composer require thinkinggame/ta-php-sdk:v3.1.1 --no-update
# 把 composer.json 的 require 结果同步进 composer.dev.json / composer.prod.json
rm -f composer.json composer.lock
```

注意：`composer.json`、`composer.lock` 在 .gitignore 中，不入库。

### 3. 本地验证

```bash
python3 -m json.tool composer.dev.json >/dev/null
python3 -m json.tool composer.prod.json >/dev/null
python3 - <<'PY'
import json
for name in ("composer.dev.json", "composer.prod.json"):
    data = json.load(open(name, encoding="utf-8"))
    req = data.get("require", {})
    assert req.get("thinkinggame/ta-php-sdk") == "v3.1.1", (name, req.get("thinkinggame/ta-php-sdk"))
    print(name, "OK")
PY
git diff --check
git diff -- composer.dev.json composer.prod.json
```

### 4. 提交推送 main

```bash
git add composer.dev.json composer.prod.json
git commit -m "chore: add thinking analytics sdk"
git push origin main
git rev-parse --short HEAD
```

只提交本次依赖文件，不夹带其他改动。

### 5. 正式服务器部署

```bash
ssh <MAIN_SSH_USER>@<MAIN_SERVER_IP>
cd <MAIN_OPS_DIR>
git status --short --branch
git pull --ff-only origin main
git rev-parse --short HEAD

cd <MAIN_OPS_DIR>/src/youdianse-php
git status --short --branch
git pull --ff-only origin main
git rev-parse --short HEAD
```

然后走正式发布（二选一）：

```text
方式 1：打开 <正式 CICD Web> 选择 main 最新提交发布（携带 php-cron 执行容器）。
方式 2：命令行构建并重建容器：
  docker compose --env-file .ops-build.env --profile cron up -d --force-recreate --no-build web nginx cron
```

发布说明：虽然“无需业务代码发布”，但 composer 包是构建期安装进镜像的，
必须重新 build 镜像并重建容器，容器内才会出现 vendor/thinkinggame/ta-php-sdk。

### 6. 容器内验证（关键步骤）

```bash
docker ps --filter name=youdianse --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'

# 方式 1：composer show
docker exec <web容器> sh -lc 'composer show thinkinggame/ta-php-sdk'

# 方式 2：vendor 目录
docker exec <web容器> sh -lc 'ls -d vendor/thinkinggame/ta-php-sdk'

# 方式 3：installed.json
docker exec <web容器> sh -lc 'grep -A2 "\"name\": \"thinkinggame/ta-php-sdk\"" vendor/composer/installed.json'

# 后台入口健康检查
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" https://<正式后台域名>/admin1866/login
```

要求：composer show 输出 `versions : * v3.1.1`（或等价版本 v3.1.1），
vendor 目录存在，后台 HTTP 200。

### 7. 通知与收口

```text
1. 部署前/后按步骤发送【正式环境｜步骤 N 完成】通知。
2. 更新运维仓库 docs/workbench，记录正式 main 提交号、镜像 tag、容器验证结果。
3. 发送最终汇总和本文档附件到运维群。
```

### 8. 回滚

```text
1. 业务仓库 main 回退或反向提交移除 composer.dev.json / composer.prod.json
   中的 thinkinggame/ta-php-sdk，推送 main。
2. 正式服务器拉取回滚提交。
3. 重新构建 youdianse-php 镜像并重建 web/nginx/cron。
4. 验证容器内 SDK 已移除、后台 HTTP 200。
```

## 验证清单（全部通过才算完成）

```text
□ composer.dev.json / composer.prod.json JSON 合法且 require 含 v3.1.1
□ main 提交已推送；服务器业务 HEAD 与 origin/main 一致
□ 镜像 tag 为 main-<gitid>；web/nginx/cron 均 Up
□ 容器内 vendor/thinkinggame/ta-php-sdk 存在，版本 v3.1.1
□ 后台入口 HTTP 200
□ 后续任意 docker 容器创建/发布后复检该包仍存在（大数据上报必须时刻有）
```

## 可直接整段发给 AI 的提示词

```text
你是运维自动化助手。请在“正式环境 / main 分支”的业务仓库新增 composer 依赖
thinkinggame/ta-php-sdk:v3.1.1，并在正式服务器构建镜像、重建容器后验证。

要求：
1. 该包用于大数据上报，创建 docker 容器时镜像内必须时刻包含该包。
2. 只修改 composer.dev.json / composer.prod.json 的 require，新增
   "thinkinggame/ta-php-sdk": "v3.1.1"；composer.json/composer.lock 不入库。
3. 只提交本次依赖文件并推送 main。
4. 正式服务器拉取 main，构建 youdianse-php:main-<gitid> 并重建 web/nginx/cron。
5. 验证：composer show thinkinggame/ta-php-sdk 版本 v3.1.1；
   vendor/thinkinggame/ta-php-sdk 存在；后台入口 HTTP 200。
6. 不输出、不提交任何 token、chat_id、SSH 密码、发布密码、私钥、带凭据 URL。
7. 完成后汇报：main 提交号、服务器业务 HEAD、镜像 tag、容器状态、
   容器内 SDK 版本、后台 HTTP 状态。

正式环境信息：
- 本地正式业务仓库：<LOCAL_MAIN_PHP_REPO_PATH>
- 正式服务器 SSH：<MAIN_SSH_USER>@<MAIN_SERVER_IP>
- 服务器运维目录：<MAIN_OPS_DIR>
- CICD Web：<MAIN_CICD_URL>
```

## 测试环境参考记录

```text
docs/2026-08-06-1748-【运维记录】测试环境新增大数据上报SDK与te-sdk配置.md
业务提交 b3706f8c；镜像 youdianse-php:dev-b3706f8c；容器内 SDK v3.1.1 验证通过。
```
