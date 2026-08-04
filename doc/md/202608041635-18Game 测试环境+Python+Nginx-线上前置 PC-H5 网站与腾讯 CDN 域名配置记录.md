---
id: "doc-e05d77a76766"
title: "线上前置 PC/H5 网站与腾讯 CDN 域名配置记录"
date: "2026-08-04T16:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "监控告警", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1635-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%2B%E9%85%8D%E7%BD%AE%E9%83%A8%E7%BD%B2%E3%80%91%E7%BA%BF%E4%B8%8A%E5%89%8D%E7%BD%AEPC-H5%E7%BD%91%E7%AB%99%E4%B8%8E%E8%85%BE%E8%AE%AFCDN%E5%9F%9F%E5%90%8D%E9%85%8D%E7%BD%AE.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1635-【运维记录+配置部署】线上前置PC-H5网站与腾讯CDN域名配置.md"
sourceSha256: "6b6a77a97dc94b7069a16b7c28f64513fa4481fa95ed4d6f4e211b2d426adaf8"
sourceSystem: "project-doc"
---

# 线上前置 PC/H5 网站与腾讯 CDN 域名配置记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1635-【运维记录+配置部署】线上前置PC-H5网站与腾讯CDN域名配置.md`

> 整理日期：2026-08-04 16:35｜日期依据：文件名日期

环境标签：线上前置模拟测试 / 游点涩 / PC / H5 / 备案域名 / EdgeOne / COS / CDN / 43.241.16.84

## 1. 本次目标

本次不是做静态说明页，而是为 43.241.16.84 准备游点涩线上前置 PC/H5 前端网站配置、ben-bot 发版入口，以及腾讯 CDN/备案域名链路整理。

43.241.16.84 的定位：

- 上线前最后一次前端模拟测试机器。
- PC/H5 可同机运行。
- 对接线上配置做提前排雷，但不等于直接正式上线。
- 后续可作为线上腾讯云 CDN 备用回源 IP。

## 2. 已完成操作

### 2.1 workbench 与历史资料读取

已读取 workbench 固定入口、机器矩阵、运行链路、通知目标和历史测试 H5/PC 发版、COS/EdgeOne、备案域名链路文档。

核心参考：

- `devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md`
- `devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】腾讯COS新加坡私有化与邮件监控.md`
- `devops/python/ben-bot/doc/2026-08-04_1548-【运维规划+链路整理】备案域名与线上前置前端部署关系.md`

### 2.2 43.241.16.84 Nginx 网站配置

已在服务器部署：

```text
/etc/nginx/conf.d/10-youdianse-preprod-frontends.conf
```

本地留档：

```text
devops/python/ben-bot/data/scripts/线上前置-游点涩-前端配置/nginx/youdianse-preprod-frontends.conf
```

配置内容：

| 类型 | 域名 | 目标 |
| --- | --- | --- |
| H5 页面 | `main-h5.hbabaxb.cn`、`main-h5.hbazuua.cn` | `203.0.113.1:3003` |
| PC 页面 | `test-pc.hbabaxb.cn`、`test-pc.hbazuua.cn`、`main-pc.hbabaxb.cn`、`main-pc.hbazuua.cn` | `203.0.113.1:3004` |
| API 路径 | `/api`、`/channel`、`/customer` | `https://admin.youdianse.com` |
| H5 静态资源路径 | `/images`、`/image`、`/video`、`/videos`、`/media`、`/favicon.ico` | `https://main-h5-s3.hbabaxb.cn` |
| PC 静态资源路径 | `/images`、`/image`、`/video`、`/videos`、`/media`、`/favicon.ico`、`/192.png`、`/512.png` | `https://main-pc-s3.hbabaxb.cn` |

验证结果：

| 检查项 | 结果 |
| --- | --- |
| `nginx -t` | 通过 |
| `systemctl reload nginx` | 通过 |
| 本机 `Host: main-h5.hbabaxb.cn /healthz` | `200` |
| 本机 `Host: test-pc.hbabaxb.cn /healthz` | `200` |
| 本机 `Host: main-pc.hbabaxb.cn /healthz` | `200` |

说明：目前页面根路径需要前端容器启动后才会正常返回业务页面；当前只完成网站入口和健康页验证。

### 2.3 ben-bot 线上前置发版入口

已新增并同步到 ben-bot 宿主机和容器：

```text
devops/python/ben-bot/data/scripts/线上前置-游点涩-h5-发版/
devops/python/ben-bot/data/scripts/线上前置-游点涩-pc-发版/
devops/python/ben-bot/data/scripts/线上前置-游点涩-前端配置/
```

入口规划：

| 入口 | 分支 | 目标服务器 | 容器端口 | 页面域名 | 静态 CDN |
| --- | --- | --- | --- | --- | --- |
| `线上前置-游点涩-h5-发版` | `main` | `43.241.16.84` | `3003` | `https://main-h5.hbabaxb.cn` | `https://main-h5-s3.hbabaxb.cn` |
| `线上前置-游点涩-pc-发版` | `dev` | `43.241.16.84` | `3004` | `https://test-pc.hbabaxb.cn` | `https://main-pc-s3.hbabaxb.cn` |

安全修正：

- 未默认写已有线上 uploads 桶。
- 未默认写线上后端业务资源桶。
- H5/PC 前端静态资源改为独立 preprod 命名：

```text
18game-nuxt-static-preprod-h5
18game-nuxt-static-preprod-h5-sg-1450169938
18game-nuxt-static-preprod-pc
18game-nuxt-static-preprod-pc-sg-1450169938
```

容器内验证：

| 检查项 | 结果 |
| --- | --- |
| `py_compile` | 通过 |
| H5 `list_json` | 能读取 `main` 最近提交 |
| PC `list_json` | 能读取 `dev` 最近提交 |

本次没有触发前端正式发布，没有写 S3/COS 对象，也没有切换 CDN 源站。

## 3. 当前备案域名关系

### 3.1 测试环境现状

| 用途 | 域名 | 当前状态 |
| --- | --- | --- |
| H5 页面 | `test-h5.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在 |
| PC 页面 | `test-pc.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在，当前仍服务测试 PC |
| H5 前端静态资源 | `test-h5-s3.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在 |
| PC 前端静态资源 | `test-pc-s3.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在 |
| 后端 uploads 图片 | `test-img.hbabaxb.cn` | DNSPod CNAME 已存在 |

测试环境域名本次没有切换。

### 3.2 线上前置规划状态

| 用途 | 建议域名 | 当前状态 | 备注 |
| --- | --- | --- | --- |
| H5 页面 | `main-h5.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在；HTTPS 抽测超时 | 待回源链路修通后再切源到 43.241.16.84 |
| PC 页面 | `main-pc.hbabaxb.cn` | 当前未解析 | 建议新增独立 PC 前置域名，避免复用 `test-pc` 影响测试环境 |
| PC 页面临时候选 | `test-pc.hbabaxb.cn` | 当前已被测试 PC 使用 | 不建议直接切到 43.241.16.84 |
| H5 前端静态资源 | `main-h5-s3.hbabaxb.cn` | 当前未解析 | 需要新建 EdgeOne 域名和 COS 源站 |
| PC 前端静态资源 | `main-pc-s3.hbabaxb.cn` | 当前未解析 | 需要新建 EdgeOne 域名和 COS 源站 |
| 后端 uploads 图片 | `main-img.hbabaxb.cn` | 当前未解析 | 可作为 `main-s3.hbabaxb.cn` 的语义化别名，但需要单独建 EdgeOne/DNS/证书 |
| 线上业务资源现有域名 | `main-s3.hbabaxb.cn` | DNSPod CNAME 已存在，EdgeOne 域名已存在 | 当前已指向线上腾讯新加坡 COS uploads 桶 |

## 4. 当前阻塞点

### 4.1 43.241.16.84 公网 HTTP 回源异常

现象：

- 服务器本机访问 Nginx 正常。
- 从 ben-bot AWS 机器访问 `43.241.16.84:80`：TCP 能建立，但 HTTP 请求超时，无响应体。
- 抓包只看到超时后的连接关闭包，没有看到完整 HTTP 请求进入 Nginx。
- 本机防火墙未阻断：UFW inactive，iptables INPUT 默认 ACCEPT，Nginx 正常监听 80。

影响：

- 当前不适合把 EdgeOne 页面域名源站切到 `43.241.16.84`。
- 若现在切源，腾讯 CDN 回源大概率会超时，页面会不可用。

建议：

- 联系服务器供应商或机房检查 80 端口 HTTP 数据链路、防护策略、安全组、回程路由。
- 修复后至少从 ben-bot AWS 机器验证：

```text
curl -H "Host: main-h5.hbabaxb.cn" http://43.241.16.84/healthz
curl -H "Host: main-pc.hbabaxb.cn" http://43.241.16.84/healthz
```

均应返回 `ok`。

### 4.2 `test-pc.hbabaxb.cn` 与线上前置 PC 命名冲突

用户给的线上环境规划里 PC 页面写了 `test-pc.备案域名`，但当前 `test-pc.hbabaxb.cn` 已经是测试 PC 入口。

结论：

- 不建议直接把 `test-pc.hbabaxb.cn` 切到 43.241.16.84。
- 推荐新增 `main-pc.hbabaxb.cn` 作为线上前置 PC 页面域名。
- Nginx 已提前兼容 `main-pc.hbabaxb.cn`，待 EdgeOne/DNS 配好即可使用。

### 4.3 线上前置静态资源域名未落地

当前缺：

```text
main-h5-s3.hbabaxb.cn
main-pc-s3.hbabaxb.cn
```

需要完成：

1. 创建或确认独立 preprod COS 前端静态桶。
2. 创建 EdgeOne 加速域名，源站指向对应 COS 私有桶。
3. 配置 CNAME 到 DNSPod。
4. 配置 EdgeOne 证书验证记录。
5. 验证 COS 原始域名私有、EdgeOne 域名可读。

## 5. 后续落地清单

建议按以下顺序执行：

1. 修通 43.241.16.84 公网 HTTP 回源。
2. 新建 `main-pc.hbabaxb.cn` EdgeOne 页面域名，源站 `43.241.16.84`，Host Header 用 `main-pc.hbabaxb.cn`。
3. 复核 `main-h5.hbabaxb.cn` 是否可切到 `43.241.16.84`，切换前保留回滚源站。
4. 新建 `main-h5-s3.hbabaxb.cn`、`main-pc-s3.hbabaxb.cn` 静态资源 EdgeOne 域名。
5. 新建或确认 preprod COS 前端静态桶，并保持私有。
6. DNSPod 补齐 `main-pc`、`main-h5-s3`、`main-pc-s3`、按需补 `main-img`。
7. 用 ben-bot 线上前置 H5/PC 入口选择提交发布到 43.241.16.84。
8. 验证页面、`version.txt`、`version.json`、`_nuxt`、图片、视频资源加载。
9. 再决定是否把稳定版本发布到正式 AWS 前端服务器。

## 6. 群通知记录

本次按要求每个阶段都已通知：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容均只包含操作总结、结果和阻塞点，未包含密码、token、Secret Key、私钥、Cookie 或完整 Signed URL。

## 7. 本次核心结论

本次已经把 43.241.16.84 的线上前置 H5/PC Nginx 网站配置和 ben-bot 发版入口准备好，并完成容器内校验；但腾讯 CDN 页面域名还不能安全切到这台机器，核心原因是 43.241.16.84 公网 HTTP 回源链路异常。

另外，`test-pc.hbabaxb.cn` 已经承载测试 PC，不适合作为线上前置 PC 域名直接复用；建议新增 `main-pc.hbabaxb.cn`。前端静态资源的 `main-h5-s3/main-pc-s3` 还需要补 EdgeOne、DNSPod、证书和独立 COS 私有桶后，才能执行真正的前置发版与网页验证。
