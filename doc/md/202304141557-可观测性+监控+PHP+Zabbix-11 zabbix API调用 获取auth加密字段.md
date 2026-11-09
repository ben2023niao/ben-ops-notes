---
id: "doc-a6dbe4733769"
title: "11 zabbix API调用 获取auth加密字段"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423170.html"
---

# 11 zabbix API调用 获取auth加密字段

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BPHP%2BZabbix-11%20zabbix%20API%E8%B0%83%E7%94%A8%20%E8%8E%B7%E5%8F%96auth%E5%8A%A0%E5%AF%86%E5%AD%97%E6%AE%B5.md)

```bash
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"user.authenticate","params":{"user":"admin","password":"zabbix"},"auth":null,"id":0}' http://203.0.113.1/zabbix/api_jsonrpc.php

将"method":"user.authenticate"改成"method":"user.login";
```
