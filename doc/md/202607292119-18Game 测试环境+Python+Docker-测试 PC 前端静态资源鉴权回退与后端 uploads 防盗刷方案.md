---
id: "doc-b33dde17b6e5"
title: "测试 PC 前端静态资源鉴权回退与后端 uploads 防盗刷方案"
date: "2026-07-29T21:19:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "自动化", "CDN", "DNS", "安全运维", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2119-%E3%80%90%E6%9E%B6%E6%9E%84%E8%B0%83%E6%95%B4%2B%E5%9B%9E%E9%80%80%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%89%8D%E7%AB%AF%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E9%89%B4%E6%9D%83%E5%9B%9E%E9%80%80%E4%B8%8E%E5%90%8E%E7%AB%AFuploads%E9%98%B2%E7%9B%97%E5%88%B7%E6%96%B9%E6%A1%88.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md"
sourceSha256: "5d57dc0ea74a13592e72124acf17afc6e31791352ce428e967dd814a8102c13b"
sourceSystem: "project-doc"
---

# 测试 PC 前端静态资源鉴权回退与后端 uploads 防盗刷方案

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md`

> 整理日期：2026-07-29 21:19｜日期依据：文件名日期

环境标签：测试环境

## 1. 背景

2026-07-29 测试 PC 前端曾尝试对腾讯新加坡 COS 上的前端媒体资源增加 URL token 鉴权，用于减少资源被盗刷。

上线验证后发现该方向不适合作为前端打包资源方案：

- 前端页面域名会持续新增和变化，JS/CSS/图片跨域和 CORS 维护成本高。
- 前端打包出来的图片、SVG、WebP 数量不多，风险收益不高。
- 鉴权参数叠加相对路径后，出现部分 SVG/WebP 524、跨域或资源加载不稳定。
- 真正容易被外部复用和盗刷的是后端 uploads 图片，例如后台接口返回的 CloudFront 图片地址。

本次结论：前端打包资源还原为不加密；后端 uploads 图片单独设计腾讯 CDN/EdgeOne 反代域名并在该链路做防盗刷/鉴权。

状态更新：2026-07-29 21:55 已完成测试后端 uploads 图片反代落地，`test-img.hbabaxb.cn` 已接入 EdgeOne，后端 `cdn_image` 展示域名已切到新域名。详细执行记录见 `2026-07-29_2155-【网络调整+安全优化】测试后端uploads图片EdgeOne反代与防盗刷落地记录.md`。

## 2. 回退范围

本次只处理测试 PC 前端发布入口：

```text
测试环境-游点涩-pc-发版
```

涉及域名：

```text
https://pc.youdianse-test.xyz
https://test-pc.hbabaxb.cn
https://test-pc-s3.hbabaxb.cn
```

不改动：

- H5 当前测试环境业务。
- 线上前端 AWS S3 公开资源访问方式。
- 后端 uploads 图片上传逻辑。
- 后端 APK/App 包 AWS S3 链路。

## 3. 本次实际操作

### 3.1 关闭 PC 前端发布默认鉴权

本地与 ben-bot 服务器均已同步：

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/benbot_plugin.py
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py
devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_config.py
```

关键变化：

```text
YOUDIANSE_PC_TEST_TENCENT_STATIC_AUTH_ENABLE=0
TENCENT_STATIC_AUTH_ENABLE 默认值=0
发布结构版本=tooling-v20-frontend-static-no-auth
```

效果：

- PC 按钮发布和 webhook 自动发布都会走同一套无鉴权配置。
- 构建阶段不再给前端图片、SVG、WebP、视频、JS、CSS 写入 `token` 和 `t` 参数。
- 前端静态资源继续双推 AWS S3 和腾讯新加坡 COS。

### 3.2 删除 EdgeOne 前端媒体鉴权规则

已删除 `test-pc-s3.hbabaxb.cn` 下历史测试用的媒体鉴权规则：

```text
test-pc-s3-media-auth-images
test-pc-s3-media-auth-image
test-pc-s3-media-auth-video
test-pc-s3-media-auth-videos
test-pc-s3-media-auth-media
test-pc-s3-media-auth-root-icons
```

删除后，前端静态域名不再要求 token。

### 3.3 刷新腾讯 EdgeOne 缓存

刷新范围：

```text
https://test-pc-s3.hbabaxb.cn/_nuxt/
https://test-pc-s3.hbabaxb.cn/images/
```

刷新任务：

```text
JobId=3t4t4b2g7cha
JobId=3t4tmo22xcgb
```

### 3.4 重新发布 PC 最新版本

重新触发：

```text
测试环境-游点涩-pc-发版
```

发布版本：

```text
git 短 id: 3dfe674
```

构建日志确认：

```text
TENCENT_STATIC_AUTH_ENABLE=0
本次 Docker build 不启用腾讯静态资源鉴权签名改写
COS 静态资源同步: 成功
腾讯 CDN 缓存刷新: 成功
```

## 4. 当前验证结果

版本验证：

| URL | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/version.json` | `3dfe674` |
| `https://test-pc.hbabaxb.cn/version.json` | `3dfe674` |
| `https://test-pc-s3.hbabaxb.cn/version.json` | `3dfe674` |

页面 HTML 验证：

| 页面 | 结果 |
| --- | --- |
| `https://pc.youdianse-test.xyz/` | `[敏感内容已脱敏] |
| `https://test-pc.hbabaxb.cn/` | `[敏感内容已脱敏] |

静态资源抽样：

| URL | 结果 |
| --- | --- |
| `https://test-pc-s3.hbabaxb.cn/images/signup/play.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/bullet.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/menu.svg` | `200 image/svg+xml` |
| `https://test-pc-s3.hbabaxb.cn/images/index-new/main-bg.webp` | `200 image/webp` |
| `https://test-pc.hbabaxb.cn/images/signup/play.svg` | `200 image/svg+xml` |

## 5. 当前链路

PC 前端页面：

```text
AWS/原测试入口: https://pc.youdianse-test.xyz
备案入口: https://test-pc.hbabaxb.cn
```

PC 前端静态资源：

```text
展示域名: https://test-pc-s3.hbabaxb.cn
AWS 公开桶: s3://18game-nuxt-static-test-pc
腾讯 COS 私有桶: 18game-nuxt-static-test-pc-sg-1450169938
腾讯 COS 区域: ap-singapore
EdgeOne CNAME: test-pc-s3.hbabaxb.cn.eo.dnse4.com
```

当前发布规则：

```text
构建 .output/public
-> 同步 AWS 前端公开桶
-> 同步腾讯新加坡 COS 私有桶
-> 页面优先加载 test-pc-s3.hbabaxb.cn
-> 发布后刷新 _nuxt/ 和 images/
```

## 6. 后端 uploads 反代防盗刷方案

### 6.1 目标

将后端接口返回的 AWS CloudFront uploads 图片通过腾讯 CDN/EdgeOne 反代访问，再只对这条业务图片链路做防盗刷/鉴权。

示例原地址：

```text
https://d1rct3ku9n07y3.cloudfront.net/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png
```

建议测试环境新地址：

```text
https://test-img.hbabaxb.cn/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png
```

备选命名：

```text
test-img.hbabaxb.cn
test-uploads.hbabaxb.cn
```

正式环境可对应：

```text
main-img.hbabaxb.cn
main-uploads.hbabaxb.cn
```

### 6.2 EdgeOne/CDN 配置建议

测试环境：

```text
加速域名: test-img.hbabaxb.cn
源站类型: IP/域名
源站地址: d1rct3ku9n07y3.cloudfront.net
回源 Host: d1rct3ku9n07y3.cloudfront.net
缓存路径: /uploads/*
协议: HTTPS 回源
```

DNS：

```text
test-img.hbabaxb.cn CNAME test-img.hbabaxb.cn.eo.dnse4.com
_dnsauth.test-img.hbabaxb.cn CNAME 按 EdgeOne 证书验证值填写
```

### 6.3 不改开发代码时的边界

如果完全不改后端配置或代码，后端接口仍会返回原 CloudFront 地址：

```text
https://d1rct3ku9n07y3.cloudfront.net/uploads/...
```

浏览器不会自动改用 `test-img.hbabaxb.cn`。因此至少需要二选一：

1. 后端展示域名配置从 CloudFront 域名切到 `test-img.hbabaxb.cn`，上传仍继续写 AWS S3。
2. 在网关或 EdgeOne 函数层改写接口响应里的图片域名。

建议优先采用第 1 种：改后端环境配置或后台展示域名，不改上传逻辑，风险最小、可回滚。

### 6.4 防盗刷等级

低改造、弱保护：

```text
Referer 白名单:
- https://pc.youdianse-test.xyz
- https://test-pc.hbabaxb.cn
- https://h5.youdianse-test.xyz
- https://test-h5.hbabaxb.cn
```

优点：不需要前端打包资源改造。
缺点：Referer 可伪造，只能挡普通盗链。

中等保护：

```text
EdgeOne Token 鉴权只开启 /uploads/*
```

要求：后端返回图片 URL 时生成 token 和过期时间，或由网关统一改写响应。
优点：不影响前端 JS/CSS，不需要给大量页面域名配置 CORS。
缺点：需要后端配置/代码或边缘函数配合签名。

推荐顺序：

1. 先建 `test-img.hbabaxb.cn` 反代 CloudFront uploads，并只加 Referer 白名单。
2. 后端展示域名切到 `test-img.hbabaxb.cn`，验证接口图片展示。
3. 如盗刷风险仍高，再做 `/uploads/*` token 鉴权。

## 7. 回滚方式

如 PC 前端回退后出现问题：

```text
重新发布上一版可用 PC 前端 git 短 id
恢复 test-pc-s3 EdgeOne 规则前先确认是否仍需要前端鉴权
腾讯缓存刷新 _nuxt/ 和 images/
```

如后续 `test-img.hbabaxb.cn` 反代方案异常：

```text
后端展示域名切回 d1rct3ku9n07y3.cloudfront.net
暂停 EdgeOne 鉴权规则
保留 AWS S3 上传逻辑不变
```

## 8. 飞机群通知

已通知群：

```text
稳定备案域名+腾讯云原厂
```

通知内容：

- 前端静态资源鉴权回退开始。
- ben-bot 已同步并重启。
- EdgeOne 旧媒体鉴权规则删除。
- 腾讯缓存刷新。
- PC 重新发布 `3dfe674`。
- 公网验证无 token、静态资源 200。

## 9. 关联文档

```text
devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md
devops/python/ben-bot/doc/2026-07-29_1828-【架构改造+安全优化】测试PC前端腾讯静态资源鉴权改造记录.md
devops/python/ben-bot/doc/2026-07-29_1932-【安全优化+架构改造】测试PC前端媒体资源Token鉴权落地验证记录.md
devops/python/ben-bot/doc/2026-07-29_2045-【修复Bug+网络调整】测试PC图片相对路径反代与腾讯鉴权修复记录.md
```

说明：`1828`、`1932`、`2045` 为历史尝试记录，当前有效方案以本文和 `1806` 索引第 8 节为准。
