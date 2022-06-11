---
id: "doc-b10dd929cb4d"
title: "nginx-docker-compose.yml"
date: "2022-06-11T16:36:28.755000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "Nginx", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/nginx-docker-compose.yml.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "c4d834b3b096e38c05efd301a2dda657d51dfa789c963a84ab981dc8b52864bf"
---

# nginx-docker-compose.yml

> 原文：[nginx-docker-compose.yml](https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/nginx-docker-compose.yml.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:36｜日期依据：GitBook 页面更新时间

```bash
-- 1. 启动一个默认实例
docker run --name nginx -d nginx

-- 2. 把文件拷出来
cd /data/docker/nginx
docker cp nginx:/etc/nginx/nginx.conf .
docker cp nginx:/etc/nginx/conf.d/default.conf .
docker cp nginx:/usr/share/nginx/html/* .
docker cp nginx:/usr/share/nginx/html/50x.html .
docker cp nginx:/usr/share/nginx/html/index.html .

-- 3. 删除默认实例
docker stop nginx && docker rm nginx

-- 4. 启动新实例
docker run --name nginx -p 81:80 \
  -v /data/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /data/docker/nginx/html:/usr/share/nginx/html \
  -v /data/docker/nginx/conf.d:/etc/nginx/conf.d \
  -d nginx

version: '3.0'

services:
  nginx:
    restart: always
    image: nginx:1.16.6-alpine
    ports:
      - 8080:8080
      - 80:80
      - 443:443
    volumes:
      - /home/service/nginx/conf.d:/etc/nginx/conf.d
      - /home/service/nginx/log:/var/log/nginx
      - /home/service/nginx/static:/usr/share/nginx/html
      - /etc/letsencrypt:/etc/letsencrypt
```
