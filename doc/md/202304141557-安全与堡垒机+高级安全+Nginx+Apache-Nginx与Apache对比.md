---
id: "doc-f248020cb351"
title: "Nginx与Apache对比"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Nginx", "Apache", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656798.html"
---

# Nginx与Apache对比

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BNginx%2BApache-Nginx%E4%B8%8EApache%E5%AF%B9%E6%AF%94.md)

## Nginx与Apache区别

### 优点

1. 轻量级，采用 **[C 语言](https://haicoder.net/c/c-tutorial.html)** 进行编写，同样的 web 服务，会占用更少的内存及资源。
2. 抗并发，**[nginx](https://haicoder.net/nginx/nginx-tutorial.html)** 以 epoll and kqueue 作为开发模型，处理请求是异步非阻塞的，多个连接对应一个进程，负载能力比 apache 高很多，而 apache 则是同步多进程模型，只能一个连接对应一个进程，当压力过大时，它是会被阻塞型的。
在高并发下 nginx 能保持低资源低消耗高性能 ，而 apache 在 **[PHP](https://haicoder.net/php/php-tutorial.html)** 处理慢或者前端压力很大的情况下，很容易出现进程数飙升，从而拒绝服务的现象。
3. 设计高度模块化，编写模块相对简单。
4. 配置简洁，正则配置让很多事情变得简单，而且改完配置能使用 -t 测试配置有没有问题，apache 配置复杂 ，重启的时候发现配置出错了，会很崩溃。
5. 一般用于处理静态文件，静态处理性能比 apache 高三倍以上。
6. 作为负载均衡服务器，支持 7 层负载均衡。
7. 本身就是一个反向代理服务器，而且可以作为非常优秀的邮件代理服务器。
8. nginx 启动特别容易, 并且几乎可以做到 7*24 不间断运行，即使运行数个月也不需要重新启动，支持热部署，比如：实现不间断服务的情况下进行软件版本的升级与版本的回退。
9. 社区活跃，各种高性能模块出品迅速。

### 缺点

1. apache 的 rewrite 比 nginx 强大，在 rewrite 频繁的情况下，用 apache。
2. apache 发展到现在，模块超多，基本想到的都可以找到。
3. apache 更为成熟，少 bug ，nginx 的 bug 相对较多。
4. apache 超稳定，Nginx 一个进程死掉时，会影响到多个用户的使用，稳定性差。
5. apache 对 PHP 支持比较简单，nginx 需要配合其他后端用。
6. apache 在处理动态请求有优势，nginx 在这方面是鸡肋，一般动态请求要 apache 去做，nginx 适合静态和反向。
7. apache 仍然是目前的主流，拥有丰富的特性，成熟的技术和开发社区。

## Nginx与Apache区别总结

Apache 是同步多进程模型，一个连接对应一个进程，而 Nginx 是异步的，多个连接（万级别）可以对应一个进程。
