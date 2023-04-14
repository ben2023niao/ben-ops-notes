---
id: "doc-b1efa428b8f4"
title: "Docker 部署 MySQL(8和5.7）"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "MySQL", "Docker", "SQL注入", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/79927240.html"
---

# Docker 部署 MySQL(8和5.7）

**安装 MySQL**

**拉取镜像**

使用下面的命令拉取 MySQL 数据库的镜像：

| 123 | `$` `sudo` `docker pull mysql` `# 拉取最新版本的镜像，当前为 MySQL 8 版本，tag 为 latest` `$` `sudo` `docker pull mysql:5.7` `# 指定拉取 MySQL 5.7 版本` |

| --- | --- |

也可以使用搜索命令，查找其他的 MySQL 相关镜像，其中有标识 Stars 数，即受欢迎程度。

| 1 | `$` `sudo` `docker search mysql` |

| --- | --- |

运行 MySQL

| 1234567 | `$` `sudo` `docker run -p 3306:3306 \``--name mysql \``-``v` `$PWD``/conf``:``/etc/mysql/conf``.d \``-``v` `$PWD``/logs``:``/logs` `\``-``v` `$PWD``/data``:``/var/lib/mysql` `\``-e MYSQL_ROOT_PASSWORD=your-password \``-d mysql` |

| --- | --- |

命令说明：

- -p 3306:3306 ：将容器的 3306 端口映射到主机的 3306 端口。
- -v $PWD/[conf:/etc/mysql/conf.d](http://conf/etc/mysql/conf.d) ：将主机当前目录下的 conf/my.cnf 挂载到容器的 /etc/mysql/my.cnf。
- -v $PWD/[logs:/logs](http://logs/logs) ：将主机当前目录下的 logs 目录挂载到容器的 /logs。
- -v $PWD/[data:/var/lib/mysql](http://data/var/lib/mysql) ：将主机当前目录下的data目录挂载到容器的 /var/lib/mysql 。
- -e MYSQL_ROOT_PASSWORD=your-password ：初始化 root 用户的密码,建议使用复杂度高的密码。
- -d mysql : 要部署的镜像名，如果是5.7版本的话，这里则为mysql:5.7

**配置远程访问**

远程访问 MySQL 属于基本配置，但是在配置的时候要注意安全性问题，否则将存在安全性隐患，尤其是企业用服务器更要注重安全性。

并且需要注意服务器防火墙要开启 3306 端口，服务器提供商的安全组中也需要开启，否则会无法访问哦。

要配置远程访问，先要打开 MySQL 的控制终端，使用下面的命令开启：

| 12345 | ``` $ sudo docker exec -it mysql bash # 进入 MySQL 容器   $ mysql -uroot -p # 登录 MySQL，执行后输入密码进入 MySQL   $ use mysql; # 选择使用 mysql 数据库 ``` |

| --- | --- |

**MySQL 8 配置**

| 1234567891011121314 | `CREATE` `USER` `'username'``@``'%'` `IDENTIFIED` `BY` `'password'``;``# 创建一个账号，用来进行远程访问；``# {usernama} 是远程访问登录的用户名，不建议用 root;``# {``password``} 是远程访问的登录密码;``#` `'%'``代表的是所有IP，如果可以尽量设置指定 IP 或 IP 段` `GRANT` `ALL` `ON` `*.*` `TO` `'username'``@``'%'``;``# 赋予所有权限给之前创建的账号` `ALTER` `USER` `'username'``@``'%'` `IDENTIFIED` `WITH` `mysql_native_password` `BY` `'password'``;``# 确认使用这里的密码登录此账号` `FLUSH` `PRIVILEGES``;``# 刷新权限` |

| --- | --- |

完整命令如下所示：

| 123456789101112 | `CREATE` `USER` `'james'``@``'%'` `IDENTIFIED` `BY` `'123456asd'``;``# 创建一个账号-james，用来进行远程访问；` `GRANT` `ALL` `ON` `*.*` `TO` `'james'``@``'%'``;``# 赋予所有权限给之前创建的账号:james` `ALTER` `USER` `'james'``@``'%'` `IDENTIFIED` `WITH` `mysql_native_password` `BY` `'123456asd'``;``# 确认使用密码{123456asd}登录此账号{james}``# 密码尽量复杂，安全性更高。` `FLUSH` `PRIVILEGES``;``# 刷新权限` |

| --- | --- |

配置完毕后，使用 Navicat 工具或其他工具进行连接测试即可。

**MySQL 5.7 配置**

| 1234567 | `GRANT` `ALL` `PRIVILEGES` `ON` `*.*` `TO` `'username'``@``'%'` `IDENTIFIED` `BY` `'password'` `WITH` `GRANT` `OPTION``;``# {usernama} 是远程访问登录的用户名，不建议用 root;``# {``password``} 是远程访问的登录密码;``#` `'%'``代表的是所有IP，如果可以尽量设置指定 IP 或 IP 段` `FLUSH` `PRIVILEGES``;``# 刷新权限` |

| --- | --- |

配置完毕后，使用 Navicat 工具或其他工具进行连接测试即可。

注：如果无法访问请注意防火墙 3306 端口是否开启，服务器提供商的安全组中的端口是否开启。
