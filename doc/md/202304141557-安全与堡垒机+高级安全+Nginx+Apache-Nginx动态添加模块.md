---
id: "doc-27759c76b632"
title: "Nginx动态添加模块"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Nginx", "Apache", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68656849.html"
---

# Nginx动态添加模块

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BNginx%2BApache-Nginx%E5%8A%A8%E6%80%81%E6%B7%BB%E5%8A%A0%E6%A8%A1%E5%9D%97.md)

很多时候，我们根据当时的项目情况和业务需求安装完 **[Nginx](https://haicoder.net/nginx/nginx-tutorial.html)** 后，后续随着业务的发展，往往会给安装好的 Nginx 添加其他的功能模块。在为 Nginx 添加功能模块时，要求 Nginx 不停机。

这就涉及到如何为已安装的 Nginx 动态添加模块的问题。本文，就和小伙伴们一起探讨如何为已安装的 Nginx 动态添加模块的问题。

## 为Nginx动态添加模块

这里以安装第三方 ngx_http_google_filter_module 模块为例。Nginx 的模块是需要重新编译 Nginx，而不是像 Apache 一样配置文件引用 .so。

### 下载扩展

```
下载第三方扩展模块 ngx_http_google_filter_module

# cd /data/software/
# git clone https://github.com/cuber/ngx_http_google_filter_module
查看安装模块
查看 Nginx 编译安装时安装了哪些模块，将命令行切换到 Nginx 执行程序所在的目录并输入 ./nginx -V，具体如下：

[root@binghe sbin]# ./nginx -V
nginx version: nginx/1.19.1
built by gcc 4.4.7 20120313 (Red Hat 4.4.7-17) (GCC)
built with OpenSSL 1.0.2 22 Jan 2015
TLS SNI support enabled
configure arguments: --prefix=/usr/local/nginx-1.19.1 --with-openssl=/usr/local/src/openssl-1.0.2 --with-pcre=/usr/local/src/pcre-8.37 --with-zlib=/usr/local/src/zlib-1.2.8 --with-http_ssl_module
[root@binghe sbin]#
可以看出编译安装 Nginx 使用的参数如下：

--prefix=/usr/local/nginx-1.19.1 --with-openssl=/usr/local/src/openssl-1.0.2 --with-pcre=/usr/local/src/pcre-8.37 --with-zlib=/usr/local/src/zlib-1.2.8 --with-http_ssl_module
重新编译
加入需要安装的模块，重新编译，这里添加 --add-module=/data/software/ngx_http_google_filter_module，具体如下：

./configure --prefix=/usr/local/nginx-1.19.1 --with-openssl=/usr/local/src/openssl-1.0.2 --with-pcre=/usr/local/src/pcre-8.37 --with-zlib=/usr/local/src/zlib-1.2.8 --with-http_ssl_module -–add-module=/data/software/ngx_http_google_filter_module
如上，将之前安装Nginx的参数全部加上，最后添加 --add-module=/data/software/ngx_http_google_filter_module，之后，我们要进行编译操作，如下：

# make    //千万不要make install，不然就真的覆盖
这里，需要注意的是：不要执行 make install 命令。

替换nginx二进制文件
# 备份原来的nginx执行程序
# mv /usr/local/nginx-1.19.1/sbin/nginx /usr/local/nginx-1.19.1/sbin/nginx.bak
# 将新编译的nginx执行程序复制到/usr/local/nginx-1.19.1/sbin/目录下
# cp /opt/nginx/sbin/nginx /usr/local/nginx-1.19.1/sbin/
```
