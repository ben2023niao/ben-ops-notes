---
id: "doc-545367615bac"
title: "【运维记录】线上环境 AWS 账号与 CDN 限流排查记录"
date: "2026-08-20T04:18:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0418-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83AWS%E8%B4%A6%E5%8F%B7%E4%B8%8ECDN%E9%99%90%E6%B5%81%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0418-【运维记录】线上环境AWS账号与CDN限流排查记录.md"
sourceSha256: "5ee8854134d082215730347645d928c19fba92b4c0ba62b0d339799c544e1914"
sourceSystem: "project-doc"
---

# 【运维记录】线上环境 AWS 账号与 CDN 限流排查记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608200418-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BNginx-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%20AWS%20%E8%B4%A6%E5%8F%B7%E4%B8%8E%20CDN%20%E9%99%90%E6%B5%81%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-20 04:18｜日期依据：文件名日期

文档日期：2026-08-20 04:18
环境：游点涩线上环境（main 分支）
分类：运维记录
标签：线上环境、AWS、CloudFront、CDN、限流、账号权限

## 背景

用户要求登录 AWS 查询是否为 CDN 限流或 AWS 限制，涉及 2 个 AWS 账号。

## 查询结果

### 账号 1（176528004422 / IAM：s3-game-prod）

```text
凭据来源：env/.env.prod（AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY）
权限范围：仅为 S3 上传/删除（用于日志 S3 保留）
实测：
  STS get-caller-identity        成功
  S3 ListBuckets / HeadBucket    AccessDenied
  S3 GetBucketPolicy/Website      AccessDenied
  CloudFront ListDistributions   AccessDenied
  CloudWatch ListMetrics         无权限
  EC2 DescribeRegions            无权限
  ELBv2 DescribeLoadBalancers    AccessDenied
结论：账号 1 无法查询 CDN 指标、配额或 WAF 限流。
```

### 账号 2（CDN/CloudFront）

```text
后端 / 网关 / 宝塔 / 前端均未找到第二套 AWS 凭据。
CloudFront 分配 dznzlumehrpl5 不在账号 1 可见范围，归属账号 2。
需要账号 2 只读访问密钥（cloudfront + cloudwatch ReadOnly）才能继续查询。
```

### CDN 侧间接验证（无需 AWS API）

```text
https://h5.18h.game/ 与 /api：
  HTTP/2 200；x-cache: Miss from cloudfront；x-amz-cf-pop: MNL51-P1；
  无 x-amz-cf-error / 502 / 503 —— CloudFront 边缘无错误、无限流迹象。
此前故障已定位为网关 nginx worker_connections 打满（已修复），并非 CDN 限流。
```

## 结论与后续

```text
1. 无证据表明 CDN 限流或 AWS 限制导致登录故障；故障根因为网关 nginx 连接打满（已修复）。
2. 若要深入核对 CloudFront 5xxErrorRate / 配额 / WAF 规则，需账号 2 只读密钥。
3. 建议：为账号 2 创建只读 IAM 用户（CloudFrontReadOnlyAccess + CloudWatchReadOnlyAccess），
   由运维保管，后续可直接做 CDN 健康与限流巡检。
```

## 通知记录

```text
步骤 1 AWS 账号与 CDN 限流查询结果   message_id 9989
```

## 安全与敏感内容

本记录不输出 AWS access key、Telegram token/chat_id、私钥、Git 凭据。
