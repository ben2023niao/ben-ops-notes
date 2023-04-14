---
id: "doc-ce85aca75974"
title: "my.cnf"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "MySQL", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/my.cnf_68650144.html"
---

# my.cnf

```
[mysqld]
datadir=/data/mysql
log-error=/data/mysql/mysql.log
pid-file=/data/mysql/mysql.pid
socket=/var/lib/mysql/mysql.sock
symbolic-links=0
max_connections=1000!includedir /etc/my.cnf.d
```
