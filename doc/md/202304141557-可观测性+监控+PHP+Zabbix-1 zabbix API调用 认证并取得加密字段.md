---
id: "doc-adfe2b294531"
title: "1 zabbix API调用 认证并取得加密字段"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423118.html"
---

# 1 zabbix API调用 认证并取得加密字段

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
