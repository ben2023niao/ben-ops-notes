---
id: "doc-2c747ef46e1c"
title: "搭建Nginx"
date: "2022-06-11T16:19:38.787000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "Nginx", "MySQL", "自动化", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-nginx.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "43067541a5550106491b5ca497c658681a73d977e50e0625b1810e8c5406d87f"
---

# 搭建Nginx

> 原文：[搭建Nginx](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/da-jian-nginx.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:19｜日期依据：GitBook 页面更新时间

**1. 前提是Docker已经安装好了**

**2.拉取Nginx镜像**

```bash
docker pull nginx
#使用命令查看拉取到的镜像
docker images
```

**3. 运行Nginx镜像**

```bash
docker run -d -p 80:80 --name nginx nginx
```

参数说明

- `-d` 以守护模式运行镜像，也就是后台运行
- `-p` 宿主机端口映射的镜像端口，左边是宿主机端口，右边是镜像端口，`80`是Nginx访问端口
- `--name`给容器起一个唯一的别名

启动后输入`docker ps -a`即可查看运行的容器：

**4. 访问Nginx**

浏览器访问`http://ip`即可,出现以下页面说明运行成功

**5. 配置Nginx**

- 我们首先需要在宿主机创建用于存放nginx日志、配置文件和相关静态资源的目录，并将其挂载到容器内对应路径。
- 后续更新我们只需要更改宿主机目录下的配置文件或者静态文件就可以更新容器内资源，这样可以确保容器挂掉只需要重新启动一个容器挂载上数据去就完美无缺的还原，这也是容器轻量快速方便的原因。不只是nginx容器，其余的像mysql容器也一定要记得挂载/data数据文件，防止容器宕掉丢失数据。

```
mkdir -p /home/service/nginx/log
mkdir -p /home/service/nginx/conf
mkdir -p /home/service/nginx/conf.d
mkdir -p /home/service/nginx/static
mkdir -p /home/service/nginx/ssl
```

然后从Nginx容器中复制一份配置文件到宿主机刚刚创建的conf目录

可以看到已经有了

查看一下内容

上图可以看出，这个配置文件还引入了其他的配置文件，所以我们需要把`include`引入的文件也复制一份到宿主机，但是我们不知道那些文件叫什么，所以我们需要进入容器内查看

可以看到里面有个default.conf文件

我们需要把这个文件复制到宿主机，使用`exit`命令退出容器

还记得我们前面访问nginx的时候那个页面吗？是的，那个页面也要复制到宿主机

**6. 修改配置文件**

开始修改宿主机上复制出来的conf文件，首先修改`nginx.conf`，修改配置文件修改后的结果：

查看`default.conf`

**停止上次的nginx容器并删除容器**

**重新启动一个nginx镜像**

`-v`的意思就是把宿主机目录挂载到冒号后面的容器目录

`--link`用于连接容器，后面是零一个容器的唯一name，这样nginx就可以在配置文件使用`jenkins:端口`配置了

**此处多监听了一个443端口，用于以后配置https**
修改一下nginx默认的`index.html`，更有辨识度

**7.配置Https访问**

我是在阿里云申请了免费的一年ssl证书，大家可以百度一下，下载的是nginx的

并且在其中加入了许多优化的配置,`nginx.conf` ：

> 注意：这里更新的是宿主机上的nginx.conf
>
> 然后进入容器重启nginx即可
> 也可以不用进入容器重启，直接重启容器也可以
> `docker restart nginx`

配置完成
