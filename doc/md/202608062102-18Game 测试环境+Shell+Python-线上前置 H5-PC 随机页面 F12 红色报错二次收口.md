---
id: "doc-32a707bd1af7"
title: "线上前置 H5/PC 随机页面 F12 红色报错二次收口"
date: "2026-08-06T21:02:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_2102-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AEH5-PC%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2F12%E7%BA%A2%E8%89%B2%E6%8A%A5%E9%94%99%E4%BA%8C%E6%AC%A1%E6%94%B6%E5%8F%A3.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_2102-【修复Bug+验证记录】线上前置H5-PC随机页面F12红色报错二次收口.md"
sourceSha256: "57d8463ebc38e492d8b194d937f98673d3f994ddd61dfdc501e06ca0db1e299c"
sourceSystem: "project-doc"
---

# 线上前置 H5/PC 随机页面 F12 红色报错二次收口

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_2102-【修复Bug+验证记录】线上前置H5-PC随机页面F12红色报错二次收口.md`

> 整理日期：2026-08-06 21:02｜日期依据：文件名日期

环境标签：线上前置 / 游点涩 / H5-PC / Nginx / AWS S3 / Service Worker / 前端静态资源

## 用户要求

- 读取 `doc` 里面补资源的文档。
- 使用 `workbench`，读取之前操作留下的 `doc` 文档。
- 每步操作都发群通知。
- 参考刚刚测试环境的修复过程。
- 处理前置环境 PC/H5 随机页面打开时浏览器控制台大量红色报错。
- 操作完成后先验证，再汇总文档，并把汇总和文档发群里。

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
- `devops/python/ben-bot/doc/2026-08-06_2036-【修复Bug+验证记录】测试H5-PC随机页面F12红色报错收口.md`
- `devops/python/ben-bot/doc/2026-08-06_2010-【修复Bug+验证记录】线上前置yiyi0620前端F12报错收尾.md`
- `devops/python/ben-bot/doc/2026-08-06_1952-【配置部署+机器人优化】yiyi0620证书与ben-bot前端发版展示收尾.md`
- `devops/python/ben-bot/doc/` 下包含“补资源 / workbox / uploads / CloudFront / 缺图 / 前置”的历史记录

## 只读复现

前置入口：

- `https://h5.yiyi0620.com`
- `https://pc.yiyi0620.com`

抽样页面：

- `/`
- `/bonus`
- `/game`
- `/community`

复现结果：

- H5/PC 页面入口均返回 200。
- H5/PC 旧 `workbox-9031cd6a.js`、`workbox-9031cd6b.js` 返回 `200 text/html`，容易让旧浏览器 Service Worker 继续执行异常逻辑。
- H5/PC `/images/aside/home.svg`、`game.svg`、`aboutus.svg` 返回 403。
- H5 根路径 `/footer-logo.webp`、`/placeholder.webp` 返回 403。
- 初始抽样 210 个资源，发现 12 个需处理项。

## 根因

1. 旧浏览器 Service Worker 仍可能请求已不存在的历史 workbox 文件。
   这些路径在前置 Nuxt fallback 下返回 HTML，不是 JavaScript；旧 SW 加载后容易在浏览器控制台形成红色错误。

2. H5/PC 页面或缓存中存在 `/images/aside/*.svg` 历史引用。
   当前 H5/PC preprod AWS S3 桶没有这些对象，Nginx 代理到 S3 后返回 403。

3. H5 根路径 `footer-logo.webp`、`placeholder.webp` 不是 H5 桶里的真实对象。
   H5 桶有 `/images/placeholder.png`，但没有这两个根路径 webp；为避免红错，本轮使用透明图兜底。

说明：本轮未修改业务接口、未修改线上后台数据、未修改 `cdn_image`，也未批量替换 uploads 域名。

## 变更

### 日本前置 Nginx

目标文件：

- `/etc/nginx/conf.d/10-youdianse-preprod-frontends.conf`

4 个 server block 均增加：

- `location = /sw.js`
  - 返回 no-store 清理脚本。
  - 激活后清 Cache Storage，并注销旧 Service Worker。

- `location ~ ^/workbox-[0-9a-f]+\.js$`
  - 返回 no-store 的 no-op Workbox AMD 模块。
  - 避免旧 workbox 请求拿到 HTML。

- `location ^~ /images/aside/`
  - 返回 Nginx `empty_gif`。
  - 消除历史缺失 aside 图标带来的 403。

H5 的 80/443 server block 额外增加：

- `location ~ ^/(footer-logo|placeholder)\.webp$`
  - 返回 Nginx `empty_gif`。
  - 消除 H5 根路径历史 webp 缺失 403。

远端备份：

- `/root/.codex-backup/preprod-yiyi0620-random-f12-fix-20260806205920`

### 本地与 ben-bot 模板

已更新本地模板：

- `devops/python/ben-bot/data/scripts/线上前置-游点涩-前端配置/nginx/youdianse-preprod-frontends.conf`

已同步到 ben-bot 运行机和容器，避免后续机器人发布覆盖本次修复。

ben-bot 运行机备份：

- `/opt/telegram/18game_devops/.codex-backup/preprod-random-f12-template-20260806210203`

容器内验证：

- 修复标记：4 处
- `location = /sw.js`：4 处
- `location ^~ /images/aside/`：4 处

## 验证

### Nginx

- `nginx -t` 通过。
- `systemctl reload nginx` 成功。
- Nginx / Docker 状态均 active。

### 关键 URL

H5：

- `https://h5.yiyi0620.com/sw.js`：`200 application/javascript`
- `https://h5.yiyi0620.com/workbox-9031cd6a.js`：`200 application/javascript`
- `https://h5.yiyi0620.com/workbox-9031cd6b.js`：`200 application/javascript`
- `https://h5.yiyi0620.com/images/aside/home.svg`：`200 image/gif`
- `https://h5.yiyi0620.com/images/aside/game.svg`：`200 image/gif`
- `https://h5.yiyi0620.com/images/aside/aboutus.svg`：`200 image/gif`
- `https://h5.yiyi0620.com/footer-logo.webp`：`200 image/gif`
- `https://h5.yiyi0620.com/placeholder.webp`：`200 image/gif`

PC：

- `https://pc.yiyi0620.com/sw.js`：`200 application/javascript`
- `https://pc.yiyi0620.com/workbox-9031cd6a.js`：`200 application/javascript`
- `https://pc.yiyi0620.com/workbox-9031cd6b.js`：`200 application/javascript`
- `https://pc.yiyi0620.com/images/aside/home.svg`：`200 image/gif`
- `https://pc.yiyi0620.com/images/aside/game.svg`：`200 image/gif`
- `https://pc.yiyi0620.com/images/aside/aboutus.svg`：`200 image/gif`
- `https://pc.yiyi0620.com/footer-logo.webp`：`200`
- `https://pc.yiyi0620.com/placeholder.webp`：`200`

### 页面抽样

页面均返回 200：

- `https://h5.yiyi0620.com/`
- `https://h5.yiyi0620.com/bonus`
- `https://h5.yiyi0620.com/game`
- `https://h5.yiyi0620.com/community`
- `https://pc.yiyi0620.com/`
- `https://pc.yiyi0620.com/bonus`
- `https://pc.yiyi0620.com/game`
- `https://pc.yiyi0620.com/community`

最终资源抽样：

- 总资源：210
- 200：208
- 403：2
- 排除裸 S3/CloudFront 根地址后坏资源：0

说明：保留的 403 是页面里的裸源站根地址预连接/根地址检查，不是实际图片、JS、CSS 或接口资源。

## 群通知

本任务每步已同步：

- `18game运维`
- `18GAME_ 上线群（正式環境）`

已通知步骤：

1. 接收任务与执行顺序。
2. 读取 workbench 和历史文档完成。
3. 只读复现与定位完成。
4. Nginx 备份、部署、`nginx -t`、reload 完成。
5. 关键 URL 和页面资源抽样验证完成。
6. ben-bot 运行机和容器模板持久化同步完成。

通知内容未包含密码、token、Secret、私钥、完整 `.env` 或数据库连接串。

## 回滚

1. 远端 Nginx 回滚：
   使用 `/root/.codex-backup/preprod-yiyi0620-random-f12-fix-20260806205920/10-youdianse-preprod-frontends.conf` 覆盖 `/etc/nginx/conf.d/10-youdianse-preprod-frontends.conf`，然后执行 `nginx -t && systemctl reload nginx`。

2. ben-bot 模板回滚：
   使用 `/opt/telegram/18game_devops/.codex-backup/preprod-random-f12-template-20260806210203/youdianse-preprod-frontends.conf` 覆盖 ben-bot 运行机同名模板，并同步容器。

## 结论

线上前置 H5/PC 随机页面 F12 红色报错残留已二次收口。旧 Service Worker/workbox、`/images/aside/` 缺失图和 H5 根路径历史 webp 缺失均已处理，并完成关键 URL 与 8 个页面资源抽样验证。
