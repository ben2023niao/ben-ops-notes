---
id: "doc-669fe33a0ab6"
title: "Nginx解决跨域方案二"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Nginx", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/68656786.html"
---

# Nginx解决跨域方案二

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BNginx%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-Nginx%E8%A7%A3%E5%86%B3%E8%B7%A8%E5%9F%9F%E6%96%B9%E6%A1%88%E4%BA%8C.md)

也可以直接简单粗暴的设置全局配置了，如下：

```nginx
http {
 include mime.types;
 default_type application/octet-stream;
 sendfile on;
 #连接超时时间，服务器会在这个时间过后关闭连接。
 keepalive_timeout 10;
 # gizp压缩
 gzip on;
 # 直接请求nginx也是会报跨域错误的这里设置允许跨域
 # 如果代理地址已经允许跨域则不需要这些, 否则报错(虽然这样nginx跨域就没意义了)
 add_header Access-Control-Allow-Origin *;
 add_header Access-Control-Allow-Headers X-Requested-With;
 add_header Access-Control-Allow-Methods GET,POST,OPTIONS;
 # srever模块配置是http模块中的一个子模块，用来定义一个虚拟访问主机
 server {
 listen 80;
 server_name localhost;
 # 根路径指到index.html
 location / {
 root html;
 index index.html index.htm;
 }
 # localhost/api 的请求会被转发到192.168.0.103:8080
 location /api {
 rewrite ^/b/(.*)$ /$1 break; # 去除本地接口/api前缀, 否则会出现404
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_pass http://203.0.113.1:8080; # 转发地址
 }
 # 重定向错误页面到/50x.html
 error_page 500 502 503 504 /50x.html;
 location = /50x.html {
 root html;
 }
 }
}
```
