---
id: "doc-a6dbe4733769"
title: "11 zabbix API调用 获取auth加密字段"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423170.html"
---

# 11 zabbix API调用 获取auth加密字段

```bash
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"user.authenticate","params":{"user":"admin","password":"zabbix"},"auth":null,"id":0}' http://203.0.113.1/zabbix/api_jsonrpc.php

将"method":"user.authenticate"改成"method":"user.login";
```
