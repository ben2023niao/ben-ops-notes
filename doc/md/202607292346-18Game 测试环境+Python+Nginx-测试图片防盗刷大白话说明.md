---
id: "doc-14ef0c6241d8"
title: "测试图片防盗刷大白话说明"
date: "2026-07-29T23:46:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Python", "Nginx", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2346-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%98%B2%E7%9B%97%E5%88%B7%E5%A4%A7%E7%99%BD%E8%AF%9D%E8%AF%B4%E6%98%8E.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2346-【运维记录】测试图片防盗刷大白话说明.md"
sourceSha256: "67e979fbb758ccaaab4efef8086a33a112b85d79531d781286bedefc4b5d803c"
sourceSystem: "project-doc"
---

# 测试图片防盗刷大白话说明

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607292346-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BPython%2BNginx-%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87%E9%98%B2%E7%9B%97%E5%88%B7%E5%A4%A7%E7%99%BD%E8%AF%9D%E8%AF%B4%E6%98%8E.md)

> 整理日期：2026-07-29 23:46｜日期依据：文件名日期

环境标签：测试环境

时间：2026-07-29 23:46
分类：运维记录 / 安全优化 / 大白话说明
范围：测试环境 PC、后端 uploads 图片、`test-img.hbabaxb.cn`

## 1. 现在改成什么样了

测试环境 PC：

```text
https://test-pc.hbabaxb.cn
```

现在页面里正常展示的敏感业务图片，已经走下面这个新图片域名：

```text
https://test-img.hbabaxb.cn
```

正常页面里加载图片时，图片地址后面会带：

```text
敏感凭据：[已脱敏]
t=时间
```

简单理解：

```text
带 token 和 t：正常显示原图
不带 token 和 t：不给看原图，只显示默认占位图
token 或 t 过期：不给看原图，只显示默认占位图
```

## 2. 给运营看的说明

如果用户正常打开测试 PC 页面：

```text
https://test-pc.hbabaxb.cn
```

页面里的图片是正常显示的。

如果有人复制一张后台上传图片的原始地址，单独打开：

```text
https://test-img.hbabaxb.cn/uploads/xxx.webp
```

看到的不会是原图，而是一个默认图片。

目的：

```text
别人不能直接复制原始图片地址到外面长期使用
别人爬裸图链接时，只会拿到默认图
正常页面访问不受影响
```

## 3. 给开发看的说明

后端返回图片地址时，会给 `test-img.hbabaxb.cn/uploads/*` 这类图片追加签名参数：

```text
?敏感凭据：[已脱敏]
```

示例：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏]
```

这个地址在有效期内可以正常显示原图。

没有签名的地址：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp
```

不会返回原图，会返回默认占位图。

注意：

- 不改上传逻辑。
- 不改 AWS S3 原始存储。
- 不改前端打包静态资源。
- 不影响线上 AWS 图片链路。
- 只处理测试环境 `test-img.hbabaxb.cn/uploads/*`。

## 4. 给运维看的说明

Nginx 现在不是返回 403，也不是 302 跳转。

现在做法是：

```text
原始 URL 保持不变
Nginx 内部转发到默认占位图
浏览器看到的是原始 URL
实际返回内容是默认图 image/webp
```

实现方式：

```text
error_page 418 = @placeholder_image
@placeholder_image 内部 rewrite 到 /images/mine/footer-app-download-icon.webp
再 proxy 到 test-pc-s3.hbabaxb.cn
```

这样做的好处：

```text
没有 302 跳转
地址栏不会暴露默认图地址
爬虫请求裸图时拿到的是默认图内容
页面正常带 token 的图片仍返回原图
```

## 5. 验证结果

测试 PC 页面：

```text
https://test-pc.hbabaxb.cn
结果：200，页面正常打开
```

带 token 和 t 的后端图片：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏]
结果：200 image/webp，正常显示原图
```

不带 token 的原始图片：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp
结果：200 image/webp，URL 不变，显示默认占位图
```

空 token：

```text
https://test-img.hbabaxb.cn/uploads/2025-11-12/62053cee53eb8c7efdc909b8ad2284f4_large.webp?敏感凭据：[已脱敏] image/webp，URL 不变，显示默认占位图
```

默认占位图：

```text
https://test-pc.hbabaxb.cn/images/mine/footer-app-download-icon.webp
结果：200 image/webp
```

## 6. 一句话总结

```text
正常页面访问：能看原图
复制裸图链接：只能看默认图
链接带 token/t 且没过期：能看原图
token/t 过期或缺失：只能看默认图
```

## 7. 后续注意

- 后续如果测试 H5/PC 重新发版，需要继续确认页面图片是否都带 `token/t`。
- 如果以后要做到“随便填 token 也不能看”，需要再启用 Nginx Lua/md5 强校验。
- 当前方案重点先解决裸图直连和爬虫直接抓原始 URL 的问题。
- 正式环境不要直接照搬，必须单独规划、验证和回滚。

## 8. 关联文档

```text
devops/python/ben-bot/doc/2026-07-29_2320-【安全优化+架构改造】测试后端uploads图片签名URL准备态记录.md
devops/python/ben-bot/doc/2026-07-29_2345-【安全优化+网络调整】测试PC静态图片直开Token门槛记录.md
```
