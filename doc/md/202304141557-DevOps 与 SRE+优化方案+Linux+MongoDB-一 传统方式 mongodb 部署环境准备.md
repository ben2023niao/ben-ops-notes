---
id: "doc-f491e7c79c2a"
title: "一 传统方式 mongodb 部署环境准备"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "MongoDB", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/84414079.html"
---

# 一 传统方式 mongodb 部署环境准备

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BMongoDB-%E4%B8%80%20%E4%BC%A0%E7%BB%9F%E6%96%B9%E5%BC%8F%20mongodb%20%E9%83%A8%E7%BD%B2%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87.md)

```
ip地址                    主机名                               角色
203.0.113.1      mongodb-master01                        副本集主节点
203.0.113.1      mongodb-slave01                         副本集副本节点
203.0.113.1      mongodb-slave02                         副本集副本节点
三个节点机均设置好各自的主机名，并如下设置好hosts绑定
[root@mongodb-master01 ~]# cat /etc/hosts
............
203.0.113.1    mongodb-master01
203.0.113.1    mongodb-slave01
203.0.113.1    mongodb-slave02

三个节点机均关闭selinux，为了测试方便，将iptables也关闭
[root@mongodb-master01 ~]# setenforce 0
[root@mongodb-master01 ~]# cat /etc/sysconfig/selinux
...........
SELINUX=disabled

[root@mongodb-master01 ~]# iptables -F
[root@mongodb-master01 ~]# /etc/init.d/iptables stop
[root@mongodb-master01 ~]# /etc/init.d/iptables stop
iptables: Setting chains to policy ACCEPT: filter          [  OK  ]
iptables: Flushing firewall rules:                         [  OK  ]
iptables: Unloading modules:                               [  OK  ]
```
