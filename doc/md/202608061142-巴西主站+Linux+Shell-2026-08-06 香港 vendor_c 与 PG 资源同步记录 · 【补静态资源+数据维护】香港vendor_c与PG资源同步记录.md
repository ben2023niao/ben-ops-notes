---
id: "doc-0c7a5e3c445c"
title: "2026-08-06 香港 vendor_c 与 PG 资源同步记录 · 【补静态资源+数据维护】香港vendor_c与PG资源同步记录"
date: "2026-08-06T11:42:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "监控告警", "自动化", "CDN"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/live/2026-08-06-1142-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%2B%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E9%A6%99%E6%B8%AFvendor_c%E4%B8%8EPG%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/live/2026-08-06-1142-【补静态资源+数据维护】香港vendor_c与PG资源同步记录.md"
sourceSha256: "f32926a84c3110ca7270c6e46c4e9e3ae0790583d85e46ed397cdb2be4988359"
sourceSystem: "project-doc"
---

# 2026-08-06 香港 vendor_c 与 PG 资源同步记录 · 【补静态资源+数据维护】香港vendor_c与PG资源同步记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061142-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-2026-08-06%20%E9%A6%99%E6%B8%AF%20vendor_c%20%E4%B8%8E%20PG%20%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95%20%C2%B7%20%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%2B%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E9%A6%99%E6%B8%AFvendor_c%E4%B8%8EPG%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-06 11:42｜日期依据：文件名日期

本文记录按 `cn` 分支香港架构，从 AWS S3 / Google Cloud Storage 同步香港资源的过程：

- `vendor_c_static.tar.gz`：vendor_c 厂商静态资源。
- `pgnew_shared.tar.gz`：只替换 PG 厂商 `pgnew/shared`，不替换 PG3 / PG4 / PG5。
- `vendor_c_db.tar.gz`：vendor_c 厂商结果集。

## 任务边界

用户要求：

```text
aws S3: 需同步香港
vendor_c_static.tar.gz vendor_c厂商资源
pgnew_shared.tar.gz 替换pg厂商pgnew目录下的shared

google cloud 存储桶:
vendor_c_db.tar.gz vendor_c厂商结果集

看 cn 分支就知道香港的了
pgnew_shared.tar.gz 这个 pg 的只替换 pgnew，pg3/4/5 都不要换。
```

执行位置：

```text
香港入口/Nginx：192.0.2.14 / bizops-hongkong-game-results-data-bt
AWS Profile：bizops-hk
AWS 私有桶：s3://bizops-h5-hk-517506432530
```

按 `origin/cn` 分支核验出的香港架构：

```text
静态资源：CloudFront OAC -> 香港私有 S3
动态接口：CloudFront -> 香港 Nginx 192.0.2.14 -> 外部双后端
外部后端：192.0.2.18 / 192.0.2.19
```

本次未操作巴西目录，未发布业务代码，未写 PG3 / PG4 / PG5 静态前缀。

## cn 分支与实时环境核验

读取的 `origin/cn` 关键文件：

```text
docker/doc/某业务公司运维AI交接总览.md
docker/doc/2026-07-17-香港AWS-S3与CloudFront迁移搭建记录.md
docker/doc/2026-07-17-香港CN五厂商收口与vendor_b-AWS接入完整记录.md
docker/doc/2026-07-17-香港CN五厂商前端可用域名清单.md
docker/deploy/hongkong/nginx-bizops.conf
docker/deploy/hongkong/sync_gcs_to_s3.py
docker/deploy/hongkong/validate_cloudfront_static.py
docker/conf/domains/pg.json
```

实时只读核验：

```text
香港入口：hostname=bizops-hongkong-game-results-data-bt，root 登录 OK。
AWS 身份：arn:aws:iam::517506432530:user/bizops-hk-nginx-ai。
目标桶：bizops-h5-hk-517506432530，Versioning=Enabled。
vendor_c 静态 CloudFront：E1U27HV4LQHIE2 / d306fzdxcl4hgw.cloudfront.net / Deployed / 5 aliases。
PG 静态 CloudFront：E2JLARIGDV5VZV / d1wnhpyrlnptrk.cloudfront.net / Deployed / 5 aliases。
```

外部后端实时连通性：

```text
192.0.2.18:9091  open
192.0.2.19:9091 open
192.0.2.18:9104  closed
192.0.2.19:9104 closed
192.0.2.18:22    closed
192.0.2.19:22   closed
```

因此本次 vendor_c 结果集完成香港入口源目录替换；未能推送到外部后端容器目录，也未验证 vendor_c 动态服务。

## 源包校验

工作目录：

```text
/root/bizops-resource-sync/hk-vendor_c-pg-20260806
```

AWS S3：

```text
s3://bizops-h5/vendor_c_static.tar.gz
Size：893,894,723 bytes
LastModified：2026-08-06 02:35:15 UTC
SHA256：730ea43aefeaa3cfe5efb47f9930b36425653f5c0719470119681781b87f4ec0
tar entries：26,822
顶层：./vendor_cstatic/
危险路径：0

s3://bizops-h5/pgnew_shared.tar.gz
Size：5,918,711 bytes
LastModified：2026-08-06 02:35:54 UTC
SHA256：3b24d23b736d9194b37af641f7a27d0c087fb723295c1f307ce36d34280b4ec9
tar entries：224
顶层：./shared/
危险路径：0
解包文件：180
```

Google Cloud Storage：

```text
gs://bizops-storage-slots-statics/game-results/vendor_c_db.tar.gz
Generation：1785983982829706
Size：624,371,535 bytes
Update time：2026-08-06 02:39:42 UTC
SHA256：2e69a2c7106d4a855e66567a0068baa4eebb3f0fe18af8cc027917be357cacac
tar entries：51
顶层：./vendor_c/
危险路径：0
```

## 静态资源同步

映射关系：

```text
vendor_cstatic/ -> s3://bizops-h5-hk-517506432530/vendor_c-static/
shared/        -> s3://bizops-h5-hk-517506432530/pg-static/shared/
```

dry-run：

```text
vendor_c 静态：待上传 0，对比后香港 S3 已是同版。
PG pgnew/shared：待上传 87 个对象。
```

实际同步：

```text
vendor_c 静态：上传 0 个对象。
PG pgnew/shared：上传 87 个对象。
post dry-run：两组均为 0 待上传。
```

CloudFront 刷新：

```text
PG static distribution：E2JLARIGDV5VZV
path：/shared/*
invalidation：IASQFD77H11E5Y82WMM94Y4INU
status：Completed
```

PG3 / PG4 / PG5 范围审计：

```text
同步日志未出现 pg3-static / pg4-static / pg5-static。
pg3-static/shared/ 自 2026-08-06 03:00 UTC 后新增版本：0
pg4-static/shared/ 自 2026-08-06 03:00 UTC 后新增版本：0
pg5-static/shared/ 自 2026-08-06 03:00 UTC 后新增版本：0
```

## 静态验证

PG `pgnew/shared` 代表文件：

```text
路径：shared/2c6e37b73c/03e51d9de2.5d961.json
size：8,198
SHA256：335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3
```

验证结果：

```text
pg-static.hkcloudplay01.com ～ pg-static.hkcloudplay05.com
5 / 5 HTTP 200
5 / 5 CORS *
5 / 5 SHA256 匹配
```

vendor_c 代表文件：

```text
路径：config/config.js
size：4,728
SHA256：836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c
```

验证结果：

```text
vendor_c-static.hkcloudplay01.com ～ vendor_c-static.hkcloudplay05.com
5 / 5 HTTP 200
5 / 5 CORS *
5 / 5 SHA256 匹配
```

说明：虽然 `cn` 历史文档记录 vendor_c 不属于当时启用范围，但实时验证显示当前 5 个 `vendor_c-static` 域名可访问并返回正确内容。

## vendor_c 结果集

替换目标：

```text
/www/wwwroot/game_results_data/vendor_c
```

替换前：

```text
owner/group：1002:1003
文件数：33
总字节：4,195,937,280
```

新包：

```text
DB 文件数：50
总字节：5,447,141,376
manifest SHA256：c1ea781173d7683f00172571458a257a2f3822602faf5306ee2c8fd93eec09f7
SQLite quick_check：50 / 50 OK
```

切换方式：

```text
1. 解包到 /root/bizops-resource-sync/hk-vendor_c-pg-20260806/extract/results/vendor_c。
2. 继承旧目录 owner/group 1002:1003。
3. 旧目录原子改名为备份。
4. 新目录原子改名为 /www/wwwroot/game_results_data/vendor_c。
5. 切换后再次执行 SQLite quick_check。
```

备份目录：

```text
/www/wwwroot/game_results_data/vendor_c.backup-20260806T032503Z-before-vendor_c-db
```

切换后：

```text
owner/group：1002:1003
文件数：50
总字节：5,447,141,376
SQLite quick_check：50 / 50 OK
```

外部后端说明：

```text
192.0.2.18 / 192.0.2.19 的 9104 与 SSH 当前不可达。
本次未能同步到后端 /opt/game_results_datas/vendor_c，也未能重启或验证 vendor_c 容器。
```

## 证据文件

香港入口机：

```text
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/vendor_c_static.tar.gz.list
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/pgnew_shared.tar.gz.list
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/vendor_c_db.tar.gz.list
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/s3-dryrun-vendor_c-static.txt
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/s3-dryrun-pg-shared.txt
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/s3-sync-vendor_c-static.log
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/s3-sync-pg-shared.log
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/cloudfront-invalidation-pg-shared.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/static-public-verify.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/vendor_c-real-dns-verify.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/vendor_c-db-sqlite-check.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/vendor_c-db-post-check.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/pg-scope-audit.json
/root/bizops-resource-sync/hk-vendor_c-pg-20260806/reports/final-verify-summary.json
```

## 飞机群通知

群：监控报警群

```text
3134：步骤 1/10，任务开始
3135：步骤 2/10，香港只读环境核验有差异
3136：步骤 3/10，按用户指示改以 cn 分支核验香港配置
3137：步骤 4/10，cn 分支香港架构核验完成
3138：步骤 5/10，源包下载和结构校验通过
3139：步骤 6/10，S3 dry-run 完成
3140：步骤 7/10，静态资源 S3 同步与 CDN 刷新完成
3141：步骤 8/10，静态公开验证通过
3142：步骤 9/10，Playson 结果集切换完成，PG 范围已复核
3143：步骤 10/10，最终汇总
3144：文档附件
```

## 结论

```text
香港 vendor_c 静态资源已确认同步到私有 S3 并通过 5 个真实静态域名验证。
香港 PG pgnew/shared 已上传 87 个对象并刷新 PG static CloudFront，5 个真实 PG 静态域名验证通过。
PG3 / PG4 / PG5 未同步、未刷新、未产生本任务新增版本。
香港入口 vendor_c 结果集已替换为 50 个 DB，切换前后 SQLite quick_check 均为 50/50 OK。
外部 vendor_c 后端 9104 与 SSH 当前不可达，因此结果集未推送到后端容器目录。
```
