---
id: "doc-6c7080ecfae6"
title: "2026-10-05 香港 vendor_b 游戏打不开：资源 403 定位 + 回退老 vendor_a 前缀修复"
date: "2026-10-05T13:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-05-1320-%E3%80%90%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E3%80%91%E9%A6%99%E6%B8%AFvendor_b%E6%B8%B8%E6%88%8F%E8%B5%84%E6%BA%90403%E5%AE%9A%E4%BD%8D%E4%B8%8Evendor_a%E5%89%8D%E7%BC%80%E5%85%9C%E5%BA%95%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1320-【故障处理】香港vendor_b游戏资源403定位与vendor_a前缀兜底修复.md"
sourceSha256: "a1a6e14add3386c3aead837d19c8a954f6dcc63a3dfbaf6656ddaa7356d326b2"
sourceSystem: "project-doc"
---

# 2026-10-05 香港 vendor_b 游戏打不开：资源 403 定位 + 回退老 vendor_a 前缀修复

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1320-【故障处理】香港vendor_b游戏资源403定位与vendor_a前缀兜底修复.md`

> 整理日期：2026-10-05 13:20｜日期依据：文件名日期

## 一、现象与线索

```text
开发（C++）反馈：「vendor_b 这个游戏还是报错」，给了两条线索：
  1) 游戏页：https://vendor_b-static1.k8x2v9.shop/lj500/index.html?...&gameID=664&name=lj500&lang=cn...
  2) 一条 curl：GET https://vendor_b-games.m4q7z1.shop/lj500/ 带 key/token/lang/name/referer/origin
     （origin/referer = https://vendor_b-static1.k8x2v9.shop，sec-fetch-site: cross-site）
token 里的 iat=1791176375 / exp=1791176985 → 会话时间 2026-10-05 12:59:35 ~ 13:09:45（北京）。
```

## 二、定位过程（先排除误判）

```text
1) 页面与映射本身没问题：
     vendor_b-static1.k8x2v9.shop/lj500/index.html = 200 / 97,383B（vendor_b 自己的大阪桶）
     /lj500/ = 302 -> /lj500/index.html；主 JS /commom_v3_1.0.9.js = 200 / 45,119B（MIME 正确）
     vendor_b-games.<域>/health = 200
2) POST /lj500/req 用空 body 测出的 500「Invalid IP.」是**我自己的测试假象**：
     · 直接打后端（源码 192.0.2.1 → 私网）时 share.utils.get_real_ip 返回 None → 抛 Invalid IP
     · 用 tcpdump 抓真实链路：后端收到的是 X-Real-IP: 43.168.x（EdgeOne 公网）、
       X-Forwarded-For: 112.207.x, 43.168.x，都是公网；用同组合打 platform-api
       /what-is-my-ip 能正确回显公网 IP → 链路 IP 传递没问题
     · 再用空 body 打 /lj500/req 时后端报的是 protobuf 解码失败（serverProto.Request），
       即空 body 本来就该失败 —— 不是游戏的问题
     · 容器 mmdb、share.so（md5 e5589555…）、start.sh 与巴西源端一致，均无差异
3) 真正在报错的是**静态资源 403**。按开发会话窗口（04:55–05:12 UTC）过滤 standby nginx：
     41 × 403  /astarte/3.6/web-mobile/assets/vendor_b/native/**（4 个文件反复重试）
      5 × 403  /csh/htt/smallicon/setting.json
      4 × 403  /lj500/favicon0.ico
      7 × 404  /lj500/src/{polyfills,system}.bundle.*.js、/lj500/TaDa_Logo_APNG_s.png、
               /lj500/vendor_b_NEW.png、/lj500/Intro_ProgressBar*(_Bottom)_vendor_b.png
     16 × 405  /cdn-cgi/rum（Cloudflare RUM 探针，无害）
      3 × 500  /lj2/req
4) 这些资源去哪儿了？实测各个源：
     · vendor_b 大阪桶 bizops-s3-vendor_b-static1：只有 lj500/index.html 和 astarte/…/vendor_b/index.8c409.js 等，
       **没有** /lj500/src/*.js、logos、intro 图片 → 403
     · 老 HK 主桶 bizops-h5-hk-517506432530 的 vendor_a-statics1 / vendor_a-statics2 前缀：
       `vendor_a-statics1/lj500/src/polyfills.bundle.5adbf.js` = 200 / 14,750B
       `vendor_a-statics1/lj500/src/system.bundle.692e9.js` = 200 / 12,028B
       `vendor_a-statics1/lj500/Intro_ProgressBar_vendor_b.png` = 200 / 1,003B
       `vendor_a-statics2/lj500/TaDa_Logo_APNG_s.png` = 200 / 41,805B
       `vendor_a-statics2/lj500/vendor_b_NEW.png` = 200 / 242,584B
     → 即：**游戏页从 vendor_b 新桶加载，但同目录的其余资源还留在老的 vendor_a 前缀里**
       （老映射本来就是 vendor_b-static -> vendor_a-statics、vendor_b-static1 -> vendor_a-statics1）。
```

## 三、修复（standby nginx，vendor_b 静态域名）

```text
思路：vendor_b 自己的桶优先（内容正确），**缺的对象再回退老 vendor_a 前缀**（补资源缺口），
      不改变「vendor_b 优先」的口径，也不影响其它厂家。

改动 1：nginx-standby.conf 新增 map（按 server_name 捕获的前缀选老前缀）
  map $bizops_static_prefix $bizops_vendor_b_vendor_a_prefix {
      default          "___noprefix___";   # 其它前缀兜底链最终 403（等于查不到）
      vendor_b-static      vendor_a-statics;
      vendor_b-static1     vendor_a-statics1;
  }

改动 2：snippets/bizops-hk-standby-vendor_b-static.conf
  · location /、/static/images/intro/、= /astarte/.../versions.json 都加
        proxy_intercept_errors on; error_page 403 404 = @vendor_b_vendor_a_fallback;
  · 自己再定义一个 location ~* \.js$（放在通用 static-extra 片段之后，正则先匹配先赢）：
    与通用片段同口径（OPTIONS 204 / 强制 application/javascript; charset=utf-8 / CORS *），
    但回源失败时也走 @vendor_b_vendor_a_fallback —— 否则 /lj500/src/*.bundle.js 会被通用 .js 规则抢先处理，回退不生效
  · 新增 @vendor_b_vendor_a_fallback：rewrite 成 /<vendor_a 前缀><原 URI>，回源 HK 主桶（ap-east-1）

备份：/etc/nginx/sites-available/bizops-hk-standby.conf.bak-20261005-1311-vendor_bvendor_a +
      /etc/nginx/snippets/bizops-hk-standby-vendor_b-static.conf.bak-20261005-1311；nginx -t 通过后 reload。
```

## 四、验证（经 EdgeOne 公网，vendor_b-static1.k8x2v9.shop）

| 请求 | 修复前 | 修复后 |
| --- | --- | --- |
| `/lj500/src/polyfills.bundle.5adbf.js` | 404 | **200 / 14,750B（application/javascript; charset=utf-8）** |
| `/lj500/src/system.bundle.692e9.js` | 404 | **200 / 12,028B** |
| `/lj500/TaDa_Logo_APNG_s.png` | 404 | **200 / 41,805B（image/png）** |
| `/lj500/vendor_b_NEW.png` | 404 | **200 / 242,584B** |
| `/lj500/Intro_ProgressBar_vendor_b.png` | 404 | **200 / 1,003B** |
| `/lj500/Intro_ProgressBar_Bottom_vendor_b.png` | 404 | **200 / 1,013B** |
| `/lj500/index.html` | 200 / 97,383B（vendor_b 自己） | 200 / 97,383B（**仍优先用 vendor_b 自己的**，不是 vendor_a 的 98,564B） |
| `/ifff/index.html` | 200 / 34,238B | 200 / 34,238B |
| `/lj500/` 目录 | 302 | 302 |
| `OPTIONS /lj500/index.html` | 204 | 204 |
| `/x/customizations.info` | 200 空 | 200 空 |
| `/astarte/3.6/web-mobile/assets/versions.json` | 200 | 200 |
| `/zh-CN/intro?game=664` +Referer | 200 / 13,473B | 200 / 13,473B |
| 其它厂家：`pg-static/lj500/src/...`、`pg-static/zh-CN/intro` | 403 | **403（未受影响）** |
| 06/07 兜底块（Host 直连本机）：vendor_b-static1.hkcloudplay06.com 同路径 | 403 | **200 / 14,750B** |

## 五、仍然缺的资源（需要开发补，nginx 无法兜）

```text
这几个路径在**所有源**里都不存在（vendor_b 大阪桶 / HK 主桶 vendor_a-statics1-5 / GCS 全试过）：
  /astarte/3.6/web-mobile/assets/vendor_b/native/1a/1a23e78f3.d3fbc.webp      ← 41 次 403
  /astarte/3.6/web-mobile/assets/vendor_b/native/1c/1c8b28224.eabe3.webp
  /astarte/3.6/web-mobile/assets/vendor_b/native/29/299d2d3a-…-70d88dda59fd.23b03.png
  /astarte/3.6/web-mobile/assets/vendor_b/native/fd/fd30e95d-…-fc4fdd3051b8.bb552.webp
  /csh/htt/smallicon/setting.json                                        ← 5 次 403
  /lj500/favicon0.ico                                                    ← 4 次 403（vendor_a 前缀也没有，影响小）
两个注意点：
  · 06/07 的静态域名走 Cloudflare Worker（不经过本机 nginx），本轮的 nginx 兜底对它们无效，
    要么让开发把这些资源也传到 vendor_b 大阪桶，要么改 Worker；
  · 若同一路径 vendor_b 桶与 vendor_a 前缀都存在，**永远是 vendor_b 桶优先**（本轮设计如此）。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf（新增 map $bizops_static_prefix $bizops_vendor_b_vendor_a_prefix）
docker/deploy/hongkong/nginx-standby-vendor_b-static.conf（.js 独立 location + @vendor_b_vendor_a_fallback）
docker/doc/2026-10-05-1400-【架构改造】香港vendor_b静态域名按Worker路径映射并补intro-astarte处理.md（同一天的映射改造）
docker/doc/2026-10-05-1230-【架构改造】香港nginx的vendor_b静态改为走自己的大阪桶（对齐香港Worker）.md
```
