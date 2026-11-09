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

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610240000-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BDocker%2BNginx-%E9%A6%99%E6%B8%AF%20cn%20%E5%88%86%E6%94%AF%E5%AF%BC%E5%85%A5%E8%AF%B4%E6%98%8E.md)

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
