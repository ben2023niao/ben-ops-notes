---
id: "doc-99fbdcb9adbe"
title: "2026-07-29 vendor_d / PPK / vendor_a 客户端资源包巴西覆盖记录"
date: "2026-07-29T17:54:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Docker", "Nginx", "监控告警", "CDN", "安全运维", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-07-29-1754-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E3%80%91vendor_dPPKvendor_a%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%B5%84%E6%BA%90%E5%8C%85%E5%B7%B4%E8%A5%BF%E8%A6%86%E7%9B%96%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-07-29-1754-【补静态资源】vendor_dPPKvendor_a客户端资源包巴西覆盖记录.md"
sourceSha256: "d7331ef014da51e180fd7b8245d1b60304d4f24e34601432338d6b54a4970eba"
sourceSystem: "project-doc"
---

# 2026-07-29 vendor_d / PPK / vendor_a 客户端资源包巴西覆盖记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607291754-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BDocker-2026-07-29%20vendor_d%20-%20PPK%20-%20vendor_a%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%B5%84%E6%BA%90%E5%8C%85%E5%B7%B4%E8%A5%BF%E8%A6%86%E7%9B%96%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-29 17:54｜日期依据：文件名日期

本文记录开发上传到 AWS S3 `bizops-h5` 的客户端资源包 `vendor_d.tar.gz`、`ppk.tar.gz`、`vendor_a.tar.gz` 覆盖巴西静态资源的全过程：AWS 权限确认、下载、包结构校验、宝塔源目录 overlay、GCS live/backup 同步、Cloud CDN 刷新、公开链路验证和飞机群分步通知。

## 任务边界

需求：

```text
vendor_d.tar.gz
ppk.tar.gz
vendor_a.tar.gz
这几个先覆盖巴西。
香港不用覆盖。
```

本次只操作巴西宝塔：

```text
192.0.2.8
/www/wwwroot/vendor_d-static
/www/wwwroot/ppk-static
/www/wwwroot/vendor_a-statics
/www/wwwroot/vendor_a-statics1
/www/wwwroot/vendor_a-statics2
```

香港机器、香港 S3、香港 CloudFront 均未覆盖。

## AWS 权限与凭据

初始巴西宝塔 AWS 凭据：

```text
文件：/root/bizops-aws-prod.env
身份：arn:aws:iam::176528004422:user/s3-game-prod
结果：对 s3://bizops-h5/vendor_d.tar.gz、ppk.tar.gz、vendor_a.tar.gz 的 HeadObject/GetObject 均为 403 / AccessDenied
```

`bizops-h5` 所在 AWS 账号为 `517506432530`。最终改用该账号下的 `linux-uploader`：

```text
身份：arn:aws:iam::517506432530:user/linux-uploader
用途：开发上传新客户端资源到 s3://bizops-h5 后，巴西宝塔下载客户端补资源包
宝塔临时 env：/root/bizops-h5-download.env
Access Key 标识：AKIAX...BDN4
权限：s3-rw-bizops-h5
验证：STS、ListBucket、HeadObject、range GetObject 均通过
```

安全说明：

```text
明文 AWS_SECRET_ACCESS_KEY 不写入仓库、日志或飞机群。
完整 Access Key / Secret 只保留在宝塔 root-only env。
任务完成后可按安全要求禁用或轮换本次新建 Access Key。
```

该凭据索引已补充到：

```text
docker/线上服务器信息/README.md
docker/线上服务器信息/servers.json
```

## 下载与校验

宝塔工作目录：

```text
/root/bizops-static-import/client-update-20260729-vendor_d-ppk-vendor_a
```

S3 下载结果：

```text
vendor_d.tar.gz  955,880,898 bytes
SHA256 3e3c18c66d29ca067a4d6b9f58f9735f13da5d800b5de25879878cc6980d4c49

ppk.tar.gz  1,858,296,409 bytes
SHA256 b9c5eae37856283cb4416b31fa7456b6af38712a9aed52f26372b892e925abc8

vendor_a.tar.gz  2,253,975,488 bytes
SHA256 a9d49a3d5b8e9712a2edd6a64c3cf9bb23485b580ab9349f3269c18e242f8d1c
```

tar 结构校验：

```text
vendor_d.tar.gz：49,595 entries，危险路径 0，顶层 vendor_d/
ppk.tar.gz：9,369 entries，危险路径 0，顶层 popok/
vendor_a.tar.gz：30,946 entries，危险路径 0，顶层 vendor_astatic/、vendor_astatic1/、vendor_astatic2/
```

目标映射：

```text
vendor_d/       -> /www/wwwroot/vendor_d-static
popok/       -> /www/wwwroot/ppk-static
vendor_astatic/  -> /www/wwwroot/vendor_a-statics
vendor_astatic1/ -> /www/wwwroot/vendor_a-statics1
vendor_astatic2/ -> /www/wwwroot/vendor_a-statics2
```

## 宝塔源目录覆盖

覆盖方式：

```text
rsync -a --checksum --chown=www:www
未使用 --delete
```

dry-run 差异：

```text
vendor_d：新增 568，更新 157，传输 140,737,067 bytes
PPK：新增 1，更新 0，传输 2,839 bytes
vendor_a 主目录：无内容差异
vendor_a1：新增 231，更新 0，传输 60,167,472 bytes
vendor_a2：新增 0，更新 2，传输 192,154 bytes
```

备份：

```text
/root/bizops-static-import/client-update-20260729-vendor_d-ppk-vendor_a/backup-replaced
vendor_d：备份 157 个被覆盖文件
vendor_a2：备份 2 个被覆盖文件
```

合并后二次 dry-run：

```text
vendor_d post_files=0
ppk post_files=0
vendor_a post_files=0
vendor_a1 post_files=0
vendor_a2 post_files=0
```

## GCS 同步

live / backup 目标：

```text
vendor_d live：gs://bizops-gcs-vendor_d-static
vendor_d backup：gs://bizops-game-statics-gcs/vendor_d-static

PPK live：gs://bizops-gcs-ppk-static
PPK backup：gs://bizops-game-statics-gcs/ppk-static

vendor_a live：gs://bizops-gcs-vendor_a-statics
vendor_a backup：gs://bizops-game-statics-gcs/vendor_a-statics

vendor_a1 live：gs://bizops-gcs-vendor_a-statics1
vendor_a1 backup：gs://bizops-game-statics-gcs/vendor_a-statics1

vendor_a2 live：gs://bizops-gcs-vendor_a-statics2
vendor_a2 backup：gs://bizops-game-statics-gcs/vendor_a-statics2
```

同步结果：

```text
vendor_d live：完成全目录 rsync，29.9k objects / 1.2 GiB
vendor_d backup：按变更清单上传 725，失败 0
PPK live/backup：各上传 1，失败 0
vendor_a 主目录 live/backup：无内容差异
vendor_a1 live/backup：各上传 231，失败 0
vendor_a2 live/backup：各上传 2，失败 0
```

说明：vendor_d live 全目录 rsync 完成后，原会话未继续写 summary；后续目标改用 dry-run 变更清单同步，避免再次全目录扫描。未使用删除操作。

## Cloud CDN 刷新

URL map：

```text
bizops-static-gcs-map
project：infra-alc-20260511
```

刷新范围：

```text
vendor_d static hosts：22
PPK static hosts：22
vendor_a1 static hosts：22
vendor_a2 static hosts：22
路径：/*
```

结果：

```text
提交 invalidation：88
提交失败：0
DONE：88/88
```

vendor_a 主目录本次无内容差异，因此未单独刷新 vendor_a 主静态 host。

## 公开链路验证

验证实际变更文件：

```text
vendor_d：sw.js
PPK：popok/res-fun.pokgaming.com/shared/core/translations.zip
vendor_a1：tcb_backup/Intro_ProgressBar.png
vendor_a2：lj500/index.html
```

验证结果：

```text
vendor_d：22/22 hosts HTTP 200，CORS *
PPK：22/22 hosts HTTP 200，CORS *
vendor_a1：22/22 hosts HTTP 200，CORS *
vendor_a2：22/22 hosts HTTP 200，CORS *
合计：88/88 OK
```

验证报告：

```text
/root/bizops-static-import/client-update-20260729-vendor_d-ppk-vendor_a/reports/public-verify.json
```

## 飞机群通知

群：监控报警群

```text
3016：步骤1/权限预检，s3-game-prod 读 bizops-h5 失败
3017：步骤2/bucket policy 保存后复测仍 403
3018：步骤3/全桶 bucket policy 复测仍 403
3019：步骤4/bizops-hk-nginx-ai 补 S3 权限
3020：步骤5/宝塔未找到 bizops-hk-nginx-ai 凭证
3021：步骤6/机器人 AWS 身份确认，仍为 s3-game-prod
3022：步骤7/cn 凭据线索确认，香港 bizops-hk 为 bizops-hk-nginx-ai
3023：步骤8/切换为 linux-uploader 方案
3024：步骤9/未找到 linux-uploader 既有凭证
3025：步骤10/写入 linux-uploader 临时 env 前通知
3026：步骤11/S3 权限复测通过
3028：步骤12/S3 资源包下载完成
3030：步骤13/资源包结构校验通过
3031：步骤14/dry-run 差异预演完成
3032：步骤15/宝塔源目录合并完成
3033：步骤16/GCS 同步进行中
3034：步骤17/GCS 同步策略调整
3042：步骤18/GCS 同步完成
3043：步骤19/准备刷新 Cloud CDN
3047：步骤20/Cloud CDN 刷新完成
3048：步骤21/公开链路验证通过
3049：最终汇总
3050：文档附件
```

## 结论

```text
巴西 vendor_d / PPK / vendor_a1 / vendor_a2 客户端资源已覆盖、同步、刷新并验证通过。
vendor_a 主目录本次包内容与现网无差异。
香港未覆盖。
```
