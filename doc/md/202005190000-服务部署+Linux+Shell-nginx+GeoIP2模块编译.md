---
id: "doc-766c21d72151"
title: "nginx+GeoIP2模块编译"
date: "2020-05-19T00:00:00+08:00"
dateSource: "正文原始日期"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Linux", "Shell", "Docker", "Nginx", "CDN", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx+geoip2-mo-kuai-bian-yi.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "f253bb91ff1f7cec7246f4054e65d6998fac804df61e7f270bd2a3e25bd55cd6"
---

# nginx+GeoIP2模块编译

> 原文：[nginx+GeoIP2模块编译](https://xn--6o0a585a.gitbook.io/devops/fu-wu/nginx/nginx+geoip2-mo-kuai-bian-yi.html)

> 来源：GitBook 网页 HTML｜页面时间：2020-05-19 00:00｜日期依据：正文原始日期

```
sudo docker run -it --name nginxgeoip2 docker.io/centos:7 /bin/bash
yum -y install git
git clone https://github.com/HackerNiao/nginx-geoip2
bash -x nginx-geoip2/nginx_geoip2.sh
```

```bash
#!/bin/bash
# 安装依赖
yum -y update
yum -y install vim wget zip unzip git gcc pcre-devel openssl openssl-devel gd-devel

mkdir /opt
cd /opt/
# 下载geoip2模块的代码
wget https://github.com/maxmind/libmaxminddb/releases/download/1.3.2/libmaxminddb-1.3.2.tar.gz
tar -zxvf libmaxminddb-1.3.2.tar.gz
cd libmaxminddb-1.3.2
./configure && make && make install
echo /usr/local/lib  >> /etc/ld.so.conf.d/local.conf
ldconfig
# 此代码参与nginx的编译
mkdir -p /usr/share/GeoIP/
cd /opt/
git clone https://github.com/HackerNiao/nginx-geoip2
cd nginx-geoip2
tar -zxvf GeoLite2-City_20200519.tar.gz
mv ./GeoLite2-City_20200519/GeoLite2-City.mmdb /usr/share/GeoIP/
tar -zxvf GeoLite2-Country_20200519.tar.gz
mv ./GeoLite2-Country_20200519/GeoLite2-Country.mmdb /usr/share/GeoIP/

# 设置www用户
useradd -s /sbin/nologin -M www
id www

cd /opt/
wget https://nginx.org/download/nginx-1.20.2.tar.gz
tar zxvf nginx-1.20.2.tar.gz
cd nginx-1.20.2
./configure --user=www --group=www \
--with-select_module \
--with-poll_module \
--with-pcre \
--with-http_v2_module \
--with-stream \
--with-stream_ssl_module \
--with-stream_ssl_preread_module \
--with-http_stub_status_module \
--with-http_ssl_module \
--with-http_image_filter_module \
--with-http_gzip_static_module \
--with-http_gunzip_module \
--with-http_sub_module \
--with-http_flv_module \
--with-http_addition_module \
--with-http_realip_module \
--with-http_mp4_module \
--prefix=/www/server/nginx \
--add-module=/opt/nginx-geoip2/ngx_http_geoip2_module
make && make install

cp /www/server/nginx/sbin/nginx /sbin/

nginx -t

mkdir -p /www/server/nginx/conf/vhost
cd /www/server/nginx/conf/
cp nginx.conf nginx.conf.back

cat > /www/server/nginx/conf/nginx.conf <<"EOF"
user  www www;
worker_rlimit_nofile 51200;
worker_processes  auto;
events
    {
        use epoll;
        worker_connections 51200;
        multi_accept on;
    }

http {
    include       mime.types;
    include       vhost/*.conf;
    set_real_ip_from 203.0.113.1/0;
    real_ip_header X-Forwarded-For;
    geoip2  /usr/share/GeoIP/GeoLite2-Country.mmdb {
          $geoip2_Country_code country iso_code;
    }
    geoip2  /usr/share/GeoIP/GeoLite2-City.mmdb {
          $geoip2_City_code country iso_code;
    }
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    server {
        listen       80;
        server_name  localhost;
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
EOF

cat > /www/server/nginx/conf/vhost/zh-api-cdn-host.conf <<"EOF"
upstream zh-api-cdn-host {
    ip_hash;
    server 203.0.113.1 weight=1 max_fails=2 fail_timeout=2s;
}
server
{
    listen 80;
    server_name zh-api-cdn-host.666.com;
    index index.php index.html index.htm default.php default.htm default.html;
#   root /www/wwwroot/zh-api-cdn-host.666.com;

location / {
            proxy_pass http://zh-api-cdn-host/$uri;
            proxy_set_header Host $host:$server_port;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header token $http_token;
        }
    access_log  /www/server/nginx/logs/zh-api-cdn-host.666.com.log;
    error_log  /www/server/nginx/logs/zh-api-cdn-host.666.com.error.log;
}
EOF

cat > /www/server/nginx/conf/vhost/zh-h5.conf <<"EOF"
upstream zh-h5 {
    ip_hash;
    server 203.0.113.1:81 weight=1 max_fails=2 fail_timeout=2s;
    server 203.0.113.1:82 weight=1 max_fails=2 fail_timeout=2s;
    server 203.0.113.1:83 weight=1 max_fails=2 fail_timeout=2s;
}

server
{
    listen 80;
    server_name zh-h5.666.com;
    index index.php index.html index.htm default.php default.htm default.html;
location ~ .* {
set $language 0;
if ($geoip2_country_code = CN) {
  set $language "1";
  add_header  accept-language zh-CN;
}
if ($geoip2_country_code = MO) {
  set $language "2";
  add_header  accept-language zh-CN;
}
if ($geoip2_country_code = HK) {
  set $language "3";
  add_header  accept-language zh-CN;
}
if ($geoip2_country_code = TW) {
  set $language "4";
  add_header  accept-language zh-CN;
}
if ($geoip2_country_code = VN) {
  set $language "5";
  add_header  accept-language vi-VN;
}
if ($language = 0){
    add_header  accept-language en;
}
        try_files $uri $uri/ /index.html;
            proxy_pass http://zh-h5;
            proxy_set_header Host $host:$server_port;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Accept-Language $http_accept_language;
            proxy_set_header token $http_token;
   }
    access_log  /www/server/nginx/logs/zh-h5.666.com.log;
    error_log  /www/server/nginx/logs/zh-h5.666.com.error.log;
}
EOF
nginx -t
```
