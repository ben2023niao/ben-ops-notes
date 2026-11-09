---
id: "doc-8234b6b35a0d"
title: "如何使用 curl 和 openssl 命令简单测试域名被 SNI 阻断"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "DNS", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/66980680.html"
---

# 如何使用 curl 和 openssl 命令简单测试域名被 SNI 阻断

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BDNS%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8%20curl%20%E5%92%8C%20openssl%20%E5%91%BD%E4%BB%A4%E7%AE%80%E5%8D%95%E6%B5%8B%E8%AF%95%E5%9F%9F%E5%90%8D%E8%A2%AB%20SNI%20%E9%98%BB%E6%96%AD.md)

惊闻泉州已部署域名白名单，看到有人买域名买服务器来测试，其实用不着，还有人拿墙内的 IP 来测试，方法就错了

分享下使用 curl 和 openssl 进行简单测试的命令

随便找一个没有被墙境外 IP ，需要开着 https 服务，比如任意 CLF 的 IP ，此处使用 203.0.113.1 。任意编造一个白名单外的域名，比如 [abc123.com](http://abc123.com/)

## 使用 openssl 测试：

```
openssl s_client -connect 203.0.113.1:443 -servername abc123.com
```

如果没有 SNI 阻断的话，返回结果如下：

```
CONNECTED(00000003)
140693079176320:error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure:../ssl/record/rec_layer_s3.c:1544:SSL alert number 40
---
no peer certificate available
---
No client certificate CA names sent
---
SSL handshake has read 7 bytes and written 302 bytes
Verification: OK
```

如果被 SNI 阻断的话，返回结果如下（本人所处地方没有白名单，所以使用黑名单里的域名测试，[twitter.com](http://twitter.com/) ）：

```
CONNECTED(00000003)
write:errno=104
---
no peer certificate available
---
No client certificate CA names sent
---
SSL handshake has read 0 bytes and written 303 bytes
Verification: OK
```

对比分析可以看到区别，被 SNI 阻断的域名不会收到任何服务器的回应，`SSL handshake has read 0 bytes`

## 使用 curl 测试

```bash
curl --resolve abc123.com:443:203.0.113.1 https://abc123.com -iv
```

如果没有 SNI 阻断的话，返回信息如下：

```bash
curl --resolve abc123.com:443:203.0.113.1 https://abc123.com -iv
* Expire in 0 ms for 6 (transfer 0x55d868a5dfb0)
* Added abc123.com:443:203.0.113.1 to DNS cache
* Hostname abc123.com was found in DNS cache
* Trying 203.0.113.1...
* TCP_NODELAY set
* Expire in 200 ms for 4 (transfer 0x55d868a5dfb0)
* Connected to abc123.com (203.0.113.1) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
* CAfile: none
 CApath: /etc/ssl/certs
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS alert, handshake failure (552):
* error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure
* Closing connection 0
curl: (35) error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure
```

如果被 SNI 阻断的话，返回信息如下：

```bash
curl --resolve twitter.com:443:203.0.113.1 https://twitter.com -iv
* Expire in 0 ms for 6 (transfer 0x55dea6262fb0)
* Added twitter.com:443:203.0.113.1 to DNS cache
* Hostname twitter.com was found in DNS cache
* Trying 203.0.113.1...
* TCP_NODELAY set
* Expire in 200 ms for 4 (transfer 0x55dea6262fb0)
* Connected to twitter.com (203.0.113.1) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
* CAfile: none
 CApath: /etc/ssl/certs
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to twitter.com:443
* Closing connection 0
curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to twitter.com:443
```

对比分析可以看到区别，被 SNI 阻断的域名，同样收不到任何服务器的回应，正常的域名会有"TLSv1.3 (IN), TLS alert, handshake failure (552)"

测试时需要注意的是，被 SNI 阻断后，测试的 IP 也会被 IP 阻断一段时间，可以换一个 IP 继续测试
