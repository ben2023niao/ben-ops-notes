---
id: "doc-714c60ce709f"
title: "zabbix API调用 curl 技巧"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423116.html"
---

# zabbix API调用 curl 技巧

使用curl访问Zabbix API的示例代码

```bash
curl -X POST -H 'Content-Type: application/json-rpc' -d '{
    "jsonrpc": "2.0",
    "method": "apiinfo.version",
    "params": [],
    "id": 1,
    "auth": null
}' http://your.zabbix.server/api_jsonrpc.php
```

这个例子中，使用curl向Zabbix API发送一个名为apiinfo.version的请求，该请求没有参数，用于获取Zabbix API的版本号。在请求头中，我们指定了Content-Type为application/json-rpc，指定了请求正文为JSON格式的参数。在请求正文中，我们定义了jsonrpc、method、params、id和auth等参数。其中，id是一个任意数字，用于标识本次请求，auth可以为空，表示未进行身份验证。

需要注意的是，在使用Zabbix API时，需要对请求进行身份验证，可以通过用户名和密码或者API Token进行身份验证。如果没有进行身份验证，API只能访问公共数据。在请求头中需要包含Authorization字段，用于进行身份验证。

总之，使用curl访问Zabbix API需要指定请求的URL、请求方法、请求头和请求正文等参数，具体参数格式可以参考Zabbix API文档。
