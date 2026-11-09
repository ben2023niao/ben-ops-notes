---
id: "doc-63368c81b7e1"
title: "搭建Zookeeper"
date: "2022-06-11T16:20:55.869000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-zookeeper.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "3ac7a14da3b369632f28dcbd1f9904e23c078c3272beddb575ad58fb40f4c1c0"
---

# 搭建Zookeeper

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111620-%E5%AE%B9%E5%99%A8%E4%B8%8E%E4%BA%91%E5%8E%9F%E7%94%9F%2BDocker%2BShell-%E6%90%AD%E5%BB%BAZookeeper.md)

> 原文：[搭建Zookeeper](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-zookeeper.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:20｜日期依据：GitBook 页面更新时间

**1. 前提是Docker已经安装好了**

**2.拉取Zookeeper镜像**

```bash
docker pull zookeeper
#使用命令查看拉取到的镜像
docker images
```

**3.启动Zookeeper**

```bash
#创建宿主机挂载目录
mkdir -p /home/service/zookeeper/conf
mkdir -p /home/service/zookeeper/data
mkdir -p /home/service/zookeeper/log

docker run -d --name zk --restart always zookeeper

#把容器中的配置文件复制出来
docker cp -a zk:/conf/zoo.cfg /home/service/zookeeper/conf/zoo.cfg

docker stop zk
docker rm zk
docker run -d --name zk --restart always \
-p 2181:2181 -p 2888:2888 -p 3888:3888 \
-v /home/service/zookeeper/conf/zoo.cfg:/conf/zoo.cfg \
-v /home/service/zookeeper/data:/data \
-v /home/service/zookeeper/log:/datalog \
zookeeper
```

> 完成，三个端口分别是：zookeeper客户端端口，跟随端口，选择端口
