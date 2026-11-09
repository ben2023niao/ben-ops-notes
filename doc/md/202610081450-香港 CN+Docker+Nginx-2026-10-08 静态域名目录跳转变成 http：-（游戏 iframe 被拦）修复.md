---
id: "doc-bf245aba6ab1"
title: "2026-10-08 静态域名目录跳转变成 http：//（游戏 iframe 被拦）修复"
date: "2026-10-08T14:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-08-1450-%E3%80%90%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E3%80%91%E9%9D%99%E6%80%81%E5%9F%9F%E5%90%8D%E7%9B%AE%E5%BD%95%E8%B7%B3%E8%BD%AC%E8%A2%AB%E5%86%99%E6%88%90http-absolute_redirect-off%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-08-1450-【故障处理】静态域名目录跳转被写成http-absolute_redirect-off修复.md"
sourceSha256: "7d1c2b876b7f59950a6abb59d9d4617a8f86c23a60528d982cb527ba1e6061ba"
sourceSystem: "project-doc"
---

# 2026-10-08 静态域名目录跳转变成 http：//（游戏 iframe 被拦）修复

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-10-08-1450-【故障处理】静态域名目录跳转被写成http-absolute_redirect-off修复.md`

> 整理日期：2026-10-08 14:50｜日期依据：文件名日期

## 一、现象

```text
用户给出大厅里失败的那条请求（iframe 导航）：
  GET https://vendor_b-static.k8x2v9.shop/csh/?apiId=10585&…&sip=vendor_b-games.k8x2v9.shop&gameID=2&lang=zh&…&provider_name=vendor_b
  （sec-fetch-dest: iframe / sec-fetch-mode: navigate / referer: https://97578aa.com/）
并指出：请求是 https，但「location 里面变成了 http」。
```

## 二、复现与根因

```text
修复前（经腾讯 EdgeOne 访问静态域名）：
  GET https://vendor_b-static.k8x2v9.shop/csh/?gameID=2&x=1  →  302
  location: http://vendor_b-static.k8x2v9.shop/csh/index.html?gameID=2&x=1      ← 绝对跳转且是 http
对比：直连本机 443 时 Location 是 https://…（所以只在边缘链路复现）。

根因：静态块的目录处理是 `rewrite ^(.+)/$ $1/index.html redirect;`，
      nginx 默认按 **$scheme** 生成**绝对** Location；而腾讯 EdgeOne 回源到本机走的是 HTTP
      → Location 写成 http:// → 页面本身是 https 的 iframe → 浏览器按混合内容/协议不一致拦掉 → 游戏进不去。
      （与 2026-10-08-1425 那条 X-Forwarded-Proto=http 是同一个「边缘回源是 HTTP」的根。）
```

## 三、修复

```text
静态 server 块统一加 `absolute_redirect off;`：nginx 生成的跳转改用**相对 Location**，
查询串保持原样（nginx 会自动带上原始 args）。

落点（5 处）：
  · snippets/bizops-hk-standby-vendor_b-static.conf       （vendor_b-static / vendor_b-static1）
  · snippets/bizops-hk-standby-gcs-static.conf        （v2~v5 分组）
  · nginx-standby.conf 的 m4q7z1 / k8x2v9 两个通用静态块
  · nginx-standby.conf 的 06/07 通用静态块

备份：bizops-hk-standby.conf.bak-20261008-1443-relredir、
      snippets/bizops-hk-standby-{vendor_b-static,gcs-static}.conf.bak-20261008-1443；nginx -t 通过后 reload（active）。
```

## 四、验证（线上实测）

| 请求 | 修复前 | 修复后 |
| --- | --- | --- |
| `vendor_b-static.k8x2v9.shop/csh/?gameID=2&x=1` | 302 `location: http://…` | 302 **`location: /csh/index.html?gameID=2&x=1`** |
| `vendor_b-static.m4q7z1.shop/csh/?…` | http | 相对 Location |
| `vendor_b-static2.k8x2v9.shop/csh/?…`（v2，GCS 分组） | http | 相对 Location |
| `vendor_b-static3-aws.hkcloudplay06.com/csh/?…`（v3，GCS 分组） | http | 相对 Location |
| `pg-static.m4q7z1.shop/csh/?…`（其它厂家通用块） | http | 相对 Location |
| 跟随跳转 `curl -L` | — | final_url = `https://vendor_b-static.k8x2v9.shop/csh/index.html?gameID=2&provider_name=vendor_b`，**200 / 34,239B** |
| 用户那条完整 `/csh/` URL（含 apiId/be/gs/sip/ssoKey…） | — | 302 + 相对 Location，**参数一个没丢** |

```text
补充：06/07 链路的静态域名走 Cloudflare Worker，Worker 里的目录跳转是用 `new URL(request.url)` 生成的
（request.url 是客户端 URL，https），本来就不会变 http，不受本问题影响。
```

## 五、关联

```text
docker/deploy/hongkong/nginx-standby.conf（3 处 absolute_redirect off）
docker/deploy/hongkong/nginx-standby-vendor_b-static.conf、nginx-standby-gcs-static.conf（各 1 处）
docker/doc/2026-10-08-1425-【故障处理】腾讯EdgeOne回源HTTP导致X-Forwarded-Proto为http（vendor_b进不去）修复.md
docker/doc/2026-10-08-1440-【故障处理】大厅拉起vendor_b失败-静态域名根探活403与v2-v5分组404修复.md
```
