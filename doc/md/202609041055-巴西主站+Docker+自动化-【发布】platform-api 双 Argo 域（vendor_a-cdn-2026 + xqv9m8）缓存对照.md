---
id: "doc-151a3c0498ab"
title: "【发布】platform-api 双 Argo 域（vendor_a-cdn-2026 + xqv9m8）缓存对照"
date: "2026-09-04T10:55:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-04-1055-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E5%8F%8CArgo%E5%9F%9Fvendor_a-xqv%E7%BC%93%E5%AD%98%E5%AF%B9%E7%85%A7%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-04-1055-【发布】platform-api双Argo域vendor_a-xqv缓存对照记录.md"
sourceSha256: "020dfb59ba83c246c9a3520a6119552f0e34e219be1b5573feb51c3f1b6b1b16"
sourceSystem: "project-doc"
---

# 【发布】platform-api 双 Argo 域（vendor_a-cdn-2026 + xqv9m8）缓存对照

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-04-1055-【发布】platform-api双Argo域vendor_a-xqv缓存对照记录.md`

> 整理日期：2026-09-04 10:55｜日期依据：文件名日期

时间：2026-09-04 10:55（Asia/Manila）
项目：某业务公司 / PGServer master（platform-api domains）
状态：✅ 完成（01 单机，双域配置并验证）

## 一、需求

```text
platform-api 保留 vendor_a-cdn-2026.icu（单域缓存正常）基础上，
再加一个开 Argo 的域名（选 xqv9m8.icu，Argo/Tiered 均开），
用于对照测试“多域名下静态文件是否走 CDN 缓存”。
```

## 二、执行

```text
1) 备份：宝塔 /root/bizops-platform-config-backup-20260904-add-xqv-before/
   （baota + 01 宿主 + 01 容器）；
2) 7 份 domains：vendor_a-cdn-2026 host 后追加同前缀 xqv9m8 host；
   校验 bad=0、单列表无重复；
3) 01 同步 + docker cp 7 份 + restart platform-api。
```

## 三、验证

```text
1) 容器内 host：vendor_a-cdn-2026=29、xqv9m8=29、cdn-tokyo-bizops=0；
2) 公网 api/pg-games .{vendor_a-cdn-2026,xqv9m8}.icu /health rcode=0；
3) 静态缓存：pg-static.{vendor_a-cdn-2026,xqv9m8}.icu/126/index.html
   连续 3 次 cf-cache-status=HIT（age ~647-648）。
```

## 四、飞机群通知 message_id

```text
5143 任务开始
5144 双域上线 + 缓存对照结果
```

## 五、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
