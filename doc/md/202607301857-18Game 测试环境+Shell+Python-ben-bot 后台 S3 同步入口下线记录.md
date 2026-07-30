---
id: "doc-7a9f49a618f0"
title: "ben-bot 后台 S3 同步入口下线记录"
date: "2026-07-30T18:57:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1857-%E3%80%90%E4%BC%98%E5%8C%96%2B%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91ben-bot%E5%90%8E%E5%8F%B0S3%E5%90%8C%E6%AD%A5%E5%85%A5%E5%8F%A3%E4%B8%8B%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1857-【优化+运维记录】ben-bot后台S3同步入口下线记录.md"
sourceSha256: "201b7dfa02d9d8c113e2fe7abf5f4906fc66b47bd5e86c9a5f0d149eb877fca4"
sourceSystem: "project-doc"
---

# ben-bot 后台 S3 同步入口下线记录

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-07-30_1857-【优化+运维记录】ben-bot后台S3同步入口下线记录.md`

> 整理日期：2026-07-30 18:57｜日期依据：文件名日期

环境标签：测试+线上环境

时间：2026-07-30 18:57

## 背景

游点涩测试和线上后台 uploads 资源已经改为通过备案域名链路访问：

- 测试环境：`test-s3.*` / `test-img.*` 备案域名链路
- 线上环境：`main-s3.*` 备案域名链路

原来的机器人手动同步入口用于把后台 AWS S3 增量同步到腾讯新加坡 COS。现在后台图片访问链路已经调整，继续保留这两个按钮容易让运维误点，也容易和当前备案域名链路混淆，所以本次下线。

## 本次下线内容

从 ben-bot 主菜单移除：

- `测试后台-S3同步`
- `线上后台-S3同步`

删除对应按钮目录：

- `data/scripts/测试环境-游点涩后台-s3-同步/`
- `data/scripts/线上环境-游点涩后台-s3-同步/`

删除共享同步脚本：

- `data/scripts/.shared/backend_s3_sync.py`

清理容器环境变量注入：

- `YOUDIANSE_TEST_BACKEND_S3_*`
- `YOUDIANSE_PROD_BACKEND_S3_*`

菜单发现逻辑同步做了一个小优化：

- 忽略 `__pycache__` 目录，避免 Python 缓存目录被误展示成机器人按钮或分类。

## 不影响内容

本次只下线“后台 S3 手动同步”入口，不影响下面这些能力：

- `测试环境-游点涩-h5-发版`
- `测试环境-游点涩-pc-发版`
- `线上环境-游点涩-h5-发版`
- H5/PC 前端构建后同步到 AWS 前端桶
- H5/PC 前端构建后同步到腾讯新加坡 COS 静态桶
- H5/PC 发布后的腾讯 CDN/EdgeOne 缓存刷新
- 后端发布、定时任务、脱敏配置查看、域名接入、文档入口

## 后续运维规则

后台 uploads 图片资源以后按备案域名链路处理，不再从机器人按钮触发旧的 AWS 到 COS 后台同步。

如果以后确实需要重新做后台资源迁移，应重新开一个明确任务，单独写方案、验证源桶和目标桶，再新增临时脚本或一次性执行记录，不建议恢复常驻按钮。

## 验证项

本次完成后需要验证：

1. 代码里不再有两个后台 S3 同步按钮入口。已验证。
2. 机器人主菜单不再显示 `测试后台-S3同步`、`线上后台-S3同步`。已验证。
3. 前端 H5/PC 发布按钮仍存在。已验证。
4. 前端静态资源双推 AWS + 腾讯新加坡 COS 的发布逻辑未被移除。已验证。
5. ben-bot 容器重建/重启后运行正常。已验证。
6. 机器人已尽可能广播到已记录群。结果：成功 5 个群，失败 0 个。

## 部署记录

本地提交：

- `6483fb9 chore: remove backend s3 sync bot entries`
- `5405f3b fix: hide pycache from bot menu registry`

服务器部署：

- 机器：ben-bot 当前运行服务器
- 路径：`/opt/telegram/18game_devops`
- 方式：服务器工作区存在现场改动，未直接 `git pull` 覆盖；采用备份后精确同步和重建。
- 备份：`/opt/telegram/18game_devops/.codex-backup/ben-bot-s3-disable-20260730110353/`
- 容器：`ben-bot` 已重建并启动。

## 回滚方式

如果需要恢复旧入口：

```bash
git revert <本次提交>
```

然后重新部署 ben-bot。

恢复前必须再次确认后台 AWS S3 到腾讯 COS 同步是否仍是当前业务需要，避免把旧链路重新放回机器人主界面。
