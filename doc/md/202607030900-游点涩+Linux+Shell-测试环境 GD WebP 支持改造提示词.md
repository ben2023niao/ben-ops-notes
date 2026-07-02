---
id: "doc-75d7e5e95dfb"
title: "测试环境 GD WebP 支持改造提示词"
date: "2026-07-03T09:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "MySQL", "Redis"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-03-0900-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83GD-WebP%E6%94%AF%E6%8C%81%E6%94%B9%E9%80%A0%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-03-0900-【架构改造】测试环境GD-WebP支持改造提示词.md"
sourceSha256: "f6d74c78681ae13f50e635f8557fb3e29160264d488b0ba952a21227e96867d8"
sourceSystem: "project-doc"
---

# 测试环境 GD WebP 支持改造提示词

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-03-0900-【架构改造】测试环境GD-WebP支持改造提示词.md`

> 整理日期：2026-07-03 09:00｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-03
环境：游点涩测试环境（dev 分支）
分类：架构改造

用途：给 AI 或运维同学复刻“测试环境 PHP GD 扩展增加 WebP 支持”的完整操作流程。这个改造用于缩略图等图片处理需求，目标是让 `youdianse-dev-php-web` 和共用镜像的 `youdianse-dev-php-cron` 都支持 `imagewebp()`。

把下面整段提示词发给 AI，让 AI 先确认当前环境和分支，再执行。

```text
你是运维自动化助手。我要在“游点涩测试环境 / dev 分支”给 PHP GD 扩展补齐 WebP 支持，用于缩略图等图片处理需求。

核心背景：
1. 业务需要生成缩略图，GD 库是 PHP 常用图片处理扩展。
2. 当前测试容器 youdianse-dev-php-web 里 GD 已编译，但缺少 WebP 支持时会出现：
   - gd_info()["WebP Support"] 为 false
   - function_exists("imagewebp") 为 false
3. 正确修复方式是改运维仓库 Dockerfile 并重建镜像，不要临时进入运行中容器 apt install。
4. web 和 cron 共用同一套 PHP 镜像，发布时要确保 youdianse-dev-php-web 和 youdianse-dev-php-cron 都使用新镜像。

测试环境信息：
- 运维仓库本地路径：<LOCAL_DEV_REPO_PATH>
- 仓库分支：dev
- 测试服务器：root@38.92.8.34
- 服务器运维目录：/opt/docker-youdianse-php
- Web 容器：youdianse-dev-php-web
- Cron 容器：youdianse-dev-php-cron
- Nginx 容器：youdianse-dev-php-nginx
- PHP 镜像标签格式：youdianse-php:dev-<业务短提交>
- Dockerfile：php-web.Dockerfile
- CICD Web 测试访问地址：https://cicd.youdianse-test.xyz
- Telegram token/chat_id 来源：服务器本地 cicd-web/runtime/secrets.env 或 cicd-web/config/settings.json；不要打印敏感值。

目标：
1. 在 dev 分支的 php-web.Dockerfile 中安装 WebP 编译依赖。
2. 编译 PHP GD 时启用 WebP。
3. 提交并推送 dev 分支。
4. 测试服务器拉取 dev 后，用当前业务代码 git id 重建并重启测试容器。
5. 验证 youdianse-dev-php-web：
   - gd_info()["WebP Support"] = true
   - imagewebp() 存在
   - imagewebp() 能实际写出 .webp 文件
6. 验证 youdianse-dev-php-cron 同样支持 WebP。
7. 验证发布健康检查通过。
8. 最后发送 Telegram 普通文本通知，并附上本提示词文档。

边界要求：
1. 只操作测试环境，不要改线上 main 分支，不要登录线上服务器。
2. 不要打印服务器密码、SSH key、Telegram token、chat_id、发布密码、私钥。
3. 不要把任何密码、token、chat_id 写进 Git。
4. 不要直接修改运行中容器作为最终方案，必须通过 Dockerfile + 镜像重建固化。
5. 不要改 PHP 版本、Phalcon 版本、业务代码、nginx 配置、env 配置。
6. 如果服务器工作区有非本次操作产生的改动，先汇报，不要覆盖。

本地确认：
1. 进入运维仓库：
   cd <LOCAL_DEV_REPO_PATH>
2. 确认分支和工作区：
   git status --short --branch
   git branch --show-current
   git rev-parse --short HEAD
3. 确认当前 Dockerfile 相关内容：
   rg -n "libwebp|docker-php-ext-configure gd|libpng-dev|libjpeg-dev|libfreetype6-dev" php-web.Dockerfile

本地修改：
1. 修改 php-web.Dockerfile 的 apt 依赖行，确保包含：
   libwebp-dev
2. 修改 GD configure 行，确保包含：
   --with-webp
3. 期望结果类似：
   libzip-dev libpng-dev libjpeg-dev libfreetype6-dev libwebp-dev \

   RUN docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
       && docker-php-ext-install -j"$(nproc)" \
       pdo_mysql mysqli zip gd bcmath opcache sockets intl

本地验证：
1. Dockerfile 语法和 diff 检查：
   git diff -- php-web.Dockerfile
   git diff --check
2. 确认只改了预期文件：
   git status --short
   git diff --stat

提交推送：
1. 提交：
   git add php-web.Dockerfile
   git commit -m "Enable GD WebP support"
2. 推送：
   git push origin dev
3. 记录提交号：
   git rev-parse --short HEAD

测试服务器部署：
1. SSH 登录测试服务器：
   ssh root@38.92.8.34
2. 进入运维目录：
   cd /opt/docker-youdianse-php
3. 确认当前状态：
   git status --short --branch
   git rev-parse --short HEAD
4. 拉取 dev：
   git pull --ff-only origin dev
5. 确认 Dockerfile 已包含 WebP：
   rg -n "libwebp|docker-php-ext-configure gd|--with-webp" php-web.Dockerfile
6. 获取当前测试环境业务代码提交号。如果服务器有业务仓库目录，优先使用当前已部署业务仓库的 HEAD：
   git -C src/youdianse-php rev-parse HEAD
   git -C src/youdianse-php rev-parse --short HEAD
7. 用当前业务 git id 重建并发布，避免误切业务版本：
   python3 cicd-web.py deploy --git-id <BUSINESS_GIT_SHA> --with-cron
8. 构建日志中重点确认 GD configure 有 WebP：
   checking for libwebp... yes
9. 发布完成后确认容器运行：
   docker ps --format "{{.Names}} {{.Image}} {{.Status}}" | grep -E "youdianse-dev-php-(web|cron|nginx)"

容器验证：
1. 验证 Web 容器：
   docker exec youdianse-dev-php-web php -r '$gd=gd_info(); echo "GD WebP Support: ".(($gd["WebP Support"] ?? false) ? "yes" : "no")."\n"; echo "imagewebp: ".(function_exists("imagewebp") ? "yes" : "no")."\n"; $im=imagecreatetruecolor(2,2); $ok=imagewebp($im, "/tmp/gd-webp-test.webp"); imagedestroy($im); echo "imagewebp_write: ".($ok && is_file("/tmp/gd-webp-test.webp") ? "yes" : "no")."\n"; @unlink("/tmp/gd-webp-test.webp");'
2. 预期输出：
   GD WebP Support: yes
   imagewebp: yes
   imagewebp_write: yes
3. 验证 Cron 容器：
   docker exec youdianse-dev-php-cron php -r '$gd=gd_info(); echo "cron GD WebP Support: ".(($gd["WebP Support"] ?? false) ? "yes" : "no")."\n"; echo "cron imagewebp: ".(function_exists("imagewebp") ? "yes" : "no")."\n";'
4. 预期输出：
   cron GD WebP Support: yes
   cron imagewebp: yes

健康检查：
1. 如果 cicd-web.py deploy 已完成健康检查，确认日志里有：
   - HTTP: 200
   - Session writable
   - Redis open
   - MongoDB open
   - 总体 SUCCESS
2. 如需手动补充检查，执行：
   docker compose ps
   docker logs --tail 100 youdianse-dev-php-web
   docker logs --tail 100 youdianse-dev-php-nginx

Telegram 通知：
1. 发送前不要打印 token/chat_id。
2. 优先从服务器本地 cicd-web/runtime/secrets.env 或 cicd-web/config/settings.json 读取 Telegram 配置。
3. 发送普通文本消息，并把本提示词文档作为文件附件发到运维飞机群。
4. 消息模板：

游点涩测试环境 GD WebP 支持改造完成
<当前北京时间>

本次更新：为测试环境 PHP GD 扩展补齐 WebP 支持，用于缩略图等图片处理需求。
改动内容：
1. php-web.Dockerfile 增加 libwebp-dev 编译依赖。
2. docker-php-ext-configure gd 增加 --with-webp。
3. 已重建测试镜像并重启 youdianse-dev-php-web / youdianse-dev-php-cron。

验证结果：
GD WebP Support: yes
imagewebp: yes
imagewebp_write: yes
cron GD WebP Support: yes
cron imagewebp: yes

测试环境健康检查：通过。
文档附件：2026-07-03-0900-【架构改造】测试环境GD-WebP支持改造提示词.md

@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre

完成后汇报：
1. 本地 dev 分支提交号。
2. 测试服务器是否已拉到最新 dev。
3. 测试环境使用的业务代码 git id。
4. 新镜像标签。
5. Web 容器 GD WebP/imagewebp/write 测试结果。
6. Cron 容器 GD WebP/imagewebp 测试结果。
7. 健康检查是否通过。
8. Telegram 文本和文档附件是否发送成功。
```

## 本次测试环境已完成结果

```text
运维仓库提交：32ad96d Enable GD WebP support
改动文件：php-web.Dockerfile
业务代码 git id：ebfb527fab781a1097b6ecd0fc2ed1324c051756
测试镜像：youdianse-php:dev-ebfb527fab78
测试容器：
- youdianse-dev-php-web
- youdianse-dev-php-cron
- youdianse-dev-php-nginx

验证结果：
GD WebP Support: yes
imagewebp: yes
imagewebp_write: yes
cron GD WebP Support: yes
cron imagewebp: yes
```
