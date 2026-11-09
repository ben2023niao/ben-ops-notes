---
id: "doc-a4762f456e95"
title: "运行目录与发布规范 · runtime-and-release"
date: "2026-11-05T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/guides/runtime-and-release.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/guides/runtime-and-release.md"
sourceSha256: "cdb767ca354d5695fc5c66f9b7173cad216b08c40bfdfd1950fada01794beffd"
sourceSystem: "project-doc"
---

# 运行目录与发布规范 · runtime-and-release

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611050000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BPython-%E8%BF%90%E8%A1%8C%E7%9B%AE%E5%BD%95%E4%B8%8E%E5%8F%91%E5%B8%83%E8%A7%84%E8%8C%83%20%C2%B7%20runtime-and-release.md)

> 整理日期：2026-11-05 00:00｜日期依据：正文日期

更新时间：2026-11-05

## 巴西

### 代码打包机 03

```text
主机：192.0.2.20 / 192.0.2.1
目录：/data/pgserver
```

职责：

- 拉取 `ben` 分支业务代码；
- 构建并推送厂家镜像到内网 registry；
- 从 `platform-api/conf/domains/` 准备巴西域名与游戏 ID；
- 从 `platform-api/conf/domains-hk/` 准备香港域名与游戏 ID；
- 准备一份共享 `share.so`；
- 从 `version-bx/` 准备巴西 `server_configs` / `version.json`；
- 从 `version-zh/` 准备香港 `server_configs` / `version.json`；
- 为巴西 01/02 和香港 01/02 提供镜像和配置源。

环境配置目录必须分开：

```text
巴西源：platform-api/conf/domains/
香港源：platform-api/conf/domains-hk/
共享：/data/pgserver/share.so
巴西配置：/data/pgserver/version-bx/{server_configs,version.json}
香港配置：/data/pgserver/version-zh/{server_configs,version.json}

巴西 runtime：/data/server-runtime/conf/domains/
香港 runtime：/data/server-runtime-hk/conf/domains/
```

不要把巴西 `domains` 复制到香港，也不要把香港 `domains-hk` 复制到巴西。
`build.sh` 会分别在两个 runtime 中同步并校验对应目录。

运维控制台支持选择厂家后按固定 4 路动态补位调用单个厂家构建：保持最多 4 个
厂家同时运行，任一厂家完成即补入下一个。每个并发任务使用
独立的临时 `RUNTIME_DIR` / `RUNTIME_HK_DIR`，避免同时覆盖正式域名和配置；
全部厂家成功后才一次性合并到正式 runtime。任一厂家失败时动态队列仍会收完
正在执行的结果，最终以非零退出并阻止 runtime 合并；失败厂家状态和日志保留。

巴西和香港的 `server_configs` / `version.json` 必须分别从 `version-bx`、
`version-zh` 同步。构建脚本逐文件校验来源与目标，并输出
`BRAZIL_RUNTIME_MEvendor_aTA_OK`、`HONGKONG_RUNTIME_MEvendor_aTA_OK` 和
`SHARE_SO_BOTH_ENVS_OK`。

香港 `/data/server-runtime-hk/conf/configs-api.py` 是独立专源，构建合并绝不
写入该文件。香港发布只允许从该专源同步到香港节点，执行前备份节点旧文件，
并校验源文件前后 SHA256、目标 SHA256 三者一致。

### 巴西 01/02/04/05

```text
目录：/data/server-runtime
```

发布顺序：

```text
01 停 -> 从 03 同步 -> 修复并校验结果集权限 -> start
验证 01
02/04/05 循环：停 -> 从 03 同步 -> 修复并校验结果集权限 -> start
逐台验证
```

不得先同时停多台。02/04/05 必须等 01 正常后再批量操作，且批量内任一节点
失败就停止后续节点，保证始终有节点承接 Nginx 流量。

## 香港

### 配置源

```text
源码：03 `/data/pgserver/platform-api/conf/domains-hk/`
运行时：03 `/data/server-runtime-hk/conf/domains/`
```

### 香港 01/02

```text
目录：/data/server-runtime
镜像仓库：192.0.2.20:5000
```

发布顺序：

```text
01 停 -> 同步配置 -> 同步结果集 -> start
验证 01
02 停 -> 同步配置 -> 同步结果集 -> start
验证 02
```

香港从 2026-11-03 起同时运行 vendor_a HTTP（9096）和 vendor_a WS2（8765）。
两者使用同一个 vendor_a 镜像；发布 vendor_a 时仍按 01 验证后 02 的顺序操作。

## 校验

打包前先校验域名与游戏 ID：

```bash
cd /data/pgserver
python3 scripts/validate_domains.py
```

CI 在 `ben` 分支执行相同校验。校验会阻止明显的巴西/香港域名串环境。

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
