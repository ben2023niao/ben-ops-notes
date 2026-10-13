---
id: "doc-ad53e3032d89"
title: "【运维】巴西线上 PP 静态资源 CDN 缓存刷新（含 zone 查询漏刷 bug 修复）"
date: "2026-10-14T10:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "CDN", "DNS", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-14-1035-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91%E5%B7%B4%E8%A5%BF%E7%BA%BF%E4%B8%8APP%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CDN%E7%BC%93%E5%AD%98%E5%88%B7%E6%96%B0%E8%AE%B0%E5%BD%95%28%E5%90%AB%E5%88%86%E5%8C%BA%E6%9F%A5%E8%AF%A2%E6%BC%8F%E5%88%B7bug%E4%BF%AE%E5%A4%8D%29.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-14-1035-【运维】巴西线上PP静态资源CDN缓存刷新记录(含分区查询漏刷bug修复).md"
sourceSha256: "937c693f721f525fbecce665b141351bb2c2a392fae3608e557563c90f2942bb"
sourceSystem: "project-doc"
---

# 【运维】巴西线上 PP 静态资源 CDN 缓存刷新（含 zone 查询漏刷 bug 修复）

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-14-1035-【运维】巴西线上PP静态资源CDN缓存刷新记录(含分区查询漏刷bug修复).md`

> 整理日期：2026-10-14 10:35｜日期依据：文件名日期

时间：2026-10-14 10:35（北京）/ 02:35（UTC）
需求：「清理一下巴西线上 pp 的静态资源缓存」，本轮**不通知飞机群**。
对象：`pp-static.*`（21 个根域名 + d1b2q3p.cfd 不在服务列表）走 Cloudflare → Worker → GCS
　　　`newgg2-dbqp-gcs-pp-static`（圣保罗桶）。

---

## 一、结论

```text
· 22 个服务 pp-static.* 的 zone 全部 purge_everything 成功（ok=22 fail=0）
· 复测：22 个 zone 上 pp 的资源都是 cf-cache-status=MISS + HTTP 200（缓存已清、回源正常）；
  再打一次即回到 HIT（缓存重新建立），说明链路健康
· 顺带修掉脚本一个会「漏刷主域名」的 bug（见第三节），并留了备份
```

## 二、为什么是「整 zone 刷新」而不是「按 URL 刷新」

```text
仓库里 docker/scripts/cf_purge_zones.sh 顶部就写了（2026-09-16 实测）：
  静态链路是 Cloudflare Worker + fetch(cf.cacheKey/cacheEverything)，
  **purge files（按 URL 刷新）对它是无效的**，刷新后请求仍是 cf-cache=HIT；
  只有两种有效方式：① 整 zone purge_everything（本脚本用的）② 改 Worker 的缓存盐重新部署。
本次沿用 ①：只对**确实在服务 pp-static.* 的 zone** 做 purge_everything，
把影响面压到最小（代价：同一 zone 下其它厂家的缓存也会被清掉，
它们会重新从 GCS 回源一次，属可接受的冷缓存抖动）。

判定"哪些 zone 在服务 pp-static.*"的方式：脚本对每个候选根域名请求
  https://pp-static.<zone>/health.json
返回 200 的才算（本次 22 个 zone 命中，从宝塔巴西出口请求，不受国家白名单影响）。
```

## 三、⚠️ 修复：zone 列表只读第一页导致「漏刷主域名」

```text
现象：第一次执行显示 PURGE_DONE ok=19 fail=0（看着成功），但复测发现
      pp-static.xqv9m8.icu 的资源仍是 cf-cache-status=HIT —— 也就是说**根本没刷到**。
原因：旧脚本用列表接口取 zone id：
        GET /client/v4/zones?per_page=50
      但本账户 zone 总数 > 50，接口只返回第一页 → xqv9m8.icu、
      tada-host-2026.icu、tada-host-game.icu 三个 zone 不在第一页，直接被漏掉。
      （其中 xqv9m8.icu 是最主要的根域名，漏刷影响最大。）

修复（docker/scripts/cf_purge_zones.sh）：改为**按名字逐个精确查**：
        GET /client/v4/zones?name=<zone>   → 取 result[0].id
      并把查不到的 zone 显式打印「⚠️ 查不到 zone（跳过）」，避免静默漏刷。

修复后重新执行：PURGE_DONE ok=22 fail=0（这次包含 xqv9m8.icu），复测全部 MISS。

历史影响提醒：**这个 bug 从脚本诞生起就存在**——此前按本脚本做的刷新
（例如文档里 2026-09-16 那次）同样会漏掉这 3 个 zone，需要时值得补刷一次。
```

## 四、实测验证

```text
基线（刷新前）：GET https://pp-static.xqv9m8.icu/gs2c/common/game-history-client/0.28720e9b.min.js
  第 1 次 MISS → 第 2/3 次 HIT（确认该 zone 原本有缓存，验证有意义）

刷新：bash /opt/dbqp-scripts/cf_purge_zones.sh --vendor pp   （耗时 26s，ok=22 fail=0）

刷新后：
  · 22 个 zone 抽样：cf-cache-status=MISS + HTTP 200 + content-length 13311（与源一致）
  · 用「没被验证请求碰过」的对象复核（favicon.ico）→ 5 个 zone 全 MISS，排除"是我自己把它又拉回缓存"的干扰
  · 再请求一次 → 回到 HIT，回源与缓存重建正常
【注】第一次 22-zone 复盘时看到的 5 个 HIT，正是我验证时请求过的那 5 个 zone（被自己重新缓存），
      用另一个对象复核后确认为 MISS，属正常现象。
```

## 五、运维手册

```bash
# 刷新某个厂家的静态缓存（在宝塔上跑，CF token 在 /root/dbqp-cf-dns.env，有 IP 白名单）
bash /opt/dbqp-scripts/cf_purge_zones.sh --vendor pp
bash /opt/dbqp-scripts/cf_purge_zones.sh --vendor panda
bash /opt/dbqp-scripts/cf_purge_zones.sh --zones xqv9m8.icu,q7m9v8.icu      # 指定 zone
bash /opt/dbqp-scripts/cf_purge_zones.sh --all                            # 全部静态 zone

# 验证（换一个你这次没请求过的对象，避免误判）
curl -s -o /dev/null -D - "https://pp-static.xqv9m8.icu/favicon.ico" | grep -iE "^HTTP/|cf-cache-status"

# 如果未来要「只刷一个厂家」，需要把 Worker 的缓存盐改成 per-vendor 才能做到；
# 换全局盐会影响所有厂家（cf_worker_cache_refresh.sh）
```

## 六、相关文件

```text
docker/scripts/cf_purge_zones.sh          # 本次修复（zone 按名字精确查）
/opt/dbqp-scripts/cf_purge_zones.sh       # 宝塔部署副本（旧版已备份 .bak-20261014-103225-before-zone-lookup-fix）
docker/doc/2026-09-10-0949-…CDN缓存清理与Worker缓存盐记录.md   # 同类操作历史记录
docker/doc/2026-09-14-1400-…GCS单桶化与Worker变更全记录.md      # 静态链路（Worker + GCS）现状
```
