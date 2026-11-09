---
id: "doc-5c01efb3d797"
title: "2026-10-05 香港 vendor_b 静态域名：按 Worker 路径映射 + 补 intro/astarte 处理"
date: "2026-10-05T14:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-05-1400-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFvendor_b%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%E6%8C%89Worker%E8%B7%AF%E5%BE%84%E6%98%A0%E5%B0%84%E5%B9%B6%E8%A1%A5intro-astarte%E5%A4%84%E7%90%86.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1400-【架构改造】香港vendor_b静态域名按Worker路径映射并补intro-astarte处理.md"
sourceSha256: "8d342410b398e1a8b5d44cd9b3befbccfaf5a4ebc60c2a452d7a234845e55abc"
sourceSystem: "project-doc"
---

# 2026-10-05 香港 vendor_b 静态域名：按 Worker 路径映射 + 补 intro/astarte 处理

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610051400-%E9%A6%99%E6%B8%AF%20CN%2BDocker%2BNginx-2026-10-05%20%E9%A6%99%E6%B8%AF%20vendor_b%20%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%EF%BC%9A%E6%8C%89%20Worker%20%E8%B7%AF%E5%BE%84%E6%98%A0%E5%B0%84%20%2B%20%E8%A1%A5%20intro-astarte%20%E5%A4%84%E7%90%86.md)

> 整理日期：2026-10-05 14:00｜日期依据：文件名日期

## 一、需求

```text
开发（C++）先贴了老 vendor_b 静态 nginx 的两段 server 配置：
  vendor_b-test.bxgjnet.com   -> root /data/static/vendor_bstatic;  index index.html ...
  vendor_b-test1.bxgjnet.com  -> root /data/static/vendor_bstatic1; + intro 图片/intro 帮助页/.js MIME/astarte versions.json/404.png
运维口径（用户 2026-10-05 明确）：**不要照抄老配置的本地目录，静态资源路径映射参考香港的 Cloudflare Worker**。
本轮要求：每步发群通知 → 备份 nginx → 改造 → 验证 → 文档 → 本地提交（不推送）。
```

## 二、分析（先核实，再动手）

```text
1) 香港 Worker 的映射（docker/deploy/hongkong/hk_static_worker.js 的 PREFIX_MAP）：
     vendor_b-static  -> https://bizops-s3-vendor_b-static.s3.ap-northeast-3.amazonaws.com
     vendor_b-static1 -> https://bizops-s3-vendor_b-static1.s3.ap-northeast-3.amazonaws.com
     vendor_b-static2 -> 无映射（Worker 直接放行）
   即「一个厂家一个桶」，对象直接放在桶根；Worker 另外还做：OPTIONS 204、
   目录 302 -> index.html、.js 强制 MIME、customizations.info 空 200、CORS。
2) 现网核实（改造前）：
     vendor_b-static.m4q7z1.shop/ifff/index.html  = 200 / 34,238B（vendor_b 自己的桶）
     vendor_b-static1.m4q7z1.shop/lj500/index.html= 200 / 97,383B
     /lj500/ 目录 = 302、OPTIONS = 204（通用静态块已按 Worker 口径做过）
   结论：**映射部分已经基本对齐**，缺的是老配置里 vendor_b 专属的三条路径处理。
3) 缺口（改造前实测都是 403）：
     /zh-CN/intro?game=664        -> 403（但桶里确实有 lj500/intro/zh-CN.html = 200 / 13,473B）
     /astarte/3.6/web-mobile/assets/versions.json（vendor_b-static1）已 200，但没有 Vary: Referer
     /static/images/intro/...     老配置有路径规整规则，当前没有
4) 老配置里 ① 的 code 来自 `map $arg_game $intro_code` 整表（游戏 id -> 目录名），
   开发没有给全表；本轮改成按 **Referer** 推导（游戏页地址形如 /lj500/index.html，
   第一个路径段就是目录名），不用维护整表，也不需要额外映射。
```

## 三、备份（改动前）

```text
standby 192.0.2.37（承载 m4q7z1 / k8x2v9 / 06 / 07）：
  /etc/nginx/sites-available/bizops-hk-standby.conf.bak-20261005-0454-vendor_b2
  /tmp/nginx-etc-20261005-0454.tgz
入口机 192.0.2.14：
  /etc/nginx/sites-available/bizops-hongkong.conf.bak-20261005-0454-vendor_b2
  /tmp/nginx-etc-20261005-0454.tgz
入仓（docker/deploy/hongkong/nginx-backup/）：
  nginx-standby-etc-nginx-20261005-0454.tgz
  nginx-entry-etc-nginx-20261005-0454.tgz
⚠️ 打包时排除 /etc/nginx/ssl：20261002 那份旧备份里带了 standby 的 TLS 私钥，
   本轮一并重新打包成不含 ssl/key 的版本（该文件从未 push 到 origin，私钥未外泄到远端）。
```

## 四、实现

```text
新增两个片段（standby 的 /etc/nginx/snippets/）：
  bizops-hk-standby-s3-origin.conf   —— 按 server_name 命名捕获的前缀回源 bizops-s3-<前缀>（大阪）
  bizops-hk-standby-vendor_b-static.conf —— vendor_b 静态 server 块共用内容
nginx-standby.conf 改动：
  ① 新增 map $http_referer $bizops_vendor_b_intro_code（正则取 Referer 第一个路径段；
     匹配不到落到占位目录 ___noref___，必然 403 → 最后统一转 404）
  ② 新增两个 server 块（放在通用静态块之前，正则 server_name 先匹配先赢）：
       ~^(?<bizops_static_prefix>vendor_b-static1?)\.(m4q7z1|k8x2v9)\.shop$
       ~^(?<bizops_static_prefix>vendor_b-static1?)\.hkcloudplay0[67]\.com$
  ③ 06/07 的通用静态兜底块 server_name 里去掉 vendor_b-static|vendor_b-static1
     （交给新块；vendor_b-static2 维持原状，Worker 也没有它的映射）
vendor_b 静态块内容（= Worker 行为 + 老配置的三条处理）：
  · 目录 302 -> index.html、OPTIONS 204、.js MIME、customizations.info 空 200、CORS *
  · ① /<lang>/intro?game=<id> -> /<code>/intro/<lang>.html
       语言逐级回退：请求语言 -> zh-CN -> en-US -> pt-BR，四跳都没有 -> 404
  · ② location ~ /static/images/intro/ 做路径规整
  · ③ location = /astarte/3.6/web-mobile/assets/versions.json 带 Vary: Referer
  · intro 相关响应统一 Cache-Control: no-store
```

```text
踩坑记录：
1) 第一版用 `if ($bizops_vendor_b_intro_code = "") { return 404; }`，实测没 Referer 时仍返回 403 ——
   原因不是 if 没生效，而是 **return 404 又被同一 location 的 error_page 404 抓走**，
   落进兜底链、最后一跳把 S3 的 403 原样返回。改成「占位目录 + 最后一跳 404」后干净了。
2) EdgeOne / CF 的缓存键**不含 Referer**：第一版给 intro 成功响应加了 max-age=604800，
   实测带 Referer 的 200 被边缘缓存后，随后不带 Referer 的请求也返回了 200（串味）。
   所以改成 no-store：宁可不缓存，也不要把「有/无 Referer」两种结果互相顶掉 7 天。
3) S3 缺对象返回的是 403 而不是 404，兜底链必须同时接 403 与 404，并开 recursive_error_pages。
```

## 五、验证（standby 源站 + 经 EdgeOne 公网，均实测）

| 请求 | 结果 |
| --- | --- |
| `vendor_b-static1.m4q7z1.shop/lj500/index.html` | 200 / 97,383B（vendor_b-static1 桶） |
| `vendor_b-static.m4q7z1.shop/ifff/index.html`、`vendor_b-static.k8x2v9.shop/ifff/index.html` | 200 / 34,238B |
| `/lj500/` | 302 → `/lj500/index.html` |
| `OPTIONS /lj500/index.html` | 204 |
| `/zh-CN/intro?game=664` + `Referer: .../lj500/index.html` | **200 / 13,473B** |
| `/xx-YY/intro?game=664` + 同 Referer（语言回退） | 200 / 13,473B |
| `/zh-CN/intro?game=664&fresh=1` 不带 Referer | **404 + `Cache-Control: no-store`** |
| `Referer: .../ifff/index.html`（桶里没有 intro） | 404（不是 S3 的 403 XML） |
| `/astarte/3.6/web-mobile/assets/versions.json` | 200 + `Vary: Referer` |
| `/x/customizations.info` | 200 / 0B |
| 其它厂家静态（pg-static / pp-static / vendor_d-static）同名路径 | 403，**行为未变** |
| 动态：`vendor_b-games.m4q7z1.shop/health`、`k8x2v9/health`、`/lj500/index.html` | 200（无回归） |
| 06/07 兜底块（Host 直连本机）：`vendor_b-static1.hkcloudplay07.com/lj500/index.html` | 200 / 97,383B |

```text
nginx -t 通过后才 reload；reload 后 systemctl is-active nginx = active。
```

## 六、影响面与回滚

```text
影响面：只影响 vendor_b-static / vendor_b-static1 两个前缀（m4q7z1 / k8x2v9 / 06 / 07 四套域名），
        其它厂家静态域名、动态域名、WebSocket 均未改动；
        vendor_b-static2 未纳入本块（Worker 也没有映射），保持原状。
回滚（standby）：
  cp /etc/nginx/sites-available/bizops-hk-standby.conf.bak-20261005-0454-vendor_b2 \
     /etc/nginx/sites-available/bizops-hk-standby.conf && nginx -t && systemctl reload nginx
  （片段文件留着不影响；如需彻底还原再删 /etc/nginx/snippets/bizops-hk-standby-s3-origin.conf、
    bizops-hk-standby-vendor_b-static.conf）
```

## 七、关联

```text
docker/deploy/hongkong/nginx-standby.conf（新增 map + 两个 vendor_b 静态 server 块）
docker/deploy/hongkong/nginx-standby-vendor_b-static.conf（vendor_b 静态块共用内容）
docker/deploy/hongkong/nginx-standby-s3-origin.conf（按前缀回源大阪桶）
docker/deploy/hongkong/hk_static_worker.js（路径映射的唯一口径来源）
docker/deploy/hongkong/nginx-backup/nginx-{standby,entry}-etc-nginx-20261005-0454.tgz
docker/doc/2026-10-05-1230-【架构改造】香港nginx的vendor_b静态改为走自己的大阪桶（对齐香港Worker）.md
docker/doc/2026-10-05-1330-【架构改造】香港vendor_b-games游戏启动页nginx兜底（后端无路由回vendor_b静态桶）.md
```
