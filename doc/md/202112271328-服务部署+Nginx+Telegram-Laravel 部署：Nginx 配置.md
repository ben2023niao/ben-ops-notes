---
id: "doc-65cb36c1ee1c"
title: "Laravel 部署：Nginx 配置"
date: "2021-12-27T13:28:17.379000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Nginx", "Telegram"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/laravel-bu-shu/laravel-bu-shu-nginx-pei-zhi.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "75621269140643197dfd5e767ad442cd7c620f926ca26a6244c9a79883db2b83"
---

# Laravel 部署：Nginx 配置

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202112271328-%E6%9C%8D%E5%8A%A1%E9%83%A8%E7%BD%B2%2BNginx%2BTelegram-Laravel%20%E9%83%A8%E7%BD%B2%EF%BC%9ANginx%20%E9%85%8D%E7%BD%AE.md)

> 原文：[Laravel 部署：Nginx 配置](https://xn--6o0a585a.gitbook.io/devops/fu-wu/laravel-bu-shu/laravel-bu-shu-nginx-pei-zhi.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-27 13:28｜日期依据：GitBook 页面更新时间

Nginx 虚拟主机配置 如果你把应用程序部署到执行 Nginx 的服务器，你可以使用下面的配置内容来开始设置你的 Web 服务器。此配置内容最好根据你的服务器需求做一些自定义的修改。如果你需要托管你的服务器，可以考虑 [Laravel Forget](https://forge.laravel.com/) 等服务：

```
server {
    listen 80;
    server_name example.com;
    root /example.com/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    index index.html index.htm index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php7.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

开启 Gzip 压缩 开启 Gzip 能让 Nginx 压缩一些文件，从而加载速度更快。

软重启 Nginx

`sudo systemctl reload nginx`

测试是否生效：

`curl -H "Accept-Encoding: gzip" -I http://www.example.com`

返回 `Content-Encoding: gzip` 即为成功。
示例：

`HTTP/1.1 200 OK Server: nginx Date: Wed, 26 Jun 2019 03:47:49 GMT Content-Type: text/html; charset=UTF-8 Connection: keep-alive Content-Encoding: gzip`
