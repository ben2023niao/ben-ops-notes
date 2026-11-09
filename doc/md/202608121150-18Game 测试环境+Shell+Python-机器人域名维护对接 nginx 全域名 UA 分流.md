---
id: "doc-f5a37995e104"
title: "机器人域名维护对接 nginx 全域名 UA 分流"
date: "2026-08-12T11:50:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1150-%E3%80%90%E9%85%8D%E7%BD%AE%E5%90%8C%E6%AD%A5%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4%E5%AF%B9%E6%8E%A5nginx%E5%85%A8%E5%9F%9F%E5%90%8DUA%E5%88%86%E6%B5%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1150-【配置同步+验证记录】机器人域名维护对接nginx全域名UA分流.md"
sourceSha256: "71ffc7c9470c7e138eaf1945e54b3f62384c5837f13906483372eb1bcfdf3f83"
sourceSystem: "project-doc"
---

# 机器人域名维护对接 nginx 全域名 UA 分流

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608121150-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%9F%9F%E5%90%8D%E7%BB%B4%E6%8A%A4%E5%AF%B9%E6%8E%A5%20nginx%20%E5%85%A8%E5%9F%9F%E5%90%8D%20UA%20%E5%88%86%E6%B5%81.md)

> 整理日期：2026-08-12 11:50｜日期依据：文件名日期

环境标签：通用 / ben-bot / 前端域名维护 / 16.208.38.88

时间：2026-08-12 11:50（Asia/Manila）

## 背景

服务器 nginx 已改为全部域名默认按设备 UA 分流（`10-youdianse-prod-maps.conf` 的 `$h5pc_mode` 默认 `h5`→`ua`；`20-youdianse-prod-unified.conf` 移除 http 强制 301）。机器人域名维护脚本需要同步对齐，否则快速检查显示的模式、新增域名写入的模式会与 nginx 实际不一致。

## 变更

`youdianse_domain_maint.py`（服务器 `/usr/local/bin/youdianse-domain-maint.py`）：

1. `mode_of`：默认模式 `h5` → `ua`（与 maps 默认一致），并移除旧的 h5./www. 特殊处理；`pc.*` 仍固定 `pc`，显式条目优先。
2. `add_domain`：新增域名时 `h5` 类型显式写 `h5.<域名> h5`、`pc` 类型显式写 `pc.<域名> pc`（不再依赖已改变的默认值），`redirect`/`ua` 照旧写模式。

备份：`/root/.codex-backup/youdianse-domain-maint.py.pre-ua-default.bak`

## 验证

### check --quick --json（模式与 nginx 实际一致）

| 域名 | 模式 |
| --- | --- |
| taokju.com | ua ✅ |
| h5.youdianse.com | ua ✅ |
| www.youdianse.com | ua ✅ |
| 118acs2.com | ua ✅ |
| shouyek.com | ua ✅ |
| pc.yds-pc-h5-01.cc | pc ✅ |
| yds-pc-h5-01.cc | redirect ✅ |

### add --dry-run（显式模式写入）

- `--type h5` → 将新增 `h5.demo-h5-test.com h5`
- `--type pc` → 将新增 `pc.demo-pc-test.com pc`
- `--type ua` → 将新增 `demo-ua-test.com ua`

## 影响

- 机器人快速检查的“模式”列：老 H5 根域名/子域名现在显示 `UA适配`，与 nginx 实际分流一致。
- 新增域名语义不变：h5 类型=纯 H5（h5.* 显式 h5）、pc 类型=纯 PC、ua 类型=按设备分流、redirect=设备跳转。
