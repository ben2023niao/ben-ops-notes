---
id: "doc-af358334677a"
title: "8 zabbix API调用 获取指定时间点的值数据"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423163.html"
---

# 8 zabbix API调用 获取指定时间点的值数据

```bash
curl -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc": "2.0","method":"history.get","params":{"history":0,"itemids":["23902"],"time_from":"1398873600","time_till":"1399046400","output":"extend","filter":{"clock":"1399026180"}},"auth": "91aca8c1fe89c89c2e457ab18a28e79b","id": 0}' http://203.0.113.1/zabbix/api_jsonrpc.php
```
