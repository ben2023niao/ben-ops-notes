---
id: "doc-309d077e8fd5"
title: "2026-10-05 香港 nginx 补齐巴西 Worker 的静态规则（PP 游戏进不去修复）"
date: "2026-10-05T11:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1110-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFnginx%E8%A1%A5%E9%BD%90%E5%B7%B4%E8%A5%BFWorker%E9%9D%99%E6%80%81%E8%A7%84%E5%88%99%EF%BC%88PP%E8%BF%9B%E4%B8%8D%E5%8E%BB%E4%BF%AE%E5%A4%8D%EF%BC%89.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1110-【架构改造】香港nginx补齐巴西Worker静态规则（PP进不去修复）.md"
sourceSha256: "e9dc14bc956a797c8da6b8a16c3148ce8dfeadf81c431c0bcb830459e6b810ae"
sourceSystem: "project-doc"
---

# 2026-10-05 香港 nginx 补齐巴西 Worker 的静态规则（PP 游戏进不去修复）

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-10-05-1110-【架构改造】香港nginx补齐巴西Worker静态规则（PP进不去修复）.md`

> 整理日期：2026-10-05 11:10｜日期依据：文件名日期

## 一、问题与结论

```text
用户反馈：PP 游戏进不去、缺东西；巴西那边是 Worker 实现的，香港这边要用 nginx 实现。
给到的地址：
  https://pp-static.k8x2v9.shop/gs2c/common/v5/games-html5/games/vs/vs20starprss/desktop/customizations.info?key=9d6a7

结论：巴西线上静态资源是 Cloudflare Worker 实现的，Worker 里有两段「合并 Nginx 规则」，
      香港 k8x2v9 / m4q7z1 这两个站点是 EdgeOne + 本机 nginx、没有 Worker，
      这两条规则我们没实现 → PP 拉 customizations.info 拿到 403 → 游戏进不去。
      已按同一口径在 nginx 侧补齐，验证通过。
本轮按用户要求不通知飞机群。
```

## 二、定位过程

```text
1) 复现：
   https://pp-static.k8x2v9.shop/…/vs20starprss/desktop/customizations.info?key=9d6a7 -> 403（243B S3 AccessDenied）
   直连源站 nginx（Host 头）同样 403；直连大阪桶 dbqp-s3-pp-static 也是 403 → 源站根本没有这个对象
2) 影响面（standby nginx access.log 统计）：
   customizations.info 累计 155/137/91/49 次 403（vs5lckpnd / vs20starprss / vs10bbhas / vs10spellmastr）
   其它 PP 路径正常：/gs2c/gamename.json 200、/gs2c/html5Game.html 200、/gs2c/saveSettings.do 200
   → 只差这一个文件
3) 巴西做法（把巴西线上 Worker 备份出来看到，dev 版 HK Worker 里也有同样两段）：
   🎯 合并 Nginx 规则 1：url.pathname 以 /customizations.info 结尾 → 直接返回
       200 + 空 body + Content-Type: application/octet-stream + Cache-Control: public, max-age=604800
   🎯 合并 Nginx 规则 2：.js 文件 → 强制 Content-Type: application/javascript; charset=utf-8
4) 三条链路对照（修复前）：
   老域名 pp-static.hkcloudplay01.com（CloudFront 链路）        -> 200
   pp-static.hkcloudplay06.com（Cloudflare + Worker）           -> 200（Worker 规则生效）
   pp-static.{k8x2v9,m4q7z1}.shop（EdgeOne + 本机 nginx）        -> 403 ← 缺这两条规则
```

## 三、实施（nginx 侧补齐）

```text
新增共用片段：docker/deploy/hongkong/nginx-standby-static-extra.conf
  → 部署到 standby /etc/nginx/snippets/dbqp-hk-standby-static-extra.conf
  内容（与 Worker 完全一致）：
    规则 1  location ~ /customizations\.info$   → default_type application/octet-stream +
            Cache-Control public, max-age=604800 + CORS * + return 200（空 body）；OPTIONS → 204
    规则 2  location ~* \.js$                  → proxy_hide_header Content-Type +
            add_header Content-Type "application/javascript; charset=utf-8" + CORS，
            其余照旧回源 dbqp-s3-<前缀>
在两个静态 server 块（m4q7z1 / k8x2v9 的 <前缀>-static.<域>）里 include 该片段。
备份：/etc/nginx/sites-available/dbqp-hk-standby.conf.bak-20261005-pp-static
校验：nginx -t 通过 → systemctl reload nginx
```

## 四、验证

```text
源站直测（Host: pp-static.k8x2v9.shop）
  /…/vs20starprss/desktop/customizations.info?key=9d6a7 -> 200  0B  application/octet-stream
      响应头：Cache-Control: public, max-age=604800 ｜ Access-Control-Allow-Origin: *
  /…/vs10spellmastr/desktop/customizations.info         -> 200  0B  application/octet-stream
  /gs2c/gamename.json                                   -> 200  4306B  application/json（未受影响）
经 EdgeOne（公网，已刷缓存）
  pp-static.m4q7z1.shop / pp-static.k8x2v9.shop 的 vs20starprss、vs5lckpnd
      customizations.info -> 200  0B  application/octet-stream
  /gs2c/gamename.json -> 200 application/json ｜ /gs2c/html5Game.html -> 200 text/html
EdgeOne 缓存刷新：两站点 purge_url（4 个游戏的 customizations.info）
  m4q7z1 JobId 3vt9vtvqn5ri ｜ k8x2v9 JobId 3vt9vu38d6af（FailedList 均为空）
说明：规则 2（.js 强制 MIME）已加载进生效配置（nginx -T 可见），但现网静态桶里暂时找不到
      真实存在的 .js 对象做正向验证（日志里的 .js 请求多为缺失对象 → 403，行为与改造前一致）；
      一旦有 .js 对象即按 UTF-8 javascript 输出，与巴西 Worker 行为相同。
```

## 五、遗留

```text
1. 老域名 01-05（CloudFront 链路）该路径实测 200，不受影响；06/07 走 Cloudflare + Worker，规则本来就有。
2. 本次只补齐了这两条规则；如果后续发现巴西 Worker 里还有别的静态特例（例如 health.json 的独立缓存键），
   再逐条对齐（health.json 的缓存键是边缘缓存机制，nginx 侧无对应概念，不需要）。
3. 目录请求 302 → index.html、OPTIONS 204、CORS * 这些此前已在 nginx 实现，本轮未改。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby-static-extra.conf（本轮新增片段）
docker/deploy/hongkong/nginx-standby.conf（两个静态块 include 了该片段）
docker/deploy/hongkong/cdn-backup/worker/summer-wave-c94f.js（巴西 Worker 备份，规则出处）
docker/deploy/hongkong/cdn-backup/worker/dbqp-hk-static-proxy.js（HK Worker，含同样两段规则）
```
