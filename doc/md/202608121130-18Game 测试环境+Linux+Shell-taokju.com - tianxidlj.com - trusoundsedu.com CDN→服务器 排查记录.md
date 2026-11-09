---
id: "doc-4ba98757ee33"
title: "taokju.com / tianxidlj.com / trusoundsedu.com CDN→服务器 排查记录"
date: "2026-08-12T11:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "CDN", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1130-%E3%80%90%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95%E3%80%91taokju-tianxidlj-trusoundsedu-CDN%E5%9B%9E%E6%BA%90%E8%AF%8A%E6%96%AD.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1130-【排查记录】taokju-tianxidlj-trusoundsedu-CDN回源诊断.md"
sourceSha256: "568af97f2e1590f05e80e44ee0867b9dea208cf46a8f2df85f8fd65bbe63e857"
sourceSystem: "project-doc"
---

# taokju.com / tianxidlj.com / trusoundsedu.com CDN→服务器 排查记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121130-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-taokju.com%20-%20tianxidlj.com%20-%20trusoundsedu.com%20CDN%E2%86%92%E6%9C%8D%E5%8A%A1%E5%99%A8%20%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-12 11:30｜日期依据：文件名日期

环境标签：线上环境 / 前端域名维护 / AWS CDN / 16.208.38.88

时间：2026-08-12 11:30（Asia/Manila）

## 结论

服务器侧完全正常（证书、nginx、源站 HTTPS 均 OK）；问题出在 AWS CloudFront 回源协议配置为 HTTP（80），源站 80 端口强制 301 到 https，导致公网 HTTPS 访问循环跳转。

## 排查明细

### 1. DNS（公网）

| 域名 | 解析结果 |
| --- | --- |
| taokju.com | d1ptfbbusmbyd1.cloudfront.net（CloudFront 边缘 IP） |
| tianxidlj.com | donx8vz3b19um.cloudfront.net（CloudFront 边缘 IP） |
| trusoundsedu.com | dl4sgwlpppdd2.cloudfront.net（CloudFront 边缘 IP） |

✅ CDN 在入口。

### 2. 公网 HTTPS（经 CloudFront）

三个域名均为：

```
HTTP/2 301
location: https://<域名>/
server: nginx/1.18.0 (Ubuntu)
x-cache: Miss from cloudfront
via: <...>.cloudfront.net (CloudFront)
```

❌ 访问 https 却被源站 301 到同一个 https 地址，浏览器无限跳转循环。说明 CloudFront 用 HTTP（80）回源，源站 80 端口执行 `return 301 https://$host$request_uri` 后又把 301 返回给客户端。

### 3. 直连源站 16.208.38.88

```
taokju.com        https(443) 200，version.json=游点涩h5新线上
tianxidlj.com     https(443) 200，version.json=游点涩h5新线上
trusoundsedu.com  https(443) 200，version.json=游点涩h5新线上
```

✅ 源站 HTTPS 反代 H5 容器（3003）正常。

### 4. 服务器证书

| 域名 | CN / SAN | 到期 |
| --- | --- | --- |
| taokju.com | taokju.com | 2026-11-10 |
| tianxidlj.com | tianxidlj.com | 2026-11-10 |
| trusoundsedu.com | trusoundsedu.com | 2026-11-10 |

✅ 均为刚签发的 Let's Encrypt 证书。

### 5. nginx 配置

- `20-youdianse-prod-unified.conf` server_name 含三个域名 ✅
- 三个域名未在 `$h5pc_mode` maps 标注，走默认 h5 模式（直连验证正常）✅
- `location /` 中 `if ($scheme = http) { return 301 https://$host$request_uri; }` 为 80 端口强制 HTTPS 跳转，即循环跳转来源

## 修复方案

在 AWS CloudFront 控制台，把这 3 个域名对应 Distribution 的 **Origin Protocol Policy 改为 HTTPS only**（回源 `16.208.38.88:443`），保存后等待生效即可，服务器无需改动。

注意：此前 shouyek.com / shyssjt.com / syyhslzp.com 公网也出现过同样的 301 现象，建议按同方案一并检查修正。
