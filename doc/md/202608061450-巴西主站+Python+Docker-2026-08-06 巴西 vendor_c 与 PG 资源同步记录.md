---
id: "doc-944c691cba5a"
title: "2026-08-06 巴西 vendor_c 与 PG 资源同步记录"
date: "2026-08-06T14:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Python", "Docker", "Nginx", "监控告警", "自动化", "CDN", "数据库恢复"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-06-1450-%E3%80%90%E8%A1%A5%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%2B%E6%95%B0%E6%8D%AE%E7%BB%B4%E6%8A%A4%E3%80%91%E5%B7%B4%E8%A5%BFvendor_c%E4%B8%8EPG%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-06-1450-【补静态资源+数据维护】巴西vendor_c与PG资源同步记录.md"
sourceSha256: "82140e08a65b0611fa36edda3efeceea526adf8373d8773b984dd90b9fd6aa6f"
sourceSystem: "project-doc"
---

# 2026-08-06 巴西 vendor_c 与 PG 资源同步记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061450-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BPython%2BDocker-2026-08-06%20%E5%B7%B4%E8%A5%BF%20vendor_c%20%E4%B8%8E%20PG%20%E8%B5%84%E6%BA%90%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-06 14:50｜日期依据：文件名日期

本文记录按香港同版资源补齐巴西生产环境：

- `vendor_c_static.tar.gz`：vendor_c 厂商静态资源。
- `pgnew_shared.tar.gz`：只替换 PG 厂商 `pgnew/shared`，不替换 PG3 / PG4 / PG5。
- `vendor_c_db.tar.gz`：vendor_c 厂商结果集。

## 任务边界

用户要求：

```text
巴西项目也要更新客户端代码啊
aws S3:
vendor_c_static.tar.gz vendor_c厂商资源
pgnew_shared.tar.gz 替换pg厂商pgnew目录下的shared

google cloud 存储桶:
vendor_c_db.tar.gz vendor_c厂商结果集

看 cn 分支就知道香港的了
pgnew_shared.tar.gz 这个 pg 的只替换 pgnew，pg3,4,5都不要换。
```

执行位置：

```text
巴西宝塔：192.0.2.8 / bizops-saopaulo-game-results-data-bt
后台 01：192.0.2.1 / bizops-saopaulo-sanic-prod-01
后台 02：192.0.2.1 / bizops-saopaulo-sanic-prod-02
工作目录：/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg
```

本次未发布业务代码，未操作香港环境，未写 PG3 / PG4 / PG5。

## 端口复核

用户提醒后，实时复核历史文档、服务配置、Nginx upstream 和 Docker inspect：

```text
服务配置：宿主机 9104 -> 容器内 9020
Nginx upstream：192.0.2.1:9104 + 192.0.2.1:9104
容器：bizops-vendor_c-release-01 / 02
挂载：/opt/game_results_datas/vendor_c -> /app/game_result_datas/vendor_c
```

因此宝塔/Nginx/后端宿主机健康检查使用 `9104`，容器内端口为 `9020`。

## 源包校验

AWS S3：

```text
s3://bizops-h5/vendor_c_static.tar.gz
Size：893,894,723 bytes
LastModified：2026-08-06 02:35:15 UTC
SHA256：730ea43aefeaa3cfe5efb47f9930b36425653f5c0719470119681781b87f4ec0
tar entries：26,822
顶层：./vendor_cstatic/
危险路径：0
解包文件：25,818

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
解包 DB：50
SQLite quick_check：50 / 50 OK
manifest SHA256：c1ea781173d7683f00172571458a257a2f3822602faf5306ee2c8fd93eec09f7
```

## 静态资源同步

映射关系：

```text
vendor_cstatic/ -> /www/wwwroot/vendor_c-static/
shared/        -> /www/wwwroot/pg-static/shared/
```

dry-run：

```text
vendor_c 静态：文件内容差异 0。
PG pgnew/shared：87 个文件差异，新增 82，覆盖 5。
PG 覆盖前备份：5 个旧文件。
```

实际覆盖：

```text
vendor_c 静态：同版，跳过写文件。
PG pgnew/shared：只按 --files-from 覆盖 87 个 shared 文件。
PG 覆盖后二次 dry-run：文件差异 0。
代表文件：shared/2c6e37b73c/03e51d9de2.5d961.json
SHA256：335299ab4270db94053b2bac5f8a977c027f26f93b7406f29883d975cfa45ac3
```

GCS 与 CDN：

```text
vendor_c live dry-run：0 待复制，0 删除。
vendor_c backup dry-run：0 待复制，0 删除。

PG shared live：同步 180 个对象到 gs://bizops-gcs-pg-static/shared。
PG shared backup：同步 180 个对象到 gs://bizops-game-statics-gcs/pg-static/shared。
PG shared live/backup 二次 dry-run：0 待复制，0 删除。

PG static CDN：22 个 host 刷新 /shared/*，22 / 22 DONE。
```

PG3 / PG4 / PG5 范围审计：

```text
dry-run、实际 rsync、GCS 同步日志和 CDN 刷新日志均未命中 pg3-static / pg4-static / pg5-static。
```

## vendor_c 结果集

替换目标：

```text
宝塔源目录：/www/wwwroot/game_results_data/vendor_c
后端目录：/opt/game_results_datas/vendor_c
```

宝塔切换：

```text
旧目录 owner/group：1002:1003
新目录文件数：50
新目录字节数：5,447,141,376
宝塔备份：/www/wwwroot/game_results_data/vendor_c.backup-20260806T063302Z-before-vendor_c-db
切换后 SQLite quick_check：50 / 50 OK
```

后端滚动切换：

```text
后端 01 临时目录：/opt/game_results_datas/.vendor_c-new-20260806T063302Z
后端 02 临时目录：/opt/game_results_datas/.vendor_c-new-20260806T063302Z
后端备份：/opt/game_results_datas/vendor_c.backup-20260806T063302Z-before-vendor_c-db
```

第一次在后端 01 使用宿主机 `sqlite3` 命令校验时发现命令不存在；当时尚未停止容器、尚未切换后端目录。随后改用后端 `python3` 的 sqlite3 标准库做同等 `PRAGMA quick_check`。

最终后端结果：

```text
后端 01：stage quick_check 50/50 OK，容器 bizops-vendor_c-release-01 running，RestartCount=0，9104 open，目标 50 DB。
后端 02：stage quick_check 50/50 OK，容器 bizops-vendor_c-release-02 running，RestartCount=0，9104 open，目标 50 DB。
```

## 最终验证

静态公开验证：

```text
PG static：
  host：22
  path：shared/2c6e37b73c/03e51d9de2.5d961.json
  HTTP 200 + SHA256 匹配：22 / 22

vendor_c static：
  host：22
  path：config/config.js
  HTTP 200 + SHA256 匹配：22 / 22
```

动态与入口验证：

```text
https://vendor_c-games.xqv9m8.icu/config/config.js
  HTTP 200

https://vendor_c-games.xqv9m8.icu/web-api/game-proxy/v2/Ping/Get?gi=power_crown
  HTTP 200

https://ind-h5.bizopsplus999.com/vendor_cbronline/
  HTTP 200
```

后端最终状态：

```text
bizops-saopaulo-sanic-prod-01：bizops-vendor_c-release-01 running，RestartCount=0，/opt/game_results_datas/vendor_c 50 DB，9104 open。
bizops-saopaulo-sanic-prod-02：bizops-vendor_c-release-02 running，RestartCount=0，/opt/game_results_datas/vendor_c 50 DB，9104 open。
```

## 证据文件

巴西宝塔：

```text
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/preflight.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/vendor_c-realtime-port-verify.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/source-download-verify.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/rsync-dryrun-vendor_c-static.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/rsync-dryrun-pg-shared.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/static-dryrun-summary.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/static-overlay-summary.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/gcs-cdn-summary.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/cdn-invalidation-status.tsv
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/vendor_c-db-local-post-check.tsv
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/vendor_c-db-switch-summary.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/vendor_c-db-backend-resume-summary.txt
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/final-public-verify.json
/root/bizops-static-import/client-update-20260806-1412-brazil-vendor_c-pg/reports/final-backend-state.txt
```

## 飞机群通知

群：监控报警群

```text
3150：步骤 1/8，任务开始
3151：步骤 2/8，只读预检完成
3154：步骤 3/8，源包下载与校验完成，含端口复核
3155：步骤 4/8，静态 dry-run 与备份完成
3156：步骤 5/8，静态 GCS 与 CDN 完成
3158：步骤 6/8，后端校验工具差异，未停容器未切换后端，改用 python3 sqlite3
3165：步骤 7/8，vendor_c 结果集切换完成
3168：步骤 8/8，最终验证通过
3169：文档附件
```

## 结论

```text
巴西 vendor_c 静态资源与源包同版，GCS live/backup dry-run 均为 0，22 个公开静态域名验证通过。
巴西 PG pgnew/shared 已只写 /www/wwwroot/pg-static/shared，GCS live/backup 同步完成，22 个 PG static 域名验证通过。
PG3 / PG4 / PG5 未写入、未同步、未刷新。
巴西 vendor_c 结果集已在宝塔源目录和两台后端切换为 50 个 DB，切换前后 SQLite 校验通过，两台 vendor_c 容器运行正常。
```
