---
id: "doc-85b0a4b8ff30"
title: "5 zabbix API调用 获取指定主机itemids"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423154.html"
---

# 5 zabbix API调用 获取指定主机itemids

```bash
curl -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc": "2.0","method":"item.get","params":{"output":["itemids"],"hostids":"10119"},"auth": "91aca8c1fe89c89c2e457ab18a28e79b","id": 0}' https://zabbix.bssrv.com/zabbix/api_jsonrpc.php
```
