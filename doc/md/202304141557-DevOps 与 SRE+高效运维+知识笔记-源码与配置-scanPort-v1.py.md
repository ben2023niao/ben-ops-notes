---
id: "doc-a732dc6f661d"
title: "scanPort-v1.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/scanPort-v1.py_72056966.html"
---

# scanPort-v1.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-scanPort-v1.py.md)

```python
#! /usr/bin/python
# ! -*- coding:UTF-8 -*-
import socket,time
port =[80,21,1433,3389,8000,6666,135,445]
def isOpen(ip,port):
s = socket.socket()
try:
s.connect(ip,port)
return True
except:
return False
def scan(ip):
for x in port:
if isOpen(ip,x):
print "%s host %s is open"%(ip,x)
time.sleep(1)
else:
print "%s host %s is close"%(ip,x)
time.sleep(1)
scan('203.0.113.1')
```
