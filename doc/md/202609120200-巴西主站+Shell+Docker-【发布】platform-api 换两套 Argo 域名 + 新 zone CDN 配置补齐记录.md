---
id: "doc-1e14317a1f70"
title: "【发布】platform-api 换两套 Argo 域名 + 新 zone CDN 配置补齐记录"
date: "2026-09-12T02:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "监控告警", "自动化", "CDN", "DNS"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-12-0200-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%E6%8D%A2%E4%B8%A4%E5%A5%97Argo%E5%9F%9F%E5%90%8D%E4%B8%8E%E6%96%B0zone%E7%9A%84CDN%E9%85%8D%E7%BD%AE%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-12-0200-【发布】platform-api换两套Argo域名与新zone的CDN配置补齐记录.md"
sourceSha256: "5c81ea44a93942697e308dd19ea0b48c4864b344fa92debf0905c2040a960e2c"
sourceSystem: "project-doc"
---

# 【发布】platform-api 换两套 Argo 域名 + 新 zone CDN 配置补齐记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609120200-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91platform-api%20%E6%8D%A2%E4%B8%A4%E5%A5%97%20Argo%20%E5%9F%9F%E5%90%8D%20%2B%20%E6%96%B0%20zone%20CDN%20%E9%85%8D%E7%BD%AE%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-12 02:00｜日期依据：文件名日期

时间：2026-09-12 02:00（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地 + 宝塔 192.0.2.8 + 后端 01 192.0.2.1 + Cloudflare API）
状态：✅ 完成并验证

## 一、任务

```text
用户要求：
1) platform-api 里把另外 2 套已开 Argo 的域名加进来，然后下掉目前这套域名；
2) 核对新域名的 CDN 各配置（Worker 等），都要参照老域名的配置来做；
3) 把替换下来的老域名整理成测试清单（带 health.json）发群，供巴西侧验证是否 DNS 污染；
4) 各厂家游戏抽测。
```

## 二、Argo 三套确认（CF API 全量核对 42 个 zone）

```text
Argo Smart Routing = on 的只有 3 套：
  cdn-tokyo-bizops.icu（本次下掉的「目前这套」）
  vendor_a-cdn-2026.icu  ┐
  xqv9m8.icu         ┘ 本次换上的两套
```

## 三、新 zone 的 CDN 配置缺口（对照老 zone 发现）

```text
对照对象：老 zone cdn-tokyo-bizops.icu

                     静态 DNS   静态 Worker 路由
  老 zone              16 条       8 条
  xqv9m8.icu           13 条       4 条   ← 缺 3 DNS / 4 路由
  vendor_a-cdn-2026.icu    13 条       4 条   ← 缺 3 DNS / 4 路由

缺口明细（两个新 zone 相同）：
  DNS  ：vendor_a-statics3 / vendor_a-statics4 / vendor_a-statics5
         CNAME -> newgg2-bizops-gcs-vendor_a-staticsN-sa.storage.googleapis.com（proxied）
  路由 ：vendor_a-statics3/4/5.<zone>/* 与 *-statics1.<zone>/* -> summer-wave-c94f

根因与现象：
  通配路由 *-static.<zone>/* 匹配不到 vendor_a-statics3/4/5
  （主机名以 -statics3 结尾，不是 -static），
  叠加缺少 DNS 记录 → 这两套新域名的 vendor_a-statics3/4/5 全部 520，
  其余 14 个静态域正常 200。
```

## 四、执行

```text
1) 补齐新 zone 配置（只动新 zone，老 zone 不改）
   新增 3 条 DNS + 4 条 Worker 路由 × 2 个 zone = 14 项，全部 OK
   复核：三 zone 配置一致（DNS 16 / 路由 8），无差异
2) platform-api 域名替换（7 份配置）
   pg / vendor_a / pp / popok / vendor_c / vendor_d / g759
   下掉 cdn-tokyo-bizops.icu；换上 xqv9m8.icu + vendor_a-cdn-2026.icu
   覆盖 static_hosts / game_hosts / api_hosts 以及 pg3-7、vendor_a v1-v5 分组
3) 发布到后端 01（容器不挂载该目录，用 docker cp + 重启）
   docker cp 7 份 → bizops-platform-api-release-01:/app/platform-api/conf/domains/
   docker restart；容器内旧域名残留检查 = 0
4) 服务器 /opt/pgserver/platform-api/conf/domains 同步为新配置
```

## 五、验证

```text
1) 静态域：17 个前缀 × 2 套新域 = 34/34 全部 200，异常 0
2) 游戏/API 域：8/8 返回 200
3) zone 级设置三套一致：Brotli on / Early Hints on / Polish lossy /
   Always HTTPS on / min TLS 1.2 / SSL full
4) 各厂家抽测（巴西机房出口、iPhone UA，入口 → 点第一个游戏）：
   PG canvas=1（画面出现「开始」按钮，落地 vendor_a-cdn-2026.icu）
   vendor_a / PP / PPK / vendor_c / PANDA / G759 均 canvas=1 已渲染
   落地域名全部为新域名，无一例走 cdn-tokyo-bizops.icu
5) PG 重点复测：由「卡在正在加载[6%]」变为出现「开始」按钮；
   无 4xx/5xx、无 pending、无 JS error；仅剩历史已知的 Service Worker 注册告警
6) 容器内抽查：
   pg.json default = {pg-static/pg-games/api}.{xqv9m8.icu, vendor_a-cdn-2026.icu}
   vendor_a v5 分组 = vendor_a-statics5.{xqv9m8.icu, vendor_a-cdn-2026.icu}
```

## 六、给巴西侧的老域名污染排查清单

```text
已发群（message_id 6319）：老域名 cdn-tokyo-bizops.icu
  17 条静态域 /health.json + 8 条游戏 API /health 直链
  正常判定：返回 JSON 且含 "rcode":0、"msg":"succ"
  DNS 对照：老域名正常应解析到 192.0.2.33 / 192.0.2.34
  建议动作：dnschecker/whatsmydns 巴西各州解析截图、4G 与 Wi-Fi 各测、
            与 192.0.2.31 / 192.0.2.30 对比、失败记录城市/运营商/机型/截图
```

## 七、留下的可复用脚本

```text
docker/scripts/cf_zone_static_compare.py   新旧 zone 静态 CDN 配置差异对比
docker/scripts/cf_zone_static_sync.py      按老 zone 补齐新 zone 的 DNS + Worker 路由
docker/scripts/platform_api_domains_switch.py  platform-api 域名套替换（dry-run/apply）
docker/scripts/deploy_platform_domains.sh  后端 01 热更域名配置并重启 platform-api
docker/scripts/vendor_ua_stats.py          各厂家在线用户 UA 统计（iOS/Android 等）
```

## 八、回退步骤

```text
1) 域名回退：把 7 份 JSON 的 hosts 换回 cdn-tokyo-bizops.icu
   （可用 platform_api_domains_switch.py --from xqv9m8.icu,vendor_a-cdn-2026.icu
     --to cdn-tokyo-bizops.icu --apply），再跑 deploy_platform_domains.sh
2) 新增的 DNS/路由是增量且只在新 zone，可不回退；如需删除按上面清单逐条删除
3) 本轮未改 nginx / DNS 解析 / 老 zone，无其它回退面
```

## 九、遗留

```text
- 老域名 cdn-tokyo-bizops.icu 保留解析（不删），等巴西侧污染排查结论；
  若确认污染严重，再统一清理该 zone 的解析与路由。
- 桌面端 UA（Windows Chrome/15x）在 g759 接口上有大量无 token 轮询请求，
  疑为自动化流量，建议后续单独甄别（见 vendor_ua_stats.py 输出）。
```

## 十、飞机群通知 message_id

```text
6316 替换完成（本地配置）+ Argo 三套确认
6317 新域名 CDN 配置核对结果（缺 3 DNS + 4 路由）
6318 补齐完成 + 换域名已发布
6319 老域名污染排查清单（给 Lion 团队）
6320 各厂家抽测结果
```

## 十一、本地提交

```text
6683790e feat(platform-api): 换用 xqv9m8.icu + vendor_a-cdn-2026.icu 两套 Argo 域名
         （含本记录、CDN 对比/补齐脚本、域名替换与发布脚本、UA 统计与客户端排查工具）
master 领先 origin/master，未 Push
```
