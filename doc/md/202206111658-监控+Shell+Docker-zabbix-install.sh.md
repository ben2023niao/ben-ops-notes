---
id: "doc-41bf5cc3ccf1"
title: "zabbix-install.sh"
date: "2022-06-11T16:58:24.873000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Shell", "Docker", "Nginx", "MySQL", "Zabbix", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu/zabbix-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "ad0b4768d91eca79b616528664be70d27647c7e07d5183d85af2263e712c1523"
---

# zabbix-install.sh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111658-%E7%9B%91%E6%8E%A7%2BShell%2BDocker-zabbix-install.sh.md)

> 原文：[zabbix-install.sh](https://xn--6o0a585a.gitbook.io/devops/jian-kong/zabbix-jian-kong-bu-shu/zabbix-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:58｜日期依据：GitBook 页面更新时间

```bash
#zabbix 服务端部署
docker run --name mysql-server -t \
      -e MYSQL_DATABASE="zabbix" \
      -e MYSQL_USER="zabbix" \
      -e MYSQL_PASSWORD="zabbix" \
      -e MYSQL_ROOT_PASSWORD="zabbix" \
      -d mysql:5.7  \
--character-set-server=utf8 --collation-server=utf8_bin

docker run --name zabbix-server-mysql -t \
      -e DB_SERVER_HOST="mysql-server" \
      -e MYSQL_DATABASE="zabbix" \
      -e MYSQL_USER="zabbix" \
      -e MYSQL_PASSWORD="zabbix" \
      -e MYSQL_ROOT_PASSWORD="zabbix" \
      --link mysql-server:mysql \
      -p 10051:10051 \
      -d zabbix/zabbix-server-mysql:latest

docker run --name zabbix-web-nginx-mysql -t \
      -e DB_SERVER_HOST="mysql-server" \
      -e MYSQL_DATABASE="zabbix" \
      -e MYSQL_USER="zabbix" \
      -e MYSQL_PASSWORD="zabbix" \
      -e MYSQL_ROOT_PASSWORD="zabbix" \
      --link mysql-server:mysql \
      --link zabbix-server-mysql:zabbix-server \
      -p 8888:80 \
      -d zabbix/zabbix-web-nginx-mysql:latest

#http://localhost:8080
#帐号密码:
#Admin
#zabbix

#添加zabbix 客户端，客户端不建议容器部署

rpm -i https://repo.zabbix.com/zabbix/3.4/rhel/7/x86_64/zabbix-release-3.4-2.el7.noarch.rpm
yum -y install zabbix-agent

#修改配置文件，指定一下 zabbix-server 的地址
#修改前更改路由使宿主机等到达server容器IP
route add -net 203.0.113.1/16 gw 203.0.113.1

[root@nginx ~]# vim /etc/zabbix/zabbix_agentd.conf
Server=203.0.113.1 #容器IP
UnsafeUserParameters=1
Include=/etc/zabbix/zabbix_agentd.d/*.conf
[root@nginx ~]# systemctl start zabbix-agent
```
