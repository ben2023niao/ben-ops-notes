---
id: "doc-229ad7a4427b"
title: "zookeeper集群"
date: "2022-06-11T16:25:37.322000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Linux", "Shell", "数据库恢复", "安全运维", "故障排查", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-zookeeper/zookeeper-ji-qun.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "998dd04caae22a636af237110041b53694865339af56ac5650e610886e73ce06"
---

# zookeeper集群

> 原文：[zookeeper集群](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-zookeeper/zookeeper-ji-qun.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:25｜日期依据：GitBook 页面更新时间

三台主机：

- 主机一：203.0.113.1
- 主机一：203.0.113.1
- 主机一：203.0.113.1

1、下载镜像

```bash
docker pull zookeeper:3.4.12
```

2、在主机上建立挂载目录和zookeeper配置文件

```
mkdir -p /home/data/zookeeper_data/conf \
mkdir -p /home/data/zookeeper_data/data \
cd /home/data/zookeeper_data/conf
touch zoo.cfg
vi zoo.cfg
```

三台主机上的zoo.cfg配置信息如下：

```
clientPort=2181
dataDir=/data
dataLogDir=/data/log
tickTime=2000
initLimit=5
syncLimit=2
autopurge.snapRetainCount=3
autopurge.purgeInterval=0
maxClientCnxns=60
server.0=203.0.113.1:2888:3888
server.1=203.0.113.1:2888:3888
server.2=203.0.113.1:2888:3888
```

3、在主机一上为自己分配server id，命令如下：

在主机二上为自己分配server id，命令如下：

在主机二上为自己分配server id，命令如下：

4、三台主机依次启动容器：

命令说明：

- --network host: 使用主机上的网络配置，如果不用这种模式，而用默认的bridge模式，会导致容器跨主机间通信失败
- -v /data/zookeeper_data/data:/data：主机的数据目录挂载到容器/data下
- -v /data/zookeeper_data/conf:/conf： 主机的配置目录挂载到容器的/conf下，容器内的zkServer.sh默认会读取/conf/zoo.cfg下的配置

都启动完成后，每台主机的2181/2888/3888端口都会开放出来了

5、验证

使用windows工具zoolnspector

6、排错
前面两台发现没有问题，后面有台机器报错。
权限不足，发现用户不一样：

根据后面的信息我查到是因为selinux的原因。

这是因为开启了SELinux，解决办法：
①直接将SELinux的工作模式设置成 disabled，这样就不会出现策略拦截问题了，但是这样的话我们的系统就没有SELinux安全防护了

②通过 restorecon 或者 chcon 命令来修复我们的文件上下文信息

命令 restorecon 可以用来恢复文件默认的上下文：

//-R 表示递归，如果是目录，则该目录下的所有子目录、文件都会得到修复
命令 chcon 可以改变文件的上下文信息，通常我们使用一个参照文件来进行修改：
