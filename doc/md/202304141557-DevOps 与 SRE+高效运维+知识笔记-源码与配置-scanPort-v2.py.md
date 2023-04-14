---
id: "doc-05d94f37976b"
title: "scanPort-v2.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/scanPort-v2.py_72056968.html"
---

# scanPort-v2.py

## 扫描器完善后（未引入多线程和单接口）

```python
#! /usr/bin/python
# ! -*- coding:UTF-8 -*-
import socket,sys,os
port =[21,80,43,135,445,1433,3306,3389]
def open(ip,port):
s =socket.socket()
try:
s.connect((ip,port))
return True
except:
return False
def scanIp(ip):
for x in port:
if open(ip,x):
print("%s host %s is open!")%(ip,x)
else:
print("%s host %s is close!")%(ip,x)
def rscan(ip):
for x in range(s,e):
if open(ip,x):
print("%s host %s is open!") % (ip, x)
else:
print("%s host %s is close!") % (ip, x)
if len(sys.argv)<2:
print '''
    This program prints files to the standard output.
       Any number of files can be specified.
       Options include:
       --version : Prints the version number
       --help    : Display this help
    '''
sys.exit()
if sys.argv[1].startswith('--'):
option =sys.argv[1][2:]
if option == 'version':
print 'version 1.0'
elif option == 'help':
print ''' python.py scanport.py host port
            python.py scanport.py host
            python.py scanport.py 203.0.113.1 21,80,135
            python.py scanport.py 203.0.113.1 80-90
            python py scanport.py 203.0.113.1 all
        '''
else:
print "Unknown option!"
sys.exit()
if len(sys.argv) == 2:
scanIp(sys.argv[1])
elif len(sys.argv) == 3:
try:
if ',' in sys.argv[2]:
p =sys.argv[2]
p =p.split(',') #以逗号为分隔符，将此分开，成为列表
for x in p:
a =[]
a.append(int(x))
port = a
scanIp(sys.argv[1])
elif '-' in sys.argv[2]:
a =sys.argv[2]
a =a.split('-')
s =int(a[0])
e =int(a[1])+1
rscan(sys.argv[1])
elif sys.argv[2] == 'all':
s = 1
e = 65536
rscan(sys.argv[1])
elif sys.argv[2] is
except KeyboardInterrupt:
print "Program End!"
```
