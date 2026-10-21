---
id: "doc-8ccbc6683fd0"
title: "【备份】AWS CloudFront d3hmby9nizcg7v.cloudfront.net 配置导出"
date: "2026-10-21T23:28:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Python", "Docker", "CDN", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-2328-%E3%80%90%E5%A4%87%E4%BB%BD%E3%80%91AWS%20CloudFront%20d3hmby9nizcg7v%E9%85%8D%E7%BD%AE%E5%AF%BC%E5%87%BA.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-2328-【备份】AWS CloudFront d3hmby9nizcg7v配置导出.md"
sourceSha256: "82ad83825b2d7d1c1d47d34cc25a15b8bb69c576b7a20d5cef3d4ede9549e5ec"
sourceSystem: "project-doc"
---

# 【备份】AWS CloudFront d3hmby9nizcg7v.cloudfront.net 配置导出

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-21-2328-【备份】AWS CloudFront d3hmby9nizcg7v配置导出.md`

> 整理日期：2026-10-21 23:28｜日期依据：文件名日期

- 导出时间：2026-10-21 23:28（Asia/Manila）
- AWS 账号：`916965751623`
- AWS 区域：`us-east-1`
- CloudFront Distribution ID：`E1VM53PCL7TTU8`
- CloudFront 域名：`d3hmby9nizcg7v.cloudfront.net`
- 状态：`Deployed`
- 启用状态：`Enabled`
- 最近修改：2026-10-21 23:18:42（Asia/Manila）
- 导出身份：IAM 用户 `arn:aws:iam::916965751623:user/cdn-refresh`
- 导出方式：`cloudfront:GetDistribution`
- 凭据策略：不记录、不转发 Access Key / Secret Access Key

## 一、结论

配置已成功导出，`GetDistribution` 返回体中包含完整的
`Distribution.DistributionConfig`，可满足当前配置归档和人工恢复参考。

当前 IAM 用户没有以下附加资源的读取权限：

- `cloudfront:ListTagsForResource` → `AccessDenied`
- `cloudfront:GetCachePolicy` → `AccessDenied`
- `cloudfront:GetKeyGroup` → `AccessDenied`

因此备份包含分发主体及其全部内嵌配置，但不包含标签、受管缓存策略正文和 Key Group 公钥详情；相关资源 ID 已保留在分发配置中。

## 二、配置摘要

| 项目 | 值 |
| --- | --- |
| Comment | `youdianse tcdn origin jtcdn.laosiji1788.com` |
| Origin | `jtcdn.laosiji1788.com` |
| Origin protocol | `https-only` |
| Origin HTTP / HTTPS port | `80` / `443` |
| Origin timeout / attempts | `10s` / `3` |
| Origin Access Control | 未配置 |
| Origin custom headers | 无 |
| Default root object | 空 |
| Alias | 无 |
| Price class | `PriceClass_All` |
| HTTP version | `http2and3` |
| IPv6 | 启用 |
| Viewer protocol | `redirect-to-https` |
| Allowed methods | `GET / HEAD / OPTIONS` |
| Cached methods | `GET / HEAD` |
| Compression | 启用 |
| Cache policy ID | `658327ea-f89d-4fab-a63d-7e88639e58f6` |
| Trusted key group | `acc84a79-9a8d-4e33-909e-b1b215d7fbd2` |
| Origin request policy | 未配置 |
| Response headers policy | 未配置 |
| Lambda@Edge / CloudFront Functions | 未配置 |
| Web ACL | 未配置 |
| Logging | 未启用 |
| Geo restriction | `none` |
| Viewer certificate | CloudFront 默认证书 |
| Minimum TLS | `TLSv1` |

## 三、备份文件

目录：

```text
ops/production/cdn-backups/2026-10-21-d3hmby9nizcg7v-E1VM53PCL7TTU8/
```

文件：

| 文件 | 说明 | SHA-256 |
| --- | --- | --- |
| `get-distribution-response.json` | `GetDistribution` 完整原始响应，包含 `DistributionConfig` | `d2e3523dad89cbcf572aa215ae512d1509f1dc11f11f9298d6cf27174afa1f87` |
| `distribution-config.json` | 单独抽出的 `DistributionConfig` | `48d6b73335bdd4ca150453f954c556e6710ae0097e5c59be22399a270eba4e16` |
| `export-metadata.json` | AWS 账号、Distribution ID、导出时间、权限结果 | `61ab3955fe0fb6a568cce366dcfd91c15fca19e8f14097ed754b99c00bf4f13e` |
| `README.md` | 备份目录说明及权限边界 | `058e09279f5ffe1928f8a3c0ecb133872ca3c6b9d6e3ed2693af8237922da7be` |

压缩包：

```text
/tmp/youdianse-cloudfront-d3hmby9nizcg7v-20261021.tar.gz
SHA-256: af0790a636b5957abedd473d2b7605afea001b63dd66134e4331c3a128b4ec2a
```

## 四、验证

1. `GetDistribution` 成功，目标 Distribution ID、域名、ARN 与预期一致。
2. 所有 JSON 文件均通过 `python3 -m json.tool` 解析。
3. 全目录扫描未发现 AWS Access Key、Secret、私钥、密码或回源认证头。
4. 原始响应与单独配置使用相同分发 ID，域名为 `d3hmby9nizcg7v.cloudfront.net`。
5. 压缩包已通过 `tar -tzf` 完整性检查，包含 4 个文件。

## 五、权限说明

历史记录表明该 IAM 用户 `cdn-refresh` 主要用于 CloudFront 缓存失效，权限范围不包含配置修改，也不包含缓存策略、Key Group 和标签读取。因此本次未尝试任何写操作。

若后续需要完整恢复标签、缓存策略正文或 Key Group 公钥，需要账号
`916965751623` 另行授予最小只读权限：

```text
cloudfront:GetDistribution
cloudfront:ListTagsForResource
cloudfront:GetCachePolicy
cloudfront:GetKeyGroup
```

## 六、通知记录

| 步骤 | 内容 | 线上群 | 18game 群 |
| --- | --- | --- | --- |
| 1 | 失败排查：错误账号/无浏览器会话 | 13707 | 118664 |
| 2 | 历史文档定位 CDN 账号 916965751623 | 13708 | 118665 |
| 3 | 配置导出与本地归档 | 13708 | 118665 |
| 4 | 文档 118666 / 配置包 118667 | 不发送 | 118666、118667 |
| 5 | Git 提交结果 | 待发送 | 待发送 |

## 七、敏感信息声明

本文和备份目录不含 AWS Access Key、Secret Access Key、Telegram token/chat_id、SSH 密码、私钥或 Git 凭据。AWS 账号 ID、Distribution ID、ARN 和资源 ID 属于内部资源标识，仅供授权运维使用。
