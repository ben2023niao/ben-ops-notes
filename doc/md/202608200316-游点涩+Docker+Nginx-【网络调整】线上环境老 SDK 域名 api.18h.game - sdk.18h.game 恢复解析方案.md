---
id: "doc-731436a5f583"
title: "【网络调整】线上环境老 SDK 域名 api.18h.game / sdk.18h.game 恢复解析方案"
date: "2026-08-20T03:16:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "CDN", "DNS", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0316-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E8%80%81SDK%E5%9F%9F%E5%90%8Dapi.18h.game%E4%B8%8Esdk.18h.game%E6%81%A2%E5%A4%8D%E8%A7%A3%E6%9E%90%E6%96%B9%E6%A1%88.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0316-【网络调整】线上环境老SDK域名api.18h.game与sdk.18h.game恢复解析方案.md"
sourceSha256: "ebb6f6af8089becbf21038e489e41ca4783713da40e4d10c6c940b89abc2291a"
sourceSystem: "project-doc"
---

# 【网络调整】线上环境老 SDK 域名 api.18h.game / sdk.18h.game 恢复解析方案

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0316-【网络调整】线上环境老SDK域名api.18h.game与sdk.18h.game恢复解析方案.md`

> 整理日期：2026-08-20 03:16｜日期依据：文件名日期

文档日期：2026-08-20 03:16
环境：游点涩线上环境（main 分支）
分类：网络调整
标签：线上环境、DNS、老SDK、api.18h.game、sdk.18h.game、GoDaddy、宝塔、Let's Encrypt

## 背景

蜜桃、欲女梦工厂、淫欲斗罗等游戏仍无法登录，平台全链路核验健康后，剩余风险定位为
老版本 SDK 配置的 API 域名失效。实测确认：

```text
api.18h.game   —— 无 DNS 解析（NXDOMAIN）
sdk.18h.game   —— 无 DNS 解析（NXDOMAIN）
api.youdianse.com —— 有解析（16.208.5.147）但直连 https 返回 000（无证书/站点匹配），
                    带 Host: www.youdianse.com 才 200（同为“死记录”）
正常链路：h5.18h.game/api、www.youdianse.com/api（CloudFront/网关 -> 宝塔 -> 后端 8088）
```

老 SDK 无论配置上述三个域名中的哪个，登录请求都会在 DNS/TLS 层失败 → “网络连接失败”。

## 恢复方案

### 1. DNS（GoDaddy 控制台，18h.game 区域）

```text
主机记录：api   类型：A   值：16.208.5.147（宝塔）   TTL：600
主机记录：sdk   类型：A   值：16.208.5.147（宝塔）   TTL：600
```

若老包使用 api.youdianse.com：在 youdianse.com 区域加/改
`api A 16.208.5.147`（记录已存在，但需补证书与站点，见下）。

### 2. 证书（宝塔面板）

```text
等待 DNS 生效（dig api.18h.game 能解析后）
宝塔面板 -> 网站 -> 对应站点（new.youdianse.com 或新建站点）-> SSL -> Let's Encrypt
-> 勾选 api.18h.game、sdk.18h.game 申请证书（HTTP-01 验证，解析指向宝塔即可通过）
```

### 3. 宝塔站点/代理

```text
把 api.18h.game、sdk.18h.game 加入 new.youdianse.com.conf 的 server_name：
该站点扩展配置已包含 location ~ ^/(api|channel|customer)(/|$) -> proxy_pass http://203.0.113.1:8088
加入后 nginx -t && nginx -s reload
```

### 4. 验证

```text
curl -X POST https://api.18h.game/api/sdk/system/info -H 'Content-Type: application/json' -d '{}' -> 200
故障游戏（蜜桃/欲女梦工厂/淫欲斗罗）重新登录/选服/支付测试
```

### 5. 备选方案

```text
推动游戏更新 SDK，API base 改用 h5.18h.game/api 或 www.youdianse.com/api（推荐长期方案）。
```

## 执行分工

```text
DNS 记录：由域名管理员（Ben/发行）在 GoDaddy 控制台添加。
证书+站点：授权后由运维在宝塔侧执行（本方案文档化，待授权）。
```

## 通知记录

```text
步骤 1 确认 api/sdk 三个候选域名均为死记录   message_id 9964
步骤 2 老 SDK 域名恢复解析方案              message_id 9965
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据、.env 敏感值。
