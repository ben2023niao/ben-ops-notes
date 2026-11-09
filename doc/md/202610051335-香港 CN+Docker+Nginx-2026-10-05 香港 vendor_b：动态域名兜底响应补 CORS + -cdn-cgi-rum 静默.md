---
id: "doc-e61fba52e9b8"
title: "2026-10-05 香港 vendor_b：动态域名兜底响应补 CORS + /cdn-cgi/rum 静默"
date: "2026-10-05T13:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "自动化", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-05-1335-%E3%80%90%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E3%80%91%E9%A6%99%E6%B8%AFvendor_b%E5%8A%A8%E6%80%81%E5%9F%9F%E5%90%8D%E5%85%9C%E5%BA%95%E5%93%8D%E5%BA%94%E8%A1%A5CORS%E4%B8%8Ecdn-cgi%E9%9D%99%E9%BB%98.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1335-【故障处理】香港vendor_b动态域名兜底响应补CORS与cdn-cgi静默.md"
sourceSha256: "60073dc5fe61b3564ce78ca10712970c3f519c4628c2a6b35b8aab097e543292"
sourceSystem: "project-doc"
---

# 2026-10-05 香港 vendor_b：动态域名兜底响应补 CORS + /cdn-cgi/rum 静默

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1335-【故障处理】香港vendor_b动态域名兜底响应补CORS与cdn-cgi静默.md`

> 整理日期：2026-10-05 13:35｜日期依据：文件名日期

## 一、这一轮开发给的三条请求

```text
1) 游戏页：https://vendor_b-static1.k8x2v9.shop/lj500/index.html?...&gameID=664&sip=vendor_b-games.k8x2v9.shop...
   （token iat=1791177292 → 会话时间 2026-10-05 13:14:52 北京）
2) curl https://vendor_b-games.k8x2v9.shop/lj500/  ← 带 key/token/lang/name，Origin=静态域名、
   referer=静态域名根、sec-fetch-mode: cors、sec-fetch-site: same-site
3) curl POST https://vendor_b-static1.k8x2v9.shop/cdn-cgi/rum   ← CF Web Analytics 探针（same-origin）
```

## 二、逐条核实（EdgeOne 链路 = k8x2v9 / m4q7z1）

| 请求 | 实测 | 说明 |
| --- | --- | --- |
| 游戏页 `/lj500/index.html` | 200 / 97,383B | 正常（vendor_b 自己桶） |
| `GET vendor_b-games.k8x2v9.shop/lj500/`（带 Origin） | **200 / 97,383B 但没有任何 CORS 头** | 该响应是 nginx 的静态兜底（@vendor_b_page_static1 从 S3 取游戏页），**后端加不了头**，浏览器 cors 模式会直接拦掉 → console 报跨域 |
| 同一条打 CF 链路 `vendor_b-games.hkcloudplay06.com/lj500/` | 404 / 14B + **完整 CORS 头**（回显 Origin、allow-credentials） | 这是后端自己产出的响应，头是全的 —— 两条链路行为不一致 |
| `POST /cdn-cgi/rum`（静态域名） | 405 / 368B | 页面里带 CF Web Analytics，在非 CF 域名上打到源站，console 一直报错 |

```text
附带核实：空 body 打 POST /lj500/req 的 500「Invalid IP.」仍是测试假象
（本机/私网源 → share.utils.get_real_ip 返回 None）；真实链路 X-Real-IP/XFF 都是公网，
同组合打 platform-api /what-is-my-ip 能正确回显。
另外日志里 05:1x 有 60 次 `GET /lj500/ 200 31411`（referer = 静态域名根，UA 是浏览器/自动化），
这些是 **200**、不是报错；我枚举了四个域名的静态/动态/socket 站点与全部后端端口都没复现出 31,411，
判断来自自动化浏览器巡检环境，先记录为待观察项。
```

## 三、修复（只动「nginx 自己产出的响应」，不改后端口径）

```text
1) 新增 snippets/bizops-hk-standby-vendor_b-cors.conf（回显 Origin + allow-credentials + Vary: Origin，
   与后端行为一致），在 m4q7z1 / k8x2v9 两个 vendor_b-games 块的
   @vendor_b_page_static1、@vendor_b_page_static0（共 4 处）include。
   —— 后端正常响应不经过这里，仍是后端自己加头（不违反「动态跨域归开发」的口径）。
2) snippets/bizops-hk-standby-vendor_b-static.conf 增加
   location = /cdn-cgi/rum { add_header ACAO "*"; return 204; }
   —— CF 探针在非 CF 域名上静默，不再刷 console（探针数据本来也不经我们统计）。

备份：bizops-hk-standby.conf.bak-20261005-1318-vendor_bcors +
      snippets/bizops-hk-standby-vendor_b-static.conf.bak-20261005-1318；nginx -t 通过后 reload。
```

## 四、验证（经 EdgeOne）

| 请求 | 结果 |
| --- | --- |
| `GET vendor_b-games.k8x2v9.shop/lj500/` + `Origin: https://vendor_b-static1.k8x2v9.shop` | 200 + `access-control-allow-origin: <回显>` + `allow-credentials: true` + `vary: Origin` |
| 同上打 m4q7z1（Origin=静态域名） | 200 + 同样三个头 |
| 不带 Origin 请求 | 200，**不输出** `access-control-allow-origin`（空值不写头） |
| `POST /cdn-cgi/rum`（vendor_b-static1.k8x2v9.shop） | 405 → **204** |
| `/lj500/index.html` / `/lj500/vendor_b_NEW.png` / `/lj500/src/polyfills.bundle.5adbf.js` | 200（97,383 / 242,584 / 14,750） |
| `/astarte/3.6/web-mobile/assets/versions.json`、`OPTIONS`、`/zh-CN/intro`、`/health` | 200 / 204 / 200 / 200（均无回归） |

## 五、关联

```text
docker/deploy/hongkong/nginx-standby-vendor_b-cors.conf（新增）
docker/deploy/hongkong/nginx-standby-vendor_b-static.conf（/cdn-cgi/rum 204）
docker/deploy/hongkong/nginx-standby.conf（4 处 include）
docker/doc/2026-10-05-1320-【故障处理】香港vendor_b游戏资源403定位与vendor_a前缀兜底修复.md（上一轮：资源兜底）
```
