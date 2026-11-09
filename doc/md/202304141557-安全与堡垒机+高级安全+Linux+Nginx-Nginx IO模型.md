---
id: "doc-d303a255693d"
title: "Nginx IO模型"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "Nginx", "Apache", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656813.html"
---

# Nginx IO模型

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BLinux%2BNginx-Nginx%20IO%E6%A8%A1%E5%9E%8B.md)

**[Nginx](https://haicoder.net/nginx/nginx-tutorial.html)** 支持多种并发模型，并发模型的具体实现根据系统平台而有所不同。在支持多种并发模型的平台上，Nginx 自动选择最高效的模型。但我们也可以使用 use 指令在配置文件中显式地定义某个并发模型。

## Nginx中支持的并发模型

### select

IO 多路复用、标准并发模型。在编译 Nginx 时，如果所使用的系统平台没有更高效的并发模型，select 模块将被自动编译。configure 脚本的选项：–with-select_module 和 --without-select_module 可被用来强制性地开启或禁止 select 模块的编译。

### poll

IO 多路复用、标准并发模型。与 select 类似，在编译 Nginx 时，如果所使用的系统平台没有更高效的并发模型，poll 模块将被自动编译。configure 脚本的选项：–with-poll_module 和 --without-poll_module 可用于强制性地开启或禁止 poll 模块的编译。

### epoll

IO 多路复用、高效并发模型，可在 Linux 2.6+ 及以上内核可以使用。

### kqueue

IO 多路复用、高效并发模型，可在 FreeBSD 4.1+, OpenBSD 2.9+, NetBSD 2.0, and Mac OS X 平台中使用。

### /dev/poll

高效并发模型，可在 Solaris 7 11/99+, HP/UX 11.22+ (eventport), IRIX 6.5.15+, and Tru64 UNIX 5.1A+ 平台使用。

### eventport

高效并发模型，可用于 Solaris 10 平台，PS：由于一些已知的问题，建议使用/dev/poll替代。

## Nginx epoll

为什么 epoll 快，比较一下 Apache 常用的 select 和 Nginx 常用的 epoll：

### select

1. 最大并发数限制，因为一个进程所打开的 FD （文件描述符）是有限制的，由 FD_SETSIZE 设置，默认值是 1024/2048，因此 Select 模型的最大并发数就被相应限制了。自己改改这个 FD_SETSIZE？ 想法虽好，可是先看看下面吧。
2. 效率问题，select 每次调用都会线性扫描全部的 FD 集合，这样效率就会呈现线性下降，把 FD_SETSIZE 改大的后果就是，大家都慢慢来，什么？都超时了。
3. 内核/用户空间，内存拷贝问题，如何让内核把 FD 消息通知给用户空间呢？在这个问题上 select 采取了内存拷贝方法，在 FD 非常多的时候，非常的耗费时间。

总结为：1、连接数受限 2、查找配对速度慢 3、数据由内核拷贝到用户态消耗时间。

### epoll

1. Epoll 没有最大并发连接的限制，上限是最大可以打开文件的数目，这个数字一般远大于 2048, 一般来说这个数目和系统内存关系很大 ，具体数目可以 cat /proc/sys/fs/file-max 查看。
2. 效率提升，Epoll 最大的优点就在于它只管你 “活跃” 的连接 ，而跟连接总数无关，因此在实际的网络环境中，Epoll 的效率就会远远高于 select 和 poll。
3. 内存共享，Epoll 在这点上使用了 “共享内存”，这个内存拷贝也省略了。
