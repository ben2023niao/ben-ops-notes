---
id: "doc-8cf582cfae4e"
title: "线上网关 nginx 日志压缩与 S3 归档自动化"
date: "2026-08-24T19:15:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-24_1915-%E3%80%90%E9%85%8D%E7%BD%AE%2B%E8%87%AA%E5%8A%A8%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%BD%91%E5%85%B3nginx%E6%97%A5%E5%BF%97%E5%8E%8B%E7%BC%A9%E4%B8%8ES3%E5%BD%92%E6%A1%A3.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-24_1915-【配置+自动化】线上网关nginx日志压缩与S3归档.md"
sourceSha256: "688efe0826a4a6f5fddb826815ec2d2bd85261e90c8173a01d7d3170932297a3"
sourceSystem: "project-doc"
---

# 线上网关 nginx 日志压缩与 S3 归档自动化

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-24_1915-【配置+自动化】线上网关nginx日志压缩与S3归档.md`

> 整理日期：2026-08-24 19:15｜日期依据：文件名日期

时间：2026-08-24 19:15
环境标签：线上环境 / 网关 16.208.38.88 / 日志自动化 / S3

## 需求

16.208.38.88（线上新 H5+PC 网关）日志自动化压缩，一星期前日志上传 S3 后清理本地，保证磁盘空间够用。

## 方案与落地

1. **压缩（网关本地）**：`/etc/logrotate.d/nginx` 保留天数 14→7（每日自动压缩；原配置备份 `nginx.bak.20260824`）。
2. **归档（ben-bot 宿主机每日 03:05，root cron）**：
   - 脚本：`/usr/local/bin/youdianse-nginx-log-archive.sh`（仓库副本 `devops/scripts/youdianse-nginx-log-archive.sh`）
   - 逻辑：ssh 到网关列出 7 天前 `*.gz` → scp 拉到本机 → curl AWS SigV4 上传 `s3://youdianse-prod-gateway-logs/nginx/<文件名>`（Content-Encoding: gzip）→ 校验 200 后 `sudo rm` 网关本地
   - 凭证：每次运行从 ben-bot 容器环境读取 `YOUDIANSE_H5_TEST_AWS_ACCESS_KEY_ID/SECRET`，不落盘
3. **S3 桶**：`youdianse-prod-gateway-logs`（ap-southeast-1，已创建并验证）。

## 验证（首次真实归档）

- S3 对象：`nginx/access.log.9/10/11.gz`、`nginx/error.log.9/10/11.gz` 共 6 个，PUT http=200。
- 网关：7 天前 `.gz` 剩余 0；`/var/log/nginx` 6.3G；磁盘 32%（34G 可用）。
- ben-bot 宿主机无临时文件残留。

## 说明

- 归档失败会保留本地并记录日志（`/var/log/youdianse-nginx-log-archive.log`），下次重跑可重传（PUT 幂等）。
- 若网关 access 日志仍快速增长，建议后续对静态/图片路径关闭 access_log，或调整 logrotate 保留天数。

## 通知与提交

- 步骤 1-3 已同步 `18GAME_ 上线群（正式環境）`。
- 本地 Git 已提交（不 Push）。
