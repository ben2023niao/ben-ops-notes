---
id: "doc-ac5a7764979d"
title: "部署etcd节点"
date: "2022-06-11T16:30:47.166000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Linux", "Go", "Kubernetes", "安全运维"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/bu-shu-etcd-jie-dian.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "f3251f90fa9d29aa52d1ad94f3979e65542cd6679b4e4d61115d9d3131269c95"
---

# 部署etcd节点

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111630-%E5%AE%B9%E5%99%A8%E4%B8%8E%E4%BA%91%E5%8E%9F%E7%94%9F%2BDocker%2BLinux-%E9%83%A8%E7%BD%B2etcd%E8%8A%82%E7%82%B9.md)

> 原文：[部署etcd节点](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/bu-shu-etcd-jie-dian.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:30｜日期依据：GitBook 页面更新时间

简介：Etcd 是什么

- etcd是一个分布式可靠的键值存储，用于分布式系统的最关键数据，重点是：

1.*简单*：定义明确，面向用户的API（gRPC）

2.*安全*：具有可选客户端证书身份验证的自动TLS

3.*快速*：基准测试10,000次/秒

4.*可靠*：使用Raft一致性算法分布集群

- etcd是用Go编写的，使用[Raft](https://raft.github.io/)一致性算法来管理高度可用的复制日志。
- etcd被[许多公司](https://github.com/coreos/etcd/blob/master/Documentation/production-users.md)用于[生产](https://github.com/coreos/etcd/blob/master/Documentation/production-users.md)，开发团队在关键部署场景中支持它，其中etcd经常与[Kubernetes](http://kubernetes.io/)，[locksmith](https://github.com/coreos/locksmith)，[vulcand](https://github.com/vulcand/vulcand)，[Doorman](https://github.com/youtube/doorman)等许多应用程序配合使用。通过**严格的测试**进一步确保可靠性。
- 有关简单的命令行客户端，请参阅[etcdctl](https://github.com/coreos/etcd/tree/master/etcdctl)(etcdctl --helper)

#### 一、ETCD单机部署

**1、下载二进制包**

<https://github.com/coreos/etcd/releases>

```
wget https://github.com/etcd-io/etcd/releases/download/v3.3.12/etcd-v3.3.12-linux-arm64.tar.gz
```

**2、解压缩**

```
tar -zxvf etcd-v3.3.12-linux-arm64.tar.gz
```

**3、设置环境变量**

```
export ETCDPATH="/home/etcd/etcd-v3.3.12-linux-amd64"

export ETCDCTL_API=3

export PATH="$PATH:$ETCDPATH"
```

**4、启动etcd**

**5、客户端测试**

#### 二、docker单机部署ETCD

**1、拉取etcd镜像**

**2、设置环境变量和监听地址**

**3、运行etcd容器**

容器退出自动删除rm

容器停止总是重启

其他状态：

- no，默认策略，在容器退出时不重启容器
- on-failure，在容器非正常退出时（退出状态非0），才会重启容器
- on-failure:3，在容器非正常退出时重启容器，最多重启3次
- always，在容器退出时总是重启容器
- unless-stopped，在容器退出时总是重启容器，但是不考虑在Docker守护进程启动时就已经停止了的容器

**4、客户端测试**

#### 三、Etcd本地集群（使用goreman管理）

**1、下载etcd二进制包&&设置环境变量&&参考Etcd单机部署**

**2、安装goreman，安装goreman前需要安装go环境和git。**

**3、安装go环境**

**4、安装git**

**5、安装 goreman**

下载后的文件在`export GOPATH=/home/go/data`设置的路径中

**6、编写Procfile（管理集群）**

<https://github.com/coreos/etcd/blob/master/Procfile>

**7、启动etcd（goreman runlist）**

#### 四、docker cluster（集群）

**8、etcd集群**

**docker netword**

**9、etcd cluster**
