---
id: "doc-b4cd4a8445b2"
title: "测试环境 env 新增 EEP 测试 APK CDN 配置记录"
date: "2026-07-30T16:28:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "CDN", "安全运维", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1628-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83env%E6%96%B0%E5%A2%9EEEP%E6%B5%8B%E8%AF%95APK-CDN%E9%85%8D%E7%BD%AE%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-30-1628-【运维记录】测试环境env新增EEP测试APK-CDN配置记录.md"
sourceSha256: "03f62a0ed8bf7d944c4238763da5c69486bd90fd00568828b44bfd456c40120d"
sourceSystem: "project-doc"
---

# 测试环境 env 新增 EEP 测试 APK CDN 配置记录

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607301628-%E6%B8%B8%E7%82%B9%E6%B6%A9%2BShell%2BDocker-%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%20env%20%E6%96%B0%E5%A2%9E%20EEP%20%E6%B5%8B%E8%AF%95%20APK%20CDN%20%E9%85%8D%E7%BD%AE%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-30 16:28｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-30 16:28
环境：游点涩测试环境（dev 分支）
分类：运维记录

## 背景

根据群内需求，测试环境需要在服务器本地 `env/.env.dev` 新增 EEP 测试 APK CDN 配置。

本次只处理测试环境，不处理线上环境，不提交 `.env` 到 Git。

## 配置段

服务器文件：

```text
/opt/docker-youdianse-php/env/.env.dev
```

新增段名：

```text
[cdn.tencent.eep.prod-apk.zkifae.cn]
```

配置内容：

```text
domain=eep.prod-apk.zkifae.cn
key=已配置，明文仅保存在测试服务器 env/.env.dev，不写入文档和 Git
```

已在 `.env.dev` 中为新增段写入逐行注释：

```text
# ===== EEP 测试 APK CDN 配置（2026-07-30，@Ben_Bird 新增）=====
# 配置段名称：腾讯 CDN 配置组标识，业务按中括号内名称读取。
[cdn.tencent.eep.prod-apk.zkifae.cn]
# domain：CDN 下载域名，只填写域名本体，不带 http/https 协议。
domain=eep.prod-apk.zkifae.cn
# key：该 CDN 配置使用的鉴权密钥，只允许保存在测试服务器 env/.env.dev，不提交 Git。
key=已配置
```

## 备份

修改前已备份：

```text
/opt/docker-youdianse-php/env/.env.dev.bak.eep_prod_apk_20260730_162826
```

## 验证

配置解析：

```text
宿主机解析：OK
web 容器解析：OK
cron 容器解析：OK
```

运行检查：

```text
后台 HTTP：200
业务仓库：/opt/docker-youdianse-php/src/youdianse-php，clean
运维仓库：env/.env.dev 为服务器本地变更，不提交 Git
```

## 安全边界

- 不在文档、Git、Telegram 通知或普通日志中写入 key 明文。
- 不提交 `env/.env.dev`。
- 本配置只用于测试环境。
- 线上环境如需同类配置，应在明确线上变更窗口和审批后，按线上分支/线上服务器单独处理。

## 回滚

如需回滚本次配置：

```bash
cd /opt/docker-youdianse-php
cp -p env/.env.dev.bak.eep_prod_apk_20260730_162826 env/.env.dev
```

回滚后再次执行配置解析和后台 HTTP 检查。
