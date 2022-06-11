---
id: "doc-54787c2a2932"
title: "java容器运行外置jar"
date: "2022-06-11T16:28:17.259000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/java-rong-qi-yun-xing-wai-zhi-jar.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "20b779bda78b1c2fae3472cf031bc9c65f8e7a581ecdd27ad671ae5d17964d0a"
---

# java容器运行外置jar

> 原文：[java容器运行外置jar](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/java-rong-qi-yun-xing-wai-zhi-jar.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:28｜日期依据：GitBook 页面更新时间

#### 下载java的镜像

```bash
docker pull java:openjdk-8
```

#### spring boot

> 打包后的富jar 放入指定的目录。

- 执行命令创建容器

> 内部路径/opt/pj/business.jar，容器路径/usr/business.jar。 执行jar java -jar /usr/business.jar 暴露端口-p

```bash
docker run -d  -v /opt/pj/business.jar:/usr/business.jar --name business java:openjdk-8 -p 8888:8888 java -jar /usr/business.jar
```

#### 每次升级的时候

1. 停止stop容器
2. 替换/opt/pj/的jar
3. 启动start容器

Docker 配置参数说明

- name 用于容器的名称，可以包括一个标签
- tags 一组标签参数，在应用标签之前，name 中的标签都会被剥离;默认为空集（可选）
- dockfile 用于构建镜像Dockerfile文件，默认为 project.file('Dockerfile') 且必须是一个文件对象（可选）
- files 需要包含在 Docker 上下文中的文件列表（可选）
- buildArgs 一个键值都为 String 的 Map 集合，将为 build 命令设置 --build-arg 参数（可选）
- labels 一个键值都为 String 的 Map 集合，将为 build 命令设置 --label 参数，默认为空（可选）
- pull 是否在构建前拉取最新的基础镜像，默认为 false 。（可选）
- noCache 是否在构建时设置 --no-cache 参数，从头开始构建镜像;默认为 false 。 现在使用如下命令即可构建出 Docker 镜像（需保证当前环境中的 Docker 进程已启动） PS：其实比较简单自己总结下，学的知识活学活用。
