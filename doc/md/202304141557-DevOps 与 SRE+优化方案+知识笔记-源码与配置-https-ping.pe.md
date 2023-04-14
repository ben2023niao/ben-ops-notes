---
id: "doc-09bfce388b1b"
title: "https://ping.pe"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68653278.html"
---

# https://ping.pe

![文档配图](../media/bc82a1b556e6ac2c5d.png)

```bash
curl 'https://ping.pe/github.com' \
 -H 'authority: ping.pe' \
 -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
 -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
 -H 'cache-control: max-age=0' \
 -H 'cookie: antiflood=ee2a0f706e1d06258132e5de4ac52878' \
 -H 'referer: https://ping.pe/github.com' \
 -H 'sec-fetch-dest: document' \
 -H 'sec-fetch-mode: navigate' \
 -H 'sec-fetch-site: same-origin' \
 -H 'sec-fetch-user: ?1' \
 -H 'upgrade-insecure-requests: 1' \
 -H 'user-agent: Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1' \
 --compressed
```
