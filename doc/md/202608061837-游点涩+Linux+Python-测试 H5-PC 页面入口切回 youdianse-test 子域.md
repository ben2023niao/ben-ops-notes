---
id: "doc-bf0090234c73"
title: "测试 H5/PC 页面入口切回 youdianse-test 子域"
date: "2026-08-06T18:37:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Python", "Docker", "Nginx", "自动化", "DNS", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1837-%E3%80%90%E9%85%8D%E7%BD%AE%E8%B0%83%E6%95%B4%2B%E5%9F%9F%E5%90%8D%E5%9B%9E%E9%80%80%E3%80%91%E6%B5%8B%E8%AF%95H5-PC%E9%A1%B5%E9%9D%A2%E5%85%A5%E5%8F%A3%E5%88%87%E5%9B%9Eyoudianse-test%E5%AD%90%E5%9F%9F.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1837-【配置调整+域名回退】测试H5-PC页面入口切回youdianse-test子域.md"
sourceSha256: "7741213d378fc0ab3d4b6df34308187061a1c2de61cae51d6e56861f1359fe53"
sourceSystem: "project-doc"
---

# 测试 H5/PC 页面入口切回 youdianse-test 子域

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-06_1837-【配置调整+域名回退】测试H5-PC页面入口切回youdianse-test子域.md`

> 整理日期：2026-08-06 18:37｜日期依据：文件名日期

环境标签：测试环境 / 游点涩 / H5 / PC / 宝塔 / ben-bot / 域名回退

记录时间：2026-08-06 18:37

## 1. 目标

按用户要求读取 workbench、docker/doc 线索和历史补资源/补域名文档后，砍掉测试 H5/PC 页面入口里的旧备案域名默认链路，新增并启用：

- `https://test-h5.youdianse-test.xyz`
- `https://test-pc.youdianse-test.xyz`

同时要求测试环境机器人发布 H5/PC 最后完成输出必须显示新域名。

## 2. 历史依据

已读取：

- `workbench/START_HERE.md`
- `workbench/ACTIVE_TASKS.md`
- `workbench/PROJECT_INDEX.md`
- `workbench/MACHINE_ACCESS_MATRIX.md`
- `workbench/PROJECT_RUNTIME_CHAINS.md`
- `workbench/projects/18game_devops/CURRENT_STATE.md`
- `workbench/projects/18game_devops/CURRENT_TASK.md`
- `devops/ai_context/servers.yml`
- `devops/python/ben-bot/doc/2026-07-29_1755-【优化】测试前端发布完成通知补备案域名记录.md`
- `devops/python/ben-bot/doc/2026-08-04_2219-【运维记录+域名补全】四个备案域名测试页面入口补全.md`
- `devops/python/ben-bot/doc/2026-08-04_2143-【运维记录+域名补全】hbabaxb-hbazuua前端S3静态资源域名补全.md`
- `devops/python/ben-bot/doc/2026-08-06_1800-【架构调整+回退】测试H5-PC静态资源恢复AWS老S3.md`

结论：

- `youdianse-test.xyz` 已有泛解析 `*.youdianse-test.xyz -> 38.92.8.34`。
- 测试 H5/PC 服务器是宝塔服务器 `38.92.8.34`。
- 历史机器人完成输出通过 `BEN_BOT_ICP_ACCESS_URL` 展示页面备用域名。

## 3. 本次改动

### 3.1 ben-bot 发布完成输出

文件：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/benbot_plugin.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/server_config.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/youdianse_test_18game_h5_client.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/benbot_plugin.py`
- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/youdianse_test_18game_pc_client.py`
- `devops/python/ben-bot/app/benbot/executor.py`

结果：

- H5 完成输出域名改为 `https://test-h5.youdianse-test.xyz`。
- PC 完成输出域名改为 `https://test-pc.youdianse-test.xyz`。
- 完成消息和日志附件 caption 的文案从“备案访问域名”改为“测试访问域名”。

### 3.2 本地 PC Nginx 模板

文件：

- `devops/python/ben-bot/data/scripts/测试环境-游点涩-pc-发版/nginx/pc.youdianse-test.xyz.conf`

结果：

- `server_name` 改为 `pc.youdianse-test.xyz test-pc.youdianse-test.xyz`。
- 旧 `test-pc-s3.hbabaxb.cn` 兼容反代改回 AWS PC 老 S3 域名。

### 3.3 ben-bot 运行机

目标：

- `ubuntu@52.79.252.255`
- 仓库：`/opt/telegram/18game_devops`

处理：

- 先备份目标文件到 `.codex-backup/test-h5-pc-youdianse-alias-*`。
- 精确同步本次涉及文件。
- 重建并启动 `ben-bot` 容器。

容器内核验：

```text
h5_new=True
pc_new=True
label=True
ben-bot Up
```

### 3.4 测试宝塔 Nginx

目标：

- `38.92.8.34`
- H5 vhost：`/www/server/panel/vhost/nginx/h5.youdianse-test.xyz.conf`
- PC vhost：`/www/server/panel/vhost/nginx/pc.youdianse-test.xyz.conf`

处理：

- 先备份到 `/www/server/panel/vhost/nginx/.codex-backup/test-h5-pc-youdianse-alias-*`。
- H5 `server_name` 改为：

```text
h5.youdianse-test.xyz test-h5.youdianse-test.xyz sdk.youdianse-test.xyz
```

- PC `server_name` 改为：

```text
pc.youdianse-test.xyz test-pc.youdianse-test.xyz
```

- H5/PC vhost 证书切到已有 `*.youdianse-test.xyz` 通配证书。
- PC 旧 `test-pc-s3.hbabaxb.cn` 反代改回 AWS S3 老地址。
- `nginx -t` 通过并 reload。

## 4. 验证结果

DNS：

```text
test-h5.youdianse-test.xyz -> 38.92.8.34
test-pc.youdianse-test.xyz -> 38.92.8.34
```

HTTPS：

```text
https://test-h5.youdianse-test.xyz/version.json -> 200 ssl=0
https://test-pc.youdianse-test.xyz/version.json -> 200 ssl=0
https://test-h5.youdianse-test.xyz/ -> 200 ssl=0
https://test-pc.youdianse-test.xyz/ -> 200 ssl=0
https://h5.youdianse-test.xyz/version.json -> 200 ssl=0
https://pc.youdianse-test.xyz/version.json -> 200 ssl=0
```

证书：

```text
subject=CN=youdianse-test.xyz
SAN=DNS:*.youdianse-test.xyz, DNS:youdianse-test.xyz
```

页面内容抽查：

```text
H5 AWS S3 域命中: 111
PC AWS S3 域命中: 115
hbbfuub.cn 命中: 0
test-img. 命中: 0
```

远端当前配置残留检查：

```text
旧 test-h5.hb* / test-pc.hb* 页面别名: none
旧 test-pc-s3.hbabaxb.cn: none
```

## 5. 飞机群通知

本次按 workbench 测试环境默认通知目标发送到：

- `18game运维`

已发送阶段通知：

- 步骤 1：上下文读取完成。
- 步骤 2：workbench 和历史 doc 读取、目标确认完成。
- 步骤 3：DNS、证书、宝塔当前配置只读核验完成。
- 步骤 4：本地配置修改和 py_compile 完成。
- 步骤 5：ben-bot 运行机同步、重建和容器内核验完成。
- 步骤 6：宝塔 Nginx server_name 与 PC S3 反代改动完成。
- 步骤 7：新域名 HTTPS 证书问题修复完成。

最终汇总和本文档已发送到同一群。
