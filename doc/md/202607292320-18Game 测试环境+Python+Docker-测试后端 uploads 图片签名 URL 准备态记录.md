---
id: "doc-b4b3a34c6986"
title: "测试后端 uploads 图片签名 URL 准备态记录"
date: "2026-07-29T23:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Docker", "Nginx", "自动化", "CDN", "安全运维", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2320-%E3%80%90%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%2B%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E6%B5%8B%E8%AF%95%E5%90%8E%E7%AB%AFuploads%E5%9B%BE%E7%89%87%E7%AD%BE%E5%90%8DURL%E5%87%86%E5%A4%87%E6%80%81%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2320-【安全优化+架构改造】测试后端uploads图片签名URL准备态记录.md"
sourceSha256: "c7896ccb2b2e77b29e216333c43acb961198ef81223564c66eff8b44eefecf3e"
sourceSystem: "project-doc"
---

# 测试后端 uploads 图片签名 URL 准备态记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607292320-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BDocker-%E6%B5%8B%E8%AF%95%E5%90%8E%E7%AB%AF%20uploads%20%E5%9B%BE%E7%89%87%E7%AD%BE%E5%90%8D%20URL%20%E5%87%86%E5%A4%87%E6%80%81%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 23:20｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 23:20
分类：安全优化 / 架构改造 / 测试环境
范围：测试后端、`test-img.hbabaxb.cn`、H5/PC uploads 图片展示链路

## 1. 本次目标

减少测试环境后台上传图片被外部直接复制、公开数据采集和盗刷的风险。

约束：

- 不改后台上传逻辑。
- 不改 AWS S3 / CloudFront 原始图片链路。
- 不改前端打包静态资源。
- 不影响线上 AWS S3 当前访问方式。
- 域名、密钥和开关都从 env 配置读取，代码不写死业务域名和密钥。

## 2. 当前状态

当前处于“准备态”，还没有强制拦截裸链。

已完成：

- 后端 `CommonService::getCdnUrl()` 增加签名出口。
- 只对配置命中的 `https://test-img.hbabaxb.cn/uploads/*` 加 `token/t`。
- 其他绝对 URL 原样返回，包括老 AWS CloudFront URL。
- 测试后端 env 已增加 `cdn.test_img_auth` 配置。
- EdgeOne 已创建 `/uploads/*` Token 鉴权规则，但当前保持 `disable`。
- H5/PC 页面当前能返回带 `token/t` 的 `test-img` 图片 URL。

未启用强拦截的原因：

- H5/PC 前端页面里有 uploads 图片 URL 被固化在前端构建或静态 payload 中。
- 直接启用 EdgeOne 鉴权后，旧 payload 里的旧签名会导致图片 403。
- 已验证 30 分钟 TTL 不适合当前链路，因此已调整为 30 天 TTL。

## 3. 后端代码变更

文件：

```text
/var/www/html/youdianse-php/app/Services/Common/CommonService.php
```

变更点：

- `getCdnUrl()` 返回 URL 前统一经过 `signCdnUrlIfNeeded()`。
- `signCdnUrlIfNeeded()` 只处理配置命中的 host 和 path prefix。
- 签名方式按 EdgeOne Method D：

```text
敏感凭据：[已脱敏] + uri_path + timestamp)
t = 当前时间戳
```

说明：

- `Timeout` 由 EdgeOne 规则控制。
- `t` 不是过期时间，是签名时间。
- AWS CloudFront 绝对 URL 不匹配配置 host，会原样返回。

## 4. 后端 env 配置

本地配置文件：

```text
/Users/ben/Documents/ben/docker/dev/docker-youdianse-php/env/.env.dev
```

测试服务器配置文件：

```text
/opt/docker-youdianse-php/env/.env.dev
```

配置段：

```text
[cdn.test_img_auth]
enabled=1
hosts=test-img.hbabaxb.cn
prefixes=/uploads/
ttl=2592000
[敏感内容已脱敏]
time_param=t
key=仅 env 保存，文档不记录明文
key_file=
```

备份：

```text
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth.20260729_223439
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth_key.20260729_230110
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth_ttl.20260729_231320
```

## 5. EdgeOne 规则

站点：

```text
hbabaxb.cn
ZoneId: zone-3t1w9ksp60nn
```

规则：

```text
RuleId: rule-3t4wuw61zx90
RuleName: test-img-uploads-token-auth
Status: disable
```

匹配条件：

```text
${http.request.host} in ['test-img.hbabaxb.cn'] and ${http.request.uri.path} matches '^/uploads/.*'
```

鉴权参数：

```text
AuthType: TypeD
AuthParam: token
TimeParam: t
TimeFormat: dec
Timeout: 2592000
敏感凭据：[已脱敏] env 保持一致，文档不记录明文
```

当前保持 `disable`，避免旧 H5/PC 静态 payload 里的旧签名被拦截。

## 6. 验证记录

页面返回：

```text
https://h5.youdianse-test.xyz/      test-img URLs: 97，均带 token/t
https://pc.youdianse-test.xyz/      test-img URLs: 86，均带 token/t
https://test-pc.hbabaxb.cn/         test-img URLs: 86，均带 token/t
```

图片链路：

```text
test-img.hbabaxb.cn 裸图：当前规则 disable，抽样 200 image/webp
AWS CloudFront 老图：200 image/webp
测试源站 Nginx 直连：200 image/webp
```

EdgeOne 规则：

```text
rule-3t4wuw61zx90 disable TypeD Timeout=2592000 token/t
```

已验证的失败场景：

- 直接启用规则时，裸链可变 403。
- 但旧页面 payload 的旧签名也会 403。
- 旧 key 长度超过 EdgeOne SecretKey 限制，不能直接复用旧签名。

## 7. 后续启用步骤

要真正开启“裸链 403、签名链 200”，需要按顺序做：

1. 确认 H5/PC 前端发布窗口。
2. 重新发布 `测试环境-游点涩-h5-发版`。
3. 重新发布 `测试环境-游点涩-pc-发版`。
4. 验证新页面 payload 里的 `test-img` URL token 与当前 env key 匹配。
5. 启用 EdgeOne 规则 `rule-3t4wuw61zx90`。
6. 验证：
   - 裸链 `https://test-img.hbabaxb.cn/uploads/...` 返回 403。
   - 页面里的签名链返回 200 image/webp。
   - AWS CloudFront 老链路仍返回 200。

## 8. 回滚方式

快速回滚：

```text
将 EdgeOne rule-3t4wuw61zx90 改回 disable
```

后端回滚：

```text
恢复 CommonService.php 备份：
/var/www/html/youdianse-php/runtime/logs/CommonService.php.bak.test_img_auth.20260729_222605

恢复 env 备份：
/opt/docker-youdianse-php/env/.env.dev.bak.test_img_auth.20260729_223439

重启测试后端容器：
youdianse-dev-php-web
```

回滚后：

- 后端不再追加 `token/t`。
- `test-img.hbabaxb.cn` 继续作为普通反代域名。
- AWS CloudFront 老链路不受影响。

## 9. 给开发和运维看的大白话

这次代码只在“返回图片地址”这个出口加了一个小签名函数。

命中条件非常窄：

```text
只有 https://test-img.hbabaxb.cn/uploads/* 会加签
```

不会处理：

```text
AWS CloudFront 老图片 URL
前端 _nuxt/js/css
前端静态图片
APK/App 包
后台上传动作
线上环境
```

当前还没有真正把裸链拦住，因为前端旧构建里有旧签名。等 H5/PC 重新发布后，再启用 EdgeOne 规则才是完整闭环。
