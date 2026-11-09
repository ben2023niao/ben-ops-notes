---
id: "doc-044b4775c474"
title: "WEB资产识别"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/68657795.html"
---

# WEB资产识别

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-Linux%20%E4%B8%8E%20Shell%2B%E6%97%A5%E5%B8%B8%E8%BF%90%E7%BB%B4%2BDNS%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-WEB%E8%B5%84%E4%BA%A7%E8%AF%86%E5%88%AB.md)

WEB资产识别，使用EyeWitness<https://github.com/FortyNorthSecurity/EyeWitness>

```
python EyeWitness.py -f 目标.txt –web –active-scan –add-http-ports 80,81,88,443,888,2082,2083,3122,4848,6588,7000,7001,7002,7003,8000,8080,8081,8089,8090,8443,8500,8888,9000,9001,9200,9043,9080,10000,10051,50000 –addhttps-ports 443,8443,9043

nmap -T4 -iL 目标.txt -oX scan.xml -p 80,81,88,443,888,2082,2083,3122,4848,6588,7000,7001,7002,7003,8000,8080,8081,8089,8090,8443,8500,8888,9000,9001,9200,9043,9080,10000,10051,50000 -Pn --open -n

python EyeWitness.py -x scan.xml --web --no-dns --active-scan
```

![文档配图](../media/fb5dd075ed421de255.png)
