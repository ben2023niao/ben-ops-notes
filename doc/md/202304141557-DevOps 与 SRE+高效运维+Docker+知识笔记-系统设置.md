---
id: "doc-0524bc521827"
title: "系统设置"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Docker", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650044.html"
---

# 系统设置

## 介绍

除了页面上对系统设置的管理，`Spug` 还提供了 `manage.py set` 命令可用于通过命令行进行管理操作。

## 禁用登录MFA

当某些特殊情况下可通过 `manage.py set mfa disable` 命令禁用MFA，用法示例如下

```
cd spug/spug_api
source venv/bin/activate
python manage.py set mfa disable
```

Docker 安装的可以执行如下命令

```bash
docker exec spug python3 /data/spug/spug_api/manage.py set mfa disable
```
