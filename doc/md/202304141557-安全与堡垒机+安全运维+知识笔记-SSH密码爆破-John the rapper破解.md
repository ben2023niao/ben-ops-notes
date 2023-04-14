---
id: "doc-573617411ab1"
title: "SSH密码爆破-John the rapper破解"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652624.html"
---

# SSH密码爆破-John the rapper破解

```
cp /etc/shadow shadow.txt //直接保存shadow文件
unshadow /etc/passwd /etc/shadow >shadow.txt //如果有unshadow的话，也可以把这两个文件整合

john --wordlist=pass.txt shadow.txt //利用字典进行破解
john --show shadow.txt //查看破解信息
```

![文档配图](../media/4ea79e25eb93c92987.png)
