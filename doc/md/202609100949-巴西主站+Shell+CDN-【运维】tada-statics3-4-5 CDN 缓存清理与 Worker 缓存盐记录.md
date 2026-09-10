---
id: "doc-a03e55cdca2a"
title: "【运维】tada-statics3/4/5 CDN 缓存清理与 Worker 缓存盐记录"
date: "2026-09-10T09:49:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "CDN", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-10-0949-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91tada-statics3-5%20CDN%E7%BC%93%E5%AD%98%E6%B8%85%E7%90%86%E4%B8%8EWorker%E7%BC%93%E5%AD%98%E7%9B%90%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-10-0949-【运维】tada-statics3-5 CDN缓存清理与Worker缓存盐记录.md"
sourceSha256: "42f847b24a40fa704120f56d4b0bd28ab4ee68d42d5b68d61a410406998fc9fb"
sourceSystem: "project-doc"
---

# 【运维】tada-statics3/4/5 CDN 缓存清理与 Worker 缓存盐记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-10-0949-【运维】tada-statics3-5 CDN缓存清理与Worker缓存盐记录.md`

> 整理日期：2026-09-10 09:49｜日期依据：文件名日期

时间：2026-09-10 09:49（Asia/Manila）
项目：DBQP / PGServer master（巴西静态 CDN）
结果：✅ Worker 缓存盐升级并部署；cdn-tokyo 缓存清理完成；tada3/4/5 复测 200

## 一、操作内容

```text
1) 备份现网 Worker summer-wave-c94f 并发送到群（message 5611）：
   /root/dbqp-cf-backups/20260910-before-cachepurge/
2) Worker 缓存键统一加盐 CACHE_SALT=v4-20260910-tada345，
   使 Workers Cache API 旧缓存整体失效（CF purge 不影响 Workers Cache）。
   部署校验：live 脚本包含新盐；modified_on=2026-09-10T01:47:35Z。
3) Cloudflare 缓存清理（cdn-tokyo-dbqp.icu）：
   - 先 hosts purge：tada-statics3/4/5.cdn-tokyo-dbqp.icu → success
   - 再 purge_everything → success（确保边缘无旧 404）
4) 补充资源：dad/assets/game/game.ae2d9.zip 从参考域重新补到
   -sa / asia / backup 三路（此前对象缺失）。
```

## 二、验证

```text
tada-statics3.cdn-tokyo-dbqp.icu/mp2/index.html            → 200
tada-statics4.cdn-tokyo-dbqp.icu/dad/                      → 200
tada-statics4.cdn-tokyo-dbqp.icu/dad/assets/game/game.ae2d9.zip → 200
tada-statics4 .../astarte/3.6/.../tadaMain.ddf09.zip       → 200
tada-statics5.cdn-tokyo-dbqp.icu/c7d/index.html            → 200
（595 剩余 bd3d1/868dc.cconb 仍为上游缺失项，另行跟进）
```

## 三、影响范围

```text
仅新增桶 tada-statics3/4/5 与 cdn-tokyo zone；未修改 tada-statics0-2
与老游戏资源/域名，老业务不受影响。
```

## 四、群通知

```text
5610 步骤1/5 计划
5611 清理前 Worker 备份附件
5612 Worker 缓存盐部署
5613 CF 缓存清理开始
5614（本汇总）
```

## 五、本地提交

```text
（见提交结果群消息）
```
