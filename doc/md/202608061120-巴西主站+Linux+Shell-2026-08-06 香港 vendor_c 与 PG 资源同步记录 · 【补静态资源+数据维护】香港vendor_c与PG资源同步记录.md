---
id: "doc-1f1e976835eb"
title: "2026-08-06 香港 vendor_c 与 PG 资源同步记录 · 【补静态资源+数据维护】香港vendor_c与PG资源同步记录"
date: "2026-08-06T11:20:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-08-06-1120-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%2B%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E9%A6%99%E6%B8%AFvendor_c%E4%B8%8EPG%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-08-06-1120-【补静态资源+数据维护】香港vendor_c与PG资源同步记录.md"
sourceSha256: "d7d31f1f463b42cb2206761c04d1c594cbc76fc7c51fdb028d2cd351ee52b32e"
sourceSystem: "project-doc"
---

# 2026-08-06 香港 vendor_c 与 PG 资源同步记录 · 【补静态资源+数据维护】香港vendor_c与PG资源同步记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061120-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-2026-08-06%20%E9%A6%99%E6%B8%AF%20vendor_c%20%E4%B8%8E%20PG%20%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95%20%C2%B7%20%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%2B%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E9%A6%99%E6%B8%AFvendor_c%E4%B8%8EPG%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-06 11:20｜日期依据：文件名日期

本文补录香港 `cn` 环境按用户要求同步 Playson 与 PG 资源的执行记录，并记录本会话在补文档前做的只读复核。

## 执行结论

```text
范围：仅香港 AWS S3 / CloudFront 与香港入口机；未操作巴西，未发布业务代码。
AWS S3 源包：
  vendor_c_static.tar.gz -> Playson 厂商静态资源
  pgnew_shared.tar.gz -> 仅 PG pgnew/shared
Google Cloud 源包：
  vendor_c_db.tar.gz -> Playson 厂商结果集
PG 范围：只替换 pgnew/shared；未替换 pg3、pg4、pg5。
Playson 静态：香港 S3 vendor_c-static 已是同版，公开链路验证通过。
PG shared：香港 S3 pg-static/shared 实际上传 87 个对象，CloudFront /shared/* 刷新完成，公开链路验证通过。
Playson 结果集：香港入口 /www/wwwroot/game_results_data/vendor_c 已原子替换，旧目录已备份，切换前后 SQLite quick_check 均 50/50 OK。
外部后端：192.0.2.18 / 192.0.2.19 的 9104 与 SSH 当时不可达，因此未推送后端容器目录。
```

## 任务来源

用户要求：

```text
读取 docker 下 doc 里面补资源的文档。
使用 workbench。
读取之前操作留下的 doc 文档。
每步操作都发群通知。
操作完成后先验证然后汇总文档，汇总和文档发群里。

aws S3: 需同步香港
vendor_c_static.tar.gz vendor_c厂商资源
pgnew_shared.tar.gz 替换pg厂商pgnew目录下的shared

google cloud 存储桶:
vendor_c_db.tar.gz vendor_c厂商结果集

看 cn 分支就知道香港的了。
pgnew_shared.tar.gz 替换pg厂商pgnew目录下的shared 这个pg的只替换pgnew哦，pg3,4,5都不要换。
```

本次补录前已读取：

```text
docker/workbench/START_HERE.md
docker/workbench/CURRENT_TASK.md
docker/workbench/CURRENT_STATE.md
docker/workbench/MACHINE_ACCESS_MATRIX.md
docker/workbench/PROJECT_RUNTIME_CHAINS.md
docker/workbench/DECISIONS.md
docker/workbench/ACTIVE_TASKS.md
docker/doc/2026-08-04-1233-【补静态资源+网络调整】香港Playson静态资源与域名接入记录.md
origin/master:docker/doc/2026-07-13-PG1312883黄金摇钱树静态资源补文件与GCS同步记录.md
origin/master:docker/doc/2026-07-14-vendor_a葡萄牙语静态资源完整包部署与验证记录.md
origin/master:docker/ben-bot/README.md
```

`origin/master` 最新提交为 `fbf75231 修复vendor_a规则页面`，只修改 `vendor_a/vendor_b.py` 和 `vendor_a/vendor_a.py`，没有新增本次香港资源同步文档。master 可参考的是旧资源包校验/同步/验证文档风格，以及 ben-bot 通知机制；香港事实仍以 `cn` workbench 和实时只读验证为准。

## 源包核验

群通知记录的源包校验结果：

```text
AWS vendor_c_static.tar.gz
  size: 893,894,723 bytes
  SHA256: 730ea43aefeaa3cfe5efb47f9930b36425653f5c0719470119681781b87f4ec0
  entries: 26,822
  top: ./vendor_cstatic/
  dangerous paths: 0

AWS pgnew_shared.tar.gz
  size: 5,918,711 bytes
  SHA256: 3b24d23b736d9194b37af641f7a27d0c087fb723295c1f307ce36d34280b4ec9
  entries: 224
  top: ./shared/
  dangerous paths: 0

GCS vendor_c_db.tar.gz
  size: 624,371,535 bytes
  SHA256: 2e69a2c7106d4a855e66567a0068baa4eebb3f0fe18af8cc027917be357cacac
  entries: 51
  top: ./vendor_c/
  dangerous paths: 0
```

## 香港架构确认

按 `cn` 分支和 workbench 确认香港当前链路：

```text
静态：Cloudflare DNS-only CNAME -> CloudFront OAC -> 私有 S3 bizops-h5-hk-517506432530
动态：CloudFront -> 香港 Nginx 192.0.2.14 -> 外部后端 192.0.2.18 / 192.0.2.19
入口机：192.0.2.14 / bizops-hongkong-game-results-data-bt
```

本任务开始时的特别边界：

```text
不操作巴西目录。
不发布业务代码。
覆盖前备份。
不把 Secret、Token、密码写入群或文档。
PG shared 只进入 pg-static/shared，不进入 pg3-static/shared、pg4-static/shared、pg5-static/shared。
```

## S3 同步记录

目标桶：

```text
s3://bizops-h5-hk-517506432530
Versioning: Enabled
```

Playson 静态：

```text
source: vendor_cstatic/
target: s3://bizops-h5-hk-517506432530/vendor_c-static/
dry-run 待上传：0
实际上传：0
结论：香港 S3 已是同版。
```

PG shared：

```text
source: shared/
target: s3://bizops-h5-hk-517506432530/pg-static/shared/
dry-run 待上传：87
实际上传：87
post dry-run 待上传：0
delete: 未使用
```

CloudFront：

```text
PG static distribution: E2JLARIGDV5VZV
paths: /shared/*
invalidation: IASQFD77H11E5Y82WMM94Y4INU
status: Completed
```

## Playson 结果集切换

群通知记录：

```text
target: /www/wwwroot/game_results_data/vendor_c
backup: vendor_c.backup-20260806T032503Z-before-vendor_c-db
new DB count: 50
new DB bytes: 5,447,141,376
pre-switch SQLite quick_check: 50/50 OK
post-switch SQLite quick_check: 50/50 OK
manifest SHA256: c1ea781173d7683f00172571458a257a2f3822602faf5306ee2c8fd93eec09f7
```

本会话补文档时，本地未注入 `PGSERVER_DEPLOY_PASS`，因此未能重新登录香港入口机复核 SQLite 和目录；该部分以 2026-08-06 群通知记录为证据。

## 最终只读复核

补文档前，本地公网验证如下。

PG shared 样本：

```text
path: /shared/2c6e37b73c/03e51d9de2.5d961.json

pg-static.hkcloudplay01.com -> 200, 8198 bytes, SHA256 335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3, CORS *
pg-static.hkcloudplay02.com -> 200, 8198 bytes, SHA256 335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3, CORS *
pg-static.hkcloudplay03.com -> 200, 8198 bytes, SHA256 335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3, CORS *
pg-static.hkcloudplay04.com -> 200, 8198 bytes, SHA256 335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3, CORS *
pg-static.hkcloudplay05.com -> 200, 8198 bytes, SHA256 335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3, CORS *
```

Playson 静态样本：

```text
path: /config/config.js

vendor_c-static.hkcloudplay01.com -> 200, 4728 bytes, SHA256 836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c, CORS *
vendor_c-static.hkcloudplay02.com -> 200, 4728 bytes, SHA256 836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c, CORS *
vendor_c-static.hkcloudplay03.com -> 200, 4728 bytes, SHA256 836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c, CORS *
vendor_c-static.hkcloudplay04.com -> 200, 4728 bytes, SHA256 836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c, CORS *
vendor_c-static.hkcloudplay05.com -> 200, 4728 bytes, SHA256 836d1d0e6c91176e87593e612d8aa65a4f1ac9e71a62ed915b725a88ed25830c, CORS *
```

S3 私有性：

```text
https://bizops-h5-hk-517506432530.s3.ap-east-1.amazonaws.com/pg-static/shared/2c6e37b73c/03e51d9de2.5d961.json -> 403
https://bizops-h5-hk-517506432530.s3.ap-east-1.amazonaws.com/vendor_c-static/config/config.js -> 403
```

PG3/4/5 范围复核：

```text
pg3-static.hkcloudplay01.com/shared/2c6e37b73c/03e51d9de2.5d961.json -> 403
pg4-static.hkcloudplay01.com/shared/2c6e37b73c/03e51d9de2.5d961.json -> 403
pg5-static.hkcloudplay01.com/shared/2c6e37b73c/03e51d9de2.5d961.json -> 403
```

该样本在 `pg-static` 为 200，在 `pg3/4/5-static` 为 403，符合本次“只替换 pgnew，不替换 PG3/4/5”的范围要求。

Playson 动态根路径补充观察：

```text
vendor_c-games.hkcloudplay01.com -> 404
vendor_c-games.hkcloudplay02.com -> 404
vendor_c-games.hkcloudplay03.com -> 404
vendor_c-games.hkcloudplay04.com -> 404
vendor_c-games.hkcloudplay05.com -> 404
vendor_c-api.hkplaycore.com -> 404
```

说明：本次任务核心为静态与结果集补资源。Playson 动态业务链路是否可用，仍需按实际业务路径、后端服务状态和后端团队边界另行复测。

## 飞机群通知

用户提供的群通知内容显示本次生产操作已按 1/10 至 10/10 分步发送，并发送文档附件口径：

```text
步骤 1/10：任务开始，明确范围、资源包和保护要求。
步骤 2/10：香港只读环境核验，历史后端 01/02 不在当前实例列表，入口机目录状态记录。
步骤 3/10：按用户指示改以 cn 分支核验香港配置。
步骤 4/10：cn 分支香港架构核验完成，确认 S3/CloudFront/Nginx/外部双后端链路。
步骤 5/10：三个源包下载、SHA256 和结构校验通过。
步骤 6/10：香港 S3 dry-run 完成。
步骤 7/10：S3 同步与 PG static CloudFront 刷新完成。
步骤 8/10：PG shared 与 Playson static 公开验证通过。
步骤 9/10：Playson 结果集切换完成，PG3/4/5 未触碰复核完成。
步骤 10/10：最终汇总完成。
文档附件：已按用户贴出的群消息发送，message_id 未在当前会话文本中提供。
```

本次补文档/复核新增通知：

```text
文档补录 1/3：已读取 cn workbench 与 master 最新提交，静态公网复核通过，message_id=3145。
文档补录 2/3：事件文档已写入，workbench 已更新，CI 与敏感扫描通过，message_id=3146。
文档补录 3/3：最终汇总已发送，message_id=3147。
文档附件：已发送，message_id=3148。
文档附件定稿版：已发送，message_id=3149。
```

## 回滚

PG shared：

```text
S3 bucket versioning 已启用。
如需回退，按对象版本恢复 pg-static/shared/ 下本次更新的 87 个对象，然后刷新 CloudFront E2JLARIGDV5VZV /shared/*。
不得回退或改动 pg3-static/shared、pg4-static/shared、pg5-static/shared。
```

Playson 静态：

```text
本次 vendor_c-static 实际上传 0，对象已是同版；无需回滚。
```

Playson 结果集：

```text
入口机旧目录备份：/www/wwwroot/game_results_data/vendor_c.backup-20260806T032503Z-before-vendor_c-db
如需回滚，先停止依赖该结果集的读取进程或确认可热切，再把当前目录备份后原子切回旧目录，并重新执行 SQLite quick_check。
```

## 后续事项

```text
1. 如需把 Playson 结果集推到外部后端容器目录，需后端团队提供可达 SSH 或发布入口，并明确目录。
2. 如需复测 Playson 动态业务可用性，应使用实际业务 URL，而不是仅访问域名根路径。
3. 如果本地要直接发群通知，应注入 TG_BOT_TOKEN / TELEGRAM_API_TOKEN 和 TG_CHAT_ID / BEN_BOT_MONITOR_CHAT_ID，避免依赖 master 巡检脚本中的兜底配置。
```
