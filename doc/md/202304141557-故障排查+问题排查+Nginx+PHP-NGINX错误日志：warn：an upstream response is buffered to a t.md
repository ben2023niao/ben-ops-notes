---
id: "doc-955bc5ff4a74"
title: "NGINX错误日志：warn：an upstream response is buffered to a temporary file排查"
date: "2023-04-14T15:57:00"
categories: ["故障排查", "问题排查"]
tags: ["故障排查", "问题排查", "Nginx", "PHP", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/10-问题排查/birdben/66980272.html"
---

# NGINX错误日志：warn：an upstream response is buffered to a temporary file排查

查看Nginx日志，发现有很多报错

```
2021/02/27 17:00:54 [warn] 28#28: *49939
an upstream response is buffered to a temporary file /var/cache/nginx/proxy_temp/6/14/0000000146 while reading upstream, client: xxx.xxx.xxx.x,
server: airflow.yidianshihui.com, request: "GET /home HTTP/1.1", upstream: "http://xxx.xxx.xxx.xxx:xxxx/home", host: "airflow.yidianshihui.com",
referrer: "http://airflow.yidianshihui.com/home?tags=%E6%AF%8F%E6%97%A5ic_sku%E5%90%8C%E6%AD%A5"
```

## 1.错误日志：warn：an upstream response is buffered to a temporary file

```
解决办法：增加fastcgi_buffers      8 4K;     fastcgi_buffer_size  4K;
```

### 2. a client request body is buffered to a temporary file

解决办法：增加client_max_body_size 2050m; client_body_buffer_size 1024k;

## Nginx 的 buffer 机制：

对于来自 FastCGI Server 的 Response，Nginx 将其缓冲到内存中，然后依次发送到客户端浏览器。缓冲区的大小由 fastcgi_buffers 和 fastcgi_buffer_size 两个值控制。

比如如下配置：

```
fastcgi_buffers      8 4K;
fastcgi_buffer_size  4K;
```

fastcgi_buffers 控制 nginx 最多创建 8 个大小为 4K 的缓冲区，而 fastcgi_buffer_size 则是处理 Response 时第一个缓冲区的大小，不包含在前者中。所以总计能创建的最大内存缓冲区大小是 8*4K+4K = 36k。而这些缓冲区是根据实际的 Response 大小动态生成的，并不是一次性创建的。比如一个 8K 的页面，Nginx 会创建 2*4K 共 2 个 buffers。

当 Response 小于等于 36k 时，所有数据当然全部在内存中处理。如果 Response 大于 36k 呢？fastcgi_temp 的作用就在于此。多出来的数据会被临时写入到文件中，放在这个目录下面。同时你会在 error.log 中看到一条类似 warning：

```
2010/03/13 03:42:22 [warn] 3994#0: *1 an upstream response is buffered to a temporary file
/usr/local/nginx/fastcgi_temp/1/00/0000000001 while reading upstream,
client: 203.0.113.1,
server: www.xxx.cn,
request: "POST /test.php HTTP/1.1",
upstream: "fastcgi://203.0.113.1:9000",
host: "xxx.cn",
referrer: "http://xxx.cn/test.php"
```

显然，缓冲区设置的太小的话，Nginx 会频繁读写硬盘，对性能有很大的影响，但也不是越大越好，没意义

官方文档：
[http://nginx.org/en/docs/http/ngx_http_core_module.html#client_body_buffer_size](https://links.jianshu.com/go?to=http://nginx.org/en/docs/http/ngx_http_core_module.html#client_body_buffer_size)

修改Nginx配置：

```nginx
location /api {
 proxy_set_header Host $http_host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_pass http://elk_server/api;
 client_body_buffer_size 1024k;
 client_max_body_size 2050m;
 fastcgi_buffers 8 4K;
 fastcgi_buffer_size 4K;
 }
```

参考：
[Nginx性能调优之buffer参数设置](https://links.jianshu.com/go?to=https://blog.csdn.net/zhouyan8603/article/details/89410119)
[nginx常见问题](https://links.jianshu.com/go?to=https://my.oschina.net/linland/blog/373315)
