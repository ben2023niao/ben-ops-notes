---
id: "doc-5ae3d13a9572"
title: "nginx.conf"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Nginx", "Java", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/nginx.conf_68650146.html"
---

# nginx.conf

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BNginx%2BJava-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-nginx.conf.md)

```nginx
# For more information on configuration, see:
# * Official English Documentation: http://nginx.org/en/docs/
# * Official Russian Documentation: http://nginx.org/ru/docs/user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;events {
worker_connections 1024;
}http {
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
'$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for"';access_log /var/log/nginx/access.log main;sendfile on;
tcp_nopush on;
tcp_nodelay on;
keepalive_timeout 65;
types_hash_max_size 2048;
server_tokens off;include /etc/nginx/mime.types;
default_type application/octet-stream;# Load modular configuration files from the /etc/nginx/conf.d directory.
# See http://nginx.org/en/docs/ngx_core_module.html#include
# for more information.
include /etc/nginx/conf.d/*.conf;server {
listen 80 default_server;
listen [::]:80 default_server;
server_name _;
root /data/spug/spug_web/build;
client_max_body_size 100m;
add_header X-Frame-Options SAMEORIGIN always;gzip on;
gzip_min_length 1k;
gzip_buffers 4 16k;
gzip_http_version 1.1;
gzip_comp_level 7;
gzip_types text/plain text/css text/javascript application/javascript application/json;
gzip_disable "MSIE [1-6]\.";
gzip_vary on;location ^~ /api/ {
rewrite ^/api(.*) $1 break;
proxy_pass http://203.0.113.1:9001;
proxy_read_timeout 180s;
proxy_redirect off;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}location ^~ /api/ws/ {
rewrite ^/api(.*) $1 break;
proxy_pass http://203.0.113.1:9002;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

location / {
try_files $uri /index.html;
}
}
}
```
