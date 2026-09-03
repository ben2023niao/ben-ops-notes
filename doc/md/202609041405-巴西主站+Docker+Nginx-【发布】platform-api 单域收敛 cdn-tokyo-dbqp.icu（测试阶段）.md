---
id: "doc-1a780b3bb7fa"
title: "【发布】platform-api 单域收敛 cdn-tokyo-dbqp.icu（测试阶段）"
date: "2026-09-04T14:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "自动化", "CDN", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-04-1405-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E5%8D%95%E5%9F%9Fcdn-tokyo%E6%94%B6%E6%95%9B%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1405-【发布】platform-api单域cdn-tokyo收敛记录.md"
sourceSha256: "4d8bd19760bfd3591ab4c22a0c27fda0ed75aaf0851329c41379610ef95da89d"
sourceSystem: "project-doc"
---

# 【发布】platform-api 单域收敛 cdn-tokyo-dbqp.icu（测试阶段）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-04-1405-【发布】platform-api单域cdn-tokyo收敛记录.md`

> 整理日期：2026-09-04 14:05｜日期依据：文件名日期

时间：2026-09-04 14:05（Asia/Manila）
项目：DBQP / PGServer master（platform-api domains）
状态：✅ 完成（01 单机，仅 cdn-tokyo-dbqp）

## 一、需求

```text
测试阶段把 3 套域名收敛为只使用 cdn-tokyo-dbqp.icu 一套，更新发布生效。
```

## 二、执行

```text
1) 备份：宝塔 /root/dbqp-platform-config-backup-20260904-single-tokyo-before/
   （baota + 01 宿主 + 01 容器）；
2) 7 份 domains 仅保留 .cdn-tokyo-dbqp.icu（删除 tada/xqv），校验通过；
3) 01 同步 + docker cp + restart platform-api。
```

## 三、验证

```text
1) 容器 host：cdn-tokyo-dbqp=29，tada-cdn-2026=0，xqv9m8=0；
2) api/pg-games.cdn-tokyo-dbqp.icu /health rcode=0；
3) 02/03 停止，nginx 仍只指 01。
```

## 四、飞机群通知 message_id

```text
5164 任务开始
5165 发布完成
```

## 五、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
