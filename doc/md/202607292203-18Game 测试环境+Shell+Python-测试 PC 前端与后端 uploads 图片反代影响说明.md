---
id: "doc-9d4984392fac"
title: "测试 PC 前端与后端 uploads 图片反代影响说明"
date: "2026-07-29T22:03:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "自动化", "CDN", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2203-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95PC%E5%89%8D%E7%AB%AF%E4%B8%8E%E5%90%8E%E7%AB%AFuploads%E5%9B%BE%E7%89%87%E5%8F%8D%E4%BB%A3%E5%BD%B1%E5%93%8D%E8%AF%B4%E6%98%8E.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2203-【运维记录】测试PC前端与后端uploads图片反代影响说明.md"
sourceSha256: "ac2e87982f852859f48d6c8d5c19a6260c8da706e3cd35b90e5c6caf9d9cce7c"
sourceSystem: "project-doc"
---

# 测试 PC 前端与后端 uploads 图片反代影响说明

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-29_2203-【运维记录】测试PC前端与后端uploads图片反代影响说明.md`

> 整理日期：2026-07-29 22:03｜日期依据：文件名日期

环境标签：测试环境

## 1. 给运维和开发看的结论

这次不是继续做前端静态资源加密，也不是修改图片上传逻辑。

本次最终方案是：

```text
前端打包资源保持不加密
后端 uploads 图片单独走 test-img.hbabaxb.cn
test-img.hbabaxb.cn 通过腾讯 EdgeOne 反代 AWS CloudFront uploads
在测试源站 Nginx 做基础 Referer 防盗刷
```

## 2. 测试 PC 前端修改了什么

测试 PC 前端资源鉴权已经回退：

- 不再给 PC 前端打包资源追加 `token` 和 `t` 参数。
- 不再对 PC 前端 `_nuxt`、JS、CSS、SVG、WebP、图片做加密访问。
- `test-pc-s3.hbabaxb.cn` 继续只负责 PC 前端构建产物。

PC 前端发布仍保持原来的双推逻辑：

```text
PC 前端构建产物 .output/public
-> AWS 前端公开桶
-> 腾讯新加坡 COS 私有桶
-> 页面优先加载 test-pc-s3.hbabaxb.cn
```

PC 前端页面入口：

```text
AWS/原入口: https://pc.youdianse-test.xyz
备案入口: https://test-pc.hbabaxb.cn
```

PC 前端静态资源域名：

```text
https://test-pc-s3.hbabaxb.cn
```

## 3. 测试 PC 前端新增了什么

新增一个后端图片展示域名：

```text
https://test-img.hbabaxb.cn
```

这个域名不负责 PC 前端打包资源。

它只用于后端 uploads 图片展示，例如：

```text
原来:
https://d1rct3ku9n07y3.cloudfront.net/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png

现在:
https://test-img.hbabaxb.cn/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png
```

## 4. 测试后端修改了什么

只修改了测试后端配置里的图片展示域名：

```text
配置项: Mongo config.code = cdn_image
```

修改内容：

```text
将 cdn_image 中 CloudFront 展示项:
https://d1rct3ku9n07y3.cloudfront.net

替换为:
https://test-img.hbabaxb.cn
```

本次替换数量：

```text
2 处
```

后端配置缓存：

```text
system_config 已清理
```

配置备份：

```text
/var/www/html/youdianse-php/runtime/logs/cdn_image_backup_20260729_215058.txt
```

## 5. 测试后端新增了什么

新增测试源站 Nginx 配置：

```text
本地:
devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/test-img.hbabaxb.cn.conf

服务器:
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
```

访问链路：

```text
浏览器
-> test-img.hbabaxb.cn
-> 腾讯 EdgeOne
-> 测试服务器 Nginx
-> AWS CloudFront d1rct3ku9n07y3.cloudfront.net
-> AWS S3 uploads 图片
```

Nginx 防盗刷规则：

```text
只允许访问 /uploads/*
允许 Referer / 空 Referer:
- none
- *.hbabaxb.cn
- *.youdianse-test.xyz

无 Referer:
- 200

非本站 Referer:
- 403
```

缓存处理：

```text
Cache-Control: private, no-store, max-age=0
Vary: Referer
```

原因：

- 如果 EdgeOne 缓存了允许 Referer 的图片，再被外部无 Referer 命中同一个缓存，会绕过源站校验。
- 所以这条 uploads 反代链路不让 EdgeOne 缓存图片，每次回到 Nginx 判断 Referer。

## 6. 是否影响测试 H5

不会影响测试 H5 的前端静态资源发布链路。

本次没有修改：

- H5 前端打包脚本。
- H5 S3/COS 同步逻辑。
- H5 静态资源域名 `test-h5-s3.hbabaxb.cn`。
- H5 页面入口 `h5.youdianse-test.xyz` / `test-h5.hbabaxb.cn`。

但需要注意：

如果测试 H5 页面也调用同一个测试后端接口，并且接口返回 uploads 图片，那么 H5 拿到的 uploads 图片展示域名也会变成：

```text
https://test-img.hbabaxb.cn
```

这是因为 `cdn_image` 是测试后端的公共图片展示配置。

这属于后端返回图片域名变化，不是 H5 前端发布链路变化。

## 7. 是否影响后台图片上传

不影响后台图片上传。

本次没有修改：

- 图片上传代码。
- AWS S3 上传桶。
- 上传密钥。
- 后台上传入口。
- APK/App 客户端包链路。

后台图片仍然上传到 AWS S3。

这次只改“图片展示时返回哪个域名”，没有改“图片上传到哪里”。

## 8. 验证结果

页面返回：

```text
https://test-pc.hbabaxb.cn/
命中 test-img.hbabaxb.cn: 86 处

https://pc.youdianse-test.xyz/
命中 test-img.hbabaxb.cn: 86 处
```

样例图片：

```text
https://test-img.hbabaxb.cn/uploads/2026-03-02/809f5e380d5eec76d232b5d5a2ca634d.png
```

验证结果：

| 场景 | 结果 |
| --- | --- |
| `Referer: https://test-pc.hbabaxb.cn/` | `200 image/webp` |
| 无 Referer | `200 image/webp` |
| `Referer: https://example.com/` | `403 text/html` |

2026-07-29 22:05 修正：

- `pc.youdianse-test.xyz` 页面当前图片请求策略是 `no-referrer`，正常页面图片请求也不带 Referer。
- 为避免正常 PC 页面图片 403，已允许空 Referer。
- 这能恢复页面图片，但 Referer 防盗刷无法拦截所有空 Referer 直链。
- 后续如果需要更强防盗刷，应改为不依赖 Referer 的方案。

补充观察：

- 测试源站 Nginx 直连验证正常。
- EdgeOne 多数节点允许 Referer 返回 200。
- 个别 EdgeOne A 记录从当前本地网络直连超时，判断为新域名边缘调度或网络可达性差异，需要继续观察。

## 9. 回滚说明

如果发现异常，优先回滚后端 `cdn_image`。

回滚方式：

1. 使用备份文件恢复 `cdn_image` 原值。
2. 删除 `system_config` 缓存。
3. 验证接口重新返回原 CloudFront 域名。

回滚目标：

```text
https://d1rct3ku9n07y3.cloudfront.net
```

注意：

- 不需要回滚前端 H5/PC 发布脚本。
- 不需要修改图片上传逻辑。
- 如果只停用 `test-img.hbabaxb.cn`，但不回滚 `cdn_image`，页面会继续拿到 `test-img` 域名，图片可能不可用。
