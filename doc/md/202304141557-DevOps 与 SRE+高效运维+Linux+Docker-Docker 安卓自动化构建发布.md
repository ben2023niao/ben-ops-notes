---
id: "doc-d49e807f37a4"
title: "Docker 安卓自动化构建发布"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Linux", "Docker", "Java", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649843.html"
---

# Docker 安卓自动化构建发布

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BLinux%2BDocker-Docker%20%E5%AE%89%E5%8D%93%E8%87%AA%E5%8A%A8%E5%8C%96%E6%9E%84%E5%BB%BA%E5%8F%91%E5%B8%83.md)

```bash
docker run -itd -p 6080:80 \
-e RESOLUTION=1920x1080 \
-e USER=android \
-e PASSWORD=[已脱敏] \
-e HTTP_PASSWORD=android \
-e VNC_PASSWORD=android \
-v /opt/ziben:/opt/ \
--name taihe_android_apk \
dorowu/ubuntu-desktop-lxde-vnc:bionic

以上代码默认拉取最新版的镜像latest版本，默认为最新版ubuntu20.04，当然也可以拉取其它版本的镜像，比如：
docker pull dorowu/docker-ubuntu-vnc-desktop:focal # 拉取Ubuntu 20.04 (latest)
docker pull dorowu/docker-ubuntu-vnc-desktop: focal-lxqt: # 拉取Ubuntu 20.04 LXQt
docker pull dorowu/docker-ubuntu-vnc-desktop: bionic: # 拉取Ubuntu 18.04
docker pull dorowu/docker-ubuntu-vnc-desktop: bionic-lxqt: # 拉取Ubuntu 18.04 LXQt
docker pull dorowu/docker-ubuntu-vnc-desktop: xenial: # 拉取Ubuntu 16.04 (deprecated)
docker pull dorowu/docker-ubuntu-vnc-desktop: trusty: # 拉取Ubuntu 14.04 (deprecated)
```

![文档配图](../media/97435935987634e48c.png)
![文档配图](../media/be0cfa23b8190c07f7.png)

```bash
#上传 android-studio-2021.1.1.22-linux.tar.gz 安装 jdk环境
cd /opt ; apt update ; apt -y install wget git vim openjdk-17* ; java -version ; javac -version
#解压安装 android-studio
tar -zvxf android-studio-2021.1.1.22-linux.tar.gz
bash /opt/android-studio/bin/studio.sh
```

![文档配图](../media/a4807d6c0099e0b306.png)
![文档配图](../media/2b4e81cae2e1614cc2.png)

![文档配图](../media/c70defdd2d84ba3a2c.png)
导出docker
![文档配图](../media/5a83a569fee8f54d12.png)

```bash
docker export taihe_android_apk > taihe_android_apk.tar
```

新服务器导入镜像
![文档配图](../media/ef71ba8f52ea3107c9.png)

```bash
docker import - taihe_android_apk < taihe_android_apk.tar

启动镜像
docker run -itd -p 6080:80 -e RESOLUTION=1920x1080 -e USER=android -e PASSWORD=[已脱敏] -e HTTP_PASSWORD=android -e VNC_PASSWORD=android --name taihe_android_apk taihe_android_apk /bin/bash
```
