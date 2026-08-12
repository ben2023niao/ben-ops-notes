---
id: "doc-46ba2dbe29e9"
title: "全部域名 UA 分流改造与 syyhslzp 回源问题"
date: "2026-08-12T11:40:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "CDN", "DNS", "故障排查", "数据库恢复"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1140-%E3%80%90%E9%85%8D%E7%BD%AE%E5%8F%98%E6%9B%B4%2B%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%E3%80%91%E5%85%A8%E9%83%A8%E5%9F%9F%E5%90%8DUA%E5%88%86%E6%B5%81%E4%B8%8Esyyhslzp%E5%9B%9E%E6%BA%90%E9%97%AE%E9%A2%98.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1140-【配置变更+验证记录】全部域名UA分流与syyhslzp回源问题.md"
sourceSha256: "d8397a59d019f4552f5982e0aecf89526fced5afafa42c6793dd9f8b8fb84608"
sourceSystem: "project-doc"
---

# 全部域名 UA 分流改造与 syyhslzp 回源问题

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-12_1140-【配置变更+验证记录】全部域名UA分流与syyhslzp回源问题.md`

> 整理日期：2026-08-12 11:40｜日期依据：文件名日期

环境标签：线上环境 / 前端域名维护 / nginx / 16.208.38.88 / AWS CloudFront

时间：2026-08-12 11:40（Asia/Manila）

## 背景

用户要求全部域名按设备分流：手机打开显示 H5，电脑打开显示 PC（包括 taokju.com / tianxidlj.com / trusoundsedu.com 等老 H5 域名）。

## 变更

1. `20-youdianse-prod-unified.conf`：移除 `if ($scheme = http) return 301 https://...`（CloudFront 用 HTTP 回源时导致 301 循环；恢复合并前“80 直接反代”行为）。
   - 备份：`/root/.codex-backup/20-youdianse-prod-unified.conf.pre-remove-http-redirect.bak`
2. `10-youdianse-prod-maps.conf`：`$h5pc_mode` 默认值 `h5` → `ua`，全部域名默认按 UA 分流（手机→3003 H5、电脑→3004 PC）；`pc.*` 保持固定 PC，`yds-pc-h5-*` 跳转类保持 redirect。
   - 备份：`/root/.codex-backup/10-youdianse-prod-maps.conf.pre-ua-default.bak`

均 `nginx -t` 通过后 reload。

## 验证结果

### 公网（经 CloudFront，手机 UA / 电脑 UA 分别请求 version.json）

| 域名 | 手机 | 电脑 |
| --- | --- | --- |
| taokju.com | H5 ✅ | PC ✅ |
| tianxidlj.com | H5 ✅ | PC ✅ |
| trusoundsedu.com | H5 ✅ | PC ✅ |
| shouyek.com | H5 ✅ | PC ✅ |
| shyssjt.com | H5 ✅ | PC ✅ |
| syyhslzp.com | PC ❌ | PC ✅ |

### 直连源站 16.208.38.88:443（手机/电脑 UA）

| 域名 | 手机 | 电脑 |
| --- | --- | --- |
| 118acs2.com | H5 ✅ | PC ✅ |
| ydsgames.com | H5 ✅ | PC ✅ |
| youdianse.one | H5 ✅ | PC ✅ |
| h5.youdianse.com | H5 ✅ | PC ✅ |
| www.youdianse.com | H5 ✅ | PC ✅ |

### 跳转类不受影响

- `yds-pc-h5-01.cc` 手机 UA → 301 `https://h5.yds-pc-h5-01.cc/` ✅
- `pc.yds-pc-h5-01.cc` → 200 PC ✅

## syyhslzp.com 问题（未随本次解决）

- 抓包确认：syyhslzp.com 的 CloudFront 回源时把 User-Agent 改写为 `Amazon CloudFront`，源站无法识别真实设备，默认按 PC 处理 → 手机用户也拿到 PC。
- 其余 5 个域名（taokju/tianxidlj/trusoundsedu/shouyek/shyssjt）的 CloudFront 均转发真实 UA，故分流正常。
- 修复选项（需用户决策）：
  1. 域名侧：把 syyhslzp.com 的 DNS A 记录改为直连 `16.208.38.88`（绕过该 CloudFront），UA 分流即可生效（已验证直连手机→H5、电脑→PC）。
  2. CF 账号侧：在该 Distribution 的回源策略里转发/保留 User-Agent（当前账号不可操作）。

## 结论

- 服务器侧已完成全部域名 UA 分流改造，除 syyhslzp.com（CF 改写 UA）外，其余域名公网手机/电脑分流均正常。
