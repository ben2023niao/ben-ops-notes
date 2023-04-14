---
id: "doc-74c5db632a3f"
title: "14 zabbix API调用 获取告警介质"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423178.html"
---

# 14 zabbix API调用 获取告警介质

```bash
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"usermedia.get","params":{"output":"extend"},"auth":"91aca8c1fe89c89c2e457ab18a28e79b","id":1 }' http://203.0.113.1/zabbix/api_jsonrpc.php
```
