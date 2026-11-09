---
id: "doc-c6fe079f3d21"
title: "测试 H5/PC 随机页面 F12 红色报错收口"
date: "2026-08-06T20:36:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_2036-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2F12%E7%BA%A2%E8%89%B2%E6%8A%A5%E9%94%99%E6%94%B6%E5%8F%A3.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_2036-【修复Bug+验证记录】测试H5-PC随机页面F12红色报错收口.md"
sourceSha256: "84f9532e79fedad61ccd2344d49949b9cb8f924865ac575ca965b7a911e270df"
sourceSystem: "project-doc"
---

# 测试 H5/PC 随机页面 F12 红色报错收口

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608062036-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%B5%8B%E8%AF%95%20H5-PC%20%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2%20F12%20%E7%BA%A2%E8%89%B2%E6%8A%A5%E9%94%99%E6%94%B6%E5%8F%A3.md)

> 整理日期：2026-08-06 20:36｜日期依据：文件名日期

环境标签：测试环境 / 游点涩 / H5-PC / 前端静态资源 / 后台图片资源 / Service Worker

## 用户要求

- 读取 `doc` 里面补资源的文档。
- 使用 `workbench`，读取之前操作留下的 `doc` 文档。
- 每步操作都发群通知。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里。
- 处理测试环境 PC/H5 随机页面打开时浏览器控制台大量红色报错。

## 已读取依据

- `AGENTS.md`
- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_INDEX.md`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/NOTIFICATION_TARGETS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`
- `devops/ai_context/youdianse_h5_s3_rollout.md`
- `devops/python/ben-bot/doc/2026-08-06_1800-【架构调整+回退】测试H5-PC静态资源恢复AWS老S3.md`
- `devops/python/ben-bot/doc/` 下包含“补资源 / CloudFront / uploads / cdn_image / workbox / headico”的历史记录

## 根因

1. 旧浏览器 Service Worker 仍在请求过期的 `workbox-9031cd6a.js`。
   当前站点只存在新的 workbox 文件；旧 `workbox-9031cd6a.js` 在 Nuxt fallback 下可能返回 HTML，旧 SW 运行时图片缓存继续写入浏览器缓存，控制台出现多条 `QuotaExceededError`。

2. PC 页面存在 `/images/aside/*.svg` 历史引用。
   当前 PC AWS S3 中没有这些对象，PC 同源路径代理到 S3 后返回 403；H5 同源路径此前会回落 HTML。

3. 首页游戏“欲落降临”存在一条历史上传图。
   游戏 `_id=456` 的 `cover=/uploads/2026-03-17/b6a1bed72f2cf11d344b08117cc792b2.jpg` 经当前测试后台图片域 `d1rct3ku9n07y3.cloudfront.net` 返回 404，但旧 AWS/CloudFront `d391me9s8n5j5s.cloudfront.net` 同路径返回 200。

4. 本机浏览器控制插件不可用。
   本轮无法直接驱动 in-app browser 采集 DevTools console，因此使用 HTTP、Content-Type、SSR HTML 和页面资源抽样进行验证。

## 变更

### 1. 测试宝塔 Nginx

目标文件：

- `/www/server/panel/vhost/nginx/h5.youdianse-test.xyz.conf`
- `/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf`

增加：

- `location = /sw.js`：返回 no-store 的清理脚本，激活后清理 Cache Storage 并注销旧 Service Worker。
- `location ~ ^/workbox-[0-9a-f]+\.js$`：返回 no-store 的 no-op Workbox AMD 模块，避免旧 SW 引用过期 workbox 时拿到 HTML。
- `location ^~ /images/aside/`：返回 Nginx `empty_gif`，消除历史缺失 aside 图标引起的 403/HTML fallback 红错。

远端备份：

- `/root/.codex-backup/test-youdianse-red-errors-20260806202548`
- `/root/.codex-backup/test-youdianse-aside-prefix-20260806202729`

### 2. 测试 PC 发布模板

同步修改本地模板，避免下次机器人发布 PC 后覆盖掉本次 Nginx 修复：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf`

### 3. 测试后台单条游戏数据

只修复一条确认坏链：

- 集合模型：`App\Models\Common\GameModel`
- 记录：`_id=456`
- 标题：`欲落降临`
- 字段：`cover`
- 原值：相对 `/uploads/2026-03-17/b6a1bed72f2cf11d344b08117cc792b2.jpg`，经 d1 返回 404
- 新值：旧 AWS/CloudFront 完整 URL `https://d391me9s8n5j5s.cloudfront.net/uploads/2026-03-17/b6a1bed72f2cf11d344b08117cc792b2.jpg`

数据备份：

- PHP 容器内 `/var/www/html/youdianse-php/runtime/logs/game_456_cover_backup_20260806_203349.json`

说明：未批量替换 d1/d391，也未修改 `cdn_image` 主配置。抽样显示 d1 当前仍是测试 uploads 主展示域，大多数上传图正常；全局切换到 d391 会引入更多不可访问资源。

## 验证

### Nginx

- `nginx -t` 通过。
- Nginx reload 成功。

### 关键 URL

- `https://h5.youdianse-test.xyz/sw.js`：`200 application/javascript`
- `https://pc.youdianse-test.xyz/sw.js`：`200 application/javascript`
- `https://h5.youdianse-test.xyz/workbox-9031cd6a.js`：`200 application/javascript`
- `https://pc.youdianse-test.xyz/workbox-9031cd6a.js`：`200 application/javascript`
- `https://h5.youdianse-test.xyz/images/aside/home.svg`：`200 image/gif`
- `https://pc.youdianse-test.xyz/images/aside/home.svg`：`200 image/gif`

### 页面

- `https://h5.youdianse-test.xyz/`：200
- `https://h5.youdianse-test.xyz/bonus`：200
- `https://pc.youdianse-test.xyz/`：200
- `https://pc.youdianse-test.xyz/bonus`：200

### 资源抽样

最终抽样 4 个页面共 335 个资源：

- 200：332
- 403：3
- 排除裸 S3/CloudFront 根地址预连接后，坏资源：0

被排除的 403 是裸域名预连接/根地址，不是页面实际图片、JS、CSS 资源：

- `https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com`
- `https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com`
- `https://d391me9s8n5j5s.cloudfront.net`

### 单条坏图

- 原 d1 链：404
- 新 d391 链：200 image/jpeg
- H5/PC 首页 SSR 已不再包含该 d1 404 链，已包含新 d391 可访问链。

## 群通知

本任务每步已同步：

- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容仅包含步骤、结论、备份路径和验证结果；未发送密码、token、Secret、私钥、完整 `.env` 或数据库连接串。

## 回滚

1. Nginx 回滚：
   使用远端备份目录中的对应 `h5.youdianse-test.xyz.conf`、`pc.youdianse-test.xyz.conf` 覆盖回 `/www/server/panel/vhost/nginx/`，执行 `nginx -t && /etc/init.d/nginx reload`。

2. 游戏数据回滚：
   使用 PHP 容器内备份 `game_456_cover_backup_20260806_203349.json` 中的原 `cover` 值恢复 `_id=456`，再清缓存并复验首页。

## 结论

测试环境 H5/PC 随机页面主要 F12 红色报错已收口。旧 Service Worker/workbox、PC aside 缺失资源、首页单条历史坏图均已处理并验证通过。
