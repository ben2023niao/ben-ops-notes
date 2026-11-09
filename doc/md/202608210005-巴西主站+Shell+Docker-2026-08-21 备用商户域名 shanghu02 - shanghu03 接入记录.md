---
id: "doc-7ad27dba4b3e"
title: "2026-08-21 备用商户域名 shanghu02 / shanghu03 接入记录"
date: "2026-08-21T00:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "监控告警", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-21-0005-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E5%A4%87%E7%94%A8%E5%95%86%E6%88%B7%E5%9F%9F%E5%90%8Dshanghu02%E4%B8%8Eshanghu03%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-21-0005-【架构改造】备用商户域名shanghu02与shanghu03接入记录.md"
sourceSha256: "485d3a604bae556efd13a7061def721f09fe9bae70f60509620b202606054f2e"
sourceSystem: "project-doc"
---

# 2026-08-21 备用商户域名 shanghu02 / shanghu03 接入记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-08-21-0005-【架构改造】备用商户域名shanghu02与shanghu03接入记录.md`

> 整理日期：2026-08-21 00:05｜日期依据：文件名日期

时间：2026-08-21 00:05（Asia/Manila）
项目：某业务公司 / PGServer master
范围：备用商户域名 socket.shanghu02.cc / socket.shanghu03.cc 接入（参考 socket.shanghu01.cc）
执行人：Codex（本地工作区 + 宝塔 + 备用 nginx + Cloudflare API）

## 背景

```text
商户 API 域名已统一为独立商户域名体系（shanghu01.cc）。
用户单独购买 shanghu02.cc / shanghu03.cc 作为备用商户域名，要求参考 socket.shanghu01.cc 接入，
与主域名同等可用，避免单一商户域名单点故障。
```

## 处理

```text
1. Cloudflare：
   - shanghu02.cc（zone id 060f...，初始 pending）与 shanghu03.cc（zone id a336...，active）
     均已接入本 Cloudflare 账户（NS bjorn/romina）；
   - 两个 zone 均新增 A 记录 socket -> 192.0.2.8（橙云 proxied，TTL auto）；
   - 等待注册商 NS 委托传播，DNS 生效后解析到 Cloudflare 边缘。
2. 宝塔：socket 站点 server_name 由单域名扩展为
   socket.shanghu01.cc socket.shanghu02.cc socket.shanghu03.cc；
   nginx -t 通过并 reload；原文件备份 .bak-20260820-shanghu23。
3. 备用机：/etc/nginx/conf.d/socket.xtmpz.com.conf 同样扩展并 reload。
4. 监控扩展（docker/scripts/entry_health_monitor.py）：
   - 每个商户域名 4 个关键接口探测（Register/Login/QueryBalance/GameLogs，
     200/400/401/403 视为链路正常）；
   - 3 个域名共 12 项 socket 探测，总检查数 25 项；备用机 cron 已同步。
```

## 验证

```text
1. 公网 Register：socket.shanghu01.cc / shanghu02.cc / shanghu03.cc 全部 400
   （“missing params p” 业务校验，链路正常）；
2. 系统 resolver 确认三域名均解析到 Cloudflare 边缘 IP；
3. 备用机运行监控脚本：25 项检查 OK（无报警）；
4. 宝塔/备用机 nginx -t 全部通过。
```

## 结论

```text
商户 API 域名现为 3 个独立域名（shanghu01 主 + shanghu02/03 备用），均回源宝塔 192.0.2.8，
任一域名异常可通过入口监控第一时间报警，备用域名可即时接管。
```

## 最后安全点 / 建议

```text
本地 master：ae88a0f6（本次本地 Commit 后更新；未 Push；origin= b3083550）。
建议：后续新增商户域名统一在 shanghu0x.cc 体系下，同步 socket 站点 server_name 与监控 URLS。
```
