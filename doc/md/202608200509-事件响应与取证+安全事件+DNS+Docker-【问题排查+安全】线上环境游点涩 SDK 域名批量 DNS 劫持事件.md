---
id: "doc-01e4955dbea4"
title: "【问题排查+安全】线上环境游点涩 SDK 域名批量 DNS 劫持事件"
date: "2026-08-20T05:09:00"
categories: ["事件响应与取证", "安全事件"]
tags: ["事件响应与取证", "安全事件", "DNS", "Docker", "PHP", "备份恢复", "监控告警", "知识笔记"]
source: "03-安全运营与应急/01-安全事件与取证/游点涩-域名与网关攻击/2026-08-20-0509-【问题排查+安全】线上环境游点涩SDK域名批量DNS劫持事件.md"
---

# 【问题排查+安全】线上环境游点涩 SDK 域名批量 DNS 劫持事件

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608200509-%E4%BA%8B%E4%BB%B6%E5%93%8D%E5%BA%94%E4%B8%8E%E5%8F%96%E8%AF%81%2B%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%2BDNS%2BDocker-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%2B%E5%AE%89%E5%85%A8%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%B8%B8%E7%82%B9%E6%B6%A9%20SDK%20%E5%9F%9F%E5%90%8D%E6%89%B9%E9%87%8F%20DNS%20%E5%8A%AB%E6%8C%81%E4%BA%8B%E4%BB%B6.md)

> 来源：本地项目文档 `game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0509-【问题排查+安全】线上环境游点涩SDK域名批量DNS劫持事件.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

文档日期：2026-08-20 05:09
环境：游点涩线上环境（main 分支）
分类：问题排查+安全
风险等级：E4（紧急）
标签：线上环境、DNS 劫持、SDK 域名、注册商、Cloudflare、安全事件

## 事件概述

用户反馈游点涩 SDK 域名打开被劫持。核验确认 10 个 SDK 域名
（安卓 5 个 + iOS 5 个）于 2026-08-19 16:14 UTC（08-20 00:14 CST）被批量修改 DNS，
解析指向与平台无关的第三方站点。

## 受影响域名

```text
安卓 SDK：bjyinhegame.com、wangcaitt.com、shouyek.com、huochechushou.com、tywhtg.com
iOS：clfhjg.com、caijiesh.com、jszz809.com、xflqzgj.com、baiyingnet.com
```

## 核验证据

```text
1. DNS：9 个域名解析到 Cloudflare（104.21.x / 172.67.x），
   打开为“银河剧场/旺柴短剧”等第三方短剧站；
   xflqzgj.com CNAME -> d1bgdvss2p4aqh.cloudfront.net（CloudFront）；
2. NS：9 个域名为 everton/serena.ns.cloudflare.com，xflqzgj.com 为 share-dns；
3. whois（bjyinhegame.com / wangcaitt.com）：
   Registrar: Gname.com Pte. Ltd.
   Updated Date: 2026-08-19T16:14:23Z / 16:14:28Z（批量修改时间）
   Creation: 2025-09（注册时间较短）
4. 宝塔 new.youdianse.com.conf 均配置这些域名（应指向 203.0.113.1）；
5. 蜜桃乌托邦 APK DEX 内包含 wangcaitt.com / tywhtg.com / shouyek.com /
   huochechushou.com / bjyinhegame.com（即游戏 SDK 包内域名）。
```

## 影响

```text
1. 使用这些 SDK 域名的游戏登录/注册/进游戏失败或被导到劫持页（钓鱼风险）；
2. 与蜜桃/欲女/性界登录失败同源：sdkDomains 或包内 SDK 域名被劫持；
3. 用户访问这些域名可能被第三方短剧站诱导（安全风险）。
```

## 紧急处置（需域名管理员立即执行）

```text
1. 登录 Gname 注册商，恢复 10 个域名 NS 与 A 记录：
   A 记录指向 203.0.113.1（宝塔，与 new.youdianse.com.conf 匹配）；
2. 修改注册商账号密码、开启 2FA、确认注册商锁定；
3. 排查注册商账号是否被盗/域名是否被批量转移；
4. 全量审计平台其它域名 NS/A 记录是否也被改；
5. 平台侧兜底：将 sdkDomains 返回域名切到 h5.18h.game / sdk.youdianse.com。
```

## 后续核查

```text
1. 恢复后逐域名验证：dig A -> 203.0.113.1，curl https 应回到平台；
2. 建议对平台全部域名做 NS/A 记录基线监控与告警；
3. 建议域名注册商账号统一开启 2FA + 转移锁 + 修改锁。
```

## DNS 恢复核查（2026-08-20 05:37 补充）

```text
逐个核验 10 个域名：

已部分恢复（A 已指到网关 203.0.113.1）：
  jszz809.com  A=203.0.113.1  NS 仍 Cloudflare  强制走网关 /api=200，公网仍 404
  xflqzgj.com  A=203.0.113.1  NS share-dns      强制走网关 /api=200，公网 200
  tywhtg.com   A=203.0.113.1  NS 仍 Cloudflare  强制走网关 /api=200，公网仍 404

仍未恢复（A 仍 Cloudflare 劫持 IP）：
  caijiesh.com / baiyingnet.com / bjyinhegame.com / wangcaitt.com /
  shouyek.com / huochechushou.com / clfhjg.com

结论：需在 Gname 把 NS 改回正确权威 DNS 并把 A 统一为
203.0.113.1（宝塔）或 203.0.113.1（网关，已实测可服务 /api）。
```

## 通知记录

```text
紧急 E4 通知（10 个域名被劫持）   message_id 9997
DNS 恢复核查（未全部恢复）        message_id 10083
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、注册商密码。
