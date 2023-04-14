---
id: "doc-c510ac0a8b64"
title: "2 zabbix API调用 获取指定主机hostids"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423123.html"
---

# 2 zabbix API调用 获取指定主机hostids

```bash
curl -s -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc": "2.0","method":"host.get","params":{"output":["hostid"],"filter": {"host":"203.0.113.1"}},"auth": "b61b7168931be1065cd722ab44e32d2a","id": 0}' https://zabbix.bssrv.com/zabbix/api_jsonrpc.php
```
