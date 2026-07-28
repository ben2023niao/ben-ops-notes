---
id: "doc-cacca42e5c7e"
title: "测试 PC 前端媒体资源 Token 鉴权落地验证记录"
date: "2026-07-29T19:32:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1932-%E3%80%90%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%89%8D%E7%AB%AF%E5%AA%92%E4%BD%93%E8%B5%84%E6%BA%90Token%E9%89%B4%E6%9D%83%E8%90%BD%E5%9C%B0%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1932-【安全优化+架构改造】测试PC前端媒体资源Token鉴权落地验证记录.md"
sourceSha256: "1942c8b0b3b15080ded7a0ec5a24d840bf77dfa98cb60f054b3e37e2066b219b"
sourceSystem: "project-doc"
---

# 测试 PC 前端媒体资源 Token 鉴权落地验证记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1932-【安全优化+架构改造】测试PC前端媒体资源Token鉴权落地验证记录.md`

> 整理日期：2026-07-29 19:32｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 19:32
分类：安全优化 / 架构改造 / 测试环境
范围：测试环境-游点涩-pc-发版、`test-pc-s3.hbabaxb.cn`

状态更新：2026-07-29 21:19 已回退前端静态资源 Token 鉴权，当前有效方案以 `2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md` 为准。

## 结论

测试 PC 已完成简化版静态资源鉴权：

- JS/CSS 不加密，避免新增页面域名时反复维护 CORS 白名单
- 图片、视频、图标类媒体资源加 `token/t`
- EdgeOne 只对 `test-pc-s3.hbabaxb.cn` 的媒体资源路径做 Token 鉴权
- 测试 PC 按钮发布和 webhook 发布共用同一套脚本，后续发布会自动走同样逻辑

## 当前链路

页面域名：

- AWS/现入口：`https://pc.youdianse-test.xyz/`
- 备案入口：`https://test-pc.hbabaxb.cn/`

前端静态资源：

- 展示域名：`https://test-pc-s3.hbabaxb.cn`
- AWS 公开桶：`s3://18game-nuxt-static-test-pc`，`ap-southeast-1`
- 腾讯 COS 私有桶：`18game-nuxt-static-test-pc-sg-1450169938`，`ap-singapore`
- EdgeOne CNAME：`test-pc-s3.hbabaxb.cn.eo.dnse4.com`

## 本次操作

1. 调整发布脚本签名前缀，只覆盖媒体路径：
   - `/images/`
   - `/image/`
   - `/video/`
   - `/videos/`
   - `/media/`
   - `/favicon.ico`
   - `/192.png`
   - `/512.png`
2. 调整签名脚本后缀判断，只处理图片和视频类文件。
3. 同步脚本到 ben-bot 服务器并重建启动 `ben-bot`。
4. 触发 `测试环境-游点涩-pc-发版`，git 短 ID：`32ecf54`。
5. 发布过程中完成 AWS S3 同步、腾讯新加坡 COS 同步、腾讯 CDN 刷新。
6. 创建 EdgeOne 媒体资源鉴权规则。
7. 验证页面、资源和无签访问拦截结果。

## EdgeOne 规则

站点：`hbabaxb.cn`
ZoneId：`zone-3t1w9ksp60nn`
域名：`test-pc-s3.hbabaxb.cn`

规则：

- `/images/`：`rule-3t4pph3d8mka`
- `/image/`：`rule-3t4ppi0dwb0g`
- `/video/`：`rule-3t4ppj0qf48q`
- `/videos/`：`rule-3t4ppjup78c7`
- `/media/`：`rule-3t4ppkqvw5yy`
- 根目录图标：`rule-3t4pplkkooon`

Method：EdgeOne URL 鉴权 Method D
签名参数：`token`
时间参数：`t`
有效期：30 天
签名 Key：仅服务器私密环境变量维护，文档不记录明文。

## 验证结果

页面访问：

- `https://pc.youdianse-test.xyz/`：200
- `https://test-pc.hbabaxb.cn/`：200
- `https://test-pc-s3.hbabaxb.cn/version.txt`：200

页面 HTML 统计：

- 腾讯静态资源引用：99
- JS/CSS 引用：81
- JS/CSS 带 token：0
- 媒体资源引用：17
- 媒体资源带 token：17

单资源验证：

- `https://test-pc-s3.hbabaxb.cn/_nuxt/entry.DnB0JDod.css`：200
- `https://test-pc-s3.hbabaxb.cn/_nuxt/SQCi_SES.js`：200
- `https://test-pc-s3.hbabaxb.cn/images/index-new/main-game.svg?敏感凭据：[已脱敏]
- `https://test-pc-s3.hbabaxb.cn/images/index-new/main-game.svg`：403

容器：

- `youdianse_pc_dev_18game_pc_client_3004`：运行中

## 后续维护

- 新增页面入口域名时，一般不需要改 `test-pc-s3.hbabaxb.cn` 的 CORS 白名单。
- 新增前端媒体目录时，需要同步补充发布脚本签名前缀和 EdgeOne 鉴权规则。
- 如果后续要保护 `_nuxt` 下图片，需要先确认 CSS/JS 中引用的 `_nuxt` 图片是否已全部可被签名脚本覆盖，再单独扩展规则。
- H5 和线上环境不要直接套用本次规则，先单独发版验证。
