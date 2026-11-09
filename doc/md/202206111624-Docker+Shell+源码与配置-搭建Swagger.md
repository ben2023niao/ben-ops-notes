---
id: "doc-45b6e306e39f"
title: "搭建Swagger"
date: "2022-06-11T16:24:24.416000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-swagger.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "99611294fd9b9ce2f75c8e81f83759d641fe1d274123f203fb621258a9b2108d"
---

# 搭建Swagger

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111624-Docker%2BShell%2B%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-%E6%90%AD%E5%BB%BASwagger.md)

> 原文：[搭建Swagger](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-swagger.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:24｜日期依据：GitBook 页面更新时间

#### 1、下载swagger-editor的容器

```bash
docker pull swaggerapi/swagger-editor
docker run -d -p 81:8080 swaggerapi/swagger-editor
```

#### 2、下载swagger-ui的容器

```bash
docker pull swaggerapi/swagger-ui
```

json文件挂在到容器中

```bash
docker run -d -p 80:8080 -e SWAGGER_JSON=/foo/swagger.json -v /home/service/swagger/swagger.json:/foo swaggerapi/swagger-ui
```

-p：宿主机端口：容器端口，将容器端口暴露给宿主机端口
-d:后台启动
-e：执行容器中/foo/swagger.json
-v：将宿主机中/home/service/swagger/swagger.json挂载到容器 /foo中执行

#### 3、web验证

输入：[http://主机IP](http://xn--ip-wz2cm89g/)：端口
