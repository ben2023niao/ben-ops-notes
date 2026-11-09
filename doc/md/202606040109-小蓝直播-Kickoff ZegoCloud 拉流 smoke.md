---
id: "doc-85b2b8d996f5"
title: "Kickoff ZegoCloud 拉流 smoke"
date: "2026-06-04T01:09:00+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "小蓝直播"]
tags: ["小蓝直播"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Projects/work/game/xiaolan-watches/dev/apps/web/docs/zego-play-smoke.html"
sourcePath: "~/Projects/work/game/xiaolan-watches/dev/apps/web/docs/zego-play-smoke.html"
sourceSha256: "41309cf7dca45f3d604aa31808b40bb5ca2130fa09a9bf8f44fc71820a74fc10"
sourceSystem: "project-doc"
---

# Kickoff ZegoCloud 拉流 smoke

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202606040109-%E5%B0%8F%E8%93%9D%E7%9B%B4%E6%92%AD-Kickoff%20ZegoCloud%20%E6%8B%89%E6%B5%81%20smoke.md)

> 整理日期：2026-06-04 01:09｜日期依据：文件创建/修改时间

步骤:
 **① 主播在 admin 后台对某 room 调 StartLive 后**,
 **② 在下面输 room_id 点【拉流】**,
 **③ 看下面视频框出图 + Console 无 error** 即完整链路通。
 后端只验证到协议层(curl 返回 schema 正确),端到端拉流需要本页面真跑一遍。

API Base

room_id

拉流
停止

### 响应参数

### 视频

### Console 日志

```

```
