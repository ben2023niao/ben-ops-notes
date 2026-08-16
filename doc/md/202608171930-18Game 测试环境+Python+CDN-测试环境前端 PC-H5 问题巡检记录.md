---
id: "doc-5c2ed1c0f380"
title: "测试环境前端 PC/H5 问题巡检记录"
date: "2026-08-17T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "CDN", "DNS", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_1930-%E3%80%90%E5%B7%A1%E6%A3%80%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E5%89%8D%E7%AB%AFPC-H5%E9%97%AE%E9%A2%98%E8%AF%8A%E6%96%AD.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_1930-【巡检记录】测试环境前端PC-H5问题诊断.md"
sourceSha256: "85d55f191d9f71df3d29c3a6e7099d6cd7f8bee2828f5454d8456e00c40bdc01"
sourceSystem: "project-doc"
---

# 测试环境前端 PC/H5 问题巡检记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-17_1930-【巡检记录】测试环境前端PC-H5问题诊断.md`

> 整理日期：2026-08-17 19:30｜日期依据：文件名日期

环境标签：测试环境 / H5 / PC / 域名 / DNS / SSR

时间：2026-08-17 19:30（Asia/Manila）

## 背景

刚修复测试环境上传 GIF 显示问题（`cdn_image` free/aws → `https://dd3tn75akeg7c.cloudfront.net`）。随后按用户要求巡检测试环境前端 PC 与 H5 是否存在其它问题。

## 巡检结果

### 问题 1：test-h5/test-pc 备案别名域名全部无法访问（DNS 解析失败）❌

| 域名 | 结果 |
| --- | --- |
| test-h5.hbabaxb.cn | 解析失败（CNAME 悬空） |
| test-pc.hbabaxb.cn | 解析失败（CNAME 悬空） |
| test-h5.hbazuua.cn | 解析失败（CNAME 悬空） |
| test-pc.hbazuua.cn | 解析失败（CNAME 悬空） |

- 证据：`hbabaxb.cn` / `hbazuua.cn` 的 NS 已是 DNSPod（a/b/c.dnspod.com），但 4 条测试别名仍 CNAME 指向 EdgeOne 内部域名 `*.eo.dnse4.com`，该名称当前无 A 记录 → 域名不可解析。
- 影响：H5/PC 备案入口全部打不开；只能走 `youdianse-test.xyz`。
- 修复建议：在 DNSPod 为这 4 条记录配置 A → `38.92.8.34`（或改为可解析 CNAME 目标），并补齐 test-h5/test-pc.hbazuua.cn 证书（历史 Hostname mismatch 一并处理）。

### 问题 2：H5 页面 SSR 极慢（14-25 秒）⚠️

| 页面 | 耗时 | 状态 |
| --- | --- | --- |
| https://h5.youdianse-test.xyz/ | ~14.8s | 200 |
| https://h5.youdianse-test.xyz/game | ~14.0s | 200 |
| https://h5.youdianse-test.xyz/game/detail/285 | ~24.6s | 200 |
| https://pc.youdianse-test.xyz/ | ~0.34s | 200 |
| /favicon.ico /robots.txt /sw.js /version.json | <0.3s | 200 |

- 结论：H5 页面 SSR 渲染极慢（约 14-25s），PC 首页 0.3s 正常，静态路径正常 → H5 SSR 页面依赖的某个上游调用慢（测试服务器侧需排查 H5 容器 SSR 的 API/媒体请求）。
- 建议：在测试服务器（38.92.8.34）检查 H5 容器 3003 的 SSR 上游请求（测试 API、uploads/media 域名 dd3tn75akeg7c/test-img），定位慢调用并优化；可能与 GIF 修复后的媒体域名/回源链路有关。

### 问题 3：test-img.*（token/t）链路新文件回退固定图（遗留项）⚠️

- GIF 修复文档已记录：test-img 代理上游（162.211.181.13）仍指向旧 `d1rct3ku9n07y3.cloudfront.net`，新上传文件会回退 13716 字节固定图。
- 建议：把 test-img 代理上游改为 `dd3tn75akeg7c.cloudfront.net`，使该链路也支持新文件；并留意 MediaTask 可能周期性回写 `cdn_image` free/aws。

## 正常项

- h5/pc.youdianse-test.xyz 版本文件 200；静态资源（favicon/robots/sw.js）正常。
- GIF 修复生效：`https://dd3tn75akeg7c.cloudfront.net/uploads/2026-08-15/d587e2791ea0e396cbece7e552ee3fcc.gif` HTTP 200。
- PC 页面 0.3s 正常。

## 结论

- 测试环境前端当前主要问题：① test-h5/test-pc 四个备案别名 DNS 悬空不可访问；② H5 页面 SSR 14-25s 极慢；③ test-img 链路新文件仍回退固定图（遗留）。
- 修复优先级：先修 DNS（DNSPod 加 A 记录），再排查 H5 SSR 慢调用，最后处理 test-img 上游与证书。
