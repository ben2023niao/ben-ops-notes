---
id: "doc-f7c4b553b5c9"
title: "【问题排查】线上环境蜜桃与欲女梦工厂登录失败根因：正式包打入测试 SDK 域名"
date: "2026-08-20T03:48:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "Nginx", "自动化", "CDN", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0348-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83%E8%9C%9C%E6%A1%83%E4%B8%8E%E6%AC%B2%E5%A5%B3%E6%A2%A6%E5%B7%A5%E5%8E%82%E7%99%BB%E5%BD%95%E5%A4%B1%E8%B4%A5%E6%A0%B9%E5%9B%A0-%E6%AD%A3%E5%BC%8F%E5%8C%85%E6%89%93%E5%85%A5%E6%B5%8B%E8%AF%95SDK%E5%9F%9F%E5%90%8D.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0348-【问题排查】线上环境蜜桃与欲女梦工厂登录失败根因-正式包打入测试SDK域名.md"
sourceSha256: "c09bca832d86f4d288f44c37a0dc85e6585061b2a3bebb15084bba0f344582eb"
sourceSystem: "project-doc"
---

# 【问题排查】线上环境蜜桃与欲女梦工厂登录失败根因：正式包打入测试 SDK 域名

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-0348-【问题排查】线上环境蜜桃与欲女梦工厂登录失败根因-正式包打入测试SDK域名.md`

> 整理日期：2026-08-20 03:48｜日期依据：文件名日期

文档日期：2026-08-20 03:48
环境：游点涩线上环境（main 分支）
分类：问题排查
标签：线上环境、蜜桃乌托邦、欲女梦工厂、登录失败、SDK 域名、测试环境、重新打包

## 背景

用户提供测试账号（蜜桃：grow5691；欲女梦工厂：gp5219），要求下载 APK 用账号密码实测登录，
并定位“为什么登录不了”。

## 核验过程

### 1. 平台侧（正常）

```text
grow5691：user_id 8799739，is_test=0，生产 /api/sdk/Login/account 返回 status:"y" + token
gp5219：user_id 8614004，is_test=1，checkTokenV2 status:"y"
两个账号无失败登录记录；游戏 244/618 status=1（启用）
```

### 2. APK 解包（根因）

```text
蜜桃乌托邦：d391me9s8n5j5s.cloudfront.net/.../6a82acdfa231e0.49424683-蜜桃乌托邦[g18]_obt02_20260815_1.2.3_release.apk
欲女梦工厂：d391me9s8n5j5s.cloudfront.net/.../6a7f2065bb5760.73622859-1.0.2-pro.apk

两个包的 classes*.dex 中平台 SDK base URL 均为：
  https://sdk.youdianse-test.xyz/   （测试环境，IP 38.92.8.34，HTTPS 200）

生产 SDK 域名（均指向宝塔 16.208.5.147）：
  sdk.youdianse.com / sdk.youdianse-main.xyz / api.youdianse.com / api.youdianse-main.xyz
```

### 3. 实测

```text
用 grow5691 / gp5219 打 sdk.youdianse-test.xyz 登录：
  {"status":"n","error":"数据封装错误!","errorCode":2001}（测试环境非生产账号体系）
生产环境：grow5691 登录成功、gp5219 token 有效。
```

## 根因

```text
蜜桃游戏将蜜桃乌托邦（1.2.3 release，08-15）与欲女梦工厂（1.0.2-pro，08-14）
的正式包打包时，SDK base URL 错误配置为测试环境 sdk.youdianse-test.xyz，
生产账号登录全部打到测试环境，环境账号不匹配导致登录失败。
（欲女梦工厂 App 另有游戏方自己的认证 auth.for-girl.com，属游戏方基础设施。）
```

## 开关核实（2026-08-20 03:52 补充）

```text
客户端包存在“测试/线上 SDK 域名”构建开关（BUILD_TYPE/ENV 类常量），
但本次核实的两个 release 包：
  蜜桃乌托邦 1.2.3 release：全包（1953 文件）中 sdk.youdianse-test.xyz 仅出现 1 次，
    生产 SDK 域名（sdk.youdianse.com / sdk.youdianse-main.xyz / api.youdianse.com）完全不存在；
  欲女梦工厂 1.0.2-pro：同样只有 sdk.youdianse-test.xyz。
结论：开关属于构建期编译选择，该两个包的开关值 = 测试环境（编译时已烘焙进包）。
```

## 处置建议

```text
1. 蜜桃游戏/发行重新打包两个游戏：SDK base URL 改为生产
   sdk.youdianse.com（或 sdk.youdianse-main.xyz / api.youdianse.com）；
2. 核对游戏内 auth.for-girl.com 与平台回调域名指向生产；
3. 平台更新下载链接，用户重装后即可登录；
4. 发布检查加一条：正式包 SDK 域名不得为 test 环境。
5. 出包时确认开关选“线上/生产”后再发正式链接（本次为开关/配置选错环境）。
```

## 线上 SDK 域名接通（2026-08-20 03:56 补充）

```text
直接测试线上 sdk 域名时发现：
  sdk.youdianse.com / sdk.youdianse-main.xyz 原 /api 均 404（生产 SDK 域名未接到后端）

已在宝塔新增 vhost：/www/server/panel/vhost/nginx/sdk.youdianse.com.conf
  server_name sdk.youdianse.com
  SSL：*.youdianse.com 通配证书（ssl.youdianse.com，有效期至 2026-09-09）
  location /(api|channel|customer) -> proxy_pass http://203.0.113.1:8088（Host www.youdianse.com）
  location / -> 404
nginx -t 通过 + reload。

复测：https://sdk.youdianse.com/api/sdk/system/info = 200
      https://sdk.youdianse.com/api/sdk/Login/account = 200（原 404）
登录结果：grow5691 生产登录 status:"y"；gp5219 token 有效。

说明：sdk.youdianse-main.xyz 不在 *.youdianse.com 通配范围内，如需启用需在宝塔补签证书。
回滚：删除 sdk.youdianse.com.conf 并 reload。
```

## 通知记录

```text
步骤 1 根因确认（正式包打入测试 SDK 域名） message_id 9977
步骤 2 处置建议                              message_id 9978
步骤 3 开关核实（该包开关值=测试环境）      message_id 9979
步骤 1（追加）线上 SDK 域名接通并验证       message_id 9980
步骤 2（追加）结论与后续                    message_id 9981
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据；测试账号密码仅用于核验，未写入文档；
APK 临时下载解包后已清理。
