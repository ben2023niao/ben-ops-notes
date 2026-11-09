---
id: "doc-444f40331ee2"
title: "测试 PC 静态资源 CORS 与图片大小写兼容修复"
date: "2026-08-04T15:29:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Python", "Docker", "Nginx", "自动化", "CDN", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1529-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E6%A0%B9%E5%9B%A0%E6%B1%87%E6%80%BB%E3%80%91%E6%B5%8B%E8%AF%95PC%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CORS%E4%B8%8E%E5%9B%BE%E7%89%87%E5%A4%A7%E5%B0%8F%E5%86%99%E5%85%BC%E5%AE%B9%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1529-【修复Bug+根因汇总】测试PC静态资源CORS与图片大小写兼容修复.md"
sourceSha256: "3b8126c4e143056cee8e104360bd183816ec76dfddb34dabf2ffd62d980164e8"
sourceSystem: "project-doc"
---

# 测试 PC 静态资源 CORS 与图片大小写兼容修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608041529-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BPython-%E6%B5%8B%E8%AF%95%20PC%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%20CORS%20%E4%B8%8E%E5%9B%BE%E7%89%87%E5%A4%A7%E5%B0%8F%E5%86%99%E5%85%BC%E5%AE%B9%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-08-04 15:29｜日期依据：文件名日期

环境标签：测试环境、游点涩、PC、H5、前端静态资源、AWS S3、腾讯 COS、EdgeOne、CORS、图片资源

记录时间：2026-08-04 15:29

## 核心原因

本轮用户截图里的红色资源错误不是单一原因，主要由两类问题叠加：

1. `test-pc-s3.hbabaxb.cn/_nuxt/*.css` 一度在浏览器侧显示 CORS 拦截。本轮复查时，带 `Origin: https://pc.youdianse-test.xyz` 请求已能返回 `Access-Control-Allow-Origin: *`，说明当前 COS CORS 配置本身已生效；用户截图更像是浏览器缓存、Service Worker 或 EdgeOne 边缘节点仍持有旧响应头导致的残留现象。
2. PC 页面部分图片路径存在大小写不一致：
   - 实际对象存在：`/images/index-new/iOS.svg`
   - 浏览器/旧资源请求：`/images/index-new/ios.svg`
   - 实际对象存在：`/images/sidebar/sidebar-download.webp`
   - 浏览器/旧资源请求：`/images/sidebar/sidebar-downLoad.webp`

第二类是本次明确可修复的核心问题。Linux、S3、COS 对对象名大小写敏感，旧路径对象不存在时，PC 源站 Nginx 又把 `/images/` 反代到 `test-pc-s3.hbabaxb.cn`，所以浏览器看到的表现可能是 404、524、554 或请求超时。

## 本次操作

已读取 workbench 与历史文档，确认当前规则：

- PC/H5 前端构建静态资源走 `test-*-s3.hbabaxb.cn`。
- `_nuxt`、JS、CSS、前端内置图片不做 token 鉴权。
- PC 页面同源 `/images/` 会反代到 `https://test-pc-s3.hbabaxb.cn`。

已修改发布模板：

- 文件：`devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_templates.py`
- 变更：`pnpm build` 后、S3/COS 同步前自动生成兼容别名：
  - 若存在 `.output/public/images/index-new/iOS.svg` 且不存在 `ios.svg`，复制生成 `ios.svg`。
  - 若存在 `.output/public/images/sidebar/sidebar-download.webp` 且不存在 `sidebar-downLoad.webp`，复制生成 `sidebar-downLoad.webp`。
- 文件：`devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_config.py`
- 变更：schema 升级为 `tooling-v22-static-alias`，强制 PC 重新构建，不复用旧镜像。

## 发布执行

- 发布入口：`测试环境-游点涩-pc-发版`
- 发布 commit：`c842f12`
- 触发标记：`codex-static-alias-fix`
- 发布结果：
  - Docker 重新构建成功。
  - 构建日志确认已复制 `iOS.svg -> ios.svg`。
  - 构建日志确认已复制 `sidebar-download.webp -> sidebar-downLoad.webp`。
  - AWS S3 静态资源同步成功。
  - 腾讯 COS 静态资源同步成功。
  - EdgeOne/CDN 刷新成功，JobId：`3td1dngmeazb`。
  - PC 测试容器启动成功。

## 验证结果

| 验证项 | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/images/index-new/ios.svg` | 200，可完整下载，大小 7055 bytes |
| `https://test-pc-s3.hbabaxb.cn/images/index-new/ios.svg` | HEAD 200，CORS 头存在；HTTP/2 重试可完整下载 |
| `https://pc.youdianse-test.xyz/images/sidebar/sidebar-downLoad.webp` | 200，可完整下载，大小 14106 bytes |
| `https://test-pc-s3.hbabaxb.cn/images/sidebar/sidebar-downLoad.webp` | 200，可完整下载，大小 14106 bytes |
| `https://test-pc-s3.hbabaxb.cn/_nuxt/c-image.CpoeIJpi.css` | 200，`Access-Control-Allow-Origin: *`，可完整下载 |
| `https://test-pc-s3.hbabaxb.cn/_nuxt/c-common-dialog.C5YdnXTs.css` | 200，`Access-Control-Allow-Origin: *`，可完整下载 |
| `https://test-h5-s3.hbabaxb.cn/_nuxt/entry.9fJ8Knpu.css` | 200，`Access-Control-Allow-Origin: *`，可完整下载 |
| `https://pc.youdianse-test.xyz/` | 200，HTML 可完整下载 |
| `https://h5.youdianse-test.xyz/` | 200，HTML 可完整下载 |
| `https://test-pc.hbabaxb.cn/` | 200，HTML 可完整下载 |
| `https://test-h5.hbabaxb.cn/` | 200，HTML 可完整下载 |

重试观察：

- `test-pc-s3.hbabaxb.cn/images/index-new/ios.svg` 对象已存在，HTTP/2 连续重试成功。
- HTTP/1.1 直连该静态域偶发 `Empty reply from server`，判断为 EdgeOne/COS 边缘连接抖动观察项，不是对象缺失。

## 处理建议

- 用户浏览器若仍看到旧 CORS 红错，先清浏览器缓存、强制刷新，必要时清 Service Worker。
- 若仍能复现，保留失败请求的具体 URL、时间、Request ID、边缘 IP，再提交腾讯云侧查边缘节点。
- 后续前端代码最好统一文件名大小写，避免依赖兼容别名长期兜底。

## 群通知记录

2026-08-04 15:32 已将最终汇总和本文件发送到：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

## 结论

本次核心问题已定位并修复：PC 图片资源的大小写不一致导致兼容路径缺失，叠加 `/images/` 同源反代和 EdgeOne 边缘缓存/连接表现，最终在浏览器中体现为 524、554、超时或资源加载失败。现已通过发布模板自动生成兼容别名并重新发布 PC，缺失的两个图片路径已恢复；CSS CORS 当前验证为正常。
