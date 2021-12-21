---
id: "doc-2845c9d2c4d4"
title: "zabbix监控部署"
date: "2021-12-21T15:30:01.526000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Shell", "Docker", "Nginx", "MySQL", "Zabbix", "监控告警"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "cf026bb5a44dd88362bc6cd9e6ae77cb60b51d1acc54b9e032b514177521abfb"
---

# zabbix监控部署

> 原文：[zabbix监控部署](https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-21 15:30｜日期依据：GitBook 页面更新时间

1、部署zabbix-server

```bash
docker run --name zabbix-mysql-server --hostname zabbix-mysql-server \
-e MYSQL_ROOT_PASSWORD="123456" \
-e MYSQL_USER="zabbix" \
-e MYSQL_PASSWORD="123456" \
-e MYSQL_DATABASE="zabbix" \
-p 3306:3306 \
-d mysql:5.7 --character-set-server=utf8 --collation-server=utf8_bin
```

```bash
docker run --name zabbix-server-mysql --hostname zabbix-server-mysql \
--link zabbix-mysql-server:mysql \
-e DB_SERVER_HOST="mysql" \
-e MYSQL_USER="zabbix" \
-e MYSQL_DATABASE="zabbix" \
-e MYSQL_PASSWORD="123456" \
-v /etc/localtime:/etc/localtime:ro \
-v /data/docker/zabbix/alertscripts:/usr/lib/zabbix/alertscripts \
-v /data/docker/zabbix/externalscripts:/usr/lib/zabbix/externalscripts \
-p 10051:10051 \
-d zabbix/zabbix-server-mysql
```

```bash
docker run --name zabbix-web-nginx-mysql --hostname zabbix-web-nginx-mysql \
--link zabbix-mysql-server:mysql \
--link zabbix-server-mysql:zabbix-server \
-e DB_SERVER_HOST="mysql" \
-e MYSQL_USER="zabbix" \
-e MYSQL_PASSWORD="123456" \
-e MYSQL_DATABASE="zabbix" \
-e ZBX_SERVER_HOST="zabbix-server" \
-e PHP_TZ="Asia/Shanghai" \
-p 8000:80 \
-p 8443:443 \
-d zabbix/zabbix-web-nginx-mysql
```

浏览器访问 <http://203.0.113.1:8000> 默认登录 username: Admin password: [已脱敏]

2、部署zabbix-agent

说明下，mysql没做数据卷的映射，nginx也没做数据卷的映射，在实际生产环境下，最好做数据映射。防止数据丢失。

docker-zabbbix-agent的安装以及链接zabbix-server 最后需要在web端将，zabbix-agent添加到zabbix-server的host列表里面。
