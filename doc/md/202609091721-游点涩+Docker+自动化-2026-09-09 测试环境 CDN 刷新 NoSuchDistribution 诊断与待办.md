---
id: "doc-035c69842617"
title: "2026-09-09 测试环境 CDN 刷新 NoSuchDistribution 诊断与待办"
date: "2026-09-09T17:21:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "自动化", "CDN", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1721-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83CDN%E5%88%B7%E6%96%B0NoSuchDistribution%E8%AF%8A%E6%96%AD%E4%B8%8E%E5%BE%85%E5%8A%9E.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1721-【修复Bug】测试环境CDN刷新NoSuchDistribution诊断与待办.md"
sourceSha256: "c75fd16dde3b84ac780d5dabd47206d3035b7f2cbc125fd11835989dfcac51b2"
sourceSystem: "project-doc"
---

# 2026-09-09 测试环境 CDN 刷新 NoSuchDistribution 诊断与待办

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-09-09-1721-【修复Bug】测试环境CDN刷新NoSuchDistribution诊断与待办.md`

> 整理日期：2026-09-09 17:21｜日期依据：文件名日期

环境标签：测试环境（dev 分支）

文档日期：2026-09-09

分类：修复 Bug / AWS 配置

## 现象

后端 `DomainPublishService` 在 S3 推送成功后执行 CloudFront 失效：

```text
S3 推送成功，但 CDN 刷新失败
CreateInvalidation distribution/E23LIE7DZK2TPM
404 NoSuchDistribution
```

## 已核验事实

```text
1. env/.env.dev [aws]
   - AWS_BUCKET=18game-storage-dev-176528004422
   - AWS_DOMAIN=https://d391me9s8n5j5s.cloudfront.net
   - AWS_DISTRIBUTION_ID=E23LIE7DZK2TPM

2. 当前 env [aws] 的 IAM 调用者
   - STS GetCallerIdentity = arn:aws:iam::176528004422:user/18game-dev

3. S3 桶策略
   - 桶属 176528004422
   - 允许 cloudfront.amazonaws.com 读取的 SourceArn：
     arn:aws:cloudfront::916965751623:distribution/E23LIE7DZK2TPM
     arn:aws:cloudfront::916965751623:distribution/E2IR59D7WYLSCN

4. 业务文件实际访问
   - /domain/*.png（新推送）只有 dd3tn75akeg7c.cloudfront.net 返回 200
   - d391 / d7j2 / d1rct 均不可访问该文件

5. CloudFront 探测（使用当前 env [aws] 同一组凭据，仅无害路径）
   - E23LIE7DZK2TPM -> 404 NoSuchDistribution
   - E2IR59D7WYLSCN -> 403 AccessDenied
   - ListDistributions / GetDistribution / ListUsers -> 403 AccessDenied
```

## 根因结论

```text
CloudFront 分发（916965751623）与应用 IAM / S3（176528004422）分属不同 AWS 账号。
env [aws] 的 18game-dev 凭据只有 S3 权限，无法对 916965751623 下的
E23/E2IR 分发执行 CreateInvalidation，因此返回 404/403。
仅修改 AWS_DISTRIBUTION_ID 值不能解决；核心是“执行失效的凭据/权限/账号关系”。
```

## 待 AWS 侧确认/处理（二选一）

```text
方案 A（推荐，保持现有跨账号桶授权）
  在 AWS 916965751623 中提供可被后端调用的 CloudFront 账号/角色
  （具备 cloudfront:CreateInvalidation），并把凭据或 AssumeRole 配置
  接入 env/.env.dev [aws] / 后端 DomainPublishService。

方案 B
  如果测试环境实际分发应归 176528004422 管理：
  1. 在 176528004422 创建/确认对应 CloudFront 分发并给出正确 DistributionId；
  2. 给 18game-dev 增加 cloudfront:CreateInvalidation；
  3. 更新 env/.env.dev AWS_DISTRIBUTION_ID 并重新发布。
```

## 回滚 / 安全

```text
本次未修改 env 运行值、未修改桶策略、未删除任何配置；
全程未输出 AWS Secret、Telegram token、chat_id、密码或私钥。
```

## 相关文件

```text
env/.env.dev
app/Services/Common/DomainPublishService.php（live 容器内代码）
workbench/CURRENT_TASK.md
本文档
```
