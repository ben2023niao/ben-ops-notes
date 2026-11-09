---
id: "doc-2ed07143685b"
title: "2026-08-27 香港 CloudFront 禁用 IPv6 与巴西 Cloudflare 待办记录"
date: "2026-08-27T13:33:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "自动化", "CDN", "DNS", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-08-27-1333-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E9%A6%99%E6%B8%AFCloudFront%E7%A6%81%E7%94%A8IPv6%E4%B8%8E%E5%B7%B4%E8%A5%BFCF%E5%BE%85%E5%8A%9E%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-08-27-1333-【网络调整】香港CloudFront禁用IPv6与巴西CF待办记录.md"
sourceSha256: "78d8b047c9d14739f19a8f6f0c655a69cd27e1a47fe69a9045be88f612dd00ca"
sourceSystem: "project-doc"
---

# 2026-08-27 香港 CloudFront 禁用 IPv6 与巴西 Cloudflare 待办记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608271333-%E9%A6%99%E6%B8%AF%20CN%2BDocker%2B%E8%87%AA%E5%8A%A8%E5%8C%96-2026-08-27%20%E9%A6%99%E6%B8%AF%20CloudFront%20%E7%A6%81%E7%94%A8%20IPv6%20%E4%B8%8E%E5%B7%B4%E8%A5%BF%20Cloudflare%20%E5%BE%85%E5%8A%9E%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-27 13:33｜日期依据：文件名日期

时间：2026-08-27 13:33（Asia/Manila）
项目：某业务公司 / PGServer cn（香港入口）+ 巴西域名
范围：全部域名改为仅走 CDN IPv4、不发布/不解析 IPv6（AAAA）
执行人：Codex（本地工作区 + 香港入口机 192.0.2.14 + 宝塔 192.0.2.8）

## 任务边界

用户要求：

```text
现在域名全部上的 CF，需要到 CDN 设置一下，全部走 CDN 的 IPv4、不要走 IPv6；
示例：pg-games.hkcloudplay03.com 解析出 IPv6（2409:8924:...），要全部改为 IPv4；
访问策略验证 IPv6；香港和巴西所有都一样处理；
固定流程：状态检查 -> doc/workbench -> 每步群通知 -> 验证 -> 文档 -> 汇总发群 -> 本地提交（不 Push）。
```

## 一、调查结论

```text
香港：域名均为 DNS-only CNAME -> CloudFront；zone 无 AAAA 记录；
  公网解析（192.0.2.30/192.0.2.31）返回 CloudFront IPv6（2600:9000 段），
  即 IPv6 来自 CloudFront 分配本身（IsIPV6Enabled=True）。
巴西：动态域名 A 记录 proxied=True（走 Cloudflare CDN），
  公网解析返回 Cloudflare IPv6（2606:4700 段），即 CF 自动 AAAA；
  静态域名 proxied=False（A -> Google LB），无 CF AAAA。
Cloudflare token 权限：香港 cf-api token 与巴西 token 均只有 Zone Read + DNS Edit，
  Zone Settings（ipv6）读取/修改返回 403，无法通过 API 关闭 CF IPv6。
```

## 二、香港执行（已完成并验证）

```text
1. 枚举香港全部 CloudFront 分配：16 个，全部 IsIPV6Enabled=True：
   pg-static(E2JLARIGDV5VZV) / pg3(E1MELSI31IM0FQ) / pg4(E310K7HLRALCN8) /
   pg5(EAUVKSKQC1239) / pp(E2B947FD8LP93P) / ppk(E358927OQC0NKV) /
   vendor_d(E11FJTU4P1WOTI) / vendor_c(E1U27HV4LQHIE2) / g759(E2GEOW3X246399) /
   vendor_b-static(E2KICAEYOWJ24E) / vendor_b-static1(EIKLXE4BT0I05) / vendor_b-static2(E38M63JF95BKAL) /
   vendor_a-statics(E361R7YAZ3ABQG) / vendor_a-statics1(E4V8D7TI5QGAZ) / vendor_a-statics2(E3W3NP8TT0BQ5B) /
   dynamic(E3QV4VIGTRVCVD)。
2. 批量修改 DistributionConfig.IsIPV6Enabled=False（get-distribution-config + update-distribution）。
3. 全部 Deployed。
4. 验证：
   - 配置确认 ipv6=False、状态 Deployed；
   - AAAA 消失：pg-games.hkcloudplay03.com / g759-static / pp-static / vendor_b-static / api.hkplaycore.com
     公网解析只剩 CNAME，无 AAAA 地址（192.0.2.30 与 192.0.2.31 均确认）；
   - IPv4 正常：A 记录正常，curl -4 访问 200/404（应用自身状态）。
```

## 三、巴西待办（需 Cloudflare 面板或更高权限 token）

```text
需要把以下 15 个 zone 的 “IPv6 Compatibility” 关闭（Network -> IPv6 Compatibility -> Off），
关闭后 proxied 记录不再自动发布 AAAA，全部走 IPv4：

playgame-api.vip
playgameserver.com
q7m9v8.icu
qv9m8.icu
shanghu01.cc / shanghu02.cc / shanghu03.cc
t6qv8m.icu
vendor_a-cdn-2026.icu / vendor_a-cdn-game.icu
vendor_a-cf-2026.cyou / vendor_a-cf-game.cyou
vendor_a-host-2026.icu / vendor_a-host-game.icu
xqv9m8.icu

说明：
  - 现有 Cloudflare token（香港 cf-api 与巴西 某业务公司 DNS 切换）无 Zone Settings 权限，API 修改返回 403；
  - 若提供具备 Zone Settings Edit 的 token，可按同样方式批量处理；
  - 主巴西游戏域名（bizopsplus999.com / xtmpz.com）不在当前 token 可见 zone 列表，需确认其所在账号。
```

## 飞机群通知 message_id

```text
4090：步骤 1/4 调查结论与方案
4092：步骤 2/4 枚举结果（16 个分配）
4093：步骤 3/4 修改已提交
4094：步骤 4/4 验证通过（香港）
4095：巴西处理说明
4096：最终汇总
4097：文档附件
4098：提交结果
```

## 回滚 / 遗留事项

```text
回滚：香港如需恢复 IPv6，将 16 个分配 IsIPV6Enabled 改回 True 并等待 Deployed。
遗留：
  - 巴西 15 个 zone 的 IPv6 Compatibility 关闭需面板操作或更高权限 token；
  - 主巴西游戏域名（bizopsplus999.com / xtmpz.com）账号归属待确认。
```
