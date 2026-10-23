---
id: "doc-5df7f03e2946"
title: "香港 cn 分支导入说明"
date: "2026-10-24T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "CDN", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/hongkong/cn/SOURCE.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/SOURCE.md"
sourceSha256: "eba28d622b4d120560eac176b8f2b84b171e8483d6aab95ea406cd9f3697a38e"
sourceSystem: "project-doc"
---

# 香港 cn 分支导入说明

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/SOURCE.md`

> 整理日期：2026-10-24 00:00｜日期依据：正文日期

来源分支：`origin/cn`
来源提交：`5c3b3de6a5beef52aa9c8f152366e9650503610f`
导入日期：2026-10-24

导入内容：

- `docker/doc/*` 香港历史记录；
- `docker/conf/domains/*` 香港域名源配置；
- `docker/deploy/hongkong/*` 香港 Cloudflare/AWS 工具和 Nginx 源配置；
- `docker/README.md` 的香港说明。

导入时只复制文件，不切换当前 `master`，不修改 `ben`/`cn` 远端分支。
线上实时配置与 `cn` 分支存在差异时，以线上为准。
