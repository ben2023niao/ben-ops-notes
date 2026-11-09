---
id: "doc-9fc8d1d6ee74"
title: "【问题排查】线上环境性界大战 iOS 登录/注册与 SDK 域名核验记录"
date: "2026-08-20T04:53:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Redis", "自动化", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0453-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%80%A7%E7%95%8C%E5%A4%A7%E6%88%98iOS%E7%99%BB%E5%BD%95%E6%B3%A8%E5%86%8C%E4%B8%8ESDK%E5%9F%9F%E5%90%8D%E6%A0%B8%E9%AA%8C%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0453-【问题排查】线上环境性界大战iOS登录注册与SDK域名核验记录.md"
sourceSha256: "2548fa8620c24f52de2353e7484302bdc53be171f89cf20ceaf11e3b8f2872a9"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境性界大战 iOS 登录/注册与 SDK 域名核验记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608200453-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BDocker%2BRedis-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E6%80%A7%E7%95%8C%E5%A4%A7%E6%88%98%20iOS%20%E7%99%BB%E5%BD%95-%E6%B3%A8%E5%86%8C%E4%B8%8E%20SDK%20%E5%9F%9F%E5%90%8D%E6%A0%B8%E9%AA%8C%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-20 04:53｜日期依据：文件名日期

文档日期：2026-08-20 04:53
环境：游点涩线上环境（main 分支）
分类：问题排查
标签：线上环境、性界大战、iOS、登录注册、sdkDomains、域名访问策略验证

## 背景

性界大战 iOS App：
- P1：老用户可登录可充值，无法进入游戏；
- P2：新用户无法注册。
要求查询该域名历史登录使用的 SDK 域名。

## 核验结果

### 老用户 zora5367（P1）

```text
登录成功：04:23:13 / 04:35:15，/api/sdk/Login/account status:"y"
链路：h5.18h.game/api（CloudFront -> 网关 -> 宝塔 -> 后端），XFF 含网关 203.0.113.1
登录后客户端还调用 Login/username（注册接口）4 次与 system/gameTrack；
生产注册接口近 3 小时全部 status:"y"
未发现平台侧选服/进游戏调用 -> 进游戏失败在游戏方或被访问策略验证域名侧
```

### SDK 域名下发

```text
生产 /api/sdk/system/sdkDomains 返回：["https://h5.game-app543.com"]
实测 https://h5.game-app543.com/api：
  HTTP 302 -> https://blocked.sbmd.cicc.gov.ph（菲律宾政府网站访问策略验证页）
  跟随重定向 -> 403
数据源：Mongo domain 集合 _id 34（type=main，domain=https://h5.game-app543.com，status=0，缓存 5 分钟）
```

## 结论

```text
1. 登录/充值走内置 h5.18h.game（可用）-> 老用户可登录可充值；
2. 注册/进游戏等走 sdkDomains 下发的 h5.game-app543.com（被菲律宾政府访问策略验证）：
   -> 新用户无法注册（P2）；
   -> 老用户进入游戏相关调用失败（P1）。
```

## 建议修复（需授权）

```text
1. 将 Mongo domain 集合 _id 34（type=main）域名改为 https://h5.18h.game
   （或 https://sdk.youdianse.com，均已接通、未访问策略验证），并清除 Redis 域名缓存（TTL 300s）；
2. 同步排查其它游戏/H5 是否引用被访问策略验证域名 h5.game-app543.com；
3. 发布检查：SDK 域名下发前校验可达性（非 302/访问策略验证页）。
```

## 通知记录

```text
性界大战 iOS 登录/注册与 SDK 域名核验   message_id 9996
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据；测试账号密码仅用于核验。
