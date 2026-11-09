---
id: "doc-57394c04de12"
title: "测试 PC 图片相对路径反代与腾讯鉴权修复记录"
date: "2026-07-29T20:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "自动化", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2045-%E3%80%90%E4%BF%AE%E5%A4%8DBug%2B%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%9B%BE%E7%89%87%E7%9B%B8%E5%AF%B9%E8%B7%AF%E5%BE%84%E5%8F%8D%E4%BB%A3%E4%B8%8E%E8%85%BE%E8%AE%AF%E9%89%B4%E6%9D%83%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2045-【修复Bug+网络调整】测试PC图片相对路径反代与腾讯鉴权修复记录.md"
sourceSha256: "07d0af35b6bcd33d3e02b68c830f68b9be206d0ece232a60fd7b32654c16774a"
sourceSystem: "project-doc"
---

# 测试 PC 图片相对路径反代与腾讯鉴权修复记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607292045-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BNginx-%E6%B5%8B%E8%AF%95%20PC%20%E5%9B%BE%E7%89%87%E7%9B%B8%E5%AF%B9%E8%B7%AF%E5%BE%84%E5%8F%8D%E4%BB%A3%E4%B8%8E%E8%85%BE%E8%AE%AF%E9%89%B4%E6%9D%83%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 20:45｜日期依据：文件名日期

环境标签：测试环境

更新时间：2026-07-29 20:45

状态更新：2026-07-29 21:19 已回退前端静态资源鉴权，页面域名 `/images/*` 兼容反代可保留，但不再追加或校验 token；当前有效方案以 `2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md` 为准。

## 1、问题现象

- 访问 `https://test-pc.hbabaxb.cn/` 时，部分 `webp`、`svg` 图片显示异常。
- 浏览器 Network 可见部分资源请求到 `https://test-pc-s3.hbabaxb.cn/images/...` 后出现 524 或连接异常。
- 另有部分相对路径资源请求到页面域名，例如 `https://test-pc.hbabaxb.cn/images/placeholder.webp?...`，返回内容曾为 Nuxt HTML，而不是图片。

## 2、影响范围

- 测试环境 PC 页面：
  - `https://pc.youdianse-test.xyz/`
  - `https://test-pc.hbabaxb.cn/`
- 测试 PC 前端静态资源域名：
  - `https://test-pc-s3.hbabaxb.cn`
- 本次只处理测试 PC 前端静态图片/媒体资源，不改后端 uploads、APK/App 包链路。

## 3、原因判断

- PC 前端构建后，`_nuxt` 的 CSS/JS 资源走腾讯静态域名 `test-pc-s3.hbabaxb.cn`。
- 图片、SVG、WebP 等媒体资源启用了腾讯 EdgeOne/COS URL 鉴权，未签名访问会返回 403，这是预期。
- 部分运行时或 HTML 内的 `/images/...` 相对路径会落到页面域名：
  - `pc.youdianse-test.xyz/images/...`
  - `test-pc.hbabaxb.cn/images/...`
- 页面域名原来由 Nuxt 容器接管 `/images/...`，导致某些图片请求返回 HTML，浏览器显示为坏图。
- 曾尝试在构建产物中把 `/images/...` 改为绝对腾讯静态域名，但前端运行时已有 CDN 前缀拼接逻辑，容易生成双重 URL，因此已回退。

## 4、修复方案

- 保持构建产物的图片签名逻辑不再强行改成绝对 URL。
- 在测试 PC 页面域名 Nginx 增加媒体路径反代：
  - `/images/`
  - `/image/`
  - `/video/`
  - `/videos/`
  - `/media/`
  - `/favicon.ico`
  - `/192.png`
  - `/512.png`
- 上述路径统一反代到 `https://test-pc-s3.hbabaxb.cn`，保留原始 query token。
- 这样相对路径访问页面域名时，也会转到腾讯静态资源链路，并继续受腾讯鉴权保护。

## 5、操作记录

- 更新本地 Nginx 模板：
  - `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf`
- 线上测试服务器 Nginx 配置备份：
  - `/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf.bak.pc-image-proxy-20260729203505`
- 测试服务器执行：
  - `nginx -t` 通过
  - `nginx -s reload` 成功
- 回退不合适的“相对图片改绝对腾讯 CDN URL”方案。
- 发布结构版本升级：
  - `tooling-v18-tencent-auth-media-only`
  - `tooling-v19-tencent-auth-root-relative-proxy`
- 通过机器人重新发布测试 PC 当前版本：
  - 发布入口：`测试环境-游点涩-pc-发版`
  - git 短 ID：`b209f18`
  - 发布结果：成功
  - 耗时：约 238.7 秒

## 6、验证结果

- 版本检查：
  - `https://pc.youdianse-test.xyz/version.json`：`b209f18`
  - `https://test-pc.hbabaxb.cn/version.json`：`b209f18`
  - `https://test-pc-s3.hbabaxb.cn/version.json`：`b209f18`
- HTML 检查：
  - 未发现 `test-pc-s3.hbabaxb.cn/https://test-pc-s3.hbabaxb.cn` 双重静态域名前缀。
- 页面域名相对图片检查：
  - `https://test-pc.hbabaxb.cn/images/placeholder.webp?...` 返回 `206 image/webp`
  - `https://pc.youdianse-test.xyz/images/placeholder.webp?...` 返回 `206 image/webp`
- CSS 图片签名检查：
  - `bullet.svg`、`bullet-active.svg`、`menu.svg`、`main-bg.webp` 等 CSS 引用均已带 `token` 和 `t` 参数。
- 真实签名样本检查：
  - `test-pc-s3.hbabaxb.cn/images/bullet.svg?...` 返回 `200 image/svg+xml`
  - `test-pc.hbabaxb.cn/images/bullet.svg?...` 返回 `200 image/svg+xml`
  - `test-pc.hbabaxb.cn/images/menu.svg?...` 连续 3 次返回 `200 image/svg+xml`
  - `test-pc.hbabaxb.cn/images/index-new/main-bg.webp?...` 连续 3 次返回 `200 image/webp`
- 鉴权检查：
  - 不带 token 的 `test-pc-s3.hbabaxb.cn/images/bullet.svg` 返回 403。
  - 不带 token 的 `test-pc.hbabaxb.cn/images/bullet.svg` 返回 403。

## 7、当前结论

- 测试 PC 页面域名下的相对图片路径已由 Nginx 转到腾讯静态资源域名，不再返回 Nuxt HTML。
- 腾讯 COS/EdgeOne 私有化和 URL 鉴权仍然生效，未签名访问继续拒绝。
- PC 发布流程已重新发布并刷新腾讯缓存，当前版本一致。
- 如后续新增更多页面域名，只要共用该 PC Nginx 模板或同等媒体路径反代规则，就不需要逐个改前端代码。

## 8、后续建议

- H5 测试环境如出现同类 `/images/...` 相对路径问题，可按 PC 方案增加页面域名媒体路径反代。
- 对 EdgeOne 静态域名可继续观察不同网络运营商节点的 524/连接重置，如持续复现再单独排查腾讯边缘节点或回源策略。
- 发布机器人最终通知中继续保留备案域名、腾讯静态域名、版本信息和日志附件，方便业务侧复核。
