---
id: "doc-d6b3d77d2599"
title: "四个备案域名关系整理清晰版"
date: "2026-08-04T22:02:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2202-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E5%9F%9F%E5%90%8D%E5%85%B3%E7%B3%BB%E3%80%91%E5%9B%9B%E4%B8%AA%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E5%85%B3%E7%B3%BB%E6%95%B4%E7%90%86%E6%B8%85%E6%99%B0%E7%89%88.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2202-【运维记录+域名关系】四个备案域名关系整理清晰版.md"
sourceSha256: "0ab95cf3397234306bced07464be3ced5556459dbb6a1bdcb365e4901f238267"
sourceSystem: "project-doc"
---

# 四个备案域名关系整理清晰版

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2202-【运维记录+域名关系】四个备案域名关系整理清晰版.md`

> 整理日期：2026-08-04 22:02｜日期依据：文件名日期

环境标签：测试环境、线上前置、腾讯云备案域名、腾讯 COS、日本 Nginx

时间：2026-08-04 22:02

## 一、域名费用与定位

| 域名 | 周期 | 费用 | 主定位 |
| --- | --- | --- | --- |
| `hbabaxb.cn` | 08.11 - 09.11 | 200u | 测试页面主域 + 测试图片主域 |
| `hbazuua.cn` | 08.11 - 09.11 | 200u | 测试页面备用 + 测试图片备用 |
| `hbbfuub.cn` | 08.04 - 09.04 | 200u | 测试 H5/PC 前端静态资源 |
| `hbakjja.cn` | 08.04 - 09.04 | 200u | 线上前置 H5/PC 前端静态资源 |

## 二、测试环境页面

H5 页面：

- `https://h5.youdianse-test.xyz`
- `https://test-h5.hbabaxb.cn`
- `https://test-h5.hbazuua.cn`，备用，旧 EdgeOne 链路仍需观察
- `https://test-h5.hbbfuub.cn`
- `https://test-h5.hbakjja.cn`

PC 页面：

- `https://pc.youdianse-test.xyz`
- `https://test-pc.hbabaxb.cn`
- `https://test-pc.hbazuua.cn`，备用
- `https://test-pc.hbbfuub.cn`
- `https://test-pc.hbakjja.cn`

页面入口链路：

```text
用户浏览器
  -> test-h5 / test-pc 备案页面域名
  -> 测试前端服务器 38.92.8.34
  -> H5 容器 3003 / PC 容器 3004
```

本轮补全验证：

- `test-h5.hbbfuub.cn`、`test-pc.hbbfuub.cn` 已严格 HTTPS 验证 200。
- `test-h5.hbakjja.cn`、`test-pc.hbakjja.cn` 已严格 HTTPS 验证 200。
- 新证书 `youdianse-test-pages-icp` 覆盖以上新增页面域名，到期 `2026-11-02`。

## 三、测试环境前端静态资源

要求：不走腾讯 CDN / EdgeOne。

H5 静态资源：

- 默认域名：`https://test-h5-s3.hbbfuub.cn`
- COS 桶：`18game-nuxt-static-test-h5-sg-1450169938`

PC 静态资源：

- 默认域名：`https://test-pc-s3.hbbfuub.cn`
- COS 桶：`18game-nuxt-static-test-pc-sg-1450169938`

补充说明：

- `test-h5-s3.hbabaxb.cn`、`test-pc-s3.hbabaxb.cn`
- `test-h5-s3.hbazuua.cn`、`test-pc-s3.hbazuua.cn`

以上 4 个域名也已补全为同链路备用能力，均可走日本 Nginx 反代腾讯 COS。

## 四、线上前置静态资源

要求：不走腾讯 CDN / EdgeOne。

H5 静态资源：

- 默认域名：`https://main-h5-s3.hbakjja.cn`
- COS 桶：`18game-nuxt-static-preprod-h5-sg-1450169938`

PC 静态资源：

- 默认域名：`https://main-pc-s3.hbakjja.cn`
- COS 桶：`18game-nuxt-static-preprod-pc-sg-1450169938`

补充说明：

- `main-h5-s3.hbabaxb.cn`、`main-pc-s3.hbabaxb.cn`
- `main-h5-s3.hbazuua.cn`、`main-pc-s3.hbazuua.cn`

以上 4 个域名也已补全为同链路备用能力，均可走日本 Nginx 反代腾讯 COS。

## 五、后端 uploads 图片

- 测试主用：`https://test-img.hbabaxb.cn/uploads/...`
- 测试备用：`https://test-img.hbazuua.cn/uploads/...`
- AWS 源/兜底：`https://d1rct3ku9n07y3.cloudfront.net/uploads/...`
- 线上规划：`https://main-img.备案域名/uploads/...`

## 六、链路重点

前端静态资源：

```text
用户浏览器
  -> S3 域名
  -> 日本 Nginx 138.252.248.139
  -> 腾讯 COS
```

后端图片资源：

```text
用户浏览器
  -> test-img / main-img
  -> 后端 uploads 链路
```

后端接口：

```text
页面同域 /api、/channel、/customer
  -> 反代到对应后端
```

## 七、清晰版结论

- `hbabaxb.cn`、`hbazuua.cn` 负责测试页面和测试图片。
- `hbbfuub.cn` 负责测试 H5/PC 前端静态资源默认域。
- `hbakjja.cn` 负责线上前置 H5/PC 前端静态资源默认域。
- 前端静态资源不走腾讯 CDN / EdgeOne，避免缓存和 CORS 反复问题。
- `hbabaxb.cn`、`hbazuua.cn` 的 S3 静态资源子域已补全，可作为同链路备用能力。

## 八、群发清晰版

```text
【四个备案域名关系整理】

一、域名费用与定位
hbabaxb.cn   08.11-09.11  200u
用途：测试页面主域 + 测试图片主域

hbazuua.cn   08.11-09.11  200u
用途：测试页面备用 + 测试图片备用

hbbfuub.cn   08.04-09.04  200u
用途：测试 H5/PC 前端静态资源

hbakjja.cn   08.04-09.04  200u
用途：线上前置 H5/PC 前端静态资源

二、测试环境页面
H5 页面：
- h5.youdianse-test.xyz
- test-h5.hbabaxb.cn
- test-h5.hbazuua.cn（备用，旧 EdgeOne 链路仍需观察）
- test-h5.hbbfuub.cn
- test-h5.hbakjja.cn

PC 页面：
- pc.youdianse-test.xyz
- test-pc.hbabaxb.cn
- test-pc.hbazuua.cn（备用）
- test-pc.hbbfuub.cn
- test-pc.hbakjja.cn

三、测试环境前端静态资源
不走腾讯 CDN / EdgeOne

H5 静态资源：
- test-h5-s3.hbbfuub.cn
- COS: 18game-nuxt-static-test-h5-sg-1450169938

PC 静态资源：
- test-pc-s3.hbbfuub.cn
- COS: 18game-nuxt-static-test-pc-sg-1450169938

四、线上前置静态资源
不走腾讯 CDN / EdgeOne

H5 静态资源：
- main-h5-s3.hbakjja.cn
- COS: 18game-nuxt-static-preprod-h5-sg-1450169938

PC 静态资源：
- main-pc-s3.hbakjja.cn
- COS: 18game-nuxt-static-preprod-pc-sg-1450169938

五、后端 uploads 图片
测试主用：
- test-img.hbabaxb.cn/uploads/...

测试备用：
- test-img.hbazuua.cn/uploads/...

AWS 源/兜底：
- d1rct3ku9n07y3.cloudfront.net/uploads/...

线上规划：
- main-img.备案域名/uploads/...

六、链路重点
前端静态资源：
用户浏览器 -> S3 域名 -> 日本 Nginx -> 腾讯 COS

后端图片资源：
用户浏览器 -> test-img/main-img -> 后端 uploads 链路

后端接口：
页面同域 /api、/channel、/customer 反代到对应后端

结论：
hbabaxb.cn、hbazuua.cn 负责测试页面和图片。
hbbfuub.cn 负责测试前端静态资源。
hbakjja.cn 负责线上前置静态资源。
前端静态资源不走腾讯 CDN，避免缓存和 CORS 反复问题。
```
