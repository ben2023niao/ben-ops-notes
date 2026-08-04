---
id: "doc-dccb1be24f59"
title: "四个备案域名测试页面入口补全"
date: "2026-08-04T22:19:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2219-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E5%9F%9F%E5%90%8D%E8%A1%A5%E5%85%A8%E3%80%91%E5%9B%9B%E4%B8%AA%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E6%B5%8B%E8%AF%95%E9%A1%B5%E9%9D%A2%E5%85%A5%E5%8F%A3%E8%A1%A5%E5%85%A8.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2219-【运维记录+域名补全】四个备案域名测试页面入口补全.md"
sourceSha256: "9eabf42b284c1e6d8c5b130a7211bc0a7f0e7e32e08a5c8115ed5b7519048d78"
sourceSystem: "project-doc"
---

# 四个备案域名测试页面入口补全

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2219-【运维记录+域名补全】四个备案域名测试页面入口补全.md`

> 整理日期：2026-08-04 22:19｜日期依据：文件名日期

环境标签：测试环境、腾讯云备案域名、DNSPod、Nginx、HTTPS 证书

时间：2026-08-04 22:19

## 一、本次目标

用户指出测试环境页面只列了 `hbabaxb.cn`、`hbazuua.cn`，要求把另外两个备案域名也补全。

本次补全对象：

- `test-h5.hbbfuub.cn`
- `test-pc.hbbfuub.cn`
- `test-h5.hbakjja.cn`
- `test-pc.hbakjja.cn`

## 二、改造内容

### DNS

已在 DNSPod 新增 4 条 A 记录，全部指向测试前端服务器：

```text
test-h5.hbbfuub.cn  -> 38.92.8.34
test-pc.hbbfuub.cn  -> 38.92.8.34
test-h5.hbakjja.cn  -> 38.92.8.34
test-pc.hbakjja.cn  -> 38.92.8.34
```

### Nginx

已在测试前端服务器 `38.92.8.34` 更新 H5/PC 站点配置：

- H5 站点加入 `test-h5.hbbfuub.cn`、`test-h5.hbakjja.cn`
- PC 站点加入 `test-pc.hbbfuub.cn`、`test-pc.hbakjja.cn`
- ACME challenge 路径已在 HTTP/HTTPS server block 中补齐
- `nginx -t` 通过并已 reload

### HTTPS 证书

已签发 Let's Encrypt 证书：

- 证书名：`youdianse-test-pages-icp`
- 到期时间：`2026-11-02`
- 覆盖域名：
  - `h5.youdianse-test.xyz`
  - `pc.youdianse-test.xyz`
  - `sdk.youdianse-test.xyz`
  - `test-h5.hbbfuub.cn`
  - `test-pc.hbbfuub.cn`
  - `test-h5.hbakjja.cn`
  - `test-pc.hbakjja.cn`

## 三、验证结果

严格 HTTPS 验证结果：

```text
test-h5.hbbfuub.cn        /             200
test-h5.hbbfuub.cn        /version.json 200
test-pc.hbbfuub.cn        /             200
test-pc.hbbfuub.cn        /version.json 200
test-h5.hbakjja.cn        /             200
test-h5.hbakjja.cn        /version.json 200
test-pc.hbakjja.cn        /             200
test-pc.hbakjja.cn        /version.json 200
h5.youdianse-test.xyz     /             200
h5.youdianse-test.xyz     /version.json 200
pc.youdianse-test.xyz     /             200
pc.youdianse-test.xyz     /version.json 200
```

观察项：

- `test-h5.hbazuua.cn` 旧 EdgeOne 备用链路本轮仍观察到 SSL 连接超时。
- 该问题属于旧备用 EdgeOne 链路观察项，不影响本轮新增的 `hbbfuub.cn`、`hbakjja.cn` 直连测试页面入口。

## 四、更新后的域名关系

### 域名费用与定位

```text
hbabaxb.cn   08.11-09.11  200u
用途：测试页面主域 + 测试图片主域

hbazuua.cn   08.11-09.11  200u
用途：测试页面备用 + 测试图片备用

hbbfuub.cn   08.04-09.04  200u
用途：测试 H5/PC 前端静态资源，同时已补测试页面入口

hbakjja.cn   08.04-09.04  200u
用途：线上前置 H5/PC 前端静态资源，同时已补测试页面入口
```

### 测试环境页面

```text
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
```

### 页面入口链路

```text
用户浏览器
  -> test-h5 / test-pc 备案页面域名
  -> 测试前端服务器 38.92.8.34
  -> H5 容器 3003 / PC 容器 3004
```

### 前端静态资源链路

```text
用户浏览器
  -> test-h5-s3 / test-pc-s3 / main-h5-s3 / main-pc-s3
  -> 日本 Nginx 138.252.248.139
  -> 腾讯 COS
```

## 五、结论

- 4 个备案域名的测试页面关系已补齐。
- 新增 4 个测试页面入口已完成 DNS、Nginx、HTTPS 证书和访问验证。
- 页面入口和前端静态资源入口已经分开：页面走测试前端服务器，静态资源走日本 Nginx 反代腾讯 COS。
- 前端静态资源仍保持不走腾讯 CDN / EdgeOne，继续规避缓存和 CORS 反复问题。
