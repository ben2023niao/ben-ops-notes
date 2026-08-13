---
id: "doc-ee68f341fd1a"
title: "SEO异常验证异常验证 canonical 指向 pc 测试域名 紧急修复与全量验证"
date: "2026-08-14T15:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-14_1540-%E3%80%90%E7%B4%A7%E6%80%A5%E4%BF%AE%E5%A4%8D%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91SEO%20canonical%E6%8C%87%E5%90%91pc%E6%B5%8B%E8%AF%95%E5%9F%9F%E5%90%8D%E4%BF%AE%E5%A4%8D%E4%B8%8E%E5%85%A8%E9%87%8F%E9%AA%8C%E8%AF%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-14_1540-【紧急修复+验证记录】SEO canonical指向pc测试域名修复与全量验证.md"
sourceSha256: "2e62d574f154499144a08b9251c62e17d710fef6b27795c99511f41608a3b541"
sourceSystem: "project-doc"
---

# SEO异常验证异常验证 canonical 指向 pc 测试域名 紧急修复与全量验证

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-14_1540-【紧急修复+验证记录】SEO canonical指向pc测试域名修复与全量验证.md`

> 整理日期：2026-08-14 15:40｜日期依据：文件名日期

环境标签：线上环境 / SEO异常验证 / canonical / H5 / PC / 16.208.38.88 / 宝塔

时间：2026-08-14 15:40（Asia/Manila）

## 现象

主站每个页面的 canonical 指向 `pc.yds-pc-h5-01.cc`（该域名全站 noindex），可能导致 Google 整体不收录；Hector 要求全部恢复为 `https://www.youdianse.com`。

## 根因

1. 发布脚本 `线上环境-游点涩-新h5-发版` / `新pc-发版` 的 `NUXT_PUBLIC_SITE_URL` 分别写死为 `https://h5.yds-pc-h5-01.cc` / `https://pc.yds-pc-h5-01.cc`，Nuxt 用它生成 canonical（前端已内置归一化：youdianse.com/www → https://www.youdianse.com，但 pc./h5. 域名不会被归一化）。
2. noindex 按请求 Host 白名单判定（仅 youdianse.com / www / h5.youdianse.com 可收录）；CloudFront 回源 Host=pc.yds-pc-h5-01.cc 导致判 noindex。

## 修复

### 发布脚本（机器人侧）

- `线上环境-游点涩-新h5-发版/youdianse_prod_18game_h5_client.py`：`NUXT_PUBLIC_SITE_URL` → `https://www.youdianse.com`
- `线上环境-游点涩-新pc-发版/youdianse_prod_18game_pc_client.py`：`NUXT_PUBLIC_SITE_URL` → `https://www.youdianse.com`
- ben-bot 容器重建。

### 重新发布

| 目标 | 版本 | 结果 |
| --- | --- | --- |
| 新服务器 H5（16.208.38.88:3003） | main 64d3bdb | ✅ 容器已启动 |
| 新服务器 PC（16.208.38.88:3004） | dev cbaacc2 | ✅ 容器已启动 |
| 宝塔 H5（13.208.101.121:3003，配置本就 https://youdianse.com） | main 64d3bdb | ✅ 容器已启动 |

## 验证

### canonical（直连源站，100 个域名逐条发群）

- 93 个域名 canonical = `https://www.youdianse.com/` ✅
- 6 个为 301 跳转域名（yds-pc-h5-01/02/03.cc + www），跳转正常，落地页 canonical 正确
- `ops.youdianse.com`：已加入 nginx 但无 SSL 证书，443 直连失败（异常项）

### 手机→H5 / 电脑→PC 分流

- 93 个域名正确（手机 youdianse_prod_h5、电脑 youdianse_prod_pc）
- 其余为 301 跳转/无证书域名

### robots

- 可收录白名单（设计）：youdianse.com / www.youdianse.com / h5.youdianse.com；手机（H5 构建）为 `index, follow`
- 宝塔 H5（Host=www.youdianse.com）：`index, follow` + canonical www ✅
- 其余域名 noindex（镜像/落地页，设计如此）

## 异常/待办清单

1. `ops.youdianse.com`：已加入 nginx 但无证书（live/ 目录缺失），443 失败——需签发证书或确认是否保留。
2. PC 端 SSR robots：youdianse.com/www/h5 电脑（PC 构建）SSR 输出 noindex（SPA 客户端会按 Host 修正，需前端确认 SSR 默认 meta 是否也要改成 index）。
3. CF 回源 Host：回源 Host 需为 youdianse.com/www 之一，否则经 CDN 的请求仍按 Host 判 noindex（运营正在改回源，改完复验）。

## 结论

- canonical 已全部恢复为 https://www.youdianse.com（新 H5/新 PC/宝塔 H5 三个环境均重新发布并验证）。
- 100 个域名逐条验证结果已发群；异常 3 项列明待办。

## 追加：youdianse 系 robots 全量 index,follow（2026-08-14）

- 需求：只要是 youdianse 的域名，robots 都必须是 index,follow（Hector：游戏库/首页等都被误判 noindex）。
- 实现（nginx，参照 18game pc18game.shop 的 nginx 模式）：
  - `10-youdianse-prod-maps.conf`：新增 `map $host $robots_meta_repl`（Host 含 youdianse → index,follow）与 `map $host $robots_x_tag`（X-Robots-Tag 响应头）。
  - `20-youdianse-prod-unified.conf` `location /`：`sub_filter` 把 `noindex, nofollow` / `noindex, follow` 改写为 `index, follow`；`proxy_set_header Accept-Encoding ""`（禁用上游 gzip 才能 sub_filter）；`proxy_hide_header X-Robots-Tag`（访问策略验证应用自带 noindex，避免冲突）+ `add_header X-Robots-Tag $robots_x_tag always`。
- 验证（直连源站全量巡检 93 个域名，汇总一条发群）：
  - youdianse 系 9 个：全部 index,follow ✅（youdianse.com / www / h5 / new / h5-001 / h5.youdianse-main.xyz / youdianse-abc.com / youdianse.me / youdianse.one / youdianse.vip）
  - 非 youdianse 84 个：全部 noindex ✅（渠道/镜像域名）
  - canonical www.youdianse.com：87 个正常（6 个为 yds-pc-h5 301 跳转域名）
  - 说明：h5.yodianse.com（yodianse 拼写）按规则保持 noindex，如需收录请确认。

## 追加：SEO异常验证 最终需求（仅 *.youdianse.com 收录 + youdianse 根域/子域 301 到 www）（2026-08-15）

- 最终需求（Hector/Kermit/陈岩 + 文档「游点涩基础谷歌SEO异常验证操作清单」）：
  - index,follow 仅限 `*.youdianse.com`（根域 + 全部子域）；
  - youdianse.com 裸域 + 所有子域（除 www）301 → `https://www.youdianse.com`；
  - 其余落地页/渠道域名（含 youdianse-abc.com、youdianse.me/one/vip、*.youdianse-main.xyz）一律 noindex,nofollow。
- 实现：
  - `10-youdianse-prod-maps.conf`：robots_meta_repl / robots_x_tag 匹配范围由 `~*youdianse` 收窄为 精确 youdianse.com + `~*\.youdianse\.com$`；新增 `youdianse_main_redirect` map（www=0、裸域/子域=1）。
  - `20-youdianse-prod-unified.conf`：`location /` 顶部 `if ($youdianse_main_redirect = 1) return 301 https://www.youdianse.com$request_uri;`。
- 验证（直连源站全量巡检 93 域名，汇总一条发群）：
  - www.youdianse.com：200 + index,follow ✅
  - h5/new.youdianse.com：301 → https://www.youdianse.com（路径保留）✅
  - youdianse.com 裸域：301 → www ✅；ops.youdianse.com 公网 301 → www ✅
  - 非 youdianse 84 个：noindex,nofollow ✅；落地页 youdianse-abc/me/one/vip/*.youdianse-main.xyz 已改回 noindex ✅
  - 6 个 yds-pc-h5 301 跳转域名正常 ✅；无异常。
