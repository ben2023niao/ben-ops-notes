---
id: "doc-d37e824255b8"
title: "常见下载器 docker 启动方式"
date: "2022-02-05T15:14:05.264000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "自动化"]
tags: ["自动化", "Linux", "Shell", "Docker"]
source: "https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/chang-jian-xia-zai-qi-docker-qi-dong-fang-shi.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "ea6e5836133342e68479639395270f9ab73475658c62b4f3a43eb4b3304b26eb"
---

# 常见下载器 docker 启动方式

> 原文：[常见下载器 docker 启动方式](https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/chang-jian-xia-zai-qi-docker-qi-dong-fang-shi.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-02-05 15:14｜日期依据：GitBook 页面更新时间

经常在维护的`BT`离线程序的`Docker`镜像 `Aria2`、`utorrent`、`Deluge`、`Transmission`、`Rutorrent`、`Qbittorrent`

### 安装Docker

首先安装下面程序之前，需要在服务器上安装`Docker`环境，使用命令：

```
#CentOS 6系统
rpm -iUvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum update -y
yum -y install docker-io
service docker start
chkconfig docker on

#CentOS 7、Debian、Ubuntu系统
curl -sSL https://get.docker.com/ | sh
systemctl start docker
systemctl enable docker
```

### 安装Aria2

**镜像来源：**<https://hub.docker.com/r/onisuly/aria2-with-webui>

先安装`Docker`，然后执行以下命令：

```bash
docker run --restart=always --name aria2-ariang -d \
-p 6060:80 \
-p 6800:6800 \
-e SECRET=[已脱敏] \
-v ~/aria2/down:/data \
-v ~/aria2/conf:/conf \
onisuly/aria2-with-webui
```

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

如果你不想用了，可以使用以下命令卸载：

### 安装utorrent

**镜像来源：**<https://hub.docker.com/r/ekho/utorrent>

先安装`Docker`，然后执行以下命令：

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

如果你不想用了，可以使用以下命令卸载：

### 安装Deluge

**镜像来源：**<https://hub.docker.com/r/linuxserver/deluge>

先安装`Docker`，然后执行以下命令：

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

进入界面后，记得点击上方的`Preferences`，将下载目录设置为`/downloads`。

如果你不想用了，可以使用以下命令卸载：

### 安装Transmission

**镜像来源：**<https://hub.docker.com/r/linuxserver/transmission>

先安装`Docker`，然后执行以下命令：

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

如果你不想用了，可以使用以下命令卸载：

### 安装Rutorrent

**镜像来源：**<https://hub.docker.com/r/linuxserver/rutorrent>

先安装`Docker`，然后执行以下命令：

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

如果你不想用了，可以使用以下命令卸载：

### 安装Qbittorrent

**镜像来源：**<https://hub.docker.com/r/linuxserver/qbittorrent>

先安装`Docker`，然后执行以下命令：

安装完成后，相关信息如下：

`CentOS`系统安装后，可能还需要开启相应的端口，大致如下：

如果你不想用了，可以使用以下命令卸载：
