---
id: "doc-aa7d98798f29"
title: "备案域名前端静态资源 COS 绑定域名直连关系"
date: "2026-08-04T17:02:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "DNS", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1702-%E3%80%90%E8%BF%90%E7%BB%B4%E8%A7%84%E5%88%92%2B%E9%93%BE%E8%B7%AF%E6%94%B9%E9%80%A0%E3%80%91%E5%A4%87%E6%A1%88%E5%9F%9F%E5%90%8D%E5%89%8D%E7%AB%AF%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90COS%E7%BB%91%E5%AE%9A%E5%9F%9F%E5%90%8D%E7%9B%B4%E8%BF%9E%E5%85%B3%E7%B3%BB.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1702-【运维规划+链路改造】备案域名前端静态资源COS绑定域名直连关系.md"
sourceSha256: "d701c2e4c04c94a11c1c53c85c3379b697bc4108b29a1af449e020c2dc306df5"
sourceSystem: "project-doc"
---

# 备案域名前端静态资源 COS 绑定域名直连关系

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-04_1702-【运维规划+链路改造】备案域名前端静态资源COS绑定域名直连关系.md`

> 整理日期：2026-08-04 17:02｜日期依据：文件名日期

环境标签：测试环境 / 线上前置 / 线上环境 / 游点涩 / 前端静态资源 / 腾讯 COS / 备案域名 / 不走腾讯 CDN

## 1. 本次核心改造

本次改造目标是把前端 H5/PC 打包发布资源从“腾讯 CDN/EdgeOne 加速域名 + 缓存刷新”口径调整为：

```text
前端构建产物 -> 各自独立腾讯 COS/S3 桶 -> COS 绑定自定义备案域名访问
```

关键要求：

- `test-h5-s3.备案域名`、`test-pc-s3.备案域名`、`main-h5-s3.备案域名`、`main-pc-s3.备案域名` 必须分别对应独立前端静态资源桶。
- 前端静态资源域名必须绑定到腾讯 COS/S3，不能混用后端 uploads 桶。
- 前端静态资源域名不走腾讯 CDN/EdgeOne，避免缓存导致旧 JS/CSS/图片残留。
- 后端上传资源继续走独立 `test-img/main-img.备案域名`，该链路可以按腾讯云 CDN 反代 AWS S3 或既有 uploads 源站处理。
- `43.241.16.84` 因 80 不通，不再作为本轮线上前置入口首选；后续等待用户提供日本服务器替换。

## 2. 已完成脚本改造

已把 ben-bot 相关发版入口默认腾讯 CDN/EdgeOne 刷新关闭：

| 发布入口 | 改造结果 |
| --- | --- |
| `测试环境-游点涩-h5-发版` | `YOUDIANSE_H5_TEST_TENCENT_CDN_PURGE_ENABLED=0` |
| `测试环境-游点涩-pc-发版` | `YOUDIANSE_PC_TEST_TENCENT_CDN_PURGE_ENABLED=0` |
| `线上前置-游点涩-h5-发版` | `YOUDIANSE_H5_TEST_TENCENT_CDN_PURGE_ENABLED=0` |
| `线上前置-游点涩-pc-发版` | `YOUDIANSE_PC_TEST_TENCENT_CDN_PURGE_ENABLED=0` |

验证结果：

- 本地 `py_compile` 通过。
- ben-bot 容器内 `py_compile` 通过。
- ben-bot 容器内测试 H5/PC `list_json` 正常。
- 本次未触发前端发布，未修改真实 DNS/COS 域名绑定。

说明：脚本中的部分变量名仍保留 `STATIC_CDN_URL`、`BEN_BOT_TENCENT_CDN_URL` 等历史命名，但新口径下这些值表示“前端静态资源访问域名”，不是腾讯 CDN 缓存链路。

## 3. 测试环境关系

### 3.1 页面入口

| 类型 | 域名 | 目标 |
| --- | --- | --- |
| H5 页面 | `test-h5.备案域名` | 测试 H5 页面入口，当前示例 `test-h5.hbabaxb.cn` |
| PC 页面 | `test-pc.备案域名` | 测试 PC 页面入口，当前示例 `test-pc.hbabaxb.cn` |

### 3.2 前端静态资源

| 类型 | 域名 | 腾讯 COS/S3 桶 | 新规则 |
| --- | --- | --- | --- |
| H5 前端构建资源 | `test-h5-s3.备案域名` | `18game-nuxt-static-test-h5-sg-1450169938` | 绑定 COS 自定义域名访问，不走腾讯 CDN |
| PC 前端构建资源 | `test-pc-s3.备案域名` | `18game-nuxt-static-test-pc-sg-1450169938` | 绑定 COS 自定义域名访问，不走腾讯 CDN |

范围：

- `_nuxt/`
- 前端内置 `images/`
- 前端内置 `video/videos/media`
- PWA 资源、`favicon.ico`、`192.png`、`512.png`
- `version.txt`、`version.json`

### 3.3 后端上传资源

| 类型 | 域名 | 目标 |
| --- | --- | --- |
| 后端 uploads 图片/视频 | `test-img.备案域名` | 腾讯云 CDN 反代后端 AWS S3 或既有 uploads 源链路 |

说明：

- 后端 uploads 不进入 `test-h5-s3/test-pc-s3`。
- 前端构建资源不进入 `test-img`。

## 4. 线上/线上前置关系

### 4.1 页面入口

| 类型 | 域名 | 目标 |
| --- | --- | --- |
| H5 页面 | `main-h5.备案域名` | 后续日本服务器提供后部署 H5 页面容器 |
| PC 页面 | `test-pc.备案域名` | 用户当前规划名称；与测试 PC 入口重名，切换前必须确认影响 |

备注：

- 之前准备的 `43.241.16.84` 因公网 80 不通，后续由日本服务器替换。
- 如果继续使用 `test-pc.备案域名` 作为线上 PC 页面入口，需要明确它不再作为测试 PC 页面入口，或改用独立 `main-pc.备案域名` 避免混淆。

### 4.2 前端静态资源

| 类型 | 域名 | 腾讯 COS/S3 桶建议 | 新规则 |
| --- | --- | --- | --- |
| H5 前端构建资源 | `main-h5-s3.备案域名` | `18game-nuxt-static-preprod-h5-sg-1450169938` 或正式线上独立 H5 桶 | 绑定 COS 自定义域名访问，不走腾讯 CDN |
| PC 前端构建资源 | `main-pc-s3.备案域名` | `18game-nuxt-static-preprod-pc-sg-1450169938` 或正式线上独立 PC 桶 | 绑定 COS 自定义域名访问，不走腾讯 CDN |

注意：

- `main-h5-s3` 与 `main-pc-s3` 必须是两个独立前端静态资源桶或至少两个明确隔离的前缀策略。
- 不要与 `main-img` 后端上传资源混用。
- 不要与现有 `main-s3` 后端业务资源链路混用。

### 4.3 后端上传资源

| 类型 | 域名 | 目标 |
| --- | --- | --- |
| 后端 uploads 图片/视频 | `main-img.备案域名` | 腾讯云 CDN 反代线上 AWS S3 或既有线上 uploads 源链路 |

说明：

- `main-img` 是后端上传资源链路。
- `main-h5-s3/main-pc-s3` 是前端构建资源链路。
- 两者缓存策略、鉴权策略、回源策略要分开。

## 5. DNS/COS 落地要求

每个前端静态资源域名都需要完成：

1. 创建或确认独立腾讯 COS/S3 桶。
2. 在腾讯 COS 桶上绑定对应自定义备案域名。
3. 按 COS 控制台给出的目标配置 DNS CNAME。
4. 配置 HTTPS 证书。
5. 验证域名直接访问对象返回最新资源。
6. 验证不经过腾讯 CDN/EdgeOne 缓存层。

建议验证样例：

```text
https://test-h5-s3.备案域名/version.txt
https://test-pc-s3.备案域名/version.txt
https://main-h5-s3.备案域名/version.txt
https://main-pc-s3.备案域名/version.txt
```

## 6. 后续待办

1. 等待用户提供日本服务器信息，用于替换 `43.241.16.84` 作为线上前置页面入口服务器。
2. 按新规则确认或创建 `main-h5-s3/main-pc-s3` 对应腾讯 COS/S3 桶。
3. 把 `test-h5-s3/test-pc-s3` 从 EdgeOne/CDN 访问口径切到 COS 绑定自定义域名直连口径，切换前需验证 DNS、证书、CORS、对象访问。
4. 按同样方式落地 `main-h5-s3/main-pc-s3`。
5. 完成后再执行 H5/PC 发版验证页面资源是否即时更新，无 CDN 缓存残留。

## 7. 本次通知

已按步骤通知：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容只包含操作总结、结果和阻塞点，不包含密码、token、Secret Key、私钥、Cookie 或完整 Signed URL。
