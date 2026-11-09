---
id: "doc-05555a4a37e6"
title: "测试环境上传 GIF 无法显示诊断记录"
date: "2026-08-17T18:31:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "Redis", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-17-1831-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E4%B8%8A%E4%BC%A0GIF%E6%97%A0%E6%B3%95%E6%98%BE%E7%A4%BA%E8%AF%8A%E6%96%AD%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-08-17-1831-【修复Bug】测试环境上传GIF无法显示诊断记录.md"
sourceSha256: "cc9d80a058086e5bac012488200aeea1117ef924fa78bc79b1d0cf7d6a2b4714"
sourceSystem: "project-doc"
---

# 测试环境上传 GIF 无法显示诊断记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608171831-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%E4%B8%8A%E4%BC%A0%20GIF%20%E6%97%A0%E6%B3%95%E6%98%BE%E7%A4%BA%E8%AF%8A%E6%96%AD%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-17 18:31｜日期依据：文件名日期

环境标签：测试环境

时间：2026-08-17 18:31

## 背景

前端反馈测试后台上传 GIF 后无法正常显示，资源 URL：

```text
https://d1rct3ku9n07y3.cloudfront.net/uploads/2026-08-15/d587e2791ea0e396cbece7e552ee3fcc.gif
```

## 排查过程与证据

### 1. URL 直达探测

```text
d1rct3ku9n07y3.cloudfront.net/...gif       -> HTTP 404（nginx 自定义 404 页，经 CloudFront）
admin.youdianse-test.xyz/uploads/...gif    -> HTTP 404
```

### 2. S3 对象核验（使用 env/.env.dev [aws] 凭据签名请求，未输出密钥）

```text
桶：18game-storage-dev-176528004422
对象：uploads/2026-08-15/d587e2791ea0e396cbece7e552ee3fcc.gif
HEAD 结果：HTTP 200，Content-Type: image/gif，Content-Length: 1,393,352
结论：上传本身成功，对象在 S3 上存在且为有效 GIF。
```

### 3. 域名链路对照

```text
应用配置 AWS_DOMAIN = https://d391me9s8n5j5s.cloudfront.net（正确上传展示域名）
群内 URL d1rct3ku9n07y3.cloudfront.net = 旧兜底域名（nginx 源，仅覆盖历史文件）

d391me9s8n5j5s/新 GIF    -> HTTP 403 AccessDenied（S3 源 XML 报错）
d391me9s8n5j5s/旧 png(2026-01-20) -> HTTP 200 image/png（旧对象正常）
d1rct3ku9n07y3/旧 png   -> HTTP 200 image/webp（旧对象正常，可访问）
d1rct3ku9n07y3/新 GIF   -> HTTP 404（新文件不在该旧源）
S3 直连无鉴权（新旧对象） -> HTTP 403（桶不公开，走 CloudFront OAI）
```

### 4. 上传代码与日志

```text
app/Controller/ApiV1/UploadController.php uploadAction：
  S3Client putObject(Bucket / Key / Body / ContentType)，未设置 ACL / 所有权参数。
应用日志 2026-08-15 19:10:02：上传成功，thumb_skip_gif（GIF 不生成缩略图，属正常逻辑）。
```

## 结论（两处叠加问题）

```text
1. 展示域名用错：页面/前端使用了旧兜底域名 d1rct3ku9n07y3，新上传文件不在该源，
   因此必然 404；正确域名应是应用配置的 d391me9s8n5j5s（或 test-img.* token/t 链路）。
2. 新上传对象权限问题：即使换成正确域名 d391，新 GIF 也返回 403 AccessDenied，
   而旧对象 200 正常 → 新上传对象对 CloudFront OAI 不可读
   （对象所有权 / ACL / 桶策略与上传身份不匹配，属“近期新对象”普遍问题）。
```

## 建议修复（待用户/运维确认后执行）

```text
1. 前端/后台 uploads 展示统一使用应用返回的域名（AWS_DOMAIN=d391… 或 test-img.* 带 token/t），
   废弃 d1rct 旧域名引用。
2. AWS 控制台核对桶 18game-storage-dev-176528004422：
   - Object Ownership 设置；
   - CloudFront OAI 桶策略是否允许 s3:GetObject（应覆盖所有对象）；
   视情况二选一：
   a) 上传代码 putObject 增加 'ACL' => 'public-read' 或给桶所有者授权；
   b) 修正上传 IAM 与桶所有者关系 / 桶策略，使新对象可被 OAI 读取。
3. 改后重新上传并验证 d391 / test-img 域名返回 200；必要时清 CloudFront 缓存。
4. 本次仅诊断，未改代码；修复实施需用户确认。
```

## 定论与修复尝试（2026-08-17 18:40 更新）

```text
1. 该 GIF 上传成功且对象完好（S3 签名 GET 200，1,393,352 字节）。
2. 正确展示域名 d391me9s8n5j5s.cloudfront.net 的 S3 源站当前对所有请求返回 403 AccessDenied：
   - 新对象 403、不存在的 key 也 403、随机 query 复测仍 403 → 不是缓存、不是单个对象权限；
   - 旧对象 200 是 CloudFront 缓存命中（x-cache: Hit from cloudfront），缓存过期后同样会断。
3. 已尝试修复：
   - 对象自复制并设 bucket-owner-full-control → 成功（数据不变），d391 仍 403；
   - 新建带 bucket-owner-full-control 的对象 → d391 仍 403；
   - 桶不允许 ACL（public-read 返回 AccessControlListNotSupported）。
4. 定论：S3 桶 18game-storage-dev-176528004422 与 CloudFront d391 的源站读取授权整体失效
   （OAI/OAC 缺失或桶策略未授权），影响所有新上传资源（GIF/图片/文件），不只本次 GIF。
5. 当前应用 [aws] 凭据无 GetBucketPolicy / PutBucketPolicy / CloudFront 管理权限，无法自行修复。
```

## 修复步骤（需 AWS 控制台/管理权限，运维执行）

```text
1. 确认 d391me9s8n5j5s.cloudfront.net 的 Origin 指向桶 18game-storage-dev-176528004422。
2. 为该 Distribution 配置 Origin Access（OAC/OAI），并在桶策略中允许该主体 s3:GetObject：
   示例（Principal 的 ARN 需按实际 OAI/OAC 替换）：
   {
     "Effect": "Allow",
     "Principal": { "AWS": "<OAI/OAC principal ARN>" },
     "Action": "s3:GetObject",
     "Resource": "arn:aws:s3:::18game-storage-dev-176528004422/uploads/*"
   }
3. 改完验证（随机 query 防缓存）：
   curl -I "https://d391me9s8n5j5s.cloudfront.net/uploads/2026-08-15/d587e2791ea0e396cbece7e552ee3fcc.gif?cb=1"
   期望 HTTP 200、Content-Type image/gif。
4. 前端展示域名统一用 d391… 或 test-img.*（token/t）链路；d1rct… 为旧兜底域名，
   新文件不在其上，不要用于新资源展示。
5. 历史缓存对象在策略修复后会重新回源恢复；必要时对 /uploads/* 执行 CloudFront 缓存失效。
```

## 实际修复（2026-08-17 19:30 完成，无需改 AWS 桶策略）

```text
进一步定位：桶策略其实已授权 CloudFront 分发 E23LIE7DZK2TPM（OAC），
该分发对应域名 = https://dd3tn75akeg7c.cloudfront.net（env [cdn.aws.18game] backend_cdn_domain），
实测新 GIF 在该域名直接 HTTP 200（回源 Miss）。

根因（最终）：
  应用展示/生成 uploads URL 用的域名配置错误：
  DB config 集合 cdn_image 的 free/aws 指向旧域名 https://d1rct3ku9n07y3.cloudfront.net
  （历史 nginx 源，新文件不在其上 → 404）；
  media_url 已是正确域名 dd3tn75akeg7c。

处理（2026-08-17）：
  1. 备份后更新 DB config 集合 cdn_image：
     free=>https://dd3tn75akeg7c.cloudfront.net
     aws=>https://dd3tn75akeg7c.cloudfront.net
     tencent / telnet 保持不变；
     media_url 保持 https://dd3tn75akeg7c.cloudfront.net。
  2. 尝试清理 Redis system_config 配置缓存（未命中 key，缓存 300s 自动刷新）。
  3. 验证：
     https://dd3tn75akeg7c.cloudfront.net/uploads/2026-08-15/d587e2791ea0e396cbece7e552ee3fcc.gif
     -> HTTP 200，Content-Type binary/octet-stream，Content-Length 1,393,352。
  4. 未修改 AWS 桶策略；S3 直连仍 403（保持仅授权分发可读的安全姿态）。

遗留观察项：
  1. MediaTask（MediaLSJService::getCdnDomain）可能周期性把 cdn_image free/aws 改回媒体平台返回值；
     若媒体平台测试项目仍返回 d1rct，需要改媒体平台配置或在代码层做域名修正（建议后续加代码兜底）。
  2. test-img.*（token/t）链路当前代理上游仍是 d1rct，新文件会回退固定图；
     如需该链路也支持新文件，需把 162.211.181.13 的 test-img 上游改为 dd3tn75akeg7c。
  3. 前端页面若仍展示 d1rct 绝对 URL（历史库记录），需刷新为 dd3tn75akeg7c。
```

## 安全说明

```text
排查全程未输出 AWS 密钥、Telegram token/chat_id、Git 凭据。
```
