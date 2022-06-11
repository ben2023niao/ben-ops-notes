---
id: "doc-36ab3198856d"
title: "搭建Jenkins"
date: "2022-06-11T16:20:18.631000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Linux", "Shell", "Nginx", "自动化"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-jenkins.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "d83804a4881ab20414f9effeda4c1a75c01b6f2da1c9c42d8b87958ce18d4e17"
---

# 搭建Jenkins

> 原文：[搭建Jenkins](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-jenkins.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:20｜日期依据：GitBook 页面更新时间

**1. 前提是Docker已经安装好了**

**2.拉取Jenkins镜像**

```bash
docker pull jenkins/jenkins:lts
#使用命令查看拉取到的镜像
docker images
```

**3. 运行JenKins镜像**

```bash
docker run -d -v jenkins_home:/home/service/jenkins -p 7070:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts
```

参数说明

- `-d` 以守护模式运行镜像，也就是后台运行
- `-v` 把Jenkins容器内的目录挂载到宿主机的目录
- `-p` 宿主机端口映射的镜像端口，左边是宿主机端口，右边是镜像端口，`7070`是Jenkins访问端口，另外还要暴露一个`tcp`端口`50000`
- `--name`给容器起一个唯一的别名

启动后输入`docker ps -a`即可查看运行的容器：

**4. 访问Jenkins**

浏览器访问`http://ip:7070`即可进入Jenkins

但是我希望通过nginx转发进入jenkins，所以接下来配置nginx转发到Jenkins

没有安装nginx的可以看这里-->CentOS 7使用Docker搭建Nginx

**5.实现同主机不同容器通信**

刚开始配的时候，傻傻的直接用nginx转发到7070端口，结果发现怎么都访问不到，琢磨半天之后突然想起来前几天看的【Docker技术入门与实战第二版】中说的容器通信，让我恍然大悟

容器通信方式很多种，我这里选择docker的link机制来访问

停止并删除nginx容器

首先修改nginx的配置文件：

在nginx容器启动命令使用--link 容器名 来访问Jenkins容器

然后访问`https://ip`访问即可,第一次进入需要登陆

密码需要进入jenkins容器里面获取

得到的密码登陆即可

**6. 配置Jenkins**

> 想方便的可以直接安装推荐的插件，我选择自定义安装
> 之后慢慢等待安装完成即可，时间有点久

**7.给jenkins配置一个二级域名**
