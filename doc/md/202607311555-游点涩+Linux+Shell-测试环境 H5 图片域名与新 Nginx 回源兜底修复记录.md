---
id: "doc-f9c559dcbf76"
title: "测试环境 H5 图片域名与新 Nginx 回源兜底修复记录"
date: "2026-07-31T15:55:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-31-1555-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83H5%E5%9B%BE%E7%89%87%E5%9F%9F%E5%90%8D%E4%B8%8E%E6%96%B0Nginx%E5%9B%9E%E6%BA%90%E5%85%9C%E5%BA%95%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-31-1555-【修复Bug】测试环境H5图片域名与新Nginx回源兜底修复记录.md"
sourceSha256: "e3be1b244baf8640d354ef9e11e92a125d483e6d6929979073afcc60cceb76f8"
sourceSystem: "project-doc"
---

# 测试环境 H5 图片域名与新 Nginx 回源兜底修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607311555-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20H5%20%E5%9B%BE%E7%89%87%E5%9F%9F%E5%90%8D%E4%B8%8E%E6%96%B0%20Nginx%20%E5%9B%9E%E6%BA%90%E5%85%9C%E5%BA%95%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-31 15:55｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-31 15:55

## 问题现象

用户截图中，测试环境 H5 页面出现图片和静态资源相关报错：

```text
页面：https://h5.youdianse-test.xyz/game
静态资源：https://test-h5-s3.hbabaxb.cn/_nuxt/DAoDNwHT.js
图片资源：https://test-img.hbabaxb.cn/uploads/..._square.webp?敏感凭据：[已脱敏]
```

截图中的主要现象：

```text
test-h5-s3.hbabaxb.cn 的 _nuxt JS 曾出现 CORS 报错
test-img.hbabaxb.cn 的 uploads 图片出现 404 / 固定图异常
```

## 排查结论

### 1. H5 静态资源 CORS 当前公网正常

公网复核：

```text
https://test-h5-s3.hbabaxb.cn/_nuxt/DAoDNwHT.js
HTTP 200
Access-Control-Allow-Origin: *
Content-Type: text/javascript
```

说明当前 H5 静态资源域名已具备跨域响应头。截图里的 CORS 报错更像是边缘缓存、旧响应头或当时回源异常造成。

### 2. test-img 缺失源图没有统一兜底

复现用唯一路径请求：

```text
https://test-img.hbabaxb.cn/uploads/__codex_missing_20260731_1616.webp?敏感凭据：[已脱敏]
```

公网 HTTPS 曾返回：

```text
HTTP 404 / 502
size=150 或 27
未返回 13716 字节固定图
```

这说明公网链路中的某个回源层仍在直接透传 CloudFront 404/502，而不是统一落到固定占位图。

### 3. 新 Nginx 源站曾处于 failed 状态

新服务器：

```text
IP：162.211.181.13
hostname：youdianse-test-cdn-proxy
配置：/etc/nginx/conf.d/youdianse-test-record-domains.conf
```

排查时发现：

```text
nginx.service=failed
80 端口未监听
```

历史失败原因是 Nginx 启动时解析 S3 上游域名失败。重新执行 `nginx -t` 时已通过，因此启动 Nginx 后恢复：

```text
nginx=active
listen=0.0.0.0:80
listen=[::]:80
```

### 4. 公网 test-img 当前未命中新源站

新源站 access log 中能看到本机和 `--resolve` 直连请求：

```text
test-img.hbabaxb.cn code=200 size=13716
test-img.hbazuua.cn code=200 size=13716
```

但公网 HTTPS 唯一路径没有出现在 `162.211.181.13` 的 access log，也没有出现在旧测试服务器 `38.92.8.34` 的已知日志中。

因此当前剩余问题在腾讯 EdgeOne / CDN 层：

```text
test-img.hbabaxb.cn / test-img.hbazuua.cn 的公网 HTTPS 回源没有稳定命中 162.211.181.13:80
```

## 已执行修复

### 1. 修复并启动新源站 Nginx

执行范围：

```text
只操作测试环境新 Nginx 服务器 162.211.181.13
不触碰正式环境
不输出或记录任何敏感密钥
```

处理动作：

```text
备份 /etc/nginx/conf.d/youdianse-test-record-domains.conf
更新 test-img.* /uploads/ 兜底规则
补 PC 静态资源 CORS 头
启动并 reload Nginx
```

验证：

```text
nginx -t：success
systemctl is-active nginx：active
80 端口：listening
```

### 2. test-img 上游错误统一兜底固定图

当前 `test-img.*` 规则：

```text
缺 token：固定图
缺 t：固定图
referer 不允许：固定图
CloudFront 上游 403/404/500/502/503/504：固定图
```

关键 Nginx 行为：

```nginx
proxy_intercept_errors on;
error_page 403 404 500 502 503 504 = @placeholder_image;
```

固定图：

```text
/images/mine/footer-app-download-icon.webp
固定图源站：18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com
预期大小：13716
```

### 3. 静态资源 CORS

H5 静态资源：

```text
test-h5-s3.hbabaxb.cn 当前由 H5 S3 桶返回 CORS
公网验证已包含 Access-Control-Allow-Origin: *
```

PC 静态资源：

```text
test-pc-s3.hbabaxb.cn 在新 Nginx 补充 CORS 响应头
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, HEAD, OPTIONS
Access-Control-Allow-Headers: Origin, Range, Accept, Content-Type, Authorization
Access-Control-Expose-Headers: Content-Length, Content-Range, ETag, Last-Modified
```

## 验证结果

### 新源站本机验证

```text
Host: test-h5-s3.hbabaxb.cn
URL: /_nuxt/DAoDNwHT.js
HTTP 200
Access-Control-Allow-Origin: *
Content-Type: text/javascript
```

```text
Host: test-pc-s3.hbabaxb.cn
URL: /version.json
HTTP 200
Access-Control-Allow-Origin: *
Content-Type: application/json
```

```text
Host: test-img.hbabaxb.cn
URL: /uploads/__codex_missing_20260731_1616.webp?敏感凭据：[已脱敏]
HTTP 200
size=13716
```

```text
Host: test-img.hbazuua.cn
URL: /uploads/__codex_missing_20260731_1616.webp?敏感凭据：[已脱敏]
HTTP 200
size=13716
```

### 直连新源站验证

用 `--resolve` 强制域名走 `162.211.181.13:80`：

```text
test-img.hbabaxb.cn HTTP 200 size=13716
test-img.hbazuua.cn HTTP 200 size=13716
```

说明新源站 Nginx 规则本身已经生效。

### 公网 HTTPS 验证

```text
test-h5-s3.hbabaxb.cn/_nuxt/DAoDNwHT.js：HTTP 200，Access-Control-Allow-Origin: *
test-img.hbabaxb.cn 缺失图：公网仍返回 404，带 CloudFront error 头
test-img.hbazuua.cn 缺失图：公网仍返回 502
```

公网 test-img 唯一路径未进入新源站 access log。

## 仍需在腾讯 EdgeOne / CDN 控制台处理

必须确认并修改以下两个域名的回源：

```text
test-img.hbabaxb.cn
test-img.hbazuua.cn
```

目标配置：

```text
源站类型：IP 源站
源站 IP：162.211.181.13
回源协议：HTTP
回源端口：80
回源 Host：保持原请求域名
缓存：修改后清理 test-img.* /uploads/* 相关缓存
```

不要配置：

```text
HTTPS 回源到 162.211.181.13
直接回源 d1rct3ku9n07y3.cloudfront.net
回源 Host 改成 CloudFront 域名
```

因为当前固定图兜底、token/t 参数检查和上游错误拦截都在 `162.211.181.13` 的 Nginx 里完成。

## 后续验证命令

### 确认公网是否命中新源站

先发公网请求：

```bash
curl -k -sS -D - -o /tmp/test-img-missing.webp \
  -H 'Referer: https://h5.youdianse-test.xyz/game' \
  'https://test-img.hbabaxb.cn/uploads/__edgeone_probe.webp?敏感凭据：[已脱敏]
```

再到新源站查日志：

```bash
ssh root@162.211.181.13 \
  "grep '__edgeone_probe.webp' /var/log/nginx/test-img.record.access.log"
```

预期：

```text
公网 HTTP 200
公网 body size=13716
新源站 access log 有对应请求
```

### 确认 H5 图片 URL 仍带 token/t

```bash
curl -k -sS https://h5.youdianse-test.xyz/game > /tmp/h5-game.html
```

解析要求：

```text
test-img 总数 > 0
token/t 数量 = test-img 总数
sign 数量 = 0
裸链数量 = 0
```

## 当前结论

```text
后端 URL 生成：不是本次根因，页面图片 URL 已带 token/t。
新源站 Nginx：已修复并恢复 active。
H5 静态 CORS：当前公网正常。
test-img 公网缺图：仍需腾讯 EdgeOne / CDN 回源配置切到 162.211.181.13:80 并清缓存。
```
