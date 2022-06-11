---
id: "doc-7458f174f109"
title: "安装docker"
date: "2022-06-11T16:16:48.934000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Linux", "Go"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/an-zhuang-docker.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "e6f30853709ebccf8a75dd97ba9db94ed861ab324d17a8e03b9dae6ab2645ba4"
---

# 安装docker

> 原文：[安装docker](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/an-zhuang-docker.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:16｜日期依据：GitBook 页面更新时间

#### 1. 安装Docker的前提条件

> - CentOS 7 64位：系统内核3.10以上
> - CentOS 6.5 要求为64位、系统内核版本为 2.6.32-431以上
> - 查看内核版本命令：`uname -r`

#### 2. yum安装

```
yum update -y
yum -y install docker
systemctl start docker
```

```
新版本docker-ce安装
#
sudo yum install -y yum-utils \
device-mapper-persistent-data \
lvm2

#
sudo yum-config-manager \
--add-repo \
https://download.docker.com/linux/centos/docker-ce.repo
sudo yum-config-manager --enable docker-ce-nightly

#安装*最新版本*的Docker Engine-Community和containerd，或者转到下一步安装特定版本：

sudo yum install docker-ce docker-ce-cli containerd.io -y

systemctl start docker

systemctl enable docker

# yum list docker-ce --showduplicates| sort -r
```

**3. 检查启动是否成功**

出现如下输出即正常：

> Client:
> Version: 1.13.1
> API version: 1.26
> Package version: docker-1.13.1-75.git8633870.el7.centos.x86_64
> Go version: go1.9.4
> Git commit: 8633870/1.13.1
> Built: Fri Sep 28 19:45:08 2018
> OS/Arch: linux/amd64
>
> Server:
> Version: 1.13.1
> API version: 1.26 (minimum version 1.12)
> Package version: docker-1.13.1-75.git8633870.el7.centos.x86_64
> Go version: go1.9.4
> Git commit: 8633870/1.13.1
> Built: Fri Sep 28 19:45:08 2018
> OS/Arch: linux/amd64
> Experimental: false

**4. 更改安装目录**

centos 7 默认安装路径是 /var/lib/docker ，而这个是根目录，一般不会太大，修改存储目录到 /home/data/docker

进入/home/data/docker 目录建立软连接

进入 /var/lib 查看

**4. 配置国内镜像仓库源**

docker默认连接的镜像仓库是国外的，速度不是很快，所以我们可以配置国内的docker镜像仓库。

输入以下配置即可：

备用
七牛云加速器

保存、重启,设置开机自启。
