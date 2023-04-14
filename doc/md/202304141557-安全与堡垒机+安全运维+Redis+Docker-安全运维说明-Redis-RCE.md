---
id: "doc-b2511bdbcb54"
title: "Redis-RCE"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Redis", "Docker", "漏洞", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/Redis-RCE_68657810.html"
---

# Redis-RCE

漏洞复现
docker pull redis
![文档配图](../media/563d55e9041cef6db1.png)

Docker run -d redis

![文档配图](../media/64dedc5434439c8dfc.png)

Docker run -it redis /bin/bash

![文档配图](../media/3fde431618a3b92902.png)

docker inspect 9f5946f764b9 | grep IPAddress

![文档配图](../media/ee304887aa1c69f835.png)

<https://github.com/jas502n/Redis-RCE>

![文档配图](../media/181d9f44a5da5f3317.png)

漏洞原理
文章<https://paper.seebug.org/975/>

![文档配图](../media/30064d84b7bdf3938e.png)

看这张图就懂了

漏洞参考
<https://paper.seebug.org/975/>

漏洞EXP
<https://github.com/LoRexxar/redis-rogue-server>
<https://github.com/jas502n/Redis-RCE>
<https://github.com/n0b0dyCN/redis-rogue-server>
<https://github.com/RicterZ/RedisModules-ExecuteCommand>
