---
id: "doc-1406e9230570"
title: "【资源优化】大 JS / 字体 / JSON 审计记录"
date: "2026-08-30T01:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-30-0140-%E3%80%90%E8%B5%84%E6%BA%90%E4%BC%98%E5%8C%96%E3%80%91%E5%A4%A7JS%E4%B8%8E%E5%AD%97%E4%BD%93%E4%B8%8EJSON%E5%AE%A1%E8%AE%A1%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-30-0140-【资源优化】大JS与字体与JSON审计记录.md"
sourceSha256: "ed730a947d42b54e74f4d7dcc42a7871ad0b8e6d1187e5c792443f398df29878"
sourceSystem: "project-doc"
---

# 【资源优化】大 JS / 字体 / JSON 审计记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608300140-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E8%B5%84%E6%BA%90%E4%BC%98%E5%8C%96%E3%80%91%E5%A4%A7%20JS%20-%20%E5%AD%97%E4%BD%93%20-%20JSON%20%E5%AE%A1%E8%AE%A1%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-30 01:40｜日期依据：文件名日期

时间：2026-08-30 01:40（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 宝塔 + GCS）

## 一、大 JS 优化

### 分析

```text
pp game-history-client main.28720e9b.min.js（1.1MB）：
  生产静态目录无任何 HTML 引用（grep 仅命中文件自身）→ 疑似后端动态引用，不删除；
vendor_a _nuxt 大文件（652/574/557KB）：
  被 zh-CN/en-US 的 ingame/landingpage/intro 页面按序引用（body 尾部，
  13 个同步 script），内联脚本先定义 window.__NUXT__ → defer 有顺序风险、
  且脚本在 body 尾收益小 → 不盲改，真正分包需 vendor 源码（灰度待定）；
pp main.5e295630.min.js 仅存在于仓库，生产未部署。
```

### 执行（安全项）

```text
hash 文件名 JS 设 Cache-Control: public,max-age=31536000,immutable：
  并发 PATCH 3098 个对象（64 线程，8 秒，0 失败）
  验证：CF 返回 cache-control: public,max-age=31536000,immutable
备份：/www/backup/js-fonts-20260830/pp-gs2c.tar(20M) + vendor_a-pages.tar(90K)
脚本：/opt/patch_js_cache.py（仓库 docker/scripts/static_webp/ 未含，记录于 baota）
```

## 二、字体 woff2

```text
Montserrat-Medium.ttf 243KB → Montserrat-Medium.woff2 78KB（省 68%）
CSS main.28720e9b.min.css @font-face：woff2 优先 + ttf 兜底（备份 .bak-20260830）
同步 gs://bizops-gcs-pp-static-sa/gs2c/common/game-history-client/（3 对象）
验证：CF 200，font/woff2，78404B；CSS 已引用 woff2
```

## 三、JSON 冗余审计

```text
仓库级 489 个 / 16.5MB；静态引用扫描 485 个显示"未引用"，
但 i18n（game-history-client/i18n/*.json）等为动态路径引用
（如 i18n/${lang}.json），audit 不可直接删除 → 保持报告，需专项审计（P3 待办）
```

## 四、变更与备份

```text
服务器：pp-static woff2 + CSS、3098 个 JS 对象缓存头（可回滚：gsutil setmeta 还原 max-age=86400）
备份：/www/backup/js-fonts-20260830/ + CSS .bak-20260830
文档：本记录
```

## 五、待办

- vendor_a _nuxt 分包需 vendor 源码（灰度方案待定）；
- JSON 专项审计（动态引用识别）；
- 确认 pp main.28720e9b 是否被后端引用（若确认孤儿可清理）。
