---
id: "doc-0198f67535fb"
title: "搭建PHP环境"
date: "2022-06-11T16:23:51.931000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-php-huan-jing.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "2a498ebad80f703e6ead408bde9058c48f5e19fa2780329af8499da905edf0ca"
---

# 搭建PHP环境

> 原文：[搭建PHP环境](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-php-huan-jing.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:23｜日期依据：GitBook 页面更新时间

1、查找Docker Hub上的php镜像

```
docker search php
```

2、拉取官方的镜像

```bash
docker pull php:5.6-fpm
```

3、本地镜像列表里查看

```
docker images
```

4、宿主机创建目录用于容器文件挂载

```
mkdir -p /home/service/php/conf
mkdir -p /home/service/php/logs
```

5、运行php镜像

```bash
docker run -p 9000:9000 --name  php-fpm \
-v /home/service/php/conf:/usr/local/etc/php \
-v /home/service/php/logs:/phplogs \
-d php:5.6-fpm
```

6、查看容器启动情况

```
docker ps
```

> up 状态表示在运行，exit就退出
> 7、通过浏览器访问验证phpinfo

```
访问路径直接 http://ip/index.php
```
