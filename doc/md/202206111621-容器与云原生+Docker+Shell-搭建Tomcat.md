---
id: "doc-1c82befa6ff2"
title: "搭建Tomcat"
date: "2022-06-11T16:21:55.077000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-tomcat.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "ed4b7cef8741ab4a07a89aee1959e6fa12f0b2d113582af2036adafffd59b4c5"
---

# 搭建Tomcat

> 原文：[搭建Tomcat](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-tomcat.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:21｜日期依据：GitBook 页面更新时间

1、查找Docker Hub上的tomcat镜像

```
docker search tomcat
```

2、拉取官方镜像

```bash
docker pull tomcat
```

3、查看镜像是否存在

```
docker images
```

4、宿主机创建相关目录挂载到容器主机上

```
mkdir -p /home/service/tomcat/conf
mkdir -p /home/service/tomcat/webapps/test
mkdir -p /home/service/tomcat/logs
```

5、创建并运行容器

```bash
docker run --name tomcat -p 8080:8080 \
-v /home/service/tomcat/webapps/test:/usr/local/tomcat/webapps/test \
-d tomcat
```

6、查看容器是否已在运行

```
docker ps -a
```

7、通过浏览器访问

```
地址：http://ip:8080
```
