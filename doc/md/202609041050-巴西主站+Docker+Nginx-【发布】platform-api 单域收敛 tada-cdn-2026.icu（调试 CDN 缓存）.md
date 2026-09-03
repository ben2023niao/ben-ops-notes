---
id: "doc-3aff59c4113b"
title: "【发布】platform-api 单域收敛 tada-cdn-2026.icu（调试 CDN 缓存）"
date: "2026-09-04T10:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-04-1050-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E5%8D%95%E5%9F%9Ftada-cdn-2026%E6%94%B6%E6%95%9B%E8%B0%83%E8%AF%95%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1050-【发布】platform-api单域tada-cdn-2026收敛调试记录.md"
sourceSha256: "9d167734152984335e34ab0dc48fdb90c73825dd0d618b7d29345b05abed5d90"
sourceSystem: "project-doc"
---

# 【发布】platform-api 单域收敛 tada-cdn-2026.icu（调试 CDN 缓存）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1050-【发布】platform-api单域tada-cdn-2026收敛调试记录.md`

> 整理日期：2026-09-04 10:50｜日期依据：文件名日期

时间：2026-09-04 10:50（Asia/Manila）
项目：DBQP / PGServer master（platform-api domains）
状态：✅ 完成（01 单机热更，仅 tada-cdn-2026）

## 一、需求

```text
platform-api 只配置 tada-cdn-2026.icu，方便手动调试 CDN；
当前静态资源疑似没走上 CDN 缓存（多域随机分发导致冷缓存）。
```

## 二、执行

```text
1) 备份：宝塔 /root/dbqp-platform-config-backup-20260904-single-tada/
   （baota 7 份 + 01 宿主/容器各 10 份，含 fc/jdb/jili 等扩展文件）；
2) 本地 7 份 domains 收敛：删除 .xqv9m8.icu / .cdn-tokyo-dbqp.icu，
   仅保留 .tada-cdn-2026.icu（校验 bad=0）；
3) 01 /opt/pgserver 同步 + docker cp 7 份 + docker restart platform-api；
4) 验证：容器内 host 29 条全为 tada-cdn-2026，xqv=0、cdn-tokyo=0。
```

## 三、缓存验证

```text
pg-static.tada-cdn-2026.icu/126/index.html：
  首访 cf-cache-status=MISS -> 二访 HIT（age 0）
结论：单域收敛后静态资源可走上 CDN 缓存；
之前“没走缓存”问题大概率来自客户端在多个域名间随机分发/各域冷缓存。
```

## 四、公网验证

```text
api.tada-cdn-2026.icu / pg-games.tada-cdn-2026.icu /health rcode=0。
02/03 保持停止；nginx 仍仅指 01。
```

## 五、飞机群通知 message_id

```text
5140 任务开始
5141 收敛完成 + 缓存验证
```

## 六、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
