---
id: "doc-678ca42f3299"
title: "测试 H5/PC 前端静态资源与后端图片域名最终链路"
date: "2026-07-29T22:12:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2212-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E5%89%8D%E7%AB%AF%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E4%B8%8E%E5%90%8E%E7%AB%AF%E5%9B%BE%E7%89%87%E5%9F%9F%E5%90%8D%E6%9C%80%E7%BB%88%E9%93%BE%E8%B7%AF.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2212-【运维记录】测试H5-PC前端静态资源与后端图片域名最终链路.md"
sourceSha256: "e5fbfed5762d93e4748512763863196ad0aca4939fbd69b9c23b61928964bfe2"
sourceSystem: "project-doc"
---

# 测试 H5/PC 前端静态资源与后端图片域名最终链路

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2212-【运维记录】测试H5-PC前端静态资源与后端图片域名最终链路.md`

> 整理日期：2026-07-29 22:12｜日期依据：文件名日期

环境标签：测试环境

## 1. 当前结论

2026-07-29 当前测试环境 H5 和 PC 都已经使用备案域名访问后端 uploads 图片。

现在图片/资源域名分成两类：

```text
1. 前端打包静态资源域名
   用于 _nuxt、JS、CSS、前端自带图片、SVG、WebP 等。

2. 后端 uploads 图片展示域名
   用于后台上传后由接口返回的 /uploads 图片。
```

后端 uploads 图片现在同时存在两个可理解的域名：

```text
老 AWS CloudFront 域名:
https://d1rct3ku9n07y3.cloudfront.net

新腾讯 EdgeOne 备案域名:
https://test-img.hbabaxb.cn
```

当前后端接口展示优先返回新域名：

```text
https://test-img.hbabaxb.cn/uploads/...
```

## 2. H5 当前链路

页面入口：

```text
AWS/原测试入口:
https://h5.youdianse-test.xyz

备案入口:
https://test-h5.hbabaxb.cn
```

H5 前端打包静态资源：

```text
展示域名:
https://test-h5-s3.hbabaxb.cn

AWS 前端公开桶:
s3://18game-nuxt-static-test-h5
区域: ap-southeast-1

腾讯 COS 私有桶:
18game-nuxt-static-test-h5-sg-1450169938
区域: ap-singapore

EdgeOne CNAME:
test-h5-s3.hbabaxb.cn.eo.dnse4.com
```

H5 后端 uploads 图片：

```text
接口返回展示域名:
https://test-img.hbabaxb.cn/uploads/...

原始 AWS CloudFront 源:
https://d1rct3ku9n07y3.cloudfront.net/uploads/...
```

说明：

- H5 前端静态资源仍走 `test-h5-s3.hbabaxb.cn`。
- H5 页面里接口返回的后端上传图片会走 `test-img.hbabaxb.cn`。
- 本次没有修改 H5 前端发布脚本。

## 3. PC 当前链路

页面入口：

```text
AWS/原测试入口:
https://pc.youdianse-test.xyz

备案入口:
https://test-pc.hbabaxb.cn
```

PC 前端打包静态资源：

```text
展示域名:
https://test-pc-s3.hbabaxb.cn

AWS 前端公开桶:
s3://18game-nuxt-static-test-pc
区域: ap-southeast-1

腾讯 COS 私有桶:
18game-nuxt-static-test-pc-sg-1450169938
区域: ap-singapore

EdgeOne CNAME:
test-pc-s3.hbabaxb.cn.eo.dnse4.com
```

PC 后端 uploads 图片：

```text
接口返回展示域名:
https://test-img.hbabaxb.cn/uploads/...

原始 AWS CloudFront 源:
https://d1rct3ku9n07y3.cloudfront.net/uploads/...
```

说明：

- PC 前端静态资源仍走 `test-pc-s3.hbabaxb.cn`。
- PC 页面里接口返回的后端上传图片会走 `test-img.hbabaxb.cn`。
- PC 前端静态资源加密方案已经回退，当前不再给前端图片、SVG、WebP、JS、CSS 追加 token。

## 4. 后端 uploads 图片链路

当前后端配置：

```text
配置项: Mongo config.code = cdn_image
当前展示域名: https://test-img.hbabaxb.cn
```

实际访问链路：

```text
浏览器
-> https://test-img.hbabaxb.cn/uploads/...
-> 腾讯 EdgeOne
-> 测试源站 Nginx
-> AWS CloudFront d1rct3ku9n07y3.cloudfront.net
-> AWS S3 uploads 图片
```

样例图片：

```text
https://test-img.hbabaxb.cn/uploads/2026-01-28/86403be1f8740d6caacc472f28570703_large.webp
```

## 5. 目前两个图片域名怎么理解

### 5.1 老 AWS 域名

```text
https://d1rct3ku9n07y3.cloudfront.net
```

用途：

- 仍是 AWS uploads 图片源链路。
- 后台上传仍写 AWS S3。
- `test-img.hbabaxb.cn` 回源时仍会访问它。

当前状态：

- 不作为后端接口首选展示域名。
- 可以作为排查和回滚时的源站参考。

### 5.2 新腾讯备案 CDN 域名

```text
https://test-img.hbabaxb.cn
```

用途：

- H5/PC 页面展示后端 uploads 图片。
- 使用备案域名和腾讯 EdgeOne 入口。
- 后端接口当前返回该域名。

当前状态：

- H5 和 PC 已经看到该域名。
- 图片可正常 200。
- 因页面使用 `no-referrer`，当前 Nginx 允许空 Referer，外部带异常 Referer 的热链仍返回 403。

## 6. 发布规则

H5/PC 前端发布：

```text
构建 .output/public
-> 同步 AWS 前端静态桶
-> 同步腾讯新加坡 COS 私有桶
-> 页面前端静态资源优先走 test-h5-s3 / test-pc-s3
-> 发布后刷新对应 EdgeOne/CDN 的 _nuxt/ 和 images/
```

后端 uploads 图片：

```text
后台上传
-> 仍上传到 AWS S3
-> 仍可通过 AWS CloudFront 源域名访问
-> 后端展示配置返回 test-img.hbabaxb.cn
-> 浏览器通过腾讯 EdgeOne 访问图片
```

不要混淆：

- `test-h5-s3.hbabaxb.cn` / `test-pc-s3.hbabaxb.cn` 是前端构建产物域名。
- `test-img.hbabaxb.cn` 是后端 uploads 图片展示域名。
- 后端 APK/App 客户端包不在本次链路调整范围内。

## 7. 当前验证

H5：

```text
页面:
https://h5.youdianse-test.xyz/

后端 uploads 图片:
https://test-img.hbabaxb.cn/uploads/...

样例状态:
200 image/webp
```

PC：

```text
页面:
https://pc.youdianse-test.xyz/
https://test-pc.hbabaxb.cn/

后端 uploads 图片:
https://test-img.hbabaxb.cn/uploads/...

样例状态:
200 image/webp
```

抽样：

```text
https://test-img.hbabaxb.cn/uploads/2026-01-28/86403be1f8740d6caacc472f28570703_large.webp
返回: 200 image/webp
```

外部 Referer 防护：

```text
Referer: https://example.com/
返回: 403
```

## 8. 影响说明

对 H5：

- 不影响 H5 前端静态资源发布。
- H5 页面调用测试后端接口时，后端 uploads 图片会使用 `test-img.hbabaxb.cn`。

对 PC：

- 不影响 PC 前端静态资源发布。
- PC 页面调用测试后端接口时，后端 uploads 图片会使用 `test-img.hbabaxb.cn`。

对后台上传：

- 不影响上传功能。
- 上传仍写 AWS S3。
- 只是展示域名从 CloudFront 切到 `test-img.hbabaxb.cn`。

对 APK/App 包：

- 本次不改。

## 9. 关联文档

```text
devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md
devops/python/ben-bot/doc/2026-07-29_2155-【网络调整+安全优化】测试后端uploads图片EdgeOne反代与防盗刷落地记录.md
devops/python/ben-bot/doc/2026-07-29_2203-【运维记录】测试PC前端与后端uploads图片反代影响说明.md
```

## 10. 关联提交

```text
f631b59 fix: add test uploads image cdn proxy
97061fd docs: explain test pc image proxy impact
3f7b944 fix: allow no referrer for test image proxy
```
