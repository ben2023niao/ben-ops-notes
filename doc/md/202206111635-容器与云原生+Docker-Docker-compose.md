---
id: "doc-314b769d0c3f"
title: "Docker-compose"
date: "2022-06-11T16:35:18.489000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "fa89db072269d18b7651fbfb7ef08669fed1811aa571416e314980ed87953c4c"
---

# Docker-compose

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111635-%E5%AE%B9%E5%99%A8%E4%B8%8E%E4%BA%91%E5%8E%9F%E7%94%9F%2BDocker-Docker-compose.md)

> 原文：[Docker-compose](https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:35｜日期依据：GitBook 页面更新时间

安装docker-compose

1、

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

2、

```
sudo chmod +x /usr/local/bin/docker-compose
```

3、

```
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

4、

```
docker-compose --version
```
