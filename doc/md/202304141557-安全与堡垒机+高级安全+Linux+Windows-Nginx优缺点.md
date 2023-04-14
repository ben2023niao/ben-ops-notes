---
id: "doc-8b8b53a9fd5d"
title: "Nginx优缺点"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Linux", "Windows", "Nginx", "Apache", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656794.html"
---

# Nginx优缺点

## Nginx优缺点

**[Nginx](https://haicoder.net/nginx/nginx-tutorial.html)** (engine x) 是一个高性能的 **[HTTP](https://haicoder.net/http/http-tutorial.html)** 和反向代理服务，也是一个 IMAP/POP3/SMTP 服务。Nginx 是由伊戈尔·赛索耶夫为俄罗斯访问量第二的 [Rambler.ru](http://Rambler.ru) 站点(俄文:Рамблер)开发的，第一个公开版本 0.1.0 发布于 2004 年10 月 4 日。

其将源代码以类 BSD 许可证的形式发布，因它的稳定性、丰富的功能集、示例配置文件和低系统资源的消耗而闻名。2011 年 6 月 1 日，nginx 1.0.4 发布。

Nginx 是一款轻量级的 Web 服务器/反向代理服务器及电子邮件(IMAP/POP3)代理服务器，并在一个 BSD-like 协议下发行。其特点是占有内存少，并发能力强，事实上 nginx 的并发能力确实在同类型的网页服务器中表现较好，中国大陆使用 nginx 网站用户有:百度、京东、新浪、网易、腾讯、淘宝等。

## Nginx优点

1. 高并发量：根据官方给出的数据，能够支持高达 50,000 个并发连接数的响应。原因，主要是 Nginx 使用了最新的 epoll（**[Linux](https://haicoder.net/linux/linux-tutorial.html)** 2.6 内核）和 kqueue（freeBSD）网路 I/O 模型，而 Apache 使用的是传统的 Select 模型，其比较稳定的 Prefork 模式为多进程模式，需要经常派生子进程，所以消耗的 CPU 等服务器资源，要比 Nginx 高很多。
2. 内存消耗少：处理静态文件，同样起 web 服务，比 apache 占用更少的内存及资源，所以它是轻量级的。
3. 简单稳定：配置简单，基本在一个 conf 文件中配置，性能比较稳定，可以 7*24 小时长时间不间断运行。
4. 模块化程度高：Nginx 是高度模块化的设计，编写模块相对简单，包括 gzipping, byte ranges, chunked responses,以及 SSI-filter 等 filter，支持 SSL 和 TLSSNI。
5. 支持 Rwrite 重写规则：能够根据域名、URL 的不同， 将 HTTP 请求分发到不同的后端服务器群组。
6. 低成本：Nginx 可以做高并发的负载均衡，且 Nginx 是开源免费的，如果使用 F5 等硬件来做负载均衡，硬件成本比较高。购买 F5BIG-IP、NetScaler 等硬件负载均衡交换机，需要十多万到几十万人民币，而 Nginx 为开源软件，采用的是 2-clause BSD-like 协议，可以免费试用，并且可用于商业用途。

BSD 开源协议是一个给使用者很大自由的协议，协议指出可以自由使用、修改源代码、也可以将修改后的代码作为开源或专用软件再发布。
7. 支持多系统：Nginx 代码完全用 **[C 语言](https://haicoder.net/c/c-tutorial.html)** 从头写成，已经移植到许多体系结构和操作系统，包括：Linux、FreeBSD、Solaris、Mac OS X、AIX 以及 Microsoft Windows，由于 Nginx 是免费开源的，可以在各系统上编译并使用。
8. 配置文件非常简单：网络和程序一样通俗易懂，即使，非专用系统管理员也能看懂。
9. 内置的健康检查功能：如果 NginxProxy 后端的某台 Web 服务器宕机了，不会影响前端的访问。
10. 节省带宽：支持 GZIP 压缩，可以添加浏览器本地缓存的 Header 头。
11. 支持热部署：Nginx 支持热部署，它的自动特别容易，并且，几乎可以 7 天 * 24 小时不间断的运行，即使，运行数个月也不需要重新启动，还能够在不间断服务的情况下，对软件版本进行升级。

## Nginx缺点

1. 动态处理差：nginx 处理静态文件好，耗费内存少，但是处理动态页面则很鸡肋，现在一般前端用 nginx 作为反向代理抗住压力，apache 作为后端处理动态请求。
2. rewrite 弱：虽然 nginx 支持 rewrite 功能，但是相比于 Apache 来说，Apache 比 nginx 的 rewrite 强大。
3. Nginx 仅能支持 http、**[https](https://haicoder.net/https/https-tutorial.html)** 和 Email 协议，这样就在适用范围上面小些，这个是它的缺点。
4. 对后端服务器的健康检查，只支持通过端口来检测，不支持通过 url 来检测。
5. 不支持 Session 的直接保持，但能通过 ip_hash 来解决。
