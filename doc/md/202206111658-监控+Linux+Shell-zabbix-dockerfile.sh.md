---
id: "doc-a16175cd4c16"
title: "zabbix-dockerfile.sh"
date: "2022-06-11T16:58:53.618000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Linux", "Shell", "Docker", "Nginx", "MySQL", "Zabbix", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu/zabbix-dockerfile.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "f07afe7645b5e0b4803a410734092c312a4d8f51509090f834250fb9cefea294"
---

# zabbix-dockerfile.sh

> 原文：[zabbix-dockerfile.sh](https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu/zabbix-dockerfile.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:58｜日期依据：GitBook 页面更新时间

```bash
#1 mysql

mkdir /data/docker/mysql -p & cd /data/docker/mysql
#vim Dockerfile
FROM mysql:5.7
ENV LANG en_US.utf8
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone \

docker build -t debian-mysql5.7 .

docker run --hostname mysql --name debian-mysql-5.7 -t \
> -e MYSQL_USER="zabbix" \
> -e MYSQL_DATABASE="zabbix" \
> -e MYSQL_PASSWORD=[已脱敏] \
> -e MYSQL_ROOT_PASSWORD=[已脱敏] \
> -v /data/mysql:/var/lib/mysql:rw \
> -d debian-mysql5.7

#2 zabbix server
#cat Dockerfile
FROM zabbix/zabbix-server-mysql:latest
ENV LANG en_US.utf8
RUN apk add -U tzdata
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone \

docker build -t zabbix-server .

docker run --name zabbix-server -t \
> -p 10051:10051 \
> --hostname zabbix-server \
> -e DB_SERVER_HOST="debian-mysql-5.7" \
> -e MYSQL_DATABASE="zabbix" \
> -e MYSQL_USER="zabbix" \
> -e MYSQL_PASSWORD=[已脱敏] \
> -e MYSQL_ROOT_PASSWORD=[已脱敏] \
> -e ZBX_JAVAGATEWAY="zabbix-java-gateway" \
> --link debian-mysql-5.7:mysql \
> --link zabbix-java-gateway:zabbix-java-gateway \
> -d zabbix-server

#3 zabbix web
#cat Dockerfile

FROM zabbix/zabbix-web-nginx-mysql:latest
ENV LANG en_US.utf8
RUN apk add -U tzdata
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone \

docker build -t zabbix-web .

docker run --name zabbix-web -t \
> -p 80:80 \
> --hostname zabbix-web \
> -e PHP_TZ="Asia/Shanghai" \
> -e DB_SERVER_HOST="debian-mysql-5.7" \
> -e MYSQL_DATABASE="zabbix" \
> -e MYSQL_USER="zabbix" \
> -e MYSQL_PASSWORD=[已脱敏] \
> -e MYSQL_ROOT_PASSWORD=[已脱敏] \
> --link debian-mysql-5.7:mysql \
> --link zabbix-server:zabbix-server \
> -d zabbix-web

#安装 zabbix-agent
rpm -i https://repo.zabbix.com/zabbix/3.4/rhel/7/x86_64/zabbix-release-3.4-2.el7.noarch.rpm
yum -y install zabbix-agent

#配置文件
#[root@nginx ~]# vim /etc/zabbix/zabbix_agentd.conf
Server=203.0.113.1 #容器IP
UnsafeUserParameters=1
Include=/etc/zabbix/zabbix_agentd.d/*.conf
#[root@nginx ~]# systemctl start zabbix-agent
```
