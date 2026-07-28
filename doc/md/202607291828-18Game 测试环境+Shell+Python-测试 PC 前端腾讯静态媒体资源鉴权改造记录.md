---
id: "doc-254b6fbf4ab0"
title: "测试 PC 前端腾讯静态媒体资源鉴权改造记录"
date: "2026-07-29T18:28:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1828-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%2B%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%89%8D%E7%AB%AF%E8%85%BE%E8%AE%AF%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E9%89%B4%E6%9D%83%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1828-【架构改造+安全优化】测试PC前端腾讯静态资源鉴权改造记录.md"
sourceSha256: "d8af24e9387fc5b36abcc5f1290838c269466dde49e612ea1bab4defb253e88f"
sourceSystem: "project-doc"
---

# 测试 PC 前端腾讯静态媒体资源鉴权改造记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1828-【架构改造+安全优化】测试PC前端腾讯静态资源鉴权改造记录.md`

> 整理日期：2026-07-29 18:28｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 18:28
分类：架构改造 / 安全优化 / 测试环境
范围：测试环境-游点涩-pc-发版、`test-pc-s3.hbabaxb.cn`

状态更新：2026-07-29 21:19 已回退前端静态资源鉴权，当前有效方案以 `2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md` 为准。

## 背景

测试 PC 前端静态资源链路：

- 页面入口：`https://pc.youdianse-test.xyz/`
- 备案入口：`https://test-pc.hbabaxb.cn/`
- 腾讯静态资源域名：`https://test-pc-s3.hbabaxb.cn`
- AWS 公开桶：`s3://18game-nuxt-static-test-pc`，区域 `ap-southeast-1`
- 腾讯 COS 私有桶：`18game-nuxt-static-test-pc-sg-1450169938`，区域 `ap-singapore`

最初评估过对 JS/CSS/图片全部加签，但测试环境和线上入口域名会不断新增，JS/CSS 跨域如果按入口域名逐个放行，后续维护成本过高，且容易再次出现 CORS 问题。

最终策略调整为：只保护图片、视频、图标这类静态媒体资源；JS/CSS 保持普通公开加载和通配 CORS。

## 最终方案

采用腾讯 EdgeOne URL 鉴权 Method D，仅作用于 `test-pc-s3.hbabaxb.cn` 的媒体资源路径。

- URL 格式：`https://test-pc-s3.hbabaxb.cn/path/file.webp?敏感凭据：[已脱敏]
- 签名算法：`md5(KEY + Path + t)`
- 有效期：30 天
- 签名 Key 只在机器人环境变量中维护，不提交 Git，不写文档明文，不写日志
- JS/CSS 不加签，不进入 EdgeOne 鉴权规则
- 新增页面入口域名时不需要额外加 CORS 白名单

受保护路径：

- `/images/`
- `/image/`
- `/video/`
- `/videos/`
- `/media/`
- `/favicon.ico`
- `/192.png`
- `/512.png`

受保护后缀：

- 图片：`png`、`jpg`、`jpeg`、`webp`、`gif`、`svg`、`ico`、`avif`、`bmp`、`tif`、`tiff`
- 视频：`mp4`、`webm`、`mov`、`m4v`、`m3u8`、`ts`、`avi`、`mkv`

## 发布链路

1. Nuxt 正常构建 `.output/public`
2. 同步原始 `.output/public` 到 AWS S3，保持 AWS 公开桶兼容
3. 对 `.output` 内引用腾讯静态域名的媒体资源做 `token/t` 改写
4. 同步改写后的 `.output/public` 到腾讯新加坡 COS
5. 容器使用改写后的 `.output`
6. 发布完成后刷新腾讯 EdgeOne/CDN 缓存

## 代码改造点

- `remote_youdianse_h5_config.py`
  - 默认签名前缀改为媒体路径
  - 镜像结构版本更新为 `tooling-v18-tencent-auth-media-only`
- `remote_youdianse_h5_templates.py`
  - 签名脚本只判断媒体后缀
  - 保留 HTML/JS/CSS/JSON 等文本文件扫描能力，用来发现其中引用的媒体 URL
  - 不再签 JS、CSS、字体、manifest、source map
- `测试环境-游点涩-pc-发版/benbot_plugin.py`
  - PC 按钮发布默认启用媒体资源签名
- `测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py`
  - PC 发布入口默认传入媒体签名前缀

## EdgeOne 规则

由于 EdgeOne API 单条规则最多 1 个 branch，最终创建 6 条小规则：

- `test-pc-s3-media-auth-images`：`rule-3t4pph3d8mka`
- `test-pc-s3-media-auth-image`：`rule-3t4ppi0dwb0g`
- `test-pc-s3-media-auth-video`：`rule-3t4ppj0qf48q`
- `test-pc-s3-media-auth-videos`：`rule-3t4ppjup78c7`
- `test-pc-s3-media-auth-media`：`rule-3t4ppkqvw5yy`
- `test-pc-s3-media-auth-root-icons`：`rule-3t4pplkkooon`

条件格式：

```text
${http.request.host} in ['test-pc-s3.hbabaxb.cn']
and ${http.request.uri.path} matches '^/images/'
and ${http.request.file_extension} in ['png','jpg','jpeg','webp','gif','svg','ico','avif','bmp','tif','tiff','mp4','webm','mov','m4v','m3u8','ts','avi','mkv']
```

其他路径同理替换路径前缀。

## 验证记录

发布时间：2026-07-29 19:22
发布入口：测试环境-游点涩-pc-发版
发布结果：成功
git 短 ID：`32ecf54`

页面验证：

- `https://pc.youdianse-test.xyz/`：200
- `https://test-pc.hbabaxb.cn/`：200
- `https://test-pc-s3.hbabaxb.cn/version.txt`：200

HTML 资源统计：

- 腾讯静态资源引用：99
- JS/CSS 引用：81
- JS/CSS 带 token：0
- 媒体资源引用：17
- 媒体资源带 token：17

EdgeOne 鉴权验证：

- JS/CSS：200
- 带 token 图片：200
- 去掉 token 的同一张图片：403

## 注意事项

- 后端 uploads 图片、APK/App 包仍走测试后端老 AWS S3，不属于本次 PC 前端静态资源桶。
- H5 当前仍在测试，不在本次行为改造范围内。
- 后续如果要扩展到 H5 或线上，需要先确认对应静态资源域名和 EdgeOne 规则，不要直接复用测试 PC 规则。
- 腾讯 COS 桶继续保持私有，公网访问只走 EdgeOne 域名。

## 飞机群通知

目标群：稳定备案域名+腾讯云原厂

已通知：

- 确认改造范围为测试 PC
- 调整方案为只加密图片/视频媒体资源
- ben-bot 重建启动成功
- 测试 PC 发布完成
- EdgeOne 媒体鉴权规则创建完成
- 验证结果：JS/CSS 200，带 token 图片 200，无 token 图片 403
