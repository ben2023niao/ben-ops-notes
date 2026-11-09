---
id: "doc-4baf0641a133"
title: "安装redis"
date: "2022-06-11T16:17:36.424000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "Redis"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/centos7/an-zhuang-redis.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "be740d79d0f76b94ac71a950b1c05aa8e9f7aff41cb1390aae1d689728e06ff7"
---

# 安装redis

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202206111617-%E5%AE%B9%E5%99%A8%E4%B8%8E%E4%BA%91%E5%8E%9F%E7%94%9F%2BDocker%2BShell-%E5%AE%89%E8%A3%85redis.md)

> 原文：[安装redis](https://xn--6o0a585a.gitbook.io/devops/docker/centos7/an-zhuang-redis.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:17｜日期依据：GitBook 页面更新时间

**1. 前提是Docker已经安装好了**

**2.拉取Redis镜像**

```bash
docker pull redis
```

**3.启动**

```bash
docker run --name redis -p 6378:6379 -d --restart=always redis redis-server --appendonly yes --requirepass "123456"
```

> 参数讲解
>
> `--name`为容器取一个唯一的名字
>
> `-p`端口映射，把宿主机的端口映射到容器内的端口
>
> `--restar=always`随容器启动而启动
>
> `redis-server --appendonly yes`在容器里执行`redis-server`命令，打开redis持久化
>
> `--requirepass`密码

**4.连接**

```
docker ps 查看CONTAINER ID
docker exec -it 0047b8680fc2 redis-cli
```
