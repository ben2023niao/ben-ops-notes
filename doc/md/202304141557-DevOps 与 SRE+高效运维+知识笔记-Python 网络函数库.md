---
id: "doc-899e5df2d4dd"
title: "Python 网络函数库"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/72056970.html"
---

# Python 网络函数库

## socket()函数

Python 中，我们用 socket（）函数来创建套接字，语法格式如下：

```
socket.socket([family[, type[, proto]]])
```

### 参数

- family: 套接字家族可以使AF_UNIX或者AF_INET
- type: 套接字类型可以根据是面向连接的还是非连接分为`SOCK_STREAM`或`SOCK_DGRAM`
- protocol: 一般不填默认为0.

### Socket 对象(内建)方法

| 函数 | 描述 |

| --- | --- |

| 服务器端套接字 |

| s.bind() | 绑定地址（host,port）到套接字， 在AF_INET下,以元组（host,port）的形式表示地址。 |

| s.listen() | 开始TCP监听。backlog指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。 |

| s.accept() | 被动接受TCP客户端连接,(阻塞式)等待连接的到来 |

| 客户端套接字 |

| s.connect() | 主动初始化TCP服务器连接，。一般address的格式为元组（hostname,port），如果连接出错，返回socket.error错误。 |

| s.connect_ex() | connect()函数的扩展版本,出错时返回出错码,而不是抛出异常 |

| 公共用途的套接字函数 |

| s.recv() | 接收TCP数据，数据以字符串形式返回，bufsize指定要接收的最大数据量。flag提供有关消息的其他信息，通常可以忽略。 |

| s.send() | 发送TCP数据，将string中的数据发送到连接的套接字。返回值是要发送的字节数量，该数量可能小于string的字节大小。 |

| s.sendall() | 完整发送TCP数据，完整发送TCP数据。将string中的数据发送到连接的套接字，但在返回之前会尝试发送所有数据。成功返回None，失败则抛出异常。 |

| s.recvfrom() | 接收UDP数据，与recv()类似，但返回值是（data,address）。其中data是包含接收数据的字符串，address是发送数据的套接字地址。 |

| s.sendto() | 发送UDP数据，将数据发送到套接字，address是形式为（ipaddr，port）的元组，指定远程地址。返回值是发送的字节数。 |

| s.close() | 关闭套接字 |

| s.getpeername() | 返回连接套接字的远程地址。返回值通常是元组（ipaddr,port）。 |

| s.getsockname() | 返回套接字自己的地址。通常是一个元组(ipaddr,port) |

| s.setsockopt(level,optname,value) | 设置给定套接字选项的值。 |

| s.getsockopt(level,optname[.buflen]) | 返回套接字选项的值。 |

| s.settimeout(timeout) | 设置套接字操作的超时期，timeout是一个浮点数，单位是秒。值为None表示没有超时期。一般，超时期应该在刚创建套接字时设置，因为它们可能用于连接的操作（如connect()） |

| s.gettimeout() | 返回当前超时期的值，单位是秒，如果没有设置超时期，则返回None。 |

| s.fileno() | 返回套接字的文件描述符。 |

| s.setblocking(flag) | 如果flag为0，则将套接字设为非阻塞模式，否则将套接字设为阻塞模式（默认值）。非阻塞模式下，如果调用recv()没有发现任何数据，或send()调用无法立即发送数据，那么将引起socket.error异常。 |

| s.makefile() | 创建一个与该套接字相关连的文件 |

---

## 简单实例

### 服务端

我们使用 socket 模块的 **socket** 函数来创建一个 socket 对象。socket 对象可以通过调用其他函数来设置一个 socket 服务。

现在我们可以通过调用 **bind(hostname, port)** 函数来指定服务的 *port(端口)*。

接着，我们调用 socket 对象的 *accept* 方法。该方法等待客户端的连接，并返回 *connection* 对象，表示已连接到客户端。

完整代码如下：

 展开源码

```python
#!/usr/bin/python3
# 文件名：server.py
# 导入 socket、sys 模块
import socket
import sys
# 创建 socket 对象
serversocket = socket.socket(
socket.AF_INET, socket.SOCK_STREAM)
# 获取本地主机名
host = socket.gethostname()
port = 9999
# 绑定端口号
serversocket.bind((host, port))
# 设置最大连接数，超过后排队
serversocket.listen(5)
while True:
# 建立客户端连接
clientsocket,addr = serversocket.accept()
print("连接地址: %s" % str(addr))
msg='欢迎访问笨鸟教程！'+ "\r\n"
clientsocket.send(msg.encode('utf-8'))
clientsocket.close()
```

### 客户端

接下来我们写一个简单的客户端实例连接到以上创建的服务。端口号为 9999。

**socket.connect(hosname, port )** 方法打开一个 TCP 连接到主机为 *hostname* 端口为 *port* 的服务商。连接后我们就可以从服务端获取数据，记住，操作完成后需要关闭连接。

完整代码如下：

 展开源码

```python
#!/usr/bin/python3
# 文件名：client.py
# 导入 socket、sys 模块
import socket
import sys
# 创建 socket 对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 获取本地主机名
host = socket.gethostname()
# 设置端口号
port = 9999
# 连接服务，指定主机和端口
s.connect((host, port))
# 接收小于 1024 字节的数据
msg = s.recv(1024)
s.close()
print (msg.decode('utf-8'))
#现在我们打开两个终端，第一个终端执行 server.py 文件：
#$ python3 server.py
#第二个终端执行 client.py 文件：
#$ python3 client.py
#欢迎访问笨鸟教程！
#这时我们再打开第一个终端，就会看到有以下信息输出：
#连接地址： ('203.0.113.1', 33397)
```

Python Internet 模块 以下列出了 Python 网络编程的一些重要模块：

| 协议 | 功能用处 | 端口号 | Python 模块 |

| --- | --- | --- | --- |

| HTTP | 网页访问 | 80 | httplib, urllib, xmlrpclib |

| NNTP | 阅读和张贴新闻文章，俗称为”帖子” | 119 | nntplib |

| FTP | 文件传输 | 20 | ftplib, urllib |

| SMTP | 发送邮件 | 25 | smtplib |

| POP3 | 接收邮件 | 110 | poplib |

| IMAP4 | 获取邮件 | 143 | imaplib |

| Telnet | 命令行 | 23 | telnetlib |

| Gopher | 信息查找 | 70 | gopherlib, urllib |

更多内容可以参阅官网的 [Python Socket Library and Modules](https://docs.python.org/3.0/library/socket.html)。

若只使用python3.X, 下面可以不看了, 记住有个urllib的库就行了
python2.X 有这些库名可用: [urllib](https://docs.python.org/2/library/urllib.html#urllib.urlencode), [urllib2](https://docs.python.org/2/library/urllib2.html#urllib2.Request), urllib3, [httplib](https://docs.python.org/2/library/httplib.html), httplib2, requests

python3.X 有这些库名可用: urllib, urllib3, httplib2, requests

两者都有的urllib3和requests, 它们不是标准库. urllib3 提供线程安全连接池和文件post支持,与urllib及urllib2的关系不大. [requests](http://docs.python-requests.org/en/latest/index.html) 自称HTTP for Humans, 使用更简洁方便
`TCP 服务端`

```
#服务端结构：
tcps = socket() #创建服务器套接字
tcps.bind() #把地址绑定到套接字
tcps.listen() #监听链接
while True: #服务器无限循环
tcpc = tcps.accept() #接受客户端链接
while True: #通讯循环
tcpc.recv()/tcpc.send() #对话(接收与发送)
tcpc.close() #关闭客户端套接字
tcps.close() #关闭服务器套接字(可选)
```

```
时间戳服务端实例：
```

 展开源码

```python
#!/usr/bin/python3
# -*-coding:utf-8 -*-
from socket import *
import time
COD = 'utf-8'
HOST = '203.0.113.1' # 主机ip
PORT = 21566 # 软件端口号
BUFSIZ = 1024
ADDR = (HOST, PORT)
SIZE = 10
tcpS = socket(AF_INET, SOCK_STREAM) # 创建socket对象
tcpS.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) #加入socket配置，重用ip和端口
tcpS.bind(ADDR) # 绑定ip端口号
tcpS.listen(SIZE) # 设置最大链接数
while True:
print("服务器启动，监听客户端链接")
conn, addr = tcpS.accept()
print("链接的客户端", addr)
while True:
try:
data = conn.recv(BUFSIZ) # 读取已链接客户的发送的消息
except Exception:
print("断开的客户端", addr)
break
print("客户端发送的内容:",data.decode(COD))
if not data:
break
msg = time.strftime("%Y-%m-%d %X") #获取结构化事件戳
msg1 = '[%s]:%s' % (msg, data.decode(COD))
conn.send(msg1.encode(COD)) #发送消息给已链接客户端
conn.close() #关闭客户端链接
tcpS.closel()
```

**TCP 客户端**

```
#客户端结构：
tcpc = socket() # 创建客户端套接字
tcpc.connect() # 尝试连接服务器
while True: # 通讯循环
tcpc.send()/tcpc.recv() # 对话(发送/接收)
tcpc.close() # 关闭客户套接字
```

时间戳客户端实例：

 展开源码

```python
#!/usr/bin/python3
# -*-coding:utf-8 -*-
from socket import *
from time import ctime
HOST = '203.0.113.1' #服务端ip
PORT = 21566 #服务端端口号
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpCliSock = socket(AF_INET, SOCK_STREAM) #创建socket对象
tcpCliSock.connect(ADDR) #连接服务器
while True:
data = input('>>').strip()
if not data:
break
tcpCliSock.send(data.encode('utf-8')) #发送消息
data = tcpCliSock.recv(BUFSIZ) #读取消息
if not data:
break
print(data.decode('utf-8'))
tcpCliSock.close() #关闭客户端
```

## Lession11-Client.py

 展开源码

```python
#! /usr/bin/python
#! -*- coding:UTF-8 -*-
#lession11-client.py
import socket,sys,os
c =socket.socket()
host =socket.gethostname()
port =9999
c.connect((host,port))
while True:
print c.recv(1024)
while 1:
b =raw_input("Say to Server:")
c.send(b)
print "Send to server success!"
print c.recv(1024)
```

---

## Lession11-Server.py

 展开源码

```python
#! /usr/bin/python
#! -*- coding:UTF-8 -*-
import socket,sys,os
s =socket.socket()
host =socket.gethostname()
port =9999
s.bind((host,port))
s.listen(5)
while True:
c,addr =s.accept()
print("Client address is:",str(addr))
c.send("Link success!")
while 1:
if c.recv(1024) == 'cmd':
while 1:
c.send("It's cmd!")
y =os.popen(c.recv(1024)).read()
c.send(y)
print "Send to client CMD success!"
else:
print c.recv(1024)
```

---
