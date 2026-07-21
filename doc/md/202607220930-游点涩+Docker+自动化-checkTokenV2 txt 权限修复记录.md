---
id: "doc-c4354ca77ca7"
title: "checkTokenV2 txt 权限修复记录"
date: "2026-07-22T09:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0930-%E3%80%90%E4%BF%AE%E5%A4%8DBug%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83checkTokenV2-txt%E6%9D%83%E9%99%90%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0930-【修复Bug】测试环境checkTokenV2-txt权限修复记录.md"
sourceSha256: "8a34870a4a70a239eed2b933270144358c94c00e55b9447c27c511e8d70a50a0"
sourceSystem: "project-doc"
---

# checkTokenV2 txt 权限修复记录

> 来源文件：`~/Projects/work/game/youdianse-docker/dev/docker-youdianse-php/docs/2026-07-22-0930-【修复Bug】测试环境checkTokenV2-txt权限修复记录.md`

> 整理日期：2026-07-22 09:30｜日期依据：文件名日期

环境标签：测试环境

文档日期：2026-07-22
环境：游点涩测试环境（dev 分支）
分类：修复Bug

## 现象

`/customer/other/checkTokenV2` 返回：

```json
{"status":"n","error":"Service Error!","errorCode":4002}
```

业务日志显示：

```text
check_host_sign_failed / decrypt_host_sign_empty / platform=forgirl
```

## 根因

容器内 `alb_white_secret.txt` 曾为：

```text
root:root 0600
```

PHP-FPM worker 使用 `www-data` 用户运行。该权限下，业务代码中 `is_file()` 可以判断文件存在，但 `file()` 无法读取文件内容，导致平台私钥读取为空，进而 `host_sign` 解密失败。

`alb_white.txt` 当时为 `0644`，`www-data` 可读；问题集中在 `alb_white_secret.txt` 的容器内可读权限。

## 修复

运维仓库提交：

```text
6ed8043 Fix protected txt readability in containers
```

web 和 cron 容器启动时，对两份保护文件执行权限修正：

```text
chgrp www-data alb_white.txt alb_white_secret.txt
chmod 0640 alb_white.txt alb_white_secret.txt
```

这样保持文件不公开为 `0644`，同时允许 PHP-FPM / PHP CLI 所在的 `www-data` 组读取。

补充文档提交：

```text
27f0da9 Document protected txt container permissions
```

## 验证

Webhook 自动发布成功。

容器内权限：

```text
alb_white.txt owner=root:www-data mode=640
alb_white_secret.txt owner=root:www-data mode=640
```

使用 `www-data` 身份验证：

```text
alb_white.txt readable=yes file=ok
alb_white_secret.txt readable=yes file=ok
```

使用当前测试环境 `forgirl` 私钥重新生成符合接口编码规则的 `host_sign` 后，`checkTokenV2` 返回：

```json
{"code":200,"msg":"success","status":"y"}
```

## 复测说明

服务端 txt 文件存在性和容器内可读权限已恢复，可以通知测试和发行重新测试。

如果复用旧 curl 仍返回 `4002`，需要确认请求中的 `host_sign` 是否由当前测试环境对应平台私钥重新生成。旧的、过期的或使用其他环境私钥生成的 `host_sign` 仍会被业务正常拒绝。
