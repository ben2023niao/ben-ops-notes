---
id: "doc-cadc4bc2c9bd"
title: "测试前端 H5/PC 备案域名与 S3 链路索引"
date: "2026-07-29T18:06:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "自动化", "CDN", "DNS", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1806-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E5%89%8D%E7%AB%AFH5-PC%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E4%B8%8ES3%E9%93%BE%E8%B7%AF%E7%B4%A2%E5%BC%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md"
sourceSha256: "9834484711ea928bb0b8bd6d03a2fe3a4a50106ca34f041eb5fcad52577f5db9"
sourceSystem: "project-doc"
---

# 测试前端 H5/PC 备案域名与 S3 链路索引

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md`

> 整理日期：2026-07-29 18:06｜日期依据：文件名日期

环境标签：测试环境

## 1. 范围

本文只整理以下两个机器人发布入口：

- `测试环境-游点涩-h5-发版`
- `测试环境-游点涩-pc-发版`

这两个入口只负责前端构建产物 `.output/public` 的双推和页面静态资源访问。测试后端 uploads 图片、APK/App 包仍属于后端 AWS 老 S3 链路，不在本文两个前端发布按钮里改动。

## 2. 当前链路总览

| 项目 | H5 | PC |
| --- | --- | --- |
| 机器人发布入口 | `测试环境-游点涩-h5-发版` | `测试环境-游点涩-pc-发版` |
| 前端仓库分支 | `web/youdianse-h5` / `test` | `web/youdianse-pc` / `dev` |
| AWS 页面访问域名 | `https://h5.youdianse-test.xyz` | `https://pc.youdianse-test.xyz` |
| 备案页面访问域名 | `https://test-h5.hbabaxb.cn` | `https://test-pc.hbabaxb.cn` |
| 前端静态资源展示域名 | `https://test-h5-s3.hbabaxb.cn` | `https://test-pc-s3.hbabaxb.cn` |
| AWS 前端静态桶 | `18game-nuxt-static-test-h5` | `18game-nuxt-static-test-pc` |
| AWS 区域 | `ap-southeast-1` | `ap-southeast-1` |
| AWS 公开桶域名 | `https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com` | `https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com` |
| 腾讯 COS 前端桶 | `18game-nuxt-static-test-h5-sg-1450169938` | `18game-nuxt-static-test-pc-sg-1450169938` |
| 腾讯 COS 区域 | `ap-singapore` | `ap-singapore` |
| 腾讯 COS 原始域名 | `18game-nuxt-static-test-h5-sg-1450169938.cos.ap-singapore.myqcloud.com` | `18game-nuxt-static-test-pc-sg-1450169938.cos.ap-singapore.myqcloud.com` |
| 腾讯 COS 公网直连 | 私有，不对公网直连 | 私有，不对公网直连 |
| EdgeOne CNAME | `test-h5-s3.hbabaxb.cn.eo.dnse4.com` | `test-pc-s3.hbabaxb.cn.eo.dnse4.com` |
| EdgeOne Zone | `zone-3t1w9ksp60nn` | `zone-3t1w9ksp60nn` |
| 发布后刷新 | `https://test-h5-s3.hbabaxb.cn/_nuxt/`、`https://test-h5-s3.hbabaxb.cn/images/` | `https://test-pc-s3.hbabaxb.cn/_nuxt/`、`https://test-pc-s3.hbabaxb.cn/images/` |

## 3. H5 发版配置

当前按钮发布注入的关键配置：

```text
BEN_BOT_PRIMARY_URL=https://h5.youdianse-test.xyz
BEN_BOT_ICP_ACCESS_URL=https://test-h5.hbabaxb.cn
BEN_BOT_TENCENT_CDN_URL=https://test-h5-s3.hbabaxb.cn
YOUDIANSE_H5_TEST_STATIC_CDN_URL=https://test-h5-s3.hbabaxb.cn
YOUDIANSE_H5_TEST_STATIC_COS_BUCKET=18game-nuxt-static-test-h5-sg-1450169938
YOUDIANSE_H5_TEST_STATIC_COS_REGION=ap-singapore
YOUDIANSE_H5_TEST_STATIC_SYNC_DELETE=0
YOUDIANSE_H5_TEST_TENCENT_CDN_PURGE_ENABLED=1
YOUDIANSE_H5_TEST_TENCENT_CDN_ZONE_ID=zone-3t1w9ksp60nn
```

远程构建时，`.output/public` 会同步到：

```text
s3://18game-nuxt-static-test-h5
s3://18game-nuxt-static-test-h5-sg-1450169938 --endpoint-url https://cos.ap-singapore.myqcloud.com
```

## 4. PC 发版配置

当前按钮发布注入的关键配置：

```text
BEN_BOT_PRIMARY_URL=https://pc.youdianse-test.xyz
BEN_BOT_ICP_ACCESS_URL=https://test-pc.hbabaxb.cn
BEN_BOT_TENCENT_CDN_URL=https://test-pc-s3.hbabaxb.cn
YOUDIANSE_PC_TEST_STATIC_CDN_URL=https://test-pc-s3.hbabaxb.cn
YOUDIANSE_PC_TEST_STATIC_S3_BUCKET=18game-nuxt-static-test-pc
YOUDIANSE_PC_TEST_STATIC_COS_BUCKET=18game-nuxt-static-test-pc-sg-1450169938
YOUDIANSE_PC_TEST_STATIC_COS_REGION=ap-singapore
YOUDIANSE_H5_TEST_STATIC_SYNC_DELETE=0
YOUDIANSE_PC_TEST_TENCENT_CDN_PURGE_ENABLED=1
YOUDIANSE_PC_TEST_TENCENT_CDN_ZONE_ID=zone-3t1w9ksp60nn
```

PC 复用 H5 发布引擎后，`.output/public` 会同步到：

```text
s3://18game-nuxt-static-test-pc
s3://18game-nuxt-static-test-pc-sg-1450169938 --endpoint-url https://cos.ap-singapore.myqcloud.com
```

## 5. DNS 与访问验证

DNS CNAME：

```text
test-h5.hbabaxb.cn -> test-h5.hbabaxb.cn.eo.dnse4.com.
test-pc.hbabaxb.cn -> test-pc.hbabaxb.cn.eo.dnse4.com.
test-h5-s3.hbabaxb.cn -> test-h5-s3.hbabaxb.cn.eo.dnse4.com.
test-pc-s3.hbabaxb.cn -> test-pc-s3.hbabaxb.cn.eo.dnse4.com.
```

2026-07-29 18:06 抽测：

| 地址 | 结果 |
| --- | --- |
| `https://test-h5-s3.hbabaxb.cn/version.txt` | 连续 3 次 `HTTP/2 200` |
| `https://test-pc-s3.hbabaxb.cn/version.txt` | `HTTP/2 200` |
| `https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com/version.txt` | `HTTP/1.1 200` |
| `https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com/version.txt` | `HTTP/1.1 200` |

## 6. 改造前注意点

- 前端构建产物优先展示腾讯新加坡静态资源域名：H5 用 `test-h5-s3.hbabaxb.cn`，PC 用 `test-pc-s3.hbabaxb.cn`。
- AWS 前端静态桶继续保留同步，作为公开桶和兜底验证。
- 腾讯 COS 前端桶保持私有，只允许通过 EdgeOne/CDN 域名访问。
- 页面入口备案域名和前端静态资源备案域名是两条链路：`test-h5/test-pc` 走页面入口，`test-h5-s3/test-pc-s3` 走静态资源。
- 后端 uploads、APK/App 包不要混进这两个前端发布入口；后端资源仍按后端 AWS 老 S3 链路处理。

## 7. 2026-07-29 20:45 PC 优化后链路（历史记录，21:19 已回退）

本节补充 PC 在图片鉴权改造后的历史关系。H5 仍按第 3 节链路运行；PC 在第 4 节基础上曾增加页面域名媒体反代，解决 `/images/...` 相对路径落到页面域名后返回 Nuxt HTML 的问题。

2026-07-29 21:19 更新：前端打包资源数量少、域名变化频繁，给前端静态资源加 token 后引入 524、跨域和相对路径兼容问题，已回退为“前端静态资源不加密”。后续防盗刷只针对后端 uploads 图片另建腾讯 CDN/EdgeOne 反代域名处理。

### 7.1 PC 改造后访问关系

| 类型 | 域名或资源 | 当前规则 |
| --- | --- | --- |
| PC 页面主入口 | `https://pc.youdianse-test.xyz` | 页面容器入口，继续可直接访问 |
| PC 备案页面入口 | `https://test-pc.hbabaxb.cn` | EdgeOne 到测试服务器，测试服务器 Nginx 进入 PC 容器 |
| PC 前端静态展示域名 | `https://test-pc-s3.hbabaxb.cn` | EdgeOne 到腾讯新加坡 COS 私有桶 |
| PC AWS 前端静态桶 | `s3://18game-nuxt-static-test-pc` | 构建后继续同步，公开桶，保留兜底 |
| PC 腾讯 COS 前端桶 | `18game-nuxt-static-test-pc-sg-1450169938` | `ap-singapore`，私有，不允许公网直连 |
| PC EdgeOne CNAME | `test-pc-s3.hbabaxb.cn.eo.dnse4.com` | Gname/DNS 解析到 EdgeOne |
| PC 后端 uploads/APK | 后端 AWS 老 S3 | 不属于 PC 前端发布按钮，本次不切换 |

### 7.2 PC 图片/媒体鉴权边界（已回退）

PC 曾只对图片、SVG、WebP、视频等媒体资源做腾讯 URL 鉴权；`_nuxt` 下的 JS/CSS 保持不加密访问。该方案已于 2026-07-29 21:19 回退，不再作为当前发布规则。

当前鉴权前缀：

```text
/images/
/image/
/video/
/videos/
/media/
/favicon.ico
/192.png
/512.png
```

当前排除路径：

```text
/version.txt
/version.json
```

历史效果：

- 带 `token` 和 `t` 参数的媒体 URL 可通过 `test-pc-s3.hbabaxb.cn` 访问。
- 不带 token 的媒体 URL 返回 403，避免 COS 私有桶资源被直接刷。
- JS/CSS 不加密，继续由浏览器正常跨域加载。

### 7.3 PC 页面域名媒体反代（保留为兼容，不再追加 token）

PC 备案页面和原测试页面均可能出现 `/images/...` 这种相对路径。改造后，测试服务器 Nginx 对下列路径做反代：

```text
pc.youdianse-test.xyz/images/*      -> test-pc-s3.hbabaxb.cn/images/*
test-pc.hbabaxb.cn/images/*        -> test-pc-s3.hbabaxb.cn/images/*
pc.youdianse-test.xyz/image/*       -> test-pc-s3.hbabaxb.cn/image/*
test-pc.hbabaxb.cn/image/*         -> test-pc-s3.hbabaxb.cn/image/*
pc.youdianse-test.xyz/video/*       -> test-pc-s3.hbabaxb.cn/video/*
test-pc.hbabaxb.cn/video/*         -> test-pc-s3.hbabaxb.cn/video/*
pc.youdianse-test.xyz/videos/*      -> test-pc-s3.hbabaxb.cn/videos/*
test-pc.hbabaxb.cn/videos/*        -> test-pc-s3.hbabaxb.cn/videos/*
pc.youdianse-test.xyz/media/*       -> test-pc-s3.hbabaxb.cn/media/*
test-pc.hbabaxb.cn/media/*         -> test-pc-s3.hbabaxb.cn/media/*
```

当前仍可保留页面域名 `/images/*` 到 `test-pc-s3.hbabaxb.cn` 的兼容反代，但不再要求 token。历史反代曾保留原始 query，例如：

```text
https://test-pc.hbabaxb.cn/images/bullet.svg?敏感凭据：[已脱敏]
-> https://test-pc-s3.hbabaxb.cn/images/bullet.svg?敏感凭据：[已脱敏]
```

### 7.4 PC 发布与缓存刷新规则（当前为无鉴权）

PC 发布入口仍为：

```text
测试环境-游点涩-pc-发版
```

发布时：

1. 构建 PC 前端代码仓库 `web/youdianse-pc` 的 `dev` 分支。
2. 将 `.output/public` 同步到 AWS 前端静态桶 `s3://18game-nuxt-static-test-pc`。
3. 将 `.output/public` 同步到腾讯新加坡 COS 桶 `18game-nuxt-static-test-pc-sg-1450169938`。
4. 不再对前端图片、SVG、WebP、视频、JS、CSS 写入腾讯 URL 鉴权参数。
5. 刷新腾讯 EdgeOne/CDN：

```text
https://test-pc-s3.hbabaxb.cn/_nuxt/
https://test-pc-s3.hbabaxb.cn/images/
```

2026-07-29 21:19 为了让回退后最新提交重新打包，发布结构版本已升级为：

```text
tooling-v20-frontend-static-no-auth
```

### 7.5 PC 改造验证记录（历史）

2026-07-29 20:45 验证：

| 验证项 | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/version.json` | `b209f18` |
| `https://test-pc.hbabaxb.cn/version.json` | `b209f18` |
| `https://test-pc-s3.hbabaxb.cn/version.json` | `b209f18` |
| HTML 双重静态域名前缀 | 未发现 `test-pc-s3.hbabaxb.cn/https://test-pc-s3.hbabaxb.cn` |
| `test-pc.hbabaxb.cn/images/placeholder.webp?...` | `206 image/webp` |
| `pc.youdianse-test.xyz/images/placeholder.webp?...` | `206 image/webp` |
| `test-pc.hbabaxb.cn/images/bullet.svg?...` | `200 image/svg+xml` |
| `test-pc.hbabaxb.cn/images/menu.svg?...` | 连续 3 次 `200 image/svg+xml` |
| `test-pc.hbabaxb.cn/images/index-new/main-bg.webp?...` | 连续 3 次 `200 image/webp` |
| 未签名 `test-pc-s3.hbabaxb.cn/images/bullet.svg` | 403，符合鉴权预期 |

相关详细修复文档：

```text
devops/python/ben-bot/doc/2026-07-29_2045-【修复Bug+网络调整】测试PC图片相对路径反代与腾讯鉴权修复记录.md
```

相关提交：

```text
e64b654 fix: proxy pc media assets through tencent cdn
```

## 8. 2026-07-29 21:19 当前状态：前端静态资源鉴权回退

当前规则：

- H5/PC 前端打包资源不做 URL token 鉴权。
- H5/PC 构建后仍双推 AWS 前端公开桶和腾讯新加坡 COS 私有桶。
- 页面静态资源仍优先使用腾讯 EdgeOne 域名：H5 `test-h5-s3.hbabaxb.cn`，PC `test-pc-s3.hbabaxb.cn`。
- 腾讯 COS 桶继续保持私有，不开放 COS 原始域名公网直连。
- EdgeOne 只作为前端静态资源 CDN，不再承担前端资源鉴权。
- 后端 uploads 图片、APK/App 包仍走后端 AWS 老 S3；防盗刷改为单独设计后端 uploads 图片反代 CDN 域名。

PC 回退验证：

| 验证项 | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/version.json` | `3dfe674` |
| `https://test-pc.hbabaxb.cn/version.json` | `3dfe674` |
| `https://test-pc-s3.hbabaxb.cn/version.json` | `3dfe674` |
| `https://pc.youdianse-test.xyz/` HTML | `[敏感内容已脱敏] |
| `https://test-pc.hbabaxb.cn/` HTML | `[敏感内容已脱敏] |
| `https://test-pc-s3.hbabaxb.cn/images/signup/play.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/bullet.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/menu.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/index-new/main-bg.webp` | `200 image/webp` |
| `https://test-pc.hbabaxb.cn/images/signup/play.svg` | `200 image/svg+xml` |

详细文档：

```text
devops/python/ben-bot/doc/2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md
```
