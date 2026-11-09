---
id: "doc-bd772a902980"
title: "3 zabbix API调用 获取所有主机hostids"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423141.html"
---

# 3 zabbix API调用 获取所有主机hostids

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BPHP%2BZabbix-3%20zabbix%20API%E8%B0%83%E7%94%A8%20%E8%8E%B7%E5%8F%96%E6%89%80%E6%9C%89%E4%B8%BB%E6%9C%BAhostids.md)

```bash
curl -s -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc": "2.0","method":"host.get","params":{"output":["hostid"]},"auth": "b61b7168931be1065cd722ab44e32d2a","id": 0}' https://zabbix.bssrv.com/zabbix/api_jsonrpc.php
```
