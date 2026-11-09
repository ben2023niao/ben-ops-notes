---
id: "doc-adfe2b294531"
title: "1 zabbix API调用 认证并取得加密字段"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423118.html"
---

# 1 zabbix API调用 认证并取得加密字段

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BPHP%2BZabbix-1%20zabbix%20API%E8%B0%83%E7%94%A8%20%E8%AE%A4%E8%AF%81%E5%B9%B6%E5%8F%96%E5%BE%97%E5%8A%A0%E5%AF%86%E5%AD%97%E6%AE%B5.md)

![文档配图](../media/34fe8b508622ecea58.png)

```bash
ZUSER="$1"
ZPASSWD="$2"
echo "开始获取令牌"

curl -s -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":
"2.0","method":"user.login","params":{"user":"'$ZUSER'","password":"'$ZPASSWD'"},"auth":
null,"id":0}' https://zabbix.bssrv.com/zabbix/api_jsonrpc.php

echo "成功获取令牌 $AUTH" > session.txt
```
