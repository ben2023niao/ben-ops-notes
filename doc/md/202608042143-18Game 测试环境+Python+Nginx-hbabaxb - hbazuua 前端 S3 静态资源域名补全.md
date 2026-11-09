---
id: "doc-49991df39f4e"
title: "hbabaxb / hbazuua 前端 S3 静态资源域名补全"
date: "2026-08-04T21:43:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "自动化", "CDN", "DNS", "故障排查", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2143-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E5%9F%9F%E5%90%8D%E8%A1%A5%E5%85%A8%E3%80%91hbabaxb-hbazuua%E5%89%8D%E7%AB%AFS3%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E5%9F%9F%E5%90%8D%E8%A1%A5%E5%85%A8.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2143-【运维记录+域名补全】hbabaxb-hbazuua前端S3静态资源域名补全.md"
sourceSha256: "dde19f71ca67946e036708ef0cf183ddd965b7260425d661a6b30b4a17d870c3"
sourceSystem: "project-doc"
---

# hbabaxb / hbazuua 前端 S3 静态资源域名补全

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608042143-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BNginx-hbabaxb%20-%20hbazuua%20%E5%89%8D%E7%AB%AF%20S3%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E5%9F%9F%E5%90%8D%E8%A1%A5%E5%85%A8.md)

> 整理日期：2026-08-04 21:43｜日期依据：文件名日期

环境标签：测试环境、线上前置、腾讯云备案域名、腾讯 COS、日本 Nginx

时间：2026-08-04 21:43

## 本次目标

按用户追加要求，补全以下两个备案域名的前端 S3 静态资源子域：

- `hbabaxb.cn`：08.11 ~ 09.11，200u，用途为测试页面主域 + 测试图片主域
- `hbazuua.cn`：08.11 ~ 09.11，200u，用途为测试页面备用 + 测试图片备用

需要把两个域名也配置上 `test-h5-s3`、`test-pc-s3`、`main-h5-s3`、`main-pc-s3`，并走统一无 CDN 缓存链路：

```text
备案域名 S3 子域
  -> DNS A 记录到日本 Nginx 138.252.248.139
  -> Nginx HTTPS 反代腾讯 COS
  -> 强制 CORS:* 和 no-store/no-cache
```

本任务按用户最新要求只通知：

- `18game运维`
- `18GAME_ 上线群（正式環境）`

未通知：`稳定备案域名+腾讯云原厂`。

## 核心原因

之前整理四个备案域名时，`hbabaxb.cn`、`hbazuua.cn` 主要按“测试页面入口 + 测试图片域”记录；前端 S3 静态资源默认迁移到了 `hbbfuub.cn` 和 `hbakjja.cn`。

用户追加要求明确：`hbabaxb.cn`、`hbazuua.cn` 这两个域名也要补全同样的 S3 静态资源子域，避免后续按测试主域/备用域访问时仍缺少对应静态资源链路。

## DNS 变更

目标 IP：`138.252.248.139`

| 域名 | 类型 | 结果 |
| --- | --- | --- |
| `test-h5-s3.hbabaxb.cn` | CNAME 改 A | 指向日本 Nginx |
| `test-pc-s3.hbabaxb.cn` | CNAME 改 A | 指向日本 Nginx |
| `main-h5-s3.hbabaxb.cn` | 新增 A | 指向日本 Nginx |
| `main-pc-s3.hbabaxb.cn` | 新增 A | 指向日本 Nginx |
| `test-h5-s3.hbazuua.cn` | 新增 A | 指向日本 Nginx |
| `test-pc-s3.hbazuua.cn` | 新增 A | 指向日本 Nginx |
| `main-h5-s3.hbazuua.cn` | 新增 A | 指向日本 Nginx |
| `main-pc-s3.hbazuua.cn` | 新增 A | 指向日本 Nginx |

DNS 验证：

- ben-bot 服务器：8 个 S3 子域名均解析到 `138.252.248.139`
- 日本 Nginx 服务器：8 个 S3 子域名均解析到 `138.252.248.139`
- 本机解析曾有 `test-h5-s3.hbabaxb.cn` 命中旧 EdgeOne 缓存，属于 TTL 过渡，不影响服务器侧和证书签发验证

## Nginx 映射

服务器：`root@138.252.248.139:38927`

配置文件：

- `/etc/nginx/conf.d/30-youdianse-static-cos-proxy.conf`

当前 12 个静态资源域名均已加入 `server_name` 和 COS 上游映射：

| 域名 | COS 桶 |
| --- | --- |
| `test-h5-s3.hbbfuub.cn` | `18game-nuxt-static-test-h5-sg-1450169938` |
| `test-pc-s3.hbbfuub.cn` | `18game-nuxt-static-test-pc-sg-1450169938` |
| `main-h5-s3.hbakjja.cn` | `18game-nuxt-static-preprod-h5-sg-1450169938` |
| `main-pc-s3.hbakjja.cn` | `18game-nuxt-static-preprod-pc-sg-1450169938` |
| `test-h5-s3.hbabaxb.cn` | `18game-nuxt-static-test-h5-sg-1450169938` |
| `test-pc-s3.hbabaxb.cn` | `18game-nuxt-static-test-pc-sg-1450169938` |
| `main-h5-s3.hbabaxb.cn` | `18game-nuxt-static-preprod-h5-sg-1450169938` |
| `main-pc-s3.hbabaxb.cn` | `18game-nuxt-static-preprod-pc-sg-1450169938` |
| `test-h5-s3.hbazuua.cn` | `18game-nuxt-static-test-h5-sg-1450169938` |
| `test-pc-s3.hbazuua.cn` | `18game-nuxt-static-test-pc-sg-1450169938` |
| `main-h5-s3.hbazuua.cn` | `18game-nuxt-static-preprod-h5-sg-1450169938` |
| `main-pc-s3.hbazuua.cn` | `18game-nuxt-static-preprod-pc-sg-1450169938` |

Nginx 检查：

- `nginx -t`：通过
- `systemctl reload nginx`：已执行

## HTTPS 证书

证书名称：

- `test-h5-s3.hbbfuub.cn`

证书已从 4 个域名扩展到 12 个域名，覆盖：

```text
test-h5-s3.hbbfuub.cn
test-pc-s3.hbbfuub.cn
main-h5-s3.hbakjja.cn
main-pc-s3.hbakjja.cn
test-h5-s3.hbabaxb.cn
test-pc-s3.hbabaxb.cn
main-h5-s3.hbabaxb.cn
main-pc-s3.hbabaxb.cn
test-h5-s3.hbazuua.cn
test-pc-s3.hbazuua.cn
main-h5-s3.hbazuua.cn
main-pc-s3.hbazuua.cn
```

证书到期时间：2026-11-02

## 访问验证

验证方式：带 `Origin: https://pc.youdianse-test.xyz` 请求每个域名的 `version.txt`。

| 域名 | HTTP | CORS | 缓存 |
| --- | --- | --- | --- |
| `test-h5-s3.hbbfuub.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `test-pc-s3.hbbfuub.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-h5-s3.hbakjja.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-pc-s3.hbakjja.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `test-h5-s3.hbabaxb.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `test-pc-s3.hbabaxb.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-h5-s3.hbabaxb.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-pc-s3.hbabaxb.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `test-h5-s3.hbazuua.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `test-pc-s3.hbazuua.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-h5-s3.hbazuua.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |
| `main-pc-s3.hbazuua.cn` | 200 | `Access-Control-Allow-Origin: *` | `no-store/no-cache` |

## 当前域名关系

```text
测试页面和图片
  hbabaxb.cn
    test-h5.hbabaxb.cn       测试 H5 主入口
    test-pc.hbabaxb.cn       测试 PC 主入口
    test-img.hbabaxb.cn      测试 uploads 图片主域
  hbazuua.cn
    test-h5.hbazuua.cn       测试 H5 备用入口
    test-pc.hbazuua.cn       测试 PC 备用入口
    test-img.hbazuua.cn      测试 uploads 图片备用域

测试前端静态资源
  默认无 CDN 域
    test-h5-s3.hbbfuub.cn    -> 日本 Nginx -> 测试 H5 腾讯 COS
    test-pc-s3.hbbfuub.cn    -> 日本 Nginx -> 测试 PC 腾讯 COS
  已补全域
    test-h5-s3.hbabaxb.cn    -> 日本 Nginx -> 测试 H5 腾讯 COS
    test-pc-s3.hbabaxb.cn    -> 日本 Nginx -> 测试 PC 腾讯 COS
    test-h5-s3.hbazuua.cn    -> 日本 Nginx -> 测试 H5 腾讯 COS
    test-pc-s3.hbazuua.cn    -> 日本 Nginx -> 测试 PC 腾讯 COS

线上前置静态资源
  默认无 CDN 域
    main-h5-s3.hbakjja.cn    -> 日本 Nginx -> 线上前置 H5 腾讯 COS
    main-pc-s3.hbakjja.cn    -> 日本 Nginx -> 线上前置 PC 腾讯 COS
  已补全域
    main-h5-s3.hbabaxb.cn    -> 日本 Nginx -> 线上前置 H5 腾讯 COS
    main-pc-s3.hbabaxb.cn    -> 日本 Nginx -> 线上前置 PC 腾讯 COS
    main-h5-s3.hbazuua.cn    -> 日本 Nginx -> 线上前置 H5 腾讯 COS
    main-pc-s3.hbazuua.cn    -> 日本 Nginx -> 线上前置 PC 腾讯 COS
```

## 结论

`hbabaxb.cn` 和 `hbazuua.cn` 已补齐前端 S3 静态资源子域，测试和线上前置的 H5/PC 静态资源都可以使用同一套“备案域名 -> 日本 Nginx -> 腾讯 COS”的无 CDN 缓存链路。

本轮主要优化点：

- 补齐测试主/备用备案域名的 S3 静态资源子域，避免域名关系不完整
- 移除静态资源对 EdgeOne/CDN 缓存的依赖，降低 CSS/JS CORS 反复异常
- 统一 HTTPS 证书和 Nginx 反代映射，后续发布和排障口径更清晰
- 保留 `hbbfuub.cn`、`hbakjja.cn` 作为当前默认静态资源域，同时让 `hbabaxb.cn`、`hbazuua.cn` 具备完整备用能力
