---
id: "doc-c069a4806a55"
title: "【发布】platform-api 单 Argo 域名配置上线记录"
date: "2026-09-03T00:39:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-03-0039-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E5%8D%95Argo%E5%9F%9F%E5%90%8D%E9%85%8D%E7%BD%AE%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-03-0039-【发布】platform-api单Argo域名配置上线记录.md"
sourceSha256: "2ae56d1d73378e1c3fc9b99ce5473c4b87193c20e47d5080412966eebe2dbd8a"
sourceSystem: "project-doc"
---

# 【发布】platform-api 单 Argo 域名配置上线记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-03-0039-【发布】platform-api单Argo域名配置上线记录.md`

> 整理日期：2026-09-03 00:39｜日期依据：文件名日期

时间：2026-09-03 00:39（Asia/Manila）
项目：DBQP / PGServer master（platform-api 运行配置）
状态：✅ 已发布并验证（3/3 后端）

## 一、背景

```text
用户要求：备份 platform-api 配置；只配置一套域名（选已开 Argo 的域名），
便于发布后直接验证“预热效果”；随后立即发布。
选用域名：xqv9m8.icu（历史 3 套 Argo 域之一，CF API 查证
smart_routing=on）。
```

## 二、备份

```text
位置：宝塔 /root/dbqp-platform-config-backup-20260903/（root-only）
  baota-domains：宝塔 /opt/pgserver 副本 7 份
  domains-01/02/03：3 台后端容器运行配置（各含 7 份 + 既有扩展文件）
回滚：用备份目录文件 docker cp 回容器 + docker restart。
```

## 三、配置改动

```text
platform-api/conf/domains 下 7 份 JSON
（pg/tada/pp/popok/playson/panda/g759）：
- static_hosts / game_hosts / api_hosts 全部收敛为 xqv9m8.icu 单域名；
- 例：pg3-7 static 仅 <prefix>.xqv9m8.icu；game 共用
  pg-games.xqv9m8.icu；api 仅 api.xqv9m8.icu；
- diff：7 文件 +36/-587。
```

## 四、发布与验证

```text
1) 宝塔 /opt/pgserver 副本同步；
2) 3 台后端（203.0.113.1/.4/.11）platform-api 容器
   docker cp 7 份配置 + docker restart（顺序执行）；
3) 容器内校验：7 份配置均只含 xqv9m8 单域名；
4) 公网抽检：
   api/pg-games/tada-games/pp-games .xqv9m8.icu /health = 200 rcode=0
   pg-static health.json、pg6-static 1834850/index.html = 200。
```

## 五、效果

```text
发布后所有厂家统一走 xqv9m8（Argo）单套域名：
  - 预热对象确定（单一 zone/域名），测试“预热后首访速度”不再受 20-zone
    随机池干扰；
  - Argo Smart Routing 开启，跨区回源路径有优化空间（可与预热叠加复测）。
```

## 六、飞机群通知 message_id

```text
4959 任务开始（1/8）
4960 备份 + Argo 确认（1/8 完成）
4961 配置收敛（2/8）
4962 本地验证（3/8）
4963 发布开始（4/8）
4964 发布完成（4/8）
4965 线上验证（5/8）
4966 文档完成（6/8）
4967 汇总 + 事件文档附件（主体提交前）
4968 提交结果（master 5386ff4e / cn 9c1076aa，均未 Push）
```

## 七、本地提交

```text
master：5386ff4e ops: platform-api domains to single Argo domain xqv9m8.icu
cn：9c1076aa docs: cross-link master platform-api single Argo domain publish
（均未 Push；master 领先 origin/master 25，cn 领先 origin/cn 38）
```

## 八、关联更新（2026-09-03 02:00 回写）

```text
发布后同日追加核查/实测，均关联本文档：
1) CDN Tiered Cache 核查：xqv9m8.icu（本发布唯一承载域）Smart Tiered Cache = ON，
   账号 42 zone 仅 3 个 ON（另 cdn-tokyo-dbqp.icu、m6xv8q.cyou）；
2) 多地区实测（马尼拉/巴西/东京）东京最快且稳定，NRT 预热 + Argo/Tiered Cache 生效。
详见：2026-09-03-0135-【竞品分析】多游戏多地区点击渲染对比与CDN核查记录.md
```
