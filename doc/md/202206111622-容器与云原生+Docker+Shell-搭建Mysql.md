---
id: "doc-8354620da03a"
title: "搭建Mysql"
date: "2022-06-11T16:22:28.820000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "MySQL", "数据库恢复", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-mysql.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "07db4a516336589b8387fbf9e16ca71385e753f0eaba6976f56d2cff835259a3"
---

# 搭建Mysql

> 原文：[搭建Mysql](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-mysql.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:22｜日期依据：GitBook 页面更新时间

**1. 前提是Docker已经安装好了**

**2.拉取mysql镜像**

```bash
docker pull mysql:5.7
docker images
```

- 宿主机创建几个文件夹用于容器文件挂载

```
mkdir -p /home/service/mysql/data
mkdir -p /home/service/mysql/conf/my.cnf
```

在my.cnf追加如下数据

```
[mysqld]
user=mysql
character-set-server=utf8
default_authentication_plugin=mysql_native_password
default-time_zone = '+8:00'
[client]
default-character-set=utf8
[mysql]
default-character-set=utf8
```

- 然后运行命令启动mysql

> 命令讲解
> `-p` 3306:3306：将容器的3306端口映射到主机的3306端口
> `-e` MYSQL_ROOT_PASSWORD=[已脱敏]
> `-e` TZ=Asia/Shanghai 修改容器默认时区为上海
> `-v`=/mysqltest/config/my.cnf:/etc/my.cnf：映射配置文件
> `-v`=/mysqltest/data:/var/lib/mysql：映射数据目录
> 注意：不同mysql版本可能配置文件目录和路径不一样，mysql5.7的容器路径为 /etc/mysql/mysql.conf.d/mysqld.cnf。

- 进入容器

- 登陆mysql

- 创建mysql用户

- 然后就可以使用admin用户登陆了，因为mysql8与mysql5.7授权有一些不一样，mysql必须先创建用户才能授权，不然会出错。

#### 3、修改时区

加入如下一行

或者直接追加写入

- 修改时区

在我们备份数据库的时候，有用到时间因素，但是 Docker 容器中默认为 +0 时区，而我们是 +8 时区，我们将宿主机的时区文件映射过去就行。

退出容器重启容器

查看时区命令
