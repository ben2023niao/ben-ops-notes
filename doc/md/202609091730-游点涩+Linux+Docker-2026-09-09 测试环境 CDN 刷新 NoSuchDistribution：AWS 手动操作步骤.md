---
id: "doc-b98af6c52bc8"
title: "2026-09-09 测试环境 CDN 刷新 NoSuchDistribution：AWS 手动操作步骤"
date: "2026-09-09T17:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Docker", "自动化", "CDN", "安全运维", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1730-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83CDN%E5%88%B7%E6%96%B0NoSuchDistribution-AWS%E6%89%8B%E5%8A%A8%E6%93%8D%E4%BD%9C%E6%AD%A5%E9%AA%A4.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1730-【运维记录】测试环境CDN刷新NoSuchDistribution-AWS手动操作步骤.md"
sourceSha256: "feeda4fdec82885494fe1bba41be75ba7a14995508a90e2dca964af5b4120ffb"
sourceSystem: "project-doc"
---

# 2026-09-09 测试环境 CDN 刷新 NoSuchDistribution：AWS 手动操作步骤

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1730-【运维记录】测试环境CDN刷新NoSuchDistribution-AWS手动操作步骤.md`

> 整理日期：2026-09-09 17:30｜日期依据：文件名日期

环境标签：测试环境（dev 分支）

文档日期：2026-09-09

分类：运维记录 / AWS 手动操作

## 1. 先读懂两个账号

```text
账号 A：176528004422
  - S3 桶：18game-storage-dev-176528004422
  - IAM 用户：18game-dev（当前 env [aws] 使用的上传/读桶凭据）

账号 B：916965751623
  - CloudFront 分发所在账号
  - 桶策略允许其读取：E23LIE7DZK2TPM、E2IR59D7WYLSCN

当前报错原因：
后端用账号 A 的 18game-dev 去给账号 B 的分发建失效，所以 E23 返回 404，
账号 A 内又找不到/无权操作该分发。
```

## 2. 最快的“手动验证/手动清缓存”（不解决自动刷新，但可先确认目标）

登录 AWS 账号 B（916965751623）控制台：

```text
https://console.aws.amazon.com/cloudfront
```

在 Distributions 中：

```text
1. 搜索/确认 E23LIE7DZK2TPM 或域名 dd3tn75akeg7c.cloudfront.net
2. 打开该 Distribution
3. 选择 Invalidation 页签
4. Create invalidation
5. 对象路径填：/domain/*
6. Create invalidation
```

预期：

```text
页面出现 Invalidation，状态 InProgress -> Completed；
后台重新打开预览/推送时文件即可回源新内容。
```

> 如果账号 B 里找不到 E23，则说明桶策略中的 E23 也不是当前测试分发的正确 ID，
> 需由 AWS 管理员给出真正承载 dd3tn75akeg7c 的分发 ID。

## 3. 让后端代码具备自动失效能力（推荐方案 A）

后端自动刷新应使用 CloudFront 所属账号 B 的权限，而不是账号 A 的 S3 凭据。

### 3.1 在账号 B 建专用 IAM 用户

```text
AWS 账号 B（916965751623）→ IAM → Users → Create user
用户：youdianse-test-cf-invalidate
访问类型：Programmatic access（Access key），不开控制台
```

给该用户附加内联策略：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations",
        "cloudfront:GetDistribution"
      ],
      "Resource": [
        "arn:aws:cloudfront::916965751623:distribution/E23LIE7DZK2TPM",
        "arn:aws:cloudfront::916965751623:distribution/E2IR59D7WYLSCN"
      ]
    }
  ]
}
```

创建 Access Key 后安全保存，只给后端配置使用。

### 3.2 后端配置与代码改造

```text
env/.env.dev [aws] 现有 key 保留给 S3 上传；
新增/提供 CloudFront key 字段，例如：

[敏感内容已脱敏] Key ID>
[敏感内容已脱敏]

DomainPublishService 创建 CloudFrontClient 时改用 AWS_CDN_* 凭据；
其余 S3 逻辑仍用 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY。
```

改造后重新发布业务代码，再由后端重试推送；预期 `cdn_status=1`。

## 4. 推荐方案 A 的另一种做法：跨账号角色（不开新 Access Key）

账号 B（916965751623）IAM：

```text
Role：youdianse-test-cf-invalidator
信任策略（允许账号 A 的 18game-dev 切换）：
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::176528004422:user/18game-dev"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

角色权限：同 3.1 的 cloudfront:CreateInvalidation 策略。
```

账号 A（176528004422）IAM：

```text
给 18game-dev 附加内联策略：
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::916965751623:role/youdianse-test-cf-invalidator"
}
```

后端代码先 `sts:AssumeRole` 获取临时凭据，再创建 CloudFront 失效请求。

## 5. 方案 B：如果坚持分发应属于账号 A（176528004422）

```text
1. 登录 AWS 账号 A（176528004422）CloudFront 控制台
2. 查看是否有 Distribution 域名 = dd3tn75akeg7c.cloudfront.net / d391me9s8n5j5s.cloudfront.net
3. 若有：记下正确 DistributionId；给 18game-dev 增加
   cloudfront:CreateInvalidation 策略（Resource 指向该 Distribution ARN）
4. 更新 env/.env.dev AWS_DISTRIBUTION_ID 为该 ID 并重新发布
5. 若无：说明测试 CDN 不在账号 A，不要猜测/自建重复分发，回到方案 A
```

## 6. 验证清单

```text
手动清缓存：账号 B 控制台 E23 分发 Invalidation /domain/* 成功
自动刷新：后端重试后返回 cdn_status=1、无 cdn_error
日志：DomainPublishLog 中 cdn_invalidation_status=1，cdn_invalidation_id 非空
安全：Access Key 只进运行时 secrets/env，不进 Git/文档/群通知
```

## 7. 安全与后续

```text
账号 ID 与 Distribution ID 属于资源标识，但不要在公网/无关群展开；
AWS Secret、Telegram token、chat_id、SSH/发布密码、私钥一律不写入文档/Git/群。
```
