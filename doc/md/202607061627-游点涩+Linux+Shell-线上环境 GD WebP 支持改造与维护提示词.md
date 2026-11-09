---
id: "doc-d18bc9f92382"
title: "线上环境 GD WebP 支持改造与维护提示词"
date: "2026-07-06T16:27:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "Nginx", "MySQL", "Redis"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-06-1627-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83GD-WebP%E6%94%AF%E6%8C%81%E6%94%B9%E9%80%A0%E7%BB%B4%E6%8A%A4%E6%8F%90%E7%A4%BA%E8%AF%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md"
sourceSha256: "6b6c28040cbfab5bba8afd0565b64f082cc65f093602e9c15214cbadc498f0fb"
sourceSystem: "project-doc"
---

# 线上环境 GD WebP 支持改造与维护提示词

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607061627-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20GD%20WebP%20%E6%94%AF%E6%8C%81%E6%94%B9%E9%80%A0%E4%B8%8E%E7%BB%B4%E6%8A%A4%E6%8F%90%E7%A4%BA%E8%AF%8D.md)

> 整理日期：2026-07-06 16:27｜日期依据：文件名日期

文档日期：2026-07-06 16:27
环境：游点涩线上环境（main 分支）
分类：架构改造

用途：把这份提示词发给 AI 或运维同学，用于复刻、发布、验证和维护“游点涩线上 PHP GD 扩展增加 WebP 支持”改造。这个改造用于缩略图等图片处理需求，目标是让 `youdianse-main-php-web` 和共用镜像的 `youdianse-main-php-cron` 都支持 `imagewebp()`。

文件位置：

```text
docs/2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md
```

## 直接可用提示词

把下面整段提示词发给 AI，让 AI 先确认当前环境和分支，再执行。

```text
你是运维自动化助手。我要在“游点涩线上环境 / main 分支”给 PHP GD 扩展补齐 WebP 支持，用于缩略图等图片处理需求。

核心背景：
1. 业务需要生成缩略图，GD 库是 PHP 常用图片处理扩展。
2. 容器里 GD 已编译但缺少 WebP 支持时，会出现：
   - gd_info()["WebP Support"] 为 false
   - function_exists("imagewebp") 为 false
3. 正确修复方式是改运维仓库 Dockerfile 并重建镜像，不要临时进入运行中容器 apt install。
4. web 和 cron 共用同一套 PHP 镜像，发布时要确保 youdianse-main-php-web 和 youdianse-main-php-cron 都使用新镜像。

线上环境信息：
- 运维仓库本地路径：/Users/ben/Documents/ben/docker/main/docker-youdianse-php
- 仓库分支：main
- 后端服务器：ubuntu@16.209.16.108
- 服务器运维目录：/opt/docker-youdianse-php
- Web 容器：youdianse-main-php-web
- Cron 容器：youdianse-main-php-cron
- Nginx 容器：youdianse-main-php-nginx
- PHP 镜像标签格式：youdianse-php:main-<业务短提交>
- Dockerfile：php-web.Dockerfile
- CICD Web 线上访问地址：https://cicd.youdianse-main.xyz
- Telegram token/chat_id 来源：服务器本地 cicd-web/runtime/secrets.env 或 cicd-web/config/settings.json；不要打印敏感值。

目标：
1. 在 main 分支的 php-web.Dockerfile 中安装 WebP 编译依赖。
2. 编译 PHP GD 时启用 WebP。
3. 提交并推送 main 分支。
4. 线上后端服务器拉取 main 后，用当前业务代码 git id 或 CICD Web 手动发布重建镜像。
5. 验证 youdianse-main-php-web：
   - gd_info()["WebP Support"] = true
   - imagewebp() 存在
   - imagewebp() 能实际写出 .webp 文件
6. 验证 youdianse-main-php-cron 同样支持 WebP。
7. 验证发布健康检查通过。
8. 发送 Telegram 普通文本通知，并附上本提示词文档。

边界要求：
1. 只操作线上 main 分支和线上后端服务器，不要误切测试 dev 分支。
2. 不要打印服务器密码、SSH key、Telegram token、chat_id、发布密码、私钥。
3. 不要把任何密码、token、chat_id 写进 Git。
4. 不要直接修改运行中容器作为最终方案，必须通过 Dockerfile + 镜像重建固化。
5. 不要改 PHP 版本、Phalcon 版本、业务代码、nginx 配置、env 配置。
6. 如果本地或服务器工作区有非本次操作产生的改动，先汇报，不要覆盖。

本地确认：
1. 进入运维仓库：
   cd /Users/ben/Documents/ben/docker/main/docker-youdianse-php
2. 确认分支和工作区：
   git status --short --branch
   git branch --show-current
   git rev-parse --short HEAD
3. 确认当前 Dockerfile 相关内容：
   rg -n "libwebp|docker-php-ext-configure gd|libpng-dev|libjpeg-dev|libfreetype6-dev|--with-webp" php-web.Dockerfile

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
1. Dockerfile 和文档检查：
   rg -n "libwebp|--with-webp|docker-php-ext-configure gd" php-web.Dockerfile
   git diff -- php-web.Dockerfile docs/2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md
   git diff --check
2. 确认只改了预期文件：
   git status --short
   git diff --stat

提交推送：
1. 提交：
   git add php-web.Dockerfile docs/2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md
   git commit -m "Enable production GD WebP support"
2. 推送：
   git push origin main
3. 记录提交号：
   git rev-parse --short HEAD

线上服务器部署准备：
1. SSH 登录线上后端服务器：
   ssh -i id_rsa ubuntu@16.209.16.108
2. 进入运维目录：
   cd /opt/docker-youdianse-php
3. 确认当前状态：
   sudo git status --short --branch
   sudo git rev-parse --short HEAD
4. 拉取 main：
   sudo git pull --ff-only origin main
5. 确认 Dockerfile 已包含 WebP：
   rg -n "libwebp|docker-php-ext-configure gd|--with-webp" php-web.Dockerfile

发布方式：
1. 优先使用 CICD Web 页面手动发布，避免误切业务版本：
   https://cicd.youdianse-main.xyz
2. 如果需要命令行发布，先获取当前业务代码提交号：
   git -C src/youdianse-php rev-parse HEAD
   git -C src/youdianse-php rev-parse --short HEAD
3. 用当前业务 git id 重建并发布：
   sudo cicd-web/runtime/venv/bin/python cicd-web.py deploy --git-id <BUSINESS_GIT_SHA> --with-cron
4. 构建日志中重点确认 GD configure 有 WebP：
   docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp
   checking for libwebp... yes
5. 发布完成后确认容器运行：
   sudo docker ps --format "{{.Names}} {{.Image}} {{.Status}}" | grep -E "youdianse-main-php-(web|cron|nginx)"

容器验证：
1. 验证 Web 容器：
   sudo docker exec youdianse-main-php-web php -r '$gd=gd_info(); echo "GD WebP Support: ".(($gd["WebP Support"] ?? false) ? "yes" : "no")."\n"; echo "imagewebp: ".(function_exists("imagewebp") ? "yes" : "no")."\n"; $im=imagecreatetruecolor(2,2); $ok=imagewebp($im, "/tmp/gd-webp-test.webp"); imagedestroy($im); echo "imagewebp_write: ".($ok && is_file("/tmp/gd-webp-test.webp") ? "yes" : "no")."\n"; @unlink("/tmp/gd-webp-test.webp");'
2. 预期输出：
   GD WebP Support: yes
   imagewebp: yes
   imagewebp_write: yes
3. 验证 Cron 容器：
   sudo docker exec youdianse-main-php-cron php -r '$gd=gd_info(); echo "cron GD WebP Support: ".(($gd["WebP Support"] ?? false) ? "yes" : "no")."\n"; echo "cron imagewebp: ".(function_exists("imagewebp") ? "yes" : "no")."\n";'
4. 预期输出：
   cron GD WebP Support: yes
   cron imagewebp: yes

健康检查：
1. 如果 CICD Web 发布已完成健康检查，确认日志里有：
   - HTTP: 200
   - Session writable
   - Redis open
   - MongoDB open
   - 总体 SUCCESS
2. 如需手动补充检查：
   curl -sS -o /tmp/youdianse-admin-health.html -w "admin_http:%{http_code} time:%{time_total}\n" http://203.0.113.1:8088/admin1866/login
   sudo docker compose ps
   sudo docker logs --tail 100 youdianse-main-php-web
   sudo docker logs --tail 100 youdianse-main-php-nginx

Telegram 通知：
1. 发送前不要打印 token/chat_id。
2. 优先使用服务器本地 cicd-web 的 Telegram 配置。
3. 发送普通文本消息，并把本提示词文档作为文件附件发到运维飞机群。
4. 消息模板：

游点涩线上 GD WebP 支持改造完成
<当前北京时间>

本次更新：为线上 PHP GD 扩展补齐 WebP 支持，用于缩略图等图片处理需求。
改动内容：
1. php-web.Dockerfile 增加 libwebp-dev 编译依赖。
2. docker-php-ext-configure gd 增加 --with-webp。
3. 已重建线上镜像并重启 youdianse-main-php-web / youdianse-main-php-cron。

验证结果：
GD WebP Support: yes
imagewebp: yes
imagewebp_write: yes
cron GD WebP Support: yes
cron imagewebp: yes

线上健康检查：通过。
文档附件：2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md

@Ben_Bird @jett_yunwei @Kermit0824 @melo_sre @Daviea2

完成后汇报：
1. 本地 main 分支提交号。
2. 线上服务器是否已拉到最新 main。
3. 线上环境使用的业务代码 git id。
4. 新镜像标签。
5. Web 容器 GD WebP/imagewebp/write 测试结果。
6. Cron 容器 GD WebP/imagewebp 测试结果。
7. 健康检查是否通过。
8. Telegram 文本和文档附件是否发送成功。
```

## 本次线上改造记录

```text
改动文件：
- php-web.Dockerfile
- docs/2026-07-06-1627-【架构改造】线上环境GD-WebP支持改造维护提示词.md

Dockerfile 改动：
- apt 编译依赖增加 libwebp-dev
- docker-php-ext-configure gd 增加 --with-webp
```

## 维护注意事项

- 这个改造只有在重新构建 PHP 镜像并重启 `web` / `cron` 后才会在容器中生效。
- 如果只是 `git pull` 到线上服务器但没有发布，新容器不会自动具备 WebP 支持。
- 不要在运行中的容器里临时 `apt install libwebp-dev` 作为最终方案。
- `web` 和 `cron` 共用同一镜像，验证时两个容器都要检查。
- 发送群通知时不要暴露任何 token、密码、私钥或含凭据的 Git URL。
