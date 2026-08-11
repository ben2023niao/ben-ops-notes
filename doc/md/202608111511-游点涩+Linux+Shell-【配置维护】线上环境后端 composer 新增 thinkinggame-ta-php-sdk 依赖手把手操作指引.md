---
id: "doc-f66e51a47d0d"
title: "【配置维护】线上环境后端 composer 新增 thinkinggame-ta-php-sdk 依赖手把手操作指引"
date: "2026-08-11T15:11:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Redis", "自动化", "安全运维"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-11-1511-%E3%80%90%E9%85%8D%E7%BD%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E5%90%8E%E7%AB%AFcomposer%E6%96%B0%E5%A2%9Ethinkinggame-ta-php-sdk%E4%BE%9D%E8%B5%96%E6%89%8B%E6%8A%8A%E6%89%8B%E6%93%8D%E4%BD%9C%E6%8C%87%E5%BC%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-11-1511-【配置维护】线上环境后端composer新增thinkinggame-ta-php-sdk依赖手把手操作指引.md"
sourceSha256: "46fd92437adaab791299936f47e821b0309790475c7a1122068947b5acfc3e09"
sourceSystem: "project-doc"
---

# 【配置维护】线上环境后端 composer 新增 thinkinggame-ta-php-sdk 依赖手把手操作指引

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-11-1511-【配置维护】线上环境后端composer新增thinkinggame-ta-php-sdk依赖手把手操作指引.md`

> 整理日期：2026-08-11 15:11｜日期依据：文件名日期

文档日期：2026-08-11 15:11
环境：游点涩线上环境（main 分支）
分类：配置维护
标签：线上环境、后端、composer、依赖、thinkinggame、ta-php-sdk、手把手

## 需求与工单信息

```text
平台：youdianse
是否影响用户：无
影响范围（功能）：后台代码新增 composer 包
前端/后端：后端
环境：生产环境（main）
开发：@ck80605
测试：@xiaoheitu777
运维：@Kermit0824 @jett_yunwei @Ben_Bird @melo_sre @Daviea2
升级内容：无需代码发布，只是 composer 新增一个包
注意：该包用于大数据上报，创建 docker 容器时必须始终包含
依赖：composer require thinkinggame/ta-php-sdk:v3.1.1
```

## 结论速览

```text
依赖已加入业务仓库 composer.dev.json 与 composer.prod.json：
  "thinkinggame/ta-php-sdk": "v3.1.1"
业务仓库提交：c315279d（chore: 新增 thinkinggame/ta-php-sdk v3.1.1 大数据上报依赖）
本次未触发代码发布/容器重建；下次发布构建（docker compose build）会自动把该包打进镜像。
生产镜像内已验证：composer require 成功、v3.1.1 安装、自动加载 ThinkingData\TDAnalytics 可用。
```

## 为什么这样加（关键架构事实）

1. 业务仓库 `src/youdianse-php` 的 `.gitignore` 排除了 `/composer.json`、`/composer.lock`、`/vendor`；仓库里只维护 `composer.dev.json` 和 `composer.prod.json` 两个依赖入口文件。
2. `php-web.Dockerfile` 构建阶段执行：

   ```bash
   RUN cp composer.dev.json composer.json \
       && composer install --no-interaction --prefer-dist --optimize-autoloader
   ```

   所以容器里的 `composer.json` 实际来自 `composer.dev.json`；要让新包“创建容器时必须有”，必须改 `composer.dev.json`。
3. `composer.prod.json` 是历史遗留的另一个入口（比 dev 多一个 `config.audit` 块），当前构建不用它；为保持两个文件一致、避免将来切换入口时漏包，本次同步修改。
4. 容器启动入口脚本（web/cron-entrypoint）在缺少 `composer.json` 时也会用 `composer.dev.json` 补一份，进一步确认 dev 文件是唯一事实来源。
5. 依赖与业务代码解耦：本次只改依赖入口，不发布代码；开发后续在 `composer.dev.json` 里再加同一行（相同 key、相同值）不会产生 git 冲突。

## 操作前检查清单

```text
□ 读取 workbench/START_HERE.md 与相关 docs，确认本次是线上 main 环境
□ 核对正式群通知要求（每步完成后发【线上环境｜步骤 N 完成】并 @ 名单）
□ 核对生产容器 PHP 扩展是否满足新包要求
□ 核对本地/线上业务仓库状态与远端 main 是否最新
□ 确认目标群 chat_title = 18GAME_ 上线群（正式環境）
```

## 手把手操作步骤

### 第 1 步：只读核验生产容器扩展

```bash
ssh -i id_rsa ubuntu@16.209.16.108
sudo docker exec youdianse-main-php-web php -m | grep -iE '^(curl|zlib|json|mongodb|redis|openssl|pdo)$'
sudo docker exec youdianse-main-php-web cat /var/www/html/youdianse-php/composer.json | head -30
```

说明：ta-php-sdk v3.1.1 要求 `php >=5.5` 与 `ext-curl / ext-zlib / ext-json`；生产为 PHP 7.4.33，上述扩展齐全，满足要求。

### 第 2 步：核对仓库状态

```bash
cd src/youdianse-php          # 本地业务仓库
git status --short --branch
git fetch origin main
git merge --ff-only origin/main   # 确保基于最新 main
```

说明：本次操作前远端 main 已前进到 fd13b44b，本地先同步再改，避免 push 被拒。

### 第 3 步：生产镜像内验证 composer require

用与生产完全一致的环境做一次性验证（容器退出即丢弃，不碰线上）：

```bash
sudo docker run --rm --entrypoint bash youdianse-php:main-87c27ceb3e7c -lc \
  "cd /var/www/html/youdianse-php && composer require thinkinggame/ta-php-sdk:v3.1.1 --no-interaction --prefer-dist --no-progress"
```

验证输出应包含：

```text
Lock file operations: 1 install, 0 updates, 0 removals
  - Locking thinkinggame/ta-php-sdk (v3.1.1)
  - Installing thinkinggame/ta-php-sdk (v3.1.1)
```

再验证自动加载（SDK 类名带命名空间 `ThinkingData\TDAnalytics`）：

```bash
sudo docker run --rm --entrypoint bash youdianse-php:main-87c27ceb3e7c -lc \
  "cd /var/www/html/youdianse-php && composer require thinkinggame/ta-php-sdk:v3.1.1 --no-interaction --prefer-dist >/dev/null 2>&1; \
   php -r 'require \"vendor/autoload.php\"; var_dump(class_exists(\"ThinkingData\\\\TDAnalytics\")); echo ThinkingData\\SDK_VERSION, PHP_EOL;'"
```

预期：`bool(true)` 与 `3.1.1`。

### 第 4 步：修改依赖入口文件

在 `composer.dev.json` 与 `composer.prod.json` 的 `require` 段末尾追加（与 composer 生成格式一致）：

```json
    "telegram-bot/api": "^2.5",
    "thinkinggame/ta-php-sdk": "v3.1.1"
```

校验 JSON：

```bash
python3 -m json.tool composer.dev.json >/dev/null && python3 -m json.tool composer.prod.json >/dev/null
```

### 第 5 步：提交并推送业务仓库

```bash
cd src/youdianse-php
git add composer.dev.json composer.prod.json
git commit -m "chore: 新增 thinkinggame/ta-php-sdk v3.1.1 大数据上报依赖"
git push origin main
```

### 第 6 步：同步线上业务仓库

```bash
cd /opt/docker-youdianse-php/src/youdianse-php
sudo git fetch origin main
sudo git checkout -B main origin/main
sudo grep -n "thinkinggame" composer.dev.json composer.prod.json
```

说明：CICD 构建使用线上仓库工作树（`APP_SOURCE_DIR=src/youdianse-php`），所以线上业务仓库必须拿到最新 main。

### 第 7 步：通知与文档

```text
□ 每完成一步发送正式群 Telegram 通知，标题【线上环境｜步骤 N 完成】
□ 通知统一 @Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2
□ 写事件/操作文档到 docs/YYYY-MM-DD-HHMM-【配置维护】线上环境…md
□ 汇总与文档附件发群；最后合并提交本地运维仓库
```

## 本次执行结果

```text
生产镜像验证：composer require 成功；v3.1.1 锁定并安装；class_exists(ThinkingData\TDAnalytics)=true；SDK_VERSION=3.1.1
业务仓库提交：c315279d，2 文件 +4/-2，origin/main 已同步
线上业务仓库：HEAD=c315279d，工作树干净，composer.dev.json / composer.prod.json 均含依赖
本次未触发发布：当前线上容器仍为旧镜像，下次发布构建后容器内将包含该包
通知：步骤 1-5 已发送（message_id 8992-8996），后续步骤见群内
```

## 发布后验证命令（下次发布时使用）

```bash
sudo docker exec youdianse-main-php-web composer show thinkinggame/ta-php-sdk
sudo docker exec youdianse-main-php-web php -r \
  'require "/var/www/html/youdianse-php/vendor/autoload.php"; var_dump(class_exists("ThinkingData\\TDAnalytics"));'
```

## 关于开发后续发布的说明

开发 @ck80605 后续在 `composer.dev.json` 里同样加上 `"thinkinggame/ta-php-sdk": "v3.1.1"` 不会影响本次变更：

- 相同 key、相同值，git 合并视为无差异；
- 依赖入口文件与业务代码分开提交，加依赖不需要等代码发布；
- 只要 `composer.dev.json` 保持该行，任何 docker 构建都会包含此包。

## 回滚

```text
1. 业务仓库 revert 或删除该行并推送：
   git revert c315279d && git push origin main
2. 同步线上业务仓库：
   cd /opt/docker-youdianse-php/src/youdianse-php && sudo git fetch origin main && sudo git checkout -B main origin/main
3. 下次构建将不再包含该包；已发布容器不受影响（本次未发布）。
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、Git 凭据、私钥。业务仓库 remote URL 若带凭据，不在文档中记录。
