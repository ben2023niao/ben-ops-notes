---
id: "doc-82bc53467494"
title: "1 Zabbix监控K8S 环境准备和说明"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "Kubernetes", "SQL注入", "监控告警", "Zabbix", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/84423002.html"
---

# 1 Zabbix监控K8S 环境准备和说明

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BKubernetes%2BSQL%E6%B3%A8%E5%85%A5-1%20Zabbix%E7%9B%91%E6%8E%A7K8S%20%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87%E5%92%8C%E8%AF%B4%E6%98%8E.md)

首先你确保已经部署好了一套[K8S](https://www.dqzboy.com/tag/k8s "View all posts in K8S")集群，然后我们需要在`[zabbix](https://www.dqzboy.com/tag/zabbix "View all posts in zabbix")-server`端安装部署`python3`，默认Cent OS系统中使用的python2，在监控服务端节点上安装`python3`

```
1、下载python3安装包
[root@zabbix-server ~]# wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
2、安装依赖包文件
[root@zabbix-server ~]# yum -y install zlib zlib-devel bzip2 bzip2-devel ncurses ncurses-devel readline readline-devel openssl openssl-devel openssl-static xz lzma xz-devel sqlite sqlite-devel gdbm gdbm-devel tk tk-devel libffi libffi-devel gcc make glibc-kernheaders
3、创建目录并安装
[root@zabbix-server ~]# mkdir /usr/local/python3

#解压至当前目录下即可
[root@zabbix-server ~]# tar -zxvf Python-3.7.4.tgz

#编译安装
[root@zabbix-server ~]# cd Python-3.7.4
[root@zabbix-server Python-3.7.4]# ./configure --prefix=/usr/local/python3 --with-ssl --enable-shared CFLAGS=-fPIC
[root@zabbix-server Python-3.7.4]# make && make install
4、建立执行文件软链
[root@zabbix-server ~]# ln -sv /usr/local/python3/bin/python3.7 /usr/bin/python3
[root@zabbix-server ~]# ln -sv /usr/local/python3/bin/pip3.7 /usr/bin/pip3
问题处理：找不到libpython3.7m.so.1.0依赖包
[root@zabbix-server ~]# find / -name libpython3.7m.so.1.0
/root/Python-3.7.4/libpython3.7m.so.1.0
/usr/local/python3/lib/libpython3.7m.so.1.0

[root@zabbix-server ~]# echo "/usr/local/python3/lib " > /etc/ld.so.conf.d/python3.7.conf
[root@zabbix-server ~]# ldconfig
[root@zabbix-server ~]# ldd /usr/local/python3/bin/python3.7
5、zabbix-sender安装
#安装yum源,zabbix服务端一般都会安装了yum源，如果没有的则需要执行
[root@zabbix-server ~]# rpm -Uvh https://repo.zabbix.com/zabbix/5.0/rhel/7/x86_64/zabbix-release-5.0-1.el7.noarch.rpm

#更新yum仓库
[root@zabbix-server ~]# yum repolist

#安装zabbix-sender
[root@zabbix-server ~]# yum -y install zabbix-sender

#检测zabbix-sender命令可用
[root@zabbix-server ~]# zabbix_sender -V
zabbix_sender (Zabbix) 5.0.7
```
