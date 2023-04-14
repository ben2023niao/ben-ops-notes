---
id: "doc-379b48069166"
title: "Connection reset by peer的问题排查"
date: "2023-04-14T15:57:00"
categories: ["故障排查", "问题排查"]
tags: ["故障排查", "问题排查", "Docker", "Nginx", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/10-问题排查/birdben/66980267.html"
---

# Connection reset by peer的问题排查

## 参考：[NGINX错误日志：warn：an upstream response is buffered to a temporary file排查](https://confluence.bssrv.com/pages/viewpage.action?pageId=66980272&src=contextnavpagetreemode)一、报错解释

### 1.1、报错原因

> Connection reset by peer是连接断开后的读和写操作引起的。

```
1、如果一端的Socket被关闭，另一端仍发送数据，发送的第一个数据包引发该异常(Connect reset by peer)。
（Socket默认连接60秒，60秒之内没有进行心跳交互，即读写数据，就会自动关闭连接）
2、一端退出，但退出时并未关闭该连接，另一端如果在从连接中读数据则抛出该异常（Connection reset）。
```

### 1.2、报错场景

```
1、服务器的并发连接数超过了其承载量，服务器会将其中一些连接关闭
（如果nginx配置了limit_conn addr 10;那单个用户连接数达到限制，也会报这个错）
2、客户关掉了浏览器，而服务器还在给客户端发送数据
3、防火墙的问题
4、服务器内存、存储等满了也会导致请求失败
```

## 二、真实场景问题排查

### 2.1、问题描述

> 最近日志总是出现报错`Connection reset by peer`，是偶现的。

```
经过排查发现，出现这个报错的几个场景
1、访问时间较长、请求数据较大的接口，快速多刷几次就会报错
2、上传大点的文件会报错
```

### 2.2、问题排查

首先根据报错解释中的报错场景，结合真实场景可以排除如下几个

> 1、连接数超过了其承载量 【排除】

这个是第一想法，因为我们的场景中有快速多刷几次就会报错，并且因为我们使用了cdn加速（会有代理ip代理用户真实ip），所以怀疑nginx配置的limit_conn addr 10限制成了`代理ip`的链接个数，那么很可能单个ip达到存在超10个链接的限制,后面的就会报这个错。
而上传大点的文件报错是因为，上传时间长会较长时间创建连接，比较容易超过10个连接的限制。

但是，为何每次都是快速刷3次就会报，这也太巧合了吧。并且limit_conn addr 10限制的好像是真实的ip(没验证)

> 2、客户关掉了浏览器，而服务器还在给客户端发送数据 【排除】

这个跟我们场景不符合

> 3、防火墙问题 【排除】

如果是防火墙问题，肯定是大量的这个报错，但是现在是个别现象

> 4、服务器内存、存储等满了也会导致请求失败 【正解】

报错出现后第一时间怀疑了是内存的问题，但是`htop`查看了一下，内存完全没问题的。对磁盘空间异常自信，就没看。

后面排查nginx报错，发现`nginx an upstream response is buffered to a temporary file`,才想到。
因为Nginx 将response缓冲到内存中，然后依次发送到客户端浏览器。但是如果response超过缓存区大小，就会保存到磁盘上，这个报错就说明了保存到了磁盘上，与此同时就报了Connection reset by peer，所以就是：请求的response缓冲到内存中，超过缓存区大小，就会保存到磁盘上，磁盘不足则报错Connection reset by peer。
而上传文件报错是因为需要暂存服务器上过度一下，存的时候磁盘不足则失败。

`df -lh`查看果然磁盘爆满（原因是docker的日志文件占用磁盘很大空间，清理掉、并做限制即可）

## 三、补充

> nginx an upstream response is buffered to a temporary file

对于来自 FastCGI Server 的 Response，Nginx 将其缓冲到内存中，然后依次发送到客户端浏览器。缓冲区的大小由 fastcgi_buffers 和 fastcgi_buffer_size 两个值控制。

```
fastcgi_buffers      8 4K;
fastcgi_buffer_size  4K;
```

fastcgi_buffers 控制 nginx 最多创建 8 个大小为 4K 的缓冲区。
fastcgi_buffer_size 则是处理 Response 时第一个缓冲区的大小，不包含在前者中。
所以总计能创建的最大内存缓冲区大小是 8*4K+4K = 36k。
而这些缓冲区是根据实际的 Response 大小动态生成的，并不是一次性创建的。比如一个 8K 的页面，Nginx 会创建 12K 共 2 个 buffers。
