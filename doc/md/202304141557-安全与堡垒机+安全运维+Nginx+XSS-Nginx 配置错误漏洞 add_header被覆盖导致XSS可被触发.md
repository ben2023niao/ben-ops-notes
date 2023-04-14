---
id: "doc-62a6783eaac6"
title: "Nginx 配置错误漏洞 add_header被覆盖导致XSS可被触发"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Nginx", "XSS", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/84422167.html"
---

# Nginx 配置错误漏洞 add_header被覆盖导致XSS可被触发

## 复现过程

Nginx配置文件子块（server、location、if）中的`add_header`，将会覆盖父块中的`add_header`添加的HTTP头，造成一些安全隐患。

如下列代码，整站（父块中）添加了CSP头：

```
add_header Content-Security-Policy "default-src 'self'";
add_header X-Frame-Options DENY;

location = /test1 {
    rewrite ^(.*)$ /xss.html break;
}

location = /test2 {
    add_header X-Content-Type-Options nosniff;
    rewrite ^(.*)$ /xss.html break;
}
```

但`/test2`的location中又添加了`X-Content-Type-Options`头，导致父块中的`add_header`全部失效：
![文档配图](../media/a3852c544170dc79e6.png)
XSS可被触发：
![文档配图](../media/ea71ecd6c466316058.png)
