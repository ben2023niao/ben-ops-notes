---
id: "doc-2ef3ce776ff5"
title: "openssl 自签名10年证书"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/84416825.html"
---

# openssl 自签名10年证书

![文档配图](../media/07416b03e25363b0f1.png)

```
openssl genrsa -out server.key 1024

openssl req -new -key server.key -out server.csr

openssl x509 -req -in server.csr -out server.crt -signkey server.key -days 3650
```
