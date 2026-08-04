---
id: "doc-805119153a44"
title: "四个备案域名与 H5/PC/S3/IMG 链路整理"
date: "2026-08-04T21:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "CDN", "DNS"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2130-%E3%80%90%E8%BF%90%E7%BB%B4%E8%A7%84%E5%88%92%2B%E5%9F%9F%E5%90%8D%E5%85%B3%E7%B3%BB%E3%80%91%E5%9B%9B%E4%B8%AA%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E4%B8%8EH5-PC-S3-IMG%E9%93%BE%E8%B7%AF%E6%95%B4%E7%90%86.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2130-【运维规划+域名关系】四个备案域名与H5-PC-S3-IMG链路整理.md"
sourceSha256: "929001d1dcae7ad0f415da83814e3b56afddda7fd04ee5d2eaaeb26a06c18ff7"
sourceSystem: "project-doc"
---

# 四个备案域名与 H5/PC/S3/IMG 链路整理

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2130-【运维规划+域名关系】四个备案域名与H5-PC-S3-IMG链路整理.md`

> 整理日期：2026-08-04 21:30｜日期依据：文件名日期

环境标签：测试环境 / 线上前置 / 线上环境 / 备案域名 / 腾讯 COS / 静态资源 / 图片资源

记录时间：2026-08-04 21:30

## 本次结论

本次整理 4 个备案域名的职责边界，核心原则如下：

- 页面入口、前端构建静态资源、后端 uploads 图片分开。
- 前端 H5/PC 打包产物使用各自独立腾讯 COS/S3 桶。
- `test-h5-s3`、`test-pc-s3`、`main-h5-s3`、`main-pc-s3` 这类前端静态资源域名不走腾讯 CDN/EdgeOne，避免缓存和 CORS 反复问题。
- 当前新静态资源域名通过日本服务器 `138.252.248.139` 的 Nginx HTTPS 反代到腾讯 COS，并统一补 CORS 与 no-cache/no-store 响应头。
- 后端 uploads 图片继续走 `test-img/main-img` 这类独立图片链路，不和前端构建资源混用。

## 四个备案域名费用与定位

| 域名 | 费用周期 | 月费用 | 当前定位 |
| --- | --- | --- | --- |
| `hbabaxb.cn` | 08.11 ~ 09.11 | 200u | 测试环境主备案域：H5/PC 页面入口、测试图片主链路 |
| `hbazuua.cn` | 08.11 ~ 09.11 | 200u | 测试环境备用备案域：H5/PC 页面备用、测试图片备用链路 |
| `hbbfuub.cn` | 08.04 ~ 09.04 | 200u | 测试环境前端静态资源新域名：H5/PC 打包资源无 CDN 链路 |
| `hbakjja.cn` | 08.04 ~ 09.04 | 200u | 线上前置/上线前模拟静态资源新域名：H5/PC 打包资源无 CDN 链路 |

## 树形链路版

```text
用户浏览器
├─ 测试环境 H5 页面
│  ├─ https://h5.youdianse-test.xyz
│  ├─ https://test-h5.hbabaxb.cn
│  └─ https://test-h5.hbazuua.cn（备用，证书需单独确认）
├─ 测试环境 PC 页面
│  ├─ https://pc.youdianse-test.xyz
│  ├─ https://test-pc.hbabaxb.cn
│  └─ https://test-pc.hbazuua.cn（备用，证书需单独确认）
├─ 测试环境前端静态资源（不走腾讯 CDN/EdgeOne）
│  ├─ H5: https://test-h5-s3.hbbfuub.cn
│  │  └─ 日本 Nginx 138.252.248.139 -> 腾讯 COS: 18game-nuxt-static-test-h5-sg-1450169938
│  └─ PC: https://test-pc-s3.hbbfuub.cn
│     └─ 日本 Nginx 138.252.248.139 -> 腾讯 COS: 18game-nuxt-static-test-pc-sg-1450169938
├─ 线上前置/上线前模拟前端静态资源（不走腾讯 CDN/EdgeOne）
│  ├─ H5: https://main-h5-s3.hbakjja.cn
│  │  └─ 日本 Nginx 138.252.248.139 -> 腾讯 COS: 18game-nuxt-static-preprod-h5-sg-1450169938
│  └─ PC: https://main-pc-s3.hbakjja.cn
│     └─ 日本 Nginx 138.252.248.139 -> 腾讯 COS: 18game-nuxt-static-preprod-pc-sg-1450169938
├─ 后端 uploads 图片
│  ├─ 测试主用: https://test-img.hbabaxb.cn/uploads/...
│  ├─ 测试候选: https://test-img.hbazuua.cn/uploads/...
│  ├─ AWS 源/兜底: https://d1rct3ku9n07y3.cloudfront.net/uploads/...
│  └─ 线上规划: https://main-img.备案域名/uploads/...
└─ 后端接口
   ├─ 页面同域 /api、/channel、/customer 反代到对应后端
   └─ 测试前端 env 仍记录 https://admin.youdianse-test.xyz 作为测试 API 域名
```

旧静态域说明：

- `https://test-h5-s3.hbabaxb.cn`：旧测试 H5 静态域，已停止作为页面构建静态域。
- `https://test-pc-s3.hbabaxb.cn`：旧测试 PC 静态域，已停止作为页面构建静态域。
- 停用原因：旧域名仍走 EdgeOne，曾出现部分边缘节点 `200` 但缺 CORS 响应头，导致浏览器拦截 CSS/JS。

## 当前推荐落地域名

### 测试环境

| 用途 | 推荐域名 | 当前状态 | 链路说明 |
| --- | --- | --- | --- |
| H5 页面入口 | `test-h5.hbabaxb.cn` | 已在用 | 页面入口，走现有 EdgeOne/页面链路 |
| H5 页面备用 | `test-h5.hbazuua.cn` | 备用，证书需单独确认 | 页面备用入口，不承载前端构建静态资源 |
| H5 前端静态资源 | `test-h5-s3.hbbfuub.cn` | 已启用 | A 到 `138.252.248.139` -> 日本 Nginx -> 腾讯 COS 桶 |
| PC 页面入口 | `test-pc.hbabaxb.cn` | 已在用 | 页面入口，走现有 EdgeOne/页面链路 |
| PC 页面备用 | `test-pc.hbazuua.cn` | 备用，证书需单独确认 | 页面备用入口，不承载前端构建静态资源 |
| PC 前端静态资源 | `test-pc-s3.hbbfuub.cn` | 已启用 | A 到 `138.252.248.139` -> 日本 Nginx -> 腾讯 COS 桶 |
| 后端 uploads 图片主域 | `test-img.hbabaxb.cn` | 已在用 | 后端上传图片展示链路，和前端静态资源分离 |
| 后端 uploads 图片备用 | `test-img.hbazuua.cn` | 已在用 | 后端上传图片备用展示链路 |

### 线上前置 / 上线前模拟

| 用途 | 推荐域名 | 当前状态 | 链路说明 |
| --- | --- | --- | --- |
| H5 页面入口 | `main-h5.备案域名` | 待页面域名正式指定 | 线上前置 H5 页面入口，后续回源日本前置服务器 |
| PC 页面入口 | `main-pc.备案域名` | 待页面域名正式指定 | 建议使用 `main-pc`，不要复用测试环境 `test-pc` 名称 |
| H5 前端静态资源 | `main-h5-s3.hbakjja.cn` | 已启用静态资源链路 | A 到 `138.252.248.139` -> 日本 Nginx -> 线上前置 H5 腾讯 COS 桶 |
| PC 前端静态资源 | `main-pc-s3.hbakjja.cn` | 已启用静态资源链路 | A 到 `138.252.248.139` -> 日本 Nginx -> 线上前置 PC 腾讯 COS 桶 |
| 后端 uploads 图片 | `main-img.备案域名` | 待线上图片链路正式指定 | 线上后端上传图片展示链路，不和前端构建静态资源混用 |

说明：用户原口径里线上 PC 页面写过 `test-pc.备案域名`，但该名字已经用于测试环境 PC。为避免混淆，线上前置/线上环境建议统一使用 `main-pc.备案域名`。

## 四个 S3 静态资源域名

| 域名 | 环境 | 用途 | 当前 DNS | 当前响应策略 |
| --- | --- | --- | --- | --- |
| `test-h5-s3.hbbfuub.cn` | 测试 | H5 前端打包资源 | A -> `138.252.248.139` | `CORS:*`、`no-store` |
| `test-pc-s3.hbbfuub.cn` | 测试 | PC 前端打包资源 | A -> `138.252.248.139` | `CORS:*`、`no-store` |
| `main-h5-s3.hbakjja.cn` | 线上前置/上线前模拟 | H5 前端打包资源 | A -> `138.252.248.139` | `CORS:*`、`no-store` |
| `main-pc-s3.hbakjja.cn` | 线上前置/上线前模拟 | PC 前端打包资源 | A -> `138.252.248.139` | `CORS:*`、`no-store` |

这 4 个域名全部不走腾讯 CDN/EdgeOne。原因是前端打包资源文件名、Service Worker、CSS/JS 加载和跨域响应头对缓存一致性要求高，旧 EdgeOne 静态域已经出现过 `200` 但缺 `Access-Control-Allow-Origin` 的边缘节点抖动。

## 腾讯 COS 桶关系

| 域名 | 腾讯 COS 桶 | 说明 |
| --- | --- | --- |
| `test-h5-s3.hbbfuub.cn` | `18game-nuxt-static-test-h5-sg-1450169938` | 测试 H5 前端构建资源 |
| `test-pc-s3.hbbfuub.cn` | `18game-nuxt-static-test-pc-sg-1450169938` | 测试 PC 前端构建资源 |
| `main-h5-s3.hbakjja.cn` | `18game-nuxt-static-preprod-h5-sg-1450169938` | 线上前置 H5 前端构建资源 |
| `main-pc-s3.hbakjja.cn` | `18game-nuxt-static-preprod-pc-sg-1450169938` | 线上前置 PC 前端构建资源 |

## 当前 DNS 抽查

| 域名 | DNS 结果 |
| --- | --- |
| `test-h5-s3.hbbfuub.cn` | `138.252.248.139` |
| `test-pc-s3.hbbfuub.cn` | `138.252.248.139` |
| `main-h5-s3.hbakjja.cn` | `138.252.248.139` |
| `main-pc-s3.hbakjja.cn` | `138.252.248.139` |
| `test-h5.hbabaxb.cn` | EdgeOne CNAME |
| `test-pc.hbabaxb.cn` | EdgeOne CNAME |
| `test-img.hbabaxb.cn` | EdgeOne CNAME |
| `test-img.hbazuua.cn` | EdgeOne CNAME |

## 给群里的简版关系

4 个备案域名当前这样分：

- `hbabaxb.cn`：测试环境主备案域，承接 `test-h5`、`test-pc`、`test-img`。
- `hbazuua.cn`：测试环境备用备案域，承接备用页面和备用 `test-img`，页面证书需单独确认。
- `hbbfuub.cn`：测试环境前端静态资源专用，承接 `test-h5-s3`、`test-pc-s3`，不走腾讯 CDN。
- `hbakjja.cn`：线上前置/上线前模拟静态资源专用，承接 `main-h5-s3`、`main-pc-s3`，不走腾讯 CDN。

核心链路：

```text
测试 H5 页面 -> test-h5.hbabaxb.cn
测试 H5 静态资源 -> test-h5-s3.hbbfuub.cn -> 日本 Nginx -> 腾讯 COS

测试 PC 页面 -> test-pc.hbabaxb.cn
测试 PC 静态资源 -> test-pc-s3.hbbfuub.cn -> 日本 Nginx -> 腾讯 COS

线上前置 H5 静态资源 -> main-h5-s3.hbakjja.cn -> 日本 Nginx -> 腾讯 COS
线上前置 PC 静态资源 -> main-pc-s3.hbakjja.cn -> 日本 Nginx -> 腾讯 COS

测试图片 -> test-img.hbabaxb.cn / test-img.hbazuua.cn
线上图片 -> main-img.备案域名，后续单独落正式链路
```

## 后续注意

1. 前端构建资源不要再回到旧 `test-h5-s3.hbabaxb.cn`、`test-pc-s3.hbabaxb.cn`，旧域名保留为历史/回滚观察对象。
2. `hbazuua.cn` 当前更适合作为备用页面/图片域，若要启用页面入口，需要单独确认证书覆盖。
3. 线上前置页面域名建议明确成 `main-h5.备案域名`、`main-pc.备案域名`，避免把线上 PC 写成 `test-pc`。
4. `main-img.备案域名` 是后端 uploads 图片链路，和前端 `main-*-s3` COS 打包资源链路分开维护。

## 群发优化版

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
- test-h5.hbazuua.cn（备用，证书需确认）

PC 页面：
- pc.youdianse-test.xyz
- test-pc.hbabaxb.cn
- test-pc.hbazuua.cn（备用，证书需确认）

三、测试环境前端静态资源
不走腾讯 CDN / EdgeOne

H5 静态资源：
- test-h5-s3.hbbfuub.cn
- 腾讯 COS: 18game-nuxt-static-test-h5-sg-1450169938

PC 静态资源：
- test-pc-s3.hbbfuub.cn
- 腾讯 COS: 18game-nuxt-static-test-pc-sg-1450169938

四、线上前置静态资源
不走腾讯 CDN / EdgeOne

H5 静态资源：
- main-h5-s3.hbakjja.cn
- 腾讯 COS: 18game-nuxt-static-preprod-h5-sg-1450169938

PC 静态资源：
- main-pc-s3.hbakjja.cn
- 腾讯 COS: 18game-nuxt-static-preprod-pc-sg-1450169938

五、后端 uploads 图片
测试主用：
- test-img.hbabaxb.cn/uploads/...

测试备用：
- test-img.hbazuua.cn/uploads/...

AWS 源 / 兜底：
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
