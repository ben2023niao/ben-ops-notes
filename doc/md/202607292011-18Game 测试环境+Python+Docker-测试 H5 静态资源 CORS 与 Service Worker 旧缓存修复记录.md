---
id: "doc-df0c10a6f960"
title: "测试 H5 静态资源 CORS 与 Service Worker 旧缓存修复记录"
date: "2026-07-29T20:11:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "自动化", "CDN", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2011-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E6%B5%8B%E8%AF%95H5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CORS%E4%B8%8EServiceWorker%E6%97%A7%E7%BC%93%E5%AD%98%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2011-【修复Bug+网络调整】测试H5静态资源CORS与ServiceWorker旧缓存修复记录.md"
sourceSha256: "ddb195372b6beec5957ae81275ce5adbed1c4e1049e60a1a3187fd27ee728911"
sourceSystem: "project-doc"
---

# 测试 H5 静态资源 CORS 与 Service Worker 旧缓存修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607292011-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BDocker-%E6%B5%8B%E8%AF%95%20H5%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%20CORS%20%E4%B8%8E%20Service%20Worker%20%E6%97%A7%E7%BC%93%E5%AD%98%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 20:11｜日期依据：文件名日期

环境标签：测试环境

## 基本信息

- 时间：2026-07-29 20:11
- 分类：修复 Bug、网络调整
- 环境：测试环境-游点涩-h5
- 页面入口：https://h5.youdianse-test.xyz/
- 备案入口：https://test-h5.hbabaxb.cn/
- 腾讯静态资源域名：https://test-h5-s3.hbabaxb.cn/
- 腾讯 COS 桶：18game-nuxt-static-test-h5-sg-1450169938
- COS 地域：ap-singapore
- 发布版本：fe30810
- 通知群：稳定备案域名+腾讯云原厂

## 问题现象

- H5 页面进入部分页面后样式异常、页面发黑或资源加载不完整。
- 浏览器 F12 看到 `test-h5-s3.hbabaxb.cn` 的 `_nuxt/*.css`、`_nuxt/*.js`、`images/*` 有 CORS 报错或 5xx/连接异常。
- 截图中部分请求来自 Service Worker，说明浏览器可能仍在请求旧缓存里的历史 chunk。

## 原因判断

- H5 静态 COS / EdgeOne 链路之前返回固定 `Access-Control-Allow-Origin: https://h5.youdianse-test.xyz`。
- 当页面通过备案入口或新增域名访问时，浏览器 Origin 不一致，会拦截 CSS/JS。
- H5 浏览器 Service Worker 可能还保留旧 HTML/chunk 引用，继续请求历史构建文件。
- 旧报错文件中有大小写不一致或历史构建文件，例如 `_nuxt/index.Csv-yEZN.css`；当前实际存在文件为 `_nuxt/index.CSv-yEZN.css`。

## 处理步骤

1. 在飞机群同步开始排查 H5 页面异常。
2. 检查页面入口和备案入口，确认两者均能返回 200。
3. 抽查 `test-h5-s3.hbabaxb.cn` 静态资源响应头，确认 CORS 返回固定旧 Origin。
4. 将 H5 前端新加坡 COS 桶 CORS 调整为：
   - AllowedOrigin：`*`
   - AllowedMethod：`GET, HEAD`
   - AllowedHeader：`*`
   - ExposeHeader：`ETag, Content-Length, Content-Type`
   - MaxAgeSeconds：86400
5. 同步将 PC 前端新加坡 COS 桶 CORS 调整为同一规则，避免 PC 后续新增页面域名再遇到同类问题。
6. 对 H5 静态资源域名执行 EdgeOne 刷新：
   - `_nuxt/`
   - `images/`
   - `sw.js`
   - `workbox-9031cd5a.js`
   - `manifest.webmanifest`
   - `test-h5-s3.hbabaxb.cn` host 级刷新
7. 重新触发 `测试环境-游点涩-h5-发版`，版本 `fe30810`。
8. 发布流程完成 AWS S3 同步、腾讯 COS 同步、Docker 构建、容器启动和腾讯 CDN 刷新。

## 验证结果

- `https://h5.youdianse-test.xyz/`：200
- `https://test-h5.hbabaxb.cn/`：200
- `https://h5.youdianse-test.xyz/version.txt`：200，版本 `fe30810`
- `https://test-h5-s3.hbabaxb.cn/version.txt`：200，版本 `fe30810`
- 当前 H5 页面引用腾讯静态资源数：107
- 当前 H5 页面 CSS/JS 引用数：71
- 以 `Origin: https://h5.youdianse-test.xyz` 抽测当前 71 个 CSS/JS：全部 `206 + Access-Control-Allow-Origin: *`
- 以 `Origin: https://test-h5.hbabaxb.cn` 抽测关键 CSS/JS：`206 + Access-Control-Allow-Origin: *`
- 截图涉及的当前文件 `_nuxt/index.CSv-yEZN.css`：206
- 截图中大小写不一致旧文件 `_nuxt/index.Csv-yEZN.css`：404，判断为历史缓存或旧 Service Worker 引用。

## 后续注意

- H5 当前不启用腾讯静态资源 token 鉴权，避免影响测试中页面。
- 如果个人浏览器仍看到旧 chunk 报错，需要清理该站点缓存或注销 Service Worker 后强刷。
- 后续新增 H5/PC 页面域名时，不需要再逐个给 COS CORS 加 Origin，前端静态域统一由 `Access-Control-Allow-Origin: *` 兼容。
- EdgeOne 个别节点抽测时出现过连接 reset/timeout，但重试能返回 206；需要继续观察，如重复出现再联系腾讯云排查边缘节点链路。
