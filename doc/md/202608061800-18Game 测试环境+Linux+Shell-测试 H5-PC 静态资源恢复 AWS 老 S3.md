---
id: "doc-c24bfdcc501f"
title: "测试 H5/PC 静态资源恢复 AWS 老 S3"
date: "2026-08-06T18:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1800-%E3%80%90%E6%9E%B6%E6%9E%84%E8%B0%83%E6%95%B4%2B%E5%9B%9E%E9%80%80%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%81%A2%E5%A4%8DAWS%E8%80%81S3.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1800-【架构调整+回退】测试H5-PC静态资源恢复AWS老S3.md"
sourceSha256: "94d454101bb9491b95352c50626db0045988ab06847505cc3a54fa00c400e161"
sourceSystem: "project-doc"
---

# 测试 H5/PC 静态资源恢复 AWS 老 S3

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608061800-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BLinux%2BShell-%E6%B5%8B%E8%AF%95%20H5-PC%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E6%81%A2%E5%A4%8D%20AWS%20%E8%80%81%20S3.md)

> 整理日期：2026-08-06 18:00｜日期依据：文件名日期

环境标签：测试环境 / H5 / PC / AWS S3 / ben-bot / 回退

记录时间：2026-08-06 18:00

## 1. 目标

按用户要求读取 workbench 与历史 S3/静态资源文档，把测试环境 H5/PC 前端构建配置恢复到之前的 AWS S3 老地址：

| 项目 | 当前默认 `NUXT_PUBLIC_CDN_URL` |
| --- | --- |
| 测试 H5 | `https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com` |
| 测试 PC | `https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com` |

本次同时从测试 H5/PC 默认发布链路里移除：

- `test-h5-s3.备案域名`、`test-pc-s3.备案域名` 作为默认前端静态资源域。
- 腾讯 COS 默认同步。
- 腾讯 CDN/EdgeOne 默认刷新。
- 前端静态资源签名鉴权。
- 用户追加要求：测试环境 `test-img.备案域名` 也恢复为后台原始 AWS CloudFront uploads 展示域名，不再返回 `test-img` 备案图片域名和 `token/t` 签名参数。

## 2. 历史依据

已读取：

- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `devops/ai_context/servers.yml`
- `devops/python/ben-bot/doc/2026-07-27_1503-【架构改造+网络调整】游点涩S3拆分与发版操作记录.md`
- `devops/python/ben-bot/doc/2026-07-29_1806-【运维记录】测试前端H5-PC备案域名与S3链路索引.md`
- `devops/python/ben-bot/doc/2026-07-29_2119-【架构调整+回退】测试PC前端静态资源鉴权回退与后端uploads防盗刷方案.md`
- `devops/python/ben-bot/doc/2026-07-29_2155-【网络调整+安全优化】测试后端uploads图片EdgeOne反代与防盗刷落地记录.md`
- `devops/python/ben-bot/doc/2026-07-29_2212-【运维记录】测试H5-PC前端静态资源与后端图片域名最终链路.md`
- `devops/python/ben-bot/doc/2026-08-04_2119-【修复Bug+链路改造】新增备案域名静态资源无CDN反代与测试H5-PC重发验证.md`

历史提交和文档确认，AWS 老公开桶域名为：

- H5：`https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com`
- PC：`https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com`

## 3. 本次改动

### 3.1 测试 H5 发布入口

文件：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/benbot_plugin.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/remote_youdianse_h5_config.py`

结果：

- `YOUDIANSE_H5_TEST_STATIC_CDN_URL` 改为 AWS H5 老 S3 域名。
- `YOUDIANSE_H5_TEST_STATIC_COS_BUCKET` 置空。
- 新增并传递 `YOUDIANSE_H5_TEST_SYNC_STATIC_TO_COS=0`。
- `YOUDIANSE_H5_TEST_TENCENT_CDN_PURGE_ENABLED=0` 保持关闭。
- 镜像结构版本升级到 `tooling-v23-aws-static-restore`，确保下一次发布会重建镜像并写入新的 `.env`。

### 3.2 测试 PC 发布入口

文件：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/benbot_plugin.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py`

结果：

- `YOUDIANSE_PC_TEST_STATIC_CDN_URL` 改为 AWS PC 老 S3 域名。
- `YOUDIANSE_PC_TEST_STATIC_COS_BUCKET` 置空。
- 新增并传递 `YOUDIANSE_PC_TEST_SYNC_STATIC_TO_COS=0`。
- `YOUDIANSE_PC_TEST_TENCENT_CDN_PURGE_ENABLED=0` 保持关闭。
- 删除测试 PC 插件和 PC wrapper 的静态资源签名鉴权默认变量映射。

### 3.3 PC Nginx 兼容反代模板

文件：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/test-img.hbabaxb.cn.conf`

结果：

- PC 页面域名下 `/images/`、`/image/`、`/video/`、`/videos/`、`/media/`、`/favicon.ico`、`/192.png`、`/512.png` 等兼容反代从旧 `test-pc-s3.hbabaxb.cn` 改为 AWS PC 老 S3 域名。
- 后端 uploads 图片主链路不改；只把占位图来源恢复到 PC AWS 前端静态桶。

### 3.4 ben-bot 容器环境

文件：

- `devops/python/ben-bot/docker/docker-compose.yml`

结果：

- 增加 `YOUDIANSE_H5_TEST_SYNC_STATIC_TO_COS` 和 `YOUDIANSE_PC_TEST_SYNC_STATIC_TO_COS` 注入项。
- 移除 `YOUDIANSE_PC_TEST_TENCENT_STATIC_AUTH_KEY` 注入项，避免测试 PC 静态资源签名 Key 再进入容器默认环境。

### 3.5 工作台与事实源

已更新：

- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`

## 4. 本地验证

已完成：

```text
python3 -m py_compile H5/PC 发布入口和共享配置：通过
测试 H5/PC 发布入口 grep hbbfuub 静态域：无命中
测试 PC 插件默认静态签名变量：已移除
```

## 5. 远端同步与验证

### 5.1 ben-bot 运行机同步

目标：

- `ubuntu@52.79.252.255`
- 仓库：`/opt/telegram/18game_devops`
- 机器人目录：`/opt/telegram/18game_devops/devops/python/ben-bot`

处理：

- 远端工作区存在现场修改，未执行 `git reset` 或整仓覆盖。
- 先备份目标文件到：`/opt/telegram/18game_devops/.codex-backup/test-h5-pc-aws-s3-restore-202608061800`
- 精确同步本次涉及脚本、Nginx 模板、compose 和 workbench 文档。
- 更新 ben-bot 运行 `.env` 的非敏感配置项：
  - H5/PC 静态 CDN URL 改为 AWS S3 老域名。
  - H5/PC COS bucket 置空。
  - H5/PC `SYNC_STATIC_TO_COS=0`。
  - H5/PC 腾讯刷新关闭。
  - 移除测试静态资源签名 Key 注入项。
- 重新构建并启动 `ben-bot` 容器。

容器内核验：

```text
H5_CDN=https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com
PC_CDN=https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com
H5/PC COS bucket 长度=0
H5/PC SYNC_STATIC_TO_COS=0
PC 静态签名 Key 不存在
ben-bot Up
```

### 5.2 H5/PC 重发版

由于首次外部页面 HTML 仍引用旧 `hbbfuub` 静态域，已重发当前测试版本：

| 项目 | Git 短 ID | 结果 |
| --- | --- | --- |
| H5 | `5d6fec5` | 成功 |
| PC | `041764b` | 成功 |

发布日志关键结论：

- Docker build 同步 Nuxt 静态资源到 AWS S3。
- 不同步腾讯 COS。
- 不刷新腾讯 CDN/EdgeOne。
- 不启用腾讯静态资源鉴权签名改写。
- 容器启动成功：
  - `youdianse_test_18game_h5_client_3003`
  - `youdianse_pc_dev_18game_pc_client_3004`

### 5.3 后台 uploads / test-img 回退

用户追加要求后，已处理测试后台图片展示域名：

配置项：

```text
Mongo collection: config
code: cdn_image
```

变更前：

```text
free=>https://test-img.hbabaxb.cn
aws=>https://test-img.hbabaxb.cn
```

变更后：

```text
free=>https://d1rct3ku9n07y3.cloudfront.net
aws=>https://d1rct3ku9n07y3.cloudfront.net
```

保留未动：

```text
tencent=>https://18game-storage-dev-uploads-1450169938.cos.ap-guangzhou.myqcloud.com
telnet=>https://jxkjg.missnlady.com
```

回滚点：

```text
/var/www/html/youdianse-php/runtime/logs/cdn_image_backup_20260806_aws_restore_20260806_181556.json
/opt/docker-youdianse-php/env/.env.dev.bak_before_remove_test_img_cdn_20260806_181959
```

同时处理：

- 清理 `system_config` 和后端应用缓存。
- 从宿主机事实源 `/opt/docker-youdianse-php/env/.env.dev` 移除 `[cdn.tencent.test-img]` 段，避免 `test-img` 再追加 `token/t`。
- 重启测试后台 `php-web` 和 `php-nginx` 容器。

### 5.4 最终验证

页面验证：

| 入口 | AWS 前端静态域命中 | hbbfuub 静态域命中 | CloudFront uploads 命中 | test-img 命中 | `敏感凭据：[已脱敏] 命中 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `https://h5.youdianse-test.xyz/` | H5 111 | 0 | 97 | 0 | 0 |
| `https://pc.youdianse-test.xyz/` | PC 115 | 0 | 86 | 0 | 0 |
| `https://test-h5.hbabaxb.cn/` | H5 111 | 0 | 97 | 0 | 0 |
| `https://test-pc.hbabaxb.cn/` | PC 115 | 0 | 86 | 0 | 0 |

HTTP 验证：

```text
https://h5.youdianse-test.xyz/version.json -> HTTP/2 200
https://pc.youdianse-test.xyz/version.json -> HTTP/2 200
https://18game-nuxt-static-test-h5.s3.ap-southeast-1.amazonaws.com/version.json -> HTTP/1.1 200 OK
https://18game-nuxt-static-test-pc.s3.ap-southeast-1.amazonaws.com/version.json -> HTTP/1.1 200 OK
https://admin.youdianse-test.xyz/ -> HTTP/2 404
```

说明：`admin.youdianse-test.xyz` 根路径历史上即返回 404，不代表 API 不可用。

后台验证：

```text
cdn_image free/aws: https://d1rct3ku9n07y3.cloudfront.net
宿主机 .env.dev: [cdn.tencent.test-img] absent
youdianse-dev-php-web: Up
youdianse-dev-php-nginx: Up
youdianse-dev-php-cron: Up
```

## 6. 飞机群通知

本次测试环境任务按 workbench 默认通知目标发送到：

- `18game运维`

已发送阶段通知：

- 步骤 1：上下文读取完成。
- 步骤 2：历史 AWS S3 老地址核验完成。
- 步骤 3：本地配置回退和本地校验完成。
- 步骤 4：workbench / servers / 文档更新完成。
- 步骤 5：ben-bot 运行机只读核验完成。
- 步骤 6：远端文件同步、`.env` 更新和 ben-bot 重建完成。
- 步骤 7：页面仍引用旧静态域，启动 H5/PC 重发。
- 步骤 8：H5/PC 重发完成并验证 AWS S3 静态域。
- 步骤 9：`test-img` 历史链路确认。
- 步骤 10：后台 `cdn_image` 回退并清缓存。
- 步骤 11：后台容器状态复查并恢复。
- 步骤 12：最终验证通过。

最终汇总和本文档已发送到同一群。
