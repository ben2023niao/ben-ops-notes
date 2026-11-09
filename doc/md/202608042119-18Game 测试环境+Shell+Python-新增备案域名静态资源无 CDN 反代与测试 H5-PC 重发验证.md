---
id: "doc-eed6b7d37cdd"
title: "新增备案域名静态资源无 CDN 反代与测试 H5/PC 重发验证"
date: "2026-08-04T21:19:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2119-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E9%93%BE%E8%B7%AF%E6%94%B9%E9%80%A0%E3%80%91%E6%96%B0%E5%A2%9E%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%97%A0CDN%E5%8F%8D%E4%BB%A3%E4%B8%8E%E6%B5%8B%E8%AF%95H5-PC%E9%87%8D%E5%8F%91%E9%AA%8C%E8%AF%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_2119-【修复Bug+链路改造】新增备案域名静态资源无CDN反代与测试H5-PC重发验证.md"
sourceSha256: "023d56ad54b261df5ba8ab53263dbad3a04ed9f3597c52603678e5257bb548ba"
sourceSystem: "project-doc"
---

# 新增备案域名静态资源无 CDN 反代与测试 H5/PC 重发验证

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608042119-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%96%B0%E5%A2%9E%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%97%A0%20CDN%20%E5%8F%8D%E4%BB%A3%E4%B8%8E%E6%B5%8B%E8%AF%95%20H5-PC%20%E9%87%8D%E5%8F%91%E9%AA%8C%E8%AF%81.md)

> 整理日期：2026-08-04 21:19｜日期依据：文件名日期

环境标签：测试环境 / 线上前置 / 腾讯云备案域名 / COS / Nginx / H5 / PC

记录时间：2026-08-04 21:19

## 本次结论

- 已把新增备案域名用于前端静态资源新链路，测试 H5/PC 不再引用旧 `test-h5-s3.hbabaxb.cn`、`test-pc-s3.hbabaxb.cn` 静态域。
- 本次核心修复不是继续刷新旧 EdgeOne 缓存，而是把前端静态资源切到新备案域名，并通过日本服务器 Nginx 反代独立腾讯 COS 桶，强制 `CORS:*` 和 `no-store`。
- 测试 H5 已重发 `9d3d113`，测试 PC 已重发 `c842f12`。
- 页面验证通过：PC/H5 页面入口 200，页面 HTML 中旧静态域引用数为 0，新静态域引用已生效。
- 静态资源验证通过：PC/H5 entry CSS 均返回 `200 + text/css + Access-Control-Allow-Origin:* + Cache-Control:no-store`。
- 四个新静态资源域验证通过：DNS 均指向 `138.252.248.139`，HTTPS 证书覆盖，`version.txt` 均返回 `200 + CORS:* + no-store`。

## 本次通知范围

用户已明确要求后续不要再通知 `稳定备案域名+腾讯云原厂`。

本次后续通知只发送到：

- `18game运维`
- `18GAME_ 上线群（正式環境）`

## 问题核心原因

截图中的失败表现是 CSS/JS 请求返回 `200`，但浏览器仍报 CORS 错误。原因是旧静态资源域名虽然命名为 `*-s3`，但实际仍走 EdgeOne：

- `test-h5-s3.hbabaxb.cn`
- `test-pc-s3.hbabaxb.cn`

旧 EdgeOne 边缘节点存在响应头不一致问题，部分节点返回对象时缺少 `Access-Control-Allow-Origin`。浏览器会直接拦截跨域 stylesheet/script，因此页面样式、弹窗组件、图片资源表现为反复异常。

继续刷新旧 CDN 只能临时止血，不能彻底避免边缘缓存抖动。彻底方案是：新备案域名、新静态资源入口、独立 COS 桶、禁用腾讯 CDN/EdgeOne 缓存。

## 最终链路

### 测试环境

| 类型 | 域名 | 当前链路 |
| --- | --- | --- |
| H5 页面 | `https://h5.youdianse-test.xyz/` | 测试 H5 容器，版本 `9d3d113` |
| PC 页面 | `https://pc.youdianse-test.xyz/` | 测试 PC 容器，版本 `c842f12` |
| H5 备案入口 | `https://test-h5.hbabaxb.cn/` | 现有备案页面入口，保持不变 |
| PC 备案入口 | `https://test-pc.hbabaxb.cn/` | 现有备案页面入口，保持不变 |
| H5 前端静态资源 | `https://test-h5-s3.hbbfuub.cn/` | DNS A -> `138.252.248.139` -> 日本 Nginx -> 腾讯 COS |
| PC 前端静态资源 | `https://test-pc-s3.hbbfuub.cn/` | DNS A -> `138.252.248.139` -> 日本 Nginx -> 腾讯 COS |
| 后端 uploads 图片 | `https://test-img.hbabaxb.cn/uploads/...` | 后端上传资源链路，和前端构建资源分离 |

### 线上前置/上线前模拟

| 类型 | 域名 | 当前链路 |
| --- | --- | --- |
| H5 前端静态资源 | `https://main-h5-s3.hbakjja.cn/` | DNS A -> `138.252.248.139` -> 日本 Nginx -> 线上前置 H5 COS |
| PC 前端静态资源 | `https://main-pc-s3.hbakjja.cn/` | DNS A -> `138.252.248.139` -> 日本 Nginx -> 线上前置 PC COS |

说明：线上前置页面容器后续部署到日本服务器后，再按 `main-h5/main-pc` 页面入口继续接入。前端静态资源域本次已先配置出来，方便后续发版直接使用。

## DNS 与 Nginx 配置

### DNSPod 记录

| 域名 | 类型 | 值 | TTL |
| --- | --- | --- | --- |
| `test-h5-s3.hbbfuub.cn` | A | `138.252.248.139` | 600 |
| `test-pc-s3.hbbfuub.cn` | A | `138.252.248.139` | 600 |
| `main-h5-s3.hbakjja.cn` | A | `138.252.248.139` | 600 |
| `main-pc-s3.hbakjja.cn` | A | `138.252.248.139` | 600 |

### 日本服务器

- 服务器：`138.252.248.139:38927`
- 角色：线上前置/静态资源反代入口
- Nginx 配置：`/etc/nginx/conf.d/30-youdianse-static-cos-proxy.conf`
- 公共片段：`/etc/nginx/snippets/youdianse-static-cos-proxy-common.conf`
- 证书：Let's Encrypt
- 证书到期：2026-11-02
- 证书 SAN：
  - `test-h5-s3.hbbfuub.cn`
  - `test-pc-s3.hbbfuub.cn`
  - `main-h5-s3.hbakjja.cn`
  - `main-pc-s3.hbakjja.cn`

Nginx 反代策略：

- 按 Host 转发到各自独立 COS bucket endpoint。
- 对外统一补充 `Access-Control-Allow-Origin:*`。
- 对外统一补充 `Cache-Control:no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0`。
- 隐藏上游可能冲突的 CORS 头和强制下载头。
- 支持 `OPTIONS` 预检返回 204。

## COS 桶关系

| 用途 | COS 桶 |
| --- | --- |
| 测试 H5 静态资源 | `18game-nuxt-static-test-h5-sg-1450169938` |
| 测试 PC 静态资源 | `18game-nuxt-static-test-pc-sg-1450169938` |
| 线上前置 H5 静态资源 | `18game-nuxt-static-preprod-h5-sg-1450169938` |
| 线上前置 PC 静态资源 | `18game-nuxt-static-preprod-pc-sg-1450169938` |

四个桶已统一配置 CORS：

- Method：`GET, HEAD`
- Origin：`*`
- Header：`*`
- Expose：`ETag, Content-Length, Content-Type`
- MaxAge：86400

## 为什么没有继续用 COS 直连 HTTPS

最初尝试为 COS 绑定自定义源站域名，HTTP/COS 配置一度可查询，但公网 HTTPS 访问会遇到 COS 默认证书与自定义域名不匹配问题。由于页面是 HTTPS，不能切到 HTTP 静态资源，也不能让浏览器接受证书不匹配。

因此本次采用腾讯文档支持的 HTTPS 反代方案：自定义域名解析到自管 Nginx，Nginx 持有正确证书，再反代到 COS endpoint。这样既不走腾讯 CDN/EdgeOne，也能保证 HTTPS、CORS 和缓存策略可控。

参考：

- Tencent Cloud COS 自定义源站域名与 HTTPS 证书说明：`https://www.tencentcloud.com/document/product/436/31507`
- Tencent Cloud COS HTTPS 访问反向代理方式：`https://www.tencentcloud.com/document/product/436/11142`
- Tencent Cloud COS 自定义源站域名证书/访问异常说明：`https://www.tencentcloud.com/document/product/436/40174`

## 发布脚本改造

已同步到 ben-bot 宿主机和容器：

- `测试环境-游点涩-h5-发版`
  - 默认静态域：`https://test-h5-s3.hbbfuub.cn`
  - 腾讯 CDN 刷新：关闭
- `测试环境-游点涩-pc-发版`
  - 默认静态域：`https://test-pc-s3.hbbfuub.cn`
  - 腾讯 CDN 刷新：关闭
- `线上前置-游点涩-h5-发版`
  - 默认静态域：`https://main-h5-s3.hbakjja.cn`
  - 腾讯 CDN 刷新：关闭
- `线上前置-游点涩-pc-发版`
  - 默认静态域：`https://main-pc-s3.hbakjja.cn`
  - 腾讯 CDN 刷新：关闭

脚本校验：

- 本地 `py_compile`：通过。
- 容器内 `py_compile`：通过。
- 容器内 H5/PC `list_json`：通过。
- 容器内配置 grep：四个新静态资源域已生效。

## 发布结果

### 测试 H5

- Commit：`9d3d113`
- 分支：`test`
- 页面：`https://h5.youdianse-test.xyz/`
- 版本：`https://h5.youdianse-test.xyz/version.txt`
- 构建静态域：`https://test-h5-s3.hbbfuub.cn`
- 结果：发布成功，容器已启动。

### 测试 PC

- Commit：`c842f12`
- 分支：`dev`
- 页面：`https://pc.youdianse-test.xyz/`
- 版本：`https://pc.youdianse-test.xyz/version.txt`
- 构建静态域：`https://test-pc-s3.hbbfuub.cn`
- 结果：发布成功，容器已启动。

## 验证结果

### 页面版本

| 页面 | HTTP | 版本 |
| --- | --- | --- |
| `https://pc.youdianse-test.xyz/version.txt` | 200 | `c842f12` |
| `https://h5.youdianse-test.xyz/version.txt` | 200 | `9d3d113` |

页面入口抽查：

| 页面 | HTTP |
| --- | --- |
| `https://pc.youdianse-test.xyz/` | 200 |
| `https://h5.youdianse-test.xyz/` | 200 |
| `https://test-pc.hbabaxb.cn/` | 200 |
| `https://test-h5.hbabaxb.cn/` | 200 |

### 页面静态域引用

| 页面 | 旧静态域引用 | 新静态域引用 |
| --- | --- | --- |
| PC | `test-pc-s3.hbabaxb.cn` = 0 | `test-pc-s3.hbbfuub.cn` = 115 |
| H5 | `test-h5-s3.hbabaxb.cn` = 0 | `test-h5-s3.hbbfuub.cn` = 111 |

说明：PC/H5 页面仍会出现 `test-img.hbabaxb.cn`，这是后端 uploads 图片链路，不是前端构建静态资源链路，本次不改。

### CSS 抽样

| 资源 | HTTP | Content-Type | CORS | Cache-Control |
| --- | --- | --- | --- | --- |
| `https://test-pc-s3.hbbfuub.cn/_nuxt/entry.K3NpkUUj.css` | 200 | `text/css` | `*` | `no-store` |
| `https://test-h5-s3.hbbfuub.cn/_nuxt/entry.9fJ8Knpu.css` | 200 | `text/css` | `*` | `no-store` |

### 四个新域名抽查

| 域名 | DNS | HTTPS | CORS | Cache |
| --- | --- | --- | --- | --- |
| `test-h5-s3.hbbfuub.cn` | `138.252.248.139` | 200 | `*` | `no-store` |
| `test-pc-s3.hbbfuub.cn` | `138.252.248.139` | 200 | `*` | `no-store` |
| `main-h5-s3.hbakjja.cn` | `138.252.248.139` | 200 | `*` | `no-store` |
| `main-pc-s3.hbakjja.cn` | `138.252.248.139` | 200 | `*` | `no-store` |

服务器侧验证：

- ben-bot 服务器解析四个域名均为 `138.252.248.139`。
- 日本服务器本机解析四个域名均为 `138.252.248.139`。
- 日本服务器 `nginx -t` 通过。

## 已发群通知

已按步骤发送：

- H5 重发完成通知。
- PC 重发完成通知。
- 后续最终汇总和本文档只发送到 `18game运维` 与 `18GAME_ 上线群（正式環境）`。

## 后续建议

1. 测试同事刷新浏览器缓存或用无痕窗口复测 PC/H5，重点看 Network 是否仍有 `test-*-s3.hbabaxb.cn` 静态资源请求。
2. 如浏览器已安装旧 PWA/Service Worker，建议在 DevTools Application 中 unregister 旧 SW 后再复测。
3. 线上前置 H5/PC 发版时直接使用 `main-h5-s3.hbakjja.cn`、`main-pc-s3.hbakjja.cn`，不要再回到旧 EdgeOne 静态域。
4. 证书到期前需要确认证书自动续期；当前到期时间为 2026-11-02。
