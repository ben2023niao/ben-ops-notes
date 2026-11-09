---
id: "doc-66f5328302e3"
title: "Nginx与Apache选择"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Nginx", "Apache", "PHP", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656800.html"
---

# Nginx与Apache选择

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BNginx%2BApache-Nginx%E4%B8%8EApache%E9%80%89%E6%8B%A9.md)

## Apache

●　apache 的 rewrite 比 **[nginx](https://haicoder.net/nginx/nginx-tutorial.html)** 强大，在 rewrite 频繁的情况下，用 apache

●　apache 发展到现在，模块超多，基本想到的都可以找到

●　apache 更为成熟，少 bug ，nginx 的 bug 相对较多

●　apache 超稳定

●　apache 对 **[PHP](https://haicoder.net/php/php-tutorial.html)** 支持比较简单，nginx 需要配合其他后端用

●　apache 在处理动态请求有优势，nginx 在这方面是鸡肋，一般动态请求要 apache 去做，nginx 适合静态和反向。

●　apache 仍然是目前的主流，拥有丰富的特性，成熟的技术和开发社区

## Nginx

●　轻量级，采用 **[C 语言](https://haicoder.net/c/c-tutorial.html)** 进行编写，同样的 web 服务，会占用更少的内存及资源

●　抗并发，nginx 以 epoll and kqueue 作为开发模型，处理请求是异步非阻塞的，负载能力比 apache 高很多，而 apache 则是阻塞型的。在高并发下 nginx 能保持低资源低消耗高性能 ，而 apache 在 PHP 处理慢或者前端压力很大的情况下，很容易出现进程数飙升，从而拒绝服务的现象。

●　nginx 处理静态文件好，静态处理性能比 apache 高三倍以上

●　nginx 的设计高度模块化，编写模块相对简单

●　nginx 配置简洁，正则配置让很多事情变得简单，而且改完配置能使用 -t 测试配置有没有问题，apache 配置复杂 ，重启的时候发现配置出错了，会很崩溃

●　nginx 作为负载均衡服务器，支持 7 层负载均衡

●　nginx 本身就是一个反向代理服务器，而且可以作为非常优秀的邮件代理服务器

●　启动特别容易, 并且几乎可以做到 7*24 不间断运行，即使运行数个月也不需要重新启动，还能够不间断服务的情况下进行软件版本的升级

●　社区活跃，各种高性能模块出品迅速

## Nginx和Apache选择总结

一般来说，需要性能的 web 服务，用 nginx 。如果不需要性能只求稳定，更考虑 apache 。更为通用的方案是，前端 nginx 抗并发，后端 apache 集群，配合起来会更好。
