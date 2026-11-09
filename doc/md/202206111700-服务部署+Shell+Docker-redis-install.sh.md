---
id: "doc-829737c9c701"
title: "redis-install.sh"
date: "2022-06-11T17:00:07.788000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "服务部署"]
tags: ["服务部署", "Shell", "Docker", "Redis", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/fu-wu/redis-install.sh.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "5c059128a105116ce474322b58319ea759033ca74105c49ec58b35ef11f4a17d"
---

# redis-install.sh

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111700-%E6%9C%8D%E5%8A%A1%E9%83%A8%E7%BD%B2%2BShell%2BDocker-redis-install.sh.md)

> 原文：[redis-install.sh](https://xn--6o0a585a.gitbook.io/devops/fu-wu/redis-install.sh.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 17:00｜日期依据：GitBook 页面更新时间

```bash
docker pull redis
mkdir -p /root/docker/redis/conf
mkdir -p /root/docker/redis/data
docker run -d --privileged=true -p 6379:6379 --restart always -v /root/docker/redis/conf/redis.conf:/etc/redis/redis.conf -v /root/docker/redis/data:/data --name myredis redis redis-server /etc/redis/redis.conf --appendonly yes
docker run --name my-redis -p 16379:6379 -v $(pwd)/data:/data -d redis redis-server --appendonly yes
```
