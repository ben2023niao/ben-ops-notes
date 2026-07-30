---
id: "doc-378b42b931ed"
title: "测试图片加密防盗刷多域名签名配置优化记录"
date: "2026-07-30T18:28:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1828-%E3%80%90%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%2B%E5%90%8E%E7%AB%AF%E6%94%B9%E9%80%A0%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E5%8A%A0%E5%AF%86%E9%98%B2%E7%9B%97%E5%88%B7%E5%A4%9A%E5%9F%9F%E5%90%8D%E7%AD%BE%E5%90%8D%E9%85%8D%E7%BD%AE%E4%BC%98%E5%8C%96%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1828-【安全优化+后端改造】测试图片加密防盗刷多域名签名配置优化记录.md"
sourceSha256: "ba4a5be42438a8684ab931734b9bfa23be99c7f6eca7d1c7ebb90d08fea95ac3"
sourceSystem: "project-doc"
---

# 测试图片加密防盗刷多域名签名配置优化记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1828-【安全优化+后端改造】测试图片加密防盗刷多域名签名配置优化记录.md`

> 整理日期：2026-07-30 18:28｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-30 18:28

## 背景

测试环境后端 uploads 图片已经通过 `test-img.hbabaxb.cn`、`test-img.hbazuua.cn` 接入腾讯 EdgeOne/CDN，用于减少图片被直接复制、公开数据采集和盗刷。

之前后端图片签名逻辑较偏单域名或固定写法，后续如果继续增加备案图片域名，代码容易反复改动。此次优化目标是把图片签名规则收敛到 env 配置中，代码只做通用读取和签名。

## 本次目标

- 不改上传逻辑。
- 不改 AWS S3 和 AWS CloudFront 老链路。
- 不影响线上现有 AWS 图片访问方式。
- 只对 env 明确配置的腾讯图片 CDN 域名生效。
- 新增图片域名时尽量只改 env，不再改 PHP 代码。

## 后端代码变更

后端仓库：

```text
/Users/ben/Documents/ben/docker/dev/docker-youdianse-php/src/youdianse-php
```

分支：

```text
dev
```

提交：

```text
cbd772ff fix: support per-domain cdn image signing
```

修改文件：

```text
app/Services/Common/CommonService.php
```

主要改动：

- `getCdnUrl()` 返回 URL 前统一经过 `signCdnUrlIfNeeded()`。
- `signCdnUrlIfNeeded()` 只处理 env 里明确配置的腾讯 CDN 图片域名。
- 只处理命中 `domain + path_prefix` 的路径，例如 `/uploads/`。
- 已经带 `token/t` 的图片 URL 不重复追加签名。
- AWS CloudFront、AWS S3、其他不匹配的绝对 URL 原样返回。
- 保留远端 `dev` 最新 `media://` 处理逻辑，避免媒体路径被提前返回。

## env 配置方式

示例结构如下，密钥只放 env，不写进代码和文档明文：

```ini
[cdn.tencent.test-img.hbabaxb.cn]
domain=test-img.hbabaxb.cn
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=仅 env 保存，不记录明文
key_file=

[cdn.tencent.test-img.hbazuua.cn]
domain=test-img.hbazuua.cn
path_prefix=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=仅 env 保存，不记录明文
key_file=
```

后续新增图片 CDN 域名时，按相同格式增加一段配置即可。

## 签名规则

当前按腾讯 EdgeOne/CDN 鉴权规则生成：

```text
敏感凭据：[已脱敏] + uri_path + timestamp)
t = 当前时间戳
```

说明：

- `key` 来自 env 或 `key_file`。
- `uri_path` 只取 URL path，例如 `/uploads/2025-11-12/xxx.webp`。
- `t` 是签名时间戳。
- 有效期由 EdgeOne/CDN 鉴权规则控制。

## 生效范围

会签名：

```text
https://test-img.hbabaxb.cn/uploads/xxx.webp
https://test-img.hbazuua.cn/uploads/xxx.webp
```

不会签名，会原样返回：

```text
https://d1rct3ku9n07y3.cloudfront.net/uploads/xxx.webp
https://其他未配置域名/uploads/xxx.webp
https://test-img.hbabaxb.cn/非uploads路径/xxx.webp
```

## 对业务影响

对测试 PC/H5：

- 后端接口返回的测试图片域名如果是 `test-img.*`，会自动带 `token/t`。
- 页面内正常加载图片不受影响。
- 直接复制裸图片 URL 打开时，会由 Nginx/EdgeOne 规则返回默认占位图或拒绝原图。

对 AWS 老链路：

- AWS CloudFront 绝对 URL 不匹配 env 中的腾讯域名配置，会原样返回。
- 不影响线上当前 AWS S3 图片访问。
- 不影响后台上传到 AWS S3 的动作。

对开发：

- 新增图片 CDN 域名优先改 env。
- 不建议在业务代码里硬编码新域名和密钥。
- 如果新增路径需要防盗刷，只扩展 `path_prefix` 或新增配置段。

对运维：

- 密钥继续只在服务器 env 或密钥文件维护。
- 文档不记录 key 明文。
- 发布前确认 env 配置段和 EdgeOne/CDN 鉴权规则一致。
- 若出现图片异常，可临时回滚后端代码或关闭对应 env 配置段。

## 验证记录

本地验证：

```text
docker run --rm -v "$敏感凭据：[已脱敏] -w /app php:7.4-fpm php -l app/Services/Common/CommonService.php
结果：No syntax errors detected
```

Git 检查：

```text
git diff --check
结果：通过
```

提交状态：

```text
本地 dev 与 origin/dev 已一致
origin/dev commit：cbd772ff
```

## 回滚方式

如需回滚本次后端代码：

```bash
cd /Users/ben/Documents/ben/docker/dev/docker-youdianse-php/src/youdianse-php
git revert cbd772ff
git push origin dev
```

如需临时停用某个图片域名签名：

```ini
# 删除或注释对应配置段，或清空 key
[cdn.tencent.test-img.xxx]
key=
```

停用后对应域名不会再由后端追加 `token/t`，但 CDN/Nginx 侧规则仍需同步确认，避免前后端策略不一致。

## 飞机群通知记录

已通知群：

```text
稳定备案域名+腾讯云原厂
```

通知内容包含：

- 修改文件和 commit。
- 多域名 env 配置方式。
- AWS 老链路不受影响说明。
- 本地验证结果。
- 正常 push 到远端 dev，未强推。
