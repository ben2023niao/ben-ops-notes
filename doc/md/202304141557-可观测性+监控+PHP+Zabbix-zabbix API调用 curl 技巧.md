---
id: "doc-714c60ce709f"
title: "zabbix API调用 curl 技巧"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "PHP", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423116.html"
---

# zabbix API调用 curl 技巧

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BPHP%2BZabbix-zabbix%20API%E8%B0%83%E7%94%A8%20curl%20%E6%8A%80%E5%B7%A7.md)

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
