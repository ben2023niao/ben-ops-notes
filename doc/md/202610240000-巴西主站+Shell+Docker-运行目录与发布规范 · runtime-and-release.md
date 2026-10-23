---
id: "doc-d6275e3ce076"
title: "运行目录与发布规范 · runtime-and-release"
date: "2026-10-24T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/pgserver/master/docs/guides/runtime-and-release.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/guides/runtime-and-release.md"
sourceSha256: "b7270b0704f181e46dd2b5ab083eb414b230d8c50fd0f3095a0f7e6417643bed"
sourceSystem: "project-doc"
---

# 运行目录与发布规范 · runtime-and-release

> 来源文件：`~/Projects/work/game/pgserver/master/docs/guides/runtime-and-release.md`

> 整理日期：2026-10-24 00:00｜日期依据：正文日期

更新时间：2026-10-24

## 巴西

### 代码打包机 03

```text
主机：34.39.180.82 / 203.0.113.1
目录：/data/pgserver
```

职责：

- 拉取 `ben` 分支业务代码；
- 构建并推送厂家镜像到内网 registry；
- 准备 `share.so`、`version.json`、`server_configs`、域名配置；
- 为巴西 01/02 和香港 01/02 提供镜像和配置源。

### 巴西 01/02

```text
目录：/data/server-runtime
```

发布顺序：

```text
01 停 -> 从 03 同步 -> start
验证 01
02 停 -> 从 03 同步 -> start
验证 02
```

不得先同时停两台。02 必须等 01 正常后再操作。

## 香港

### 配置源

```text
巴西 03：/data/server-runtime-hk
```

### 香港 01/02

```text
目录：/data/server-runtime
镜像仓库：34.39.180.82:5000
```

发布顺序：

```text
01 停 -> 同步配置 -> 同步结果集 -> start
验证 01
02 停 -> 同步配置 -> 同步结果集 -> start
验证 02
```

香港不启动 TADA HTTP 主服务，只启动 TADA WS2。

## 校验

每台后端启动后必须检查：

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'
md5sum /data/server-runtime/share.so
cat /data/server-runtime/version.json
```

按选择厂家检查容器名和端口。发现失败先停止后续机器操作。

## CDN

巴西：

```text
Cloudflare Worker -> GCS
```

香港：

```text
CloudFront -> 私有 S3
```

改 Worker 前必须先备份线上版本。清静态缓存后必须从目标区域验证，避免国家白名单或地区网络造成误判。
