---
id: "doc-6dc12aa0fd43"
title: "创建mysql数据库"
date: "2022-06-11T16:34:51.863000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "MySQL", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/chuang-jian-mysql-shu-ju-ku.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "d9a8b66a6e1a890fac659a376c6de87d47f39d959ee0f4892861f798a370ec89"
---

# 创建mysql数据库

> 原文：[创建mysql数据库](https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/chuang-jian-mysql-shu-ju-ku.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:34｜日期依据：GitBook 页面更新时间

docker-compose 创建数据库
`docker-compose -f db.yml up -d`

```
db:
  container_name: mysql
  image: mysql:5.7.17
  command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8 --collation-server=utf8_unicode_ci
  restart: always
  environment:
    MYSQL_ROOT_PASSWORD=[已脱敏]
  ports:
   - '3307:3306'
  volumes:
   - '/data/docker/volume/mysql/data:/var/lib/mysql'
   - '/data/docker/volume/mysql/logs:/logs'
   - '/data/docker/volume/mysql/conf:/etc/mysql/conf.d'
```
