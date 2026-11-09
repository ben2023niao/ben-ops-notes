---
id: "doc-d5bea7bd8ef0"
title: "13 zabbix API调用 获取zabbix系统中以定义了的macro"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423176.html"
---

# 13 zabbix API调用 获取zabbix系统中以定义了的macro

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BPHP%2BZabbix-13%20zabbix%20API%E8%B0%83%E7%94%A8%20%E8%8E%B7%E5%8F%96zabbix%E7%B3%BB%E7%BB%9F%E4%B8%AD%E4%BB%A5%E5%AE%9A%E4%B9%89%E4%BA%86%E7%9A%84macro.md)

```bash
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"usermacro.get","params":{"output":"extend"},"auth":"91aca8c1fe89c89c2e457ab18a28e79b","id":1 }' http://203.0.113.1/zabbix/api_jsonrpc.php
```
